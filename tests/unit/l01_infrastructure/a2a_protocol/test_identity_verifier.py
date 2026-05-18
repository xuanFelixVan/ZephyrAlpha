# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_identity_verifier
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Identity Verifier"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery.identity_verifier import IdentityVerifier


class TestIdentityVerifier:
    def test_sign_and_verify(self):
        verifier = IdentityVerifier(b"test-secret")
        sig = verifier.sign("agent-x", {"action": "read"})
        assert verifier.verify("agent-x", {"action": "read"}, sig)

    def test_invalid_signature(self):
        verifier = IdentityVerifier(b"test-secret")
        assert not verifier.verify("agent-x", {"action": "read"}, "bad-signature")

    def test_challenge_generation(self):
        verifier = IdentityVerifier()
        challenge = verifier.generate_challenge()
        assert len(challenge) == 64
