# [A_test] module_id: MOD-GOV_a2a_voting | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_voting
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_voting.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting import (
    A2AVoting,
    VoteAction,
)


class TestA2AVoting:
    def test_create_default(self):
        v = A2AVoting()
        assert v.default_quorum == 0.5

    def test_open_proposal_and_cast_vote(self):
        v = A2AVoting()
        v.open_proposal("prop-1")
        result = v.cast_vote("prop-1", "agent-a", VoteAction.APPROVE, weight=1.0)
        assert result is True

    def test_cast_vote_nonexistent_proposal(self):
        v = A2AVoting()
        result = v.cast_vote("missing", "agent-a", VoteAction.APPROVE)
        assert result is False

    def test_tally_simple_majority(self):
        v = A2AVoting(default_quorum=0.5)
        v.open_proposal("prop-2")
        v.cast_vote("prop-2", "a1", VoteAction.APPROVE, 2.0)
        v.cast_vote("prop-2", "a2", VoteAction.APPROVE, 1.0)
        v.cast_vote("prop-2", "a3", VoteAction.REJECT, 1.0)
        result = v.tally("prop-2", participant_count=3)
        assert result.passed is True
        assert result.approve_weight == 3.0
        assert result.reject_weight == 1.0
        assert result.quorum_met is True

    def test_tally_rejected(self):
        v = A2AVoting(default_quorum=0.5)
        v.open_proposal("prop-3")
        v.cast_vote("prop-3", "a1", VoteAction.REJECT, 2.0)
        v.cast_vote("prop-3", "a2", VoteAction.APPROVE, 1.0)
        result = v.tally("prop-3", participant_count=2)
        assert result.passed is False

    def test_tally_quorum_not_met(self):
        v = A2AVoting(default_quorum=0.8)
        v.open_proposal("prop-4")
        v.cast_vote("prop-4", "a1", VoteAction.APPROVE, 1.0)
        result = v.tally("prop-4", participant_count=5)
        assert result.quorum_met is False
        assert result.passed is False

    def test_tally_nonexistent_proposal(self):
        v = A2AVoting()
        result = v.tally("missing", participant_count=1)
        assert result.total_weight == 0.0

    def test_abstain_vote(self):
        v = A2AVoting(default_quorum=0.5)
        v.open_proposal("prop-5")
        v.cast_vote("prop-5", "a1", VoteAction.APPROVE, 1.0)
        v.cast_vote("prop-5", "a2", VoteAction.ABSTAIN, 1.0)
        result = v.tally("prop-5", participant_count=2)
        assert result.abstain_weight == 1.0
        assert result.passed is True

    def test_custom_quorum(self):
        v = A2AVoting()
        v.open_proposal("prop-6", quorum_ratio=1.0)
        v.cast_vote("prop-6", "a1", VoteAction.APPROVE, 1.0)
        result = v.tally("prop-6", participant_count=2)
        assert result.quorum_met is False
