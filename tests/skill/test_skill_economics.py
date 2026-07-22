# [A_test] module_id: MOD-GOV_skill_economics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_economics
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_economics.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skills.skill_economics import PRICING, SkillEconomics


@pytest.fixture
def econ():
    return SkillEconomics()


class TestSkillEconomicsInit:
    def test_instantiation(self, econ):
        assert econ._costs == {}
        assert econ._spent == 0.0

    def test_pricing_table_not_empty(self):
        assert len(PRICING) > 0
        for model, prices in PRICING.items():
            assert "in" in prices
            assert "out" in prices
            assert prices["in"] >= 0
            assert prices["out"] >= 0


class TestSkillEconomicsTrackCost:
    def test_track_cost_single_call(self, econ):
        result = econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        assert result["skill_id"] == "skill-1"
        assert result["cost_estimated"] > 0
        assert result["session_total"] == result["cost_estimated"]

    def test_track_cost_accumulates(self, econ):
        econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        r2 = econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        assert r2["session_total"] > r2["cost_estimated"]

    def test_track_cost_updates_skill_record(self, econ):
        econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        costs = econ.get_costs("skill-1")
        assert costs["calls"] == 1
        assert costs["in"] == 1000
        assert costs["out"] == 500
        assert costs["total_cost"] > 0

    def test_track_cost_multiple_skills(self, econ):
        econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        econ.track_cost("skill-2", 2000, 1000, "gpt-4o")
        c1 = econ.get_costs("skill-1")
        c2 = econ.get_costs("skill-2")
        assert c1["calls"] == 1
        assert c2["calls"] == 1
        assert c2["total_cost"] > c1["total_cost"]

    def test_track_cost_zero_tokens(self, econ):
        result = econ.track_cost("skill-1", 0, 0, "deepseek-chat")
        assert result["cost_estimated"] == 0.0

    def test_track_cost_unknown_model_uses_default(self, econ):
        result = econ.track_cost("skill-1", 1000, 1000, "unknown-model-xyz")
        assert result["cost_estimated"] > 0

    def test_track_cost_claude_pricing(self, econ):
        result = econ.track_cost("skill-1", 1000, 1000, "claude-sonnet-4")
        assert result["cost_estimated"] > 0
        p = PRICING["claude-sonnet-4"]
        expected = (1000 / 1000.0) * p["in"] + (1000 / 1000.0) * p["out"]
        assert abs(result["cost_estimated"] - expected) < 0.001


class TestSkillEconomicsGetCosts:
    def test_get_costs_existing_skill(self, econ):
        econ.track_cost("skill-1", 1000, 500, "deepseek-chat")
        costs = econ.get_costs("skill-1")
        assert "total_cost" in costs
        assert "calls" in costs

    def test_get_costs_nonexistent_skill(self, econ):
        costs = econ.get_costs("no-such-skill")
        assert costs["total_cost"] == 0.0
        assert costs["calls"] == 0


class TestSkillEconomicsRecommendCheapest:
    def test_recommend_returns_model(self, econ):
        result = econ.recommend_cheapest_model()
        assert "recommended" in result
        assert "cost_per_1k_in" in result
        assert "cost_per_1k_out" in result

    def test_recommend_cheapest_is_lowest_cost(self, econ):
        result = econ.recommend_cheapest_model()
        total = result["cost_per_1k_in"] + result["cost_per_1k_out"]
        for model, prices in PRICING.items():
            if model in ("deepseek-chat", "glm-4-flash"):
                continue
            assert total <= prices["in"] + prices["out"]

    def test_recommend_with_different_strength(self, econ):
        r1 = econ.recommend_cheapest_model("code_generation")
        r2 = econ.recommend_cheapest_model("analysis")
        assert "recommended" in r1
        assert "recommended" in r2
