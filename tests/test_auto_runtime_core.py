# [A_test] module_id: SRC-TST-0381 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
from __future__ import annotations

# [A_test] module_id=T-GEN_test_auto_runtime_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] tests.test_auto_runtime_core
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_auto_runtime_core.py
from unittest.mock import MagicMock, patch

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.runtime_config import RuntimeConfig


class TestAutoRuntimeCoreInit:
    def test_init_with_default_config(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        assert core._booted is False
        assert core.capability_registry is not None
        assert core.work_orchestrator is not None
        assert core.stop_gate is not None
        assert core.orphan_detector is not None
        assert core.onboarding_scanner is not None

    def test_init_creates_dirs(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        assert (tmp_path / "audit").exists()
        assert (tmp_path / "cards").exists()


class TestAutoRuntimeCoreBoot:
    def test_boot_success(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)

        mock_report = MagicMock()
        mock_report.success = True
        mock_report.errors = []
        mock_report.components_started = []
        mock_report.steps_completed = 0

        with patch.object(core._lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "_register_task_system_cron_jobs"):
                with patch.object(core, "_register_task_system_hooks"):
                    with patch.object(core, "_start_task_queue"):
                        with patch.object(core, "_start_blueprint_watcher"):
                            with patch.object(core, "_run_boot_triple_alignment"):
                                with patch.object(core, "_init_escalation_protocol"):
                                    report = core.boot()

        assert core._booted is True
        assert report.success is True


class TestAutoRuntimeCoreShutdown:
    def test_shutdown(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._booted = True

        mock_report = MagicMock()
        with patch.object(core._lifecycle, "shutdown_sequence", return_value=mock_report):
            report = core.shutdown()

        assert core._booted is False


class TestAutoRuntimeCoreProperties:
    def test_capability_registry_property(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        assert core.capability_registry is core._registry

    def test_integration_registry_property(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        assert core.integration_registry is core._integration_registry


class TestAutoRuntimeCoreCanStop:
    def test_can_stop_when_clear(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        with patch.object(core._audit_logger, "has_pending_flush", return_value=False):
            with patch.object(core._night_shift_queue, "has_unresolved", return_value=False):
                with patch.object(core._dream_cycle, "needs_archival", return_value=False):
                    assert core.can_stop() is True

    def test_cannot_stop_when_pending_flush(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        with patch.object(core._audit_logger, "has_pending_flush", return_value=True):
            with patch.object(core._night_shift_queue, "has_unresolved", return_value=False):
                with patch.object(core._dream_cycle, "needs_archival", return_value=False):
                    assert core.can_stop() is False


class TestAutoRuntimeCoreLearnFromTaskResult:
    def test_learn_no_task_learner(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._task_learner = None
        core.learn_from_task_result("classify", "qwen3", 100.0, 50, 0.9)


class TestAutoRuntimeCoreGetRecommendations:
    def test_get_recommendations_no_learner(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._task_learner = None
        assert core.get_task_model_recommendations() == []

    def test_learner_summary_no_learner(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            circadian_state_path=tmp_path / "circadian" / "state.json",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._task_learner = None
        assert "not initialized" in core.learner_summary()
