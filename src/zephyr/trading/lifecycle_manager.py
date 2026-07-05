# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md
# [MODULE] zephyr.trading.lifecycle_manager
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.governance.merkle_hourly; zephyr.governance.audit_trail.log_rotation; zephyr.governance.audit_trail.retention; zephyr.governance.audit_trail.tiered_storage; zephyr.governance.audit_trail.self_monitor; zephyr.governance.integrity; zephyr.infrastructure.auto_fix_engine.engine; zephyr.governance.semantic_audit.self_healer; zephyr.security.adversarial_validation.game_day_runner; zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md;并发修改需通过任务卡通道+Owner批准;已知接口漂移回归bug(4次):L134 retention.enforce(dry_run=True)非retention.dry_run;L139 tiered.migrate(dry_run=False)非tiered.auto_migrate;L247删除start_scheduler调用(SelfMonitor无此方法);禁止AI自主修改
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_lifecycle_manager | layer=module | stability=evolving | safety=L | ai_autonomy=immutable_core
# [CHANGE-NOTE] 2026-06-26: Owner 授权手术式修改——移除 CircadianScheduler 依赖（项目硬约束"废除CircadianScheduler定时触发机制"）。
# [TTL] permanent
#   删除 circadian_scheduler 参数（boot_sequence/shutdown_sequence）、_register_audit_tasks（no-op）、
#   _register_audit_event_hooks（注册的回调因 trigger_event 从未被调用而永不触发=死代码）、
#   circadian_scheduler.start()/.stop() no-op 调用、finalizer.register("circadian_scheduler", ...)。
#   未改动 boot/shutdown 语义与其他组件逻辑。

__all__ = [
    "BootReport",
    "LifecycleManager",
    "ShutdownReport",
]

"""
LifecycleManager — 启动/停止序列
==================================
蓝图: ARC-0001 §6.3
借鉴: K8s Init Containers + Sidecar + Finalizer
"""

from dataclasses import dataclass, field
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

from zephyr.trading.ai_audit_logger import AiAuditLogger
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.dream_cycle import DreamCycle
from zephyr.trading.feedback_loop import FeedbackLoop
from zephyr.trading.finalizer import Finalizer
from zephyr.trading.health_monitor import HealthMonitor
from zephyr.trading.integration_registry import IntegrationRegistry
from zephyr.trading.night_shift_queue import NightShiftQueue
from zephyr.trading.runtime_config import RuntimeConfig, ensure_runtime_dirs
from zephyr.trading.stop_gate import StopGate
from zephyr.trading.work_orchestrator import WorkOrchestrator


@dataclass
class BootReport:
    success: bool = True
    steps_completed: int = 0
    errors: list[str] = field(default_factory=list)
    components_started: list[str] = field(default_factory=list)


@dataclass
class ShutdownReport:
    steps_completed: int = 0
    errors: list[str] = field(default_factory=list)
    finalizer_results: dict[str, bool] = field(default_factory=dict)


class LifecycleManager:
    """生命周期管理器——Boot + Shutdown 序列。"""

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config

    def boot_sequence(
        self,
        audit_logger: AiAuditLogger,
        registry: CapabilityRegistry,
        night_shift_queue: NightShiftQueue,
        health_monitor: HealthMonitor,
        integration_registry: IntegrationRegistry,
        work_orchestrator: WorkOrchestrator,
        dream_cycle: DreamCycle,
        feedback_loop: FeedbackLoop,
        stop_gate: StopGate,
        finalizer: Finalizer,
    ) -> BootReport:
        report = BootReport()
        steps = [
            ("01_config_validate", lambda: ensure_runtime_dirs(self._config)),
            ("02_stop_gate_init", lambda: stop_gate.initialize()),
            ("03_audit_logger_start", lambda: None),
            ("04_registry_load", lambda: registry.load_from_dir()),
            ("05_work_orch_load_dags", lambda: work_orchestrator.load_dags()),
            # 06_circadian_start 已移除：CircadianScheduler 定时调度废除（2026-06-26裁定）
            ("07_health_monitor_start", lambda: health_monitor.start()),
            ("08_integration_validate", lambda: integration_registry.validate_all()),
            # 08a_audit_schedule_register / 08b_audit_event_hooks_register 已移除：
            #   _register_audit_tasks 为 no-op；_register_audit_event_hooks 注册的回调因
            #   CircadianScheduler.trigger_event 从未被调用而永不触发=死代码。
            ("09_audit_self_monitor_start", lambda: self._start_self_monitor()),
            ("09a_governance_watchdog_start", lambda: self._start_governance_watchdog()),
        ]

        for name, fn in steps:
            try:
                fn()
                report.steps_completed += 1
                report.components_started.append(name)
            except Exception as e:
                report.errors.append(f"{name}: {e}")
                report.success = False

        finalizer.register("night_shift_queue", night_shift_queue.flush_all)
        finalizer.register("capability_registry", lambda: registry.dump_snapshot())
        finalizer.register("health-monitor", lambda: health_monitor.dump_last_snapshot())
        # finalizer.register("circadian_scheduler", ...) 已移除：save_state 为 no-op（CircadianScheduler 废除）

        return report

    def _start_self_monitor(self) -> None:
        from zephyr.governance.audit_trail.self_monitor import SelfMonitor

        self._audit_self_monitor = SelfMonitor()

    def _start_governance_watchdog(self) -> None:
        import sys as _sys

        _governance_dir = str(REPO_ROOT / "scripts" / "governance")
        if _governance_dir not in _sys.path:
            _sys.path.insert(0, _governance_dir)
        from meta.governance_watchdog import GovernanceWatchdog as _GovernanceWatchdog
        self._governance_watchdog = _GovernanceWatchdog()
        self._governance_watchdog.run(daemon=True)

    def shutdown_sequence(
        self,
        stop_gate: StopGate,
        finalizer: Finalizer,
        health_monitor: HealthMonitor,
        audit_logger: AiAuditLogger,
    ) -> ShutdownReport:
        report = ShutdownReport()

        # circadian_scheduler.stop() 已移除：no-op（CircadianScheduler 废除，2026-06-26裁定）

        # 5.144.1 修复: 4步清理无异常隔离, 若 finalizer.run() 抛异常后续 3 步全被跳过。
        # 每步独立 try/except, 异常收集到 report.errors 保证清理顺序确定性
        try:
            report.finalizer_results = finalizer.run()
            report.steps_completed += 1
        except Exception as exc:
            report.errors.append(f"finalizer.run failed: {exc}")

        try:
            health_monitor.stop()
            report.steps_completed += 1
        except Exception as exc:
            report.errors.append(f"health_monitor.stop failed: {exc}")

        try:
            audit_logger.flush()
            report.steps_completed += 1
        except Exception as exc:
            report.errors.append(f"audit_logger.flush failed: {exc}")

        try:
            stop_gate.acknowledge_shutdown()
            report.steps_completed += 1
        except Exception as exc:
            report.errors.append(f"stop_gate.acknowledge_shutdown failed: {exc}")

        return report
