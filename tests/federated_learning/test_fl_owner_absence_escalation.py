# [A_test] module_id: SRC-TST-0976 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_owner_absence_escalation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.owner_absence_escalation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_owner_absence_escalation.py
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.feedback_loop.actors.owner_absence_escalation import (
    AbsenceState,
    OwnerAbsenceEscalation,
)


class TestOwnerAbsenceEscalationInstantiation:
    def test_creates_with_defaults(self):
        escalation = OwnerAbsenceEscalation()
        assert escalation.state == AbsenceState.PRESENT
        assert escalation.auto_approved == 0
        assert escalation.pending_decisions == []


class TestOwnerAck:
    def test_ack_resets_state(self):
        escalation = OwnerAbsenceEscalation()
        escalation.state = AbsenceState.UNRESPONSIVE
        escalation.owner_ack()
        assert escalation.state == AbsenceState.PRESENT


class TestCheckAbsence:
    def test_present_within_warning_timeout(self):
        escalation = OwnerAbsenceEscalation(warning_timeout=300.0)
        escalation.last_ack = time.time()
        state = escalation.check_absence()
        assert state == AbsenceState.PRESENT

    def test_unresponsive_after_warning(self):
        escalation = OwnerAbsenceEscalation(warning_timeout=0.001, critical_timeout=10.0)
        escalation.last_ack = time.time() - 1.0
        state = escalation.check_absence()
        assert state == AbsenceState.UNRESPONSIVE

    def test_absent_after_critical_timeout(self):
        escalation = OwnerAbsenceEscalation(warning_timeout=0.001, critical_timeout=0.002)
        escalation.last_ack = time.time() - 1.0
        state = escalation.check_absence()
        assert state == AbsenceState.ABSENT


class TestSubmitDecision:
    def test_queues_when_owner_present(self):
        escalation = OwnerAbsenceEscalation()
        escalation.last_ack = time.time()
        result = escalation.submit_decision("d1", "low")
        assert result["action"] == "queued"

    def test_auto_approves_critical_when_absent(self):
        escalation = OwnerAbsenceEscalation(warning_timeout=0.001, critical_timeout=0.002)
        escalation.last_ack = time.time() - 1.0
        escalation.check_absence()
        result = escalation.submit_decision("d1", "critical")
        assert result["action"] == "auto_approved"
        assert escalation.auto_approved == 1

    def test_boundary_empty_decision_id(self):
        escalation = OwnerAbsenceEscalation()
        escalation.last_ack = time.time()
        result = escalation.submit_decision("", "low")
        assert result["decision"] == ""
