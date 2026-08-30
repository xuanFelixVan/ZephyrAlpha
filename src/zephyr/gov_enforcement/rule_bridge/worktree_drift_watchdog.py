# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-WORKTREE-WRITE-INTEGRITY-001
# [MODULE] zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.infra.process_pool (spawn_python_hidden/is_pid_alive); zephyr.shared.io.paths (anchor_main_root); zephyr.security.access_control.session_concurrency (SessionRegistry); zephyr.governance.audit.reconciliation_registry (_log_reconcile_results)
# [CONSUMERS] git_commit_gateway (_register_default_reconcilers: make_worktree_drift_watchdog_reconciler); CLI python -m ... [--once|--daemon|--status]
# [STARTUP] manual / post-commit reconciler ensure-daemon
# [MATURITY] production
# [INVARIANTS] 锚主仓工作区（anchor_main_root）；只告警不阻断（fail-open 不干扰主流程）；快照先于告警；审计写 .runtime/（永不回 tracked 区）；同签名告警去重；漂移消解自动写 clean 自愈消音；#ARCH-264：critical_warn 唯一写者=daemon（网关即时扫 observe-only）；热文件 10s 快扫+interval 全量双频节拍；quarantine 30 天 retention 自管+带外删除 tamper 审计；#ARCH-304：恰好 1 个活跃注册会话→auto-claim 替代告警（归属无歧义），0/>1 会话或 claim 失败→维持原处置（fail-closed 不放松）
# [MODIFY-GUARD] scan_once 判定逻辑（claimed/grace/dedup/auto_claim/alert 分流 + observe-only 观察员模式 + hot_only 快扫过滤）；快照目录格式 .runtime/quarantine/drift_<ts>/；_sweep_quarantine 只清理 drift_<ts> 规范命名目录
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
- auto_claim（#ARCH-304）：全项目恰好 1 个活跃注册会话 → 漂移写入归属无歧义，
  走既有 claim_files(adopt_prior_work=True) 自动认领 + 审计留痕，替代告警处置
  （2026-08-31 实证：AI 会话直改 tracked 文件未先 claim 被处置致工作丢失——
  单会话时回退/告警是误伤，pave the road）；observe-only 模式不触发（O6 不落状态变更）
- alert：以上皆非（0 或 >1 活跃会话=归属歧义 / claim 失败）→ 未登记写入方实锤 →
  快照 + critical_warn + 归因审计（fail-closed，多会话歧义场景行为零变化）

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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Final

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

GATE_ID = "GATE-WORKTREE-DRIFT-WATCHDOG"

_SCAN_INTERVAL = 60  # daemon 全量扫描间隔（秒）
_HOT_SCAN_INTERVAL = 10  # 热文件快扫间隔（秒，#ARCH-264 O3-P0）
_GRACE_AFTER_COMMIT = 600  # commit 后派生写宽限窗（秒）——reconciler 合法回写期
_IDLE_EXIT_SECONDS = 1800  # 无活跃 session 持续此秒数后 daemon 退出（同 heartbeat 活性锚语义）
_STATE_DIR = ".runtime/drift_watchdog"
_AUDIT_DIR = ".runtime/audit"
_QUARANTINE_DIR = ".runtime/quarantine"
_QUARANTINE_RETENTION_DAYS = 30  # 快照保留天数（#ARCH-264 O4：watchdog 自管 retention）
_DESIGN_MEMO_PREFIX = "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/"
_KNOWN_QUARANTINE_CAP = 500  # known_quarantine 登记上限（防状态文件膨胀）


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


def _is_hot_rel(rel: str) -> bool:
    """热文件判定（#ARCH-264 O3-P0）：DEFAULT_HOT_FILES 单真源 ∪ design_memos/ 前缀。"""
    from zephyr.shared.io.file_utils import DEFAULT_HOT_FILES  # noqa: PLC0415

    return rel in DEFAULT_HOT_FILES or rel.startswith(_DESIGN_MEMO_PREFIX)


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
                files = data.get("files")
                if files is None:
                    # 网关 save_session_snapshot 持久化格式：
                    # {"session_id", "snapshots": {abs_path: baseline_diff}, "claim_head"}
                    # ——键归一化为仓相对 POSIX 路径，与扫描的 rel 对齐
                    files = []
                    for k in data.get("snapshots", {}):
                        try:
                            r = os.path.relpath(str(k), str(root)).replace(os.sep, "/")
                        except ValueError:
                            continue  # 跨盘符等异常路径不入豁免
                        if r.startswith(".."):
                            continue
                        files.append(r)
                for f in files:
                    claimed[str(f).replace("\\", "/")] = sid
            except Exception:  # noqa: BLE001 — 单个快照损坏不影响其他
                continue
    return sessions, claimed


def _auto_claim_single_session(root: Path, rel: str, session_id: str) -> bool:
    """#ARCH-304：单活跃会话归属无歧义 → 既有 claim_files(adopt_prior_work=True) 自动认领。

    认领走网关既有机制：SessionRegistry.claim_file（冲突检测）+ 基线快照持久化
    （.runtime/claim_snapshots/<sid>.json）+ adopt 审计（<sid>_adopted.jsonl，
    存空基线使 FOREIGN-CHANGE gate 放行且留痕）。每事件新构造网关实例（漂移是低频
    事件）——从磁盘加载最新快照，杜绝长驻缓存陈旧导致 release 后重 claim 漏持久化。
    任何异常/冲突返回 False，调用方回落原告警路径（fail-closed 不放松）。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
            GitCommitGateway,
        )

        gateway = GitCommitGateway(project_root=root)
        claimed = gateway.claim_files(session_id, [str(root / rel)], adopt_prior_work=True)
        if claimed:
            return True
        logger.warning(
            "drift watchdog auto-claim conflict: file=%s not claimable by session=%s",
            rel,
            session_id,
        )
        return False
    except Exception as e:  # noqa: BLE001 — claim 链路异常回落 alert（fail-closed）
        logger.warning("drift watchdog auto-claim failed: file=%s session=%s err=%s", rel, session_id, e)
        return False


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


def _write_audit_suspects(root: Path, rel: str) -> str:
    """#ARCH-279 裁定B2：WriteAudit 告警联动——漂移文件的 write_audit 同窗口嫌疑摘要。

    守护未跑/无事件/联动异常 → 空串（调用方不拼接，告警主流程零干扰）。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.write_audit_daemon import (  # noqa: PLC0415
            suspect_summary,
        )

        return suspect_summary(rel, root, seconds=120.0, limit=3)
    except Exception:  # noqa: BLE001 — 联动失败不阻断告警主流程
        return ""


def _sweep_quarantine(root: Path, retention_days: int = _QUARANTINE_RETENTION_DAYS) -> dict:
    """quarantine retention 自管（#ARCH-264 O4）：超期 drift_* 目录清理+逐条审计。

    只清理本家产物（drift_<ts> 命名规范目录）；非标准命名（人工存证等）不碰。
    """
    result = {"removed": 0, "kept": 0}
    qdir = root / _QUARANTINE_DIR
    if not qdir.is_dir():
        return result
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    for d in sorted(qdir.iterdir()):
        if not d.is_dir() or not d.name.startswith("drift_"):
            continue
        try:
            ts = datetime.strptime(d.name[len("drift_") :], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            result["kept"] += 1  # 命名不符不碰（人工存证目录豁免）
            continue
        if ts < cutoff:
            # 授权通道唯一化（O4②）：quarantine 已入 ops_guard 保护区，本家清扫
            # 走 safe_rmtree 硬断言授权通道（reparse 检测+前缀白名单+留痕），
            # 断言拒绝=不删（安全语义），下轮再试。
            from zephyr.shared.io.file_utils import safe_rmtree  # noqa: PLC0415

            try:
                safe_rmtree(d, allowed_prefix=root / _QUARANTINE_DIR, ignore_errors=True)
            except Exception:  # noqa: BLE001 — 授权通道异常不拖垮清扫循环
                result["kept"] += 1
                continue
            _audit(
                root,
                {
                    "ts": _now_iso(),
                    "verdict": "quarantine_retention_sweep",
                    "file": d.name,
                    "retention_days": retention_days,
                },
            )
            result["removed"] += 1
        else:
            result["kept"] += 1
    return result


def _maybe_sweep_quarantine(root: Path) -> None:
    """retention 清扫的日级节流入口（daemon 每全量周期调用）。"""
    state = _load_state(root)
    today = datetime.now(timezone.utc).date().isoformat()
    if state.get("quarantine_last_sweep") == today:
        return
    swept = _sweep_quarantine(root)
    state["quarantine_last_sweep"] = today
    _save_state(root, state)
    if swept["removed"]:
        _lifecycle_log(root, "quarantine_swept", swept)


# ── 扫描主逻辑 ────────────────────────────────────────────────────────────────


def scan_once(
    project_root: str | Path,
    *,
    grace_seconds: int = _GRACE_AFTER_COMMIT,
    alert_enabled: bool = True,
    hot_only: bool = False,
) -> dict:
    """单周期扫描：tracked 漂移四路分流（claimed/grace/dedup/alert）+ 自愈。

    Args:
        project_root: 项目根（worktree 调用自动锚主仓——监视对象恒为主仓工作区）。
        grace_seconds: commit 后派生写宽限窗。
        alert_enabled: #ARCH-264 O6 唯一告警写者——False 时 observe-only
            （只归因审计+快照存证，不写 critical_warn/clean、不推进告警状态），
            网关 post-commit 即时扫用此模式，critical_warn 由 daemon 单写。
        hot_only: #ARCH-264 O3-P0 热文件快扫——True 时只扫描
            DEFAULT_HOT_FILES ∪ design_memos/（daemon 10s 快扫周期用）。

    Returns:
        摘要 dict：{scanned, drifted, alerted, observed, claimed, auto_claimed, grace_suppressed, dedup_skipped, healed}。
    """
    from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

    root = anchor_main_root(Path(str(project_root)).resolve())
    summary = {
        "scanned": 0,
        "drifted": 0,
        "alerted": 0,
        "observed": 0,
        "claimed": 0,
        "auto_claimed": 0,
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

    # O4（#ARCH-264）：known_quarantine 登记快照目录被带外删除 → tamper 审计。
    # 仅 daemon（alert_enabled）执行——观察员模式不落状态变更。
    if alert_enabled:
        known_q: list = state.setdefault("known_quarantine", [])
        for d in list(known_q):
            if not (root / d).is_dir():
                _audit(
                    root,
                    {
                        "ts": _now_iso(),
                        "file": d,
                        "verdict": "quarantine_tamper",
                        "head_sha": head_sha,
                        "active_sessions": sessions,
                    },
                )
                known_q.remove(d)

    dirty = _dirty_tracked(root)
    if hot_only:
        dirty = [rel for rel in dirty if _is_hot_rel(rel)]
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
            # #ARCH-304（2026-08-31 裁定）：恰好 1 个活跃注册会话 → 漂移写入归属无歧义，
            # 走既有 claim_files(adopt_prior_work=True) 自动认领+审计留痕，替代告警处置；
            # 0/>1 活跃会话（归属歧义）或 claim 失败 → 维持原快照+告警路径（fail-closed
            # 不放松）。observe-only（alert_enabled=False）不触发——O6 观察员不落状态变更。
            if (
                alert_enabled
                and len(sessions) == 1
                and _auto_claim_single_session(root, rel, sessions[0])
            ):
                summary["auto_claimed"] += 1
                claimed[rel] = sessions[0]  # 本周期后续一致视为已认领
                _audit(
                    root,
                    {
                        **base,
                        "verdict": "auto_claimed",
                        "auto_claim_session": sessions[0],
                        "drift_hash": wh,
                    },
                )
                # fall through → files_state 推进（同签名下轮 dedup，不重复 claim）
            else:
                snap = _snapshot(root, rel, wh)
                if not alert_enabled:
                    # O6 observe-only：快照存证+归因审计照记，但不告警、不推进告警状态
                    _audit(root, {**base, "verdict": "observed", "snapshot": snap})
                    summary["observed"] += 1
                    continue  # 不更新 files_state/alerted——daemon 下轮仍按全状态告警，防吞
                detail = (
                    f"未登记写入方致 tracked 文件内容漂移: {rel} "
                    f"(work {prev.get('work_hash', '∅')[:8]}→{wh[:8]}, HEAD blob {hb[:8]}, "
                    f"快照 {snap or '失败'}, 活跃会话 {','.join(sessions) or '无'}，非 claim 非宽限窗）"
                )
                # #ARCH-279 裁定B2：WriteAudit 联动——告警附 write_audit 同窗口嫌疑清单
                # （PID→session_id 归因），守护未跑/无事件返回空串不拼接。
                wa_suspects = _write_audit_suspects(root, rel)
                if wa_suspects:
                    detail += f"；WriteAudit 嫌疑: {wa_suspects}"
                _log_results(root, "critical_warn", detail)
                _audit(root, {**base, "verdict": "alerted", "snapshot": snap, "write_audit_suspects": wa_suspects})
                alerted[rel] = wh
                if snap:
                    # O4：快照目录登记（带外删除可观测），容量封顶防状态膨胀
                    known_q = state.setdefault("known_quarantine", [])
                    known_q.append(snap)
                    del known_q[:-_KNOWN_QUARANTINE_CAP]
                summary["alerted"] += 1
        files_state[rel] = {"work_hash": wh, "head_blob": hb, "last_seen": _now_iso()}

    # 自愈：曾告警文件本轮已干净（diff 消失=恢复/HEAD 推进=已提交吸收）
    if alert_enabled:
        for rel, sig in list(alerted.items()):
            if hot_only and not _is_hot_rel(rel):
                continue  # 快扫周期不裁决非热文件自愈（留给全量周期）
            if rel not in seen_drift:
                _log_results(root, "clean", f"tracked 漂移已消解: {rel}（alert 签名 {sig[:8]}）")
                _audit(
                    root,
                    {
                        "ts": _now_iso(),
                        "file": rel,
                        "verdict": "healed",
                        "head_sha": head_sha,
                        "active_sessions": sessions,
                    },
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
    # O3-P0（#ARCH-264）：热文件 10s 快扫 + interval 全量扫描双频节拍。
    # 快扫只过 DEFAULT_HOT_FILES ∪ design_memos/（秒级覆写压进可观测窗）；
    # 全量周期照旧并顺带日级 retention 清扫（O4）。
    hot_interval = max(1, min(interval, _HOT_SCAN_INTERVAL))
    full_every = max(1, interval // hot_interval)
    tick = 0
    while True:
        try:
            tick += 1
            if tick % full_every == 0:
                summary = scan_once(root)
                _maybe_sweep_quarantine(root)
            else:
                summary = scan_once(root, hot_only=True)
            sessions, _ = _active_sessions_and_claims(root)
            if sessions:
                idle_since = now_utc().timestamp()
            elif now_utc().timestamp() - idle_since > _IDLE_EXIT_SECONDS:
                _lifecycle_log(root, "exited", {"reason": "no active sessions idle timeout"})
                return 0
            if summary.get("alerted"):
                _lifecycle_log(root, "alerted", summary)
            time.sleep(hot_interval)
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
            # #ARCH-279 裁定B1：WriteAudit 守护随 post-commit 链幂等挂载（已跑直接返回；
            # 挂载失败不阻断 drift watchdog 主流程）。
            try:
                from zephyr.gov_enforcement.rule_bridge.write_audit_daemon import (  # noqa: PLC0415
                    ensure_daemon as _ensure_write_audit,
                )

                _ensure_write_audit(project_root)
            except Exception:  # noqa: BLE001
                logger.debug("write_audit ensure_daemon skipped", exc_info=True)
            # O6（#ARCH-264）唯一告警写者：网关即时扫 observe-only（快照+归因审计照记，
            # 不写 critical_warn/clean、不推进告警状态）——critical_warn 由 daemon 单写，
            # 消除 daemon/网关双扫描同签名重复告警（实证 3 连同签名）。
            summary = scan_once(project_root, alert_enabled=False)
            detail = (
                f"drift watchdog(observe-only): scanned={summary['scanned']} drifted={summary['drifted']} "
                f"observed={summary['observed']} claimed={summary['claimed']} grace={summary['grace_suppressed']}"
            )
            return ReconcileResult(action="clean", detail=detail, gate_id=GATE_ID)
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
