# [BLUEPRINT] MOD-INF-043
# [MODULE] scripts/backup/backup_reconciler_shadow
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/backup/backup_reconciler (config/load_config reuse); scripts/governance/meta/backup_runtime_state (_is_pid_alive reuse)
# [CONSUMERS] drills (python scripts/backup/backup_reconciler_shadow.py --drill); future promotion wires this logic into BACKUP-RECONCILER after the 7-day shadow window
# [STARTUP] manual
# [MATURITY] shadow
# [INVARIANTS] SH-11:cadence 判据=last_backup_time 与 checkpoint 面双读——checkpoint(stage_ok) 在 8h 窗内即视为"近期已有备份活动"⇒skip 重烧（被杀运行不复活为重烧全量；治 state 永不回写→cadence 永到期→落地即全量重烧）;SH-12:锁自查=持锁者 PID 存活(复用 _is_pid_alive)——活则 lock_skipped 不点火，死则记 LOCK_TAKEOVER 后点火（禁"锁文件在就永久快退"）；点火/结算只写 shadow state（backup_state_shadow.json），生产 state 零触碰（G4-6 影子红线）
# [MODIFY-GUARD] trigger/reconcile 语义与 scripts/backup/backup_reconciler.py 对称；STATE_PATH 可注入（drill 用 tmp 副本）；禁改生产锁/生产 state 路径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] state 缺失/损坏→按无状态处理（允许触发，fail-open 向"多备份"侧）；复用件加载失败→保守判活；所有 state 写失败降级日志不抛
# [TESTS] python scripts/backup/backup_reconciler_shadow.py --drill（CASE A checkpoint 绿/CASE B 无 checkpoint 红对照/CASE C 锁自检）
# [TTL] task_bound
# create-guard-not-dup: shadow twin of scripts/backup/backup_reconciler.py per G4-6 shadow mandate (work order st-backfix-20261010 T2); promotion ports this logic into the original after the 7-day shadow window, zero permanent duplication.
"""Shadow landing gate for the backup chain (work order T2, G4-6 shadow).

Production disease being cured (2026-10-10): a backup run killed before STAGE 4
never writes state -> ``last_backup_time`` stays stale -> the post-commit landing
hook sees "cadence due" on EVERY landing -> full re-burn each time (40min CH +
hours of USB I/O per round, 5+ rounds on 2026-10-10).

T2 mechanism: before igniting, read the CHECKPOINT face (backup_state_shadow.json
``stages`` written by backup_shadow.ps1). A stage_ok checkpoint inside the cadence
window proves a recent backup already did the work - the run may have been killed
afterwards, but re-burning is wrong. This module is the shadow twin of
scripts/backup/backup_reconciler.py: same trigger/reconcile shape, shadow state +
shadow lock only, zero writes to production state/lock/targets.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import PROJECT_ROOT  # canonical SSOT (main repo root)

SHADOW_STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state_shadow.json"
SHADOW_LOCK_FILE = PROJECT_ROOT / ".runtime" / "backup_shadow.lock"
SHADOW_SCRIPT = Path(__file__).resolve().parent / "backup_shadow.ps1"
IGNITE_LOG_DIR = PROJECT_ROOT / "logs"

# ps1 lock content format "PID:<n> START:<iso>" (same as production backup.ps1)
_RE_LOCK_PID = re.compile(r"PID:(\d+)")
_FULL_RUN_CADENCE_HOURS = 8.0
_IGNITE_SPAWN_TIMEOUT_S = 30


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_shadow_state(state_path: Path | None = None) -> dict[str, Any]:
    """读 shadow checkpoint state；缺失/损坏=无状态（fail-open 向多备份侧）。"""
    path = Path(state_path) if state_path else SHADOW_STATE_FILE
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, OSError, ValueError):
        return {}


def last_stage_ok_ts(state: dict[str, Any], stage: str) -> datetime | None:
    """最新 stage_ok checkpoint 时刻（freshness 真源=stage_ok 条目，skip 不覆写语义在 ps1 侧）。"""
    newest: datetime | None = None
    for entry in state.get("stages") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("stage") == stage and entry.get("status") == "stage_ok":
            try:
                ts = datetime.fromisoformat(str(entry.get("ts")))
            except (TypeError, ValueError):
                continue
            if newest is None or ts > newest:
                newest = ts
    return newest


def recent_backup_activity(state: dict[str, Any], within_hours: float = _FULL_RUN_CADENCE_HOURS) -> tuple[bool, str]:
    """checkpoint 面判据：任一实质 stage_ok 落在窗内 = 近期已有备份活动。

    实质阶段=db_dump/ch/vault（git_bundle/offrepo/g_mirror 是衍生副本，不算
    "备份做过份"的独立证据）。返回 (fresh, evidence)。
    """
    now = _utcnow()
    for stage in ("db_dump", "ch", "vault"):
        ts = last_stage_ok_ts(state, stage)
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_h = (now - ts).total_seconds() / 3600.0
        if age_h < within_hours:
            return True, f"checkpoint stage={stage} age={age_h:.2f}h < {within_hours}h"
    return False, "no substantive stage_ok checkpoint in window"


def _load_prod_config_trigger() -> dict[str, Any]:
    """复用生产 trigger 配置（backup_config.yaml §trigger），不另设真源。"""
    prod = PROJECT_ROOT / "scripts" / "backup" / "backup_reconciler.py"
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("_prod_backup_reconciler_ref", str(prod))
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cfg = mod.load_config() or {}
        return cfg.get("trigger", {}) or {}
    except Exception:  # noqa: BLE001  配置复用失败→空 dict，走调用方 fallback
        return {}


def trigger(committed_files: list[str], state_path: Path | None = None) -> bool:
    """SH-11 落地闸：重要文件 + （last_backup_time 与 checkpoint 面双读的）cadence。

    生产版条件 2 只看 last_backup_time；影子版在其上叠加 checkpoint 面：
    last_backup_time 陈旧但 checkpoint 窗内新鲜 ⇒ skip（不再重烧全量）。
    """
    cfg = _load_prod_config_trigger()
    prefixes = tuple(cfg.get("important_prefixes", ["src/", "scripts/", "config/"]))
    important = frozenset(cfg.get("important_files", []))
    has_important = any((lambda rel: rel.startswith(prefixes) or rel in important)(_rel(f)) for f in committed_files)
    if not has_important:
        return False

    state = load_shadow_state(state_path)
    # 生产形状条件 2：last_backup_time 8h
    last_backup = state.get("last_backup_time")
    if last_backup:
        try:
            ts = datetime.fromisoformat(str(last_backup))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if (_utcnow() - ts).total_seconds() < _FULL_RUN_CADENCE_HOURS * 3600:
                return False
        except (TypeError, ValueError):
            pass
    # 影子增判：checkpoint 面新鲜 ⇒ skip（被杀运行不算"久未备份"）
    fresh, evidence = recent_backup_activity(state)
    if fresh:
        print(f"[SHADOW-GATE] skip: {evidence}")
        return False
    return True


def _rel(f: str) -> str:
    # repo-relative normalization (os.path.relpath, mirroring backup_reconciler.rel_path):
    # bare repo-relative inputs must NOT be resolved against the process CWD - in a
    # session worktree that folds the worktree prefix into the path and breaks the
    # important-prefix match (drill CASE B red-proof, 2026-10-10)
    p = Path(f)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    try:
        return os.path.relpath(str(p), str(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def _is_pid_alive(pid: int) -> bool:
    """复用 backup_runtime_state._is_pid_alive；复用件不可用=保守判活。"""
    helper = PROJECT_ROOT / "scripts" / "governance" / "meta" / "backup_runtime_state.py"
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("_shadow_backup_runtime_state", str(helper))
        if spec is None or spec.loader is None:
            return True
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "_is_pid_alive", None)
        if not callable(fn):
            return True
        return bool(fn(pid))
    except Exception:  # noqa: BLE001
        return True


def read_shadow_lock_holder(lock_file: Path | None = None) -> int | None:
    path = Path(lock_file) if lock_file else SHADOW_LOCK_FILE
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except (FileNotFoundError, OSError):
        return None
    m = _RE_LOCK_PID.search(raw)
    return int(m.group(1)) if m else None


def update_shadow_state(state_path: Path | None, **fields: Any) -> None:
    """CAS-light merge 写 shadow state（drill/观测行用；ps1 侧仍是原子写真源）。"""
    path = Path(state_path) if state_path else SHADOW_STATE_FILE
    state = load_shadow_state(path)
    state.update(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def reconcile(
    session_id: str,
    state_path: Path | None = None,
    ignite: bool = True,
    lock_path: Path | None = None,
) -> dict[str, Any]:
    """影子落地通道：结算 pending（log 语义同 INV-11/12 缩尺）→ 锁自查 → 脱离点火。"""
    path = state_path or SHADOW_STATE_FILE
    state = load_shadow_state(path)

    # (0) 结算上一轮：pending 指针=state.last_ignite_log（影子 state 内自洽）
    pending_log = state.get("last_ignite_log")
    if pending_log:
        try:
            text = Path(str(pending_log)).read_text(encoding="utf-8-sig", errors="replace")
        except (FileNotFoundError, OSError):
            text = ""
        if "Another SHADOW backup is running" in text:
            update_shadow_state(path, last_run_outcome="lock_skipped", last_ignite_log=None)
            return {"action": "warn", "detail": "prior ignition lock-skipped (shadow)"}
        if "State saved" in text or "Report saved" in text:
            update_shadow_state(path, last_run_outcome="completed_verified_by_log", last_ignite_log=None)
        # 无痕迹（崩溃/被杀/仍在跑）→ fail-closed 保留 pending，不记 ok

    # (1) 锁自查（SH-12）：持锁者活→lock_skipped；死→LOCK_TAKEOVER 留痕后点火
    holder = read_shadow_lock_holder(lock_path)
    if holder is not None and holder > 0 and _is_pid_alive(holder):
        update_shadow_state(path, last_run_outcome="lock_skipped")
        return {"action": "warn", "detail": f"shadow lock held by live PID {holder}; ignition skipped"}
    if holder is not None and holder > 0:
        print(f"[SHADOW-GATE] LOCK_TAKEOVER: holder {holder} dead - proceeding (T2: dead holder != fast-exit-forever)")

    if not ignite:
        return {"action": "dry", "detail": "ignite=False (drill): would ignite backup_shadow.ps1"}

    # (2) 脱离点火 backup_shadow.ps1（轻量影链，瞬时 powershell 装载器同生产 P-7 形态）
    ts = _utcnow().strftime("%Y%m%d_%H%M%S")
    ignite_log = IGNITE_LOG_DIR / f"backup_shadow_ignite_{ts}.log"
    arg_list = f"-NoProfile -ExecutionPolicy Bypass -File {SHADOW_SCRIPT} -Mode all"
    ps_cmd = (
        "$null = Start-Process -FilePath 'powershell.exe' "
        f"-ArgumentList '{arg_list}' "
        f"-WorkingDirectory '{PROJECT_ROOT}' "
        "-WindowStyle Hidden "
        f"-RedirectStandardOutput '{ignite_log}' "
        f"-RedirectStandardError '{ignite_log}.err'"
    )
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        run_subprocess_hidden(  # 固定 powershell + 我方拼装命令，无外部输入注入面
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=_IGNITE_SPAWN_TIMEOUT_S,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        update_shadow_state(path, last_run_outcome="ignite_failed", last_ignite_error=str(exc)[:200])
        return {"action": "warn", "detail": f"shadow ignition failed: {exc}"}

    update_shadow_state(
        path,
        last_backup_launch_time=_utcnow().isoformat(),
        last_ignite_log=str(ignite_log),
        last_run_outcome="ignited_pending_verification",
        last_ignite_session_id=session_id,
    )
    return {"action": "warn", "detail": f"shadow backup ignited detached (log={ignite_log.name})"}


def _drill() -> int:
    """红绿三案：A=checkpoint 面拦重烧（绿）/B=无 checkpoint 红对照/C=锁自检。"""
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="backfix_drill_"))
    results: list[tuple[str, bool, str]] = []

    # CASE A（T2① 核心绿证）：last_backup_time 陈旧 + checkpoint 窗内新鲜 ⇒ skip
    now = _utcnow()
    killed_run_state = {
        # 被杀运行：STAGE4 未达 → last_backup_time 停 26h 前（生产病灶形态）
        "last_backup_time": (now - timedelta(hours=26)).isoformat(),
        "status": "running",
        "stages": [
            {"stage": "start", "status": "running", "ts": (now - timedelta(hours=2)).isoformat()},
            {"stage": "db_dump", "status": "stage_ok", "ts": (now - timedelta(hours=2)).isoformat()},
            {"stage": "ch", "status": "stage_ok", "ts": (now - timedelta(hours=1)).isoformat()},
            # 此后被杀——vault/report 无条目
        ],
    }
    case_a = tmp / "case_a.json"
    case_a.write_text(json.dumps(killed_run_state), encoding="utf-8")
    fired = trigger(["src/zephyr/foo.py"], state_path=case_a)
    results.append(
        (
            "CASE A checkpoint-fresh blocks re-burn (trigger=False)",
            fired is False,
            "killed run's fresh checkpoints must suppress re-ignition",
        )
    )

    # CASE B（红对照）：同 state 摘除 checkpoint ⇒ 生产同形行为=触发（证明 delta 来自 checkpoint 面）
    no_ckpt = {k: v for k, v in killed_run_state.items() if k != "stages"}
    case_b = tmp / "case_b.json"
    case_b.write_text(json.dumps(no_ckpt), encoding="utf-8")
    fired_b = trigger(["src/zephyr/foo.py"], state_path=case_b)
    results.append(
        (
            "CASE B no-checkpoint red control (trigger=True)",
            fired_b is True,
            "without checkpoints the production-shape gate re-burns (the disease)",
        )
    )

    # CASE C（SH-12 锁自检）：活持锁者→不点火；ignite=False 干跑
    lock = tmp / "shadow.lock"
    lock.write_text(f"PID:{__import__('os').getpid()} START:{_utcnow().isoformat()}", encoding="utf-8")
    st = tmp / "case_c.json"
    st.write_text("{}", encoding="utf-8")
    r = reconcile("drill", state_path=st, ignite=False, lock_path=lock)
    results.append(
        (
            "CASE C live-holder lock skip (no ignition)",
            r["action"] == "warn" and "lock held" in r["detail"],
            f"detail={r['detail']}",
        )
    )

    failed = 0
    for name, ok, why in results:
        print(f"[{'GREEN' if ok else 'RED'}] {name}" + ("" if ok else f"  <-- {why}"))
        failed += 0 if ok else 1
    print(f"drill: {len(results) - failed}/{len(results)} green")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--drill" in sys.argv:
        sys.exit(_drill())
    print("usage: python backup_reconciler_shadow.py --drill")
