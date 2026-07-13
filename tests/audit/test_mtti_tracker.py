# [A_test] module_id: SRC-TST-1296 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_mtti_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.mtti_tracker
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_mtti_tracker.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.diagnosis.mtti_tracker import MTTIEvent, MTTITracker


class TestMTTIEvent:
    def test_create_event(self):
        ev = MTTIEvent(anomaly_id="a1", occurred_at=100.0, detected_at=200.0, mtti_seconds=100.0)
        assert ev.anomaly_id == "a1"
        assert ev.mtti_seconds == 100.0

    def test_event_fields(self):
        ev = MTTIEvent(anomaly_id="a2", occurred_at=50.0, detected_at=150.0, mtti_seconds=100.0)
        assert ev.occurred_at == 50.0
        assert ev.detected_at == 150.0


class TestMTTITrackerInstantiation:
    def test_default_instantiation(self):
        tracker = MTTITracker()
        assert tracker.target_mtti_seconds == 300.0
        assert len(tracker.events) == 0

    def test_custom_target(self):
        tracker = MTTITracker(target_mtti_seconds=600.0)
        assert tracker.target_mtti_seconds == 600.0


class TestRecord:
    def test_record_event(self):
        tracker = MTTITracker()
        occurred = time.time() - 60
        event = tracker.record("anomaly-1", occurred)
        assert event.anomaly_id == "anomaly-1"
        assert event.mtti_seconds > 0
        assert len(tracker.events) == 1

    def test_record_multiple_events(self):
        tracker = MTTITracker()
        now = time.time()
        tracker.record("a1", now - 10)
        tracker.record("a2", now - 20)
        assert len(tracker.events) == 2

    def test_record_event_mtti_positive(self):
        tracker = MTTITracker()
        occurred = time.time() - 120
        event = tracker.record("a1", occurred)
        assert event.mtti_seconds >= 120.0

    def test_record_event_detected_at_is_now(self):
        tracker = MTTITracker()
        before = time.time()
        occurred = before - 5
        event = tracker.record("a1", occurred)
        after = time.time()
        assert before <= event.detected_at <= after


class TestCurrentMTTI:
    def test_no_events_returns_inf(self):
        tracker = MTTITracker()
        assert tracker.current_mtti() == float("inf")

    def test_single_event(self):
        tracker = MTTITracker()
        occurred = time.time() - 100
        tracker.record("a1", occurred)
        mtti = tracker.current_mtti()
        assert mtti >= 100.0

    def test_multiple_events_average(self):
        tracker = MTTITracker()
        now = time.time()
        tracker.record("a1", now - 200)
        tracker.record("a2", now - 100)
        mtti = tracker.current_mtti()
        assert 100.0 <= mtti <= 200.0


class TestSLABreachRate:
    def test_no_events_zero_rate(self):
        tracker = MTTITracker()
        assert tracker.sla_breach_rate() == 0.0

    def test_all_within_sla(self):
        tracker = MTTITracker(target_mtti_seconds=3600.0)
        now = time.time()
        tracker.record("a1", now - 60)
        tracker.record("a2", now - 120)
        assert tracker.sla_breach_rate() == 0.0

    def test_all_breach_sla(self):
        tracker = MTTITracker(target_mtti_seconds=1.0)
        now = time.time()
        tracker.record("a1", now - 300)
        tracker.record("a2", now - 600)
        assert tracker.sla_breach_rate() == 1.0

    def test_partial_breach(self):
        tracker = MTTITracker(target_mtti_seconds=150.0)
        now = time.time()
        tracker.record("a1", now - 100)
        tracker.record("a2", now - 200)
        assert 0.0 < tracker.sla_breach_rate() < 1.0
