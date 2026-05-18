# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_debate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Debate"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_debate import (
    A2ADebate,
    DebateResult,
    DebatePhase,
)


def test_debate_basic():
    d = A2ADebate()
    result = d.debate("agent-a", "agent-b", "use_redis_vs_postgres", "Redis is faster", "Postgres is more reliable")
    assert isinstance(result, DebateResult)
    assert result.agent_a_id == "agent-a"
    assert result.agent_b_id == "agent-b"
    assert result.topic == "use_redis_vs_postgres"
    assert len(result.rounds) == 3


def test_debate_has_claim_round():
    d = A2ADebate()
    result = d.debate("a", "b", "topic", "claim_a", "claim_b")
    assert result.rounds[0].phase == DebatePhase.CLAIM
    assert result.rounds[0].agent_a_statement == "claim_a"
    assert result.rounds[0].agent_b_statement == "claim_b"


def test_debate_has_rebuttal_round():
    d = A2ADebate()
    result = d.debate("a", "b", "topic", "claim_a", "claim_b")
    assert result.rounds[1].phase == DebatePhase.REBUTTAL


def test_debate_has_synthesis_round():
    d = A2ADebate()
    result = d.debate("a", "b", "topic", "claim_a", "claim_b")
    assert result.rounds[2].phase == DebatePhase.SYNTHESIS
    assert result.synthesis != ""
    assert result.consensus != ""
