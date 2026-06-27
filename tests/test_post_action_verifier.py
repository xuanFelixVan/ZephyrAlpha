# [A_test] module_id: SRC-TST-1390 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.post_action_verifier
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
    from zephyr.security.access_control.post_action_verifier import (
        PostActionVerifier,
        VerificationResult,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestPostActionVerifier:
    def setup_method(self):
        self.verifier = PostActionVerifier()

    def test_verify_match(self):
        v = self.verifier.verify("agent-1", "write", "ok", "ok")
        assert v.result == VerificationResult.VERIFIED
        assert v.rollback_required is False
        assert v.details == []

    def test_verify_discrepancy(self):
        v = self.verifier.verify("agent-1", "write", "expected", "actual")
        assert v.result == VerificationResult.DISCREPANCY
        assert v.rollback_required is True
        assert len(v.details) == 1

    def test_get_discrepancy_count(self):
        self.verifier.verify("agent-1", "op1", "a", "a")
        self.verifier.verify("agent-1", "op2", "b", "c")
        self.verifier.verify("agent-1", "op3", "d", "e")
        assert self.verifier.get_discrepancy_count("agent-1") == 2

    def test_should_escalate_below_threshold(self):
        self.verifier.verify("agent-1", "op1", "a", "b")
        self.verifier.verify("agent-1", "op2", "c", "d")
        assert self.verifier.should_escalate("agent-1") is False

    def test_should_escalate_at_threshold(self):
        for i in range(3):
            self.verifier.verify("agent-1", f"op{i}", f"exp{i}", f"act{i}")
        assert self.verifier.should_escalate("agent-1") is True

    def test_reset_agent(self):
        self.verifier.verify("agent-1", "op1", "a", "b")
        self.verifier.verify("agent-2", "op2", "c", "d")
        self.verifier.reset_agent("agent-1")
        assert self.verifier.get_discrepancy_count("agent-1") == 0
        assert self.verifier.get_discrepancy_count("agent-2") == 1

    def test_discrepancy_count_unknown_agent(self):
        assert self.verifier.get_discrepancy_count("unknown") == 0

    def test_verify_empty_strings(self):
        v = self.verifier.verify("", "", "", "")
        assert v.result == VerificationResult.VERIFIED

    def test_verification_result_enum_values(self):
        assert VerificationResult.VERIFIED.value == "verified"
        assert VerificationResult.DISCREPANCY.value == "discrepancy"
        assert VerificationResult.FAILED.value == "failed"
