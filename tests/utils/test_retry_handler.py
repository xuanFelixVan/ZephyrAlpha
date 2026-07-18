# [A_test] module_id: SRC-TST-1461 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-425 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_retry_handler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_retry_handler.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.reliability.retry_handler import (
    UNRECOVERABLE_EXCEPTIONS,
    RetryAttempt,
    RetryConfig,
    RetryHandler,
    RetryResult,
)


class TestRetryHandlerInstantiation:
    def test_default_construction(self):
        handler = RetryHandler()
        assert isinstance(handler._config, RetryConfig)
        assert handler._config.max_retries == 5

    def test_custom_config(self):
        config = RetryConfig(max_retries=2, base_delay_s=0.01, jitter=False)
        handler = RetryHandler(config=config)
        assert handler._config.max_retries == 2
        assert handler._config.base_delay_s == 0.01


class TestExecute:
    def test_successful_call_returns_success(self):
        handler = RetryHandler()
        result = handler.execute(lambda: 42)
        assert result.success is True
        assert len(result.attempts) == 1
        assert result.attempts[0].success is True
        assert result.final_error is None

    def test_recoverable_error_retries(self):
        config = RetryConfig(max_retries=2, base_delay_s=0.01, jitter=False)
        handler = RetryHandler(config=config)
        call_count = [0]

        def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ConnectionError("timeout")
            return "ok"

        result = handler.execute(flaky)
        assert result.success is True
        assert len(result.attempts) == 3
        assert call_count[0] == 3

    def test_unrecoverable_error_fails_immediately(self):
        config = RetryConfig(max_retries=5, base_delay_s=0.01, jitter=False)
        handler = RetryHandler(config=config)

        result = handler.execute(lambda: (_ for _ in ()).throw(ValueError("bad")))
        assert result.success is False
        assert len(result.attempts) == 1
        assert isinstance(result.final_error, ValueError)

    def test_max_retries_exhausted(self):
        config = RetryConfig(max_retries=2, base_delay_s=0.01, jitter=False)
        handler = RetryHandler(config=config)

        result = handler.execute(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
        assert result.success is False
        assert len(result.attempts) == 3
        assert isinstance(result.final_error, ConnectionError)

    def test_execute_with_args_and_kwargs(self):
        handler = RetryHandler()

        def add(a, b, extra=0):
            return a + b + extra

        result = handler.execute(add, 1, 2, extra=3)
        assert result.success is True
        assert result.attempts[0].success is True

    def test_type_error_is_unrecoverable(self):
        handler = RetryHandler(config=RetryConfig(max_retries=3, base_delay_s=0.01, jitter=False))
        result = handler.execute(lambda: (_ for _ in ()).throw(TypeError("type")))
        assert result.success is False
        assert len(result.attempts) == 1

    def test_assertion_error_is_unrecoverable(self):
        handler = RetryHandler(config=RetryConfig(max_retries=3, base_delay_s=0.01, jitter=False))
        result = handler.execute(lambda: (_ for _ in ()).throw(AssertionError("assert")))
        assert result.success is False
        assert len(result.attempts) == 1

    def test_import_error_is_unrecoverable(self):
        handler = RetryHandler(config=RetryConfig(max_retries=3, base_delay_s=0.01, jitter=False))
        result = handler.execute(lambda: (_ for _ in ()).throw(ImportError("no module")))
        assert result.success is False
        assert len(result.attempts) == 1

    def test_syntax_error_is_unrecoverable(self):
        handler = RetryHandler(config=RetryConfig(max_retries=3, base_delay_s=0.01, jitter=False))
        result = handler.execute(lambda: (_ for _ in ()).throw(SyntaxError("syntax")))
        assert result.success is False
        assert len(result.attempts) == 1

    def test_attribute_error_is_unrecoverable(self):
        handler = RetryHandler(config=RetryConfig(max_retries=3, base_delay_s=0.01, jitter=False))
        result = handler.execute(lambda: (_ for _ in ()).throw(AttributeError("attr")))
        assert result.success is False
        assert len(result.attempts) == 1


class TestIsUnrecoverable:
    def test_value_error_is_unrecoverable(self):
        assert RetryHandler._is_unrecoverable(ValueError("x")) is True

    def test_connection_error_is_recoverable(self):
        assert RetryHandler._is_unrecoverable(ConnectionError("x")) is False

    def test_runtime_error_is_recoverable(self):
        assert RetryHandler._is_unrecoverable(RuntimeError("x")) is False

    def test_type_error_is_unrecoverable(self):
        assert RetryHandler._is_unrecoverable(TypeError("x")) is True


class TestRetryConfigDataclass:
    def test_default_values(self):
        cfg = RetryConfig()
        assert cfg.base_delay_s == 1.0
        assert cfg.max_delay_s == 64.0
        assert cfg.max_retries == 5
        assert cfg.backoff_multiplier == 2.0
        assert cfg.jitter is True


class TestRetryAttemptDataclass:
    def test_fields(self):
        attempt = RetryAttempt(attempt=1, success=True, delay_s=0.1)
        assert attempt.attempt == 1
        assert attempt.success is True
        assert attempt.delay_s == 0.1
        assert attempt.exception is None
        assert attempt.total_time_s == 0.0

    def test_failed_attempt(self):
        attempt = RetryAttempt(
            attempt=2,
            success=False,
            delay_s=1.0,
            exception=ConnectionError("fail"),
            total_time_s=1.5,
        )
        assert attempt.success is False
        assert isinstance(attempt.exception, ConnectionError)


class TestRetryResultDataclass:
    def test_success_result(self):
        result = RetryResult(
            success=True,
            attempts=[RetryAttempt(attempt=1, success=True, delay_s=0.1)],
            total_time_s=0.1,
        )
        assert result.success is True
        assert result.final_error is None

    def test_failure_result(self):
        result = RetryResult(
            success=False,
            attempts=[RetryAttempt(attempt=1, success=False, delay_s=0.1, exception=RuntimeError("e"))],
            total_time_s=0.1,
            final_error=RuntimeError("e"),
        )
        assert result.success is False
        assert isinstance(result.final_error, RuntimeError)


class TestUnrecoverableExceptions:
    def test_tuple_contains_expected_types(self):
        assert ValueError in UNRECOVERABLE_EXCEPTIONS
        assert TypeError in UNRECOVERABLE_EXCEPTIONS
        assert AssertionError in UNRECOVERABLE_EXCEPTIONS
        assert SyntaxError in UNRECOVERABLE_EXCEPTIONS
        assert ImportError in UNRECOVERABLE_EXCEPTIONS
        assert AttributeError in UNRECOVERABLE_EXCEPTIONS
