# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_six_step_flow | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_six_step_flow
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_six_step_flow.py
# [TTL] task_bound
"""D-FACTOR-GOV-04 六步流程编排测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- submit_factor: 提交后初始状态 research / 重复提交幂等
- get_status: 未提交返回 None / 已提交返回 FlowStatus
- advance: research→development 无门禁 / development→backtest 无门禁
  / backtest→paper 需门禁 / 门禁未过不推进 / 到 production 无法推进 / 未提交推进报错
- check_exit_gate: research/development 无门禁 / backtest 需门禁
"""

from __future__ import annotations

import pytest

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.six_step_flow import (
    SIX_STEPS,
    FlowStatus,
    SixStepFlow,
)


def _passing_result() -> EvaluationResult:
    """构造通过 ABS001 门禁的评估结果。"""
    return EvaluationResult("f1", 0.05, 0.1, 0.6, 0.55, False, 50)


def _failing_result() -> EvaluationResult:
    """构造不通过 ABS001 门禁的评估结果。"""
    return EvaluationResult("f1", 0.01, 0.1, 0.3, 0.4, True, 50)


class TestSubmitFactor:
    def test_initial_state_is_research(self):
        flow = SixStepFlow()
        state = flow.submit_factor("f1")
        assert state == "research"

    def test_submit_twice_keeps_research(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        state = flow.submit_factor("f1")
        assert state == "research"


class TestGetStatus:
    def test_unsubmitted_returns_none(self):
        flow = SixStepFlow()
        assert flow.get_status("unknown") is None

    def test_returns_flow_status(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        status = flow.get_status("f1")
        assert isinstance(status, FlowStatus)
        assert status.factor_id == "f1"
        assert status.current_step == "research"
        assert status.step_name == "研究"
        assert status.step_index == 0
        assert status.can_advance is True

    def test_step_index_advances(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())  # → development
        status = flow.get_status("f1")
        assert status.step_index == 1
        assert status.current_step == "development"


class TestAdvanceNoGate:
    def test_research_to_development_no_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        # 即使评估结果不达标，research→development 也无门禁
        new_step, msg = flow.advance("f1", _failing_result())
        assert new_step == "development"
        assert "推进" in msg

    def test_development_to_backtest_no_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _failing_result())  # research → development
        new_step, msg = flow.advance("f1", _failing_result())  # development → backtest
        assert new_step == "backtest"


class TestAdvanceWithGate:
    def test_backtest_to_paper_requires_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())  # → development
        flow.advance("f1", _passing_result())  # → backtest
        new_step, msg = flow.advance("f1", _passing_result())  # → paper (需门禁)
        assert new_step == "paper"

    def test_gate_fails_no_advance(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())  # → development
        flow.advance("f1", _passing_result())  # → backtest
        new_step, msg = flow.advance("f1", _failing_result())  # 门禁未过
        assert new_step == "backtest"
        assert "未通过" in msg

    def test_paper_to_grayscale_requires_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())  # → development
        flow.advance("f1", _passing_result())  # → backtest
        flow.advance("f1", _passing_result())  # → paper
        new_step, msg = flow.advance("f1", _passing_result())  # → grayscale
        assert new_step == "grayscale"

    def test_grayscale_to_production_requires_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        for _ in range(4):
            flow.advance("f1", _passing_result())  # → grayscale
        new_step, msg = flow.advance("f1", _passing_result())  # → production
        assert new_step == "production"


class TestAdvanceBoundary:
    def test_at_production_cannot_advance(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        for _ in range(5):
            flow.advance("f1", _passing_result())  # → production
        assert flow.get_status("f1").current_step == "production"
        new_step, msg = flow.advance("f1", _passing_result())
        assert new_step == "production"
        assert "无法" in msg

    def test_advance_unsubmitted(self):
        flow = SixStepFlow()
        new_step, msg = flow.advance("unknown", _passing_result())
        assert new_step == ""
        assert "未提交" in msg

    def test_can_advance_false_at_production(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        for _ in range(5):
            flow.advance("f1", _passing_result())  # → production
        status = flow.get_status("f1")
        assert status.can_advance is False
        assert status.step_index == len(SIX_STEPS) - 1


class TestCheckExitGate:
    def test_research_no_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        passed, detail = flow.check_exit_gate("f1", _failing_result())
        assert passed is True
        assert detail == ""

    def test_development_no_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())  # → development
        passed, detail = flow.check_exit_gate("f1", _failing_result())
        assert passed is True

    def test_backtest_requires_gate(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())
        flow.advance("f1", _passing_result())  # → backtest
        passed, detail = flow.check_exit_gate("f1", _passing_result())
        assert passed is True

    def test_backtest_gate_fails(self):
        flow = SixStepFlow()
        flow.submit_factor("f1")
        flow.advance("f1", _passing_result())
        flow.advance("f1", _passing_result())  # → backtest
        passed, detail = flow.check_exit_gate("f1", _failing_result())
        assert passed is False

    def test_check_exit_gate_unsubmitted(self):
        flow = SixStepFlow()
        passed, detail = flow.check_exit_gate("unknown", _passing_result())
        assert passed is False
        assert "未提交" in detail
