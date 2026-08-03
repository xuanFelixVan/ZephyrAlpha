# [A_test] module_id: SRC-TST-0631 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_cost_budget
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cost_budget_root.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.cost_budget import (
    CostBudget,
    CostBudgetExceededError,
    PricingTier,
)


class TestPricingTier:
    def test_creation(self):
        tier = PricingTier(
            model="gpt-4o",
            input_price_per_1k=0.0025,
            output_price_per_1k=0.01,
        )
        assert tier.model == "gpt-4o"
        assert tier.input_price_per_1k == 0.0025
        assert tier.output_price_per_1k == 0.01
        assert tier.cached_input_price_per_1k is None

    def test_creation_with_cached(self):
        tier = PricingTier(
            model="gpt-4o",
            input_price_per_1k=0.0025,
            output_price_per_1k=0.01,
            cached_input_price_per_1k=0.00125,
        )
        assert tier.cached_input_price_per_1k == 0.00125


class TestCostBudgetExceededError:
    def test_error_message(self):
        err = CostBudgetExceededError(current=6.0, limit=5.0, provider="openai", model="gpt-4o")
        assert "6.0000" in str(err)
        assert "5.0000" in str(err)
        assert "openai" in str(err)
        assert "gpt-4o" in str(err)

    def test_error_attributes(self):
        err = CostBudgetExceededError(current=6.0, limit=5.0, provider="deepseek", model="v4")
        assert err.current == 6.0
        assert err.limit == 5.0
        assert err.provider == "deepseek"
        assert err.model == "v4"


class TestCostBudget:
    def test_instantiation_defaults(self):
        cb = CostBudget()
        assert cb.hard_limit == 10.00
        assert cb.warning_ratio == 0.80
        assert cb.cumulative_cost == 0.0
        assert cb.call_count == 0

    def test_instantiation_custom(self):
        cb = CostBudget(hard_limit=5.0, warning_ratio=0.7)
        assert cb.hard_limit == 5.0
        assert cb.warning_ratio == 0.7

    def test_set_pricing(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.01)
        assert "openai" in cb.provider_pricing
        assert "gpt-4o" in cb.provider_pricing["openai"]

    def test_set_pricing_with_cached(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.01, cached_input_1k=0.00125)
        tier = cb.provider_pricing["openai"]["gpt-4o"]
        assert tier.cached_input_price_per_1k == 0.00125

    def test_get_cost_known_provider(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0)
        cost = cb.get_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        expected = 2.5 * 1.0 + 10.0 * 0.5
        assert cost == pytest.approx(expected, abs=1e-6)

    def test_get_cost_unknown_provider(self):
        cb = CostBudget()
        assert cb.get_cost("unknown", "model", input_tokens=1000) == 0.0

    def test_get_cost_with_cached(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0, cached_input_1k=1.25)
        cost = cb.get_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500, cached_input_tokens=500)
        expected = 2.5 * 1.0 + 10.0 * 0.5 + 1.25 * 0.5
        assert cost == pytest.approx(expected, abs=1e-6)

    def test_get_cost_zero_tokens(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0)
        assert cb.get_cost("openai", "gpt-4o") == 0.0

    def test_check_budget_under_limit(self):
        cb = CostBudget(hard_limit=10.0)
        cb.assert_budget("openai", "gpt-4o")

    def test_check_budget_exceeds_limit(self):
        cb = CostBudget(hard_limit=1.0)
        cb.cumulative_cost = 1.5
        with pytest.raises(CostBudgetExceededError) as exc_info:
            cb.assert_budget("openai", "gpt-4o")
        assert exc_info.value.current == 1.5
        assert exc_info.value.limit == 1.0

    def test_check_budget_at_limit(self):
        cb = CostBudget(hard_limit=5.0)
        cb.cumulative_cost = 5.0
        with pytest.raises(CostBudgetExceededError):
            cb.assert_budget()

    def test_check_budget_or_warn_under_warning(self):
        cb = CostBudget(hard_limit=10.0, warning_ratio=0.8)
        result = cb.check_budget_or_warn("openai", "gpt-4o")
        assert result is None

    def test_check_budget_or_warn_at_warning(self):
        cb = CostBudget(hard_limit=10.0, warning_ratio=0.8)
        cb.cumulative_cost = 8.5
        result = cb.check_budget_or_warn("openai", "gpt-4o")
        assert result is not None
        assert "warning" in result.lower()

    def test_check_budget_or_warn_exceeds_hard(self):
        cb = CostBudget(hard_limit=10.0, warning_ratio=0.8)
        cb.cumulative_cost = 11.0
        with pytest.raises(CostBudgetExceededError):
            cb.check_budget_or_warn()

    def test_record_usage(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0)
        cost = cb.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert cost > 0.0
        assert cb.cumulative_cost == cost
        assert cb.call_count == 1

    def test_record_usage_unknown_provider(self):
        cb = CostBudget()
        cost = cb.record_usage("unknown", "model", input_tokens=1000)
        assert cost == 0.0
        assert cb.call_count == 1

    def test_remaining(self):
        cb = CostBudget(hard_limit=10.0)
        cb.cumulative_cost = 3.0
        assert cb.remaining == pytest.approx(7.0)

    def test_remaining_never_negative(self):
        cb = CostBudget(hard_limit=5.0)
        cb.cumulative_cost = 10.0
        assert cb.remaining == 0.0

    def test_usage_ratio(self):
        cb = CostBudget(hard_limit=10.0)
        cb.cumulative_cost = 7.5
        assert cb.usage_ratio == pytest.approx(0.75)

    def test_usage_ratio_zero_limit(self):
        cb = CostBudget(hard_limit=0)
        assert cb.usage_ratio == 1.0

    def test_reset(self):
        cb = CostBudget(hard_limit=10.0)
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0)
        cb.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        cb.reset()
        assert cb.cumulative_cost == 0.0
        assert cb.call_count == 0

    def test_multiple_record_usage_accumulates(self):
        cb = CostBudget()
        cb.set_pricing("openai", "gpt-4o", input_1k=2.5, output_1k=10.0)
        cb.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=0)
        cb.record_usage("openai", "gpt-4o", input_tokens=1000, output_tokens=0)
        assert cb.cumulative_cost == pytest.approx(5.0)
        assert cb.call_count == 2
