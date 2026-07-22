# [A_test] module_id: MOD-GOV_escalation_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-313 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_escalation_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Test Escalation Engine — MOD-INF-022 v0.14.0.

Tests the core EscalationEngine (L0-L4 model with CircuitBreaker + EconomicGuard).
Blueprint: docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md §2
"""

from unittest.mock import patch

import pytest

from zephyr.governance.escalation import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    DelegationEngine,
    DelegationStrategy,
    EconomicGuard,
    EscalationEngine,
    EscalationLevel,
    EscalationState,
    RuleCategory,
)


@pytest.fixture(autouse=True)
def _disable_lsg():
    with (
        patch.object(EscalationEngine, "_lsg_scan_input", lambda self, desc: None),
        patch.object(DelegationEngine, "_lsg_verify_delegation", lambda self, event: None),
    ):
        yield


class TestEscalationEngineCore:
    def test_engine_initializes_with_default_rules(self):
        engine = EscalationEngine("test-core")
        assert len(engine._rules) >= 9
        assert engine._circuit_breaker.state == CircuitState.CLOSED

    def test_evaluate_security_violation_triggers_l4(self):
        engine = EscalationEngine("test-sec")
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "rm -rf / --no-preserve-root")
        assert ev.category == RuleCategory.SECURITY_VIOLATION
        assert ev.level == EscalationLevel.L4_EMERGENCY
        assert ev.state == EscalationState.EVALUATING

    def test_evaluate_deadlock_triggers_l3(self):
        engine = EscalationEngine("test-dl")
        ev = engine.evaluate(RuleCategory.DEADLOCK, "Agent A waiting on B, B waiting on A")
        assert ev.level == EscalationLevel.L3_CRITICAL

    def test_evaluate_budget_exceeded_triggers_l2(self):
        engine = EscalationEngine("test-budget")
        ev = engine.evaluate(RuleCategory.BUDGET_EXCEEDED, "Token budget exhausted")
        assert ev.level == EscalationLevel.L2_HUMAN_REVIEW

    def test_evaluate_auto_guard_failure_triggers_l1(self):
        engine = EscalationEngine("test-ag")
        ev = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, "Guard check failed on schema")
        assert ev.level == EscalationLevel.L1_AUTO_FIX

    def test_evaluate_unknown_category_no_match(self):
        engine = EscalationEngine("test-unk")
        ev = engine.evaluate(RuleCategory.CUSTOM, "some random operation")
        assert ev.state == EscalationState.REJECTED

    def test_escalate_increases_level(self):
        engine = EscalationEngine("test-esc")
        ev = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, "failed guard")
        result = engine.escalate(ev)
        assert result.escalated is True
        assert result.new_level.value > EscalationLevel.L0_SELF_HEAL.value

    def test_escalate_rejected_event_returns_no_escalation(self):
        engine = EscalationEngine("test-rej")
        ev = engine.evaluate(RuleCategory.CUSTOM, "dies ist unbekannt")
        result = engine.escalate(ev)
        assert result.escalated is False

    def test_record_resolution(self):
        engine = EscalationEngine("test-resolve")
        ev = engine.evaluate(RuleCategory.TIMEOUT, "request timed out")
        engine.record_resolution(ev)
        assert ev.state == EscalationState.RESOLVED
        assert ev.resolved_at is not None

    def test_record_failure_increments_retry(self):
        engine = EscalationEngine("test-fail")
        ev = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, "failed again")
        engine.record_failure(ev)
        assert ev.retry_count == 1

    def test_get_circuit_state(self):
        engine = EscalationEngine("test-cs")
        assert engine.get_circuit_state() == CircuitState.CLOSED

    def test_get_economic_status(self):
        engine = EscalationEngine("test-econ")
        status = engine.get_economic_status()
        assert "daily_budget" in status
        assert "consumed_today" in status
        assert "hard_limit_reached" in status

    def test_get_active_count(self):
        engine = EscalationEngine("test-active")
        assert engine.get_active_count() >= 0

    def test_rule_registration_and_removal(self):
        engine = EscalationEngine("test-reg")
        from zephyr.governance.escalation import EscalationRule

        new_rule = EscalationRule("X999", RuleCategory.CUSTOM, EscalationLevel.L3_CRITICAL, priority=99)
        engine.register_rule(new_rule)
        assert "X999" in engine._rules
        engine.remove_rule("X999")
        assert "X999" not in engine._rules


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker("test-cb")
        assert cb.state == CircuitState.CLOSED

    def test_call_returns_true_when_closed(self):
        cb = CircuitBreaker("test-cb2")
        assert cb.call() is True

    def test_failures_open_circuit(self):
        cb = CircuitBreaker("test-cb3", CircuitBreakerConfig(failure_threshold=3))
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.call() is False

    def test_half_open_recovery(self):
        cb = CircuitBreaker(
            "test-cb4", CircuitBreakerConfig(failure_threshold=2, success_threshold=2, cooldown_seconds=1)
        )
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        import time

        time.sleep(1.1)
        assert cb.call() is True
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker("test-cb5", CircuitBreakerConfig(failure_threshold=2, cooldown_seconds=1))
        cb.record_failure()
        cb.record_failure()
        import time

        time.sleep(1.1)
        cb.call()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_force_open_and_close(self):
        cb = CircuitBreaker("test-cb6")
        cb.force_open()
        assert cb.state == CircuitState.OPEN
        cb.force_close()
        assert cb.state == CircuitState.CLOSED

    def test_error_budget_consumed(self):
        cb = CircuitBreaker("test-cb7", CircuitBreakerConfig(error_budget_per_hour=3))
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.error_budget_remaining <= 0


class TestDelegationEngine:
    def test_register_and_unregister_delegate(self):
        de = DelegationEngine()
        de.register_delegate("architect", ["architecture", "design"])
        assert "architect" in de._delegate_load
        de.unregister_delegate("architect")
        assert "architect" not in de._delegate_load

    def test_delegate_load_balanced(self):
        de = DelegationEngine()
        de.register_delegate("agent-a")
        de.register_delegate("agent-b")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="owner-1")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "task-1")
        assert record.to_delegate in ("agent-a", "agent-b")
        assert record.strategy == DelegationStrategy.LOAD_BALANCED

    def test_delegate_expertise_match(self):
        de = DelegationEngine()
        de.register_delegate("security-bot", ["security"])
        de.register_delegate("generic-bot")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.SECURITY_VIOLATION, owner_id="owner-2")
        record = de.delegate(ev, DelegationStrategy.EXPERTISE_MATCH, "task-sec")
        assert record.to_delegate == "security-bot"

    def test_no_available_delegate(self):
        de = DelegationEngine()
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="owner-3")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "task-2")
        assert record.to_delegate == ""

    def test_accept_and_complete_delegation(self):
        de = DelegationEngine()
        de.register_delegate("worker-1")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="owner-4")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "task-3")
        assert de.accept_delegation(record.delegation_id) is True
        assert de.complete_delegation(record.delegation_id) is True

    def test_reject_delegation(self):
        de = DelegationEngine()
        de.register_delegate("worker-2")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="owner-5")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "task-4")
        assert de.reject_delegation(record.delegation_id) is True

    def test_cleanup_expired(self):
        de = DelegationEngine()
        de.register_delegate("worker-3")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id="owner-6")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "task-5")
        record.expires_at = None
        cleaned = de.cleanup_expired()
        assert isinstance(cleaned, int)

    def test_delegate_load_capped(self):
        de = DelegationEngine()
        de.register_delegate("busy-worker")
        from zephyr.governance.escalation import EscalationEvent, RuleCategory

        for i in range(10):
            ev = EscalationEvent(category=RuleCategory.TIMEOUT, owner_id=f"owner-{i}")
            de.delegate(ev, DelegationStrategy.LOAD_BALANCED, f"task-{i}")
        assert de.get_load("busy-worker") <= 10


class TestEconomicGuard:
    def test_can_proceed_within_budget(self):
        guard = EconomicGuard("eg-1", daily_budget=100.0)
        assert guard.can_proceed(10.0) is True

    def test_hard_limit_blocks(self):
        guard = EconomicGuard("eg-2", daily_budget=50.0)
        guard.can_proceed(60.0)
        assert guard.hard_limit_reached is True
        assert guard.can_proceed(1.0) is False

    def test_consume_tracks_usage(self):
        guard = EconomicGuard("eg-3", daily_budget=100.0)
        guard.consume(30.0)
        guard.consume(20.0)
        assert guard.consumed_today == 50.0


class TestEscalationLevelHierarchy:
    def test_level_ordering(self):
        assert EscalationLevel.L0_SELF_HEAL.value < EscalationLevel.L1_AUTO_FIX.value
        assert EscalationLevel.L1_AUTO_FIX.value < EscalationLevel.L2_HUMAN_REVIEW.value
        assert EscalationLevel.L2_HUMAN_REVIEW.value < EscalationLevel.L3_CRITICAL.value
        assert EscalationLevel.L3_CRITICAL.value < EscalationLevel.L4_EMERGENCY.value

    def test_level_max_is_l4(self):
        engine = EscalationEngine("test-max")
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "test")
        for _ in range(10):
            result = engine.escalate(ev)
            ev = result.event
        assert ev.level.value <= EscalationLevel.L4_EMERGENCY.value
