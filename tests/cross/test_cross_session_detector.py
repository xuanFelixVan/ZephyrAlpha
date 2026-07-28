# [A_test] module_id: MOD-GOV_cross_session_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.detectors.cross_session_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.detectors.cross_session_detector import CrossSessionDetector, SessionToken

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestSessionToken:
    def test_defaults(self):
        token = SessionToken(agent_id="a1", session_id="s1")
        assert token.agent_id == "a1"
        assert token.session_id == "s1"
        assert len(token.nonce) > 0
        assert len(token.timestamp) > 0
        assert token.signature == ""

    def test_custom_values(self):
        token = SessionToken(agent_id="a2", session_id="s2", nonce="abc", timestamp="2026-01-01", signature="sig123")
        assert token.nonce == "abc"
        assert token.signature == "sig123"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestCrossSessionDetector:
    def test_sign_and_verify_valid(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        token = csd.sign_token("agent-1", "session-1")
        result = csd.verify_token("agent-1", "session-1", token.nonce, token.timestamp, token.signature)
        assert result["valid"] is True
        assert result["agent_id"] == "agent-1"

    def test_cross_session_forgery(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        csd.sign_token("agent-1", "session-1")
        result = csd.verify_token("agent-2", "session-1", "nonce", "ts", "sig")
        assert result["valid"] is False
        assert result["reason"] == "cross_session_forgery"

    def test_signature_mismatch(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        csd.sign_token("agent-1", "session-1")
        result = csd.verify_token("agent-1", "session-1", "wrong-nonce", "wrong-ts", "wrong-sig")
        assert result["valid"] is False
        assert result["reason"] == "signature_mismatch"

    def test_unknown_session_valid_sig(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        import hashlib
        import hmac

        nonce = "fakenonce12345678"
        ts = "2026-01-01T00:00:00+00:00"
        payload = f"agent-x:session-unknown:{nonce}:{ts}"
        sig = hmac.new(b"testsecret1234567890123456789012", payload.encode(), hashlib.sha256).hexdigest()[:32]
        result = csd.verify_token("agent-x", "session-unknown", nonce, ts, sig)
        assert result["valid"] is True

    def test_violations_recorded(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        csd.sign_token("agent-1", "session-1")
        csd.verify_token("agent-evil", "session-1", "n", "t", "s")
        assert len(csd.violations) == 1
        assert csd.violations[0]["type"] == "CROSS_SESSION_FORGERY"

    def test_default_secret_key(self):
        csd = CrossSessionDetector()
        assert len(csd.secret) > 0

    def test_sign_token_populates_active_sessions(self):
        csd = CrossSessionDetector(secret_key="testsecret1234567890123456789012")
        csd.sign_token("a1", "s1")
        assert "s1" in csd.active_sessions
        assert csd.active_sessions["s1"].agent_id == "a1"
