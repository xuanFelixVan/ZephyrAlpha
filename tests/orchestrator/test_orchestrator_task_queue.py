# [A_test] module_id: SRC-TST-1340 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_task_queue
# [INVARIANTS] TaskQueue uses Protocol-based PipelineDispatcher; tests mock repo and dispatcher
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_task_queue.py
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

from zephyr.orchestrator.task_queue import PipelineDispatcher, TaskQueue, get_queue


@dataclass
class FakeTaskCard:
    task_id: str
    status: str = "READY"


class FakeRepo:
    def __init__(self, tasks=None):
        self._tasks = list(tasks or [])
        self._transitions = []

    def list_by_status(self, status):
        return [t for t in self._tasks if t.status.lower() == status.lower()]

    def transition(self, task_id, new_status):
        self._transitions.append((task_id, new_status))
        for t in self._tasks:
            if t.task_id == task_id:
                t.status = new_status


class FakeOrchestrator:
    def __init__(self):
        self.dispatched = []

    def dispatch(self, task_card):
        self.dispatched.append(task_card)
        return True


class TestTaskQueueInit:
    def test_default_not_running(self):
        repo = FakeRepo()
        q = TaskQueue(repo)
        assert q.is_running is False

    def test_default_stats(self):
        repo = FakeRepo()
        q = TaskQueue(repo)
        stats = q.stats
        assert stats["dispatched"] == 0
        assert stats["errors"] == 0
        assert stats["cycles"] == 0


class TestTaskQueueStartStop:
    def test_start_sets_running(self):
        repo = FakeRepo()
        q = TaskQueue(repo, poll_interval=10.0)
        q.start(daemon=True)
        try:
            assert q.is_running is True
        finally:
            q.stop(timeout=2.0)

    def test_stop_clears_running(self):
        repo = FakeRepo()
        q = TaskQueue(repo, poll_interval=10.0)
        q.start(daemon=True)
        q.stop(timeout=2.0)
        assert q.is_running is False

    def test_double_start_idempotent(self):
        repo = FakeRepo()
        q = TaskQueue(repo, poll_interval=10.0)
        q.start(daemon=True)
        q.start(daemon=True)
        assert q.is_running is True
        q.stop(timeout=2.0)

    def test_stop_when_not_running(self):
        repo = FakeRepo()
        q = TaskQueue(repo)
        q.stop(timeout=1.0)
        assert q.is_running is False


class TestTaskQueueTick:
    def test_tick_dispatches_ready_tasks(self):
        tasks = [FakeTaskCard(task_id="T-1"), FakeTaskCard(task_id="T-2")]
        repo = FakeRepo(tasks)
        orch = FakeOrchestrator()
        q = TaskQueue(repo, orch, max_per_cycle=3)
        n = q._tick()
        assert n == 2
        assert len(orch.dispatched) == 2
        assert repo._transitions == [("T-1", "IN_PROGRESS"), ("T-2", "IN_PROGRESS")]

    def test_tick_respects_max_per_cycle(self):
        tasks = [FakeTaskCard(task_id=f"T-{i}") for i in range(5)]
        repo = FakeRepo(tasks)
        orch = FakeOrchestrator()
        q = TaskQueue(repo, orch, max_per_cycle=2)
        n = q._tick()
        assert n == 2

    def test_tick_no_ready_tasks(self):
        repo = FakeRepo([])
        q = TaskQueue(repo)
        n = q._tick()
        assert n == 0

    def test_tick_with_no_orchestrator(self):
        tasks = [FakeTaskCard(task_id="T-1")]
        repo = FakeRepo(tasks)
        q = TaskQueue(repo, orchestrator=None, max_per_cycle=3)
        n = q._tick()
        assert n == 1
        assert repo._transitions == [("T-1", "IN_PROGRESS")]

    def test_tick_handles_dispatch_error(self):
        tasks = [FakeTaskCard(task_id="T-1")]
        repo = FakeRepo(tasks)
        bad_orch = MagicMock()
        bad_orch.dispatch.side_effect = RuntimeError("boom")
        q = TaskQueue(repo, bad_orch, max_per_cycle=3)
        n = q._tick()
        assert n == 0
        assert q.stats["errors"] == 1


class TestTaskQueueStats:
    def test_stats_returns_copy(self):
        repo = FakeRepo()
        q = TaskQueue(repo)
        s1 = q.stats
        s1["dispatched"] = 999
        assert q.stats["dispatched"] == 0


class TestPipelineDispatcherProtocol:
    def test_fake_orchestrator_satisfies_protocol(self):
        orch = FakeOrchestrator()
        assert isinstance(orch, PipelineDispatcher)

    def test_callable_class_satisfies_protocol(self):
        class MyDispatcher:
            def dispatch(self, task_card):
                return True

        d = MyDispatcher()
        assert isinstance(d, PipelineDispatcher)


class TestGetQueue:
    def teardown_method(self):
        import zephyr.orchestrator.task_queue as tq_mod

        tq_mod._queue = None

    def test_get_queue_returns_task_queue(self):
        repo = FakeRepo()
        q = get_queue(repo)
        assert isinstance(q, TaskQueue)

    def test_get_queue_singleton(self):
        repo = FakeRepo()
        q1 = get_queue(repo)
        q2 = get_queue(repo)
        assert q1 is q2
