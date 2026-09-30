# [BLUEPRINT] MOD-GOV_SCRIPTS-002
# [MODULE] scripts.governance._tasks.session_closeout_reconciler
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.lock_files（释放/MERGE_HEAD 归属语义复用）; zephyr.security.access_control.session_concurrency; zephyr.shared.infra.process_pool
# [CONSUMERS] src/zephyr/trading/process_reaper.py（10min 脉冲第 5 步 subprocess --once）; 人工 CLI
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 默认 shadow（只判只记零动作）——动作须 --execute 或 data/runtime/session_closeout.live 开关; 判死四门全过才动（注册表证死/PID 双检/claim TTL 全过期/连续 2 轮嫌疑）; logical=True 与 data/runtime/session_closeout_keep.txt 白名单永不收尾; commit_queue 在飞项豁免; index.lock 在飞整轮缩手; MERGE_HEAD 归属死会话=只告警禁 abort/promote/handoff/报 Owner 永不自动（宪法 §2.9 人工序列）; 归档=mv 可逆（sessions→sessions_archive/YYYY-MM）; 禁 git stash drop / reset --hard; registry/git/队列任一异常=本轮零动作
# [MODIFY-GUARD] RB-3 治本设计文档 docs/_working/root_cure_campaign/RB3_session_closeout.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry 不可达/git 失败/队列扫描异常→本轮零动作+error 记录 exit 8; 有嫌疑/告警→exit 4; 干净→exit 0
# [TESTS] tests/governance/test_session_closeout_reconciler.py
# [A_module] module_id=MOD-GOV_SCRIPTS-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""session_closeout_reconciler.py — 会话收尾协调器（RB-3 治本，shadow 首版）。

病根：宪法 §2.9 收尾序列五步全是会话自觉驱动；会话死亡后无人释放 claim/清暂存残影/
归档会话目录，151 个 .runtime/sessions 只增不减，死 claim 压文件阻断新会话。

本协调器不替代人工收尾（promote/handoff/报 Owner 永不自动），只兜底无人值守场景的
机械残留：判死四门全过才动，动作三级——①释放 claim+RB1 判型清 index/stash 归档
（仅无 MERGE_HEAD）；②sessions 目录 mv 归档（可逆）；③MERGE_HEAD 归属=只告警。

挂靠：process_reaper 10min 脉冲第 5 步独立 try subprocess 调本文件 --once（子进程
隔离炸不连坐收割主链）；不新建 schtasks/cron（净零，宪法 §9.3 合规口径见设计文档 §2）。

Usage:
    python scripts/governance/_tasks/session_closeout_reconciler.py --once [--json]
    python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run [--json]
    python scripts/governance/_tasks/session_closeout_reconciler.py --status
    python scripts/governance/_tasks/session_closeout_reconciler.py --once --execute   # 显式实弹（或 data/runtime/session_closeout.live 开关）
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

__all__ = ["run_cycle", "main"]

_EXIT_OK = 0
_EXIT_PENDING = 4
_EXIT_ERROR = 8

# ---- 路径常量（repo_root 参数可注入；测试一律 tmp_path，禁写生产盘） ----
_RUNTIME_REL = Path(".runtime")
_REGISTRY_REL = _RUNTIME_REL / "session_registry.json"
_SESSIONS_REL = _RUNTIME_REL / "sessions"
_ARCHIVE_REL = _RUNTIME_REL / "sessions_archive"
_STATE_REL = _RUNTIME_REL / "session_closeout" / "state.json"
_ALERT_REL = _RUNTIME_REL / "logs" / "session_closeout_alert.jsonl"
_QUEUE_PENDING_REL = _RUNTIME_REL / "commit_queue" / "pending"
_QUEUE_PROCESSING_REL = _RUNTIME_REL / "commit_queue" / "processing"
_AILOCKS_REGISTRY_REL = Path(".ailocks") / "registry.json"
_LIVE_FLAG_REL = Path("data") / "runtime" / "session_closeout.live"
_KEEP_REL = Path("data") / "runtime" / "session_closeout_keep.txt"
_ALERT_ENV = "SESSION_CLOSEOUT_ALERT_LOG"

_STRIKES_REQUIRED = 2  # 连续 2 轮嫌疑（10min 轮隔×2=20min 确认窗，对齐 reaper 孤儿 30min 观察视界下限）
_ORPHAN_DIR_AGE_S = 7 * 86400  # 无注册表条目的孤儿垃圾目录归档门槛（mtime>7d）
_ARCHIVED_LEDGER_CAP = 200  # 归档账保留上限（防 state.json 无界增长）

_STASH_MSG_PREFIX = "dead-session-closeout"


# ============== 基础设施（jsonl/原子写/git） ==============


def _write_alert_line(path: Path, record: dict) -> bool:
    """告警行落账（一行一事件写到底，DCS decision_chain_sentinel 落账制式同款）。"""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return True
    except OSError:
        return False


def _persist_state(path: Path, data: dict) -> bool:
    """state.json 原子写（tmp + os.replace，reaper _write_status 同款）。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def _load_state_file(path: Path) -> dict | None:
    """读 JSON（不存在/损坏 → None，调用方按 fail-safe 处理）。"""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else None
    except (OSError, ValueError):
        return None


def _git(root: Path, args: list[str], timeout: int = 60) -> tuple[int, str]:
    """git 子命令（返回 (rc, stdout)；stderr 折进 stdout 尾部供诊断）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    try:
        r = run_subprocess_hidden(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
        return r.returncode, (r.stdout or "") + ("" if not r.stderr else "\n# " + r.stderr.strip()[:200])
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, f"# {type(e).__name__}: {e}"


def _index_locked(root: Path) -> bool:
    """index.lock 存在=git 写入在飞（A1 加固②同款）——本轮整体缩手。"""
    rc, out = _git(root, ["rev-parse", "--git-path", "index.lock"])
    if rc != 0 or not out.strip():
        return False
    first_line = out.splitlines()[0].strip()
    if not first_line:
        return False
    p = Path(first_line)
    if not p.is_absolute():
        p = root / p
    return p.exists()


# ============== 证据采集（全部可注入，测试 monkeypatch 这些函数） ==============


def _load_raw_registry(repo_root: Path) -> dict:
    """SessionRegistry 原始条目（含死条目——回收恰恰要区分「条目死」与「查无此会话」）。"""
    data = _load_state_file(repo_root / _REGISTRY_REL)
    return data if isinstance(data, dict) else {}


def _active_session_ids(repo_root: Path) -> set[str] | None:
    """活跃会话集（SessionRegistry.list_active 同口径，A1 判死真源）。

    Returns:
        None=registry 不可达（fail-safe：本轮零动作）。
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        return {s.session_id for s in SessionRegistry(repo_root).list_active()}
    except Exception:  # noqa: BLE001 — 注册表不可达=无法证死（防误收活会话）
        return None


def _pid_present_sessions(raw: dict) -> set[str]:
    """PID 仍存活的 sid 集（watchdog A1 _live_pid_sessions 同款保守口径：探测异常=在场）。"""
    try:
        from zephyr.shared.infra.process_pool import is_pid_alive
    except Exception:  # noqa: BLE001 — 判活设施不可用=全员按在场（fail-safe）
        return {sid for sid, info in raw.items() if int(info.get("pid") or 0) > 0}
    present: set[str] = set()
    for sid, info in raw.items():
        pid = int(info.get("pid") or 0)
        if pid <= 0:
            continue
        try:
            if is_pid_alive(pid):
                present.add(sid)
        except Exception:  # noqa: BLE001 — 探测异常按在场（宁可漏扫不可误扫）
            present.add(sid)
    return present


def _session_claims(repo_root: Path, session_id: str) -> dict[str, dict[str, Any]]:
    """.ailocks registry 中该持有者全部 claim（归一化路径 → 条目）。registry 损坏=按无 claim。"""
    data = _load_state_file(repo_root / _AILOCKS_REGISTRY_REL)
    locks = data.get("locks", {}) if isinstance(data, dict) else {}
    return {fp: info for fp, info in locks.items() if isinstance(info, dict) and info.get("owner_id") == session_id}


def _all_claim_owners(repo_root: Path) -> set[str]:
    """.ailocks 全部持有者（补「有 claim 无注册表条目」的候选面）。"""
    data = _load_state_file(repo_root / _AILOCKS_REGISTRY_REL)
    locks = data.get("locks", {}) if isinstance(data, dict) else {}
    return {info.get("owner_id") for info in locks.values() if isinstance(info, dict) and info.get("owner_id")}


def _queue_inflight_sids(repo_root: Path) -> set[str]:
    """在飞提交队列的 sid 集（pending/processing 两面；qid=q-{date}-{sid}-{seq} 文件名解析+JSON session 字段双源）。"""
    sids: set[str] = set()
    for sub in (_QUEUE_PENDING_REL, _QUEUE_PROCESSING_REL):
        qdir = repo_root / sub
        try:
            if not qdir.is_dir():
                continue
            for f in qdir.glob("q-*.json"):
                parts = f.name[2:-5].split("-", 1)  # 去掉 q- 前缀与 .json 后缀
                rest = parts[1] if len(parts) == 2 else ""
                sid_part = rest.rsplit("-", 1)[0] if "-" in rest else rest
                if sid_part:
                    sids.add(sid_part)
                item = _load_state_file(f)
                if isinstance(item, dict) and item.get("session"):
                    sids.add(str(item["session"]))
        except OSError:
            continue
    return sids


def _load_keep_sids(repo_root: Path) -> set[str]:
    """显式保留清单（data/runtime/session_closeout_keep.txt，每行一个 sid；仿 process_reaper_keep.txt 先例）。"""
    keep: set[str] = set()
    try:
        f = repo_root / _KEEP_REL
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    keep.add(line)
    except OSError:
        pass
    return keep


# ============== 判死四门 ==============


def _ev1_registry_present(info: dict, now: float) -> tuple[bool, str] | None:
    """证①·注册表条目在场：SessionRegistry 判活设施证死。返回 None=设施异常（调用方 fail-closed）。"""
    try:
        from zephyr.security.access_control.session_concurrency import SessionInfo, _is_session_alive

        ev1 = not _is_session_alive(SessionInfo.from_dict(info), now)
        return ev1, f"registry:{'dead' if ev1 else 'alive'}"
    except Exception:  # noqa: BLE001 — 判活设施异常=无法证死（fail-closed）
        return None


def _ev1_registry_absent(claims: dict[str, dict[str, Any]], now: float) -> tuple[bool, str]:
    """证①·注册表条目缺席：全部 claim PID 死亡兜底证死；判活设施不可用=无进程证据（fail-closed）。"""
    pids = [int(c.get("pid", 0) or 0) for c in claims.values()]
    try:
        from zephyr.shared.infra.process_pool import is_pid_alive

        ev1 = bool(claims) and all((not p) or p <= 0 or not is_pid_alive(p) for p in pids)
    except Exception:  # noqa: BLE001 — 判活设施不可用=无进程证据（fail-closed）
        ev1 = False
    return ev1, ("registry-absent:all-claim-pids-dead" if ev1 else "registry-absent:no-process-evidence")


def _ev2_claims_expired(claims: dict[str, dict[str, Any]], now: float) -> tuple[bool, str]:
    """证②·有 claim：全部 claim TTL 过期。"""
    unexpired = [fp for fp, c in claims.items() if float(c.get("expires_at") or 0.0) >= now]
    ev2 = not unexpired
    return ev2, f"claims:{len(claims) - len(unexpired)}/{len(claims)} expired"


def _ev2_no_claims(info: dict | None, ev1: bool) -> tuple[bool, str]:
    """证②·无 claim：仅注册表证死可成立（held 无 TTL，裁定#252）。"""
    held = list(info.get("held_files") or []) if isinstance(info, dict) else []
    ev2 = (not held) or ev1
    return ev2, ("claims:none" if not held else f"session-held:{len(held)} releasable={ev2}")


def _death_evidence(
    session_id: str,
    raw: dict,
    claims: dict[str, dict[str, Any]],
    pid_present: set[str],
    now: float,
) -> tuple[bool, str]:
    """证①（注册表/进程证死）+证②（全部 claim TTL 过期）双证判死（lock_files._death_evidence 同口径）。

    会话在场一票否决：PID 存活（gate2）或活跃集命中（gate1，调用方先查）即 False。
    """
    info = raw.get(session_id)
    if info is not None and session_id in pid_present:
        return False, "pid-alive(present)"
    # 证①：注册表证死或进程证据兜底
    if info is not None:
        probe = _ev1_registry_present(info, now)
        if probe is None:
            return False, "registry-probe-failed"
        ev1, ev1_desc = probe
    else:
        ev1, ev1_desc = _ev1_registry_absent(claims, now)
    # 证②：全部 claim TTL 过期；无 claim 时仅注册表证死可成立（held 无 TTL，裁定#252）
    if claims:
        ev2, ev2_desc = _ev2_claims_expired(claims, now)
    else:
        ev2, ev2_desc = _ev2_no_claims(info, ev1)
    return (ev1 and ev2), f"{ev1_desc}|{ev2_desc}"


def _merge_head_state(
    repo_root: Path,
    session_id: str,
    info: dict | None,
    claims: dict[str, dict[str, Any]],
    now: float,
) -> tuple[str, str]:
    """MERGE_HEAD 状态判定：no-merge-head / attributed（归属该死会话→只告警）/ not-attributed。

    归属判定复用 lock_files._merge_head_attributed_to（双条件真源，禁本地复刻）。
    """
    try:
        from scripts.lock_files import _main_merge_head_path, _merge_head_attributed_to

        if not _main_merge_head_path(repo_root).is_file():
            return "no-merge-head", ""
        session_info = None
        if info is not None:
            try:
                from zephyr.security.access_control.session_concurrency import SessionInfo

                session_info = SessionInfo.from_dict(info)
            except Exception:  # noqa: BLE001 — 条目损坏按 None（claims 兜底归因）
                session_info = None
        attributed, why = _merge_head_attributed_to(repo_root, session_id, session_info, claims, now)
        return ("attributed" if attributed else "not-attributed"), why
    except Exception as e:  # noqa: BLE001 — 归属设施异常=按存在且不明（保守不动作）
        return "not-attributed", f"probe-failed:{type(e).__name__}:{e}"


# ============== RB1 判型与动作（level ①②） ==============


def _rb1_classify(root: Path, claim_paths: list[str], sid: str) -> tuple[list[str], list[str]]:
    """claimed∩staged RB1 判型：worktree==HEAD（hash-object 比对，CRLF 免疫）→清 index 残影；
    ≠HEAD → stash 归档（pathspec 限定、禁 drop、可 pop）。仅无 MERGE_HEAD 时由调用方触发。

    Returns:
        (to_unstage, to_stash)
    """
    rc, out = _git(root, ["diff", "--cached", "--name-only"])
    staged = {ln.strip().strip('"') for ln in out.splitlines() if ln.strip()} if rc == 0 else set()
    to_unstage: list[str] = []
    to_stash: list[str] = []
    for rel in sorted(p for p in claim_paths if p in staged):
        head_rc, head_sha = _git(root, ["rev-parse", "HEAD:" + rel])
        wt_rc, wt_sha = _git(root, ["hash-object", rel])
        if head_rc == 0 and wt_rc == 0 and head_sha.splitlines()[0].strip() == wt_sha.splitlines()[0].strip():
            to_unstage.append(rel)  # 内容已落地（==HEAD），index 残影可零损失清除
        else:
            to_stash.append(rel)  # ≠HEAD（改过/新增），内容归档 stash 防 WIP 丢失
    return to_unstage, to_stash


def _release_claims(repo_root: Path, session_id: str, claim_paths: list[str], info: dict | None) -> list[str]:
    """释放死会话 claim（复用 lock_files 双登记处语义：.ailocks 锁目录+SessionRegistry held/注销）。"""
    from scripts.lock_files import _force_release_locks, _force_release_session_registry

    released = _force_release_locks(session_id, claim_paths)
    session_info = None
    if info is not None:
        try:
            from zephyr.security.access_control.session_concurrency import SessionInfo

            session_info = SessionInfo.from_dict(info)
        except Exception:  # noqa: BLE001
            session_info = None
    _force_release_session_registry(repo_root, session_id, session_info)
    return released


def _act_level1(repo_root: Path, session_id: str, claim_paths: list[str], info: dict | None) -> dict:
    """级①动作：RB1 判型清 index/stash 归档 + 双登记处释放（调用方保证无 MERGE_HEAD 且非 shadow）。"""
    res: dict[str, Any] = {"unstaged": [], "stashed": [], "stash_ref": "", "released": [], "error": ""}
    try:
        to_unstage, to_stash = _rb1_classify(repo_root, claim_paths, session_id)
        if to_unstage:
            rc, out = _git(repo_root, ["reset", "HEAD", "--", *to_unstage], timeout=120)
            if rc != 0:
                res["error"] = f"reset-failed:{out.strip()[:150]}"
                return res
            res["unstaged"] = to_unstage
        if to_stash:
            rc, out = _git(
                repo_root,
                ["stash", "push", "-m", f"{_STASH_MSG_PREFIX} {session_id}", "--", *to_stash],
                timeout=120,
            )
            if rc != 0 or "No local changes" in out:
                res["error"] = f"stash-failed:{out.strip()[:150]}"
            else:
                res["stashed"] = to_stash
                ref_rc, ref = _git(repo_root, ["rev-parse", "-q", "--verify", "refs/stash"])
                res["stash_ref"] = ref.strip() if ref_rc == 0 else "refs/stash"
        res["released"] = _release_claims(repo_root, session_id, claim_paths, info)
    except Exception as e:  # noqa: BLE001 — 动作异常如实记录（不吞失败信号）
        res["error"] = f"{type(e).__name__}: {e}"
    return res


def _act_level2(repo_root: Path, session_id: str, *, orphan: bool = False) -> dict:
    """级②动作：.runtime/sessions/<sid> 整目录 mv → sessions_archive/<YYYY-MM>/<sid>（可逆，幂等）。"""
    res: dict[str, Any] = {"archived": False, "dest": "", "error": ""}
    src = repo_root / _SESSIONS_REL / session_id
    if not src.is_dir():
        res["error"] = "session-dir-absent"
        return res
    month = datetime.fromtimestamp(time.time(), tz=timezone.utc).strftime("%Y-%m")
    dest_dir = repo_root / _ARCHIVE_REL / month
    dest = dest_dir / session_id
    if dest.exists():
        res["error"] = "archive-target-exists"  # 幂等：目标已存在不覆盖
        return res
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        res["archived"] = True
        res["dest"] = str(dest.relative_to(repo_root)).replace("\\", "/")
        res["orphan"] = orphan
    except OSError as e:
        res["error"] = f"move-failed:{e}"
    return res


# ============== 主循环 ==============


def _scan_targets(g: dict) -> tuple[list[str], list[str]]:
    """扫描面：候选（注册表∪claim 持有者−活跃）+ 孤儿目录（sessions 有、注册表无、不活跃）。"""
    root = g["root"]
    raw = g["raw"]
    active = g["active"]
    candidates = sorted((set(raw) | _all_claim_owners(root)) - active)
    session_dirs = (
        {p.name for p in (root / _SESSIONS_REL).glob("*") if p.is_dir()} if (root / _SESSIONS_REL).is_dir() else set()
    )
    orphan_dirs = sorted(session_dirs - set(raw) - active)
    return candidates, orphan_dirs


def _load_suspects_state(g: dict) -> tuple[dict, dict]:
    """读 state.json strikes 旧账并清复活会话账目；返回 (suspects, archived_ledger)。"""
    root = g["root"]
    active = g["active"]
    pid_present = g["pid_present"]
    state = _load_state_file(root / _STATE_REL) or {}
    suspects: dict = state.get("suspects", {}) if isinstance(state.get("suspects"), dict) else {}
    # 「连续」语义：活过来（活跃集/PID 在场）的会话清 strikes 旧账——
    # 否则复活会话不在候选面、旧账残留，再死时首轮即满 strikes 误触发。
    for revived in [s for s in suspects if s in active or s in pid_present]:
        suspects.pop(revived, None)
    return suspects, state.get("archived", {})


def _confirmed_actions(g: dict, sid: str, info: dict | None, claims: dict[str, dict[str, Any]]) -> None:
    """满 strikes 确认死后的动作分支：MERGE_HEAD 归属=级③只告警；shadow=预演；实弹=级①+级②。"""
    root = g["root"]
    summary = g["summary"]
    now = g["now"]
    execute = g["execute"]
    archived_ledger = g["archived_ledger"]
    suspects = g["suspects"]
    mh_state, mh_why = _merge_head_state(root, sid, info, claims, now)
    acted: dict[str, Any] = {}
    if mh_state == "attributed":
        summary["merge_warned"].append({"sid": sid, "why": mh_why})  # 级③：只告警禁 abort
    elif not execute:
        acted = {
            "would_level1_claims": len(claims),
            "would_level2_archive": (root / _SESSIONS_REL / sid).is_dir(),
        }
    elif mh_state == "no-merge-head" and claims:
        acted["level1"] = _act_level1(root, sid, sorted(claims), info)
    if execute and mh_state != "attributed" and (root / _SESSIONS_REL / sid).is_dir():
        acted["level2"] = _act_level2(root, sid)
        if acted["level2"].get("archived"):
            archived_ledger[sid] = {"ts": now, "dest": acted["level2"]["dest"], "orphan": False}
            suspects.pop(sid, None)
    summary["actions"][sid] = acted


def _process_candidate(g: dict, sid: str) -> None:
    """单候选判定：豁免三连（logical/keep/inflight）→判死四门→strikes 状态机→确认动作。"""
    summary = g["summary"]
    suspects = g["suspects"]
    raw = g["raw"]
    root = g["root"]
    keep = g["keep"]
    inflight = g["inflight"]
    pid_present = g["pid_present"]
    now = g["now"]
    summary["scanned"] += 1
    info = raw.get(sid)
    if isinstance(info, dict) and info.get("logical"):
        summary["skipped"][f"{sid}:logical"] = "W-29 长跑哨兵，永不收尾"
        suspects.pop(sid, None)
        return
    if sid in keep:
        summary["skipped"][f"{sid}:whitelist"] = "keep 清单"
        suspects.pop(sid, None)
        return
    if sid in inflight:
        summary["skipped"][f"{sid}:queue_inflight"] = "commit_queue 在飞，等袋落完"
        suspects.pop(sid, None)
        return
    claims = _session_claims(root, sid)
    dead, evidence = _death_evidence(sid, raw, claims, pid_present, now)
    if not dead:
        suspects.pop(sid, None)  # 任一门未过=「连续」中断，清零
        summary["skipped"][f"{sid}:gate"] = evidence
        return
    strikes = int(suspects.get(sid, {}).get("strikes", 0)) + 1
    suspects[sid] = {
        "strikes": strikes,
        "first_seen": suspects.get(sid, {}).get("first_seen", now),
        "evidence": evidence,
    }
    if strikes < _STRIKES_REQUIRED:
        summary["suspected"].append({"sid": sid, "strikes": strikes, "evidence": evidence})  # 首轮只 report 留观
        return
    summary["confirmed"].append(sid)
    _confirmed_actions(g, sid, info, claims)


def _process_orphans(g: dict) -> None:
    """孤儿目录面：无注册表条目且 mtime>7d 的 sessions/<sid> 归档（keep/inflight 豁免）。"""
    root = g["root"]
    summary = g["summary"]
    keep = g["keep"]
    inflight = g["inflight"]
    now = g["now"]
    execute = g["execute"]
    archived_ledger = g["archived_ledger"]
    for d in g["orphan_dirs"]:
        summary["scanned"] += 1
        dpath = root / _SESSIONS_REL / d
        try:
            age = now - dpath.stat().st_mtime
        except OSError:
            continue
        if d in keep or d in inflight or age <= _ORPHAN_DIR_AGE_S:
            summary["skipped"][f"{d}:orphan_keep"] = f"age={int(age)}s"
            continue
        summary["confirmed"].append(d)
        if not execute:
            summary["actions"][d] = {"would_level2_archive": True}
            continue
        r = _act_level2(root, d, orphan=True)
        summary["actions"][d] = r
        if r.get("archived"):
            archived_ledger[d] = {"ts": now, "dest": r["dest"], "orphan": True}


def run_cycle(
    repo_root: str | Path,
    *,
    now: float | None = None,
    execute: bool | None = None,
    force_shadow: bool = False,
) -> dict:
    """一轮会话收尾协调（判死四门→豁免过滤→动作分级→留痕）。

    Args:
        repo_root: 仓根（测试注入 tmp_path）。
        now: 时间锚（测试注入）。
        execute: 实弹开关；None=自动探测 data/runtime/session_closeout.live。
        force_shadow: True=强制 shadow（--dry-run），即使 live 开关在场。

    Returns:
        summary dict（同时落 alert jsonl 与 state.json）。
    """
    root = Path(repo_root)
    now = time.time() if now is None else now
    suspects: dict = {}  # strikes 状态机
    archived_ledger: dict = {}  # 本轮新归档账（增量并入 state.archived，cap 防无界）
    suspects_final = False  # 全量扫描完成才覆盖写 state（aborted 轮保留旧账）
    summary: dict[str, Any] = {
        "ts": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
        "mode": "shadow",
        "scanned": 0,
        "suspected": [],
        "confirmed": [],
        "actions": {},
        "merge_warned": [],
        "skipped": {},
        "errors": [],
    }
    g: dict[str, Any] = {
        "root": root,
        "now": now,
        "execute": execute,
        "summary": summary,
        "suspects": suspects,
        "archived_ledger": archived_ledger,
        "raw": {},
        "active": set(),
        "pid_present": set(),
        "inflight": set(),
        "keep": set(),
        "orphan_dirs": [],
    }
    try:
        if execute is None:
            execute = (root / _LIVE_FLAG_REL).exists()
        if force_shadow:
            execute = False
        g["execute"] = execute
        summary["mode"] = "live" if execute else "shadow"

        raw = _load_raw_registry(root)
        active = _active_session_ids(root)
        g["raw"] = raw
        if active is None:
            summary["errors"].append("registry-unreachable")
            _finalize(root, summary)
            return summary
        g["active"] = active
        if _index_locked(root):
            summary["skipped"]["round:index_locked"] = "git 写入在飞，整轮缩手"
            _finalize(root, summary)
            return summary
        g["pid_present"] = _pid_present_sessions(raw)
        g["inflight"] = _queue_inflight_sids(root)
        g["keep"] = _load_keep_sids(root)
        candidates, orphan_dirs = _scan_targets(g)
        g["orphan_dirs"] = orphan_dirs
        suspects, archived_ledger = _load_suspects_state(g)
        g["suspects"] = suspects
        g["archived_ledger"] = archived_ledger
        for sid in candidates:
            _process_candidate(g, sid)
        _process_orphans(g)
        suspects_final = True
    except Exception as e:  # noqa: BLE001 — 任一异常=本轮零动作+error（fail-safe 偏向不动作）
        summary["errors"].append(f"cycle-aborted:{type(e).__name__}:{e}")
    _finalize(root, summary, suspects if suspects_final else None, archived_ledger if suspects_final else None)
    return summary


def _finalize(root: Path, summary: dict, suspects: dict | None = None, archived: dict | None = None) -> None:
    """收尾留痕：state.json 原子写 + 告警账落一行（只记，不受 shadow/live 影响）。"""
    try:
        state = _load_state_file(root / _STATE_REL) or {"version": 1, "suspects": {}, "archived": {}}
        if summary["errors"]:
            state["last_error"] = {"ts": summary["ts"], "errors": summary["errors"]}
        if suspects is not None:
            state["suspects"] = suspects  # 本轮全量判定覆盖写；aborted 轮保留旧账
        if archived:
            merged = dict(state.get("archived") or {})
            merged.update(archived)
            state["archived"] = dict(sorted(merged.items(), reverse=False)[-_ARCHIVED_LEDGER_CAP:])
        state["last_cycle"] = {k: summary[k] for k in ("ts", "mode", "scanned", "confirmed", "merge_warned")}
        _persist_state(root / _STATE_REL, state)
    except Exception:  # noqa: BLE001 — 留痕失败不反噬主流程
        pass
    try:
        rec = {
            "ts": summary["ts"],
            "kind": "merge_warn" if summary.get("merge_warned") else "cycle",
            "mode": summary["mode"],
            "scanned": summary["scanned"],
            "suspected": summary["suspected"],
            "confirmed": summary["confirmed"],
            "actions": summary["actions"],
            "merge_warned": summary["merge_warned"],
            "skipped": summary["skipped"],
        }
        if summary["errors"]:
            rec["kind"] = "error"
            rec["errors"] = summary["errors"]
        _write_alert_line(root / _ALERT_REL, rec)
    except Exception:  # noqa: BLE001
        pass


def _print_status(repo_root: Path) -> int:
    """--status：state.json 摘要 + 最近告警行（只读）。"""
    root = Path(repo_root)
    state = _load_state_file(root / _STATE_REL)
    if not state:
        print("never_run=true（无 state.json，等待 reaper 脉冲或手工首跑）")
        return 0
    print(f"last_cycle={json.dumps(state.get('last_cycle'), ensure_ascii=False)}")
    suspects = state.get("suspects", {})
    print(f"suspects={len(suspects)}")
    for sid, s in list(suspects.items())[:10]:
        print(f"  {sid} strikes={s.get('strikes')} evidence={s.get('evidence')}")
    archived = state.get("archived", {})
    print(f"archived_total={len(archived)}")
    for sid, a in list(archived.items())[-5:]:
        print(f"  {sid} -> {a.get('dest')} orphan={a.get('orphan')}")
    if state.get("last_error"):
        print(f"last_error={json.dumps(state['last_error'], ensure_ascii=False)}")
    alert = root / _ALERT_REL
    if alert.exists():
        lines = alert.read_text(encoding="utf-8").splitlines()[-3:]
        print(f"recent_alerts={len(lines)}行（{alert.name} 尾部）")
        for ln in lines:
            print(f"  {ln[:200]}")
    live = "ON" if (root / _LIVE_FLAG_REL).exists() else "OFF（shadow）"
    print(f"live_switch={live}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="会话收尾协调器（RB-3 治本；默认 shadow 只判只记不动作）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--once", action="store_true", help="跑一轮协调（reaper 脉冲调用形态；shadow 除非 --execute/live 开关）"
    )
    group.add_argument("--dry-run", action="store_true", help="强制 shadow 判定一轮（验证用，live 开关在场也不动作）")
    group.add_argument("--status", action="store_true", help="读 state.json 摘要与最近告警（只读）")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实弹执行动作（或建 data/runtime/session_closeout.live 开关；首版保守默认 shadow）",
    )
    parser.add_argument("--json", action="store_true", help="stdout 输出 summary JSON（reaper 捕获用）")
    args = parser.parse_args(argv)

    if args.status:
        return _print_status(_PROJECT_ROOT)

    if not (args.once or args.dry_run):
        parser.print_help()
        return _EXIT_ERROR

    summary = run_cycle(_PROJECT_ROOT, execute=True if args.execute else None, force_shadow=args.dry_run)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(
            f"mode={summary['mode']} scanned={summary['scanned']} "
            f"suspected={len(summary['suspected'])} confirmed={len(summary['confirmed'])} "
            f"merge_warned={len(summary['merge_warned'])} errors={len(summary['errors'])}"
        )
    if summary["errors"]:
        return _EXIT_ERROR
    return _EXIT_PENDING if (summary["suspected"] or summary["confirmed"] or summary["merge_warned"]) else _EXIT_OK


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 死会话收尾协调器（reaper 脉冲 subprocess 调用 + 人工复跑取证双形态，非常驻自走时钟）
    sys.exit(main())
