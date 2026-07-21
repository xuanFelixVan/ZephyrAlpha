# [A_test] module_id: MOD-GOV_resilience_circuit_breaker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_resilience_circuit_breaker

# [INVARIANTS] CLOSED→OPEN需达阈值;OPEN→HALF_OPEN需超时;HALF_OPEN→CLOSED需成功

# [MODIFY-GUARD] circuit_breaker.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] CircuitOpenError

# [TESTS] pytest tests/test_resilience_circuit_breaker.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)


class TestCircuitState:
    def test_members(self):
        assert CircuitState.CLOSED.value == "CLOSED"
        assert CircuitState.OPEN.value == "OPEN"
        assert CircuitState.HALF_OPEN.value == "HALF_OPEN"


class TestCircuitBreakerInit:
    def test_defaults(self):
        cb = CircuitBreaker("test")
        assert cb.name == "test"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_custom_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout_ms=5000)
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerTransitions:
    def test_closed_stays_closed_on_success(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_closed_to_open_after_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_open_rejects_call(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb.record_failure()
        with pytest.raises(CircuitOpenError) as exc_info:
            cb.call(lambda: "never")
        assert exc_info.value.circuit_name == "test"

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        import time

        time.sleep(0.01)
        state = cb._transition()
        assert state == CircuitState.HALF_OPEN

    def test_half_open_success_closes(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        cb.record_failure()
        import time

        time.sleep(0.01)
        cb._transition()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        cb.record_failure()
        import time

        time.sleep(0.01)
        cb._transition()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_reset(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerCall:
    def test_call_succeeds_when_closed(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        result = cb.call(lambda x: x * 2, 5)
        assert result == 10

    def test_call_propagates_exception_and_records_failure(self):
        cb = CircuitBreaker("test", failure_threshold=3)

        def failing():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            cb.call(failing)
        assert cb.failure_count == 1

    def test_call_opens_after_enough_failures(self):
        cb = CircuitBreaker("test", failure_threshold=2)

        def failing():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            cb.call(failing)
        with pytest.raises(ValueError):
            cb.call(failing)
        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            cb.call(failing)


class TestCircuitOpenError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = CircuitOpenError("test_cb")
        assert isinstance(err, ZephyrBaseError)
        assert err.circuit_name == "test_cb"

    def test_default_message(self):
        err = CircuitOpenError("my_cb")
        assert "my_cb" in str(err)
        assert "OPEN" in str(err)
