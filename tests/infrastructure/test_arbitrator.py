# [A_test] module_id: MOD-GOV_arbitrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_arbitrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_arbitrator.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
    AgentMeta,
    AgentRole,
    Arbitrator,
    FileOwnership,
)


class TestAgentRole:
    def test_from_string_superadmin(self):
        assert AgentRole.from_string("superadmin") == AgentRole.SUPERADMIN

    def test_from_string_safety_operator(self):
        assert AgentRole.from_string("safety_operator") == AgentRole.SAFETY_OPERATOR

    def test_from_string_unknown_defaults_builder(self):
        assert AgentRole.from_string("unknown_role") == AgentRole.BUILDER

    def test_from_string_with_hyphens(self):
        assert AgentRole.from_string("safety-operator") == AgentRole.SAFETY_OPERATOR

    def test_role_ordering(self):
        assert AgentRole.SUPERADMIN > AgentRole.SAFETY_OPERATOR
        assert AgentRole.BUILDER > AgentRole.OBSERVER


class TestArbitrator:
    def test_tier1_priority_superadmin_vs_builder(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="sa", role=AgentRole.SUPERADMIN)
        b = AgentMeta(agent_id="bu", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["some/file.py"])
        assert result.winner == "sa"
        assert result.tier == 1
        assert result.escalation is False

    def test_tier1_priority_equal_roles(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="b1", role=AgentRole.BUILDER, tasks_completed=20)
        b = AgentMeta(agent_id="b2", role=AgentRole.BUILDER, tasks_completed=5)
        result = arb.arbitrate(a, b, ["some/file.py"])
        assert result.winner == "b1"
        assert result.tier == 1

    def test_tier2_ownership(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="so", role=AgentRole.SITE_OWNER)
        b = AgentMeta(agent_id="bu", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["scripts/deploy.py"])
        assert result.tier == 2
        assert result.winner == "so"

    def test_tier3_escalation(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="b1", role=AgentRole.BUILDER, tasks_completed=5)
        b = AgentMeta(agent_id="b2", role=AgentRole.BUILDER, tasks_completed=5)
        result = arb.arbitrate(a, b, ["src/some/file.py"])
        assert result.tier == 3
        assert result.escalation is True
        assert result.winner is None

    def test_custom_ownership_rules(self):
        custom = [FileOwnership("custom/", AgentRole.REVIEWER, "custom area")]
        arb = Arbitrator(ownership_rules=custom)
        a = AgentMeta(agent_id="rev", role=AgentRole.REVIEWER)
        b = AgentMeta(agent_id="bu", role=AgentRole.BUILDER)
        result = arb.arbitrate(a, b, ["custom/file.py"])
        assert result.winner == "rev"

    def test_owned_files_advantage(self):
        arb = Arbitrator()
        a = AgentMeta(agent_id="b1", role=AgentRole.BUILDER, owned_files=["src/my_module.py"])
        b = AgentMeta(agent_id="b2", role=AgentRole.BUILDER, tasks_completed=5)
        result = arb.arbitrate(a, b, ["src/my_module.py"])
        assert result.winner == "b1"
