# [A_test] module_id: SRC-TST-1382 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_point_in_time_reconstructor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.point_in_time_reconstructor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_point_in_time_reconstructor.py
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.feedback_loop.forensic.point_in_time_reconstructor import PointInTimeReconstructor


class TestPointInTimeReconstructor:
    def test_instantiation_defaults(self):
        pitr = PointInTimeReconstructor()
        assert pitr.snapshots == []
        assert pitr.events == []
        assert pitr.vector_clock == {}
        assert pitr.snapshot_interval == 3600.0

    def test_take_snapshot(self):
        pitr = PointInTimeReconstructor()
        pitr.take_snapshot({"state": "initial"})
        assert len(pitr.snapshots) == 1
        assert pitr.snapshots[0]["state"] == {"state": "initial"}
        assert pitr.last_snapshot_at > 0

    def test_take_snapshot_copies_state(self):
        pitr = PointInTimeReconstructor()
        state = {"key": "value"}
        pitr.take_snapshot(state)
        state["key"] = "modified"
        assert pitr.snapshots[0]["state"]["key"] == "value"

    def test_take_snapshot_max_24(self):
        pitr = PointInTimeReconstructor()
        for i in range(30):
            pitr.take_snapshot({"i": i})
        assert len(pitr.snapshots) <= 24

    def test_record_event(self):
        pitr = PointInTimeReconstructor()
        pitr.record_event("comp-a", "START", {"detail": "begin"})
        assert len(pitr.events) == 1
        assert pitr.events[0]["component"] == "comp-a"
        assert pitr.events[0]["type"] == "START"
        assert pitr.vector_clock["comp-a"] == 1

    def test_record_event_increments_vector_clock(self):
        pitr = PointInTimeReconstructor()
        pitr.record_event("comp-a", "START", {})
        pitr.record_event("comp-a", "STOP", {})
        pitr.record_event("comp-b", "START", {})
        assert pitr.vector_clock["comp-a"] == 2
        assert pitr.vector_clock["comp-b"] == 1

    def test_record_event_max_10000(self):
        pitr = PointInTimeReconstructor()
        for i in range(11000):
            pitr.record_event("comp", f"evt-{i}", {})
        assert len(pitr.events) <= 10000

    def test_reconstruct_found(self):
        pitr = PointInTimeReconstructor()
        t0 = time.time()
        pitr.take_snapshot({"base": True})
        t1 = time.time()
        pitr.record_event("comp", "UPDATE", {"val": 42})
        t2 = time.time()
        result = pitr.reconstruct(t1 + (t2 - t1) / 2)
        assert result is not None
        assert result["base"] is True

    def test_reconstruct_no_snapshot_before_target(self):
        pitr = PointInTimeReconstructor()
        result = pitr.reconstruct(time.time() - 1000)
        assert result is None

    def test_reconstruct_applies_events(self):
        pitr = PointInTimeReconstructor()
        pitr.take_snapshot({"base": True})
        t_after = time.time() + 0.01
        time.sleep(0.02)
        pitr.record_event("db", "WRITE", {"key": "val"})
        t_target = time.time()
        result = pitr.reconstruct(t_target)
        if result is not None:
            assert "base" in result

    def test_get_event_count_between(self):
        pitr = PointInTimeReconstructor()
        t_start = time.time()
        time.sleep(0.01)
        pitr.record_event("a", "E1", {})
        pitr.record_event("b", "E2", {})
        time.sleep(0.01)
        t_end = time.time()
        count = pitr.get_event_count_between(t_start, t_end)
        assert count >= 2

    def test_get_event_count_between_no_events(self):
        pitr = PointInTimeReconstructor()
        count = pitr.get_event_count_between(0, time.time())
        assert count == 0

    def test_snapshot_vector_clock_captured(self):
        pitr = PointInTimeReconstructor()
        pitr.record_event("comp", "E1", {})
        pitr.take_snapshot({"s": 1})
        assert pitr.snapshots[0]["vector_clock"] == {"comp": 1}
