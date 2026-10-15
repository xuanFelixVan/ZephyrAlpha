# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.boot_hooks
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.event_bus; zephyr.governance.event_hook; zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.gov_enforcement.rule_enforcement.triple_alignment; zephyr.governance.__init__; zephyr.governance.resilience_governance.f5_boot_integration; zephyr.governance.resilience_governance.f5_shutdown_manager
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] register_boot_hooks is idempotent; hook_registry deduplicates by name; tech_stack self-check runs first in register_boot_hooks (BLOCK=raise/DD-1,2,12, WARN=degrade/DD-3,5,16, ruling #485)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns None; logs error on failure; writes hook_failure event on critical failure
# [TESTS] tests/trading/test_boot_hooks_selfcheck.py
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_trading/algo_flow/boot_hooks.yaml
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from zephyr.shared.event_bus import EventBus, EventType

# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

if TYPE_CHECKING:
    from zephyr.governance.ops_governance.budget_engine import BudgetEngineProtocol
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol

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
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: LongevityMonitor init failed: %s", e, exc_info=True)

    # 2. HealthcheckService
    try:
        from zephyr.shared.lifecycle.healthcheck_service import HealthcheckService

        _healthcheck = HealthcheckService(project_root=project_root)
        logger.info("Shared monitoring: HealthcheckService instantiated")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: HealthDiscovery init failed: %s", e, exc_info=True)

    # 5. MetricsRegistry — 懒加载
    try:
        from zephyr.shared.observability.metrics import MetricsRegistry

        _metrics = MetricsRegistry()
        _metrics.observe("boot_hooks.init", 1.0, labels={"module": "shared_monitoring"})
        logger.info("Shared monitoring: MetricsRegistry instantiated (lazy)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: MetricsRegistry init failed: %s", e, exc_info=True)

    # 6. AutonomyMonitor
    try:
        from zephyr.shared.maintenance.autonomy_monitor import AutonomyMonitor

        _autonomy = AutonomyMonitor(data_dir=project_root / "data" / "autonomy")
        logger.info("Shared monitoring: AutonomyMonitor instantiated")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: AutonomyMonitor init failed: %s", e, exc_info=True)

    # DM-201248: 事件订阅机制
    try:
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events

        subscribe_monitoring_events()
        logger.info("Shared monitoring: event subscription registered (health)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: health event subscription failed: %s", e, exc_info=True)

    try:
        from zephyr.shared.observability.metrics import subscribe_metrics_events

        subscribe_metrics_events()
        logger.info("Shared monitoring: event subscription registered (metrics)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: metrics event subscription failed: %s", e, exc_info=True)

    # DM-201249: Finalizer 自动关闭
    try:
        from zephyr.trading.finalizer import register_monitoring_finalizers_auto

        register_monitoring_finalizers_auto()
        logger.info("Shared monitoring: finalizer registered (monitor-flush + monitor-health-snapshot)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Shared monitoring: finalizer registration failed: %s", e, exc_info=True)


_eventbus_consumers_subscribed = False


def _subscribe_eventbus_consumers() -> None:
    """统一调用各消费方模块的 subscribe_eventbus() — DM-2507-J.

    混合注册模式：各模块提供模块级 subscribe_eventbus() 函数，
    boot_hooks 统一调用。每个 subscribe_eventbus() 内部幂等。
    （计数不写死——消费方清单见下方 consumers 列表，条目数以清单为准。）

    消费方列表:
      1. F4  budget_engine          — slo_violation
      2. F5  f5_event_subscriber    — budget_exceeded/drift_detected/fix_completed/fix_failed
      3. F9  rollback_boot_integration — pipeline_failed/mcp_call_failed/kill_switch_triggered
      4. F14 pipeline_orchestrator  — pipeline_start
      5. F15 auto_fix_engine.event_hooks — drift_detected/validation_result
      6. F30 validator_event_bridge — fix_completed
      7. F1  autopilot              — task_completed
      8. F6  drift_bridge           — gate_blocked/task_completed
      9. auto_task_generator        — task_completed（自动任务生成，非架构文档生成器）
      10. premarket_checker         — premarket.check.requested（MOD-EX-063 盘前检查器）
      11. attribution_result_store  — post_settlement.recon.swept（L10b-W1 结算完成归因事件腿）
    注：架构文档生成器（23 个 generate_*.py）的自动触发不走 EventBus——见
    _subscribe_governance_regeneration()，启动时调 reconcile_stale() 按 mtime 扫描
    兜底；DB 真源变更由 apply_*.py 内联 reconcile_async() 实时触发。
    """
    global _eventbus_consumers_subscribed
    if _eventbus_consumers_subscribed:
        logger.debug("EventBus consumers already subscribed, skipping (idempotent)")
        return
    _eventbus_consumers_subscribed = True

    consumers = [
        ("F4 budget_engine", "zephyr.governance.ops_governance.budget_engine"),
        ("F5 f5_event_subscriber", "zephyr.governance.resilience_governance.f5_event_subscriber"),
        ("F9 rollback_boot_integration", "zephyr.infrastructure.rollback.rollback_boot_integration"),
        ("F14 pipeline_orchestrator", "zephyr.integration.pipeline_orchestrator"),
        ("F15 auto_fix_engine.event_hooks", "zephyr.infrastructure.auto_fix_engine.event_hooks"),
        ("F30 validator_event_bridge", "zephyr.security.adversarial_validation.validator_event_bridge"),
        ("F1 autopilot", "zephyr.trading.autopilot"),
        ("F6 drift_bridge", "zephyr.gov_drift.detector_core.bridges.drift_bridge"),
        ("auto_task_generator", "zephyr.trading.auto_task_generator"),
        ("premarket_checker", "zephyr.ex_core.premarket_checker"),
        ("trading_session", "zephyr.ex_core.trading_session"),
        # F62 违宪整改事件腿（2026-09-29 SW5）：盘后结算对账幂等日终 sweep，
        # 订阅 post_settlement.recon.requested——宪法 §9.3 reconciler 事件触发
        # （时钟腿=ZephyrAlpha_PostSettlement 计划任务退役归 Owner 门位）。
        ("post_settlement_pipeline", "zephyr.trading.post_settlement_pipeline"),
        # L10b-W1 归因事件腿（2026-10-04 EXEC-4）：sweep 完成回执 → 单日归因
        # → attribution_results 落库（UNWIRED 不伪跑/DEGRADED 不逃逸总线）。
        ("attribution_result_store", "zephyr.reporting.attribution_result_store"),
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        from zephyr.governance.event_hook import (  # noqa: import-integrity  — sys.modules shim registered in governance/__init__.py
            hook_registry,  # noqa: import-integrity  sys.modules shim registered in governance/__init__.py
        )

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
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("hook rbac_audit_sign: %s", exc, exc_info=True)

        def _on_task_failed_rbac_alert(event: object) -> None:
            """任务失败时检查是否需要触发RBAC熔断器."""
            to_status = getattr(event, "to_status", "")
            if to_status.upper() != TaskStatus.FAILED:
                return
            try:
                from zephyr.security.access_control.kill_switch import KillSwitchState, get_kill_switch

                ks = get_kill_switch()
                if ks.status.state is KillSwitchState.NORMAL:
                    logger.info(
                        "Task %s failed — RBAC kill_switch still NORMAL (no systemic threat detected)",
                        getattr(event, "task_id", ""),
                    )
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("hook rbac_kill_switch_check: %s", exc, exc_info=True)

        hook_registry.register(_on_task_in_progress_rbac_check, priority=40, name="rbac_readiness_check")
        hook_registry.register(_on_task_completed_rbac_audit, priority=46, name="rbac_audit_sign")
        hook_registry.register(_on_task_failed_rbac_alert, priority=57, name="rbac_kill_switch_check")
        logger.info("RBAC hooks registered: rbac_readiness_check / rbac_audit_sign / rbac_kill_switch_check")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("skill.freshness_critical handler failed", exc_info=True)

        bus.subscribe("skill.freshness_critical", _on_freshness_critical)
        logger.info("Skill freshness critical event subscribed")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Failed to subscribe skill.freshness_critical: %s", e, exc_info=True)


def _subscribe_governance_regeneration() -> None:
    """启动时扫描生成器输入源 mtime，YAML 比产物新则重生成（§3.2 事件驱动·启动事件）.

    生成器自动触发机制（generator_auto_trigger_pilot.md）：
      - DB 真源变更由 apply_*.py commit 后内联调用 reconcile() 实时触发
      - YAML 真源变更（手编无 apply 调用）由本函数启动时 mtime 对比兜底
    复用 scripts/governance/reconcile_generators.py 的 reconcile_stale()。
    """
    # pytest 守卫（批8 r5 实证）：测试内 boot 会真实重生成生产产物——domain_doc
    # 实测 158.7s > 120s pytest timeout 杀死全量（test_mcp_full_lifecycle_e2e
    # 中招）。测试禁写生产路径（宪法 §9.6），重生成属生产启动兜底，测试环境跳过。
    import os as _os

    if _os.environ.get("PYTEST_CURRENT_TEST"):
        logger.info("Governance regeneration skipped under pytest (test isolation)")
        return
    try:
        import sys as _sys

        _repo_root = str(REPO_ROOT)
        if _repo_root not in _sys.path:
            _sys.path.insert(0, _repo_root)
        from scripts.governance.reconcile_generators import reconcile_stale

        result = reconcile_stale()
        regenerated = result.get("regenerated", [])
        if regenerated:
            for r in regenerated:
                status = r.get("status", "?")
                name = r.get("generator", "?")
                if status == "ok":
                    logger.info(
                        "Governance regeneration: %s refreshed (%d outputs, %s, reason=%s)",
                        name,
                        len(r.get("outputs", [])),
                        r.get("elapsed_ms"),
                        r.get("stale_reason"),
                    )
                else:
                    logger.warning("Governance regeneration: %s FAILED: %s", name, r.get("error"))
            logger.info(
                "Governance regeneration complete: %d regenerated, %d skipped",
                len(regenerated),
                len(result.get("skipped", [])),
            )
        else:
            logger.debug(
                "Governance regeneration: all %d generators up-to-date",
                result.get("total_scanned", 0),
            )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Governance regeneration scan failed: %s", e, exc_info=True)


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
            all_done = all(tr.get(d).status is TaskStatus.COMPLETED for d in deps if d)
            if all_done:
                tr.transition(ds.task_id, TaskStatus.READY, note=f"unblocked by {completed_id}")
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("hook auto_retry_on_failure FAILED: %s", exc, exc_info=True)


def _hook_triple_alignment_on_verified(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    try:
        from zephyr.gov_enforcement.rule_enforcement.triple_alignment import check_triple_alignment

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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("hook triple_alignment_on_verified FAILED: %s", exc, exc_info=True)


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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("hook orc_vms_archive FAILED: %s", exc, exc_info=True)


def _hook_rbk_gate_freeze(event: object) -> None:
    try:
        to_status = getattr(event, "to_status", "")
        if to_status.upper() != "ROLLBACK":
            return
        from zephyr.infrastructure.runtime.gate_coordinator import freeze_all_gates

        result = freeze_all_gates()
        logger.info("hook rbk_gate_freeze: frozen=%s gates=%d", result.frozen, result.gates_count)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("hook rbk_gate_freeze FAILED: %s", exc, exc_info=True)


def _hook_escalation_check(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    to_status = getattr(event, "to_status", "")
    if to_status.upper() != TaskStatus.BLOCKED:
        return
    try:
        _resolve_task_repo(task_repo).check_escalation(getattr(event, "task_id", ""))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("hook escalation_check: %s", exc, exc_info=True)


def _hook_timeout_check(event: object, task_repo: TaskRepositoryProtocol | None = None) -> None:
    to_status = getattr(event, "to_status", "")
    if to_status.upper() != TaskStatus.IN_PROGRESS:
        return
    try:
        _resolve_task_repo(task_repo).check_task_timeout(getattr(event, "task_id", ""))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("hook session_shutdown_budget_close FAILED: %s", exc, exc_info=True)


def _hook_triple_align_event(event: object) -> None:
    try:
        from zephyr.gov_enforcement.rule_enforcement.triple_alignment import check_triple_alignment

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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("hook triple_align_event: %s", exc, exc_info=True)


_KILLSWITCH_DISPATCHER: object | None = None
#: BRK-064 熔断唯一权威入口的进程级持有位（策略层实例被 GC 即等于入口又变回不唯一）


def _enable_kill_switch_persistence() -> None:
    """Q3/#ARCH-340 · 系统级 KillSwitch 持久化启用（crash-only）— 装配层，幂等。

    病因：系统级开关默认纯内存（无 env 无显式路径=合法默认）⇒ 进程/机器崩溃后
    "已拉闸"这个事实蒸发（漏熔断方向）。

    契约：``get_kill_switch(state_path=...)`` 的路径**仅在单例首次构造时生效**，
    故本函数必须抢在任何无参 ``get_kill_switch()`` 调用者之前执行——
    ``register_boot_hooks`` 首行调用即为此（tech_stack 自检 DD-12 也会无参构造）。
    两处调用幂等：二次调用返回既有单例，参数被忽略。

    非静默契约：若单例已被纯内存态抢先（持久化未生效），打 CRITICAL 留痕但
    不阻断启动（熔断器本体仍可用，仅失去 crash-only）。

    边界：不改 ``kill_switch.py`` 本体（该件 MODIFY-GUARD=Owner approval + 蓝图更新，
    human_gated）——本处仅装配层启用；路径真源 = ``DEFAULT_STATE_RELATIVE``。
    """
    try:
        from zephyr.security.access_control.kill_switch import (
            DEFAULT_STATE_RELATIVE,
            get_kill_switch,
        )

        _ks = get_kill_switch(state_path=REPO_ROOT / DEFAULT_STATE_RELATIVE)
        if _ks.state_path is None:
            logger.critical(
                "KillSwitch 持久化未生效：单例已被纯内存态抢先构造（crash-only 未达成）——"
                "排查先于 _enable_kill_switch_persistence 调用 get_kill_switch() 的路径"
            )
        else:
            logger.info("KillSwitch 系统级持久化已启用: state_path=%s", _ks.state_path)
    except Exception as exc:  # noqa: BLE001 — 持久化启用失败不阻断启动（降级回纯内存=现状）
        logger.warning("KillSwitch 持久化启用失败（降级纯内存态）: %s", exc, exc_info=True)


def _init_kill_switch_orchestrator() -> None:
    """A3 接线（裁定#254）：kill switch 五域编排器开机注册生效。

    编排器只编排不持态——注册失败的单套开关仅告警，不阻断启动；
    后续运维入口经 get_orchestrator() 取同一单例发 trip/reset。

    BRK-064（全流通战役，2026-09-18）追加：同批注册 **三级响应策略层 MOD-AU-004**
    （killswitch_response_levels），使"谁决定拉哪套开关"在运行时确有唯一权威入口——
    策略层（裁决该停什么）→ 路由层（本编排器）→ 执行机构层（5 套开关本体）。
    仅注册不代调用：本批生产侧对 respond() 的调用点仍为 0（如实记黄，见
    docs/_working/fullflow_campaign/lanes/wiresafe_BRK-064_construction_pack.md）。
    """
    try:
        # Q3/#ARCH-340：系统级开关持久化——必须先于下方 tech_stack 自检（其 DD-12
        # 会无参构造 get_kill_switch() 单例，抢先则持久化永不生效）。幂等，可重复调用。
        _enable_kill_switch_persistence()

        from zephyr.autonomy_core.kill_switch_orchestrator import get_orchestrator

        orch = get_orchestrator()
        domains = sorted(orch._domains.keys()) if hasattr(orch, "_domains") else []
        logger.info("KillSwitchOrchestrator booted: system=%s domains=%s", orch._system is not None, domains)
    except Exception as exc:  # noqa: BLE001 — 启动链不因编排器故障失败
        logger.warning(
            "KillSwitchOrchestrator boot failed (kill switches remain independently usable): %s", exc, exc_info=True
        )
        return

    try:
        from zephyr.autonomy_core.killswitch_response_levels import KillSwitchResponseLayer

        global _KILLSWITCH_DISPATCHER  # noqa: PLW0603 — 进程级单例引用，禁被 GC（否则注册即失效）
        _KILLSWITCH_DISPATCHER = KillSwitchResponseLayer(orchestrator=orch, runtime_dir=REPO_ROOT / ".runtime")
        logger.info(
            "KillSwitch 响应策略层已注册（唯一权威 dispatcher，16号文 §3.4 三级映射）：level_1/2/3 → 编排器 route_incident"
        )
    except Exception as exc:  # noqa: BLE001 — 策略层注册失败不得阻断编排器已完成的注册
        logger.warning(
            "KillSwitchResponseLayer 注册失败（五域开关仍各自可用，但失去三级裁决入口）: %s", exc, exc_info=True
        )


# ---------------------------------------------------------------------------
# tech_stack 组件自检（裁定#485，2026-10-08 全流通战役）
# 吸收自 capacity_assurance/tech_stack.py 的 6 项实质检查——原 TechStackValidator
# 全仓零消费（validate_on_startup 无调用点），开机无系统性组件可用性检查；16 项中
# 仅 6 项有实质检查语义（其余为 generic 回显恒 True），吸收/废弃/在档逐项裁定见
# tech_stack_absorption_spec.md §3（阻断 3=DD-1/2/12，警告 3=DD-3/5/16）。
# ---------------------------------------------------------------------------

_tech_stack_check_done = False
#: 幂等标志（对齐 _monitoring_modules_initialized 先例）

_TECH_STACK_MANIFEST_PATH = REPO_ROOT / "config" / "tech_stack_manifest.yaml"
#: manifest 真源（REG-CAP-001 v2.7.0）——直读 repo 根配置，不复刻 tech_stack.py 的
#: 三层 dirname 死亡默认路径（src/zephyr/config/... 不存在，运行时恒走漂移内置副本）

# manifest 缺失/损坏时的最小回退清单——仅含吸收 6 项元数据（不复制全 16 项漂移副本，
#: 治理档缺席只降显示质量，检查集合与分级由裁定表唯一决定）
_TECH_STACK_FALLBACK_DECISIONS: list[dict[str, str]] = [
    {"dd_id": "DD-1", "component": "SLO 配置", "final_choice": "YAML + Pydantic v2"},
    {"dd_id": "DD-2", "component": "审计存储", "final_choice": "SQLite + hash 链"},
    {"dd_id": "DD-3", "component": "指标采样", "final_choice": "structlog + OpenTelemetry SDK"},
    {"dd_id": "DD-5", "component": "治理闭环（共享依赖腿）", "final_choice": "psutil"},
    {"dd_id": "DD-12", "component": "Kill Switch", "final_choice": "环境变量 + 文件信号"},
    {"dd_id": "DD-16", "component": "语义缓存", "final_choice": "ChromaDB 向量相似度"},
]


def _load_tech_stack_metadata() -> dict[str, dict]:
    """读 manifest 真源 → {dd_id: 决策项}；缺失/解析失败回退最小内置清单.

    manifest 是治理档非运行时必需——回退只让组件显示名退化为 dd_id 短标签，
    不改变检查集合与分级（裁定表是唯一分级真源，manifest 漂移不得改动语义）。
    """
    try:
        import yaml

        with open(_TECH_STACK_MANIFEST_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        decisions = data.get("decisions") or []
        meta = {d["dd_id"]: d for d in decisions if isinstance(d, dict) and d.get("dd_id")}
        if not meta:
            raise ValueError("manifest 无 decisions 条目")
        return meta
    except Exception as e:  # noqa: BLE001 — 治理档缺席/损坏不得阻断启动
        logger.warning(
            "tech_stack manifest 真源不可用（%s）：%s — 回退最小内置清单（仅吸收 6 项元数据）",
            _TECH_STACK_MANIFEST_PATH,
            e,
        )
        return {d["dd_id"]: dict(d) for d in _TECH_STACK_FALLBACK_DECISIONS}


def _tech_stack_warn(component: str, detail: str) -> None:
    """WARN 级降级可观测：logger.warning + tech_stack.degraded 指标（复用 observe 先例，不新注册表）."""
    logger.warning("tech_stack 自检降级：%s — %s（启动继续，相关功能降级运行）", component, detail)
    try:
        from zephyr.shared.observability.metrics import MetricsRegistry

        MetricsRegistry().observe("tech_stack.degraded", 1.0, labels={"component": component})
    except Exception as e:  # noqa: BLE001 — 指标链缺席不得放大为启动故障
        logger.debug("tech_stack.degraded metric observe failed: %s", e, exc_info=True)


def _run_tech_stack_self_check() -> None:
    """技术栈组件可用性自检（裁定#485：吸收自 capacity_assurance/tech_stack.py）.

    分级语义：
      BLOCK — DD-1 Pydantic 版本门 / DD-2 SQLite 探活 / DD-12 Kill Switch 通道：raise
              RuntimeError。这是 boot_hooks「失败仅告警」惯例的显式例外：基座错版/缺失时
              后续一切初始化都在错误地基上跑，静默降级比崩溃更危险（fail-fast）。
      WARN  — DD-3 OTel / DD-5 psutil / DD-16 ChromaDB：logger.warning + tech_stack.degraded
              指标，不阻断启动（遥测链有 stub 降级设计、向量记忆 _start_vms 本就「失败仅警告」）。
    逃生门：ZEPHYR_TECH_STACK_CHECK=0 全关；=warn 时 BLOCK 降为警告（调试用）。
    pytest 隔离：PYTEST_CURRENT_TEST 在岗时跳过 DD-16（对齐 _subscribe_governance_regeneration
    守卫先例；chromadb 探测慢且测试环境可能缺席）。
    """
    global _tech_stack_check_done
    if _tech_stack_check_done:
        logger.debug("Tech stack self-check already done, skipping (idempotent)")
        return
    _tech_stack_check_done = True

    import os

    mode = os.environ.get("ZEPHYR_TECH_STACK_CHECK", "1").strip().lower()
    if mode in ("0", "false", "off", "no"):
        logger.info("Tech stack self-check disabled via ZEPHYR_TECH_STACK_CHECK=%s", mode)
        return
    warn_only = mode in ("warn", "warn_only", "warn-only")

    meta = _load_tech_stack_metadata()

    def _label(dd_id: str) -> str:
        entry = meta.get(dd_id) or {}
        return f"{dd_id} {entry.get('component') or dd_id}"

    block_failures: list[str] = []

    # ---- BLOCK 级 ×3（裁定表：DD-1/2/12）----
    # DD-1 版本门：v1/v2 API 不兼容（191 文件基座）——错版在随机位置崩不如一条明确 RuntimeError。
    # import 失败实际到不了此处（启动链已隐式 import pydantic），到=环境诡异仍阻断。
    try:
        import pydantic

        if pydantic.__version__.startswith("2."):
            logger.info("tech_stack 自检通过：%s — pydantic==%s", _label("DD-1"), pydantic.__version__)
        else:
            block_failures.append(
                f"{_label('DD-1')}：检测到 pydantic=={pydantic.__version__}，需要 v2.x"
                " — 修复：pip install 'pydantic>=2.0'"
            )
    except Exception as e:  # noqa: BLE001 — 到此=环境级故障，阻断
        block_failures.append(f"{_label('DD-1')}：pydantic 不可用（{e!r}）— 修复：pip install 'pydantic>=2.0'")

    # DD-2 探活：内存库 SELECT 1——sqlite 编译进解释器属环境级基座；文件库连通已由
    # boot_sequence 真实开库覆盖，不重复造。
    try:
        import sqlite3

        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
        logger.info("tech_stack 自检通过：%s — sqlite3==%s", _label("DD-2"), sqlite3.sqlite_version)
    except Exception as e:  # noqa: BLE001 — 标准库损坏属环境级故障
        block_failures.append(
            f"{_label('DD-2')}：SQLite 探活失败（{e!r}）— 修复：检查 Python sqlite3 模块是否编译进当前解释器"
        )

    # DD-12 Kill Switch 通道（裁定表新设计检查体，超出原 tech_stack.py generic 能力）：
    # 唯一 hot plane 安全件（宪法 §7）——单例可达 + state 影子件（启用持久化时）可解析；
    # 纯内存态（无 env 无显式路径）是合法默认。只做通道存在性早检，与后段
    # _init_kill_switch_orchestrator 的五域注册不重复。影子件损坏时单例自身已 fail-closed
    # 按 ENGAGED 处置，此处再解析一次是为了给出可诊断的阻断而非静默带 ENGAGED 启动。
    try:
        import json as _json

        from zephyr.security.access_control.kill_switch import get_kill_switch

        ks = get_kill_switch()
        state_path = getattr(ks, "state_path", None)
        if state_path is not None and state_path.is_file():
            payload = _json.loads(state_path.read_text(encoding="utf-8"))
            if not isinstance(payload.get("engaged"), bool):
                raise ValueError("state payload malformed (engaged)")
        logger.info(
            "tech_stack 自检通过：%s — 单例可达 state_channel=%s",
            _label("DD-12"),
            state_path if state_path is not None else "in-memory",
        )
    except Exception as e:  # noqa: BLE001 — hot 安全件通道失位=阻断
        block_failures.append(
            f"{_label('DD-12')}：Kill Switch 通道失位（{e!r}）— 修复：核查 "
            "zephyr.security.access_control.kill_switch 模块与 state 影子件"
            "（env ZEPHYR_KILL_SWITCH_STATE_PATH；损坏文件删除或修复后重启）"
        )

    # ---- WARN 级 ×3（裁定表：DD-3/5/16 — 降级可跑）----
    import importlib.util

    # DD-3 OTel：遥测链有 stub 降级（tracing/span_stub 缺席可跑）；find_spec 探测不真 import
    if importlib.util.find_spec("opentelemetry") is None:
        _tech_stack_warn(_label("DD-3"), "opentelemetry 未安装 — 修复：pip install opentelemetry-api opentelemetry-sdk")

    # DD-5 psutil（裁定表拆分项：检查对象=psutil 共享依赖、多域消费；EMA 算法本体
    # 无可检依赖，保留在档不吸收）
    if importlib.util.find_spec("psutil") is None:
        _tech_stack_warn(_label("DD-5"), "psutil 未安装 — 修复：pip install psutil")

    # DD-16 ChromaDB：向量记忆降级（_start_vms 本就「失败仅警告」）；pytest 下跳过
    if not os.environ.get("PYTEST_CURRENT_TEST") and importlib.util.find_spec("chromadb") is None:
        _tech_stack_warn(_label("DD-16"), "chromadb 未安装 — 修复：pip install chromadb")

    if block_failures:
        message = "；".join(block_failures)
        if warn_only:
            logger.warning("tech_stack 自检 BLOCK 项被降级为警告（ZEPHYR_TECH_STACK_CHECK=warn，调试用）：%s", message)
            return
        raise RuntimeError(f"tech_stack 自检阻断（裁定#485 BLOCK 级组件失位，启动中止）：{message}")
    logger.info("tech_stack 自检完成：吸收 6 项（阻断 3/警告 3）全部通过或按级处置")


def register_boot_hooks(
    task_repo: TaskRepositoryProtocol | None = None,
    budget_engine: BudgetEngineProtocol | None = None,
) -> None:
    # Q3/#ARCH-340：系统级 KillSwitch 持久化启用——必须是本启动链**第一步**：
    # tech_stack 自检（下一条）的 DD-12 会无参调用 get_kill_switch() 抢先构造
    # 纯内存单例，其后任何 state_path 传参都会被忽略（首构造锁死语义）。幂等。
    _enable_kill_switch_persistence()
    # 裁定#485：依赖面自检先行——先于全部订阅/重初始化逻辑，使后继初始化的成败可归因。
    # BLOCK 级 raise 不包裹（register_task_system_hooks 与 boot() 对本函数均无 try，
    # 直达 __main__ 非零退出——设计意图，见细案 §4.1）。
    _run_tech_stack_self_check()
    try:
        from zephyr.governance.event_hook import (  # noqa: import-integrity  — sys.modules shim registered in governance/__init__.py
            hook_registry,  # noqa: import-integrity  sys.modules shim registered in governance/__init__.py
        )

        # Task system hooks — 需要 task_repo 的用 lambda 绑定
        hook_registry.register(
            lambda e: _hook_auto_unblock_dependents(e, task_repo), priority=50, name="auto_unblock_dependents"
        )
        hook_registry.register(
            lambda e: _hook_auto_retry_on_failure(e, task_repo), priority=60, name="auto_retry_on_failure"
        )
        hook_registry.register(
            lambda e: _hook_triple_alignment_on_verified(e, task_repo), priority=70, name="triple_alignment_on_verified"
        )
        hook_registry.register(lambda e: _hook_orc_vms_archive(e, task_repo), priority=48, name="orc_vms_archive")
        hook_registry.register(_hook_rbk_gate_freeze, priority=55, name="rbk_gate_freeze")
        logger.info(
            "Task system hooks registered: auto_unblock_dependents / auto_retry_on_failure / triple_alignment_on_verified / orc_vms_archive / rbk_gate_freeze"
        )

        # Event-driven hooks
        hook_registry.register(
            lambda e: _hook_escalation_check(e, task_repo), priority=56, name="escalation_check_event"
        )
        hook_registry.register(lambda e: _hook_timeout_check(e, task_repo), priority=56, name="timeout_check_event")
        hook_registry.register(lambda e: _hook_budget_delta(e, budget_engine), priority=94, name="budget_delta_event")
        hook_registry.register(_hook_session_startup_init_budget, priority=10, name="session_startup_init_budget")
        hook_registry.register(_hook_session_shutdown_budget_close, priority=90, name="session_shutdown_budget_close")
        hook_registry.register(_hook_triple_align_event, priority=72, name="triple_align_event")

        try:
            from zephyr.shared.event_bus import bus as _bus

            _bus.subscribe("blueprint.changed", _hook_triple_align_event)
            _bus.subscribe("blueprint.decomposed", _hook_triple_align_event)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("EventBus subscribe failed for triple_align blueprint hooks", exc_info=True)

        logger.info(
            "Event-driven hooks registered: escalation_check / timeout_check / budget_delta / session_startup_init_budget / session_shutdown_budget_close / triple_align"
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Failed to register task system hooks: %s", e, exc_info=True)

    # IdeHealthDaemon 常驻守护模式已于 2026-08-28 裁定废弃（OS 托管 ProcessReaper 替代，
    # 见 docs/03_modules/_domain_data/boot_autostart_architecture.md §2），此处不再注册。

    _subscribe_task_lifecycle_events(budget_engine=budget_engine)
    _register_rbac_hooks()
    _init_shared_monitoring_modules()
    _init_kill_switch_orchestrator()

    # P0-2 修复：RollbackBootIntegration 启动钩子接线 — WAL/Verifier 自动初始化
    try:
        from zephyr.infrastructure.rollback.rollback_boot_integration import RollbackBootIntegration

        _rollback_boot = RollbackBootIntegration(project_root=REPO_ROOT)
        _rollback_boot.register_startup_hook()
        logger.info("RollbackBootIntegration: registered startup hook (WAL+Verifier init)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("RollbackBootIntegration: register failed: %s", e, exc_info=True)

    # P1-10 修复：SLAMonitor 永久系统启动接入 — 事件驱动 RTO/RPO 自动记录
    try:
        from zephyr.infrastructure.sla.sla_monitor import SLAMonitor

        _sla_monitor = SLAMonitor()
        _sla_monitor.subscribe_eventbus()
        logger.info("SLAMonitor: subscribed to EventBus (RTO/RPO auto-record)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("SLAMonitor: subscribe failed: %s", e, exc_info=True)

    # P1-10 修复：Notifier 永久系统启动接入 — 事件驱动 Owner 通知
    try:
        from zephyr.infrastructure.observability.notifier import Notifier

        _notifier = Notifier()
        _notifier.subscribe_eventbus()
        logger.info("Notifier: subscribed to EventBus (pipeline_failed/kill_switch auto-notify)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Notifier: subscribe failed: %s", e, exc_info=True)

    # P1-10 修复：HealthAggregator 永久系统启动接入 — 事件驱动健康快照
    try:
        from zephyr.infrastructure.system_telemetry.health_aggregator import HealthAggregator

        _health_aggregator = HealthAggregator()
        _health_aggregator.subscribe_eventbus()
        logger.info("HealthAggregator: subscribed to EventBus (critical event auto-snapshot)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("HealthAggregator: subscribe failed: %s", e, exc_info=True)

    # AI-11 审计修复：F5 永久系统启动/关闭钩子接线 — F5四组件自动初始化+自动关闭
    # 审计发现：register_f5_boot_hook/register_f5_shutdown_hook 已定义但从未被 boot_hooks 调用，
    # 导致 F5 启动初始化（DeadlockDetector/EscalationEngine/DelegationEngine/Arbitrator）
    # 和关闭清理从未自动执行，违反 C类永久系统四要素（自动启动/关闭）。
    _f5_integration = None
    try:
        from zephyr.governance.resilience_governance.f5_boot_integration import register_f5_boot_hook

        _f5_integration = register_f5_boot_hook(project_root=REPO_ROOT)
        logger.info("F5BootIntegration: registered startup hook (F5四组件 auto-init)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("F5BootIntegration: register failed: %s", e, exc_info=True)

    try:
        from zephyr.governance.resilience_governance.f5_shutdown_manager import register_f5_shutdown_hook

        register_f5_shutdown_hook(integration=_f5_integration, project_root=REPO_ROOT)
        logger.info("F5ShutdownManager: installed shutdown hook (F5 auto-shutdown)")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("F5ShutdownManager: install failed: %s", e, exc_info=True)

    _subscribe_eventbus_consumers()
    _subscribe_skill_freshness_events()
    _subscribe_governance_regeneration()

    # 红蓝对抗提交触发消费线程 (MOD-INF-030 事件驱动)：daemon 线程轮询
    # data/red_blue/trigger_queue/，门禁达标时跑 TIER_1 对抗。
    # 就位+门禁激活：始终启动；ZEPHYR_RED_BLUE_AUTO_ENABLED!=1 时只 log 不实跑。
    try:
        from zephyr.security.adversarial_validation.commit_trigger import (
            RedBlueTriggerConsumer,
        )

        RedBlueTriggerConsumer().start()
        logger.info("RedBlueTriggerConsumer: started via boot hooks")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("MCP cluster auto-start FAILED: %s", exc, exc_info=True)

    mcp_thread = threading.Thread(target=_start_mcp_cluster, name="mcp-cluster-launcher", daemon=True)
    mcp_thread.start()
    logger.info("MCP cluster auto-start thread launched (daemon=True)")
