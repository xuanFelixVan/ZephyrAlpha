# [A_test] module_id: SRC-TST-0724 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_deferred_queue
# [INVARIANTS] DeferredQueue uses in-memory SQLite; Observer must be fresh per test
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_deferred_queue.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.shared.infra.observer import EventType, Observer
from zephyr.orchestrator.deferred_queue import DeferredQueue, DeferredTaskStatus


@pytest.fixture
def observer():
    return Observer()


@pytest.fixture
def dq(observer):
    queue = DeferredQueue(observer, db_path=":memory:")
    yield queue
    queue.close()


class TestDeferredTaskStatus:
    def test_status_values(self):
        assert DeferredTaskStatus.WAITING.value == "WAITING"
        assert DeferredTaskStatus.READY.value == "READY"
        assert DeferredTaskStatus.RUNNING.value == "RUNNING"
        assert DeferredTaskStatus.DONE.value == "DONE"
        assert DeferredTaskStatus.FAILED.value == "FAILED"

    def test_status_is_string_enum(self):
        for status in DeferredTaskStatus:
            assert isinstance(status.value, str)


class TestDeferredQueueEnqueue:
    def test_enqueue_single_task(self, dq):
        dq.enqueue("task-1", waiting_for="file_event")
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1

    def test_enqueue_multiple_tasks(self, dq):
        dq.enqueue("task-1", waiting_for="file_event")
        dq.enqueue("task-2", waiting_for="time_event")
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 2

    def test_enqueue_with_payload(self, dq):
        dq.enqueue("task-1", waiting_for="file_event", payload='{"path": "a.md"}')
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1

    def test_enqueue_upsert_replaces_existing(self, dq):
        dq.enqueue("task-1", waiting_for="file_event")
        dq.enqueue("task-1", waiting_for="time_event")
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1


class TestDeferredQueueEventWake:
    def test_event_wakes_matching_task(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        counts = dq.count_by_status()
        assert counts.get("READY", 0) == 1

    def test_event_does_not_wake_non_matching(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.TIME_EVENT, {})
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1
        assert counts.get("READY", 0) == 0

    def test_conditional_wake_with_colon_syntax(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event:path")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        counts = dq.count_by_status()
        assert counts.get("READY", 0) == 1

    def test_conditional_wake_no_match(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event:missing_key")
        observer.emit(EventType.FILE_EVENT, {"other_key": "value"})
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1


class TestDeferredQueuePopReady:
    def test_pop_ready_returns_ready_tasks(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        result = dq.pop_ready()
        assert len(result) == 1
        assert result[0]["task_id"] == "task-1"

    def test_pop_ready_sets_running_status(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        dq.pop_ready()
        counts = dq.count_by_status()
        assert counts.get("RUNNING", 0) == 1

    def test_pop_ready_empty_returns_empty(self, dq):
        result = dq.pop_ready()
        assert result == []

    def test_pop_ready_respects_limit(self, dq, observer):
        for i in range(5):
            dq.enqueue(f"task-{i}", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        result = dq.pop_ready(limit=2)
        assert len(result) == 2


class TestDeferredQueueMarkDone:
    def test_mark_done(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        dq.pop_ready()
        dq.mark_done("task-1")
        counts = dq.count_by_status()
        assert counts.get("DONE", 0) == 1


class TestDeferredQueueMarkFailed:
    def test_mark_failed(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        dq.pop_ready()
        dq.mark_failed("task-1", "timeout exceeded")
        counts = dq.count_by_status()
        assert counts.get("FAILED", 0) == 1

    def test_mark_failed_empty_error_msg(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        dq.pop_ready()
        dq.mark_failed("task-1")
        counts = dq.count_by_status()
        assert counts.get("FAILED", 0) == 1


class TestDeferredQueueBulkWake:
    def test_bulk_wake_matching(self, dq):
        dq.enqueue("task-1", waiting_for="file_event")
        dq.enqueue("task-2", waiting_for="file_event")
        count = dq.bulk_wake(EventType.FILE_EVENT)
        assert count == 2
        counts = dq.count_by_status()
        assert counts.get("READY", 0) == 2

    def test_bulk_wake_no_matching(self, dq):
        dq.enqueue("task-1", waiting_for="time_event")
        count = dq.bulk_wake(EventType.FILE_EVENT)
        assert count == 0

    def test_bulk_wake_with_payload(self, dq):
        dq.enqueue("task-1", waiting_for="file_event")
        count = dq.bulk_wake(EventType.FILE_EVENT, {"path": "a.md"})
        assert count == 1


class TestDeferredQueueCountByStatus:
    def test_empty_queue(self, dq):
        counts = dq.count_by_status()
        assert counts == {}

    def test_mixed_statuses(self, dq, observer):
        dq.enqueue("task-1", waiting_for="file_event")
        dq.enqueue("task-2", waiting_for="time_event")
        observer.emit(EventType.FILE_EVENT, {"path": "a.md"})
        counts = dq.count_by_status()
        assert counts.get("WAITING", 0) == 1
        assert counts.get("READY", 0) == 1


class TestDeferredQueueClose:
    def test_close_unsubscribes(self, observer):
        dq = DeferredQueue(observer, db_path=":memory:")
        initial_count = observer.subscriber_count(EventType.FILE_EVENT)
        assert initial_count > 0
        dq.close()
        final_count = observer.subscriber_count(EventType.FILE_EVENT)
        assert final_count == initial_count - 1
