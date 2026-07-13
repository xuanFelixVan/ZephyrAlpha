# [A_test] module_id=T-GEN_test_auto_runtime_fle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] tests.test_auto_runtime_fle_integration
# [INVARIANTS] 测试隔离外部依赖(VMS/ollama/lifecycle); 验证FLE自动启动链路
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError→skip
# [TESTS] self
# [TTL] task_bound

"""AutoRuntimeCore → FeedbackLoopScheduler 自动启动链路集成测试

验证 DM-202410 施工步骤 ②-⑥:
  ② boot() 调用 _start_fle_scheduler
  ③ _start_fle_scheduler 创建 FeedbackLoopScheduler 并 start()
  ④ shutdown() 停止 FLE
  ⑤ boot 失败时 FLE 不启动
  ⑥ mock InProcessVectorMemory 和 ollama

测试不启动真实后台线程——mock FeedbackLoopScheduler 的 start/stop。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.runtime_config import RuntimeConfig


@pytest.fixture
def config(tmp_path):
    """隔离的 RuntimeConfig——auto_start_l2=False 避免 ollama 依赖。"""
    return RuntimeConfig(
        audit_log_dir=tmp_path / "audit",
        capability_card_dir=tmp_path / "cards",
        night_shift_storage_path=tmp_path / "night.jsonl",
        work_dag_dir=tmp_path / "dags",
        dream_archive_dir=tmp_path / "dream",
        feedback_proposal_dir=tmp_path / "feedback",
        health_snapshot_dir=tmp_path / "health",
        auto_start_l2=False,
    )


@pytest.fixture
def core(config):
    """创建 AutoRuntimeCore 实例（mock _init_a2a + StatusDashboard 避免外部依赖）。"""
    with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore._init_a2a"):
        with patch("zephyr.trading.auto_runtime_core.StatusDashboard"):
            c = AutoRuntimeCore(config)
    return c


def _make_mock_report(success: bool = True):
    """创建 mock BootReport。"""
    report = MagicMock()
    report.success = success
    report.errors = []
    report.components_started = []
    report.steps_completed = 0
    return report


class TestBootCallsStartFleScheduler:
    """② boot() 调用 _start_fle_scheduler"""

    def test_boot_success_calls_start_fle_scheduler(self, core):
        """boot 成功时调用 _start_fle_scheduler。"""
        mock_report = _make_mock_report(success=True)
        with patch.object(core._lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "_register_task_system_cron_jobs"):
                with patch.object(core, "_register_task_system_hooks"):
                    with patch.object(core, "_start_task_queue"):
                        with patch.object(core, "_start_blueprint_watcher"):
                            with patch.object(core, "_start_fle_scheduler") as mock_fle:
                                with patch.object(core, "_run_boot_triple_alignment"):
                                    with patch.object(core, "_init_escalation_protocol"):
                                        core.boot()

        mock_fle.assert_called_once()

    def test_boot_failure_skips_start_fle_scheduler(self, core):
        """⑤ boot 失败时不调用 _start_fle_scheduler。"""
        mock_report = _make_mock_report(success=False)
        with patch.object(core._lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "_start_fle_scheduler") as mock_fle:
                report = core.boot()

        mock_fle.assert_not_called()
        assert report.success is False
        assert core._booted is False


class TestStartFleSchedulerCreatesAndStarts:
    """③ _start_fle_scheduler 创建 FeedbackLoopScheduler 并 start()"""

    def test_start_fle_scheduler_creates_scheduler(self, core):
        """_start_fle_scheduler 创建 FeedbackLoopScheduler 实例。"""
        with patch("zephyr.feedback_loop.scheduler.FeedbackLoopScheduler") as mock_fle_cls:
            mock_instance = MagicMock()
            mock_fle_cls.return_value = mock_instance

            core._start_fle_scheduler()

            mock_fle_cls.assert_called_once_with(poll_interval=30.0)
            assert core._fle_scheduler is mock_instance

    def test_start_fle_scheduler_does_not_call_start(self, core):
        """trae_053 v2.0.0: _start_fle_scheduler 不再调用 scheduler.start()（daemon 线程已废除）。"""
        with patch("zephyr.feedback_loop.scheduler.FeedbackLoopScheduler") as mock_fle_cls:
            mock_instance = MagicMock()
            mock_fle_cls.return_value = mock_instance

            core._start_fle_scheduler()

            mock_instance.start.assert_not_called()

    def test_start_fle_scheduler_exception_does_not_crash(self, core):
        """_start_fle_scheduler 异常不崩溃 boot（try/except 保护）。"""
        with patch("zephyr.feedback_loop.scheduler.FeedbackLoopScheduler") as mock_fle_cls:
            mock_fle_cls.side_effect = RuntimeError("VMS init failed")

            core._start_fle_scheduler()

            assert core._fle_scheduler is None

    def test_start_fle_scheduler_with_mocked_vms(self, core):
        """⑥ mock InProcessVectorMemory → FeedbackLoopScheduler 正常创建。

        FeedbackLoopScheduler.__post_init__ 会尝试初始化 VectorBridge,
        需要 InProcessVectorMemory。mock 后验证链路完整。
        """
        with patch(
            "zephyr.integration.vector_memory.in_process_vector_memory.InProcessVectorMemory"
        ) as mock_vms_cls:
            mock_vms_cls.return_value = MagicMock()

            from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

            FeedbackLoopScheduler.reset_instance()
            scheduler = FeedbackLoopScheduler(poll_interval=0.1)

            assert scheduler._running is False

            scheduler.start()
            assert scheduler._running is True

            scheduler.stop()
            assert scheduler._running is False

            FeedbackLoopScheduler.reset_instance()


class TestShutdownStopsFle:
    """④ shutdown() 停止 FLE"""

    def test_shutdown_stops_fle_scheduler(self, core):
        """shutdown() 调用 _fle_scheduler.stop()。"""
        mock_fle = MagicMock()
        core._fle_scheduler = mock_fle
        core._booted = True

        with patch.object(core._lifecycle, "shutdown_sequence", return_value=MagicMock()):
            core.shutdown()

        mock_fle.stop.assert_called_once()
        assert core._booted is False

    def test_shutdown_without_fle_scheduler(self, core):
        """shutdown() 时 _fle_scheduler=None → 不崩溃。"""
        core._fle_scheduler = None
        core._booted = True

        with patch.object(core._lifecycle, "shutdown_sequence", return_value=MagicMock()):
            core.shutdown()

        assert core._booted is False

    def test_shutdown_fle_exception_does_not_crash(self, core):
        """_fle_scheduler.stop() 异常 → shutdown 不崩溃。"""
        mock_fle = MagicMock()
        mock_fle.stop.side_effect = RuntimeError("stop failed")
        core._fle_scheduler = mock_fle
        core._booted = True

        with patch.object(core._lifecycle, "shutdown_sequence", return_value=MagicMock()):
            core.shutdown()

        assert core._booted is False

    def test_shutdown_stops_local_scheduler_and_vms(self, core):
        """shutdown() 同时停止 _local_scheduler 和 _vms。"""
        mock_local = MagicMock()
        mock_vms = MagicMock()
        core._local_scheduler = mock_local
        core._vms = mock_vms
        core._fle_scheduler = MagicMock()
        core._booted = True

        with patch.object(core._lifecycle, "shutdown_sequence", return_value=MagicMock()):
            core.shutdown()

        mock_local.stop.assert_called_once()
        mock_vms.shutdown.assert_called_once()


class TestBootFleFullChain:
    """boot → _start_fle_scheduler → FeedbackLoopScheduler 实例化（trae_053 v2.0.0 无 start）全链路"""

    def test_boot_to_fle_start_full_chain(self, core):
        """boot() 成功 → _start_fle_scheduler → FeedbackLoopScheduler 实例化（不调用 start）。

        mock lifecycle + 其他 boot 步骤，但保留 _start_fle_scheduler 真实调用，
        mock FeedbackLoopScheduler 类验证 start() 不被调用（daemon 线程已废除）。
        """
        mock_report = _make_mock_report(success=True)
        with patch.object(core._lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "_register_task_system_cron_jobs"):
                with patch.object(core, "_register_task_system_hooks"):
                    with patch.object(core, "_start_task_queue"):
                        with patch.object(core, "_start_blueprint_watcher"):
                            with patch.object(core, "_run_boot_triple_alignment"):
                                with patch.object(core, "_init_escalation_protocol"):
                                    with patch(
                                        "zephyr.feedback_loop.scheduler.FeedbackLoopScheduler"
                                    ) as mock_fle_cls:
                                        mock_instance = MagicMock()
                                        mock_fle_cls.return_value = mock_instance

                                        report = core.boot()

        assert report.success is True
        assert core._booted is True
        mock_fle_cls.assert_called_once_with(poll_interval=30.0)
        mock_instance.start.assert_not_called()
        assert core._fle_scheduler is mock_instance

    def test_boot_then_shutdown_fle_lifecycle(self, core):
        """boot() 启动 FLE → shutdown() 停止 FLE 完整生命周期。"""
        mock_fle = MagicMock()
        mock_report = _make_mock_report(success=True)

        with patch.object(core._lifecycle, "boot_sequence", return_value=mock_report):
            with patch.object(core, "_register_task_system_cron_jobs"):
                with patch.object(core, "_register_task_system_hooks"):
                    with patch.object(core, "_start_task_queue"):
                        with patch.object(core, "_start_blueprint_watcher"):
                            with patch.object(core, "_run_boot_triple_alignment"):
                                with patch.object(core, "_init_escalation_protocol"):
                                    with patch.object(
                                        core, "_start_fle_scheduler"
                                    ) as mock_start:
                                        mock_start.side_effect = lambda: setattr(
                                            core, "_fle_scheduler", mock_fle
                                        )
                                        core.boot()

        assert core._booted is True
        assert core._fle_scheduler is mock_fle

        with patch.object(core._lifecycle, "shutdown_sequence", return_value=MagicMock()):
            core.shutdown()

        mock_fle.stop.assert_called_once()
        assert core._booted is False
        assert core._fle_scheduler is mock_fle
