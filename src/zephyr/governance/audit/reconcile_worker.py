# [BLUEPRINT] MOD-GOV_RECONCILE_WORKER | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] zephyr.governance.audit.reconcile_worker
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway); zephyr.governance.audit.reconciliation_registry (_log_reconcile_results); zephyr.governance.audit.reconcile_runner (write_status_file, STATUS_*); zephyr.security.access_control.session_concurrency (SessionRegistry)
# [CONSUMERS] zephyr.governance.audit.reconcile_runner.launch_reconcile_async (subprocess spawn)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] detached subprocess（父进程退出不影响 worker）；payload file 读取后立即删除；status file 流转 pending→running→done/failed；reconciler 异常降级为 warn 结果不阻断后续；worker 异常→status=failed+errors 持久化
# [MODIFY-GUARD] main 函数签名；payload file JSON schema；status file 写入时机（running 前后/done/failed）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] payload 不存在/JSON 解析失败→status=failed 立即退出；gateway 构造失败→status=failed；reconcile_for 内部异常已在 registry 层捕获
# [TESTS] tests/governance/audit/test_reconcile_async.py
# [A_module] module_id=MOD-GOV_RECONCILE_WORKER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 launch_reconcile_async 事件触发（非 cron/manual）
"""reconcile_worker.py — 异步 reconciler worker（Ruling:100PCT-AI-GOVERNANCE P2-3，2026-07-19）

由 ``reconcile_runner.launch_reconcile_async`` spawn 为 detached subprocess，
独立执行 post-commit reconciler 链路，结果写回 status file + reconcile_execution_log 表。

CLI
---
``python -m zephyr.governance.audit.reconcile_worker --payload <payload_path>``

payload file JSON schema
------------------------
::

    {
      "commit_sha": "abc123",
      "session_id": "sess-xxx",
      "project_root": "d:/ZephyrAlpha",
      "committed_files": ["d:/ZephyrAlpha/src/...", ...],
      "commit_message": "...",
      "started_at": 1234567890
    }

执行流程
--------
1. 读取 payload file（读后删）
2. 写 status=running
3. 构造 GitCommitGateway(project_root)
4. 调用 gateway._run_post_commit_reconcile_sync_worker(...)（不递归 spawn）
   - 内部走 reconcile_for + _log_reconcile_results（与同步路径相同）
5. 写 status=done（含 reconcilers_total/warn/auto_committed 统计）
6. 异常→写 status=failed（含 errors）→ exit 1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path


def _load_payload(payload_path: str) -> dict:
    """读取 payload file 并删除（读后即焚，避免残留）。"""
    p = Path(payload_path)
    if not p.exists():
        raise FileNotFoundError(f"payload file not found: {payload_path}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    finally:
        # 读后即焚（即使 JSON 解析失败也删，避免残留阻断下次）
        try:
            p.unlink()
        except OSError:
            pass
    return data


def _write_failed_status(
    project_root: str,
    commit_sha: str,
    session_id: str,
    started_at: int,
    errors: list[str],
) -> None:
    """写 status=failed（worker 异常退出兜底）+ 持久化到 DB。

    #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：
    之前 worker 启动失败只写 status file，不写 reconcile_execution_log 表，
    违反"所有 reconciler 失败结果必须持久化记录"铁律。现补 DB 持久化。
    """
    try:
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_FAILED,
            write_status_file,
        )
        write_status_file(
            project_root, commit_sha, STATUS_FAILED,
            session_id=session_id,
            started_at=started_at,
            finished_at=int(time.time()),
            errors=errors,
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — 兜底日志失败不阻断 exit
        pass

    # 持久化 worker 启动失败到 reconcile_execution_log 表（铁律：失败结果必须持久化）
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        detail = "; ".join(errors) if errors else "worker boot failed (unknown reason)"
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="critical_warn",
                detail=f"reconcile_worker boot failed (commit={commit_sha}): {detail}",
                gate_id="RECONCILE-WORKER-BOOT",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — DB 写入失败不阻断 exit
        pass




def _write_boot_success_clean(
    project_root: str,
    commit_sha: str,
    session_id: str,
) -> None:
    """worker boot 成功 → 对 RECONCILE-WORKER-BOOT gate_id 写 clean 记录（自愈）。

    #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 治本（2026-07-21）：
    之前 worker 成功路径只写 status file（STATUS_DONE），不写 reconcile_execution_log
    clean 记录，导致 RECONCILE-WORKER-BOOT critical_warn 永不自愈（告警生命周期不对称：
    失败写 critical_warn，成功不写 clean）。本函数补全对称性——同样操作（worker boot）
    成功执行证明之前失败已解决，写 clean 记录使活跃告警自动消解。

    语义：仅对 RECONCILE-WORKER-BOOT gate_id 写 clean，不影响其他 gate_id 的告警。
    幂等：多次成功写多条 clean 记录无副作用（SQL_SELECT_ACTIVE_CRITICAL_WARNS 只需
    一条 clean 即可消解对应 critical_warn）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="clean",
                detail=(
                    f"reconcile_worker boot succeeded (commit={commit_sha}) "
                    f"— auto-selfheal of prior RECONCILE-WORKER-BOOT critical_warn"
                ),
                gate_id="RECONCILE-WORKER-BOOT",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async",
        )
    except Exception:  # noqa: BLE001 — 自愈写入失败不阻断 worker 主流程
        pass

def _write_stale_healed_clean(
    project_root: str,
    commit_sha: str,
    session_id: str,
    started_at: int,
) -> None:
    """worker 到达终态（done/failed）且运行超阈值 → 写 RECONCILE-WORKER-STALE clean（自愈）。

    #ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 治本（2026-08-01）：
    补全 RECONCILE-WORKER-STALE gate 的配对 clean 写入器（对齐 _write_boot_success_clean
    先例）。sweep 在 worker 超阈值运行时记 live-timeout critical_warn（真 active threat）；
    worker 到达终态后 stuck 条件结束——写 clean 使 SQL_AUTO_ACK_HEALED_BY_GATE 自然 ack
    历史 critical_warn，补全告警生命周期对称性（死孤儿 clean 由 sweep 收割时写，本函数
    补 worker 自然终态的 clean——两条 clean 路径覆盖 worker 生命周期的两种结束方式）。

    仅当 worker 实际运行超阈值时写——快 worker 不触发 live-timeout，无需 clean
    （避免每 commit 写一条噪音 clean）。幂等：多次写多条 clean 无副作用。
    """
    try:
        # 复用 reconcile_runner 阈值真源（同包私有常量，对齐 reconciler_health_gate
        # 跨模块复用 _check_recent_blocks 的先例，不复制阈值避免双真源漂移）。
        from zephyr.governance.audit.reconcile_runner import _STALE_THRESHOLD_SECONDS
        elapsed = int(time.time()) - started_at
        if elapsed <= _STALE_THRESHOLD_SECONDS:
            return  # 未超阈值，sweep 不会写 live-timeout critical_warn，无需自愈
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )
        _log_reconcile_results(
            project_root,
            [ReconcileResult(
                action="clean",
                detail=(
                    f"reconcile_worker reached terminal state after {elapsed}s "
                    f"(>threshold {_STALE_THRESHOLD_SECONDS}s, commit={commit_sha}) "
                    f"— auto-selfheal of prior RECONCILE-WORKER-STALE live-timeout critical_warn"
                ),
                gate_id="RECONCILE-WORKER-STALE",
            )],
            session_id or "unknown",
            trigger_source="post_commit_async_stale_healed",
        )
    except Exception:  # noqa: BLE001 — 自愈写入失败不阻断 worker 主流程
        pass

def _register_worker_session(project_root: str, commit_sha: str) -> str:
    """Register worker as a logical session in SessionRegistry.

    #ARCH-RECONCILER-WORKER-SESSION-001 Phase C (2026-07-22):
    Workers were not registered as sessions, causing:
    1. No concurrency control (unlimited parallel workers → resource exhaustion)
    2. Worker auto-commits flagged as "session not registered" (warn-only path)

    Returns:
        worker_session_id (worker-{sha8}-{pid}) for later unregister.
        Registration failure is non-fatal (worker still runs, just untracked).
    """
    worker_sid = f"worker-{commit_sha[:8]}-{os.getpid()}"
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        registry.register(worker_sid, pid=os.getpid())
    except Exception:  # noqa: BLE001 — registration failure doesn't block worker
        pass
    return worker_sid


def _unregister_worker_session(project_root: str, worker_sid: str) -> None:
    """Unregister worker session from SessionRegistry (best-effort cleanup).

    #ARCH-RECONCILER-WORKER-SESSION-001 Phase C (2026-07-22):
    Ensures worker sessions don't leak (TTL=3600s is long; explicit unregister
    on completion keeps list_active() accurate for concurrency control).
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        registry = SessionRegistry(project_root)
        registry.unregister(worker_sid)
    except Exception:  # noqa: BLE001
        pass


def _run_worker(payload: dict) -> int:
    """worker 主流程，返回 exit code（0=成功，1=失败）。"""
    from zephyr.governance.audit.reconcile_runner import (
        STATUS_DONE,
        STATUS_RUNNING,
        write_status_file,
    )

    commit_sha: str = payload.get("commit_sha", "")
    session_id: str = payload.get("session_id", "")
    project_root: str = payload.get("project_root", "")
    committed_files: list[str] = payload.get("committed_files", [])
    commit_message: str = payload.get("commit_message", "")
    started_at: int = payload.get("started_at") or int(time.time())

    if not commit_sha or not project_root:
        _write_failed_status(
            project_root or ".",
            commit_sha or "unknown",
            session_id,
            started_at,
            ["payload missing commit_sha or project_root"],
        )
        return 1

    # 1. 写 status=running
    write_status_file(
        project_root, commit_sha, STATUS_RUNNING,
        session_id=session_id,
        started_at=started_at,
        trigger_source="post_commit_async",
        worker_pid=os.getpid(),
    )

    # 1.5 注册为逻辑 session（#ARCH-RECONCILER-WORKER-SESSION-001 Phase C）
    #     使 launch_reconcile_async 能通过 list_active() 计数活跃 worker 实现并发控制。
    worker_sid = _register_worker_session(project_root, commit_sha)

    try:
        # 2. 构造 GitCommitGateway（注册全部 reconciler）
        try:
            # 延迟 import 避免 reconcile_runner import 时拉起 gateway
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
                GitCommitGateway,
            )
            gateway = GitCommitGateway(Path(project_root))
        except Exception as e:  # noqa: BLE001
            _write_failed_status(
                project_root, commit_sha, session_id, started_at,
                [f"GitCommitGateway init failed: {e}", traceback.format_exc()],
            )
            return 1

        # 3. 执行 reconciler 链路（直接调内部同步方法，不递归 spawn）
        #    _run_post_commit_reconcile_sync_worker 是 P2-3 新增的 worker-only 入口，
        #    跳过 async dispatch（避免 worker 自己又 spawn 一个 worker）。
        try:
            # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
            # 注入 heartbeat 闭包——每个 reconciler 执行前刷新 status file 心跳字段，
            # 使外部观测者可区分 live worker（心跳新鲜）与 死亡 worker（心跳陈旧）。
            from zephyr.governance.audit.reconcile_runner import write_heartbeat

            def _hb(gate_id: str, _root=project_root, _sha=commit_sha) -> None:
                write_heartbeat(_root, _sha, gate_id)

            reconcile_results = gateway._run_post_commit_reconcile_sync_worker(
                committed_files, session_id, commit_message,
                heartbeat=_hb,
            )
        except Exception as e:  # noqa: BLE001 — 兜底
            _write_failed_status(
                project_root, commit_sha, session_id, started_at,
                [f"reconcile_for failed: {e}", traceback.format_exc()],
            )
            return 1

        # 4. 统计结果
        total = len(reconcile_results)
        warn_count = sum(1 for r in reconcile_results if getattr(r, "action", "") == "warn")
        auto_count = sum(
            1 for r in reconcile_results if getattr(r, "action", "") == "auto_committed"
        )
        errors: list[str] = [
            getattr(r, "detail", "")
            for r in reconcile_results
            if getattr(r, "action", "") == "warn" and getattr(r, "detail", "")
        ]

        # 5. 写 status=done
        write_status_file(
            project_root, commit_sha, STATUS_DONE,
            session_id=session_id,
            started_at=started_at,
            finished_at=int(time.time()),
            reconcilers_total=total,
            reconcilers_warn=warn_count,
            reconcilers_auto_committed=auto_count,
            errors=errors,
            trigger_source="post_commit_async",
            worker_pid=os.getpid(),
        )

        # 6. 自愈写入：worker boot 成功 → 对 RECONCILE-WORKER-BOOT 写 clean 记录
        #    #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1：补全告警生命周期对称性
        _write_boot_success_clean(project_root, commit_sha, session_id)
        return 0
    finally:
        # #ARCH-RECONCILER-WORKER-SESSION-001 Phase C：确保 session 注销（防泄漏）
        _unregister_worker_session(project_root, worker_sid)


def main() -> int:
    """CLI 入口：``python -m zephyr.governance.audit.reconcile_worker --payload <path>``"""
    parser = argparse.ArgumentParser(
        prog="zephyr.governance.audit.reconcile_worker",
        description="Post-commit reconciler async worker (P2-3)",
    )
    parser.add_argument(
        "--payload", required=True,
        help="payload file path (JSON, read-once)",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.payload)
    except Exception as e:  # noqa: BLE001
        # payload 加载失败无法写 status（不知道 commit_sha/project_root），
        # 只能 stderr 报错 + exit 1
        sys.stderr.write(f"reconcile_worker: payload load failed: {e}\n")
        return 1

    return _run_worker(payload)


if __name__ == "__main__":
    sys.exit(main())

# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def run_worker(payload) -> int:
    """公共接口：run_worker（Stage 4 公共化，委托到 _run_worker）。"""
    return _run_worker(payload)

