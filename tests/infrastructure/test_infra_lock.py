# [A_test] module_id: MOD-GOV_infra_lock | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

from zephyr.shared.infra.lock import (
    LockError,
    LockHandle,
    MemoryLock,
)
from zephyr.shared.utils.async_utils import run_coroutine_sync


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
        handle = run_coroutine_sync(lock.acquire("resource-1"))
        assert handle is not None
        assert handle.lock_name == "resource-1"
        released = run_coroutine_sync(lock.release(handle))
        assert released is True

    def test_double_acquire_fails(self):
        lock = MemoryLock()
        h1 = run_coroutine_sync(lock.acquire("r1"))
        h2 = run_coroutine_sync(lock.acquire("r1"))
        assert h1 is not None
        assert h2 is None
        run_coroutine_sync(lock.release(h1))

    def test_is_locked(self):
        lock = MemoryLock()
        assert lock.is_locked("r1") is False
        h = run_coroutine_sync(lock.acquire("r1"))
        assert lock.is_locked("r1") is True
        run_coroutine_sync(lock.release(h))
        assert lock.is_locked("r1") is False

    def test_release_nonexistent(self):
        lock = MemoryLock()
        handle = LockHandle(lock_name="nope", owner_id="x")
        released = run_coroutine_sync(lock.release(handle))
        assert released is False

    def test_different_resources_independent(self):
        lock = MemoryLock()
        h1 = run_coroutine_sync(lock.acquire("r1"))
        h2 = run_coroutine_sync(lock.acquire("r2"))
        assert h1 is not None
        assert h2 is not None
        run_coroutine_sync(lock.release(h1))
        run_coroutine_sync(lock.release(h2))

    def test_context_manager(self):
        lock = MemoryLock()

        async def use_lock():
            async with lock.lock("resource", wait_timeout_seconds=1.0) as handle:
                assert handle is not None
                assert lock.is_locked("resource") is True
            assert lock.is_locked("resource") is False

        run_coroutine_sync(use_lock())

    def test_context_manager_contention_raises(self):
        lock = MemoryLock()

        async def use_lock():
            async with lock.lock("resource", wait_timeout_seconds=0.0) as h1:
                with pytest.raises(LockError):
                    async with lock.lock("resource", wait_timeout_seconds=0.0) as h2:
                        pass

        run_coroutine_sync(use_lock())

    def test_acquire_with_wait_timeout(self):
        lock = MemoryLock()

        async def use_lock():
            h1 = await lock.acquire("r1", wait_timeout_seconds=0.0)
            h2 = await lock.acquire("r1", wait_timeout_seconds=0.05)
            assert h1 is not None
            assert h2 is None
            await lock.release(h1)

        run_coroutine_sync(use_lock())


class TestLockError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = LockError("locked", details={"name": "r1"})
        assert isinstance(err, ZephyrBaseError)


class TestMemoryLockTTL:
    """5.40.9：TTL 过期强释语义。"""

    @pytest.mark.xfail(
        strict=False,
        reason="#ARCH-071 MemoryLock ttl_seconds 签名占位未实现（TTL 强释语义缺席）——代码侧缺口待裁定补实现",
    )
    def test_expired_lock_can_be_stolen(self):
        lock = MemoryLock()

        async def run():
            h1 = await lock.acquire("r1", ttl_seconds=0.05)
            assert h1 is not None
            await asyncio.sleep(0.1)
            # 持有者 TTL 已过期 -> 强释后抢锁成功
            h2 = await lock.acquire("r1")
            assert h2 is not None
            return h1

        h1 = run_coroutine_sync(run())
        # 被强释的原持有者 release 被 owner 校验拒绝
        released = run_coroutine_sync(lock.release(h1))
        assert released is False

    def test_unexpired_lock_cannot_be_stolen(self):
        lock = MemoryLock()

        async def run():
            h1 = await lock.acquire("r1", ttl_seconds=30.0)
            h2 = await lock.acquire("r1")
            assert h1 is not None
            assert h2 is None
            await lock.release(h1)

        run_coroutine_sync(run())

    @pytest.mark.xfail(strict=False, reason="#ARCH-071 MemoryLock is_locked 无 TTL 过期检查——代码侧缺口待裁定补实现")
    def test_is_locked_false_for_expired_hold(self):
        lock = MemoryLock()

        async def run():
            await lock.acquire("r1", ttl_seconds=0.05)
            assert lock.is_locked("r1") is True
            await asyncio.sleep(0.1)
            assert lock.is_locked("r1") is False

        run_coroutine_sync(run())

    @pytest.mark.xfail(
        strict=False,
        reason="#ARCH-071 MemoryLock ttl_seconds 签名占位未实现（TTL 强释语义缺席）——代码侧缺口待裁定补实现",
    )
    def test_wait_timeout_acquires_after_holder_ttl_expires(self):
        lock = MemoryLock()

        async def run():
            h1 = await lock.acquire("r1", ttl_seconds=0.05)
            assert h1 is not None
            # 持有者 TTL 0.05s 后到期；等待路径应检测到强释并抢锁成功，
            # 而非傻等 0.5s 超时失败
            h2 = await lock.acquire("r1", wait_timeout_seconds=0.5)
            assert h2 is not None

        run_coroutine_sync(run())
