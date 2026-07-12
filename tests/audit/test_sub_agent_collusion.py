# [A_test] module_id: SRC-TST-1698 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_sub_agent_collusion
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.sub_agent_collusion
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_sub_agent_collusion.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.sub_agent_collusion import SubAgentCollusion, VotePair


class TestVotePair:
    def test_creation(self):
        vp = VotePair(from_agent="A", to_agent="B", action_id="act-1", vote="APPROVE")
        assert vp.from_agent == "A"
        assert vp.to_agent == "B"
        assert vp.action_id == "act-1"
        assert vp.vote == "APPROVE"

    def test_creation_reject(self):
        vp = VotePair(from_agent="C", to_agent="D", action_id="act-2", vote="REJECT")
        assert vp.vote == "REJECT"


class TestSubAgentCollusion:
    def test_instantiation_defaults(self):
        sac = SubAgentCollusion()
        assert sac.votes == []
        assert sac.collusion_threshold == 3

    def test_instantiation_custom_threshold(self):
        sac = SubAgentCollusion(collusion_threshold=5)
        assert sac.collusion_threshold == 5

    def test_record_vote(self):
        sac = SubAgentCollusion()
        sac.record("A", "B", "act-1", "APPROVE")
        assert len(sac.votes) == 1
        assert sac.votes[0].from_agent == "A"
        assert sac.votes[0].to_agent == "B"
        assert sac.votes[0].vote == "APPROVE"

    def test_record_multiple_votes(self):
        sac = SubAgentCollusion()
        sac.record("A", "B", "act-1", "APPROVE")
        sac.record("B", "A", "act-2", "APPROVE")
        sac.record("A", "C", "act-3", "REJECT")
        assert len(sac.votes) == 3

    def test_detect_ring_no_collusion(self):
        sac = SubAgentCollusion()
        sac.record("A", "B", "act-1", "APPROVE")
        sac.record("A", "B", "act-2", "APPROVE")
        rings = sac.detect_ring()
        assert len(rings) == 0

    def test_detect_ring_with_collusion(self):
        sac = SubAgentCollusion()
        for i in range(3):
            sac.record("A", "B", f"act-{i}", "APPROVE")
        rings = sac.detect_ring()
        assert "A->B" in rings
        assert len(rings) == 1

    def test_detect_ring_reciprocal_collusion(self):
        sac = SubAgentCollusion()
        for i in range(3):
            sac.record("A", "B", f"act-{i}", "APPROVE")
            sac.record("B", "A", f"act-{i + 10}", "APPROVE")
        rings = sac.detect_ring()
        assert "A->B" in rings
        assert "B->A" in rings
        assert len(rings) == 2

    def test_detect_ring_rejects_not_counted(self):
        sac = SubAgentCollusion()
        for i in range(5):
            sac.record("A", "B", f"act-{i}", "REJECT")
        rings = sac.detect_ring()
        assert len(rings) == 0

    def test_detect_ring_empty_votes(self):
        sac = SubAgentCollusion()
        rings = sac.detect_ring()
        assert rings == []

    def test_detect_ring_custom_threshold(self):
        sac = SubAgentCollusion(collusion_threshold=5)
        for i in range(4):
            sac.record("A", "B", f"act-{i}", "APPROVE")
        assert len(sac.detect_ring()) == 0
        sac.record("A", "B", "act-4", "APPROVE")
        assert len(sac.detect_ring()) == 1

    def test_detect_ring_mixed_votes(self):
        sac = SubAgentCollusion()
        sac.record("A", "B", "act-1", "APPROVE")
        sac.record("A", "B", "act-2", "REJECT")
        sac.record("A", "B", "act-3", "APPROVE")
        sac.record("A", "B", "act-4", "APPROVE")
        sac.record("A", "B", "act-5", "APPROVE")
        rings = sac.detect_ring()
        assert "A->B" in rings
