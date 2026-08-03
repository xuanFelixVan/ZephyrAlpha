# [A_test] module_id: SRC-TST-0630 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_cost_attributor
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cost_attributor.py
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.budget_models import BudgetDimension
from zephyr.governance.ops_governance.cost_attributor import (
    CostAttribution,
    CostAttributor,
    CostSummary,
)


class TestCostAttribution:
    def test_creation(self):
        attr = CostAttribution(
            action_id="attr-000001",
            action_type="llm_call",
            tokens=500,
            cost=0.025,
            dimension=BudgetDimension.TOKEN,
        )
        assert attr.action_id == "attr-000001"
        assert attr.action_type == "llm_call"
        assert attr.tokens == 500
        assert attr.cost == 0.025
        assert attr.dimension == BudgetDimension.TOKEN
        assert attr.parent_id == ""
        assert attr.session_id == ""
        assert attr.timestamp > 0

    def test_with_optional_fields(self):
        attr = CostAttribution(
            action_id="attr-000002",
            action_type="embedding",
            tokens=100,
            cost=0.01,
            dimension=BudgetDimension.COST,
            parent_id="parent-1",
            session_id="sess-1",
        )
        assert attr.parent_id == "parent-1"
        assert attr.session_id == "sess-1"


class TestCostSummary:
    def test_default_values(self):
        cs = CostSummary()
        assert cs.total_tokens == 0
        assert cs.total_cost == 0.0
        assert cs.top_expensive == []

    def test_custom_values(self):
        cs = CostSummary(total_tokens=1000, total_cost=5.0)
        assert cs.total_tokens == 1000
        assert cs.total_cost == 5.0


class TestCostAttributor:
    def test_instantiation(self):
        ca = CostAttributor()
        assert ca.top_n == 10
        assert len(ca.attributions) == 0

    def test_instantiation_custom_top_n(self):
        ca = CostAttributor(top_n=5)
        assert ca.top_n == 5

    def test_attribute_returns_attribution(self):
        ca = CostAttributor()
        attr = ca.attribute("llm_call", 500, 0.025, BudgetDimension.TOKEN)
        assert attr.action_id.startswith("attr-")
        assert attr.action_type == "llm_call"
        assert attr.tokens == 500
        assert attr.cost == 0.025
        assert attr.dimension == BudgetDimension.TOKEN

    def test_attribute_increments_counter(self):
        ca = CostAttributor()
        a1 = ca.attribute("call1", 100, 0.01)
        a2 = ca.attribute("call2", 200, 0.02)
        assert a1.action_id != a2.action_id

    def test_summarize_empty(self):
        ca = CostAttributor()
        summary = ca.summarize()
        assert summary.total_tokens == 0
        assert summary.total_cost == 0.0
        assert summary.top_expensive == []

    def test_summarize_with_data(self):
        ca = CostAttributor()
        ca.attribute("llm_call", 1000, 0.05, BudgetDimension.TOKEN)
        ca.attribute("embedding", 500, 0.01, BudgetDimension.COST)
        summary = ca.summarize()
        assert summary.total_tokens == 1500
        assert summary.total_cost == pytest.approx(0.06, abs=1e-6)
        assert "llm_call" in summary.by_action_type
        assert "embedding" in summary.by_action_type
        assert BudgetDimension.TOKEN.value in summary.by_dimension
        assert BudgetDimension.COST.value in summary.by_dimension

    def test_summarize_top_expensive(self):
        ca = CostAttributor(top_n=2)
        ca.attribute("cheap", 100, 0.001)
        ca.attribute("mid", 200, 0.01)
        ca.attribute("expensive", 500, 0.1)
        summary = ca.summarize()
        assert len(summary.top_expensive) == 2
        assert summary.top_expensive[0].cost >= summary.top_expensive[1].cost

    def test_recent(self):
        ca = CostAttributor()
        for i in range(30):
            ca.attribute(f"action_{i}", i * 10, i * 0.01)
        recent = ca.recent(n=5)
        assert len(recent) == 5
        assert recent[-1].action_type == "action_29"

    def test_recent_fewer_than_n(self):
        ca = CostAttributor()
        ca.attribute("only_one", 100, 0.01)
        recent = ca.recent(n=10)
        assert len(recent) == 1

    def test_clear(self):
        ca = CostAttributor()
        ca.attribute("call", 100, 0.01)
        ca.attribute("call2", 200, 0.02)
        ca.clear()
        assert len(ca.attributions) == 0
        assert ca.counter == 0
        summary = ca.summarize()
        assert summary.total_tokens == 0

    def test_attribute_default_dimension(self):
        ca = CostAttributor()
        attr = ca.attribute("test", 100, 0.01)
        assert attr.dimension == BudgetDimension.TOKEN

    def test_summarize_cost_rounding(self):
        ca = CostAttributor()
        ca.attribute("a", 100, 0.003333)
        ca.attribute("b", 100, 0.003334)
        summary = ca.summarize()
        assert isinstance(summary.total_cost, float)
