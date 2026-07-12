# [A_test] module_id: SRC-TST-0946 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_config_timeline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.config_timeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_config_timeline.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.collectors.config_timeline import ConfigTimeline


class TestConfigTimelineInstantiation:
    def test_creates_with_defaults(self):
        timeline = ConfigTimeline()
        assert timeline.changes == []

    def test_creates_with_existing_changes(self):
        existing = [{"key": "threshold", "old": 2.5, "new": 3.0}]
        timeline = ConfigTimeline(changes=existing)
        assert len(timeline.changes) == 1


class TestRecord:
    def test_records_change(self):
        timeline = ConfigTimeline()
        timeline.record({"key": "threshold", "old": 2.5, "new": 3.0})
        assert len(timeline.changes) == 1
        assert timeline.changes[0]["key"] == "threshold"

    def test_records_multiple_changes(self):
        timeline = ConfigTimeline()
        timeline.record({"key": "a", "val": 1})
        timeline.record({"key": "b", "val": 2})
        assert len(timeline.changes) == 2

    def test_boundary_empty_change(self):
        timeline = ConfigTimeline()
        timeline.record({})
        assert len(timeline.changes) == 1

    def test_boundary_none_change_value(self):
        timeline = ConfigTimeline()
        timeline.record({"key": None})
        assert timeline.changes[0]["key"] is None
