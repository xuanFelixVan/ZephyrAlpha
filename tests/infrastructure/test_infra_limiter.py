# [A_test] module_id: MOD-GOV_infra_limiter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_limiter

# [INVARIANTS] TokenBucketLimiter令牌桶算法;acquire成功扣令牌;超max_wait抛RateLimitError

# [MODIFY-GUARD] limiter.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] RateLimitError

# [TESTS] pytest tests/test_infra_limiter.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.infra.limiter import (
    RateLimitError,
    RateLimiterStats,
    TokenBucketLimiter,
    async_limited,
)
from zephyr.shared.utils.async_utils import run_coroutine_sync


class TestTokenBucketLimiter:
    def test_acquire_within_burst(self):
        limiter = TokenBucketLimiter(permits_per_second=10.0, burst_size=5.0)
        run_coroutine_sync(limiter.acquire())
        stats = limiter.stats()
        assert stats.total_acquired == 1

    def test_multiple_acquires(self):
        limiter = TokenBucketLimiter(permits_per_second=100.0, burst_size=10.0)

        async def acquire_n(n):
            for _ in range(n):
                await limiter.acquire()

        run_coroutine_sync(acquire_n(5))
        stats = limiter.stats()
        assert stats.total_acquired == 5

    def test_exhaust_burst_then_reject(self):
        limiter = TokenBucketLimiter(permits_per_second=1.0, burst_size=2.0, max_wait_seconds=0.0)

        async def exhaust():
            await limiter.acquire()
            await limiter.acquire()
            with pytest.raises(RateLimitError):
                await limiter.acquire()

        run_coroutine_sync(exhaust())

    def test_stats(self):
        limiter = TokenBucketLimiter(permits_per_second=10.0, burst_size=5.0)
        stats = limiter.stats()
        assert isinstance(stats, RateLimiterStats)
        assert stats.permits_per_second == 10.0
        assert stats.available_tokens == 5.0

    def test_context_manager(self):
        limiter = TokenBucketLimiter(permits_per_second=100.0, burst_size=10.0)

        async def use():
            async with limiter:
                pass

        run_coroutine_sync(use())
        assert limiter.stats().total_acquired == 1

    def test_refill_over_time(self):
        limiter = TokenBucketLimiter(permits_per_second=1000.0, burst_size=1.0)
        run_coroutine_sync(limiter.acquire())
        import time

        time.sleep(0.05)

        async def check():
            await limiter.acquire()

        run_coroutine_sync(check())
        stats = limiter.stats()
        assert stats.total_acquired == 2


class TestAsyncLimited:
    def test_decorator(self):
        @async_limited(permits_per_second=100.0, burst_size=10.0)
        async def my_func(x):
            return x * 2

        result = run_coroutine_sync(my_func(5))
        assert result == 10

    def test_decorator_preserves_name(self):
        @async_limited(permits_per_second=100.0)
        async def named_func():
            return 1

        assert named_func.__name__ == "named_func"

    def test_decorator_has_limiter(self):
        @async_limited(permits_per_second=100.0)
        async def limited_fn():
            return 1

        assert hasattr(limited_fn, "_limiter")


class TestRateLimitError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = RateLimitError("exceeded", details={"wait": 5.0})
        assert isinstance(err, ZephyrBaseError)
