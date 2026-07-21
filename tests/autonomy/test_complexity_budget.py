# [A_test] module_id: MOD-GOV_complexity_budget | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_complexity_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_complexity_budget.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.complexity_budget import (
    ComplexityAdjustedBudget,
    ComplexityBudgetAdjuster,
)


class TestComplexityAdjustedBudget:
    def test_instantiation(self):
        cab = ComplexityAdjustedBudget(base_budget=8000, complexity_factor=1.1, adjusted_budget=8800)
        assert cab.base_budget == 8000
        assert cab.complexity_factor == 1.1
        assert cab.adjusted_budget == 8800

    def test_missing_field_raises(self):
        with pytest.raises(TypeError):
            ComplexityAdjustedBudget()


class TestComplexityBudgetAdjuster:
    def test_instantiation(self):
        adjuster = ComplexityBudgetAdjuster()
        assert adjuster is not None

    def test_adjust_defaults(self):
        adjuster = ComplexityBudgetAdjuster()
        result = adjuster.adjust()
        assert result.base_budget == 8000
        assert result.complexity_factor > 1.0
        assert result.adjusted_budget > result.base_budget

    def test_adjust_p0_higher_factor_than_p2(self):
        adjuster = ComplexityBudgetAdjuster()
        p0 = adjuster.adjust(base_budget=8000, ast_complexity=20, priority="P0")
        p2 = adjuster.adjust(base_budget=8000, ast_complexity=20, priority="P2")
        assert p0.complexity_factor > p2.complexity_factor

    def test_adjust_zero_complexity(self):
        adjuster = ComplexityBudgetAdjuster()
        result = adjuster.adjust(base_budget=10000, ast_complexity=0, priority="P0")
        assert result.complexity_factor == 1.0
        assert result.adjusted_budget == 10000

    def test_adjust_high_complexity(self):
        adjuster = ComplexityBudgetAdjuster()
        result = adjuster.adjust(base_budget=5000, ast_complexity=100, priority="P0")
        assert result.complexity_factor == 2.0
        assert result.adjusted_budget == 10000

    def test_adjust_factor_rounded(self):
        adjuster = ComplexityBudgetAdjuster()
        result = adjuster.adjust(base_budget=8000, ast_complexity=33, priority="P2")
        assert result.complexity_factor == round(result.complexity_factor, 2)

    def test_adjusted_budget_is_int(self):
        adjuster = ComplexityBudgetAdjuster()
        result = adjuster.adjust(base_budget=7000, ast_complexity=15, priority="P1")
        assert isinstance(result.adjusted_budget, int)
