# [A_test] module_id: MOD-GOV_e_circuit_breaker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2.3
# [MODULE] tests.test_e_circuit_breaker
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)


class TestCircuitState:
    def test_three_states(self):
        assert len(CircuitState) == 3

    def test_values(self):
        assert CircuitState.CLOSED.value == "CLOSED"
        assert CircuitState.OPEN.value == "OPEN"
        assert CircuitState.HALF_OPEN.value == "HALF_OPEN"


class TestCircuitBreakerConfig:
    def test_defaults(self):
        cfg = CircuitBreakerConfig()
        assert cfg.failure_threshold == 5
        assert cfg.success_threshold == 3
        assert cfg.timeout_seconds == 60
        assert cfg.half_open_max_requests == 1
        assert cfg.cooldown_seconds == 300
        assert cfg.error_budget_per_hour == 10

    def test_custom(self):
        cfg = CircuitBreakerConfig(failure_threshold=10, cooldown_seconds=60)
        assert cfg.failure_threshold == 10
        assert cfg.cooldown_seconds == 60


class TestCircuitBreakerInit:
    def test_default_state(self):
        cb = CircuitBreaker("test")
        assert cb.name == "test"
        assert cb.state == CircuitState.CLOSED

    def test_custom_config(self):
        cfg = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test", cfg)
        assert cb.config.failure_threshold == 3


class TestCircuitBreakerCall:
    def test_closed_state_returns_true(self):
        cb = CircuitBreaker("test")
        assert cb.call() is True

    def test_open_state_returns_false(self):
        cb = CircuitBreaker("test")
        cb.force_open()
        assert cb.call() is False

    def test_half_open_returns_true(self):
        cb = CircuitBreaker("test")
        cb.state = CircuitState.HALF_OPEN
        assert cb.call() is True


class TestCircuitBreakerRecord:
    def test_failure_increments_count(self):
        cb = CircuitBreaker("test")
        cb.record_failure()
        assert cb.failure_count == 1

    def test_threshold_exceeded_opens(self):
        cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=2))
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_success_in_half_open_closes(self):
        cb = CircuitBreaker("test", CircuitBreakerConfig(success_threshold=1))
        cb.state = CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker("test")
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0


class TestCircuitBreakerForce:
    def test_force_open(self):
        cb = CircuitBreaker("test")
        cb.force_open()
        assert cb.state == CircuitState.OPEN

    def test_force_close(self):
        cb = CircuitBreaker("test")
        cb.force_open()
        cb.force_close()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerErrorBudget:
    def test_initial_budget(self):
        cb = CircuitBreaker("test")
        assert cb.error_budget_remaining == 10

    def test_consumed_budget(self):
        cb = CircuitBreaker("test")
        for _ in range(3):
            cb.record_failure()
        assert cb.error_budget_remaining == 7

    def test_exhausted_budget(self):
        cb = CircuitBreaker("test")
        for _ in range(15):
            cb.record_failure()
        assert cb.error_budget_remaining == 0
