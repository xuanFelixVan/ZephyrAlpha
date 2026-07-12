# [A_test] module_id: SRC-TST-1231 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_llm_cost_router
# [INVARIANTS] Route decision must be deterministic for same priority
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.llm_cost_router import LLMCostRouter


class TestLLMCostRouterInstantiation:
    def test_default_values(self):
        router = LLMCostRouter()
        assert router.budget_monthly == 1000.0
        assert router.spent == 0.0

    def test_custom_values(self):
        router = LLMCostRouter(budget_monthly=500.0, spent=100.0)
        assert router.budget_monthly == 500.0
        assert router.spent == 100.0


class TestRoute:
    def test_low_priority_routes_cheap(self):
        router = LLMCostRouter()
        assert router.route(1) == "cheap-model"

    def test_high_priority_routes_best(self):
        router = LLMCostRouter()
        assert router.route(5) == "best-model"

    def test_priority_4_routes_cheap(self):
        router = LLMCostRouter()
        assert router.route(4) == "cheap-model"

    def test_priority_5_routes_best(self):
        router = LLMCostRouter()
        assert router.route(5) == "best-model"

    def test_priority_0_routes_cheap(self):
        router = LLMCostRouter()
        assert router.route(0) == "cheap-model"

    def test_priority_10_routes_best(self):
        router = LLMCostRouter()
        assert router.route(10) == "best-model"
