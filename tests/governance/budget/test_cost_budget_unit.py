# [A_test] module_id: MOD-GOV_cost_budget_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-620 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_cost_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for cost_budget.py
"""

import pytest

from zephyr.governance.ops_governance.cost_budget import CostBudget, CostBudgetExceededError, PricingTier


class TestPricingTier:
    def test_create_pricing_tier(self):
        tier = PricingTier(model="gpt-4o", input_price_per_1k=0.0025, output_price_per_1k=0.0100)
        assert tier.model == "gpt-4o"
        assert tier.input_price_per_1k == 0.0025
        assert tier.output_price_per_1k == 0.0100
        assert tier.cached_input_price_per_1k is None

    def test_pricing_tier_with_cache(self):
        tier = PricingTier(
            model="claude-3.5-sonnet",
            input_price_per_1k=0.003,
            output_price_per_1k=0.015,
            cached_input_price_per_1k=0.0003,
        )
        assert tier.cached_input_price_per_1k == 0.0003


class TestCostBudget:
    def test_initial_state(self):
        budget = CostBudget(hard_limit=10.00)
        assert budget.hard_limit == 10.00
        assert budget.cumulative_cost == 0.0
        assert budget.call_count == 0
        assert budget.remaining == 10.00
        assert budget.usage_ratio == 0.0

    def test_set_pricing(self):
        budget = CostBudget()
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        assert "openai" in budget.provider_pricing
        assert "gpt-4o" in budget.provider_pricing["openai"]

    def test_get_cost_known_provider(self):
        budget = CostBudget()
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        cost = budget.get_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert cost == pytest.approx(0.0075)

    def test_get_cost_unknown_provider_returns_zero(self):
        budget = CostBudget()
        cost = budget.get_cost("unknown", "unknown-model", input_tokens=1000)
        assert cost == 0.0

    def test_get_cost_cached_tokens(self):
        budget = CostBudget()
        budget.set_pricing("anthropic", "claude-3.5", input_1k=0.003, output_1k=0.015, cached_input_1k=0.0003)
        cost = budget.get_cost("anthropic", "claude-3.5", input_tokens=0, output_tokens=0, cached_input_tokens=1000)
        assert cost == pytest.approx(0.0003)

    def test_record_usage_updates_cumulative_cost(self):
        budget = CostBudget(hard_limit=10.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        cost = budget.record_usage("openai", "gpt-4o", input_tokens=2000, output_tokens=1000)
        assert cost == pytest.approx(0.015)
        assert budget.cumulative_cost == pytest.approx(0.015)
        assert budget.call_count == 1

    def test_record_usage_multiple_calls(self):
        budget = CostBudget(hard_limit=10.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert budget.call_count == 2
        assert budget.cumulative_cost == pytest.approx(0.015)

    def test_check_budget_under_limit(self):
        budget = CostBudget(hard_limit=10.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        budget.assert_budget()

    def test_check_budget_exceeded_raises(self):
        budget = CostBudget(hard_limit=0.001)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000)

        with pytest.raises(CostBudgetExceededError) as exc_info:
            budget.assert_budget("openai", "gpt-4o")
        assert exc_info.value.provider == "openai"
        assert exc_info.value.model == "gpt-4o"

    def test_check_budget_or_warn_below_warning(self):
        budget = CostBudget(hard_limit=10.00, warning_ratio=0.80)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000)
        assert budget.check_budget_or_warn() is None

    def test_check_budget_or_warn_above_warning(self):
        budget = CostBudget(hard_limit=0.02, warning_ratio=0.50)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=5000)
        msg = budget.check_budget_or_warn()
        assert msg is not None
        assert "warning" in msg.lower()

    def test_remaining_property(self):
        budget = CostBudget(hard_limit=5.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert budget.remaining == pytest.approx(5.00 - 0.0075)

    def test_remaining_never_negative(self):
        budget = CostBudget(hard_limit=0.001)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=10000)
        assert budget.remaining == 0.0

    def test_usage_ratio(self):
        budget = CostBudget(hard_limit=0.01)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        assert budget.usage_ratio == 0.0
        budget.record_usage("openai", "gpt-4o", input_tokens=10000)
        assert budget.usage_ratio == 1.0

    def test_reset(self):
        budget = CostBudget(hard_limit=10.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=1000)
        budget.reset()
        assert budget.cumulative_cost == 0.0
        assert budget.call_count == 0

    def test_cost_budget_exceeded_error_message(self):
        budget = CostBudget(hard_limit=0.01)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.record_usage("openai", "gpt-4o", input_tokens=10000)

        with pytest.raises(CostBudgetExceededError) as exc_info:
            budget.assert_budget("openai", "gpt-4o")
        assert "Cost budget exceeded" in str(exc_info.value)
        assert "openai" in str(exc_info.value)
