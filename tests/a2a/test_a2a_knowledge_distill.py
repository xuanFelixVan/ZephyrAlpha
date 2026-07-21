# [A_test] module_id: MOD-GOV_a2a_knowledge_distill | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_knowledge_distill
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_knowledge_distill",
    reason="a2a_knowledge_distill module not available",
)


class TestA2AKnowledgeDistill:
    def test_instantiation(self):
        obj = mod.A2AKnowledgeDistill(max_insights_per_agent=10)
        assert obj is not None

    def test_distill(self):
        obj = mod.A2AKnowledgeDistill(max_insights_per_agent=10)
        result = obj.distill("agent1", "testing", "raw notes about testing", "engineering")
        assert result is not None

    def test_get_insights(self):
        obj = mod.A2AKnowledgeDistill(max_insights_per_agent=10)
        obj.distill("agent1", "testing", "notes", "engineering")
        insights = obj.get_insights("agent1")
        assert isinstance(insights, list)

    def test_get_insights_unknown_agent(self):
        obj = mod.A2AKnowledgeDistill(max_insights_per_agent=10)
        insights = obj.get_insights("unknown")
        assert isinstance(insights, list)

    def test_distill_empty_notes(self):
        obj = mod.A2AKnowledgeDistill(max_insights_per_agent=10)
        result = obj.distill("agent1", "topic", "", "category")
        assert result is not None


class TestDistilledKnowledge:
    def test_instantiation(self):
        dk = mod.DistilledKnowledge(source_agent="a1", topic="test", insight="insight_text")
        assert dk is not None
        assert dk.source_agent == "a1"
