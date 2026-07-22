# [A_test] module_id: MOD-GOV_resilience_retry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_resilience_retry

# [INVARIANTS] RetryConfig.delay_for_attempt指数退避;should_retry黑白名单;RetryExhaustedError继承ZephyrBaseError

# [MODIFY-GUARD] retry.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] RetryExhaustedError

# [TESTS] pytest tests/test_resilience_retry.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.resilience.retry import (
    RetryConfig,
    RetryExhaustedError,
    async_retry,
)


class TestRetryConfig:
    def test_defaults(self):
        cfg = RetryConfig()
        assert cfg.max_attempts == 3
        assert cfg.base_delay_seconds == 1.0
        assert cfg.max_delay_seconds == 60.0
        assert cfg.backoff_multiplier == 2.0
        assert cfg.jitter is True

    def test_delay_for_attempt_increases(self):
        cfg = RetryConfig(base_delay_seconds=1.0, backoff_multiplier=2.0, jitter=False)
        d0 = cfg.delay_for_attempt(0)
        d1 = cfg.delay_for_attempt(1)
        d2 = cfg.delay_for_attempt(2)
        assert d0 <= d1 <= d2

    def test_delay_capped_at_max(self):
        cfg = RetryConfig(base_delay_seconds=1.0, max_delay_seconds=5.0, backoff_multiplier=10.0, jitter=False)
        d = cfg.delay_for_attempt(10)
        assert d <= 5.0

    def test_should_retry_default(self):
        cfg = RetryConfig()
        assert cfg.should_retry(ValueError("test")) is True

    def test_should_retry_whitelist(self):
        cfg = RetryConfig(retryable_exceptions=(ValueError,))
        assert cfg.should_retry(ValueError("ok")) is True
        assert cfg.should_retry(TypeError("no")) is False

    def test_should_retry_blacklist_overrides(self):
        cfg = RetryConfig(
            retryable_exceptions=(Exception,),
            non_retryable_exceptions=(ValueError,),
        )
        assert cfg.should_retry(ValueError("blocked")) is False
        assert cfg.should_retry(RuntimeError("allowed")) is True


class TestAsyncRetry:
    @pytest.mark.asyncio
    async def test_succeeds_first_try(self):
        @async_retry(RetryConfig(max_attempts=3, base_delay_seconds=0.01, jitter=False))
        async def ok():
            return "success"

        result = await ok()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retries_and_succeeds(self):
        call_count = 0

        @async_retry(RetryConfig(max_attempts=3, base_delay_seconds=0.01, jitter=False))
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "finally"

        result = await flaky()
        assert result == "finally"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausted_raises(self):
        @async_retry(RetryConfig(max_attempts=2, base_delay_seconds=0.01, jitter=False))
        async def always_fail():
            raise ValueError("nope")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await always_fail()
        assert exc_info.value.__cause__ is not None

    @pytest.mark.asyncio
    async def test_non_retryable_raises_immediately(self):
        call_count = 0

        @async_retry(
            RetryConfig(
                max_attempts=3,
                base_delay_seconds=0.01,
                retryable_exceptions=(ValueError,),
                non_retryable_exceptions=(TypeError,),
                jitter=False,
            )
        )
        async def type_error_func():
            nonlocal call_count
            call_count += 1
            raise TypeError("immediate")

        with pytest.raises(TypeError):
            await type_error_func()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_kwargs_config(self):
        @async_retry(max_attempts=2, base_delay_seconds=0.01)
        async def simple():
            return "ok"

        result = await simple()
        assert result == "ok"


class TestRetryExhaustedError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = RetryExhaustedError("exhausted", details={"max_attempts": 3})
        assert isinstance(err, ZephyrBaseError)
