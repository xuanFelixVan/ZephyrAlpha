# [A_test] module_id: SRC-TST-1057 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_global_action_scheduler
# [INVARIANTS] queue sorted by priority desc; max_concurrent limits running; deadlock detects shared resources
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.global_action_scheduler import (
    ActionState,
    GlobalActionScheduler,
    ScheduledAction,
)


class TestActionState:
    def test_enum_values(self):
        assert ActionState.QUEUED == "QUEUED"
        assert ActionState.RUNNING == "RUNNING"
        assert ActionState.PREEMPTED == "PREEMPTED"
        assert ActionState.DONE == "DONE"


class TestScheduledActionInstantiation:
    def test_default_construction(self):
        sa = ScheduledAction(action_id="a1", priority=5)
        assert sa.action_id == "a1"
        assert sa.priority == 5
        assert sa.state == ActionState.QUEUED
        assert sa.started_at is None
        assert sa.target_resources == []

    def test_custom_resources(self):
        sa = ScheduledAction(action_id="a2", priority=3, target_resources=["db", "cache"])
        assert sa.target_resources == ["db", "cache"]


class TestGlobalActionSchedulerInstantiation:
    def test_default_construction(self):
        gas = GlobalActionScheduler()
        assert gas.queue == []
        assert gas.running == {}
        assert gas.max_concurrent == 3

    def test_custom_max_concurrent(self):
        gas = GlobalActionScheduler(max_concurrent=5)
        assert gas.max_concurrent == 5


class TestEnqueue:
    def test_enqueue_dispatches_immediately(self):
        gas = GlobalActionScheduler()
        action = ScheduledAction(action_id="a1", priority=5)
        gas.enqueue(action)
        assert "a1" in gas.running
        assert gas.running["a1"].state == ActionState.RUNNING
        assert len(gas.queue) == 0

    def test_enqueue_queues_when_full(self):
        gas = GlobalActionScheduler(max_concurrent=1)
        gas.enqueue(ScheduledAction(action_id="a1", priority=10))
        gas.enqueue(ScheduledAction(action_id="a2", priority=5))
        assert len(gas.running) == 1
        assert len(gas.queue) == 1

    def test_priority_sorting(self):
        gas = GlobalActionScheduler(max_concurrent=1)
        gas.enqueue(ScheduledAction(action_id="low", priority=1))
        gas.enqueue(ScheduledAction(action_id="high", priority=10))
        gas.enqueue(ScheduledAction(action_id="mid", priority=5))
        assert gas.queue[0].action_id == "high"
        assert gas.queue[1].action_id == "mid"


class TestComplete:
    def test_complete_removes_from_running(self):
        gas = GlobalActionScheduler()
        gas.enqueue(ScheduledAction(action_id="a1", priority=5))
        gas.complete("a1")
        assert "a1" not in gas.running

    def test_complete_dispatches_queued(self):
        gas = GlobalActionScheduler(max_concurrent=1)
        gas.enqueue(ScheduledAction(action_id="a1", priority=10))
        gas.enqueue(ScheduledAction(action_id="a2", priority=5))
        gas.complete("a1")
        assert "a2" in gas.running

    def test_complete_nonexistent_action(self):
        gas = GlobalActionScheduler()
        gas.complete("nonexistent")
        assert len(gas.running) == 0

    def test_complete_sets_state_done(self):
        gas = GlobalActionScheduler()
        action = ScheduledAction(action_id="a1", priority=5)
        gas.enqueue(action)
        gas.complete("a1")
        assert action.state == ActionState.DONE


class TestPreempt:
    def test_preempt_sets_state(self):
        gas = GlobalActionScheduler()
        gas.enqueue(ScheduledAction(action_id="a1", priority=5))
        gas.preempt("a1")
        assert gas.running["a1"].state == ActionState.PREEMPTED

    def test_preempt_nonexistent(self):
        gas = GlobalActionScheduler()
        gas.preempt("nonexistent")


class TestDetectDeadlock:
    def test_no_deadlock(self):
        gas = GlobalActionScheduler()
        gas.enqueue(ScheduledAction(action_id="a1", priority=5, target_resources=["db"]))
        gas.enqueue(ScheduledAction(action_id="a2", priority=3, target_resources=["cache"]))
        assert gas.detect_deadlock() == []

    def test_deadlock_on_shared_resource(self):
        gas = GlobalActionScheduler(max_concurrent=2)
        gas.enqueue(ScheduledAction(action_id="a1", priority=5, target_resources=["db"]))
        gas.enqueue(ScheduledAction(action_id="a2", priority=3, target_resources=["db"]))
        deadlocked = gas.detect_deadlock()
        assert "a1" in deadlocked
        assert "a2" in deadlocked

    def test_no_running_no_deadlock(self):
        gas = GlobalActionScheduler()
        assert gas.detect_deadlock() == []
