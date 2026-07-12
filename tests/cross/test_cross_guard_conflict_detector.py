# [A_test] module_id: SRC-TST-0645 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_cross_guard_conflict_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cross_guard_conflict_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_cross_guard_conflict_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.cross_guard_conflict_detector import (
    CrossGuardConflictDetector,
    GuardDecision,
)


class TestGuardDecision:
    def test_fields(self):
        gd = GuardDecision(guard_id="g1", decision="act", confidence=0.9)
        assert gd.guard_id == "g1"
        assert gd.decision == "act"
        assert gd.confidence == 0.9


class TestCrossGuardConflictDetectorInstantiation:
    def test_default_params(self):
        det = CrossGuardConflictDetector()
        assert det.decision_history == []
        assert det.max_history == 100
        assert det.conflict_threshold == 3.0

    def test_opposing_decisions_defined(self):
        assert ("act", "suppress") in CrossGuardConflictDetector.OPPOSING_DECISIONS
        assert ("suppress", "act") in CrossGuardConflictDetector.OPPOSING_DECISIONS
        assert ("upgrade", "downgrade") in CrossGuardConflictDetector.OPPOSING_DECISIONS
        assert ("enable", "disable") in CrossGuardConflictDetector.OPPOSING_DECISIONS
        assert ("alert", "silence") in CrossGuardConflictDetector.OPPOSING_DECISIONS


class TestCrossGuardConflictDetectorRecordDecisionBatch:
    def test_record_increases_history(self):
        det = CrossGuardConflictDetector()
        batch = [GuardDecision(guard_id="g1", decision="act", confidence=0.9)]
        det.record_decision_batch(batch)
        assert len(det.decision_history) == 1

    def test_record_trims_at_max(self):
        det = CrossGuardConflictDetector(max_history=3)
        for i in range(5):
            det.record_decision_batch([GuardDecision(guard_id=f"g{i}", decision="act", confidence=0.5)])
        assert len(det.decision_history) == 3

    def test_record_empty_batch(self):
        det = CrossGuardConflictDetector()
        det.record_decision_batch([])
        assert len(det.decision_history) == 1


class TestCrossGuardConflictDetectorDetectConflicts:
    def test_no_conflicts_empty_history(self):
        det = CrossGuardConflictDetector()
        result = det.detect_conflicts()
        assert result["conflicts"] == []
        assert result["conflict_matrix"] == {}

    def test_no_conflicts_agreeing_guards(self):
        det = CrossGuardConflictDetector()
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="act", confidence=0.8),
        ]
        for _ in range(5):
            det.record_decision_batch(batch)
        result = det.detect_conflicts()
        assert len(result["conflicts"]) == 0

    def test_detects_opposing_decisions(self):
        det = CrossGuardConflictDetector(conflict_threshold=2.0)
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="suppress", confidence=0.8),
        ]
        for _ in range(3):
            det.record_decision_batch(batch)
        result = det.detect_conflicts()
        assert len(result["conflicts"]) > 0

    def test_conflict_matrix_contains_severity(self):
        det = CrossGuardConflictDetector(conflict_threshold=2.0)
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="suppress", confidence=0.8),
        ]
        for _ in range(5):
            det.record_decision_batch(batch)
        result = det.detect_conflicts()
        for conflict_data in result["conflict_matrix"].values():
            assert "severity" in conflict_data
            assert "conflict_count" in conflict_data


class TestCrossGuardConflictDetectorGetTopConflicts:
    def test_get_top_conflicts_default_n(self):
        det = CrossGuardConflictDetector(conflict_threshold=2.0)
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="suppress", confidence=0.8),
        ]
        for _ in range(5):
            det.record_decision_batch(batch)
        top = det.get_top_conflicts()
        assert isinstance(top, list)
        assert len(top) <= 5

    def test_get_top_conflicts_custom_n(self):
        det = CrossGuardConflictDetector(conflict_threshold=2.0)
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="suppress", confidence=0.8),
        ]
        for _ in range(5):
            det.record_decision_batch(batch)
        top = det.get_top_conflicts(n=1)
        assert len(top) <= 1

    def test_get_top_conflicts_empty(self):
        det = CrossGuardConflictDetector()
        top = det.get_top_conflicts()
        assert top == []


class TestCrossGuardConflictDetectorBoundary:
    def test_single_guard_no_conflict(self):
        det = CrossGuardConflictDetector()
        det.record_decision_batch([GuardDecision(guard_id="g1", decision="act", confidence=0.9)])
        result = det.detect_conflicts()
        assert result["conflicts"] == []

    def test_non_opposing_different_decisions(self):
        det = CrossGuardConflictDetector()
        batch = [
            GuardDecision(guard_id="g1", decision="act", confidence=0.9),
            GuardDecision(guard_id="g2", decision="alert", confidence=0.8),
        ]
        det.record_decision_batch(batch)
        result = det.detect_conflicts()
        assert ("act", "alert") not in CrossGuardConflictDetector.OPPOSING_DECISIONS
