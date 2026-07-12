# [A_test] module_id: SRC-TST-0521 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-357 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_circuit_breaker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_circuit_breaker_root.py
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

from zephyr.shared.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)


class TestCircuitBreakerInstantiation:
    def test_default_construction(self):
        cb = CircuitBreaker("test")
        assert cb.name == "test"
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_threshold == 5
        assert cb._recovery_timeout_ms == 30_000

    def test_custom_thresholds(self):
        cb = CircuitBreaker("custom", failure_threshold=5, recovery_timeout_ms=30_000)
        assert cb._failure_threshold == 5
        assert cb._recovery_timeout_ms == 30_000


class TestCall:
    def test_call_succeeds_when_closed(self):
        cb = CircuitBreaker("test")
        result = cb.call(lambda: 42)
        assert result == 42
        assert cb.state == CircuitState.CLOSED

    def test_call_tracks_failures(self):
        cb = CircuitBreaker("test", failure_threshold=2)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb.state == CircuitState.OPEN

    def test_call_raises_open_error_when_open(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=600_000)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            cb.call(lambda: 1)

    def test_call_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb.state == CircuitState.OPEN
        time.sleep(0.05)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"

    def test_call_with_args_and_kwargs(self):
        cb = CircuitBreaker("test")

        def add(a, b, extra=0):
            return a + b + extra

        result = cb.call(add, 1, 2, extra=3)
        assert result == 6

    def test_call_resets_failure_count_on_success_in_closed(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb._failure_count == 1
        cb.call(lambda: "ok")
        assert cb._failure_count == 0


class TestReset:
    def test_reset_returns_to_closed(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0

    def test_reset_allows_calls_again(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=600_000)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        cb.reset()
        result = cb.call(lambda: "works")
        assert result == "works"


class TestHalfOpenRecovery:
    def test_half_open_single_success_closes(self):
        """shared/resilience impl: HALF_OPEN→CLOSED on single success."""
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        time.sleep(0.05)
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker("test", failure_threshold=1, recovery_timeout_ms=0)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        time.sleep(0.05)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert cb.state == CircuitState.OPEN


class TestCircuitStateEnum:
    def test_enum_values(self):
        assert CircuitState.CLOSED.value == "CLOSED"
        assert CircuitState.OPEN.value == "OPEN"
        assert CircuitState.HALF_OPEN.value == "HALF_OPEN"

    def test_string_comparison(self):
        assert CircuitState.CLOSED == "CLOSED"
        assert CircuitState.OPEN == "OPEN"
