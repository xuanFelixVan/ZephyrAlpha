# [A_test] module_id: SRC-TST-1351 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_owner_absence_escalation
# [INVARIANTS] owner_ack resets state to PRESENT; critical+ABSENT triggers auto_approved
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.feedback_loop.actors.owner_absence_escalation import (
    AbsenceState,
    OwnerAbsenceEscalation,
)


class TestAbsenceState:
    def test_enum_values(self):
        assert AbsenceState.PRESENT == "PRESENT"
        assert AbsenceState.UNRESPONSIVE == "UNRESPONSIVE"
        assert AbsenceState.ABSENT == "ABSENT"


class TestOwnerAbsenceEscalationInstantiation:
    def test_default_construction(self):
        oae = OwnerAbsenceEscalation()
        assert oae.state == AbsenceState.PRESENT
        assert oae.warning_timeout == 300.0
        assert oae.critical_timeout == 900.0
        assert oae.max_queue_age == 3600.0
        assert oae.pending_decisions == []
        assert oae.auto_approved == 0

    def test_custom_timeouts(self):
        oae = OwnerAbsenceEscalation(warning_timeout=60.0, critical_timeout=120.0)
        assert oae.warning_timeout == 60.0
        assert oae.critical_timeout == 120.0


class TestOwnerAck:
    def test_ack_resets_state(self):
        oae = OwnerAbsenceEscalation()
        oae.state = AbsenceState.ABSENT
        oae.owner_ack()
        assert oae.state == AbsenceState.PRESENT

    def test_ack_updates_last_ack(self):
        oae = OwnerAbsenceEscalation()
        before = oae.last_ack
        oae.owner_ack()
        assert oae.last_ack >= before


class TestCheckAbsence:
    def test_present_within_warning_timeout(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time()
        assert oae.check_absence() == AbsenceState.PRESENT

    def test_unresponsive_after_warning_timeout(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time() - oae.warning_timeout - 1
        assert oae.check_absence() == AbsenceState.UNRESPONSIVE

    def test_absent_after_critical_timeout(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time() - oae.critical_timeout - 1
        assert oae.check_absence() == AbsenceState.ABSENT


class TestSubmitDecision:
    def test_queues_when_owner_present(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time()
        result = oae.submit_decision("dec-1", "low")
        assert result["action"] == "queued"
        assert result["decision"] == "dec-1"
        assert len(oae.pending_decisions) == 1

    def test_auto_approves_critical_when_absent(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time() - oae.critical_timeout - 1
        oae.check_absence()
        result = oae.submit_decision("dec-urgent", "critical")
        assert result["action"] == "auto_approved"
        assert result["reason"] == "owner_absent"
        assert oae.auto_approved == 1

    def test_non_critical_queues_even_when_absent(self):
        oae = OwnerAbsenceEscalation()
        oae.last_ack = time.time() - oae.critical_timeout - 1
        oae.check_absence()
        result = oae.submit_decision("dec-low", "low")
        assert result["action"] == "queued"

    def test_prune_stale_decisions(self):
        oae = OwnerAbsenceEscalation()
        stale_time = time.time() - oae.max_queue_age - 1
        oae.pending_decisions.append({"id": "stale", "urgency": "low", "submitted_at": stale_time})
        oae.submit_decision("fresh", "low")
        ids = [d["id"] for d in oae.pending_decisions]
        assert "stale" not in ids
        assert "fresh" in ids
