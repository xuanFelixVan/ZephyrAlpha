# [A_test] module_id: MOD-GOV_escalation_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_escalation_models
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_models.py -q
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

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


class TestEscalationLevel:
    def test_enum_values_contiguous(self):
        values = [m.value for m in EscalationLevel]
        assert values == list(range(5))

    def test_level_ordering(self):
        assert EscalationLevel.L0_SELF_HEAL.value < EscalationLevel.L1_AUTO_FIX.value
        assert EscalationLevel.L3_CRITICAL.value < EscalationLevel.L4_EMERGENCY.value


class TestEscalationState:
    def test_all_states_unique(self):
        names = [s.value for s in EscalationState]
        assert len(names) == len(set(names))

    def test_state_count(self):
        assert len(EscalationState) == 7


class TestRuleCategory:
    def test_all_categories_unique(self):
        values = [c.value for c in RuleCategory]
        assert len(values) == len(set(values))

    def test_category_count(self):
        assert len(RuleCategory) == 11


class TestDelegationStrategy:
    def test_all_strategies_unique(self):
        values = [s.value for s in DelegationStrategy]
        assert len(values) == len(set(values))

    def test_strategy_count(self):
        assert len(DelegationStrategy) == 5


class TestEscalationEvent:
    def test_default_instantiation(self):
        evt = EscalationEvent()
        assert evt.event_id
        assert evt.module_id == "MOD-INF-022"
        assert evt.category == RuleCategory.CUSTOM
        assert evt.level == EscalationLevel.L0_SELF_HEAL
        assert evt.state == EscalationState.DETECTED
        assert evt.retry_count == 0
        assert evt.max_retries == 3
        assert evt.circuit_breaker_triggered is False
        assert evt.economic_guard_passed is True
        assert isinstance(evt.metadata, dict)

    def test_custom_fields(self):
        evt = EscalationEvent(
            category=RuleCategory.SECURITY_VIOLATION,
            level=EscalationLevel.L4_EMERGENCY,
            description="critical breach",
            owner_id="agent-001",
        )
        assert evt.category == RuleCategory.SECURITY_VIOLATION
        assert evt.level == EscalationLevel.L4_EMERGENCY
        assert evt.description == "critical breach"
        assert evt.owner_id == "agent-001"

    def test_unique_event_ids(self):
        ids = {EscalationEvent().event_id for _ in range(100)}
        assert len(ids) == 100

    def test_timestamps_auto_set(self):
        evt = EscalationEvent()
        assert isinstance(evt.created_at, datetime)
        assert isinstance(evt.updated_at, datetime)


class TestEscalationRule:
    def test_default_instantiation(self):
        rule = EscalationRule(rule_id="T001", category=RuleCategory.TIMEOUT, target_level=EscalationLevel.L1_AUTO_FIX)
        assert rule.rule_id == "T001"
        assert rule.priority == 0
        assert rule.auto_escalate is True
        assert rule.cooldown_seconds == 300
        assert rule.max_escalations_per_hour == 10
        assert rule.delegate_strategy == DelegationStrategy.NONE
        assert rule.enabled is True

    def test_custom_fields(self):
        rule = EscalationRule(
            rule_id="T002",
            category=RuleCategory.DEADLOCK,
            target_level=EscalationLevel.L3_CRITICAL,
            priority=50,
            cooldown_seconds=60,
            delegate_strategy=DelegationStrategy.LOAD_BALANCED,
            notification_channels=["slack", "email"],
        )
        assert rule.priority == 50
        assert rule.notification_channels == ["slack", "email"]
        assert rule.delegate_strategy == DelegationStrategy.LOAD_BALANCED


class TestEconomicGuard:
    def test_can_proceed_within_budget(self):
        guard = EconomicGuard(guard_id="G001", daily_budget=100.0)
        assert guard.can_proceed(50.0) is True

    def test_can_proceed_exceeds_budget(self):
        guard = EconomicGuard(guard_id="G002", daily_budget=10.0)
        assert guard.can_proceed(15.0) is False
        assert guard.hard_limit_reached is True

    def test_consume_updates_consumed(self):
        guard = EconomicGuard(guard_id="G003", daily_budget=100.0)
        guard.consume(30.0)
        assert guard.consumed_today == 30.0

    def test_hard_limit_blocks_after_breach(self):
        guard = EconomicGuard(guard_id="G004", daily_budget=10.0)
        guard.can_proceed(20.0)
        assert guard.can_proceed(1.0) is False

    def test_boundary_exact_budget(self):
        guard = EconomicGuard(guard_id="G005", daily_budget=100.0, consumed_today=99.0)
        assert guard.can_proceed(1.0) is True
        guard.consume(1.0)
        assert guard.can_proceed(0.01) is False

    def test_zero_cost_proceeds(self):
        guard = EconomicGuard(guard_id="G006", daily_budget=100.0)
        assert guard.can_proceed(0.0) is True


class TestEscalationResult:
    def test_default_instantiation(self):
        evt = EscalationEvent()
        result = EscalationResult(event=evt, escalated=False, new_level=EscalationLevel.L0_SELF_HEAL)
        assert result.escalated is False
        assert result.delegated_to is None
        assert result.circuit_broken is False
        assert result.message == ""

    def test_escalated_result(self):
        evt = EscalationEvent()
        result = EscalationResult(
            event=evt,
            escalated=True,
            new_level=EscalationLevel.L3_CRITICAL,
            delegated_to="agent-002",
            circuit_broken=True,
            message="Escalated to critical",
        )
        assert result.escalated is True
        assert result.new_level == EscalationLevel.L3_CRITICAL
        assert result.delegated_to == "agent-002"
        assert result.circuit_broken is True


class TestDelegationRecord:
    def test_default_instantiation(self):
        rec = DelegationRecord()
        assert rec.delegation_id
        assert rec.from_owner == ""
        assert rec.strategy == DelegationStrategy.LOAD_BALANCED
        assert rec.accepted is False
        assert rec.completed is False

    def test_custom_fields(self):
        rec = DelegationRecord(
            from_owner="agent-A",
            to_delegate="agent-B",
            task_id="TASK-001",
            strategy=DelegationStrategy.EXPERTISE_MATCH,
        )
        assert rec.from_owner == "agent-A"
        assert rec.to_delegate == "agent-B"
        assert rec.strategy == DelegationStrategy.EXPERTISE_MATCH

    def test_unique_delegation_ids(self):
        ids = {DelegationRecord().delegation_id for _ in range(100)}
        assert len(ids) == 100


class TestDefaultEscalationRules:
    def test_rule_count(self):
        assert len(DEFAULT_ESCALATION_RULES) == 10

    def test_all_rules_enabled(self):
        for rule in DEFAULT_ESCALATION_RULES:
            assert rule.enabled is True

    def test_rule_ids_unique(self):
        ids = [r.rule_id for r in DEFAULT_ESCALATION_RULES]
        assert len(ids) == len(set(ids))

    def test_security_violation_is_emergency(self):
        sec_rule = next(r for r in DEFAULT_ESCALATION_RULES if r.category == RuleCategory.SECURITY_VIOLATION)
        assert sec_rule.target_level == EscalationLevel.L4_EMERGENCY
        assert sec_rule.priority == 100
