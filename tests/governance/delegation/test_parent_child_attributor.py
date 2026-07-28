# [A_test] module_id: MOD-GOV_parent_child_attributor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_parent_child_attributor
# [INVARIANTS] analyze returns DelegationReport; children_of returns list
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.parent_child_attributor import (
    AttributionChain,
    DelegationReport,
    ParentChildAttributor,
)


class TestAttributionChain:
    def test_creation(self):
        chain = AttributionChain(
            parent_id="parent-1", child_id="child-1", tokens_delegated=100, cost_delegated=0.5, depth=1
        )
        assert chain.parent_id == "parent-1"
        assert chain.tokens_delegated == 100
        assert chain.depth == 1

    def test_timestamp_auto_set(self):
        chain = AttributionChain(parent_id="p", child_id="c", tokens_delegated=50, cost_delegated=0.1, depth=1)
        assert chain.timestamp > 0


class TestParentChildAttributor:
    def test_instantiation_defaults(self):
        attr = ParentChildAttributor()
        report = attr.analyze()
        assert report.total_delegated_tokens == 0

    def test_instantiation_custom(self):
        attr = ParentChildAttributor(max_depth=3, max_delegation=50000)
        report = attr.analyze()
        assert report.chain_depth == 0

    def test_record_delegation(self):
        attr = ParentChildAttributor()
        chain = attr.record_delegation("parent-1", "child-1", tokens=100, cost=0.5)
        assert isinstance(chain, AttributionChain)
        assert chain.parent_id == "parent-1"
        assert chain.child_id == "child-1"

    def test_analyze_with_data(self):
        attr = ParentChildAttributor()
        attr.record_delegation("p1", "c1", tokens=500, cost=0.1)
        attr.record_delegation("p1", "c2", tokens=300, cost=0.2)
        report = attr.analyze()
        assert isinstance(report, DelegationReport)
        assert report.total_delegated_tokens == 800
        assert report.total_delegated_cost == pytest.approx(0.3)
        assert report.chain_depth == 2

    def test_analyze_deep_chain(self):
        attr = ParentChildAttributor(max_depth=3)
        attr.record_delegation("p1", "c1", tokens=100, cost=0.1, depth=1)
        attr.record_delegation("c1", "c2", tokens=100, cost=0.1, depth=2)
        attr.record_delegation("c2", "c3", tokens=100, cost=0.1, depth=3)
        attr.record_delegation("c3", "c4", tokens=100, cost=0.1, depth=4)
        report = attr.analyze()
        assert "过深" in report.bottleneck or report.max_depth > attr.max_depth

    def test_children_of(self):
        attr = ParentChildAttributor()
        attr.record_delegation("p1", "c1", tokens=100, cost=0.1)
        attr.record_delegation("p1", "c2", tokens=200, cost=0.2)
        attr.record_delegation("p2", "c3", tokens=300, cost=0.3)
        children = attr.children_of("p1")
        assert len(children) == 2
        assert all(c.parent_id == "p1" for c in children)

    def test_children_of_nonexistent(self):
        attr = ParentChildAttributor()
        assert attr.children_of("nonexistent") == []

    def test_chain_for(self):
        attr = ParentChildAttributor()
        attr.record_delegation("p1", "c1", tokens=100, cost=0.1)
        attr.record_delegation("p2", "c1", tokens=200, cost=0.2)
        chains = attr.chain_for("c1")
        assert len(chains) == 2

    def test_chain_for_nonexistent(self):
        attr = ParentChildAttributor()
        assert attr.chain_for("nonexistent") == []

    def test_clear(self):
        attr = ParentChildAttributor()
        attr.record_delegation("p1", "c1", tokens=100, cost=0.1)
        attr.clear()
        report = attr.analyze()
        assert report.chain_depth == 0
        assert attr.children_of("p1") == []


class TestBoundaryCases:
    def test_record_zero_tokens(self):
        attr = ParentChildAttributor()
        chain = attr.record_delegation("p", "c", tokens=0, cost=0.0)
        assert chain.tokens_delegated == 0

    def test_analyze_empty(self):
        attr = ParentChildAttributor()
        report = attr.analyze()
        assert report.bottleneck == "NONE"
        assert report.advice == "委托链健康"

    def test_over_delegation(self):
        attr = ParentChildAttributor(max_delegation=100)
        attr.record_delegation("p", "c", tokens=200, cost=0.1)
        report = attr.analyze()
        assert "200" in report.bottleneck or "超限" in report.advice
