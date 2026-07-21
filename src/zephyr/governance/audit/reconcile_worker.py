# [BLUEPRINT] MOD-GOV-reconcile_worker | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] zephyr.governance.audit.reconcile_worker
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway); zephyr.governance.audit.reconciliation_registry (_log_reconcile_results); zephyr.governance.audit.reconcile_runner (write_status_file, STATUS_*)
# [CONSUMERS] zephyr.governance.audit.reconcile_runner.launch_reconcile_async (subprocess spawn)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] detached subprocess（父进程退出不影响 worker）；payload file 读取后立即删除；status file 流转 pending→running→done/failed；reconciler 异常降级为 warn 结果不阻断后续；worker 异常→status=failed+errors 持久化
# [MODIFY-GUARD] main 函数签名；payload file JSON schema；status file 写入时机（running 前后/done/failed）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] payload 不存在/JSON 解析失败→status=failed 立即退出；gateway 构造失败→status=failed；reconcile_for 内部异常已在 registry 层捕获
# [TESTS] tests/governance/audit/test_reconcile_async.py
# [A_module] module_id=MOD-GOV-reconcile_worker | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
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
        reconcile_results = gateway._run_post_commit_reconcile_sync_worker(
            committed_files, session_id, commit_message,
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
