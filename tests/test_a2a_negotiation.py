# [A_test] module_id: SRC-TST-0244 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §
# [MODULE] tests.test_a2a_negotiation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_negotiation.py

import pytest
from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation import (
    NegotiationStatus,
    NegotiationResult,
    A2ANegotiation,
)


class TestA2ANegotiation:
    def test_create_default(self):
        neg = A2ANegotiation()
        assert neg._max_rounds == 5

    def test_create_custom(self):
        neg = A2ANegotiation(max_rounds=3, round_timeout=30.0)
        assert neg._max_rounds == 3

    def test_propose_accepted(self):
        neg = A2ANegotiation()
        result = neg.propose("agent-a", "agent-b", "resource-1", {"access": "read"})
        assert result.status == NegotiationStatus.ACCEPTED
        assert result.initiator == "agent-a"
        assert result.responder == "agent-b"

    def test_is_resolved_accepted(self):
        neg = A2ANegotiation()
        result = neg.propose("a", "b", "r", {"x": 1})
        assert A2ANegotiation.is_resolved(result) is True

    def test_is_resolved_proposed(self):
        result = NegotiationResult(
            initiator="a", responder="b",
            status=NegotiationStatus.PROPOSED,
        )
        assert A2ANegotiation.is_resolved(result) is False

    def test_needs_escalation_timeout(self):
        result = NegotiationResult(
            initiator="a", responder="b",
            status=NegotiationStatus.TIMEOUT,
        )
        assert A2ANegotiation.needs_escalation(result) is True

    def test_needs_escalation_accepted(self):
        result = NegotiationResult(
            initiator="a", responder="b",
            status=NegotiationStatus.ACCEPTED,
        )
        assert A2ANegotiation.needs_escalation(result) is False

    def test_needs_escalation_rejected(self):
        result = NegotiationResult(
            initiator="a", responder="b",
            status=NegotiationStatus.REJECTED,
        )
        assert A2ANegotiation.needs_escalation(result) is True

    def test_propose_returns_rounds(self):
        neg = A2ANegotiation()
        result = neg.propose("a", "b", "r", {"x": 1})
        assert result.rounds >= 1
