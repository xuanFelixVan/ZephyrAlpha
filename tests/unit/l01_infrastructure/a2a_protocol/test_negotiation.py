"""测试: Negotiation"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_negotiation import (
    A2ANegotiation,
    NegotiationResult,
    NegotiationStatus,
)


def test_propose_accepted():
    n = A2ANegotiation()
    result = n.propose("agent-a", "agent-b", "file_lock", {"duration": 60})
    assert isinstance(result, NegotiationResult)
    assert result.initiator == "agent-a"
    assert result.responder == "agent-b"
    assert result.status == NegotiationStatus.ACCEPTED


def test_is_resolved():
    n = A2ANegotiation()
    result = n.propose("agent-a", "agent-b", "resource", {"key": "val"})
    assert A2ANegotiation.is_resolved(result)


def test_needs_escalation_on_rejected():
    rejected = NegotiationResult(
        initiator="a", responder="b",
        status=NegotiationStatus.REJECTED,
    )
    assert A2ANegotiation.needs_escalation(rejected)


def test_needs_escalation_on_timeout():
    timeout = NegotiationResult(
        initiator="a", responder="b",
        status=NegotiationStatus.TIMEOUT,
    )
    assert A2ANegotiation.needs_escalation(timeout)


def test_propose_with_terms():
    n = A2ANegotiation()
    result = n.propose("agent-a", "agent-b", "db_table", {"mode": "exclusive", "duration": 120})
    assert result.final_terms is not None
