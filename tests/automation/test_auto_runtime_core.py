# [A_test] module_id: MOD-GOV_auto_runtime_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
from __future__ import annotations

# [A_test] module_id=MOD-GOV_auto_runtime_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

# 5.174-M5：auto_runtime_core 的组件依赖已提升为模块级 import（import 探针验证无循环），
# patch 目标同步指向 zephyr.trading.auto_runtime_core.<Name>——from-import 在模块加载时
# 绑定到 auto_runtime_core 命名空间，patch 源模块属性对已绑定名称无效。
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        assert core.booted is False
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)

        mock_report = MagicMock()
        mock_report.success = True
        mock_report.errors = []
        mock_report.components_started = []
        mock_report.steps_completed = 0

        with patch.object(core.lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "register_task_system_cron_jobs"):
                with patch.object(core, "register_task_system_hooks"):
                    with patch.object(core, "start_task_queue"):
                        with patch.object(core, "start_blueprint_watcher"):
                            with patch.object(core, "run_boot_triple_alignment"):
                                with patch.object(core, "init_escalation_protocol"):
                                    report = core.boot()

        assert core.booted is True
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.booted = True

        mock_report = MagicMock()
        with patch.object(core.lifecycle, "shutdown_sequence", return_value=mock_report):
            report = core.shutdown()

        assert core.booted is False


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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        assert core.capability_registry is core.registry

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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        assert core.integration_registry is core.integration_registry


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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        with patch.object(core.audit_logger, "has_pending_flush", return_value=False):
            with patch.object(core.night_shift_queue, "has_unresolved", return_value=False):
                with patch.object(core.dream_cycle, "needs_archival", return_value=False):
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        with patch.object(core.audit_logger, "has_pending_flush", return_value=True):
            with patch.object(core.night_shift_queue, "has_unresolved", return_value=False):
                with patch.object(core.dream_cycle, "needs_archival", return_value=False):
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.task_learner = None
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.task_learner = None
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.task_learner = None
        assert "not initialized" in core.learner_summary()


class TestStartLocalModelsRefactor:
    """5.158.11 回归测试——_start_local_models 行为等价验证。

    覆盖5个逻辑块: ollama检查/DeepSeek-OllamaChat降级/embedding warmup/scheduler/VMS。
    重构前编写，验证重构后行为不变（extract method）。
    """

    def make_core(self, tmp_path):
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.audit_logger = MagicMock()
        return core

    def test_ollama_alive_all_components_success(self, tmp_path):
        """ollama存活+DeepSeek可用+所有组件成功启动。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=True),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
            patch("zephyr.trading.auto_runtime_core.EmbeddingRouter") as MockER,
            patch("zephyr.trading.auto_runtime_core.LocalModelScheduler") as MockLS,
        ):
            MockDS.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core.start_local_models(report)
        assert "08_deepseek_chat_verify" in report.components_started
        assert "06_embedding_router_warmup" in report.components_started
        assert "12_local_scheduler_start" in report.components_started
        assert report.steps_completed == 3
        assert report.errors == []

    def test_ollama_not_alive_autostart_success(self, tmp_path):
        """ollama不存活+自动启动成功→继续启动其他组件。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=False),
            patch.object(core, "ensure_ollama_running", return_value=True),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
            patch("zephyr.trading.auto_runtime_core.EmbeddingRouter") as MockER,
            patch("zephyr.trading.auto_runtime_core.LocalModelScheduler") as MockLS,
        ):
            MockDS.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core.start_local_models(report)
        assert "ollama_auto_started" in report.components_started

    def test_ollama_not_alive_autostart_fail_returns_early(self, tmp_path):
        """ollama不存活+自动启动失败→return early，不启动其他组件。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=False),
            patch.object(core, "ensure_ollama_running", return_value=False),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
        ):
            core.start_local_models(report)
        assert any("ollama" in e for e in report.errors)
        assert "08_deepseek_chat_verify" not in report.components_started
        MockDS.assert_not_called()

    def test_deepseek_unavailable_ollama_chat_available(self, tmp_path):
        """DeepSeek不可用→降级到OllamaChat（可用）。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=True),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
            patch("zephyr.trading.auto_runtime_core.OllamaChat") as MockOC,
            patch("zephyr.trading.auto_runtime_core.EmbeddingRouter") as MockER,
            patch("zephyr.trading.auto_runtime_core.LocalModelScheduler") as MockLS,
            patch("time.sleep"),
        ):
            MockDS.return_value.available = False
            MockOC.return_value.available = True
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core.start_local_models(report)
        assert "08_ollama_chat_verify" in report.components_started
        assert "08_deepseek_chat_verify" not in report.components_started

    def test_deepseek_unavailable_ollama_chat_unavailable(self, tmp_path):
        """DeepSeek不可用+OllamaChat不可用→errors包含ollama_chat错误。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=True),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
            patch("zephyr.trading.auto_runtime_core.OllamaChat") as MockOC,
            patch("zephyr.trading.auto_runtime_core.EmbeddingRouter") as MockER,
            patch("zephyr.trading.auto_runtime_core.LocalModelScheduler") as MockLS,
        ):
            MockDS.return_value.available = False
            MockOC.return_value.available = False
            MockER.return_value.warmup = MagicMock()
            MockLS.return_value.start = MagicMock()
            core.start_local_models(report)
        assert any("ollama_chat" in e for e in report.errors)

    def test_embedding_warmup_failure_recorded(self, tmp_path):
        """embedding warmup失败→errors记录，继续后续组件。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with (
            patch.object(core, "ollama_alive", return_value=True),
            patch("zephyr.trading.auto_runtime_core.DeepSeekChat") as MockDS,
            patch("zephyr.trading.auto_runtime_core.EmbeddingRouter") as MockER,
            patch("zephyr.trading.auto_runtime_core.LocalModelScheduler") as MockLS,
        ):
            MockDS.return_value.available = True
            MockER.return_value.warmup.side_effect = RuntimeError("warmup failed")
            MockLS.return_value.start = MagicMock()
            core.start_local_models(report)
        assert any("embedding_router_warmup" in e for e in report.errors)
        assert "06_embedding_router_warmup" not in report.components_started

    def test_all_components_already_exist_direct_start(self, tmp_path):
        """所有组件已存在→直接调用start()，不创建新实例。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        existing_chat = MagicMock()
        existing_router = MagicMock()
        existing_scheduler = MagicMock()
        existing_vms = MagicMock()
        core.ollama_chat = existing_chat
        core.embedding_router = existing_router
        core.local_scheduler = existing_scheduler
        core.vms = existing_vms
        with patch.object(core, "ollama_alive", return_value=True):
            core.start_local_models(report)
        existing_scheduler.start.assert_called_once()
        existing_vms.start.assert_called_once()


class TestL0SupplyChainVerify:
    """#255③ 回归——_LocalModelBootstrap.l0_supply_chain_verify 挂接验证（2026-08-22）。

    契约：config/model_digests.yaml 缺失/空表=跳过不空转；verify_model 三态
    （verified/mismatch/missing）结果缓存 core._l0_verify_results+审计留痕；
    失败 fail-visible（report.errors）不 raise；dependency_scan 默认关。
    """

    def make_core(self, tmp_path):
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
        with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
            core = AutoRuntimeCore(config)
        core.audit_logger = MagicMock()
        return core

    def _write_cfg(self, root, body: str) -> None:
        cfg_dir = root / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        (cfg_dir / "model_digests.yaml").write_text(body, encoding="utf-8")

    def test_config_absent_skips(self, tmp_path):
        """配置文件不存在 → 跳过，结果缓存为空 dict，零 errors 零审计。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        with patch("zephyr.trading.auto_runtime_core.REPO_ROOT", tmp_path):
            from zephyr.trading.auto_runtime_core import _LocalModelBootstrap

            _LocalModelBootstrap.l0_supply_chain_verify(core, report)
        assert core._l0_verify_results == {}
        assert report.errors == []
        core._audit_logger.log_registration.assert_not_called()

    def test_empty_models_noop(self, tmp_path):
        """空 models 表 + dependency_scan 默认关 → 不构造 guard 不扫描。"""
        core = self.make_core(tmp_path)
        report = BootReport()
        self._write_cfg(tmp_path, "models: {}\ndependency_scan:\n  enabled: false\n")
        with (
            patch("zephyr.trading.auto_runtime_core.REPO_ROOT", tmp_path),
            patch(
                "zephyr.security.llm_defense.llm_security.layers.l0_supply_chain.SupplyChainGuard.scan_dependencies"
            ) as mock_scan,
        ):
            from zephyr.trading.auto_runtime_core import _LocalModelBootstrap

            _LocalModelBootstrap.l0_supply_chain_verify(core, report)
        assert core._l0_verify_results == {}
        assert report.errors == []
        mock_scan.assert_not_called()

    def test_model_verified_and_mismatch(self, tmp_path):
        """一真一假：verified 审计 OK；mismatch 进 report.errors + 状态缓存。"""
        import hashlib

        good = tmp_path / "models" / "good.bin"
        good.parent.mkdir(parents=True, exist_ok=True)
        good.write_bytes(b"weights")
        good_sha = hashlib.sha256(b"weights").hexdigest()
        bad = tmp_path / "models" / "bad.bin"
        bad.write_bytes(b"tampered")
        self._write_cfg(
            tmp_path,
            "models:\n"
            f'  "{good.as_posix()}": "{good_sha}"\n'
            f'  "{bad.as_posix()}": "{"0" * 64}"\n',
        )
        core = self.make_core(tmp_path)
        report = BootReport()
        with patch("zephyr.trading.auto_runtime_core.REPO_ROOT", tmp_path):
            from zephyr.trading.auto_runtime_core import _LocalModelBootstrap

            _LocalModelBootstrap.l0_supply_chain_verify(core, report)
        results = core._l0_verify_results
        assert results[good.as_posix()] == "verified"
        assert results[bad.as_posix()] == "mismatch"
        assert any("mismatch" in e for e in report.errors)
        statuses = [c.args[1] for c in core._audit_logger.log_registration.call_args_list]
        assert "L0_VERIFY_OK" in statuses
        assert "L0_VERIFY_MISMATCH" in statuses

    def test_dependency_scan_enabled_flags_unsafe(self, tmp_path):
        """dependency_scan 翻开 → 扫描执行+unsafe 摘要入 errors+结果缓存。"""
        from types import SimpleNamespace

        self._write_cfg(tmp_path, "models: {}\ndependency_scan:\n  enabled: true\n")
        core = self.make_core(tmp_path)
        report = BootReport()
        fake_deps = [
            SimpleNamespace(name="safe-pkg", version="1.0", is_safe=True, vulns=[]),
            SimpleNamespace(name="evil-pkg", version="0.1", is_safe=False, vulns=[{"id": "CVE-X"}]),
        ]
        with (
            patch("zephyr.trading.auto_runtime_core.REPO_ROOT", tmp_path),
            patch(
                "zephyr.security.llm_defense.llm_security.layers.l0_supply_chain.SupplyChainGuard.scan_dependencies",
                return_value=fake_deps,
            ),
        ):
            from zephyr.trading.auto_runtime_core import _LocalModelBootstrap

            _LocalModelBootstrap.l0_supply_chain_verify(core, report)
        cached = core._l0_verify_results["dependency_scan"]
        assert cached["scanned"] == 2
        assert cached["unsafe"] == ["evil-pkg"]
        assert any("evil-pkg" in e for e in report.errors)
