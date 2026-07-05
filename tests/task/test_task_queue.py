# [A_test] module_id: SRC-TST-1723 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-438 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_task_queue
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_task_queue.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.queue.task_queue import (
    QueueConfig,
    QueueItem,
    QueueItemStatus,
    TaskQueue,
)


class TestTaskQueueInstantiation:
    def test_default_construction(self):
        q = TaskQueue()
        assert q._items == []
        assert isinstance(q._config, QueueConfig)

    def test_custom_data_dir(self, tmp_path):
        q = TaskQueue(data_dir=tmp_path / "queue")
        assert q._data_dir == tmp_path / "queue"


class TestEnqueue:
    def test_enqueue_returns_queue_item(self):
        q = TaskQueue()
        item = q.enqueue("TASK-001")
        assert isinstance(item, QueueItem)
        assert item.task_id == "TASK-001"
        assert item.status == QueueItemStatus.ENQUEUED
        assert item.priority == "P2"

    def test_enqueue_with_custom_priority(self):
        q = TaskQueue()
        item = q.enqueue("TASK-002", priority="P0")
        assert item.priority == "P0"

    def test_enqueue_multiple_items(self):
        q = TaskQueue()
        q.enqueue("TASK-001")
        q.enqueue("TASK-002")
        assert len(q._items) == 2

    def test_enqueue_generates_unique_item_id(self):
        q = TaskQueue()
        a = q.enqueue("TASK-001")
        b = q.enqueue("TASK-002")
        assert a.item_id != b.item_id

    def test_enqueue_empty_task_id(self):
        q = TaskQueue()
        item = q.enqueue("")
        assert item.task_id == ""


class TestDequeueNext:
    def test_dequeue_from_empty_queue_returns_none(self):
        q = TaskQueue()
        assert q.dequeue_next() is None

    def test_dequeue_returns_highest_priority(self):
        q = TaskQueue()
        q.enqueue("LOW", priority="P2")
        q.enqueue("HIGH", priority="P0")
        q.enqueue("MID", priority="P1")
        item = q.dequeue_next()
        assert item is not None
        assert item.priority == "P0"
        assert item.task_id == "HIGH"

    def test_dequeue_sets_status_to_dispatched(self):
        q = TaskQueue()
        q.enqueue("TASK-001")
        item = q.dequeue_next()
        assert item is not None
        assert item.status == QueueItemStatus.DISPATCHED
        assert item.dispatched_at != ""

    def test_dequeue_only_enqueued_items(self):
        q = TaskQueue()
        item = q.enqueue("TASK-001")
        item.status = QueueItemStatus.COMPLETED
        assert q.dequeue_next() is None

    def test_dequeue_respects_only_p0_config(self):
        q = TaskQueue()
        q._config.only_p0 = True
        q.enqueue("LOW", priority="P2")
        q.enqueue("HIGH", priority="P0")
        item = q.dequeue_next()
        assert item is not None
        assert item.priority == "P0"

    def test_dequeue_skips_non_p0_when_only_p0(self):
        q = TaskQueue()
        q._config.only_p0 = True
        q.enqueue("LOW", priority="P2")
        assert q.dequeue_next() is None


class TestGetStats:
    def test_empty_queue_stats(self):
        q = TaskQueue()
        stats = q.get_stats()
        assert all(v == 0 for v in stats.values())

    def test_stats_after_enqueue(self):
        q = TaskQueue()
        q.enqueue("TASK-001")
        stats = q.get_stats()
        assert stats[QueueItemStatus.ENQUEUED.value] == 1

    def test_stats_after_dequeue(self):
        q = TaskQueue()
        q.enqueue("TASK-001")
        q.dequeue_next()
        stats = q.get_stats()
        assert stats[QueueItemStatus.DISPATCHED.value] == 1
        assert stats[QueueItemStatus.ENQUEUED.value] == 0


class TestClearCompleted:
    def test_clear_completed_removes_finished_items(self):
        q = TaskQueue()
        item = q.enqueue("TASK-001")
        item.status = QueueItemStatus.COMPLETED
        removed = q.clear_completed()
        assert removed == 1
        assert len(q._items) == 0

    def test_clear_completed_removes_failed_items(self):
        q = TaskQueue()
        item = q.enqueue("TASK-001")
        item.status = QueueItemStatus.FAILED
        removed = q.clear_completed()
        assert removed == 1

    def test_clear_completed_keeps_enqueued(self):
        q = TaskQueue()
        q.enqueue("TASK-001")
        removed = q.clear_completed()
        assert removed == 0
        assert len(q._items) == 1

    def test_clear_completed_on_empty_queue(self):
        q = TaskQueue()
        removed = q.clear_completed()
        assert removed == 0


class TestSetDispatchHandler:
    def test_set_handler(self):
        q = TaskQueue()
        handler_called = []

        def handler(item):
            handler_called.append(item.item_id)
            return True

        q.set_dispatch_handler(handler)
        assert q._dispatch_handler is not None


class TestQueueItemDataclass:
    def test_default_values(self):
        item = QueueItem(item_id="Q1", task_id="T1")
        assert item.priority == "P2"
        assert item.status == QueueItemStatus.ENQUEUED
        assert item.enqueued_at != ""
        assert item.dispatched_at == ""

    def test_custom_values(self):
        item = QueueItem(
            item_id="Q2",
            task_id="T2",
            priority="P0",
            status=QueueItemStatus.DISPATCHED,
        )
        assert item.priority == "P0"
        assert item.status == QueueItemStatus.DISPATCHED


class TestQueueConfigDataclass:
    def test_default_values(self):
        cfg = QueueConfig()
        assert cfg.poll_interval_s == 300
        assert cfg.auto_dispatch is True
        assert cfg.max_concurrent == 1
        assert cfg.only_p0 is False
