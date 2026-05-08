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
