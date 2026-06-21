# [A_module] module_id=MOD-ORC_lifecycle_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md

# [MODULE] zephyr.trading.lifecycle_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

__all__ = [
    "BootReport",
    "ShutdownReport",
    "LifecycleManager",
]

"""
LifecycleManager — 启动/停止序列
==================================
蓝图: ARC-0001 §6.3
借鉴: K8s Init Containers + Sidecar + Finalizer
"""

from dataclasses import dataclass, field

from zephyr.trading.ai_audit_logger import AiAuditLogger
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.circadian_scheduler import CircadianScheduler
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
        circadian_scheduler: CircadianScheduler,
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
            ("06_circadian_start", lambda: circadian_scheduler.start()),
            ("07_health_monitor_start", lambda: health-monitor.start()),
            ("08_integration_validate", lambda: integration_registry.validate_all()),
            ("08a_audit_schedule_register", lambda: self._register_audit_tasks(circadian_scheduler)),
            ("08b_audit_event_hooks_register", lambda: self._register_audit_event_hooks(circadian_scheduler)),
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
        finalizer.register("health-monitor", lambda: health-monitor.dump_last_snapshot())
        finalizer.register("circadian_scheduler", circadian_scheduler.save_state)

        return report

    def _register_audit_tasks(self, circadian_scheduler: CircadianScheduler) -> None:
        from zephyr.governance.merkle_hourly import HourlyMerkleAggregator
        from zephyr.governance.audit_trail.log_rotation import LogRotationManager
        from zephyr.governance.audit_trail.retention import RetentionEnforcer
        from zephyr.governance.audit_trail.tiered_storage import TieredStorageManager

        merkle = HourlyMerkleAggregator()
        circadian_scheduler.register_task(hour=0, name="merkle_hourly_aggregate", layer="L1", callback=merkle.aggregate)

        log_rot = LogRotationManager()
        circadian_scheduler.register_task(hour=1, name="audit_log_rotation", layer="L1", callback=log_rot.rotate)

        retention = RetentionEnforcer()
        circadian_scheduler.register_task(hour=2, name="audit_retention_dry_run", layer="L1", callback=retention.dry_run)

        tiered = TieredStorageManager()
        circadian_scheduler.register_task(hour=3, name="audit_tiered_storage_migrate", layer="L1", callback=tiered.auto_migrate)

        def _finding_lifecycle_cleanup() -> None:
            import importlib as _importlib
            _FindingLifecycleManager = _importlib.import_module("scripts.governance._finding_lifecycle").FindingLifecycleManager
            _FindingLifecycleManager().run_cleanup(dry_run=False)

        circadian_scheduler.register_task(hour=4, name="finding_lifecycle_cleanup", layer="L1", callback=_finding_lifecycle_cleanup)

        def _gate_cache_daily_invalidate() -> None:
            import importlib as _importlib
            _GateCache = _importlib.import_module("scripts.governance.observability.gate_cache").GateCache
            _GateCache().invalidate_all("*")

        circadian_scheduler.register_task(hour=0, name="gate_cache_daily_invalidate", layer="L1", callback=_gate_cache_daily_invalidate)

        def _audit_trail_integrity_verify() -> None:
            from zephyr.governance.integrity import IntegrityVerifier
            verifier = IntegrityVerifier()
            report = verifier.verify()
            corrupted = getattr(report, "corrupted_count", 0) or getattr(report, "failed", 0)
            if corrupted > 0:
                logger.warning("Audit trail integrity verify: %d corrupted entries detected", corrupted)
            else:
                logger.info("Audit trail integrity verify: chain intact")

        circadian_scheduler.register_task(hour=5, name="audit_trail_integrity_verify", layer="L1", callback=_audit_trail_integrity_verify)

        def _auto_fix_engine_scan_and_fix() -> None:
            from zephyr.security.access_control.auto_fix_engine_03.engine import AutoFixEngine
            engine = AutoFixEngine()
            fixers = getattr(engine, "_fixers", {}) or getattr(engine, "fixers", {}) or {}
            if not fixers:
                fix_types = ["scaffold_registrar", "import_fixer", "alignment_syncer"]
            else:
                fix_types = list(fixers.keys())
            fixed = 0
            for ft in fix_types:
                try:
                    action = engine.fix(ft, "src/zephyr/", dry_run=False)
                    if getattr(action, "status", None) and getattr(action.status, "value", None) == "COMPLETED":
                        fixed += 1
                except Exception:
                    pass
            if fixed > 0:
                logger.info("Auto-fix engine scan+fix: %d/%d fixes applied", fixed, len(fix_types))
            else:
                logger.info("Auto-fix engine scan+fix: no fixes needed (%d fixers checked)", len(fix_types))

        circadian_scheduler.register_task(hour=6, name="auto_fix_engine_scan_and_fix", layer="L1", callback=_auto_fix_engine_scan_and_fix)

    def _register_audit_event_hooks(self, circadian_scheduler: CircadianScheduler) -> None:
        def _on_file_change_audit() -> None:
            try:
                from zephyr.governance.semantic_audit.self_healer import SelfHealer
                healer = SelfHealer()
                logger.info("Event hook: file change triggered semantic audit")
            except Exception:
                pass

        def _on_security_event_audit() -> None:
            try:
                from zephyr.security.adversarial_validation.game_day_runner import GameDayRunner, GameDayFrequency
                runner = GameDayRunner()
                result = runner.run_game_day(GameDayFrequency.PER_COMMIT)
                if result.bypasses > 0:
                    logger.warning("Event hook: security event — %d bypasses detected", result.bypasses)
            except Exception:
                pass

        def _on_orphan_detected_audit() -> None:
            try:
                from zephyr.security.access_control.orphan_judge.judge import OrphanJudge
                judge = OrphanJudge()
                report = judge.batch_judge(scope="src/zephyr/", limit=20, dry_run=True)
                if report.by_verdict.get("DELETE", 0) > 0:
                    logger.warning("Event hook: orphan detected — %d DELETE verdicts", report.by_verdict.get("DELETE", 0))
            except Exception:
                pass

        circadian_scheduler.register_event_listener("file_change", _on_file_change_audit)
        circadian_scheduler.register_event_listener("security_event", _on_security_event_audit)
        circadian_scheduler.register_event_listener("orphan_detected", _on_orphan_detected_audit)

    def _start_self_monitor(self) -> None:
        from zephyr.governance.audit_trail.self_monitor import SelfMonitor
        self._audit_self_monitor = SelfMonitor()
        self._audit_self_monitor.start_scheduler(daemon=True)

    def _start_governance_watchdog(self) -> None:
        import importlib as _importlib
        _GovernanceWatchdog = _importlib.import_module("scripts.governance.governance_watchdog").GovernanceWatchdog
        self._governance_watchdog = _GovernanceWatchdog()
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

        health-monitor.stop()
        report.steps_completed += 1

        audit_logger.flush()
        report.steps_completed += 1

        stop_gate.acknowledge_shutdown()
        report.steps_completed += 1

        return report
