# [A_test] module_id: SRC-TST-1226 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
from __future__ import annotations

# [A_test] module_id=T-GEN_test_lifecycle_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_lifecycle_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.shared.contracts.runtime_types import RuntimeConfig
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.dream_cycle import DreamCycle
from zephyr.feedback_loop import FeedbackLoop
from zephyr.trading.finalizer import Finalizer
from zephyr.trading.health_monitor import HealthMonitor
from zephyr.trading.integration_registry import IntegrationRegistry
from zephyr.trading.lifecycle_manager import BootReport, LifecycleManager, ShutdownReport
from zephyr.trading.night_shift_queue import NightShiftQueue
from zephyr.trading.stop_gate import StopGate
from zephyr.trading.work_orchestrator import WorkOrchestrator


def _make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        audit_log_dir=tmp_path / "audit",
        capability_card_dir=tmp_path / "cards",
        work_dag_dir=tmp_path / "dags",
        dream_archive_dir=tmp_path / "dream",
        feedback_proposal_dir=tmp_path / "feedback",
        health_snapshot_dir=tmp_path / "health",
        night_shift_storage_path=tmp_path / "nshift.jsonl",
    )


class TestBootReport:
    def test_defaults(self) -> None:
        br = BootReport()
        assert br.success is True
        assert br.steps_completed == 0
        assert br.errors == []
        assert br.components_started == []


class TestShutdownReport:
    def test_defaults(self) -> None:
        sr = ShutdownReport()
        assert sr.steps_completed == 0
        assert sr.errors == []
        assert sr.finalizer_results == {}


class TestLifecycleManagerInit:
    def test_init(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        assert lm._config is config


class TestBootSequence:
    def test_boot_sequence_success(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        audit_logger = MagicMock()
        registry = CapabilityRegistry()
        night_shift = NightShiftQueue(tmp_path / "nshift.jsonl")
        health_monitor = HealthMonitor()
        integration_reg = IntegrationRegistry()
        work_orch = WorkOrchestrator(registry, dag_dir=tmp_path / "dags")
        dream = DreamCycle(archive_dir=tmp_path / "dream")
        feedback = FeedbackLoop(proposal_dir=tmp_path / "feedback")
        stop_gate = StopGate()
        finalizer = Finalizer()

        with (
            patch.object(lm, "_start_self_monitor"),
            patch.object(lm, "_start_governance_watchdog"),
        ):
            report = lm.boot_sequence(
                audit_logger=audit_logger,
                registry=registry,
                night_shift_queue=night_shift,
                health_monitor=health_monitor,
                integration_registry=integration_reg,
                work_orchestrator=work_orch,
                dream_cycle=dream,
                feedback_loop=feedback,
                stop_gate=stop_gate,
                finalizer=finalizer,
            )

        assert isinstance(report, BootReport)
        assert report.steps_completed > 0
        assert report.success is True
        assert len(report.errors) == 0

    def test_boot_sequence_registers_finalizers(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        audit_logger = MagicMock()
        registry = CapabilityRegistry()
        night_shift = NightShiftQueue(tmp_path / "nshift.jsonl")
        health_monitor = HealthMonitor()
        integration_reg = IntegrationRegistry()
        work_orch = WorkOrchestrator(registry, dag_dir=tmp_path / "dags")
        dream = DreamCycle(archive_dir=tmp_path / "dream")
        feedback = FeedbackLoop(proposal_dir=tmp_path / "feedback")
        stop_gate = StopGate()
        finalizer = Finalizer()

        with (
            patch.object(lm, "_start_self_monitor"),
            patch.object(lm, "_start_governance_watchdog"),
        ):
            lm.boot_sequence(
                audit_logger=audit_logger,
                registry=registry,
                night_shift_queue=night_shift,
                health_monitor=health_monitor,
                integration_registry=integration_reg,
                work_orchestrator=work_orch,
                dream_cycle=dream,
                feedback_loop=feedback,
                stop_gate=stop_gate,
                finalizer=finalizer,
            )

        assert len(finalizer._cleanup_fns) == 3
        types = [t for t, _ in finalizer._cleanup_fns]
        assert "night_shift_queue" in types
        assert "capability_registry" in types
        assert "health-monitor" in types

    def test_boot_sequence_step_failure(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        audit_logger = MagicMock()
        registry = MagicMock()
        registry.load_from_dir.side_effect = RuntimeError("load failed")
        night_shift = MagicMock()
        health_monitor = MagicMock()
        integration_reg = MagicMock()
        work_orch = MagicMock()
        dream = MagicMock()
        feedback = MagicMock()
        stop_gate = MagicMock()
        finalizer = Finalizer()

        with (
            patch.object(lm, "_start_self_monitor"),
            patch.object(lm, "_start_governance_watchdog"),
        ):
            report = lm.boot_sequence(
                audit_logger=audit_logger,
                registry=registry,
                night_shift_queue=night_shift,
                health_monitor=health_monitor,
                integration_registry=integration_reg,
                work_orchestrator=work_orch,
                dream_cycle=dream,
                feedback_loop=feedback,
                stop_gate=stop_gate,
                finalizer=finalizer,
            )

        assert report.success is False
        assert len(report.errors) > 0


class TestShutdownSequence:
    def test_shutdown_sequence(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        stop_gate = MagicMock()
        finalizer = MagicMock()
        finalizer.run.return_value = {"resource_a": True}
        health_monitor = MagicMock()
        audit_logger = MagicMock()

        report = lm.shutdown_sequence(
            stop_gate=stop_gate,
            finalizer=finalizer,
            health_monitor=health_monitor,
            audit_logger=audit_logger,
        )

        assert isinstance(report, ShutdownReport)
        assert report.steps_completed == 4
        finalizer.run.assert_called_once()
        health_monitor.stop.assert_called_once()
        audit_logger.flush.assert_called_once()
        stop_gate.acknowledge_shutdown.assert_called_once()

    def test_shutdown_sequence_finalizer_results(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        lm = LifecycleManager(config)
        stop_gate = MagicMock()
        finalizer = MagicMock()
        finalizer.run.return_value = {"db": True, "cache": False}
        health_monitor = MagicMock()
        audit_logger = MagicMock()

        report = lm.shutdown_sequence(
            stop_gate=stop_gate,
            finalizer=finalizer,
            health_monitor=health_monitor,
            audit_logger=audit_logger,
        )

        assert report.finalizer_results == {"db": True, "cache": False}
