# [A_test] module_id: SRC-TST-0291 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §7
# [MODULE] tests.test_agent_signer
# [INVARIANTS] Ed25519 sign/verify roundtrip; signature hex format
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.agent_signer import AgentSigner


class TestAgentSignerGenerateKeyPair:
    def test_returns_tuple_of_two_hex_strings(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        assert isinstance(private_hex, str)
        assert isinstance(public_hex, str)
        assert len(private_hex) == 64
        assert len(public_hex) == 64
        bytes.fromhex(private_hex)
        bytes.fromhex(public_hex)

    def test_generates_unique_keys_each_call(self):
        pair1 = AgentSigner.generate_key_pair()
        pair2 = AgentSigner.generate_key_pair()
        assert pair1[0] != pair2[0]
        assert pair1[1] != pair2[1]


class TestAgentSignerSign:
    def test_sign_returns_hex_string(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        event = {"action": "test", "agent_id": "a1"}
        signature = AgentSigner.sign(event, private_hex)
        assert isinstance(signature, str)
        assert len(signature) == 128
        bytes.fromhex(signature)

    def test_sign_excludes_signature_field(self):
        private_hex, _ = AgentSigner.generate_key_pair()
        event_with_sig = {"action": "test", "signature": "old_sig"}
        event_without_sig = {"action": "test"}
        sig1 = AgentSigner.sign(event_with_sig, private_hex)
        sig2 = AgentSigner.sign(event_without_sig, private_hex)
        assert sig1 == sig2


class TestAgentSignerVerify:
    def test_verify_valid_signature(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        event = {"action": "write", "target": "file.py"}
        signature = AgentSigner.sign(event, private_hex)
        assert AgentSigner.verify(event, public_hex, signature) is True

    def test_verify_tampered_event_fails(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        event = {"action": "write", "target": "file.py"}
        signature = AgentSigner.sign(event, private_hex)
        tampered = {"action": "delete", "target": "file.py"}
        assert AgentSigner.verify(tampered, public_hex, signature) is False

    def test_verify_wrong_key_fails(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        _, other_public_hex = AgentSigner.generate_key_pair()
        event = {"action": "write"}
        signature = AgentSigner.sign(event, private_hex)
        assert AgentSigner.verify(event, other_public_hex, signature) is False

    def test_verify_invalid_hex_raises(self):
        _, public_hex = AgentSigner.generate_key_pair()
        with pytest.raises(ValueError):
            AgentSigner.verify({"a": 1}, public_hex, "not_valid_hex")


class TestAgentSignerRoundtrip:
    def test_sign_verify_roundtrip_complex_event(self):
        private_hex, public_hex = AgentSigner.generate_key_pair()
        event = {
            "agent_id": "agent-001",
            "action": "file_write",
            "target_path": "src/module.py",
            "timestamp": "2026-05-22T10:00:00Z",
            "metadata": {"key": "value"},
        }
        signature = AgentSigner.sign(event, private_hex)
        assert AgentSigner.verify(event, public_hex, signature) is True
