# [A_test] module_id: MOD-GOV_infra_outbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_outbox

# [INVARIANTS] append→PENDING;mark_published→PUBLISHED;mark_failed→FAILED+retry_count++

# [MODIFY-GUARD] outbox.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] OutboxError

# [TESTS] pytest tests/test_infra_outbox.py -q
# [TTL] task_bound

import asyncio

from zephyr.shared.infra.outbox import (
    MemoryOutboxStore,
    OutboxEntry,
    OutboxError,
    OutboxPublisher,
    OutboxStatus,
)


class TestOutboxStatus:
    def test_members(self):
        assert OutboxStatus.PENDING.value == "PENDING"
        assert OutboxStatus.PUBLISHED.value == "PUBLISHED"
        assert OutboxStatus.FAILED.value == "FAILED"


class TestOutboxEntry:
    def test_defaults(self):
        entry = OutboxEntry(id="e1", event_type="test", payload={})
        assert entry.status == OutboxStatus.PENDING
        assert entry.retry_count == 0
        assert entry.idempotency_key == ""
        assert entry.published_at == 0.0


class TestMemoryOutboxStore:
    def test_append(self):
        store = MemoryOutboxStore()
        entry = asyncio.get_event_loop().run_until_complete(store.append("task.created", {"task_id": "T-001"}))
        assert entry.event_type == "task.created"
        assert entry.status == OutboxStatus.PENDING
        assert entry.idempotency_key != ""

    def test_append_with_idempotency_key(self):
        store = MemoryOutboxStore()
        entry = asyncio.get_event_loop().run_until_complete(store.append("test", {}, idempotency_key="custom-key"))
        assert entry.idempotency_key == "custom-key"

    def test_fetch_pending(self):
        store = MemoryOutboxStore()
        asyncio.get_event_loop().run_until_complete(store.append("ev1", {"a": 1}))
        asyncio.get_event_loop().run_until_complete(store.append("ev2", {"b": 2}))
        pending = asyncio.get_event_loop().run_until_complete(store.fetch_pending())
        assert len(pending) == 2

    def test_mark_published(self):
        store = MemoryOutboxStore()
        entry = asyncio.get_event_loop().run_until_complete(store.append("test", {}))
        asyncio.get_event_loop().run_until_complete(store.mark_published(entry.id))
        pending = asyncio.get_event_loop().run_until_complete(store.fetch_pending())
        assert len(pending) == 0

    def test_mark_failed(self):
        store = MemoryOutboxStore()
        entry = asyncio.get_event_loop().run_until_complete(store.append("test", {}))
        asyncio.get_event_loop().run_until_complete(store.mark_failed(entry.id))
        pending = asyncio.get_event_loop().run_until_complete(store.fetch_pending())
        assert len(pending) == 0
        entry_id = entry.id
        all_entries = asyncio.get_event_loop().run_until_complete(store.fetch_pending(limit=1000))
        count = asyncio.get_event_loop().run_until_complete(store.count_pending())
        assert count == 0

    def test_count_pending(self):
        store = MemoryOutboxStore()
        asyncio.get_event_loop().run_until_complete(store.append("a", {}))
        asyncio.get_event_loop().run_until_complete(store.append("b", {}))
        count = asyncio.get_event_loop().run_until_complete(store.count_pending())
        assert count == 2

    def test_fetch_pending_limit(self):
        store = MemoryOutboxStore()
        for i in range(5):
            asyncio.get_event_loop().run_until_complete(store.append(f"ev{i}", {}))
        pending = asyncio.get_event_loop().run_until_complete(store.fetch_pending(limit=2))
        assert len(pending) == 2

    def test_mark_published_nonexistent(self):
        store = MemoryOutboxStore()
        asyncio.get_event_loop().run_until_complete(store.mark_published("nonexistent"))

    def test_mark_failed_nonexistent(self):
        store = MemoryOutboxStore()
        asyncio.get_event_loop().run_until_complete(store.mark_failed("nonexistent"))


class TestOutboxPublisher:
    def test_publish_pending(self):
        store = MemoryOutboxStore()
        published = []

        def handler(entry):
            published.append(entry.id)

        publisher = OutboxPublisher(store=store, handler=handler, poll_interval_seconds=0.05)
        asyncio.get_event_loop().run_until_complete(store.append("test", {}))
        asyncio.get_event_loop().run_until_complete(publisher.start())
        import time

        time.sleep(0.2)
        asyncio.get_event_loop().run_until_complete(publisher.stop())
        assert len(published) >= 1

    def test_start_stop_idempotent(self):
        store = MemoryOutboxStore()
        publisher = OutboxPublisher(store=store, handler=lambda e: None, poll_interval_seconds=1.0)
        asyncio.get_event_loop().run_until_complete(publisher.start())
        asyncio.get_event_loop().run_until_complete(publisher.start())
        asyncio.get_event_loop().run_until_complete(publisher.stop())
        asyncio.get_event_loop().run_until_complete(publisher.stop())


class TestOutboxError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = OutboxError("fail", details={"entry_id": "x"})
        assert isinstance(err, ZephyrBaseError)
