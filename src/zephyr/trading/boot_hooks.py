# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.boot_hooks
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.event_bus; zephyr.governance.ops_governance.event_hook; zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.rule_enforcement.triple_alignment; zephyr.intelligence.model_evaluation.sync_engine; zephyr.governance.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] register_boot_hooks is idempotent; hook_registry deduplicates by name
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns None; logs error on failure; writes hook_failure event on critical failure
# [TESTS]
# [A_module] module_id=MOD-ORC_boot_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

from zephyr.shared.event_bus import EventBus, EventType

# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.governance.ops_governance.budget_engine import BudgetEngineProtocol

logger = logging.getLogger(__name__)

# 5.137.1 修复：自动重试门限魔数提取为命名常量
_MAX_AUTO_RETRY_LIMIT = 3


# 5.97.16 修复：抽取 _on_task_verified_triple_align 内嵌 try-except 的 helper
def _get_source_blueprint(task_id: str, task_repo: TaskRepositoryProtocol | None = None) -> str:
    """从 TaskRepository 查询 task 的 source_blueprint，失败返回空串。"""
    try:
        tr = task_repo
        if tr is None:
            from zephyr.governance.persistence.task_repo import TaskRepository

            tr = TaskRepository()
        task = tr.get(task_id)
        return getattr(task, "source_blueprint", "") if task else ""
    except Exception:
        logger.debug("task_repo.get failed for triple_align check task_id=%s", task_id, exc_info=True)
        return ""


def _subscribe_task_lifecycle_events(budget_engine: BudgetEngineProtocol | None = None) -> None:
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
        logger.debug("EventBus task lifecycle subscription skipped: %s", e, exc_info=True)


_monitoring_modules_initialized = False


def _init_shared_monitoring_modules() -> None:
    """实例化5个被动库监控模块 — DM-201246.

    在系统启动时自动实例化，而非依赖手动调用：
    1. LongevityMonitor — 长寿监控
    2. HealthcheckService — 健康检查服务
    3. AggregateHealth — 延迟到 health 就绪（需 LifecycleManager，由 AutoRuntimeCore.boot() 负责）
    4. HealthDiscovery — 注册系统健康检查
    5. MetricsRegistry — 指标注册表（懒加载）
    6. AutonomyMonitor — 自治监控

    注: AggregateHealth 延迟初始化, 本函数实际实例化5个模块 (5.157.19 修复docstring)
    """
    global _monitoring_modules_initialized
    if _monitoring_modules_initialized:
        logger.debug("Shared monitoring modules already initialized, skipping (idempotent)")
        return
    _monitoring_modules_initialized = True

    project_root = REPO_ROOT

    # 1. LongevityMonitor
    try:
        from zephyr.shared.lifecycle.longevity_monitor import LongevityMonitor
        _monitor = LongevityMonitor()
        logger.info("Shared monitoring: LongevityMonitor instantiated")
    except Exception as e:
        logger.warning("Shared monitoring: LongevityMonitor init failed: %s", e, exc_info=True)

    # 2. HealthcheckService
    try:
        from zephyr.shared.lifecycle.healthcheck_service import HealthcheckService
        _healthcheck = HealthcheckService(project_root=project_root)
        logger.info("Shared monitoring: HealthcheckService instantiated")
    except Exception as e:
        logger.warning("Shared monitoring: HealthcheckService init failed: %s", e, exc_info=True)

    # 3. AggregateHealth — DM-201247 条件已满足（HealthMonitor._monitor_loop 已实现分钟级调度），
    #    但 AggregateHealth 需 LifecycleManager 实例，本初始化阶段不可用。
    #    AggregateHealth 接入改由 AutoRuntimeCore.boot() 负责（持有 LifecycleManager）。
    # 5.12.6 修复：清理 stale TODO DM-201247（条件已满足，接入责任转移至 AutoRuntimeCore）

    # 4. HealthDiscovery — 注册系统健康检查
    try:
        from zephyr.shared.lifecycle.health_discovery import register_system_health
        def _boot_hooks_health_check() -> str:
            return "healthy"
        register_system_health("boot_hooks", _boot_hooks_health_check, source="boot_hooks")
        logger.info("Shared monitoring: HealthDiscovery registered boot_hooks health check")
    except Exception as e:
        logger.warning("Shared monitoring: HealthDiscovery init failed: %s", e, exc_info=True)

    # 5. MetricsRegistry — 懒加载
    try:
        from zephyr.shared.observability.metrics import MetricsRegistry
        _metrics = MetricsRegistry()
        _metrics.observe("boot_hooks.init", 1.0, labels={"module": "shared_monitoring"})
        logger.info("Shared monitoring: MetricsRegistry instantiated (lazy)")
    except Exception as e:
        logger.warning("Shared monitoring: MetricsRegistry init failed: %s", e, exc_info=True)

    # 6. AutonomyMonitor
    try:
        from zephyr.shared.maintenance.autonomy_monitor import AutonomyMonitor
        _autonomy = AutonomyMonitor(data_dir=project_root / "data" / "autonomy")
        logger.info("Shared monitoring: AutonomyMonitor instantiated")
    except Exception as e:
        logger.warning("Shared monitoring: AutonomyMonitor init failed: %s", e, exc_info=True)

    # DM-201248: 事件订阅机制
    try:
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events
        subscribe_monitoring_events()
        logger.info("Shared monitoring: event subscription registered (health)")
    except Exception as e:
        logger.warning("Shared monitoring: health event subscription failed: %s", e, exc_info=True)

    try:
        from zephyr.shared.observability.metrics import subscribe_metrics_events
        subscribe_metrics_events()
        logger.info("Shared monitoring: event subscription registered (metrics)")
    except Exception as e:
        logger.warning("Shared monitoring: metrics event subscription failed: %s", e, exc_info=True)

    # DM-201249: Finalizer 自动关闭
    try:
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto
        register_monitoring_finalizers_auto()
        logger.info("Shared monitoring: finalizer registered (monitor-flush + monitor-health-snapshot)")
    except Exception as e:
        logger.warning("Shared monitoring: finalizer registration failed: %s", e, exc_info=True)


_eventbus_consumers_subscribed = False


def _subscribe_eventbus_consumers() -> None:
    """统一调用9个消费方模块的 subscribe_eventbus() — DM-2507-J.

    混合注册模式：各模块提供模块级 subscribe_eventbus() 函数，
    boot_hooks 统一调用。每个 subscribe_eventbus() 内部幂等。

    消费方列表:
      1. F4  budget_engine          — slo_violation
      2. F5  f5_event_subscriber    — budget_exceeded/drift_detected/fix_completed/fix_failed
      3. F9  rollback_boot_integration — pipeline_failed/mcp_call_failed/kill_switch_triggered
      4. F14 pipeline_orchestrator  — pipeline_start
      5. F15 auto_fix_engine.event_hooks — drift_detected/validation_result
      6. F30 validator_event_bridge — fix_completed
      7. F1  autopilot              — task_completed
      8. F6  drift_bridge           — gate_blocked/task_completed
      9. auto_task_generator        — task_completed（P3 生成器触发接入）
    """
    global _eventbus_consumers_subscribed
    if _eventbus_consumers_subscribed:
        logger.debug("EventBus consumers already subscribed, skipping (idempotent)")
        return
    _eventbus_consumers_subscribed = True

    consumers = [
        ("F4 budget_engine", "zephyr.governance.ops_governance.budget_engine"),
        ("F5 f5_event_subscriber", "zephyr.governance.f5_event_subscriber"),
        ("F9 rollback_boot_integration", "zephyr.infrastructure.rollback.rollback_boot_integration"),
        ("F14 pipeline_orchestrator", "zephyr.integration.pipeline_orchestrator"),
        ("F15 auto_fix_engine.event_hooks", "zephyr.infrastructure.auto_fix_engine.event_hooks"),
        ("F30 validator_event_bridge", "zephyr.security.adversarial_validation.validator_event_bridge"),
        ("F1 autopilot", "zephyr.trading.autopilot"),
        ("F6 drift_bridge", "zephyr.governance.drift_detector_core.bridges.drift_bridge"),
        ("auto_task_generator", "zephyr.trading.auto_task_generator"),
    ]

    succeeded = 0
    failed = 0
    for label, module_path in consumers:
        try:
            import importlib

            mod = importlib.import_module(module_path)
            subscribe_fn = getattr(mod, "subscribe_eventbus", None)
            if subscribe_fn is None:
                logger.warning("EventBus consumer %s: no subscribe_eventbus() found", label)
                failed += 1
                continue
            subscribe_fn()
            succeeded += 1
            logger.info("EventBus consumer %s: subscribed", label)
        except Exception as e:
            failed += 1
            logger.warning("EventBus consumer %s: subscribe failed: %s", label, e, exc_info=True)

    logger.info(
        "EventBus consumers subscription complete: %d succeeded, %d failed (total %d)",
        succeeded,
        failed,
        len(consumers),
    )


def _register_rbac_hooks() -> None:
    """注册RBAC事件钩子 — 在任务状态转换时检查权限."""
    try:
        from zephyr.governance.ops_governance.event_hook import hook_registry

        def _on_task_in_progress_rbac_check(event: object) -> None:
            """任务开始执行时验证RBAC系统就绪状态."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != TaskStatus.IN_PROGRESS:
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
                logger.debug("hook rbac_readiness_check: %s", exc, exc_info=True)

        def _on_task_completed_rbac_audit(event: object) -> None:
            """任务完成时记录RBAC审计条目."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != TaskStatus.COMPLETED:
                return
            try:
                from zephyr.security.access_control.non_repudiation import NonRepudiation

                nr = NonRepudiation()
                task_id = getattr(event, "task_id", "")
                entry = nr.sign(f"task_completed:{task_id}", "auto_runtime_core")
                logger.debug("RBAC audit entry signed for task %s: %s", task_id, entry.hmac_hash[:16])
            except Exception as exc:
                logger.debug("hook rbac_audit_sign: %s", exc, exc_info=True)

        def _on_task_failed_rbac_alert(event: object) -> None:
            """任务失败时检查是否需要触发RBAC熔断器."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != TaskStatus.FAILED:
                return
            try:
                from zephyr.security.access_control.kill_switch import KillSwitchState, get_kill_switch

                ks = get_kill_switch()
                if ks.status.state == KillSwitchState.NORMAL:
                    logger.info(
                        "Task %s failed — RBAC kill_switch still NORMAL (no systemic threat detected)",
                        getattr(event, "task_id", ""),
                    )
            except Exception as exc:
                logger.debug("hook rbac_kill_switch_check: %s", exc, exc_info=True)

        hook_registry.register(_on_task_in_progress_rbac_check, priority=40, name="rbac_readiness_check")
        hook_registry.register(_on_task_completed_rbac_audit, priority=46, name="rbac_audit_sign")
        hook_registry.register(_on_task_failed_rbac_alert, priority=57, name="rbac_kill_switch_check")
        logger.info(
            "RBAC hooks registered: rbac_readiness_check / rbac_audit_sign / rbac_kill_switch_check"
        )
    except Exception as e:
        logger.warning("Failed to register RBAC hooks: %s", e, exc_info=True)


def _subscribe_skill_freshness_events() -> None:
    """订阅 skill.freshness_critical 事件 — 原 boot_cron_jobs 内联（2026-07-05 裁定）。"""
    try:
        from zephyr.shared.event_bus import bus

        def _on_freshness_critical(payload: dict) -> None:
            try:
                from zephyr.autonomy_core.skills.skill_freshness_ext import auto_deprecate_skill
                from zephyr.autonomy_core.skills.skill_lifecycle import SkillLifecycle

                sl = SkillLifecycle()
                for item in payload.get("criticals", []):
                    skill_id = item.get("skill_id", "")
                    score = item.get("freshness_score", 0.0)
                    if skill_id:
                        auto_deprecate_skill(sl, skill_id, score, reason="freshness_critical_auto")
            except Exception:
                logger.debug("skill.freshness_critical handler failed", exc_info=True)

        bus.subscribe("skill.freshness_critical", _on_freshness_critical)
        logger.info("Skill freshness critical event subscribed")
    except Exception as e:
        logger.warning("Failed to subscribe skill.freshness_critical: %s", e, exc_info=True)


# ---------------------------------------------------------------------------
# 5.97.3 修复: 将 register_boot_hooks 内的 13 个闭包提取为模块级私有函数
# 每个 handler 接受 (event, task_repo=None, budget_engine=None) 参数
# register_boot_hooks 通过 lambda 绑定注入的依赖
# ---------------------------------------------------------------------------


def _resolve_task_repo(task_repo: TaskRepositoryProtocol | None = None):
    """解析 task_repo — 注入则用注入的，否则惰性创建 TaskRepository。"""
    if task_repo is not None:
        return task_repo
    from zephyr.governance.persistence.task_repo import TaskRepository

    return TaskRepository()


def _hook_auto_unblock_dependents(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    try:
        tr = _resolve_task_repo(task_repo)
        completed_id = getattr(event, "task_id", "")
        if not completed_id:
            return
        downstream = tr.list_by_dependency(completed_id)
        for ds in downstream:
            if ds.status not in (TaskStatus.BLOCKED, TaskStatus.PENDING, TaskStatus.WAITING):
                continue
            deps = ds.depends_on or []
            if not deps:
                continue
            all_done = all(tr.get(d).status == TaskStatus.COMPLETED for d in deps if d)
            if all_done:
                tr.transition(ds.task_id, TaskStatus.READY, note=f"unblocked by {completed_id}")
    except Exception as exc:
        logger.error("hook auto_unblock_dependents FAILED: %s", exc, exc_info=True)


def _hook_auto_retry_on_failure(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    try:
        tr = _resolve_task_repo(task_repo)
        task_id = getattr(event, "task_id", "")
        task = tr.get(task_id)
        if not task:
            return
        retry_count = getattr(task, "retry_count", 0) or 0
        if retry_count < _MAX_AUTO_RETRY_LIMIT:
            tr.transition(
                task_id,
                TaskStatus.RETRY,
                note=f"auto-retry from hook (attempt {retry_count + 1})",
            )
    except Exception as exc:
        logger.error("hook auto_retry_on_failure FAILED: %s", exc, exc_info=True)


def _hook_triple_alignment_on_verified(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    try:
        from zephyr.governance.rule_enforcement.triple_alignment import check_triple_alignment

        task_id = getattr(event, "task_id", "")
        source_bp = _get_source_blueprint(task_id, task_repo=task_repo)
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
        logger.error("hook triple_alignment_on_verified FAILED: %s", exc, exc_info=True)


def _hook_cleanup_task_processes(event: object) -> None:
    try:
        task_id = getattr(event, "task_id", "")
        to_status = getattr(event, "to_status", "")
        if not task_id:
            return
        if to_status.upper() in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            from zephyr.trading.ide_health_daemon import kill_task_processes

            killed = kill_task_processes(task_id)
            if killed:
                logger.info("hook cleanup_task_processes: killed %d PIDs for %s", len(killed), task_id)
    except Exception as exc:
        logger.warning("hook cleanup_task_processes FAILED: %s", exc, exc_info=True)


def _hook_orc_vms_archive(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    try:
        task_id = getattr(event, "task_id", "")
        to_status = getattr(event, "to_status", "")
        if to_status.upper() != TaskStatus.COMPLETED:
            return
        from zephyr.orchestrator.execution.memory_writer import archive_to_vms

        tr = _resolve_task_repo(task_repo)
        task = tr.get(task_id)
        if task:
            archive_to_vms(task)
    except Exception as exc:
        logger.error("hook orc_vms_archive FAILED: %s", exc, exc_info=True)


def _hook_kb_vms_sync(event: object) -> None:
    try:
        task_id = getattr(event, "task_id", "")
        to_status = getattr(event, "to_status", "")
        if to_status.upper() != TaskStatus.COMPLETED:
            return
        from zephyr.intelligence.model_evaluation.sync_engine import sync_to_vms

        sync_to_vms()
    except Exception as exc:
        logger.error("hook kb_vms_sync FAILED: %s", exc, exc_info=True)


def _hook_rbk_gate_freeze(event: object) -> None:
    try:
        to_status = getattr(event, "to_status", "")
        if to_status.upper() != "ROLLBACK":
            return
        from zephyr.infrastructure.runtime.gate_coordinator import freeze_all_gates

        result = freeze_all_gates()
        logger.info("hook rbk_gate_freeze: frozen=%s gates=%d", result.frozen, result.gates_count)
    except Exception as exc:
        logger.error("hook rbk_gate_freeze FAILED: %s", exc, exc_info=True)


def _hook_escalation_check(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    to_status = getattr(event, "to_status", "")
    if to_status.upper() != TaskStatus.BLOCKED:
        return
    try:
        _resolve_task_repo(task_repo).check_escalation(getattr(event, "task_id", ""))
    except Exception as exc:
        logger.debug("hook escalation_check: %s", exc, exc_info=True)


def _hook_timeout_check(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    to_status = getattr(event, "to_status", "")
    if to_status.upper() != TaskStatus.IN_PROGRESS:
        return
    try:
        _resolve_task_repo(task_repo).check_task_timeout(getattr(event, "task_id", ""))
    except Exception as exc:
        logger.debug("hook timeout_check: %s", exc, exc_info=True)


def _hook_budget_delta(event: object, budget_engine: BudgetEngineProtocol | None = None) -> None:
    to_status = getattr(event, "to_status", "")
    if to_status.upper() != TaskStatus.COMPLETED:
        return
    try:
        engine = budget_engine
        if engine is None:
            from zephyr.governance.ops_governance.budget_engine import BudgetEngine

            engine = BudgetEngine()
        snapshot = engine.get_snapshot()
        if snapshot and getattr(snapshot, "health", "") not in ("HEALTHY", ""):
            logger.warning("Budget status: %s", snapshot.health)
    except Exception as exc:
        logger.debug("hook budget_delta: %s", exc, exc_info=True)


def _hook_session_startup_init_budget(event: object) -> None:
    try:
        from zephyr.governance.ops_governance.budget_engine import BudgetEngine

        engine = BudgetEngine.ensure_initialized()
        snapshot = engine.get_snapshot()
        logger.info(
            "session_startup: BudgetEngine initialized, health=%s, degradation=%s",
            snapshot.get("health", "UNKNOWN"),
            snapshot.get("degradation_level", "UNKNOWN"),
        )
    except Exception as exc:
        logger.error("hook session_startup_init_budget FAILED: %s", exc, exc_info=True)


def _hook_session_shutdown_budget_close(event: object) -> None:
    try:
        from zephyr.governance.ops_governance.budget_engine import BudgetEngine

        if BudgetEngine._instance is not None:
            result = BudgetEngine._instance.shutdown()
            logger.info(
                "session_shutdown: BudgetEngine closed, persisted=%s, health=%s",
                result.get("cleaned_up", False),
                result.get("snapshot", {}).get("health", "UNKNOWN"),
            )
    except Exception as exc:
        logger.error("hook session_shutdown_budget_close FAILED: %s", exc, exc_info=True)


def _hook_triple_align_event(event: object) -> None:
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
        logger.debug("hook triple_align_event: %s", exc, exc_info=True)


def register_boot_hooks(
    task_repo: TaskRepositoryProtocol | None = None,
    budget_engine: BudgetEngineProtocol | None = None,
) -> None:
    try:
        from zephyr.governance.ops_governance.event_hook import hook_registry

        # Task system hooks — 需要 task_repo 的用 lambda 绑定
        hook_registry.register(lambda e: _hook_auto_unblock_dependents(e, task_repo), priority=50, name="auto_unblock_dependents")
        hook_registry.register(lambda e: _hook_auto_retry_on_failure(e, task_repo), priority=60, name="auto_retry_on_failure")
        hook_registry.register(lambda e: _hook_triple_alignment_on_verified(e, task_repo), priority=70, name="triple_alignment_on_verified")
        hook_registry.register(_hook_cleanup_task_processes, priority=45, name="cleanup_task_processes")
        hook_registry.register(lambda e: _hook_orc_vms_archive(e, task_repo), priority=48, name="orc_vms_archive")
        hook_registry.register(_hook_kb_vms_sync, priority=47, name="kb_vms_sync")
        hook_registry.register(_hook_rbk_gate_freeze, priority=55, name="rbk_gate_freeze")
        logger.info(
            "Task system hooks registered: auto_unblock_dependents / auto_retry_on_failure / triple_alignment_on_verified / cleanup_task_processes / orc_vms_archive / kb_vms_sync / rbk_gate_freeze"
        )

        # Event-driven hooks
        hook_registry.register(lambda e: _hook_escalation_check(e, task_repo), priority=56, name="escalation_check_event")
        hook_registry.register(lambda e: _hook_timeout_check(e, task_repo), priority=56, name="timeout_check_event")
        hook_registry.register(lambda e: _hook_budget_delta(e, budget_engine), priority=94, name="budget_delta_event")
        hook_registry.register(_hook_session_startup_init_budget, priority=10, name="session_startup_init_budget")
        hook_registry.register(_hook_session_shutdown_budget_close, priority=90, name="session_shutdown_budget_close")
        hook_registry.register(_hook_triple_align_event, priority=72, name="triple_align_event")

        try:
            from zephyr.shared.event_bus import bus as _bus

            _bus.subscribe("blueprint.changed", _hook_triple_align_event)
            _bus.subscribe("blueprint.decomposed", _hook_triple_align_event)
        except Exception:
            logger.warning("EventBus subscribe failed for triple_align blueprint hooks", exc_info=True)

        logger.info("Event-driven hooks registered: escalation_check / timeout_check / budget_delta / session_startup_init_budget / session_shutdown_budget_close / triple_align")
    except Exception as e:
        logger.warning("Failed to register task system hooks: %s", e, exc_info=True)

    try:
        from zephyr.trading.ide_health_daemon import register_daemon

        register_daemon()
        logger.info("IdeHealthDaemon registered and auto-started via boot hooks")
    except Exception as e:
        logger.warning("Failed to register IdeHealthDaemon: %s", e, exc_info=True)

    _subscribe_task_lifecycle_events(budget_engine=budget_engine)
    _register_rbac_hooks()
    _init_shared_monitoring_modules()

    # P0-2 修复：RollbackBootIntegration 启动钩子接线 — WAL/Verifier 自动初始化
    try:
        from zephyr.infrastructure.rollback.rollback_boot_integration import RollbackBootIntegration
        _rollback_boot = RollbackBootIntegration(project_root=REPO_ROOT)
        _rollback_boot.register_startup_hook()
        logger.info("RollbackBootIntegration: registered startup hook (WAL+Verifier init)")
    except Exception as e:
        logger.warning("RollbackBootIntegration: register failed: %s", e, exc_info=True)

    # P1-10 修复：SLAMonitor 永久系统启动接入 — 事件驱动 RTO/RPO 自动记录
    try:
        from zephyr.infrastructure.sla.sla_monitor import SLAMonitor
        _sla_monitor = SLAMonitor()
        _sla_monitor.subscribe_eventbus()
        logger.info("SLAMonitor: subscribed to EventBus (RTO/RPO auto-record)")
    except Exception as e:
        logger.warning("SLAMonitor: subscribe failed: %s", e, exc_info=True)

    # P1-10 修复：Notifier 永久系统启动接入 — 事件驱动 Owner 通知
    try:
        from zephyr.infrastructure.observability.notifier import Notifier
        _notifier = Notifier()
        _notifier.subscribe_eventbus()
        logger.info("Notifier: subscribed to EventBus (pipeline_failed/kill_switch auto-notify)")
    except Exception as e:
        logger.warning("Notifier: subscribe failed: %s", e, exc_info=True)

    # P1-10 修复：HealthAggregator 永久系统启动接入 — 事件驱动健康快照
    try:
        from zephyr.infrastructure.system_telemetry.health_aggregator import HealthAggregator
        _health_aggregator = HealthAggregator()
        _health_aggregator.subscribe_eventbus()
        logger.info("HealthAggregator: subscribed to EventBus (critical event auto-snapshot)")
    except Exception as e:
        logger.warning("HealthAggregator: subscribe failed: %s", e, exc_info=True)

    _subscribe_eventbus_consumers()
    _subscribe_skill_freshness_events()

    # 红蓝对抗提交触发消费线程 (MOD-INF-030 事件驱动)：daemon 线程轮询
    # data/red_blue/trigger_queue/，门禁达标时跑 TIER_1 对抗。
    # 就位+门禁激活：始终启动；ZEPHYR_RED_BLUE_AUTO_ENABLED!=1 时只 log 不实跑。
    try:
        from zephyr.security.adversarial_validation.commit_trigger import (
            RedBlueTriggerConsumer,
        )
        RedBlueTriggerConsumer().start()
        logger.info("RedBlueTriggerConsumer: started via boot hooks")
    except Exception as e:
        logger.warning("RedBlueTriggerConsumer: start failed: %s", e, exc_info=True)

    # MCP 集群自动启动（daemon 线程，不阻塞主流程）
    def _start_mcp_cluster() -> None:
        """启动 MCP 集群（10 个 Server 按 DAG 拓扑排序启动）。"""
        try:
            launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
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
            logger.error("MCP cluster auto-start FAILED: %s", exc, exc_info=True)

    mcp_thread = threading.Thread(target=_start_mcp_cluster, name="mcp-cluster-launcher", daemon=True)
    mcp_thread.start()
    logger.info("MCP cluster auto-start thread launched (daemon=True)")