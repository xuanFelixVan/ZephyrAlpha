# [A_test] module_id: SRC-TST-0998 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scheduler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.scheduler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scheduler.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler, FLEPipelineEvent


class TestFLEPipelineEvent:
    def test_creates_event(self):
        event = FLEPipelineEvent(run_id="r1", timestamp=0.0, phase="collect")
        assert event.run_id == "r1"
        assert event.phase == "collect"
        assert event.g6_gate_pass is True

    def test_to_dict(self):
        event = FLEPipelineEvent(run_id="r1", timestamp=0.0, phase="collect")
        d = event.to_dict()
        assert d["run_id"] == "r1"
        assert "g6_gate_pass" in d


class TestFeedbackLoopSchedulerInstantiation:
    def test_creates_with_defaults(self):
        scheduler = FeedbackLoopScheduler()
        assert scheduler.poll_interval == 30.0
        assert scheduler.max_events == 1000
        assert scheduler._running is False

    def test_creates_with_custom_params(self):
        scheduler = FeedbackLoopScheduler(poll_interval=10.0, max_events=500)
        assert scheduler.poll_interval == 10.0
        assert scheduler.max_events == 500


class TestSchedulerMethods:
    def test_run_count_initial(self):
        scheduler = FeedbackLoopScheduler()
        assert scheduler.run_count() == 0

    def test_events_initial(self):
        scheduler = FeedbackLoopScheduler()
        assert scheduler.events() == []

    def test_health_report(self):
        scheduler = FeedbackLoopScheduler()
        report = scheduler.health_report()
        assert isinstance(report, dict)
