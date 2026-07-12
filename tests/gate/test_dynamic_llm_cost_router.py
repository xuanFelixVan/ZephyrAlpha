# [A_test] module_id: SRC-TST-0785 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_dynamic_llm_cost_router
# [INVARIANTS] Budget check must be deterministic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.dynamic_llm_cost_router import DynamicLLMCostRouter


class TestDynamicLLMCostRouterInstantiation:
    def test_default_budget(self):
        router = DynamicLLMCostRouter()
        assert router.budget_remaining == 1000.0

    def test_custom_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=500.0)
        assert router.budget_remaining == 500.0


class TestCanAfford:
    def test_can_afford_within_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=100.0)
        assert router.can_afford(50.0) is True

    def test_cannot_afford_exceeding_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=100.0)
        assert router.can_afford(150.0) is False

    def test_can_afford_exact_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=100.0)
        assert router.can_afford(100.0) is True

    def test_cannot_afford_zero_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=0.0)
        assert router.can_afford(0.01) is False

    def test_can_afford_zero_cost(self):
        router = DynamicLLMCostRouter(budget_remaining=0.0)
        assert router.can_afford(0.0) is True

    def test_cannot_afford_negative_cost(self):
        router = DynamicLLMCostRouter(budget_remaining=100.0)
        assert router.can_afford(-10.0) is True
