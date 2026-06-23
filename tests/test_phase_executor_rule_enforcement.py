# [A_test] module_id: SRC-TST-phase_executor_re | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §phase-executor
# [MODULE] tests.test_phase_executor_rule_enforcement
# [INVARIANTS] PhaseExecutor bridges PhaseManager and GateEngine; RED stops execution; context propagates
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_phase_executor_rule_enforcement.py

"""PhaseExecutor 单元测试 — 验证阶段执行器桥接 PhaseManager 和 GateEngine."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.rule_enforcement.phase_executor import (
    CheckResult,
    ExecutionContext,
    GateResultType,
    PhaseExecutionResult,
    PhaseExecutor,
)
from zephyr.governance.phase_manager import ConstructionPhase


@pytest.fixture
def executor() -> PhaseExecutor:
    return PhaseExecutor()


class TestPhaseExecutorInstantiation:
    def test_can_instantiate(self, executor: PhaseExecutor) -> None:
        assert executor is not None

    def test_gate_engine_lazy_init(self, executor: PhaseExecutor) -> None:
        assert executor._gate_engine is None

    def test_gate_engine_property_creates_instance(self) -> None:
        mock_ge = MagicMock()
        ex = PhaseExecutor(gate_engine=mock_ge)
        assert ex.gate_engine is mock_ge


class TestExecutePhase:
    def test_unknown_phase_raises_value_error(self, executor: PhaseExecutor) -> None:
        with pytest.raises(ValueError, match="未知阶段"):
            executor.execute_phase("UNKNOWN_PHASE")

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_execute_phase_returns_result(self, mock_run: MagicMock, executor: PhaseExecutor) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.GREEN
        result = executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON)

        assert isinstance(result, PhaseExecutionResult)
        assert result.phase == "PHASE_0_SKELETON"
        assert result.checks_run > 0
        assert result.overall == GateResultType.GREEN
        assert result.passed is True

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_red_stops_execution(self, mock_run: MagicMock, executor: PhaseExecutor) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.RED
        result = executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON)

        assert result.overall == GateResultType.RED
        assert result.passed is False
        assert result.red_count >= 1
        # RED should stop after first check
        assert result.checks_run == 1

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_yellow_continues_execution(self, mock_run: MagicMock, executor: PhaseExecutor) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.YELLOW
        result = executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON)

        assert result.overall == GateResultType.YELLOW
        assert result.passed is True
        assert result.yellow_count > 0
        # YELLOW should NOT stop execution
        assert result.checks_run > 1

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_check_exception_returns_yellow(self, mock_run: MagicMock, executor: PhaseExecutor) -> None:
        mock_run.side_effect = RuntimeError("test error")
        result = executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON)

        assert result.overall == GateResultType.YELLOW
        assert all(r.message.startswith("检查异常") for r in result.results)


class TestExecutionContext:
    def test_add_result(self) -> None:
        ctx = ExecutionContext(phase="test")
        cr = CheckResult(check_name="test", result=GateResultType.GREEN)
        ctx.add_result(cr)
        assert len(ctx.results) == 1

    def test_has_red(self) -> None:
        ctx = ExecutionContext(phase="test")
        ctx.add_result(CheckResult(check_name="r", result=GateResultType.RED))
        assert ctx.has_red() is True

    def test_has_yellow(self) -> None:
        ctx = ExecutionContext(phase="test")
        ctx.add_result(CheckResult(check_name="y", result=GateResultType.YELLOW))
        assert ctx.has_yellow() is True

    def test_get_result(self) -> None:
        ctx = ExecutionContext(phase="test")
        cr = CheckResult(check_name="find_me", result=GateResultType.GREEN)
        ctx.add_result(cr)
        assert ctx.get_result("find_me") is cr
        assert ctx.get_result("nonexistent") is None

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_context_propagates_results(self, mock_run: MagicMock, executor: PhaseExecutor) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.GREEN
        ctx = ExecutionContext(phase="test")
        executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON, context=ctx)

        assert len(ctx.results) > 0
        assert all(isinstance(r, CheckResult) for r in ctx.results)


class TestExecuteGate:
    def test_execute_gate_delegates_to_gate_engine(self) -> None:
        mock_ge = MagicMock()
        mock_result = MagicMock()
        mock_ge.evaluate.return_value = mock_result

        ex = PhaseExecutor(gate_engine=mock_ge)
        mock_task = MagicMock()
        result = ex.execute_gate(mock_task, "G1")

        mock_ge.evaluate.assert_called_once_with(mock_task, "G1", conn=None)
        assert result is mock_result

    def test_execute_gate_with_conn(self) -> None:
        mock_ge = MagicMock()
        mock_conn = MagicMock()
        mock_task = MagicMock()

        ex = PhaseExecutor(gate_engine=mock_ge)
        ex.execute_gate(mock_task, "G7", conn=mock_conn)

        mock_ge.evaluate.assert_called_once_with(mock_task, "G7", conn=mock_conn)


class TestExecutePhaseWithGates:
    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_gates_executed_when_phase_passes(self, mock_run: MagicMock) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.GREEN
        mock_ge = MagicMock()
        mock_ge.evaluate.return_value = MagicMock(passed=True)

        ex = PhaseExecutor(gate_engine=mock_ge)
        mock_task = MagicMock()
        phase_result, gate_results = ex.execute_phase_with_gates(
            ConstructionPhase.PHASE_0_SKELETON, mock_task, ["G1", "G7"]
        )

        assert phase_result.passed is True
        assert len(gate_results) == 2
        assert mock_ge.evaluate.call_count == 2

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_gates_skipped_when_phase_fails(self, mock_run: MagicMock) -> None:
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.RED
        mock_ge = MagicMock()

        ex = PhaseExecutor(gate_engine=mock_ge)
        mock_task = MagicMock()
        phase_result, gate_results = ex.execute_phase_with_gates(
            ConstructionPhase.PHASE_0_SKELETON, mock_task, ["G1", "G7"]
        )

        assert phase_result.passed is False
        assert len(gate_results) == 0
        mock_ge.evaluate.assert_not_called()


class TestGetPhaseSummary:
    def test_summary_returns_correct_info(self, executor: PhaseExecutor) -> None:
        summary = executor.get_phase_summary(ConstructionPhase.PHASE_0_SKELETON)

        assert summary["phase"] == "PHASE_0_SKELETON"
        assert "name" in summary
        assert "description" in summary
        assert summary["check_count"] > 0
        assert isinstance(summary["dependencies"], list)

    def test_summary_unknown_phase_raises(self, executor: PhaseExecutor) -> None:
        with pytest.raises(ValueError, match="未知阶段"):
            executor.get_phase_summary("UNKNOWN")


class TestPhaseExecutionResult:
    def test_passed_property(self) -> None:
        ctx = ExecutionContext()
        r = PhaseExecutionResult(
            phase="test", checks_run=1, results=[], overall=GateResultType.GREEN, context=ctx
        )
        assert r.passed is True

        r2 = PhaseExecutionResult(
            phase="test", checks_run=1, results=[], overall=GateResultType.RED, context=ctx
        )
        assert r2.passed is False

    def test_count_properties(self) -> None:
        ctx = ExecutionContext()
        results = [
            CheckResult(check_name="g", result=GateResultType.GREEN),
            CheckResult(check_name="y", result=GateResultType.YELLOW),
            CheckResult(check_name="r", result=GateResultType.RED),
        ]
        r = PhaseExecutionResult(
            phase="test", checks_run=3, results=results, overall=GateResultType.RED, context=ctx
        )
        assert r.green_count == 1
        assert r.yellow_count == 1
        assert r.red_count == 1


class TestRedBlueConfrontation:
    """红蓝对抗 — 测试安全边界."""

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_red_stops_immediately_no_bypass(self, mock_run: MagicMock) -> None:
        """RED检查必须立即停止，不能绕过继续执行."""
        from zephyr.governance.phase_check_registry import GateResult

        call_count = [0]

        def side_effect(check_name: str) -> GateResult:
            call_count[0] += 1
            if call_count[0] == 1:
                return GateResult.RED
            return GateResult.GREEN

        mock_run.side_effect = side_effect
        ex = PhaseExecutor()
        result = ex.execute_phase(ConstructionPhase.PHASE_0_SKELETON)

        # Only 1 check should have run (RED stops immediately)
        assert result.checks_run == 1
        assert call_count[0] == 1

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_gate_engine_not_bypassed(self, mock_run: MagicMock) -> None:
        """execute_gate必须通过GateEngine，不能绕过."""
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.GREEN
        mock_ge = MagicMock()
        mock_ge.evaluate.return_value = MagicMock(passed=False)

        ex = PhaseExecutor(gate_engine=mock_ge)
        mock_task = MagicMock()
        result = ex.execute_gate(mock_task, "G7")

        # GateEngine.evaluate must be called
        mock_ge.evaluate.assert_called_once()
        assert result is mock_ge.evaluate.return_value

    def test_deadlock_prevention_empty_gate_ids(self) -> None:
        """空gate_ids列表不应导致死锁."""
        mock_ge = MagicMock()
        ex = PhaseExecutor(gate_engine=mock_ge)

        # Should complete without hanging
        with patch(
            "zephyr.governance.rule_enforcement.phase_executor.run_check"
        ) as mock_run:
            from zephyr.governance.phase_check_registry import GateResult

            mock_run.return_value = GateResult.GREEN
            phase_result, gate_results = ex.execute_phase_with_gates(
                ConstructionPhase.PHASE_0_SKELETON, MagicMock(), []
            )

        assert len(gate_results) == 0
        mock_ge.evaluate.assert_not_called()

    @patch("zephyr.governance.rule_enforcement.phase_executor.run_check")
    def test_context_not_corrupted_between_checks(self, mock_run: MagicMock) -> None:
        """上下文不应在检查间被破坏."""
        from zephyr.governance.phase_check_registry import GateResult

        mock_run.return_value = GateResult.GREEN
        ex = PhaseExecutor()
        ctx = ExecutionContext(phase="test", extra={"key": "value"})
        ex.execute_phase(ConstructionPhase.PHASE_0_SKELETON, context=ctx)

        # Original extra data should be preserved
        assert ctx.extra["key"] == "value"
        # Results should be added
        assert len(ctx.results) > 0
