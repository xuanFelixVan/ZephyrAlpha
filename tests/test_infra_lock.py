# [A_test] module_id: SRC-TST-1125 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_lock

# [INVARIANTS] MemoryLock单进程互斥;acquire返回LockHandle;release释放锁

# [MODIFY-GUARD] lock.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] LockError

# [TESTS] pytest tests/test_infra_lock.py -q
# [TTL] task_bound

import asyncio

import pytest

from zephyr.shared.infra_06.lock import (
    LockError,
    LockHandle,
    MemoryLock,
)


class TestLockHandle:
    def test_creation(self):
        handle = LockHandle(lock_name="test", owner_id="owner-1")
        assert handle.lock_name == "test"
        assert handle.owner_id == "owner-1"

    def test_has_acquired_at(self):
        handle = LockHandle(lock_name="test", owner_id="owner-1")
        assert handle.acquired_at > 0


class TestMemoryLock:
    def test_acquire_and_release(self):
        lock = MemoryLock()
        handle = asyncio.get_event_loop().run_until_complete(lock.acquire("resource-1"))
        assert handle is not None
        assert handle.lock_name == "resource-1"
        released = asyncio.get_event_loop().run_until_complete(lock.release(handle))
        assert released is True

    def test_double_acquire_fails(self):
        lock = MemoryLock()
        h1 = asyncio.get_event_loop().run_until_complete(lock.acquire("r1"))
        h2 = asyncio.get_event_loop().run_until_complete(lock.acquire("r1"))
        assert h1 is not None
        assert h2 is None
        asyncio.get_event_loop().run_until_complete(lock.release(h1))

    def test_is_locked(self):
        lock = MemoryLock()
        assert lock.is_locked("r1") is False
        h = asyncio.get_event_loop().run_until_complete(lock.acquire("r1"))
        assert lock.is_locked("r1") is True
        asyncio.get_event_loop().run_until_complete(lock.release(h))
        assert lock.is_locked("r1") is False

    def test_release_nonexistent(self):
        lock = MemoryLock()
        handle = LockHandle(lock_name="nope", owner_id="x")
        released = asyncio.get_event_loop().run_until_complete(lock.release(handle))
        assert released is False

    def test_different_resources_independent(self):
        lock = MemoryLock()
        h1 = asyncio.get_event_loop().run_until_complete(lock.acquire("r1"))
        h2 = asyncio.get_event_loop().run_until_complete(lock.acquire("r2"))
        assert h1 is not None
        assert h2 is not None
        asyncio.get_event_loop().run_until_complete(lock.release(h1))
        asyncio.get_event_loop().run_until_complete(lock.release(h2))

    def test_context_manager(self):
        lock = MemoryLock()

        async def use_lock():
            async with lock.lock("resource", wait_timeout_seconds=1.0) as handle:
                assert handle is not None
                assert lock.is_locked("resource") is True
            assert lock.is_locked("resource") is False

        asyncio.get_event_loop().run_until_complete(use_lock())

    def test_context_manager_contention_raises(self):
        lock = MemoryLock()

        async def use_lock():
            async with lock.lock("resource", wait_timeout_seconds=0.0) as h1:
                with pytest.raises(LockError):
                    async with lock.lock("resource", wait_timeout_seconds=0.0) as h2:
                        pass

        asyncio.get_event_loop().run_until_complete(use_lock())

    def test_acquire_with_wait_timeout(self):
        lock = MemoryLock()

        async def use_lock():
            h1 = await lock.acquire("r1", wait_timeout_seconds=0.0)
            h2 = await lock.acquire("r1", wait_timeout_seconds=0.05)
            assert h1 is not None
            assert h2 is None
            await lock.release(h1)

        asyncio.get_event_loop().run_until_complete(use_lock())


class TestLockError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.integration.shared_08.errors import ZephyrBaseError

        err = LockError("locked", details={"name": "r1"})
        assert isinstance(err, ZephyrBaseError)
