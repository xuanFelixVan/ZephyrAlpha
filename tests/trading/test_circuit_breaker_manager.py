# [A_test] module_id: MOD-GOV_circuit_breaker_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_circuit_breaker_manager
# [INVARIANTS] CLOSED->OPEN when failures>=threshold; OPEN->HALF_OPEN after cooldown; HALF_OPEN->CLOSED on success
# [MODIFY-GUARD] only when CircuitBreakerManager public API changes
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import failure -> skip
# [TESTS] pytest tests/test_circuit_breaker_manager.py -q
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.infrastructure.pipeline.circuit_breaker_manager import CircuitBreakerManager
from zephyr.infrastructure.pipeline.models import CircuitBreakerState


class TestCircuitBreakerManagerInit:
    def test_instantiation(self):
        cb = CircuitBreakerManager()
        assert cb.open_count == 0

    def test_custom_params(self):
        cb = CircuitBreakerManager(failure_window_s=30.0, failure_threshold=5, cooldown_s=10.0)
        assert cb._failure_window_s == 30.0
        assert cb._failure_threshold == 5
        assert cb._cooldown_s == 10.0

    def test_log_fn_callback(self):
        logs = []
        cb = CircuitBreakerManager(log_fn=lambda level, msg: logs.append((level, msg)))
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "test-model")
        assert len(logs) > 0


class TestCircuitBreakerManagerAllowRequest:
    def test_initial_allow(self):
        cb = CircuitBreakerManager()
        assert cb.allow_request("key1", "deepseek") is True

    def test_allow_after_few_failures(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        cb.record_result("key1", success=False)
        cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is True

    def test_block_after_threshold_failures(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False

    def test_different_keys_independent(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False
        assert cb.allow_request("key2", "glm") is True


class TestCircuitBreakerManagerRecordResult:
    def test_success_clears_failures(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        cb.record_result("key1", success=False)
        cb.record_result("key1", success=False)
        cb.record_result("key1", success=True)
        assert cb.allow_request("key1", "deepseek") is True

    def test_failure_accumulates(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        cb.record_result("key1", success=False)
        cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is True
        cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False

    def test_half_open_to_closed_on_success(self):
        cb = CircuitBreakerManager(failure_threshold=3, cooldown_s=0.01)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False
        time.sleep(0.02)
        assert cb.allow_request("key1", "deepseek") is True
        cb.record_result("key1", success=True)
        st = cb.status("key1")
        assert st["key1"] == CircuitBreakerState.CLOSED.value

    def test_half_open_stays_on_failure(self):
        cb = CircuitBreakerManager(failure_threshold=3, cooldown_s=0.01)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False
        time.sleep(0.02)
        assert cb.allow_request("key1", "deepseek") is True
        cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is True
        st = cb.status("key1")
        assert st["key1"] == CircuitBreakerState.HALF_OPEN.value


class TestCircuitBreakerManagerResetAll:
    def test_reset_empty(self):
        cb = CircuitBreakerManager()
        count = cb.reset_all()
        assert count == 0

    def test_reset_with_open_breakers(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        count = cb.reset_all()
        assert count == 1
        assert cb.open_count == 0

    def test_reset_allows_requests_again(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        cb.reset_all()
        assert cb.allow_request("key1", "deepseek") is True


class TestCircuitBreakerManagerStatus:
    def test_status_unknown_key(self):
        cb = CircuitBreakerManager()
        st = cb.status("nonexistent")
        assert st["nonexistent"] == CircuitBreakerState.CLOSED.value

    def test_status_specific_key(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        st = cb.status("key1")
        assert st["key1"] == CircuitBreakerState.OPEN.value

    def test_status_all_keys(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        st = cb.status()
        assert "key1" in st
        assert st["key1"] == CircuitBreakerState.OPEN.value

    def test_status_empty(self):
        cb = CircuitBreakerManager()
        st = cb.status()
        assert st == {}


class TestCircuitBreakerManagerOpenCount:
    def test_no_open(self):
        cb = CircuitBreakerManager()
        assert cb.open_count == 0

    def test_one_open(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        assert cb.open_count == 1

    def test_multiple_open(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for key in ["key1", "key2", "key3"]:
            for _ in range(3):
                cb.record_result(key, success=False)
            cb.allow_request(key, "deepseek")
        assert cb.open_count == 3

    def test_open_count_after_reset(self):
        cb = CircuitBreakerManager(failure_threshold=3)
        for _ in range(3):
            cb.record_result("key1", success=False)
        cb.allow_request("key1", "deepseek")
        cb.reset_all()
        assert cb.open_count == 0


class TestCircuitBreakerManagerCooldown:
    def test_cooldown_transition(self):
        cb = CircuitBreakerManager(failure_threshold=3, cooldown_s=0.05)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False
        time.sleep(0.06)
        assert cb.allow_request("key1", "deepseek") is True

    def test_cooldown_not_elapsed(self):
        cb = CircuitBreakerManager(failure_threshold=3, cooldown_s=60.0)
        for _ in range(3):
            cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is False
        assert cb.allow_request("key1", "deepseek") is False


class TestCircuitBreakerManagerFailureWindow:
    def test_old_failures_expire(self):
        cb = CircuitBreakerManager(failure_window_s=0.05, failure_threshold=3)
        cb.record_result("key1", success=False)
        cb.record_result("key1", success=False)
        time.sleep(0.06)
        cb.record_result("key1", success=False)
        assert cb.allow_request("key1", "deepseek") is True
