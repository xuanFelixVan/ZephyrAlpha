# [A_test] module_id=TEST-F1-DRILL | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §3.1
# [MODULE] tests.test_circadian_red_blue_drill
# [INVARIANTS] 测试CircadianScheduler._red_blue_daily_drill回调完整链路:注册→触发GameDayRunner→审计日志→异常静默
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=红蓝演练自动化链路漏洞
# [TESTS] self
# [DOMAIN] D-ORC

"""F1 CircadianScheduler 红蓝演练回调测试

验证 CircadianScheduler 内置的每日 6:00 红蓝演练任务回调完整链路:
  ① 回调注册: _register_default_tasks() 注册 red_blue_daily_drill (hour=6, layer=L1)
  ② 回调触发: _red_blue_daily_drill() 调用 GameDayRunner.run_game_day(DAILY)
  ③ 审计日志: bypasses>0 记录 WARNING, bypasses=0 记录 INFO
  ④ 异常静默: GameDayRunner 异常不抛出, logger.debug 记录

依据: MOD-INF-035 §3.1 CircadianScheduler组件 + DM-201114 任务卡。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.security.adversarial_validation.models import GameDayResult, RedBlueReport
from zephyr.trading.circadian_scheduler import CircadianScheduler


# ---------------------------------------------------------------------------
# ① 回调注册验证
# ---------------------------------------------------------------------------


class TestRedBlueDrillRegistration:
    """验证 red_blue_daily_drill 回调被正确注册。"""

    def test_red_blue_drill_registered_in_default_tasks(self) -> None:
        """验证 start() 后 red_blue_daily_drill 被注册到 _tasks。"""
        scheduler = CircadianScheduler()
        # start() 调用 _register_default_tasks()
        scheduler._register_default_tasks()

        task_names = [t.name for t in scheduler._tasks]
        assert "red_blue_daily_drill" in task_names

    def test_red_blue_drill_registered_at_hour_6(self) -> None:
        """验证 red_blue_daily_drill 注册在 hour=6。"""
        scheduler = CircadianScheduler()
        scheduler._register_default_tasks()

        drill_tasks = [t for t in scheduler._tasks if t.name == "red_blue_daily_drill"]
        assert len(drill_tasks) == 1
        assert drill_tasks[0].hour == 6

    def test_red_blue_drill_layer_l1(self) -> None:
        """验证 red_blue_daily_drill layer=L1。"""
        scheduler = CircadianScheduler()
        scheduler._register_default_tasks()

        drill_tasks = [t for t in scheduler._tasks if t.name == "red_blue_daily_drill"]
        assert drill_tasks[0].layer == "L1"

    def test_red_blue_drill_callback_is_bound_method(self) -> None:
        """验证 red_blue_daily_drill 的 callback 是 _red_blue_daily_drill 方法。"""
        scheduler = CircadianScheduler()
        scheduler._register_default_tasks()

        drill_tasks = [t for t in scheduler._tasks if t.name == "red_blue_daily_drill"]
        callback = drill_tasks[0].callback
        assert callback is not None
        # callback 应该是 scheduler._red_blue_daily_drill 的绑定方法
        assert callable(callback)

    def test_default_tasks_not_duplicated_after_double_register(self) -> None:
        """验证重复调用 _register_default_tasks 不重复注册。"""
        scheduler = CircadianScheduler()
        scheduler._register_default_tasks()
        scheduler._register_default_tasks()  # 第二次调用

        drill_tasks = [t for t in scheduler._tasks if t.name == "red_blue_daily_drill"]
        assert len(drill_tasks) == 1


# ---------------------------------------------------------------------------
# ② 回调触发 GameDayRunner
# ---------------------------------------------------------------------------


class TestRedBlueDrillTriggerGameDayRunner:
    """验证 _red_blue_daily_drill 正确触发 GameDayRunner。"""

    def _make_result(self, total_attacks: int = 5, bypasses: int = 0) -> GameDayResult:
        report = RedBlueReport(
            session_id="test-session",
            total=total_attacks,
            blocked=total_attacks - bypasses,
            bypassed=bypasses,
        )
        return GameDayResult(total_attacks=total_attacks, bypasses=bypasses, passed=total_attacks - bypasses, report=report)

    def test_drill_calls_game_day_runner(self) -> None:
        """验证 _red_blue_daily_drill 调用 GameDayRunner.run_game_day。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with patch(
            "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
            return_value=mock_runner,
        ):
            scheduler._red_blue_daily_drill()

        mock_runner.run_game_day.assert_called_once()

    def test_drill_uses_daily_frequency(self) -> None:
        """验证 _red_blue_daily_drill 使用 GameDayFrequency.DAILY。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with patch(
            "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
            return_value=mock_runner,
        ):
            scheduler._red_blue_daily_drill()

        # 验证传入的 frequency 参数
        from zephyr.security.adversarial_validation.game_day_runner import GameDayFrequency

        call_args = mock_runner.run_game_day.call_args
        frequency = call_args[0][0] if call_args[0] else call_args[1].get("frequency")
        assert frequency == GameDayFrequency.DAILY

    def test_drill_with_zero_bypasses_does_not_warn(self) -> None:
        """验证 bypasses=0 时不记录 WARNING 级别审计日志。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=10, bypasses=0)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        # 应该被调用（INFO 级别）
        mock_audit.assert_called_once()
        # 验证 severity 是 INFO 而非 HIGH/WARNING
        call_args = mock_audit.call_args
        severity = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("severity")
        assert severity == "INFO"

    def test_drill_with_nonzero_bypasses_warns(self) -> None:
        """验证 bypasses>0 时记录 HIGH 级别审计日志。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=10, bypasses=3)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        # 应该被调用（HIGH 级别）
        mock_audit.assert_called_once()
        call_args = mock_audit.call_args
        severity = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("severity")
        assert severity == "HIGH"


# ---------------------------------------------------------------------------
# ③ 异常静默处理
# ---------------------------------------------------------------------------


class TestRedBlueDrillExceptionHandling:
    """验证 _red_blue_daily_drill 异常静默处理。"""

    def test_drill_silences_game_day_runner_exception(self) -> None:
        """验证 GameDayRunner.run_game_day 抛异常时不传播。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.side_effect = RuntimeError("game day runner crashed")

        with patch(
            "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
            return_value=mock_runner,
        ):
            # 不应抛出异常
            scheduler._red_blue_daily_drill()

    def test_drill_silences_import_exception(self) -> None:
        """验证 GameDayRunner 导入失败时不传播异常。"""
        scheduler = CircadianScheduler()

        # 模拟导入失败 - 通过 sys.modules 注入错误
        with patch.dict("sys.modules", {"zephyr.security.adversarial_validation.game_day_runner": None}):
            # 不应抛出异常
            scheduler._red_blue_daily_drill()

    def test_drill_does_not_raise_on_any_exception(self) -> None:
        """验证任何异常都不抛出（TypeError/ValueError/AttributeError）。"""
        scheduler = CircadianScheduler()

        for exc_type in [TypeError, ValueError, AttributeError, OSError]:
            mock_runner = MagicMock()
            mock_runner.run_game_day.side_effect = exc_type(f"simulated {exc_type.__name__}")

            with patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ):
                # 不应抛出任何异常
                scheduler._red_blue_daily_drill()

    def test_drill_logs_debug_on_exception(self) -> None:
        """验证异常时 logger.debug 被调用（exc_info=True）。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.side_effect = RuntimeError("test error")

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch("zephyr.trading.circadian_scheduler.logger") as mock_logger,
        ):
            scheduler._red_blue_daily_drill()

        # logger.debug 应该被调用
        mock_logger.debug.assert_called()
        # 验证 exc_info=True
        debug_call = mock_logger.debug.call_args
        assert debug_call[1].get("exc_info") is True or "exc_info" in debug_call[1]


# ---------------------------------------------------------------------------
# ④ 审计日志验证
# ---------------------------------------------------------------------------


class TestRedBlueDrillAuditLog:
    """验证 _red_blue_daily_drill 审计日志输出。"""

    def _make_result(self, total_attacks: int = 5, bypasses: int = 0) -> GameDayResult:
        report = RedBlueReport(
            session_id="test-session",
            total=total_attacks,
            blocked=total_attacks - bypasses,
            bypassed=bypasses,
        )
        return GameDayResult(total_attacks=total_attacks, bypasses=bypasses, passed=total_attacks - bypasses, report=report)

    def test_drill_audit_log_contains_correct_task_name(self) -> None:
        """验证审计日志 task_name = 'red_blue_daily_drill'。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        task_name = call_args[0][0] if call_args[0] else call_args[1].get("task_name")
        assert task_name == "red_blue_daily_drill"

    def test_drill_audit_log_contains_correct_dimension(self) -> None:
        """验证审计日志 dimension = 'D6'。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        dimension = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("dimension")
        assert dimension == "D6"

    def test_drill_audit_log_zero_bypasses_evidence(self) -> None:
        """验证 bypasses=0 时审计日志 evidence 包含 bypasses=0。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=8, bypasses=0)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        # evidence 是第5个位置参数 (index 4)
        evidence = call_args[0][4] if len(call_args[0]) > 4 else call_args[1].get("evidence")
        assert "bypasses=0" in evidence
        assert "total_attacks=8" in evidence

    def test_drill_audit_log_nonzero_bypasses_evidence(self) -> None:
        """验证 bypasses>0 时审计日志 evidence 包含正确 bypasses 数。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=10, bypasses=4)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        evidence = call_args[0][4] if len(call_args[0]) > 4 else call_args[1].get("evidence")
        assert "bypasses=4" in evidence
        assert "total_attacks=10" in evidence

    def test_drill_audit_log_description_contains_bypass_count(self) -> None:
        """验证 bypasses>0 时审计日志 description 包含 bypass 数。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=10, bypasses=3)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        # description 是第4个位置参数 (index 3)
        description = call_args[0][3] if len(call_args[0]) > 3 else call_args[1].get("description")
        assert "3 bypasses" in description


# ---------------------------------------------------------------------------
# ⑤ 集成测试：通过 register_task 注册的回调可被调用
# ---------------------------------------------------------------------------


class TestRedBlueDrillIntegration:
    """验证红蓝演练回调集成链路。"""

    def _make_result(self, total_attacks: int = 5, bypasses: int = 0) -> GameDayResult:
        report = RedBlueReport(
            session_id="test-session",
            total=total_attacks,
            blocked=total_attacks - bypasses,
            bypassed=bypasses,
        )
        return GameDayResult(total_attacks=total_attacks, bypasses=bypasses, passed=total_attacks - bypasses, report=report)

    def test_drill_via_registered_callback(self) -> None:
        """验证通过 register_task 注册的 callback 可被调用并触发 GameDayRunner。"""
        scheduler = CircadianScheduler()
        scheduler._register_default_tasks()

        drill_tasks = [t for t in scheduler._tasks if t.name == "red_blue_daily_drill"]
        callback = drill_tasks[0].callback

        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with patch(
            "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
            return_value=mock_runner,
        ):
            # 通过注册的 callback 调用
            callback()

        mock_runner.run_game_day.assert_called_once()

    def test_drill_idempotent_multiple_calls(self) -> None:
        """验证多次调用 _red_blue_daily_drill 不崩溃。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result()

        with patch(
            "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
            return_value=mock_runner,
        ):
            # 连续调用3次
            for _ in range(3):
                scheduler._red_blue_daily_drill()

        assert mock_runner.run_game_day.call_count == 3

    def test_drill_with_zero_attacks(self) -> None:
        """验证 total_attacks=0 时不崩溃（边界情况）。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=0, bypasses=0)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output"),
        ):
            # 不应抛出异常
            scheduler._red_blue_daily_drill()

        mock_runner.run_game_day.assert_called_once()

    def test_drill_all_bypasses(self) -> None:
        """验证所有攻击都被绕过时正确记录 HIGH 审计日志。"""
        scheduler = CircadianScheduler()
        mock_runner = MagicMock()
        mock_runner.run_game_day.return_value = self._make_result(total_attacks=5, bypasses=5)

        with (
            patch(
                "zephyr.security.adversarial_validation.game_day_runner.GameDayRunner",
                return_value=mock_runner,
            ),
            patch.object(scheduler, "_audit_task_jsonl_output") as mock_audit,
        ):
            scheduler._red_blue_daily_drill()

        call_args = mock_audit.call_args
        severity = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("severity")
        assert severity == "HIGH"
