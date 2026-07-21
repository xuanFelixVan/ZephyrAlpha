# [A_test] module_id: MOD-GOV_decisions | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_decisions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""决策注册表测试."""

from __future__ import annotations

from zephyr.security.access_control.decision_registry import DecisionRegistry


class TestDecisions:
    def test_log_decision(self):
        registry = DecisionRegistry()
        record = registry.log("agent_1", "read", "config.yml", "ALLOWED", rule_id="R-001")
        assert record.agent_id == "agent_1"
        assert record.result == "ALLOWED"

    def test_query_by_agent(self):
        registry = DecisionRegistry()
        registry.log("agent_a", "read", "x", "ALLOWED")
        registry.log("agent_b", "write", "y", "DENIED")
        results = registry.query(agent_id="agent_a")
        assert len(results) == 1
        assert results[0].result == "ALLOWED"

    def test_stats(self):
        registry = DecisionRegistry()
        registry.log("a", "read", "x", "ALLOWED")
        registry.log("a", "write", "y", "DENIED")
        registry.log("b", "read", "z", "ALLOWED")

        stats = registry.stats()
        assert stats["total"] == 3
        assert stats["allowed"] == 2
        assert stats["denied"] == 1
