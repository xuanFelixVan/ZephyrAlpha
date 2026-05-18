# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_voting
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Voting"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_voting import (
    A2AVoting,
    VoteAction,
    VotingResult,
)


def test_open_and_cast_vote():
    v = A2AVoting()
    v.open_proposal("prop-1")
    assert v.cast_vote("prop-1", "agent-a", VoteAction.APPROVE, weight=1.0)


def test_cast_vote_nonexistent_proposal():
    v = A2AVoting()
    assert not v.cast_vote("nonexistent", "agent-a", VoteAction.APPROVE)


def test_tally_approved():
    v = A2AVoting()
    v.open_proposal("prop-2")
    v.cast_vote("prop-2", "agent-a", VoteAction.APPROVE, weight=2.0)
    v.cast_vote("prop-2", "agent-b", VoteAction.APPROVE, weight=1.0)
    result = v.tally("prop-2", participant_count=3)
    assert isinstance(result, VotingResult)
    assert result.passed
    assert result.approve_weight == 3.0


def test_tally_rejected():
    v = A2AVoting()
    v.open_proposal("prop-3")
    v.cast_vote("prop-3", "agent-a", VoteAction.REJECT, weight=2.0)
    v.cast_vote("prop-3", "agent-b", VoteAction.APPROVE, weight=1.0)
    result = v.tally("prop-3", participant_count=3)
    assert not result.passed


def test_tally_quorum_not_met():
    v = A2AVoting(default_quorum=0.8)
    v.open_proposal("prop-4")
    v.cast_vote("prop-4", "agent-a", VoteAction.APPROVE, weight=1.0)
    result = v.tally("prop-4", participant_count=10)
    assert not result.quorum_met
    assert not result.passed


def test_tally_nonexistent():
    v = A2AVoting()
    result = v.tally("nonexistent", participant_count=1)
    assert result.proposal_id == "nonexistent"
