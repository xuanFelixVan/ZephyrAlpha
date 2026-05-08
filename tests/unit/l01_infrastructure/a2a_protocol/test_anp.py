"""测试: ANP Frame Negotiation"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_frame_negotiation import (
    A2AFrameNegotiation,
    FrameOffer,
    NegotiatedFrame,
)


def test_negotiate_compatible_agents():
    fn = A2AFrameNegotiation()
    offer_a = FrameOffer(agent_id="agent-a", protocol_version="0.10.0", frame_format="json")
    offer_b = FrameOffer(agent_id="agent-b", protocol_version="0.10.0", frame_format="json")
    result = fn.negotiate(offer_a, offer_b)
    assert isinstance(result, NegotiatedFrame)
    assert result.negotiation_successful
    assert result.protocol_version == "0.10.0"
    assert result.frame_format == "json"


def test_negotiate_incompatible_versions():
    fn = A2AFrameNegotiation(supported_versions=["0.10.0"])
    offer_a = FrameOffer(agent_id="agent-a", protocol_version="0.8.0")
    offer_b = FrameOffer(agent_id="agent-b", protocol_version="0.8.0")
    result = fn.negotiate(offer_a, offer_b)
    assert not result.negotiation_successful
    assert result.protocol_version == ""


def test_negotiate_capability_intersection():
    fn = A2AFrameNegotiation()
    offer_a = FrameOffer(agent_id="agent-a", supported_capabilities=["read", "write"])
    offer_b = FrameOffer(agent_id="agent-b", supported_capabilities=["write", "search"])
    result = fn.negotiate(offer_a, offer_b)
    assert "write" in result.agreed_capabilities
    assert "read" not in result.agreed_capabilities


def test_negotiate_max_message_size():
    fn = A2AFrameNegotiation()
    offer_a = FrameOffer(agent_id="agent-a", max_message_size=500_000)
    offer_b = FrameOffer(agent_id="agent-b", max_message_size=1_000_000)
    result = fn.negotiate(offer_a, offer_b)
    assert result.max_message_size == 500_000


def test_negotiate_compression():
    fn = A2AFrameNegotiation(supported_compressions=["none", "gzip", "zstd"])
    offer_a = FrameOffer(agent_id="agent-a", compression="gzip")
    offer_b = FrameOffer(agent_id="agent-b", compression="gzip")
    result = fn.negotiate(offer_a, offer_b)
    assert result.compression == "gzip"
