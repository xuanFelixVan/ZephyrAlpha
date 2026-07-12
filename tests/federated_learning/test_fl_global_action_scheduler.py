# [A_test] module_id: SRC-TST-0966 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_global_action_scheduler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.global_action_scheduler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_global_action_scheduler.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.global_action_scheduler import (
    ActionState,
    GlobalActionScheduler,
    ScheduledAction,
)


class TestGlobalActionSchedulerInstantiation:
    def test_creates_with_defaults(self):
        scheduler = GlobalActionScheduler()
        assert scheduler.queue == []
        assert scheduler.running == {}
        assert scheduler.max_concurrent == 3


class TestEnqueue:
    def test_enqueue_dispatches_action(self):
        scheduler = GlobalActionScheduler()
        action = ScheduledAction(action_id="a1", priority=5)
        scheduler.enqueue(action)
        assert "a1" in scheduler.running
        assert scheduler.running["a1"].state == ActionState.RUNNING

    def test_enqueue_queues_when_full(self):
        scheduler = GlobalActionScheduler(max_concurrent=1)
        scheduler.enqueue(ScheduledAction(action_id="a1", priority=5))
        scheduler.enqueue(ScheduledAction(action_id="a2", priority=3))
        assert len(scheduler.running) == 1
        assert len(scheduler.queue) == 1

    def test_priority_ordering(self):
        scheduler = GlobalActionScheduler(max_concurrent=1)
        scheduler.enqueue(ScheduledAction(action_id="low", priority=1))
        scheduler.enqueue(ScheduledAction(action_id="high", priority=10))
        assert scheduler.queue[0].action_id == "high"


class TestComplete:
    def test_complete_dispatches_next(self):
        scheduler = GlobalActionScheduler(max_concurrent=1)
        scheduler.enqueue(ScheduledAction(action_id="a1", priority=5))
        scheduler.enqueue(ScheduledAction(action_id="a2", priority=3))
        scheduler.complete("a1")
        assert "a2" in scheduler.running

    def test_complete_unknown_action(self):
        scheduler = GlobalActionScheduler()
        scheduler.complete("nonexistent")


class TestDetectDeadlock:
    def test_no_deadlock(self):
        scheduler = GlobalActionScheduler()
        scheduler.enqueue(ScheduledAction(action_id="a1", priority=5, target_resources=["r1"]))
        result = scheduler.detect_deadlock()
        assert result == []

    def test_deadlock_detected(self):
        scheduler = GlobalActionScheduler(max_concurrent=2)
        scheduler.enqueue(ScheduledAction(action_id="a1", priority=5, target_resources=["r1"]))
        scheduler.enqueue(ScheduledAction(action_id="a2", priority=5, target_resources=["r1"]))
        result = scheduler.detect_deadlock()
        assert len(result) > 0
