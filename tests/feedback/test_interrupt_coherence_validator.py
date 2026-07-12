# [A_test] module_id: SRC-TST-1148 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_interrupt_coherence_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.interrupt_coherence_validator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_interrupt_coherence_validator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.interrupt_coherence_validator import (
    CoherenceStatus,
    InterruptCoherenceValidator,
)


class TestCoherenceStatus:
    def test_enum_values(self):
        assert CoherenceStatus.COHERENT.value == "coherent"
        assert CoherenceStatus.PARTIALLY_DIRTY.value == "partially_dirty"
        assert CoherenceStatus.INCOHERENT.value == "incoherent"


class TestInterruptCoherenceValidator:
    def test_instantiation_defaults(self):
        icv = InterruptCoherenceValidator()
        assert icv.known_locks == set()
        assert icv.known_actions_in_flight == set()
        assert icv.known_references == set()
        assert icv.coherence_checks == []
        assert icv.max_checks == 50

    def test_register_and_release_lock(self):
        icv = InterruptCoherenceValidator()
        icv.register_lock("lock-1")
        assert "lock-1" in icv.known_locks
        icv.mark_lock_released("lock-1")
        assert "lock-1" not in icv.known_locks

    def test_register_and_complete_action(self):
        icv = InterruptCoherenceValidator()
        icv.register_action_in_flight("action-1")
        assert "action-1" in icv.known_actions_in_flight
        icv.mark_action_completed("action-1")
        assert "action-1" not in icv.known_actions_in_flight

    def test_register_reference(self):
        icv = InterruptCoherenceValidator()
        icv.register_reference("ref-1")
        assert "ref-1" in icv.known_references

    def test_validate_coherence_clean(self):
        icv = InterruptCoherenceValidator()
        result = icv.validate_coherence()
        assert result["status"] == CoherenceStatus.COHERENT.value
        assert result["coherent"] is True
        assert result["orphaned_locks"] == 0
        assert result["half_applied_actions"] == 0

    def test_validate_coherence_orphaned_locks(self):
        icv = InterruptCoherenceValidator()
        icv.register_lock("lock-1")
        result = icv.validate_coherence()
        assert result["status"] == CoherenceStatus.PARTIALLY_DIRTY.value
        assert result["orphaned_locks"] == 1
        assert any("orphaned locks" in issue for issue in result["issues"])

    def test_validate_coherence_half_applied_actions(self):
        icv = InterruptCoherenceValidator()
        icv.register_action_in_flight("action-1")
        result = icv.validate_coherence()
        assert result["status"] == CoherenceStatus.PARTIALLY_DIRTY.value
        assert result["half_applied_actions"] == 1

    def test_validate_coherence_multiple_issues(self):
        icv = InterruptCoherenceValidator()
        icv.register_lock("lock-1")
        icv.register_lock("lock-2")
        icv.register_action_in_flight("action-1")
        result = icv.validate_coherence()
        assert result["status"] == CoherenceStatus.PARTIALLY_DIRTY.value
        assert len(result["issues"]) == 2

    def test_auto_repair(self):
        icv = InterruptCoherenceValidator()
        icv.register_lock("lock-1")
        icv.register_action_in_flight("action-1")
        result = icv.auto_repair()
        assert result["repaired"] is True
        assert result["coherent_now"] is True
        assert result["details"]["locks_cleared"] == 1
        assert result["details"]["actions_marked_failed"] == 1

    def test_auto_repair_no_issues(self):
        icv = InterruptCoherenceValidator()
        result = icv.auto_repair()
        assert result["repaired"] is False
        assert result["coherent_now"] is True

    def test_get_coherence_history(self):
        icv = InterruptCoherenceValidator()
        icv.validate_coherence()
        icv.register_lock("lock-1")
        icv.validate_coherence()
        history = icv.get_coherence_history()
        assert len(history) == 1
        assert history[0]["coherent"] is False

    def test_max_checks_truncation(self):
        icv = InterruptCoherenceValidator(max_checks=5)
        for i in range(10):
            icv.validate_coherence()
        assert len(icv.coherence_checks) <= 5

    def test_release_nonexistent_lock(self):
        icv = InterruptCoherenceValidator()
        icv.mark_lock_released("nonexistent")
        assert len(icv.known_locks) == 0

    def test_complete_nonexistent_action(self):
        icv = InterruptCoherenceValidator()
        icv.mark_action_completed("nonexistent")
        assert len(icv.known_actions_in_flight) == 0
