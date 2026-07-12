# [A_test] module_id: SRC-TST-0955 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_dynamic_llm_cost_router
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.dynamic_llm_cost_router
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_dynamic_llm_cost_router.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.dynamic_llm_cost_router import DynamicLLMCostRouter


class TestDynamicLLMCostRouterInstantiation:
    def test_default_construction(self):
        router = DynamicLLMCostRouter()
        assert router.budget_remaining == 1000.0


class TestCanAfford:
    def test_can_afford_within_budget(self):
        router = DynamicLLMCostRouter()
        assert router.can_afford(500.0) is True

    def test_can_afford_exact_budget(self):
        router = DynamicLLMCostRouter()
        assert router.can_afford(1000.0) is True

    def test_cannot_afford_over_budget(self):
        router = DynamicLLMCostRouter()
        assert router.can_afford(1001.0) is False


class TestBoundaries:
    def test_can_afford_zero_cost(self):
        router = DynamicLLMCostRouter()
        assert router.can_afford(0.0) is True

    def test_can_afford_negative_cost(self):
        router = DynamicLLMCostRouter()
        assert router.can_afford(-1.0) is True

    def test_zero_budget(self):
        router = DynamicLLMCostRouter(budget_remaining=0.0)
        assert router.can_afford(0.01) is False
