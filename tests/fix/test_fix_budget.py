# [A_test] module_id: MOD-GOV_fix_budget | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §5
# [MODULE] tests.test_fix_budget
# [INVARIANTS] FixBudget daily<=50; monthly<=500; LLM tokens<=500000; FixStormGuard MUST detect storms
# [MODIFY-GUARD] blueprint.md §5; auto_fix_config.yaml budget section
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_fix_budget.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.auto_fix_engine.fix_budget import (
    DriftBudgetLink,
    FixBudget,
    FixStormGuard,
    LLMCostEstimator,
)
from zephyr.infrastructure.auto_fix_engine.models import BudgetInfo, FixLevel


class TestFixBudget:
    def test_default_instantiation(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(db_path=db)
        assert fb.daily_limit == 50
        assert fb.monthly_limit == 500
        assert fb.llm_token_limit == 500000

    def test_custom_config(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 10, "monthly_limit": 100, "llm_token_limit": 1000}, db_path=db)
        assert fb.daily_limit == 10
        assert fb.monthly_limit == 100
        assert fb.llm_token_limit == 1000

    def test_check_allowed(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(db_path=db)
        decision = fb.check(FixLevel.L1_RULE)
        assert decision.allowed is True
        assert decision.remaining_daily > 0

    def test_check_daily_exhausted(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 2}, db_path=db)
        fb.consume(FixLevel.L1_RULE, operation_id="op1")
        fb.consume(FixLevel.L1_RULE, operation_id="op2")
        decision = fb.check(FixLevel.L1_RULE)
        assert decision.allowed is False
        assert "Daily budget exhausted" in decision.reason

    def test_check_monthly_exhausted(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 1000, "monthly_limit": 2}, db_path=db)
        fb.consume(FixLevel.L1_RULE, operation_id="op1")
        fb.consume(FixLevel.L1_RULE, operation_id="op2")
        decision = fb.check(FixLevel.L1_RULE)
        assert decision.allowed is False
        assert "Monthly budget exhausted" in decision.reason

    def test_consume_l1(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 50, "monthly_limit": 500}, db_path=db)
        fb.consume(FixLevel.L1_RULE, operation_id="op1")
        info = fb.get_info()
        assert info.daily_remaining == 49
        assert info.monthly_remaining == 499

    def test_consume_l2_higher_cost(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 50, "monthly_limit": 500, "l2_cost_per_fix": 5}, db_path=db)
        fb.consume(FixLevel.L2_LLM, operation_id="op1")
        info = fb.get_info()
        assert info.daily_remaining == 45

    def test_consume_l3_highest_cost(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 50, "monthly_limit": 500, "l3_cost_per_fix": 10}, db_path=db)
        fb.consume(FixLevel.L3_AGENT, operation_id="op1")
        info = fb.get_info()
        assert info.daily_remaining == 40

    def test_llm_token_budget_check(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 50, "monthly_limit": 500, "llm_token_limit": 100}, db_path=db)
        fb.consume(FixLevel.L2_LLM, tokens=80, operation_id="op1")
        decision = fb.check(FixLevel.L2_LLM, tokens=50)
        assert decision.allowed is False
        assert "LLM token budget exhausted" in decision.reason

    def test_get_info(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(db_path=db)
        info = fb.get_info()
        assert isinstance(info, BudgetInfo)
        assert info.daily_remaining == 50
        assert info.monthly_remaining == 500
        assert info.llm_tokens_remaining == 500000

    def test_get_info_never_negative(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 1, "monthly_limit": 1}, db_path=db)
        fb.consume(FixLevel.L1_RULE, operation_id="op1")
        fb.consume(FixLevel.L1_RULE, operation_id="op2")
        info = fb.get_info()
        assert info.daily_remaining >= 0
        assert info.monthly_remaining >= 0

    def test_none_config_defaults(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config=None, db_path=db)
        assert fb.daily_limit == 50


class TestDriftBudgetLink:
    def test_check_drift_budget_allowed(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(db_path=db)
        dbl = DriftBudgetLink(fb)
        decision = dbl.evaluate_drift_budget()
        assert decision.allowed is True

    def test_check_drift_budget_exhausted(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(config={"daily_limit": 100, "monthly_limit": 1000}, db_path=db)
        dbl = DriftBudgetLink(fb)
        dbl.drift_fix_limit = 2
        dbl.record_drift_fix()
        dbl.record_drift_fix()
        decision = dbl.evaluate_drift_budget()
        assert decision.allowed is False
        assert "Drift fix budget exhausted" in decision.reason

    def test_record_drift_fix_increments(self, tmp_path):
        db = str(tmp_path / "budget_test.db")
        fb = FixBudget(db_path=db)
        dbl = DriftBudgetLink(fb)
        dbl.record_drift_fix()
        assert dbl.drift_fix_count == 1
        dbl.record_drift_fix()
        assert dbl.drift_fix_count == 2


class TestFixStormGuard:
    def test_default_instantiation(self):
        guard = FixStormGuard()
        assert guard.short_window == 60
        assert guard.short_threshold == 30
        assert guard.long_window == 300
        assert guard.long_threshold == 100

    def test_check_initially_passes(self):
        guard = FixStormGuard()
        ok, reason = guard.check()
        assert ok is True
        assert reason == ""

    def test_record_and_check(self):
        guard = FixStormGuard(config={"short_window_sec": 1, "short_threshold": 3})
        guard.record()
        guard.record()
        ok, reason = guard.check()
        assert ok is True

    def test_storm_detection_short_window(self):
        guard = FixStormGuard(config={"short_window_sec": 10, "short_threshold": 3, "cooldown_sec": 1})
        guard.record()
        guard.record()
        guard.record()
        ok, reason = guard.check()
        assert ok is False
        assert "Short-window storm detected" in reason

    def test_is_active_property(self):
        guard = FixStormGuard(config={"short_window_sec": 10, "short_threshold": 2, "cooldown_sec": 60})
        guard.record()
        guard.record()
        guard.check()
        assert guard.is_active is True

    def test_custom_config(self):
        guard = FixStormGuard(config={"short_window_sec": 30, "short_threshold": 5})
        assert guard.short_window == 30
        assert guard.short_threshold == 5


class TestLLMCostEstimator:
    def test_default_instantiation(self):
        est = LLMCostEstimator()
        assert est.cost_per_1k_input == 0.001
        assert est.cost_per_1k_output == 0.002

    def test_estimate(self):
        est = LLMCostEstimator(cost_per_1k_input=0.01, cost_per_1k_output=0.03)
        result = est.estimate(input_tokens=1000, output_tokens=500)
        assert result["input_tokens"] == 1000
        assert result["output_tokens"] == 500
        assert abs(result["estimated_cost"] - (0.01 + 0.015)) < 0.0001

    def test_estimate_zero_tokens(self):
        est = LLMCostEstimator()
        result = est.estimate(input_tokens=0, output_tokens=0)
        assert result["estimated_cost"] == 0.0

    def test_estimate_for_fix_simple(self):
        est = LLMCostEstimator()
        result = est.estimate_for_fix(target_lines=10, complexity="simple")
        assert result["input_tokens"] == 150
        assert result["output_tokens"] == 50

    def test_estimate_for_fix_complex(self):
        est = LLMCostEstimator()
        result = est.estimate_for_fix(target_lines=10, complexity="complex")
        assert result["input_tokens"] == 600
        assert result["output_tokens"] == 200

    def test_estimate_for_fix_unknown_complexity(self):
        est = LLMCostEstimator()
        result = est.estimate_for_fix(target_lines=10, complexity="unknown")
        assert result["input_tokens"] == 300
        assert result["output_tokens"] == 100
