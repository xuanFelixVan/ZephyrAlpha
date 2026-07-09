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
# [TTL] task_bound
from unittest.mock import MagicMock, patch

# 确保 patch 目标模块已加载（_start_local_models 内延迟 import，patch 需要模块在 sys.modules 中）
# VMS 模块不在此导入——collection_manager.py 引用的 VMS_PERSIST_DIR 在 paths.py 未定义，
# 导入会触发 ImportError；_start_local_models 的 try/except 会捕获并跳过 VMS 启动。
import zephyr.integration.local_model.deepseek_chat  # noqa: E402,F401
import zephyr.integration.local_model.embedding_router  # noqa: E402,F401
import zephyr.integration.local_model.local_model_scheduler  # noqa: E402,F401
import zephyr.integration.local_model.ollama_chat  # noqa: E402,F401

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.lifecycle_manager import BootReport
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
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._task_learner = None
        assert "not initialized" in core.learner_summary()


class TestStartLocalModelsRefactor:
    """5.158.11 回归测试——_start_local_models 行为等价验证。

    覆盖5个逻辑块: ollama检查/DeepSeek-OllamaChat降级/embedding warmup/scheduler/VMS。
    重构前编写，验证重构后行为不变（extract method）。
    """

    def _make_core(self, tmp_path):
        config = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            night_shift_storage_path=tmp_path / "night.jsonl",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            auto_start_l2=False,
        )
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
            core = AutoRuntimeCore(config)
        core._audit_logger = MagicMock()
        return core

    def test_ollama_alive_all_components_success(self, tmp_path):
        """ollama存活+DeepSeek可用+所有组件成功启动。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=True), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS, \
             patch("zephyr.integration.local_model.embedding_router.EmbeddingRouter") as MockER, \
             patch("zephyr.integration.local_model.local_model_scheduler.LocalModelScheduler") as MockLS:
            MockDS.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core._start_local_models(report)
        assert "08_deepseek_chat_verify" in report.components_started
        assert "06_embedding_router_warmup" in report.components_started
        assert "12_local_scheduler_start" in report.components_started
        assert report.steps_completed == 3
        assert report.errors == []

    def test_ollama_not_alive_autostart_success(self, tmp_path):
        """ollama不存活+自动启动成功→继续启动其他组件。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=False), \
             patch.object(core, "_ensure_ollama_running", return_value=True), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS, \
             patch("zephyr.integration.local_model.embedding_router.EmbeddingRouter") as MockER, \
             patch("zephyr.integration.local_model.local_model_scheduler.LocalModelScheduler") as MockLS:
            MockDS.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core._start_local_models(report)
        assert "ollama_auto_started" in report.components_started

    def test_ollama_not_alive_autostart_fail_returns_early(self, tmp_path):
        """ollama不存活+自动启动失败→return early，不启动其他组件。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=False), \
             patch.object(core, "_ensure_ollama_running", return_value=False), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS:
            core._start_local_models(report)
        assert any("ollama" in e for e in report.errors)
        assert "08_deepseek_chat_verify" not in report.components_started
        MockDS.assert_not_called()

    def test_deepseek_unavailable_ollama_chat_available(self, tmp_path):
        """DeepSeek不可用→降级到OllamaChat（可用）。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=True), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS, \
             patch("zephyr.integration.local_model.ollama_chat.OllamaChat") as MockOC, \
             patch("zephyr.integration.local_model.embedding_router.EmbeddingRouter") as MockER, \
             patch("zephyr.integration.local_model.local_model_scheduler.LocalModelScheduler") as MockLS, \
             patch("time.sleep"):
            MockDS.return_value.available = False
            MockOC.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core._start_local_models(report)
        assert "08_ollama_chat_verify" in report.components_started
        assert "08_deepseek_chat_verify" not in report.components_started

    def test_deepseek_unavailable_ollama_chat_unavailable(self, tmp_path):
        """DeepSeek不可用+OllamaChat不可用→errors包含ollama_chat错误。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=True), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS, \
             patch("zephyr.integration.local_model.ollama_chat.OllamaChat") as MockOC, \
             patch("zephyr.integration.local_model.embedding_router.EmbeddingRouter") as MockER, \
             patch("zephyr.integration.local_model.local_model_scheduler.LocalModelScheduler") as MockLS:
            MockDS.return_value.available = False
            MockOC.return_value.available = False
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core._start_local_models(report)
        assert any("ollama_chat" in e for e in report.errors)

    def test_embedding_warmup_failure_recorded(self, tmp_path):
        """embedding warmup失败→errors记录，继续后续组件。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        with patch.object(core, "_ollama_alive", return_value=True), \
             patch("zephyr.integration.local_model.deepseek_chat.DeepSeekChat") as MockDS, \
             patch("zephyr.integration.local_model.embedding_router.EmbeddingRouter") as MockER, \
             patch("zephyr.integration.local_model.local_model_scheduler.LocalModelScheduler") as MockLS:
            MockDS.return_value.available = True
            MockER.return_value.warmup.side_effect = RuntimeError("warmup failed")
            MockLS.return_value.start = MagicMock()
            core._start_local_models(report)
        assert any("embedding_router_warmup" in e for e in report.errors)
        assert "06_embedding_router_warmup" not in report.components_started

    def test_all_components_already_exist_direct_start(self, tmp_path):
        """所有组件已存在→直接调用start()，不创建新实例。"""
        core = self._make_core(tmp_path)
        report = BootReport()
        existing_chat = MagicMock()
        existing_router = MagicMock()
        existing_scheduler = MagicMock()
        existing_vms = MagicMock()
        core._ollama_chat = existing_chat
        core._embedding_router = existing_router
        core._local_scheduler = existing_scheduler
        core._vms = existing_vms
        with patch.object(core, "_ollama_alive", return_value=True):
            core._start_local_models(report)
        existing_scheduler.start.assert_called_once()
        existing_vms.start.assert_called_once()
