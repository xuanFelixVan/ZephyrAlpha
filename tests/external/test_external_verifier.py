# [A_test] module_id: SRC-TST-0886 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_external_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.external_verifier
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_external_verifier.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.external_verifier import (
    ExternalAudit,
    ExternalVerifier,
    Verdict,
)


class TestVerdict:
    def test_enum_values(self):
        assert Verdict.CONCUR.value == "CONCUR"
        assert Verdict.DISSENT.value == "DISSENT"
        assert Verdict.ABSTAIN.value == "ABSTAIN"


class TestExternalAudit:
    def test_creation(self):
        audit = ExternalAudit(audit_id="a1", fle_decision="repair", external_verdict=Verdict.CONCUR, reasoning="ok")
        assert audit.audit_id == "a1"
        assert audit.external_verdict is Verdict.CONCUR
        assert isinstance(audit.timestamp, float)

    def test_creation_with_timestamp(self):
        audit = ExternalAudit(
            audit_id="a2", fle_decision="skip", external_verdict=Verdict.DISSENT, reasoning="bad", timestamp=1000.0
        )
        assert audit.timestamp == 1000.0


class TestExternalVerifier:
    def test_instantiation_defaults(self):
        ev = ExternalVerifier()
        assert ev.verdicts == []
        assert ev.dissent_threshold == 3
        assert ev.consecutive_dissents == 0

    def test_verify_high_confidence_concur(self):
        ev = ExternalVerifier()
        verdict = ev.verify("a1", "repair", {"confidence": 0.9})
        assert verdict is Verdict.CONCUR
        assert ev.consecutive_dissents == 0

    def test_verify_low_confidence_dissent(self):
        ev = ExternalVerifier()
        verdict = ev.verify("a1", "repair", {"confidence": 0.3})
        assert verdict is Verdict.DISSENT
        assert ev.consecutive_dissents == 1

    def test_verify_no_confidence_dissent(self):
        ev = ExternalVerifier()
        verdict = ev.verify("a1", "repair", {})
        assert verdict is Verdict.DISSENT

    def test_verify_threshold_boundary(self):
        ev = ExternalVerifier()
        verdict = ev.verify("a1", "repair", {"confidence": 0.7})
        assert verdict is Verdict.DISSENT
        verdict2 = ev.verify("a2", "repair", {"confidence": 0.71})
        assert verdict2 is Verdict.CONCUR

    def test_consecutive_dissents_reset_on_concur(self):
        ev = ExternalVerifier()
        ev.verify("a1", "repair", {"confidence": 0.3})
        ev.verify("a2", "repair", {"confidence": 0.3})
        assert ev.consecutive_dissents == 2
        ev.verify("a3", "repair", {"confidence": 0.9})
        assert ev.consecutive_dissents == 0

    def test_should_lockdown_false(self):
        ev = ExternalVerifier()
        ev.verify("a1", "repair", {"confidence": 0.3})
        ev.verify("a2", "repair", {"confidence": 0.3})
        assert ev.should_lockdown is False

    def test_should_lockdown_true(self):
        ev = ExternalVerifier()
        for i in range(3):
            ev.verify(f"a{i}", "repair", {"confidence": 0.1})
        assert ev.should_lockdown is True

    def test_should_lockdown_resets_after_concur(self):
        ev = ExternalVerifier()
        for i in range(3):
            ev.verify(f"a{i}", "repair", {"confidence": 0.1})
        assert ev.should_lockdown is True
        ev.verify("a99", "repair", {"confidence": 0.9})
        assert ev.should_lockdown is False

    def test_verdicts_recorded(self):
        ev = ExternalVerifier()
        ev.verify("a1", "repair", {"confidence": 0.9})
        ev.verify("a2", "skip", {"confidence": 0.3})
        assert len(ev.verdicts) == 2
        assert ev.verdicts[0].external_verdict is Verdict.CONCUR
        assert ev.verdicts[1].external_verdict is Verdict.DISSENT

    def test_custom_dissent_threshold(self):
        ev = ExternalVerifier(dissent_threshold=5)
        for i in range(4):
            ev.verify(f"a{i}", "repair", {"confidence": 0.1})
        assert ev.should_lockdown is False
        ev.verify("a4", "repair", {"confidence": 0.1})
        assert ev.should_lockdown is True
