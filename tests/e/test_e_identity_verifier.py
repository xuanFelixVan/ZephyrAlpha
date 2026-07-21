# [A_test] module_id: MOD-GOV_e_identity_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_identity_verifier
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.identity_verifier import IdentityVerifier


class TestIdentityVerifierValidateSession:
    def test_valid_session(self):
        iv = IdentityVerifier()
        assert iv.validate_session("session-12345") is True

    def test_short_session(self):
        iv = IdentityVerifier()
        assert iv.validate_session("s12") is False

    def test_empty_session(self):
        iv = IdentityVerifier()
        assert iv.validate_session("") is False

    def test_none_session(self):
        iv = IdentityVerifier()
        assert iv.validate_session(None) is False

    def test_exactly_five_chars(self):
        iv = IdentityVerifier()
        assert iv.validate_session("abcde") is True


class TestIdentityVerifierVerify:
    def test_orchestrator_with_dispatch_task(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "orchestrator", "dispatch_task")
        assert ok is True
        assert msg == "OK"

    def test_orchestrator_with_invoke_gate(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "orchestrator", "invoke_gate")
        assert ok is True

    def test_orchestrator_lacks_scan_code(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "orchestrator", "scan_code")
        assert ok is False
        assert "lacks capability" in msg

    def test_script_engine_with_scan_code(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "script_engine", "scan_code")
        assert ok is True

    def test_human_owner_with_emergency_stop(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "human_owner", "emergency_stop")
        assert ok is True

    def test_unknown_role(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "session-00001", "unknown_role", "dispatch_task")
        assert ok is False
        assert "lacks capability" in msg

    def test_invalid_session(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "ab", "orchestrator", "dispatch_task")
        assert ok is False
        assert "session_id" in msg

    def test_empty_session(self):
        iv = IdentityVerifier()
        ok, msg = iv.verify("agent-1", "", "orchestrator", "dispatch_task")
        assert ok is False
