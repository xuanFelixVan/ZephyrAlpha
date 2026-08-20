# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_lifecycle_state_machine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_lifecycle_state_machine
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_lifecycle_state_machine.py
# [TTL] task_bound
"""D-FACTOR-GOV-01 因子生命周期状态机测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- create_factor_fsm: 初始状态 research / 实例类型 / 合法前向转换链
- 合法回退转换: grayscale→paper / backtest→research / paper→backtest
- 非法转换: research→backtest / research→production / development→paper 抛 InvalidTransitionError
- retired 终态: is_terminal / 终态后再转换抛错
- register_factor_lifecycle: 返回 fsm_id / 幂等
"""

from __future__ import annotations

import pytest

from zephyr.factor.governance.lifecycle_state_machine import (
    BACKTEST,
    DEPRECATED,
    DEVELOPMENT,
    FSM_ID,
    GRAYSCALE,
    PAPER,
    PRODUCTION,
    RESEARCH,
    RETIRED,
    create_factor_fsm,
    register_factor_lifecycle,
)
from zephyr.shared.lifecycle.state_machine import InvalidTransitionError, StateMachine


class TestCreateFactorFsm:
    def test_initial_state_is_research(self):
        fsm = create_factor_fsm()
        assert fsm.current_state == RESEARCH

    def test_returns_state_machine_instance(self):
        fsm = create_factor_fsm()
        assert isinstance(fsm, StateMachine)

    def test_legal_forward_transition(self):
        fsm = create_factor_fsm()
        fsm.transition(DEVELOPMENT)
        assert fsm.current_state == DEVELOPMENT

    def test_full_forward_chain(self):
        fsm = create_factor_fsm()
        chain = [DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE, PRODUCTION, DEPRECATED, RETIRED]
        for target in chain:
            fsm.transition(target)
            assert fsm.current_state == target

    def test_rollback_grayscale_to_paper(self):
        fsm = create_factor_fsm()
        for target in [DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE]:
            fsm.transition(target)
        fsm.transition(PAPER)  # 回退
        assert fsm.current_state == PAPER

    def test_rollback_backtest_to_research(self):
        fsm = create_factor_fsm()
        fsm.transition(DEVELOPMENT)
        fsm.transition(BACKTEST)
        fsm.transition(RESEARCH)  # 回退
        assert fsm.current_state == RESEARCH

    def test_rollback_paper_to_backtest(self):
        fsm = create_factor_fsm()
        fsm.transition(DEVELOPMENT)
        fsm.transition(BACKTEST)
        fsm.transition(PAPER)
        fsm.transition(BACKTEST)  # 回退
        assert fsm.current_state == BACKTEST

    def test_illegal_transition_research_to_backtest(self):
        fsm = create_factor_fsm()
        with pytest.raises(InvalidTransitionError):
            fsm.transition(BACKTEST)

    def test_illegal_transition_research_to_production(self):
        fsm = create_factor_fsm()
        with pytest.raises(InvalidTransitionError):
            fsm.transition(PRODUCTION)

    def test_illegal_transition_development_to_paper(self):
        fsm = create_factor_fsm()
        fsm.transition(DEVELOPMENT)
        with pytest.raises(InvalidTransitionError):
            fsm.transition(PAPER)

    def test_illegal_transition_backtest_to_grayscale(self):
        fsm = create_factor_fsm()
        fsm.transition(DEVELOPMENT)
        fsm.transition(BACKTEST)
        with pytest.raises(InvalidTransitionError):
            fsm.transition(GRAYSCALE)

    def test_illegal_transition_production_to_retired(self):
        fsm = create_factor_fsm()
        for target in [DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE, PRODUCTION]:
            fsm.transition(target)
        with pytest.raises(InvalidTransitionError):
            fsm.transition(RETIRED)

    def test_retired_is_terminal(self):
        fsm = create_factor_fsm()
        for target in [DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE, PRODUCTION, DEPRECATED, RETIRED]:
            fsm.transition(target)
        assert fsm.current_state == RETIRED
        assert fsm.is_terminal() is True

    def test_non_terminal_states(self):
        fsm = create_factor_fsm()
        assert fsm.is_terminal() is False
        fsm.transition(DEVELOPMENT)
        assert fsm.is_terminal() is False

    def test_illegal_transition_from_terminal_retired(self):
        fsm = create_factor_fsm()
        for target in [DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE, PRODUCTION, DEPRECATED, RETIRED]:
            fsm.transition(target)
        with pytest.raises(InvalidTransitionError):
            fsm.transition(RESEARCH)


class TestRegisterFactorLifecycle:
    def test_returns_fsm_id(self):
        fsm_id = register_factor_lifecycle()
        assert fsm_id == FSM_ID
        assert fsm_id == "factor_lifecycle"

    def test_idempotent(self):
        first = register_factor_lifecycle()
        second = register_factor_lifecycle()
        assert first == second == FSM_ID
