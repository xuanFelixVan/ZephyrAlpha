# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.runtime.lifecycle_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
LifecycleManager — 启动/停止序列
==================================
蓝图: ARC-0001 §6.3
借鉴: K8s Init Containers + Sidecar + Finalizer
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.runtime.ai_audit_logger import AiAuditLogger
from zephyr.runtime.capability_registry import CapabilityRegistry
from zephyr.runtime.circadian_scheduler import CircadianScheduler
from zephyr.runtime.dream_cycle import DreamCycle
from zephyr.runtime.feedback_loop import FeedbackLoop
from zephyr.runtime.finalizer import Finalizer
from zephyr.runtime.health_monitor import HealthMonitor
from zephyr.runtime.integration_registry import IntegrationRegistry
from zephyr.runtime.night_shift_queue import NightShiftQueue
from zephyr.runtime.runtime_config import RuntimeConfig
from zephyr.runtime.stop_gate import StopGate
from zephyr.runtime.work_orchestrator import WorkOrchestrator


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
        circadian_scheduler: CircadianScheduler,
        dream_cycle: DreamCycle,
        feedback_loop: FeedbackLoop,
        stop_gate: StopGate,
        finalizer: Finalizer,
    ) -> BootReport:
        report = BootReport()
        steps = [
            ("01_config_validate", lambda: self._config.ensure_dirs()),
            ("02_stop_gate_init", lambda: stop_gate.initialize()),
            ("03_audit_logger_start", lambda: None),
            ("04_registry_load", lambda: registry.load_from_dir()),
            ("05_work_orch_load_dags", lambda: work_orchestrator.load_dags()),
            ("06_circadian_start", lambda: circadian_scheduler.start()),
            ("07_health_monitor_start", lambda: health_monitor.start()),
            ("08_integration_validate", lambda: integration_registry.validate_all()),
            ("08a_audit_schedule_register", lambda: self._register_audit_tasks(circadian_scheduler)),
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
        finalizer.register("health_monitor", lambda: health_monitor.dump_last_snapshot())
        finalizer.register("circadian_scheduler", circadian_scheduler.save_state)

        return report

    def _register_audit_tasks(self, circadian_scheduler: CircadianScheduler) -> None:
        from zephyr.audit_trail.merkle_hourly import HourlyMerkleAggregator
        from zephyr.audit_trail.log_rotation import LogRotationManager
        from zephyr.audit_trail.retention import RetentionEnforcer
        from zephyr.audit_trail.tiered_storage import TieredStorageManager

        merkle = HourlyMerkleAggregator()
        circadian_scheduler.register_task(hour=0, name="merkle_hourly_aggregate", layer="L1", callback=merkle.aggregate)

        log_rot = LogRotationManager()
        circadian_scheduler.register_task(hour=1, name="audit_log_rotation", layer="L1", callback=log_rot.rotate)

        retention = RetentionEnforcer()
        circadian_scheduler.register_task(hour=2, name="audit_retention_dry_run", layer="L1", callback=retention.dry_run)

        tiered = TieredStorageManager()
        circadian_scheduler.register_task(hour=3, name="audit_tiered_storage_migrate", layer="L1", callback=tiered.auto_migrate)

        def _finding_lifecycle_cleanup() -> None:
            from scripts.governance._finding_lifecycle import FindingLifecycleManager
            FindingLifecycleManager().run_cleanup(dry_run=False)

        circadian_scheduler.register_task(hour=4, name="finding_lifecycle_cleanup", layer="L1", callback=_finding_lifecycle_cleanup)

        def _gate_cache_daily_invalidate() -> None:
            from scripts.governance.observability.gate_cache import GateCache
            GateCache().invalidate_all("*")

        circadian_scheduler.register_task(hour=0, name="gate_cache_daily_invalidate", layer="L1", callback=_gate_cache_daily_invalidate)

    def _start_self_monitor(self) -> None:
        from zephyr.audit_trail.self_monitor import SelfMonitor
        self._audit_self_monitor = SelfMonitor()
        self._audit_self_monitor.start_scheduler(daemon=True)

    def _start_governance_watchdog(self) -> None:
        from scripts.governance.governance_watchdog import GovernanceWatchdog
        self._governance_watchdog = GovernanceWatchdog()
        self._governance_watchdog.run(daemon=True)

    def shutdown_sequence(
        self,
        stop_gate: StopGate,
        circadian_scheduler: CircadianScheduler,
        finalizer: Finalizer,
        health_monitor: HealthMonitor,
        audit_logger: AiAuditLogger,
    ) -> ShutdownReport:
        report = ShutdownReport()

        circadian_scheduler.stop()
        report.steps_completed += 1

        report.finalizer_results = finalizer.run()
        report.steps_completed += 1

        health_monitor.stop()
        report.steps_completed += 1

        audit_logger.flush()
        report.steps_completed += 1

        stop_gate.acknowledge_shutdown()
        report.steps_completed += 1

        return report
