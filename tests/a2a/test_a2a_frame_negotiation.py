# [A_test] module_id: MOD-GOV_a2a_frame_negotiation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_frame_negotiation
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_frame_negotiation",
    reason="a2a_frame_negotiation module not available",
)


class TestA2AFrameNegotiation:
    def test_instantiation(self):
        obj = mod.A2AFrameNegotiation(
            supported_versions=["1.0", "2.0"],
            supported_formats=["json", "xml"],
            supported_compressions=["gzip", "none"],
        )
        assert obj is not None

    def test_negotiate(self):
        obj = mod.A2AFrameNegotiation(
            supported_versions=["1.0", "2.0"],
            supported_formats=["json", "xml"],
            supported_compressions=["gzip"],
        )
        offer_a = mod.FrameOffer(agent_id="a1")
        offer_b = mod.FrameOffer(agent_id="a2")
        result = obj.negotiate(offer_a, offer_b)
        assert result is not None

    def test_negotiate_returns_frame(self):
        obj = mod.A2AFrameNegotiation(
            supported_versions=["1.0"],
            supported_formats=["json"],
            supported_compressions=["none"],
        )
        result = obj.negotiate(mod.FrameOffer(agent_id="a1"), mod.FrameOffer(agent_id="a2"))
        assert isinstance(result, mod.NegotiatedFrame)

    def test_empty_supported(self):
        obj = mod.A2AFrameNegotiation(
            supported_versions=[],
            supported_formats=[],
            supported_compressions=[],
        )
        result = obj.negotiate(mod.FrameOffer(agent_id="a1"), mod.FrameOffer(agent_id="a2"))
        assert result is not None
