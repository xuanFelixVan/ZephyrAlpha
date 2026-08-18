# [A_test] module_id: MOD-GOV_escalation_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-492 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.escalation_engine.test_escalation_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: escalation_core (EscalationEngine + DelegationEngine)"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from zephyr.governance.escalation.escalation_engine import EscalationEngine
from zephyr.governance.escalation.escalation_models import (
    DEFAULT_ESCALATION_RULES,
    DelegationRecord,
    DelegationStrategy,
    EconomicGuard,
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
from zephyr.governance.resilience_governance.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


@pytest.fixture(autouse=True)
def _disable_lsg():
    with (
        patch.object(EscalationEngine, "lsg_scan_input", lambda self, desc: None),
        patch.object(DelegationEngine, "lsg_verify_delegation", lambda self, event: None),
    ):
        yield


@pytest.fixture
def engine():
    return EscalationEngine(name="test", hooks_enabled=False)


@pytest.fixture
def delegation_engine():
    return DelegationEngine()


class TestEscalationEngineInit:
    def test_default_name(self):
        eng = EscalationEngine(hooks_enabled=False)
        assert eng.name == "default"

    def test_custom_name(self, engine):
        assert engine.name == "test"

    def test_default_rules_registered(self, engine):
        for rule in DEFAULT_ESCALATION_RULES:
            assert rule.rule_id in engine.rules

    def test_hooks_disabled(self, engine):
        assert engine.hooks_enabled is False
        assert engine.extension_detectors == {}

    def test_circuit_breaker_initialized(self, engine):
        assert engine.circuit_breaker is not None
        assert engine.circuit_breaker.state == CircuitState.CLOSED

    def test_economic_guard_initialized(self, engine):
        assert engine.economic_guard is not None
        assert engine.economic_guard.daily_budget == 100.0


class TestRuleManagement:
    def test_register_rule(self, engine):
        rule = EscalationRule(
            rule_id="CUSTOM-001",
            category=RuleCategory.CUSTOM,
            target_level=EscalationLevel.L1_AUTO_FIX,
        )
        engine.register_rule(rule)
        assert "CUSTOM-001" in engine.rules

    def test_remove_rule(self, engine):
        engine.remove_rule("R001")
        assert "R001" not in engine.rules

    def test_remove_nonexistent_rule(self, engine):
        engine.remove_rule("NO-SUCH-RULE")

    def test_register_replaces_existing(self, engine):
        original = engine.rules["R001"]
        new_rule = EscalationRule(
            rule_id="R001",
            category=RuleCategory.AUTO_GUARD_FAILURE,
            target_level=EscalationLevel.L3_CRITICAL,
            priority=999,
        )
        engine.register_rule(new_rule)
        assert engine.rules["R001"].priority == 999


class TestEvaluate:
    def test_evaluate_matching_rule(self, engine):
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="auto guard failed")
        assert event.state == EscalationState.EVALUATING
        assert event.category == RuleCategory.AUTO_GUARD_FAILURE

    def test_evaluate_no_matching_rule(self, engine):
        engine.rules.clear()
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="no rules")
        assert event.state == EscalationState.REJECTED

    def test_evaluate_circuit_breaker_open(self, engine):
        engine.circuit_breaker.force_open()
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="blocked")
        assert event.circuit_breaker_triggered is True
        assert event.state == EscalationState.REJECTED

    def test_evaluate_economic_guard_blocked(self, engine):
        engine.economic_guard.hard_limit_reached = True
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="no budget")
        assert event.economic_guard_passed is False
        assert event.state == EscalationState.REJECTED

    def test_evaluate_populates_event_fields(self, engine):
        event = engine.evaluate(
            RuleCategory.DEADLOCK,
            description="deadlock detected",
            owner_id="agent-1",
            source_event_id="evt-001",
        )
        assert event.owner_id == "agent-1"
        assert event.source_event_id == "evt-001"
        assert event.category == RuleCategory.DEADLOCK

    def test_evaluate_records_recent_escalation(self, engine):
        engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="test")
        assert len(engine.recent_escalations) == 1


class TestEscalate:
    def test_escalate_auto_escalate(self, engine):
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="fail")
        result = engine.escalate(event)
        assert isinstance(result, EscalationResult)
        assert result.escalated is True
        assert result.new_level.value >= EscalationLevel.L1_AUTO_FIX.value

    def test_escalate_rejected_event(self, engine):
        event = EscalationEvent(
            category=RuleCategory.AUTO_GUARD_FAILURE,
            state=EscalationState.REJECTED,
        )
        result = engine.escalate(event)
        assert result.escalated is False
        assert "Rejected" in result.message

    def test_escalate_security_violation_to_emergency(self, engine):
        event = engine.evaluate(RuleCategory.SECURITY_VIOLATION, description="breach")
        result = engine.escalate(event)
        assert result.new_level == EscalationLevel.L4_EMERGENCY

    def test_escalate_with_delegation(self, engine):
        event = engine.evaluate(RuleCategory.DEADLOCK, description="deadlock")
        result = engine.escalate(event)
        assert result.delegated_to is not None
        assert event.state == EscalationState.DELEGATED

    def test_escalate_consumes_economic_budget(self, engine):
        initial_consumed = engine.economic_guard.consumed_today
        event = engine.evaluate(RuleCategory.SECURITY_VIOLATION, description="breach")
        engine.escalate(event)
        assert engine.economic_guard.consumed_today > initial_consumed

    def test_escalate_max_level_cap(self, engine):
        event = EscalationEvent(
            category=RuleCategory.SECURITY_VIOLATION,
            level=EscalationLevel.L4_EMERGENCY,
            state=EscalationState.EVALUATING,
        )
        result = engine.escalate(event)
        assert result.new_level.value <= EscalationLevel.L4_EMERGENCY.value


class TestRecordResolutionAndFailure:
    def test_record_resolution(self, engine):
        event = engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="fail")
        engine.record_resolution(event)
        assert event.state == EscalationState.RESOLVED
        assert event.resolved_at is not None

    def test_record_failure_increments_retry(self, engine):
        event = EscalationEvent(category=RuleCategory.AUTO_GUARD_FAILURE)
        assert event.retry_count == 0
        engine.record_failure(event)
        assert event.retry_count == 1

    def test_record_failure_trips_circuit_breaker(self, engine):
        event = EscalationEvent(category=RuleCategory.AUTO_GUARD_FAILURE)
        for _ in range(engine.circuit_breaker.config.failure_threshold):
            engine.record_failure(event)
        assert engine.circuit_breaker.state == CircuitState.OPEN


class TestCircuitBreakerIntegration:
    def test_get_circuit_state(self, engine):
        assert engine.get_circuit_state() == CircuitState.CLOSED

    def test_circuit_breaker_transitions(self, engine):
        engine.circuit_breaker.force_open()
        assert engine.get_circuit_state() == CircuitState.OPEN
        engine.circuit_breaker.force_close()
        assert engine.get_circuit_state() == CircuitState.CLOSED


class TestEconomicStatus:
    def test_get_economic_status(self, engine):
        status = engine.get_economic_status()
        assert "daily_budget" in status
        assert "consumed_today" in status
        assert "hard_limit_reached" in status
        assert status["daily_budget"] == 100.0


class TestMetrics:
    def test_get_metrics_initial(self, engine):
        metrics = engine.get_metrics()
        assert metrics["total_evals"] == 0
        assert metrics["blocks"] == 0

    def test_get_metrics_after_evaluate(self, engine):
        engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="test")
        metrics = engine.get_metrics()
        assert metrics["total_evals"] >= 1


class TestGetActiveCount:
    def test_no_active(self, engine):
        assert engine.get_active_count() == 0

    def test_active_after_evaluate(self, engine):
        engine.evaluate(RuleCategory.AUTO_GUARD_FAILURE, description="test")
        assert engine.get_active_count() >= 1


class TestHooksToggle:
    def test_enable_hooks(self, engine):
        engine.enable_hooks()
        assert engine.hooks_enabled is True

    def test_disable_hooks(self, engine):
        engine.disable_hooks()
        assert engine.hooks_enabled is False


class TestGenerateSuggestion:
    def test_each_level_has_suggestion(self, engine):
        for level in EscalationLevel:
            event = EscalationEvent(level=level)
            rule = EscalationRule(rule_id="T", category=RuleCategory.CUSTOM, target_level=level)
            suggestion = EscalationEngine.generate_suggestion(event, rule)
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0


class TestDelegationEngineInit:
    def test_empty_state(self, delegation_engine):
        assert delegation_engine.get_available_delegates() == []
        assert delegation_engine.get_pending_delegations() == []


class TestDelegateRegistration:
    def test_register_delegate(self, delegation_engine):
        delegation_engine.register_delegate("agent-1", expertise=["deadlock", "security"])
        assert delegation_engine.get_load("agent-1") == 0
        assert "agent-1" in delegation_engine.get_available_delegates()

    def test_register_delegate_no_expertise(self, delegation_engine):
        delegation_engine.register_delegate("agent-2")
        assert "agent-2" in delegation_engine.get_available_delegates()

    def test_unregister_delegate(self, delegation_engine):
        delegation_engine.register_delegate("agent-3")
        delegation_engine.unregister_delegate("agent-3")
        assert "agent-3" not in delegation_engine.get_available_delegates()

    def test_unregister_nonexistent(self, delegation_engine):
        delegation_engine.unregister_delegate("no-such-agent")


class TestDelegationFlow:
    def test_delegate_load_balanced(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        delegation_engine.register_delegate("agent-2")
        event = EscalationEvent(
            category=RuleCategory.DEADLOCK,
            owner_id="owner-1",
            description="deadlock detected",
        )
        record = delegation_engine.delegate(event, strategy=DelegationStrategy.LOAD_BALANCED)
        assert isinstance(record, DelegationRecord)
        assert record.to_delegate in ("agent-1", "agent-2")
        assert record.to_delegate != "owner-1"
        assert record.from_owner == "owner-1"

    def test_delegate_round_robin(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        delegation_engine.register_delegate("agent-2")
        event1 = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d1")
        event2 = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d2")
        r1 = delegation_engine.delegate(event1, strategy=DelegationStrategy.ROUND_ROBIN)
        r2 = delegation_engine.delegate(event2, strategy=DelegationStrategy.ROUND_ROBIN)
        delegates = {r1.to_delegate, r2.to_delegate}
        assert len(delegates) == 2

    def test_delegate_expertise_match(self, delegation_engine):
        delegation_engine.register_delegate("agent-1", expertise=["deadlock"])
        delegation_engine.register_delegate("agent-2", expertise=["security"])
        event = EscalationEvent(
            category=RuleCategory.DEADLOCK,
            owner_id="owner",
            description="deadlock",
        )
        record = delegation_engine.delegate(event, strategy=DelegationStrategy.EXPERTISE_MATCH)
        assert record.to_delegate == "agent-1"

    def test_delegate_priority_queue(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        delegation_engine.register_delegate("agent-2")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event, strategy=DelegationStrategy.PRIORITY_QUEUE)
        assert record.to_delegate in ("agent-1", "agent-2")

    def test_delegate_no_available(self, delegation_engine):
        event = EscalationEvent(category=RuleCategory.DEADLOCK, description="d")
        record = delegation_engine.delegate(event)
        assert record.to_delegate == ""

    def test_delegate_excludes_owner(self, delegation_engine):
        delegation_engine.register_delegate("owner-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner-1", description="d")
        record = delegation_engine.delegate(event)
        assert record.to_delegate == ""

    def test_delegate_increments_load(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        delegation_engine.delegate(event)
        assert delegation_engine.get_load("agent-1") == 1

    def test_delegate_sets_event_state(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        delegation_engine.delegate(event)
        assert event.state == EscalationState.DELEGATED
        assert event.delegate_id == "agent-1"


class TestDelegationAcceptComplete:
    def test_accept_delegation(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event)
        result = delegation_engine.accept_delegation(record.delegation_id)
        assert result is True

    def test_accept_nonexistent(self, delegation_engine):
        assert delegation_engine.accept_delegation("no-such-id") is False

    def test_complete_delegation(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event)
        result = delegation_engine.complete_delegation(record.delegation_id)
        assert result is True
        assert delegation_engine.get_load("agent-1") == 0

    def test_complete_nonexistent(self, delegation_engine):
        assert delegation_engine.complete_delegation("no-such-id") is False

    def test_reject_delegation(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event)
        result = delegation_engine.reject_delegation(record.delegation_id)
        assert result is True
        assert delegation_engine.get_load("agent-1") == 0


class TestDelegationLoadLimits:
    def test_max_load_per_delegate(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        for i in range(delegation_engine.MAX_LOAD_PER_DELEGATE):
            event = EscalationEvent(
                category=RuleCategory.DEADLOCK,
                owner_id="owner",
                description=f"d{i}",
            )
            delegation_engine.delegate(event)
        assert "agent-1" not in delegation_engine.get_available_delegates()

    def test_get_pending_delegations(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event)
        pending = delegation_engine.get_pending_delegations()
        assert any(p.delegation_id == record.delegation_id for p in pending)


class TestDelegationCleanup:
    def test_cleanup_expired(self, delegation_engine):
        delegation_engine.register_delegate("agent-1")
        event = EscalationEvent(category=RuleCategory.DEADLOCK, owner_id="owner", description="d")
        record = delegation_engine.delegate(event)
        record.expires_at = datetime.now(UTC) - timedelta(hours=1)
        count = delegation_engine.cleanup_expired()
        assert count == 1
        assert delegation_engine.get_load("agent-1") == 0


class TestEscalationLevelEnum:
    def test_ordering(self):
        assert EscalationLevel.L0_SELF_HEAL.value < EscalationLevel.L1_AUTO_FIX.value
        assert EscalationLevel.L1_AUTO_FIX.value < EscalationLevel.L2_HUMAN_REVIEW.value
        assert EscalationLevel.L2_HUMAN_REVIEW.value < EscalationLevel.L3_CRITICAL.value
        assert EscalationLevel.L3_CRITICAL.value < EscalationLevel.L4_EMERGENCY.value


class TestEscalationStateEnum:
    def test_all_states(self):
        states = {s.value for s in EscalationState}
        assert "DETECTED" in states
        assert "EVALUATING" in states
        assert "ESCALATED" in states
        assert "DELEGATED" in states
        assert "RESOLVED" in states
        assert "REJECTED" in states
        assert "TIMED_OUT" in states


class TestRuleCategoryEnum:
    def test_all_categories(self):
        cats = {c.value for c in RuleCategory}
        assert "deadlock" in cats
        assert "security_violation" in cats
        assert "budget_exceeded" in cats
        assert "custom" in cats


class TestEconomicGuard:
    def test_can_proceed_within_budget(self):
        guard = EconomicGuard(guard_id="test", daily_budget=100.0)
        assert guard.can_proceed(1.0) is True

    def test_can_proceed_over_budget(self):
        guard = EconomicGuard(guard_id="test", daily_budget=5.0, consumed_today=4.5)
        assert guard.can_proceed(1.0) is False
        assert guard.hard_limit_reached is True

    def test_consume(self):
        guard = EconomicGuard(guard_id="test", daily_budget=100.0)
        guard.consume(10.0)
        assert guard.consumed_today == 10.0

    def test_hard_limit_blocks(self):
        guard = EconomicGuard(guard_id="test", daily_budget=100.0, hard_limit_reached=True)
        assert guard.can_proceed(0.01) is False


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED

    def test_call_closed(self):
        cb = CircuitBreaker("test")
        assert cb.call() is True

    def test_call_open(self):
        cb = CircuitBreaker("test")
        cb.force_open()
        assert cb.call() is False

    def test_record_failure_trips_to_open(self):
        cb = CircuitBreaker("test", config=CircuitBreakerConfig(failure_threshold=3))
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_force_close(self):
        cb = CircuitBreaker("test")
        cb.force_open()
        cb.force_close()
        assert cb.state == CircuitState.CLOSED

    def test_error_budget_remaining(self):
        cb = CircuitBreaker("test", config=CircuitBreakerConfig(error_budget_per_hour=10))
        assert cb.error_budget_remaining == 10
        cb.record_failure()
        assert cb.error_budget_remaining == 9
