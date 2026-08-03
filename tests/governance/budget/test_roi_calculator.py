# [A_test] module_id: MOD-GOV_roi_calculator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_roi_calculator
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_roi_calculator.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.roi_calculator import ROICalculator, ROIResult


class TestROICalculatorInit:
    def test_instantiation(self):
        calc = ROICalculator()
        result = calc.compute()
        assert result.tokens_spent == 0
        assert result.tokens_saved == 0


class TestRecordSpend:
    def test_record_spend_accumulates(self):
        calc = ROICalculator()
        calc.record_spend(100, 0.5)
        calc.record_spend(200, 1.0)
        result = calc.compute()
        assert result.tokens_spent == 300
        assert result.cost_spent == pytest.approx(1.5)

    def test_record_spend_zero(self):
        calc = ROICalculator()
        calc.record_spend(0, 0.0)
        result = calc.compute()
        assert result.tokens_spent == 0
        assert result.cost_spent == 0.0


class TestRecordSave:
    def test_record_save_accumulates(self):
        calc = ROICalculator()
        calc.record_save(500, 2.0)
        calc.record_save(300, 1.5)
        result = calc.compute()
        assert result.tokens_saved == 800
        assert result.cost_saved == pytest.approx(3.5)

    def test_record_save_zero(self):
        calc = ROICalculator()
        calc.record_save(0, 0.0)
        result = calc.compute()
        assert result.tokens_saved == 0


class TestCompute:
    def test_compute_excellent(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(500, 5.0)
        result = calc.compute()
        assert result.verdict == "EXCELLENT"
        assert result.net_roi > 1.0

    def test_compute_good(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(200, 2.0)
        result = calc.compute()
        assert result.verdict == "GOOD"

    def test_compute_neutral(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(100, 1.0)
        result = calc.compute()
        assert result.verdict == "NEUTRAL"

    def test_compute_poor(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(50, 0.8)
        result = calc.compute()
        assert result.verdict == "POOR"

    def test_compute_terrible(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(10, 0.1)
        result = calc.compute()
        assert result.verdict == "TERRIBLE"

    def test_compute_no_spent_cost(self):
        calc = ROICalculator()
        calc.record_save(100, 0.0)
        result = calc.compute()
        assert result.verdict == "NEUTRAL"
        assert result.net_roi == 100.0

    def test_compute_no_spent_cost_negative_tokens(self):
        calc = ROICalculator()
        result = calc.compute()
        assert result.verdict == "NEUTRAL"

    def test_compute_result_fields(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(200, 2.0)
        result = calc.compute()
        assert isinstance(result, ROIResult)
        assert result.tokens_spent == 100
        assert result.tokens_saved == 200


class TestReset:
    def test_reset_clears_all(self):
        calc = ROICalculator()
        calc.record_spend(100, 1.0)
        calc.record_save(500, 5.0)
        calc.reset()
        result = calc.compute()
        assert result.tokens_spent == 0
        assert result.tokens_saved == 0
        assert result.cost_spent == 0.0
        assert result.cost_saved == 0.0
