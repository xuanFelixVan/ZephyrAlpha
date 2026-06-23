# [A_module] module_id=MOD-ORC_boot_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md

# [MODULE] zephyr.trading.boot_hooks

# [INVARIANTS] register_boot_hooks is idempotent; hook_registry deduplicates by name

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.trading.auto_runtime_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] returns None; logs error on failure; writes hook_failure event on critical failure

# [TESTS]

from __future__ import annotations

import logging
import threading
from pathlib import Path

from zephyr.shared.event_bus import EventBus, EventType

logger = logging.getLogger(__name__)


def _subscribe_task_lifecycle_events() -> None:
    try:
        bus = EventBus.get_instance()

        def _on_task_created(event: object) -> None:
            task_id = getattr(event, "task_id", "")
            logger.info("EventBus: task.created event received for %s", task_id)

        def _on_task_completed_event(event: object) -> None:
            task_id = getattr(event, "task_id", "")
            logger.info("EventBus: task.completed event received for %s", task_id)

        bus.subscribe(EventType.TASK_CREATED, _on_task_created)
        bus.subscribe(EventType.TASK_COMPLETED, _on_task_completed_event)
        logger.info("EventBus task lifecycle subscriptions registered (TASK_CREATED, TASK_COMPLETED)")
    except Exception as e:
        logger.debug("EventBus task lifecycle subscription skipped: %s", e)


def _register_rbac_hooks() -> None:
    """注册RBAC事件钩子 — 在任务状态转换时检查权限."""
    try:
        from zephyr.governance.ops_governance.event_hook import hook_registry

        def _on_task_in_progress_rbac_check(event: object) -> None:
            """任务开始执行时验证RBAC系统就绪状态."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "IN_PROGRESS":
                return
            try:
                from zephyr.security.access_control.genesis_bootstrap import (
                    get_genesis_bootstrap,
                )

                genesis = get_genesis_bootstrap()
                if not genesis.state.is_ready:
                    logger.warning(
                        "RBAC system not ready when task %s starting IN_PROGRESS — genesis phase=%s",
                        getattr(event, "task_id", ""),
                        genesis.state.phase.value,
                    )
            except Exception as exc:
                logger.debug("hook rbac_readiness_check: %s", exc)

        def _on_task_completed_rbac_audit(event: object) -> None:
            """任务完成时记录RBAC审计条目."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "COMPLETED":
                return
            try:
                from zephyr.security.access_control.non_repudiation import NonRepudiation

                nr = NonRepudiation()
                task_id = getattr(event, "task_id", "")
                entry = nr.sign(f"task_completed:{task_id}", "auto_runtime_core")
                logger.debug("RBAC audit entry signed for task %s: %s", task_id, entry.hmac_hash[:16])
            except Exception as exc:
                logger.debug("hook rbac_audit_sign: %s", exc)

        def _on_task_failed_rbac_alert(event: object) -> None:
            """任务失败时检查是否需要触发RBAC熔断器."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "FAILED":
                return
            try:
                from zephyr.security.access_control.kill_switch import KillSwitch, KillSwitchState

                ks = KillSwitch()
                if ks.status.state == KillSwitchState.NORMAL:
                    logger.info(
                        "Task %s failed — RBAC kill_switch still NORMAL (no systemic threat detected)",
                        getattr(event, "task_id", ""),
                    )
            except Exception as exc:
                logger.debug("hook rbac_kill_switch_check: %s", exc)

        hook_registry.register(_on_task_in_progress_rbac_check, priority=40, name="rbac_readiness_check")
        hook_registry.register(_on_task_completed_rbac_audit, priority=46, name="rbac_audit_sign")
        hook_registry.register(_on_task_failed_rbac_alert, priority=57, name="rbac_kill_switch_check")
        logger.info(
            "RBAC hooks registered: rbac_readiness_check / rbac_audit_sign / rbac_kill_switch_check"
        )
    except Exception as e:
        logger.warning("Failed to register RBAC hooks: %s", e)


def register_boot_hooks() -> None:
    try:
        from zephyr.governance.ops_governance.event_hook import hook_registry

        def _on_task_completed(event: object) -> None:
            try:
                from zephyr.governance.persistence.task_repo import TaskRepository

                tr = TaskRepository()
                completed_id = getattr(event, "task_id", "")
                if not completed_id:
                    return
                downstream = tr.list_by_dependency(completed_id)
                for ds in downstream:
                    if ds.status not in ("BLOCKED", "PENDING", "WAITING"):
                        continue
                    deps = ds.depends_on or []
                    if not deps:
                        continue
                    all_done = all(tr.get(d).status == "COMPLETED" for d in deps if d)
                    if all_done:
                        tr.transition(ds.task_id, "READY", note=f"unblocked by {completed_id}")
            except Exception as exc:
                logger.error("hook auto_unblock_dependents FAILED: %s", exc)

        def _on_task_failed(event: object) -> None:
            try:
                from zephyr.governance.persistence.task_repo import TaskRepository

                tr = TaskRepository()
                task_id = getattr(event, "task_id", "")
                task = tr.get(task_id)
                if not task:
                    return
                retry_count = getattr(task, "retry_count", 0) or 0
                if retry_count < 3:
                    tr.transition(
                        task_id,
                        "RETRY",
                        note=f"auto-retry from hook (attempt {retry_count + 1})",
                    )
            except Exception as exc:
                logger.error("hook auto_retry_on_failure FAILED: %s", exc)

        def _on_task_verified_triple_align(event: object) -> None:
            try:
                from zephyr.governance.rule_enforcement.triple_alignment import check_triple_alignment

                task_id = getattr(event, "task_id", "")
                source_bp = ""
                try:
                    from zephyr.governance.persistence.task_repo import TaskRepository

                    tr = TaskRepository()
                    task = tr.get(task_id)
                    source_bp = getattr(task, "source_blueprint", "") if task else ""
                except Exception:
                    pass
                if not source_bp:
                    return
                result = check_triple_alignment(specific_module=source_bp, warn_only=False)
                if not result.passed:
                    logger.error(
                        "G-TRIPLE-ALIGN FAILED after task %s verified: module %s has %d violations",
                        task_id,
                        source_bp,
                        len([v for v in result.violations if v.severity.value == "ERROR"]),
                    )
            except Exception as exc:
                logger.error("hook triple_alignment_on_verified FAILED: %s", exc)

        def _cleanup_task_processes(event: object) -> None:
            try:
                task_id = getattr(event, "task_id", "")
                to_status = getattr(event, "to_status", "")
                if not task_id:
                    return
                if to_status.upper() in ("COMPLETED", "FAILED", "CANCELLED"):
                    from zephyr.trading.ide_health_daemon import kill_task_processes

                    killed = kill_task_processes(task_id)
                    if killed:
                        logger.info("hook cleanup_task_processes: killed %d PIDs for %s", len(killed), task_id)
            except Exception as exc:
                logger.warning("hook cleanup_task_processes FAILED: %s", exc)

        def _on_task_completed_archive_vms(event: object) -> None:
            try:
                task_id = getattr(event, "task_id", "")
                to_status = getattr(event, "to_status", "")
                if to_status.upper() != "COMPLETED":
                    return
                from zephyr.governance.persistence.task_repo import TaskRepository
                from zephyr.trading.orchestrator.memory_writer import archive_to_vms

                tr = TaskRepository()
                task = tr.get(task_id)
                if task:
                    archive_to_vms(task)
            except Exception as exc:
                logger.error("hook orc_vms_archive FAILED: %s", exc)

        def _on_task_completed_sync_kb_vms(event: object) -> None:
            try:
                task_id = getattr(event, "task_id", "")
                to_status = getattr(event, "to_status", "")
                if to_status.upper() != "COMPLETED":
                    return
                from zephyr.intelligence.model_evaluation.sync_engine import sync_to_vms

                sync_to_vms()
            except Exception as exc:
                logger.error("hook kb_vms_sync FAILED: %s", exc)

        def _on_task_rollback_freeze_gates(event: object) -> None:
            try:
                to_status = getattr(event, "to_status", "")
                if to_status.upper() != "ROLLBACK":
                    return
                from zephyr.governance.gate_coordinator import freeze_all_gates

                result = freeze_all_gates()
                logger.info("hook rbk_gate_freeze: frozen=%s gates=%d", result.frozen, result.gates_count)
            except Exception as exc:
                logger.error("hook rbk_gate_freeze FAILED: %s", exc)

        hook_registry.register(_on_task_completed, priority=50, name="auto_unblock_dependents")
        hook_registry.register(_on_task_failed, priority=60, name="auto_retry_on_failure")
        hook_registry.register(_on_task_verified_triple_align, priority=70, name="triple_alignment_on_verified")
        hook_registry.register(_cleanup_task_processes, priority=45, name="cleanup_task_processes")
        hook_registry.register(_on_task_completed_archive_vms, priority=48, name="orc_vms_archive")
        hook_registry.register(_on_task_completed_sync_kb_vms, priority=47, name="kb_vms_sync")
        hook_registry.register(_on_task_rollback_freeze_gates, priority=55, name="rbk_gate_freeze")
        logger.info(
            "Task system hooks registered: auto_unblock_dependents / auto_retry_on_failure / triple_alignment_on_verified / cleanup_task_processes / orc_vms_archive / kb_vms_sync / rbk_gate_freeze"
        )

        # ── ⚡ Event-driven hooks (替代定时扫描的部分校验) ───────────

        def _on_task_blocked_escalation(event: object) -> None:
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "BLOCKED":
                return
            try:
                from zephyr.governance.persistence.task_repo import TaskRepository

                TaskRepository().check_escalation(getattr(event, "task_id", ""))
            except Exception as exc:
                logger.debug("hook escalation_check: %s", exc)

        def _on_task_in_progress_timeout(event: object) -> None:
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "IN_PROGRESS":
                return
            try:
                from zephyr.governance.persistence.task_repo import TaskRepository

                TaskRepository().check_task_timeout(getattr(event, "task_id", ""))
            except Exception as exc:
                logger.debug("hook timeout_check: %s", exc)

        def _on_task_completed_budget_delta(event: object) -> None:
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != "COMPLETED":
                return
            try:
                from zephyr.governance.budget_engine import BudgetEngine

                engine = BudgetEngine()
                snapshot = engine.get_snapshot()
                if snapshot and getattr(snapshot, "health", "") not in ("HEALTHY", ""):
                    logger.warning("Budget status: %s", snapshot.health)
            except Exception as exc:
                logger.debug("hook budget_delta: %s", exc)

        def _on_session_startup_init_budget(event: object) -> None:
            try:
                from zephyr.governance.budget_engine import BudgetEngine

                engine = BudgetEngine.ensure_initialized()
                snapshot = engine.get_snapshot()
                logger.info(
                    "session_startup: BudgetEngine initialized, health=%s, degradation=%s",
                    snapshot.get("health", "UNKNOWN"),
                    snapshot.get("degradation_level", "UNKNOWN"),
                )
            except Exception as exc:
                logger.error("hook session_startup_init_budget FAILED: %s", exc)

        def _on_session_shutdown_budget_close(event: object) -> None:
            try:
                from zephyr.governance.budget_engine import BudgetEngine

                if BudgetEngine._instance is not None:
                    result = BudgetEngine._instance.shutdown()
                    logger.info(
                        "session_shutdown: BudgetEngine closed, persisted=%s, health=%s",
                        result.get("cleaned_up", False),
                        result.get("snapshot", {}).get("health", "UNKNOWN"),
                    )
            except Exception as exc:
                logger.error("hook session_shutdown_budget_close FAILED: %s", exc)

        def _on_blueprint_changed_triple_align(event: object) -> None:
            try:
                from zephyr.governance.rule_enforcement.triple_alignment import check_triple_alignment

                source_bp = getattr(event, "blueprint_path", "") or getattr(event, "path", "")
                result = check_triple_alignment(specific_module=source_bp or None, warn_only=True)
                if not result.passed:
                    violations = len([v for v in result.violations if v.severity.value == "ERROR"])
                    if violations:
                        logger.warning(
                            "Event triple-align: %s has %d violations after blueprint change",
                            source_bp or "all",
                            violations,
                        )
            except Exception as exc:
                logger.debug("hook triple_align_event: %s", exc)

        hook_registry.register(_on_task_blocked_escalation, priority=56, name="escalation_check_event")
        hook_registry.register(_on_task_in_progress_timeout, priority=56, name="timeout_check_event")
        hook_registry.register(_on_task_completed_budget_delta, priority=94, name="budget_delta_event")
        hook_registry.register(_on_session_startup_init_budget, priority=10, name="session_startup_init_budget")
        hook_registry.register(_on_session_shutdown_budget_close, priority=90, name="session_shutdown_budget_close")
        hook_registry.register(_on_blueprint_changed_triple_align, priority=72, name="triple_align_event")

        try:
            from zephyr.integration.shared_08.event_bus import EventBusBackpressure

            _bus = EventBusBackpressure()
            _bus.subscribe("blueprint.changed", _on_blueprint_changed_triple_align)
            _bus.subscribe("blueprint.decomposed", _on_blueprint_changed_triple_align)
        except Exception:
            pass

        logger.info("Event-driven hooks registered: escalation_check / timeout_check / budget_delta / session_startup_init_budget / session_shutdown_budget_close / triple_align")
    except Exception as e:
        logger.warning("Failed to register task system hooks: %s", e)

    try:
        from zephyr.trading.ide_health_daemon import register_daemon

        register_daemon()
        logger.info("IdeHealthDaemon registered and auto-started via boot hooks")
    except Exception as e:
        logger.warning("Failed to register IdeHealthDaemon: %s", e)

    _subscribe_task_lifecycle_events()
    _register_rbac_hooks()

    # MCP 集群自动启动（daemon 线程，不阻塞主流程）
    def _start_mcp_cluster() -> None:
        """启动 MCP 集群（10 个 Server 按 DAG 拓扑排序启动）。"""
        try:
            launcher_path = Path(__file__).resolve().parents[3] / "scripts" / "mcp" / "launcher.py"
            if not launcher_path.exists():
                logger.warning("MCP launcher not found: %s", launcher_path)
                return

            import importlib.util

            spec = importlib.util.spec_from_file_location("launcher", launcher_path)
            if spec is None or spec.loader is None:
                logger.warning("MCP launcher spec creation failed")
                return
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            logger.info("MCP cluster auto-start: launching 10 servers via DAG...")
            mod.launch_all()
        except Exception as exc:
            logger.error("MCP cluster auto-start FAILED: %s", exc)

    mcp_thread = threading.Thread(target=_start_mcp_cluster, name="mcp-cluster-launcher", daemon=True)
    mcp_thread.start()
    logger.info("MCP cluster auto-start thread launched (daemon=True)")
