# [A_test] module_id: SRC-TST-1301 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-409 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_multi_model_consensus
# [INVARIANTS] ConsensusProtocol has 3 values; DebateRound has 3 rounds; escalate_to_owner returns ESCALATED prefix
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_multi_model_consensus.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.multi_model_consensus import (
    ConsensusProtocol,
    DebateRound,
    escalate_to_owner,
)


class TestConsensusProtocol:
    def test_all_protocols(self):
        expected = {"Majority", "Weighted", "Unanimous"}
        actual = {p.value for p in ConsensusProtocol}
        assert actual == expected

    def test_protocol_count(self):
        assert len(ConsensusProtocol) == 3


class TestDebateRound:
    def test_all_rounds(self):
        expected = {"R1_模型A解答", "R2_模型B挑战", "R3_模型A反驳"}
        actual = {r.value for r in DebateRound}
        assert actual == expected

    def test_round_count(self):
        assert len(DebateRound) == 3


class TestEscalateToOwner:
    def test_returns_escalated_prefix(self):
        result = escalate_to_owner("disagreement")
        assert result.startswith("ESCALATED:")

    def test_includes_reason(self):
        result = escalate_to_owner("model conflict")
        assert "model conflict" in result

    def test_includes_owner(self):
        result = escalate_to_owner("test")
        assert "Owner" in result


class TestBoundary:
    def test_escalate_empty_reason(self):
        result = escalate_to_owner("")
        assert "ESCALATED:" in result

    def test_escalate_long_reason(self):
        reason = "x" * 1000
        result = escalate_to_owner(reason)
        assert reason in result
