# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-WORKTREE-WRITE-INTEGRITY-001
# [MODULE] zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.infra.process_pool (spawn_python_hidden/is_pid_alive); zephyr.shared.io.paths (anchor_main_root); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.governance.audit.reconciliation_registry (_log_reconcile_results)
# [CONSUMERS] git_commit_gateway (_register_default_reconcilers: make_worktree_drift_watchdog_reconciler); CLI python -m ... [--once|--daemon|--status]
# [STARTUP] manual / post-commit reconciler ensure-daemon
# [MATURITY] production
# [INVARIANTS] 锚主仓工作区（anchor_main_root）；只告警不阻断（fail-open 不干扰主流程）；快照先于告警；审计写 .runtime/audit/（永不回 tracked 区）；同签名告警去重；漂移消解自动写 clean 自愈消音
# [MODIFY-GUARD] scan_once 判定逻辑（claimed/grace/dedup/self-heal 四路分流）；快照目录格式 .runtime/quarantine/drift_<ts>/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可达/DB 故障→降级 skip 不告警；daemon 循环异常写 lifecycle log 后 continue
# [TESTS] tests/governance/rule_bridge/test_worktree_drift_watchdog.py
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
# noqa: m10-time-trigger  M10豁免: daemon 循环是看门狗生命周期（同 heartbeat_daemon 先例），非业务周期触发
# noqa: m11-perm-manual-legitimate  M11豁免: post-commit reconciler ensure-spawn 的 detached daemon，非独立永久系统
"""
worktree_drift_watchdog.py — 工作区 tracked 漂移看门狗（#ARCH-WORKTREE-WRITE-INTEGRITY-001 P0-1/P0-2）

第一性原理
----------
commit 层有网关+串行锁+审计，工作区写层曾是三不管地带（无版本前置/无审计/无主动
检测）——陈旧缓冲区覆写（#68/#71/#75 族）把 tracked 文件写回旧内容时，发现靠运气、
归因无证据。本看门狗把"发现靠运气"变成"发现靠机制"：

  1. 周期性比对 tracked 文件的工作区内容与 HEAD/基线（git hash-object 语义级比对，
     CRLF 幻影天然免疫）
  2. 发现**未登记写入方**造成的内容变化：先快照存证 → 再告警（reconcile_execution_log
     critical_warn，网关 banner 自动浮现）→ 落归因审计（前后 hash + 活跃会话 + claim 归属）
  3. 漂移消解（文件回到 HEAD 或被提交）自动写 clean 记录——auto-ack 机制消音，
     无告警疲劳

四路分流（scan_once 判定）
-------------------------
- claimed：文件在活跃 session 的 claim 快照中 → 合法 WIP，不告警只记录
- grace：最近一次 commit 后 GRACE_SECONDS 内 → post-commit reconciler 合法派生写窗口，不告警只记录
- dedup：漂移内容相对上一周期未变 → 同签名不重复告警
- alert：以上皆非 → 未登记写入方实锤 → 快照 + critical_warn + 归因审计

自愈：已告警文件回到干净态（diff 消失或 HEAD 推进吸收）→ clean 记录，既有
critical_warn 被 auto-ack-healed 消音。

Usage::

    python -m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog <root> --once
    python -m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog <root> --daemon
    python -m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog <root> --status
"""

from __future__ import annotations

__all__: Final = [
    "GATE_ID",
    "scan_once",
    "run_daemon",
    "ensure_daemon",
    "make_worktree_drift_watchdog_reconciler",
]

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

GATE_ID = "GATE-WORKTREE-DRIFT-WATCHDOG"

_SCAN_INTERVAL = 60  # daemon 扫描间隔（秒）
_GRACE_AFTER_COMMIT = 600  # commit 后派生写宽限窗（秒）——reconciler 合法回写期
_IDLE_EXIT_SECONDS = 1800  # 无活跃 session 持续此秒数后 daemon 退出（同 heartbeat 活性锚语义）
_STATE_DIR = ".runtime/drift_watchdog"
_AUDIT_DIR = ".runtime/audit"
_QUARANTINE_DIR = ".runtime/quarantine"


# ── git 原语（全部经 run_subprocess_hidden，禁裸 subprocess 直调）────────────────


def _git(root: Path, args: list[str]) -> tuple[int, str]:
    """执行只读 git 命令，返回 (returncode, stdout)。失败返回 (rc, '') 不抛异常。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    try:
        r = run_subprocess_hidden(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=30,
        )
        return r.returncode, (r.stdout or "")
    except Exception as e:  # noqa: BLE001 — git 不可达降级
        logger.debug("git %s failed: %s", args[:1], e)
        return 2, ""


def _head_sha(root: Path) -> str:
    rc, out = _git(root, ["rev-parse", "HEAD"])
    return out.strip() if rc == 0 else ""


def _dirty_tracked(root: Path) -> list[str]:
    """tracked 修改清单（porcelain 双列 M/A/D/R；untracked ?? 不关心）。"""
    rc, out = _git(root, ["status", "--porcelain=v1", "--untracked-files=no"])
    if rc != 0:
        return []
    files: list[str] = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:  # rename: 取新路径
            path = path.split(" -> ", 1)[1]
        files.append(path.strip().strip('"'))
    return files


def _real_drift(root: Path, rel: str) -> bool:
    """语义级内容差异判定（git diff --quiet：CRLF 幻影/权限位噪音返回 False）。"""
    rc1, _ = _git(root, ["diff", "--quiet", "--", rel])
    rc2, _ = _git(root, ["diff", "--cached", "--quiet", "--", rel])
    return rc1 != 0 or rc2 != 0


def _work_hash(root: Path, rel: str) -> str:
    """工作区内容的 git blob hash（与 HEAD blob 同口径可比）。"""
    rc, out = _git(root, ["hash-object", "--", rel])
    return out.strip() if rc == 0 else ""


def _head_blob(root: Path, rel: str) -> str:
    rc, out = _git(root, ["rev-parse", f"HEAD:{rel}"])
    return out.strip() if rc == 0 else ""


# ── 归属判定（活跃 session + claim 快照）──────────────────────────────────────


def _active_sessions_and_claims(root: Path) -> tuple[list[str], dict[str, str]]:
    """返回 (活跃 session id 清单, {被 claim 文件: session_id})。

    claim 快照是网关 claim_files 的持久化（.runtime/claim_snapshots/<sid>.json），
    只统计当前活跃 session 的 claim——死 session 的 claim 不构成合法写入授权。
    """
    sessions: list[str] = []
    try:
        from zephyr.security.access_control.session_concurrency import (  # noqa: PLC0415
            SessionRegistry,
        )

        sessions = [s.session_id for s in SessionRegistry(root).list_active()]
    except Exception as e:  # noqa: BLE001 — registry 故障降级空清单（不误豁免）
        logger.debug("session registry query failed: %s", e)
    claimed: dict[str, str] = {}
    snap_dir = root / ".runtime" / "claim_snapshots"
    if snap_dir.is_dir():
        active = set(sessions)
        for snap in snap_dir.glob("*.json"):
            sid = snap.stem
            if sid.endswith("_adopted") or sid not in active:
                continue
            try:
                data = json.loads(snap.read_text(encoding="utf-8"))
                for f in data.get("files", []):
                    claimed[str(f)] = sid
            except Exception:  # noqa: BLE001 — 单个快照损坏不影响其他
                continue
    return sessions, claimed


# ── 状态/审计/快照/告警 ──────────────────────────────────────────────────────


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_path(root: Path) -> Path:
    return root / _STATE_DIR / "state.json"


def _load_state(root: Path) -> dict:
    try:
        return json.loads(_state_path(root).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 首跑/损坏回全新基线
        return {"files": {}, "alerted": {}}


def _save_state(root: Path, state: dict) -> None:
    p = _state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)  # 原子写，防半状态


def _audit(root: Path, record: dict) -> None:
    """归因审计（P0-2）：.runtime/audit/worktree_drift_watchdog.jsonl，永不回 tracked 区。"""
    try:
        d = root / _AUDIT_DIR
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "worktree_drift_watchdog.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("drift watchdog audit append failed: %s", e)


def _snapshot(root: Path, rel: str, work_hash: str) -> str:
    """快照存证：漂移内容复制到 .runtime/quarantine/drift_<ts>/<rel>（先存证后告警）。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    dest = root / _QUARANTINE_DIR / f"drift_{ts}" / rel
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        src = root / rel
        if src.is_file():
            dest.write_bytes(src.read_bytes())
        return str(dest.relative_to(root))
    except OSError as e:
        logger.warning("drift snapshot failed: %s (%s)", e, rel)
        return ""


def _log_results(root: Path, action: str, detail: str) -> None:
    """写 reconcile_execution_log（critical_warn→banner 自动浮现；clean→auto-ack 消音）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import (  # noqa: PLC0415
            ReconcileResult,
            _log_reconcile_results,
        )

        _log_reconcile_results(
            str(root),
            [ReconcileResult(action=action, detail=detail, gate_id=GATE_ID)],
            "drift-watchdog",
            trigger_source="watchdog_daemon",
        )
    except Exception as e:  # noqa: BLE001 — 告警落库失败不阻断（审计已留痕）
        logger.warning("drift watchdog log_results failed: %s", e)


# ── 扫描主逻辑 ────────────────────────────────────────────────────────────────


def scan_once(project_root: str | Path, *, grace_seconds: int = _GRACE_AFTER_COMMIT) -> dict:
    """单周期扫描：tracked 漂移四路分流（claimed/grace/dedup/alert）+ 自愈。

    Args:
        project_root: 项目根（worktree 调用自动锚主仓——监视对象恒为主仓工作区）。
        grace_seconds: commit 后派生写宽限窗。

    Returns:
        摘要 dict：{scanned, drifted, alerted, claimed, grace_suppressed, dedup_skipped, healed}。
    """
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())
    summary = {
        "scanned": 0,
        "drifted": 0,
        "alerted": 0,
        "claimed": 0,
        "grace_suppressed": 0,
        "dedup_skipped": 0,
        "healed": 0,
        "merge_suppressed": 0,
    }
    head_sha = _head_sha(root)
    if not head_sha:
        return summary  # git 不可达→本轮 skip（fail-open）

    state = _load_state(root)
    files_state: dict = state.setdefault("files", {})
    alerted: dict = state.setdefault("alerted", {})

    # B5 治本（2026-08-19）：merge 存续期豁免——MERGE_HEAD 存在期间工作区≠HEAD 是
    # git 机制设计（merge --no-commit 晾置/冲突待决），写入方是 git 自身，无 claim
    # 可登记，原判据必误报 critical_warn（gateway commit banner 刷屏实证）。
    # 判据复用 AI-R1-003 原语（rev-parse --git-path，互指 gateway._is_merge_in_progress）；
    # 豁免期 audit 照记 verdict=merge_suppressed，MERGE_HEAD 消解后下轮恢复监视。
    rc, mh_rel = _git(root, ["rev-parse", "--git-path", "MERGE_HEAD"])
    merge_in_progress = False
    if rc == 0 and mh_rel.strip():
        mh_path = Path(mh_rel.strip())
        if not mh_path.is_absolute():
            mh_path = root / mh_path
        merge_in_progress = mh_path.exists()

    # 最近一次 commit 时间（宽限窗锚点）
    # B5 治本：锚点扩展——HEAD reflog（merge/checkout/stash pop 回写都刷新）与
    # stash reflog（stash push/drop）一并纳入，stash 周期/gateway 正常操作的
    # 合法回写走 grace_suppressed 而非 alert；超窗未消解的真漂移照常 alert（安全网不破）。
    rc, out = _git(root, ["log", "-1", "--format=%ct"])
    anchors = [float(out.strip()) if rc == 0 and out.strip() else 0.0]
    rc, out = _git(root, ["reflog", "-1", "--format=%ct"])
    anchors.append(float(out.strip()) if rc == 0 and out.strip() else 0.0)
    rc, out = _git(root, ["reflog", "-1", "--format=%ct", "stash"])
    anchors.append(float(out.strip()) if rc == 0 and out.strip() else 0.0)
    in_grace = (now_utc().timestamp() - max(anchors)) < grace_seconds

    sessions, claimed = _active_sessions_and_claims(root)
    dirty = _dirty_tracked(root)
    summary["scanned"] = len(dirty)
    seen_drift: set[str] = set()

    for rel in dirty:
        if not _real_drift(root, rel):
            continue  # CRLF 幻影/模式位噪音
        summary["drifted"] += 1
        seen_drift.add(rel)
        wh = _work_hash(root, rel)
        hb = _head_blob(root, rel)
        prev = files_state.get(rel, {})
        base = {
            "ts": _now_iso(),
            "file": rel,
            "work_hash": wh,
            "head_blob": hb,
            "prev_work_hash": prev.get("work_hash", ""),
            "head_sha": head_sha,
            "active_sessions": sessions,
            "claimed_by": claimed.get(rel, ""),
        }
        if prev.get("work_hash") == wh:
            summary["dedup_skipped"] += 1  # 同签名漂移持续，不重复告警
            continue
        if rel in claimed:
            summary["claimed"] += 1
            _audit(root, {**base, "verdict": "claimed"})
        elif merge_in_progress:
            # B5：merge 存续期豁免（audit 照记不告警，MERGE_HEAD 消解后恢复监视）
            summary["merge_suppressed"] += 1
            _audit(root, {**base, "verdict": "merge_suppressed"})
        elif in_grace:
            summary["grace_suppressed"] += 1
            _audit(root, {**base, "verdict": "grace_suppressed"})
        else:
            snap = _snapshot(root, rel, wh)
            detail = (
                f"未登记写入方致 tracked 文件内容漂移: {rel} "
                f"(work {prev.get('work_hash', '∅')[:8]}→{wh[:8]}, HEAD blob {hb[:8]}, "
                f"快照 {snap or '失败'}, 活跃会话 {','.join(sessions) or '无'}，非 claim 非宽限窗）"
            )
            _log_results(root, "critical_warn", detail)
            _audit(root, {**base, "verdict": "alerted", "snapshot": snap})
            alerted[rel] = wh
            summary["alerted"] += 1
        files_state[rel] = {"work_hash": wh, "head_blob": hb, "last_seen": _now_iso()}

    # 自愈：曾告警文件本轮已干净（diff 消失=恢复/HEAD 推进=已提交吸收）
    for rel, sig in list(alerted.items()):
        if rel not in seen_drift:
            _log_results(root, "clean", f"tracked 漂移已消解: {rel}（alert 签名 {sig[:8]}）")
            _audit(
                root,
                {"ts": _now_iso(), "file": rel, "verdict": "healed", "head_sha": head_sha, "active_sessions": sessions},
            )
            del alerted[rel]
            files_state.pop(rel, None)
            summary["healed"] += 1

    _save_state(root, state)
    return summary


# ── daemon 生命周期（模式同 heartbeat_daemon）────────────────────────────────


def _pid_path(root: Path) -> Path:
    return root / _STATE_DIR / "watchdog.pid"


def _lifecycle_log(root: Path, status: str, extra: dict | None = None) -> None:
    rec = {"ts": _now_iso(), "pid": os.getpid(), "status": status}
    if extra:
        rec.update(extra)
    try:
        d = root / _STATE_DIR
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "watchdog.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def ensure_daemon(project_root: str | Path, interval: int = _SCAN_INTERVAL) -> bool:
    """确保看门狗 daemon 在跑（post-commit reconciler 事件轨调用点）。

    幂等：PID 文件存活则直接返回；否则 detached spawn 并写 PID 文件。
    B1/R1 治本（2026-08-19）：pytest 测试体内不 spawn 真实看门狗——实测单轮
    governance 套件泄漏 61 个 daemon 驻留主仓并发扫描（xdist 尾部资源风暴放大器，
    活体抓现场实证）。需要覆盖 daemon 生命周期的测试用 monkeypatch/真 spawn 显式管理。
    """
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logger.debug("watchdog ensure_daemon: pytest env, skip real daemon spawn")
        return True
    from zephyr.shared.infra.process_pool import (  # noqa: PLC0415
        is_pid_alive,
        spawn_python_hidden,
    )
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())
    pid_file = _pid_path(root)
    try:
        if pid_file.is_file():
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            if is_pid_alive(pid):
                return True
    except (OSError, ValueError):
        pass
    log_path = str(root / _STATE_DIR / "watchdog_stdout.log")
    (root / _STATE_DIR).mkdir(parents=True, exist_ok=True)
    proc = spawn_python_hidden(
        [
            sys.executable,
            "-m",
            "zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog",
            str(root),
            "--daemon",
            "--interval",
            str(interval),
        ],
        cwd=str(root),
        stdout_path=log_path,
        stderr_path=log_path,
    )
    try:
        pid_file.write_text(str(proc.pid), encoding="utf-8")
    except OSError:
        pass
    _lifecycle_log(root, "spawned", {"pid": proc.pid, "interval": interval})
    return True


def _acquire_single_instance_lock(root: Path):
    """单实例互斥锁（#99：防 Task Scheduler RestartOnFailure 连环拉起堆积）。

    非阻塞字节锁：拿不到锁=已有实例在岗，返回 None，调用方应立即退出。
    拿到锁的实例持有文件句柄直至进程退出（OS 自动释放，含崩溃场景——
    句柄随进程句柄表关闭而释放，无死锁残留）。
    """
    import msvcrt  # noqa: PLC0415 — Windows 专用锁（本项目运行环境=Windows 计划任务）

    lock_path = root / _STATE_DIR / "watchdog.lock"
    try:
        (root / _STATE_DIR).mkdir(parents=True, exist_ok=True)
        fh = open(lock_path, "a+b")  # noqa: SIM115 — 句柄须随进程生命周期持有，不可 with 关闭
        try:
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            fh.close()
            return None
        return fh
    except OSError:
        return None


def run_daemon(project_root: str | Path, interval: int = _SCAN_INTERVAL) -> int:
    """看门狗主循环：周期 scan_once；无活跃 session 超 _IDLE_EXIT_SECONDS 自动退出。"""
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())
    globals()["_WD_ROOT"] = str(root)

    # #99 单实例闸：第二实例（Task Scheduler 复发拉起）拿到锁失败即退，零堆积
    _lock_fh = _acquire_single_instance_lock(root)
    if _lock_fh is None:
        _lifecycle_log(root, "skipped", {"reason": "another instance already running (#99 single-instance lock)"})
        return 0
    globals()["_WD_LOCK_FH"] = _lock_fh  # 防 GC 关句柄释放锁——随进程生命周期持有

    def _on_signal(signum, frame):  # noqa: ANN001, ANN202
        _lifecycle_log(root, "interrupted", {"signal": signum})
        sys.exit(0)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _on_signal)
        except (ValueError, OSError):
            pass

    _lifecycle_log(root, "started", {"interval": interval})
    idle_since = now_utc().timestamp()
    while True:
        try:
            summary = scan_once(root)
            sessions, _ = _active_sessions_and_claims(root)
            if sessions:
                idle_since = now_utc().timestamp()
            elif now_utc().timestamp() - idle_since > _IDLE_EXIT_SECONDS:
                _lifecycle_log(root, "exited", {"reason": "no active sessions idle timeout"})
                return 0
            if summary.get("alerted"):
                _lifecycle_log(root, "alerted", summary)
            time.sleep(interval)
        except SystemExit:
            return 0
        except Exception as e:  # noqa: BLE001 — daemon 不崩溃，写下轮继续
            _lifecycle_log(root, "error", {"error": str(e)[:200]})
            time.sleep(5)


# ── post-commit reconciler 接入（事件轨 spawn 点）────────────────────────────


def make_worktree_drift_watchdog_reconciler(gateway: object):
    """构造 GATE-WORKTREE-DRIFT-WATCHDOG post-commit reconciler（ensure-daemon + 即时一扫）。

    trigger：任何非空 commit（漂移与开发活跃正相关，commit 后是 ensure 的合适时机）。
    动作：ensure_daemon（幂等）+ scan_once 即时扫描（commit 后 HEAD 已推进，合法
    派生写在宽限窗内不告警）。只记录不阻断（warn-only 语义，fail-open）。
    """
    from zephyr.governance.audit.reconciliation_registry import (  # noqa: PLC0415
        ReconcileResult,
        ReconcilerSpec,
    )

    project_root = str(getattr(gateway, "project_root", "."))

    def _trigger(committed_files: list[str]) -> bool:
        return bool(committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> "ReconcileResult":
        try:
            ensure_daemon(project_root)
            summary = scan_once(project_root)
            detail = (
                f"drift watchdog: scanned={summary['scanned']} drifted={summary['drifted']} "
                f"alerted={summary['alerted']} claimed={summary['claimed']} "
                f"grace={summary['grace_suppressed']} healed={summary['healed']}"
            )
            action = "warn" if summary["alerted"] else "clean"
            return ReconcileResult(action=action, detail=detail, gate_id=GATE_ID)
        except Exception as e:  # noqa: BLE001 — reconciler 异常降级 warn 不阻断
            return ReconcileResult(action="warn", detail=f"drift watchdog error: {e}", gate_id=GATE_ID)

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=845,
        file_ops=frozenset({"read", "write"}),  # 读 tracked 区 + 写 .runtime（快照/审计/状态）
    )


# ── CLI ───────────────────────────────────────────────────────────────────────


def _status(root: Path) -> int:
    state = _load_state(root)
    alerted = state.get("alerted", {})
    pid_file = _pid_path(root)
    pid = 0
    alive = False
    if pid_file.is_file():
        try:
            from zephyr.shared.infra.process_pool import is_pid_alive  # noqa: PLC0415

            pid = int(pid_file.read_text(encoding="utf-8").strip())
            alive = is_pid_alive(pid)
        except (OSError, ValueError):
            pass
    print(
        json.dumps(
            {
                "daemon_pid": pid,
                "daemon_alive": alive,
                "active_alerts": len(alerted),
                "alerted_files": sorted(alerted),
                "state_file": str(_state_path(root)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if alerted else 0


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="工作区 tracked 漂移看门狗")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--once", action="store_true", help="单周期扫描")
    parser.add_argument("--daemon", action="store_true", help="daemon 主循环")
    parser.add_argument("--status", action="store_true", help="状态查询")
    parser.add_argument("--interval", type=int, default=_SCAN_INTERVAL)
    args = parser.parse_args()

    _root = Path(args.project_root).resolve()
    if args.status:
        sys.exit(_status(_root))
    if args.daemon:
        sys.exit(run_daemon(_root, args.interval))
    # 默认 --once
    _summary = scan_once(_root)
    print(json.dumps(_summary, ensure_ascii=False))
    sys.exit(1 if _summary.get("alerted") else 0)
