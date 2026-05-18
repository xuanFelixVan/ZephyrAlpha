# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_arbitrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Arbitrator"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
    Arbitrator,
    AgentMeta,
    AgentRole,
    ArbitrationResult,
)


def test_tier1_priority_superadmin_wins():
    a = Arbitrator()
    agent_a = AgentMeta(agent_id="admin-1", role=AgentRole.SUPERADMIN)
    agent_b = AgentMeta(agent_id="builder-1", role=AgentRole.BUILDER)
    result = a.arbitrate(agent_a, agent_b, ["src/main.py"])
    assert isinstance(result, ArbitrationResult)
    assert result.winner == "admin-1"
    assert result.tier == 1
    assert "priority" in result.reason.lower() or "Role" in result.reason


def test_tier1_priority_safety_operator_wins():
    a = Arbitrator()
    agent_a = AgentMeta(agent_id="safety-1", role=AgentRole.SAFETY_OPERATOR)
    agent_b = AgentMeta(agent_id="builder-1", role=AgentRole.BUILDER)
    result = a.arbitrate(agent_a, agent_b, ["src/main.py"])
    assert result.winner == "safety-1"
    assert result.tier == 1


def test_tier2_ownership():
    a = Arbitrator()
    agent_a = AgentMeta(agent_id="gov-1", role=AgentRole.GOVERNANCE)
    agent_b = AgentMeta(agent_id="builder-1", role=AgentRole.BUILDER)
    result = a.arbitrate(agent_a, agent_b, ["docs/03_modules/some_blueprint.md"])
    assert result.winner is not None
    assert result.tier in (1, 2)


def test_tier3_escalation_equal_roles():
    a = Arbitrator()
    agent_a = AgentMeta(agent_id="builder-1", role=AgentRole.BUILDER, tasks_completed=3)
    agent_b = AgentMeta(agent_id="builder-2", role=AgentRole.BUILDER, tasks_completed=3)
    result = a.arbitrate(agent_a, agent_b, ["src/new_file.py"])
    assert result.escalation
    assert result.tier == 3


def test_seniority_tiebreaker():
    a = Arbitrator()
    agent_a = AgentMeta(agent_id="builder-1", role=AgentRole.BUILDER, tasks_completed=20)
    agent_b = AgentMeta(agent_id="builder-2", role=AgentRole.BUILDER, tasks_completed=3)
    result = a.arbitrate(agent_a, agent_b, ["src/main.py"])
    assert result.winner == "builder-1"
    assert result.tier == 1


def test_from_string():
    assert AgentRole.from_string("superadmin") == AgentRole.SUPERADMIN
    assert AgentRole.from_string("builder") == AgentRole.BUILDER
    assert AgentRole.from_string("unknown_role") == AgentRole.BUILDER
