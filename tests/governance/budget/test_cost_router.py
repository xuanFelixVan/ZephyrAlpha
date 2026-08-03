# [A_test] module_id: MOD-GOV_cost_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_cost_router
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cost_router.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.cost_router import (
    PRICING_TABLE,
    LLMProvider,
    ModelPricing,
    RoutingPolicy,
    estimate_cost,
    get_pricing,
    list_models_sorted_by_cost,
    route,
    route_min_cost,
)


class TestLLMProvider:
    def test_all_providers_exist(self):
        expected = [
            "deepseek",
            "glm-4.7",
            "glm-4.6",
            "glm-4.5",
            "kimi-k2",
            "claude-sonnet-4.5",
            "o4-mini",
            "gpt-5.1-codex",
            "grok-4",
            "gpt-5.2",
            "qwen3-coder",
        ]
        for name in expected:
            assert any(m.value == name for m in LLMProvider)

    def test_enum_is_str(self):
        for member in LLMProvider:
            assert isinstance(member, str)

    def test_provider_count(self):
        assert len(LLMProvider) == 11


class TestRoutingPolicy:
    def test_policies(self):
        assert RoutingPolicy.COST_MIN.value == "COST_MIN"
        assert RoutingPolicy.THROUGHPUT.value == "THROUGHPUT"

    def test_enum_is_str(self):
        for member in RoutingPolicy:
            assert isinstance(member, str)


class TestModelPricing:
    def test_creation(self):
        mp = ModelPricing(
            provider=LLMProvider.DEEPSEEK,
            cost_per_1k_input=0.27,
            cost_per_1k_output=1.10,
            throughput_rank=4,
            context_window=65536,
        )
        assert mp.provider == LLMProvider.DEEPSEEK
        assert mp.cost_per_1k_input == 0.27
        assert mp.cost_per_1k_output == 1.10
        assert mp.throughput_rank == 4
        assert mp.context_window == 65536


class TestPricingTable:
    def test_all_providers_in_table(self):
        for provider in LLMProvider:
            assert provider in PRICING_TABLE

    def test_pricing_values_positive(self):
        for provider, pricing in PRICING_TABLE.items():
            assert pricing.cost_per_1k_input > 0
            assert pricing.cost_per_1k_output > 0
            assert pricing.throughput_rank > 0
            assert pricing.context_window > 0


class TestEstimateCost:
    def test_known_provider(self):
        cost = estimate_cost(LLMProvider.DEEPSEEK, 10000)
        assert cost > 0.0
        assert isinstance(cost, float)

    def test_cost_scales_with_tokens(self):
        cost_small = estimate_cost(LLMProvider.DEEPSEEK, 1000)
        cost_large = estimate_cost(LLMProvider.DEEPSEEK, 10000)
        assert cost_large > cost_small

    def test_zero_tokens(self):
        cost = estimate_cost(LLMProvider.DEEPSEEK, 0)
        assert cost == 0.0

    def test_custom_ratio(self):
        cost_default = estimate_cost(LLMProvider.DEEPSEEK, 10000)
        cost_high_output = estimate_cost(LLMProvider.DEEPSEEK, 10000, input_output_ratio=0.1)
        p = PRICING_TABLE[LLMProvider.DEEPSEEK]
        if p.cost_per_1k_output > p.cost_per_1k_input:
            assert cost_high_output > cost_default

    def test_result_rounded(self):
        cost = estimate_cost(LLMProvider.DEEPSEEK, 12345)
        assert cost == round(cost, 4)


class TestRouteMinCost:
    def test_returns_provider(self):
        provider = route_min_cost(10000)
        assert isinstance(provider, LLMProvider)

    def test_returns_cheapest(self):
        provider = route_min_cost(10000)
        costs = {}
        for p in LLMProvider:
            costs[p] = estimate_cost(p, 10000)
        assert costs[provider] == min(costs.values())


class TestRoute:
    def test_cost_min_policy(self):
        provider = route(10000, RoutingPolicy.COST_MIN)
        assert isinstance(provider, LLMProvider)

    def test_throughput_policy(self):
        provider = route(10000, RoutingPolicy.THROUGHPUT)
        assert isinstance(provider, LLMProvider)
        candidates = sorted(PRICING_TABLE.values(), key=lambda m: m.throughput_rank)
        assert provider == candidates[0].provider

    def test_default_is_cost_min(self):
        provider = route(10000)
        min_cost_provider = route_min_cost(10000)
        assert provider == min_cost_provider


class TestGetPricing:
    def test_known_provider(self):
        pricing = get_pricing(LLMProvider.DEEPSEEK)
        assert pricing is not None
        assert pricing.provider == LLMProvider.DEEPSEEK

    def test_returns_model_pricing(self):
        pricing = get_pricing(LLMProvider.CLAUDE_SONNET_4_5)
        assert isinstance(pricing, ModelPricing)


class TestListModelsSortedByCost:
    def test_returns_list(self):
        result = list_models_sorted_by_cost()
        assert isinstance(result, list)
        assert len(result) == len(LLMProvider)

    def test_sorted_ascending(self):
        result = list_models_sorted_by_cost()
        costs = [inp + out for _, inp, out in result]
        assert costs == sorted(costs)

    def test_tuple_structure(self):
        result = list_models_sorted_by_cost()
        for provider, inp, out in result:
            assert isinstance(provider, LLMProvider)
            assert inp > 0
            assert out > 0
