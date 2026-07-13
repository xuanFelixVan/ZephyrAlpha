# [A_test] module_id: SRC-TST-1081 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_guard_cascade_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_guard_cascade_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.guard_cascade_detector import (
    GuardCascadeDetector,
    GuardTriggerEvent,
)


class TestGuardTriggerEvent:
    def test_creation_with_defaults(self):
        evt = GuardTriggerEvent(guard_id="G1", triggered_by=None, timestamp=0.0)
        assert evt.guard_id == "G1"
        assert evt.triggered_by is None
        assert evt.timestamp == 0.0

    def test_creation_with_triggered_by(self):
        evt = GuardTriggerEvent(guard_id="G2", triggered_by="G1", timestamp=1.5)
        assert evt.triggered_by == "G1"
        assert evt.timestamp == 1.5


class TestGuardCascadeDetector:
    def test_default_construction(self):
        det = GuardCascadeDetector()
        assert det.trigger_history == []
        assert det.max_history == 300
        assert det.cascade_depth_threshold == 4
        assert det.cascade_window_seconds == 5.0
        assert det.suppressed_guards == set()

    def test_custom_construction(self):
        det = GuardCascadeDetector(
            max_history=50,
            cascade_depth_threshold=2,
            cascade_window_seconds=10.0,
        )
        assert det.max_history == 50
        assert det.cascade_depth_threshold == 2
        assert det.cascade_window_seconds == 10.0

    def test_record_trigger_appends_event(self):
        det = GuardCascadeDetector()
        det.record_trigger("G1")
        assert len(det.trigger_history) == 1
        assert det.trigger_history[0].guard_id == "G1"
        assert det.trigger_history[0].triggered_by is None

    def test_record_trigger_with_triggered_by(self):
        det = GuardCascadeDetector()
        det.record_trigger("G2", triggered_by="G1")
        assert det.trigger_history[0].triggered_by == "G1"

    def test_record_trigger_trims_history(self):
        det = GuardCascadeDetector(max_history=5)
        for i in range(10):
            det.record_trigger(f"G{i}")
        assert len(det.trigger_history) == 5
        assert det.trigger_history[0].guard_id == "G5"

    def test_detect_cascade_no_cascade(self):
        det = GuardCascadeDetector(cascade_depth_threshold=4)
        for gid in ["G1", "G2", "G3"]:
            det.record_trigger(gid)
        result = det.detect_cascade()
        assert result["cascade_detected"] is False
        assert result["depth"] == 3

    def test_detect_cascade_triggers_cascade(self):
        det = GuardCascadeDetector(cascade_depth_threshold=4, cascade_window_seconds=60.0)
        for gid in ["G1", "G2", "G3", "G4"]:
            det.record_trigger(gid)
        result = det.detect_cascade()
        assert result["cascade_detected"] is True
        assert result["depth"] >= 4
        assert "suppressed" in result

    def test_detect_cascade_suppresses_downstream(self):
        det = GuardCascadeDetector(cascade_depth_threshold=3, cascade_window_seconds=60.0)
        for gid in ["G1", "G2", "G3", "G4", "G5"]:
            det.record_trigger(gid)
        det.detect_cascade()
        assert det.is_suppressed("G3")
        assert det.is_suppressed("G4")
        assert det.is_suppressed("G5")
        assert not det.is_suppressed("G1")
        assert not det.is_suppressed("G2")

    def test_is_suppressed_returns_false_for_unknown(self):
        det = GuardCascadeDetector()
        assert det.is_suppressed("nonexistent") is False

    def test_clear_suppression_specific(self):
        det = GuardCascadeDetector(cascade_depth_threshold=3, cascade_window_seconds=60.0)
        for gid in ["G1", "G2", "G3", "G4"]:
            det.record_trigger(gid)
        det.detect_cascade()
        det.clear_suppression("G3")
        assert not det.is_suppressed("G3")
        assert det.is_suppressed("G4")

    def test_clear_suppression_all(self):
        det = GuardCascadeDetector(cascade_depth_threshold=3, cascade_window_seconds=60.0)
        for gid in ["G1", "G2", "G3", "G4"]:
            det.record_trigger(gid)
        det.detect_cascade()
        det.clear_suppression()
        assert not det.is_suppressed("G3")
        assert not det.is_suppressed("G4")
        assert len(det.suppressed_guards) == 0

    def test_detect_cascade_empty_history(self):
        det = GuardCascadeDetector()
        result = det.detect_cascade()
        assert result["cascade_detected"] is False
        assert result["depth"] == 0

    def test_detect_cascade_duplicate_guards_counted_once(self):
        det = GuardCascadeDetector(cascade_depth_threshold=3, cascade_window_seconds=60.0)
        det.record_trigger("G1")
        det.record_trigger("G1")
        det.record_trigger("G1")
        result = det.detect_cascade()
        assert result["cascade_detected"] is False
        assert result["depth"] == 1
