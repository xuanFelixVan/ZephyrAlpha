# [BLUEPRINT] MOD-PA-013 | docs/03_modules/_domain_portfolio_alloc/maxdd_limit_allocator/blueprint.md | §test
# [MODULE] tests.pf_alloc.test_maxdd_limit_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.core.maxdd_limit_allocator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_maxdd_limit_allocator.py
# [A_test] module_id: MOD-PA-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-PA-013 单元测试: MaxDdLimitAllocator — 按各策略回撤预算分配资金+超限降档/暂停。

覆盖: 三档动作判定（NORMAL/DERATE/SUSPEND）、权重归一（Σ=1.0）、只减不增不变式、
输入 Fail-Closed 校验（未知策略/缺失当前回撤/非法预算）、全员暂停零除防护、
与 MOD-PA-003 组合级一刀切的职责区分（按策略颗粒度）。
"""

from __future__ import annotations

import pytest

from zephyr.pf_alloc.core.maxdd_limit_allocator import (
    DdLimitAction,
    InvalidMaxDdInputError,
    MaxDdAllocatorConfig,
    MaxDdLimitAllocator,
    StrategyDdBudget,
)

_BUDGETS = (
    StrategyDdBudget(strategy_id="alpha", base_weight=0.5, max_dd_budget=0.10),
    StrategyDdBudget(strategy_id="beta", base_weight=0.3, max_dd_budget=0.08),
    StrategyDdBudget(strategy_id="gamma", base_weight=0.2, max_dd_budget=0.05),
)


class TestTierActions:
    def test_all_normal_when_utilization_low(self):
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.02, "beta": 0.01, "gamma": 0.01})
        assert all(a is DdLimitAction.NORMAL for a in out.actions.values())

    def test_derate_at_80pct_budget(self):
        """utilization >= 0.8 → 降档（权重 ×0.5）。"""
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.085, "beta": 0.01, "gamma": 0.01})
        assert out.actions["alpha"] is DdLimitAction.DERATE
        assert out.actions["beta"] is DdLimitAction.NORMAL

    def test_suspend_over_budget(self):
        """utilization >= 1.0 → 暂停（权重=0）。"""
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.10, "beta": 0.01, "gamma": 0.01})
        assert out.actions["alpha"] is DdLimitAction.SUSPEND
        assert out.weights["alpha"] == 0.0


class TestWeightInvariants:
    def test_weights_sum_to_one_when_any_active(self):
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.085, "beta": 0.01, "gamma": 0.01})
        assert sum(out.weights.values()) == pytest.approx(1.0)

    def test_derated_strategy_weight_shrinks(self):
        """降档只减不增：alpha 降档后权重 < 其 base 归一权重 0.5。"""
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.085, "beta": 0.01, "gamma": 0.01})
        assert out.weights["alpha"] < 0.5

    def test_suspended_weight_redistributed(self):
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"gamma": 0.06, "alpha": 0.01, "beta": 0.01})
        assert out.weights["gamma"] == 0.0
        assert sum(out.weights.values()) == pytest.approx(1.0)

    def test_all_suspended_no_div_zero(self):
        alloc = MaxDdLimitAllocator()
        out = alloc.allocate(_BUDGETS, {"alpha": 0.99, "beta": 0.99, "gamma": 0.99})
        assert out.all_suspended is True
        assert all(w == 0.0 for w in out.weights.values())


class TestInputValidation:
    def test_unknown_strategy_in_drawdowns_raises(self):
        alloc = MaxDdLimitAllocator()
        with pytest.raises(InvalidMaxDdInputError, match="未知策略"):
            alloc.allocate(_BUDGETS, {"alpha": 0.01, "beta": 0.01, "gamma": 0.01, "delta": 0.01})

    def test_missing_current_drawdown_raises(self):
        """当前回撤为风控关键输入，缺失 Fail-Closed 而非默认 0。"""
        alloc = MaxDdLimitAllocator()
        with pytest.raises(InvalidMaxDdInputError, match="缺失当前回撤"):
            alloc.allocate(_BUDGETS, {"alpha": 0.01, "beta": 0.01})

    def test_negative_drawdown_raises(self):
        alloc = MaxDdLimitAllocator()
        with pytest.raises(InvalidMaxDdInputError):
            alloc.allocate(_BUDGETS, {"alpha": -0.01, "beta": 0.01, "gamma": 0.01})

    def test_invalid_budget_raises(self):
        with pytest.raises(InvalidMaxDdInputError):
            StrategyDdBudget(strategy_id="x", base_weight=0.5, max_dd_budget=0.0)

    def test_config_thresholds_guard(self):
        with pytest.raises(InvalidMaxDdInputError):
            MaxDdAllocatorConfig(derate_threshold=1.5)
