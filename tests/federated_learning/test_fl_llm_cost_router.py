# [A_test] module_id: SRC-TST-0971 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_llm_cost_router
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.llm_cost_router
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_llm_cost_router.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.llm_cost_router import LLMCostRouter


class TestLLMCostRouterInstantiation:
    def test_default_construction(self):
        router = LLMCostRouter()
        assert router.budget_monthly == 1000.0
        assert router.spent == 0.0


class TestRoute:
    def test_route_low_priority_to_cheap_model(self):
        router = LLMCostRouter()
        assert router.route(3) == "cheap-model"

    def test_route_high_priority_to_best_model(self):
        router = LLMCostRouter()
        assert router.route(7) == "best-model"

    def test_route_boundary_priority_five(self):
        router = LLMCostRouter()
        assert router.route(5) == "best-model"

    def test_route_boundary_priority_four(self):
        router = LLMCostRouter()
        assert router.route(4) == "cheap-model"


class TestBoundaries:
    def test_route_zero_priority(self):
        router = LLMCostRouter()
        assert router.route(0) == "cheap-model"

    def test_route_negative_priority(self):
        router = LLMCostRouter()
        assert router.route(-1) == "cheap-model"

    def test_route_max_priority(self):
        router = LLMCostRouter()
        assert router.route(100) == "best-model"
