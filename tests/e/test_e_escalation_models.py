# [A_test] module_id: MOD-GOV_e_escalation_models | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_escalation_models
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

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
    def test_member_count(self):
        assert len(EscalationLevel) == 5

    def test_values(self):
        assert EscalationLevel.L0_SELF_HEAL.value == 0
        assert EscalationLevel.L1_AUTO_FIX.value == 1
        assert EscalationLevel.L2_HUMAN_REVIEW.value == 2
        assert EscalationLevel.L3_CRITICAL.value == 3
        assert EscalationLevel.L4_EMERGENCY.value == 4

    def test_member_access(self):
        assert EscalationLevel(0) is EscalationLevel.L0_SELF_HEAL
        assert EscalationLevel(1) is EscalationLevel.L1_AUTO_FIX
        assert EscalationLevel(2) is EscalationLevel.L2_HUMAN_REVIEW
        assert EscalationLevel(3) is EscalationLevel.L3_CRITICAL
        assert EscalationLevel(4) is EscalationLevel.L4_EMERGENCY


class TestEscalationState:
    def test_member_count(self):
        assert len(EscalationState) == 7

    def test_values(self):
        assert EscalationState.DETECTED.value == "DETECTED"
        assert EscalationState.EVALUATING.value == "EVALUATING"
        assert EscalationState.ESCALATED.value == "ESCALATED"
        assert EscalationState.DELEGATED.value == "DELEGATED"
        assert EscalationState.RESOLVED.value == "RESOLVED"
        assert EscalationState.REJECTED.value == "REJECTED"
        assert EscalationState.TIMED_OUT.value == "TIMED_OUT"


class TestRuleCategory:
    def test_member_count(self):
        assert len(RuleCategory) == 11

    def test_values(self):
        assert RuleCategory.AUTO_GUARD_FAILURE.value == "auto_guard_failure"
        assert RuleCategory.BUDGET_EXCEEDED.value == "budget_exceeded"
        assert RuleCategory.DRIFT_DETECTED.value == "drift_detected"
        assert RuleCategory.DEADLOCK.value == "deadlock"
        assert RuleCategory.TIMEOUT.value == "timeout"
        assert RuleCategory.QUALITY_DEGRADATION.value == "quality_degradation"
        assert RuleCategory.SECURITY_VIOLATION.value == "security_violation"
        assert RuleCategory.OWNER_ABSENT.value == "owner_absent"
        assert RuleCategory.CASCADE_FAILURE.value == "cascade_failure"
        assert RuleCategory.REWARD_HACKING_REBOUND.value == "reward_hacking_rebound"
        assert RuleCategory.CUSTOM.value == "custom"


class TestDelegationStrategy:
    def test_member_count(self):
        assert len(DelegationStrategy) == 5

    def test_values(self):
        assert DelegationStrategy.LOAD_BALANCED.value == "load_balanced"
        assert DelegationStrategy.EXPERTISE_MATCH.value == "expertise_match"
        assert DelegationStrategy.ROUND_ROBIN.value == "round_robin"
        assert DelegationStrategy.PRIORITY_QUEUE.value == "priority_queue"
        assert DelegationStrategy.NONE.value == "none"


class TestEscalationEvent:
    def test_default_instantiation(self):
        event = EscalationEvent()
        assert isinstance(event.event_id, str)
        assert len(event.event_id) > 0
        assert event.module_id == "MOD-INF-022"
        assert event.source_event_id is None
        assert event.category is RuleCategory.CUSTOM
        assert event.level is EscalationLevel.L0_SELF_HEAL
        assert event.state is EscalationState.DETECTED
        assert event.description == ""
        assert event.owner_id is None
        assert event.delegate_id is None
        assert event.retry_count == 0
        assert event.max_retries == 3
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)
        assert event.resolved_at is None
        assert event.circuit_breaker_triggered is False
        assert event.economic_guard_passed is True
        assert event.metadata == {}

    def test_custom_instantiation(self):
        now = datetime.now(UTC)
        event = EscalationEvent(
            event_id="evt-001",
            module_id="MOD-TEST-001",
            source_event_id="evt-000",
            category=RuleCategory.SECURITY_VIOLATION,
            level=EscalationLevel.L4_EMERGENCY,
            state=EscalationState.ESCALATED,
            description="test event",
            owner_id="owner-1",
            delegate_id="delegate-1",
            retry_count=2,
            max_retries=5,
            created_at=now,
            updated_at=now,
            resolved_at=now,
            circuit_breaker_triggered=True,
            economic_guard_passed=False,
            metadata={"key": "value"},
        )
        assert event.event_id == "evt-001"
        assert event.module_id == "MOD-TEST-001"
        assert event.source_event_id == "evt-000"
        assert event.category is RuleCategory.SECURITY_VIOLATION
        assert event.level is EscalationLevel.L4_EMERGENCY
        assert event.state is EscalationState.ESCALATED
        assert event.description == "test event"
        assert event.owner_id == "owner-1"
        assert event.delegate_id == "delegate-1"
        assert event.retry_count == 2
        assert event.max_retries == 5
        assert event.created_at == now
        assert event.updated_at == now
        assert event.resolved_at == now
        assert event.circuit_breaker_triggered is True
        assert event.economic_guard_passed is False
        assert event.metadata == {"key": "value"}


class TestEscalationRule:
    def test_minimal_instantiation(self):
        rule = EscalationRule(
            rule_id="R-TEST",
            category=RuleCategory.DEADLOCK,
            target_level=EscalationLevel.L3_CRITICAL,
        )
        assert rule.rule_id == "R-TEST"
        assert rule.category is RuleCategory.DEADLOCK
        assert rule.target_level is EscalationLevel.L3_CRITICAL
        assert rule.priority == 0
        assert rule.condition == ""
        assert rule.auto_escalate is True
        assert rule.cooldown_seconds == 300
        assert rule.max_escalations_per_hour == 10
        assert rule.delegate_strategy is DelegationStrategy.NONE
        assert rule.notification_channels == []
        assert rule.enabled is True

    def test_full_instantiation(self):
        rule = EscalationRule(
            rule_id="R-FULL",
            category=RuleCategory.SECURITY_VIOLATION,
            target_level=EscalationLevel.L4_EMERGENCY,
            priority=100,
            condition="severity > 9",
            auto_escalate=False,
            cooldown_seconds=30,
            max_escalations_per_hour=5,
            delegate_strategy=DelegationStrategy.PRIORITY_QUEUE,
            notification_channels=["slack", "email"],
            enabled=False,
        )
        assert rule.rule_id == "R-FULL"
        assert rule.priority == 100
        assert rule.condition == "severity > 9"
        assert rule.auto_escalate is False
        assert rule.cooldown_seconds == 30
        assert rule.max_escalations_per_hour == 5
        assert rule.delegate_strategy is DelegationStrategy.PRIORITY_QUEUE
        assert rule.notification_channels == ["slack", "email"]
        assert rule.enabled is False


class TestEconomicGuard:
    def test_can_proceed_within_budget(self):
        guard = EconomicGuard("G-001", daily_budget=100.0, consumed_today=30.0)
        assert guard.can_proceed(estimated_cost=50.0) is True
        assert guard.hard_limit_reached is False

    def test_can_proceed_exceeds_budget(self):
        guard = EconomicGuard("G-002", daily_budget=100.0, consumed_today=80.0)
        assert guard.can_proceed(estimated_cost=30.0) is False
        assert guard.hard_limit_reached is True

    def test_can_proceed_hard_limit_reached(self):
        guard = EconomicGuard("G-003", daily_budget=100.0, consumed_today=0.0, hard_limit_reached=True)
        assert guard.can_proceed(estimated_cost=1.0) is False

    def test_consume_updates_consumed_today(self):
        guard = EconomicGuard("G-004", daily_budget=100.0, consumed_today=10.0)
        guard.consume(25.0)
        assert guard.consumed_today == 35.0

    def test_consume_multiple(self):
        guard = EconomicGuard("G-005", daily_budget=100.0, consumed_today=0.0)
        guard.consume(10.0)
        guard.consume(20.0)
        guard.consume(30.0)
        assert guard.consumed_today == 60.0

    def test_maybe_reset_after_one_day(self, monkeypatch):
        old_time = datetime(2026, 5, 21, 10, 0, 0, tzinfo=UTC)
        new_time = datetime(2026, 5, 22, 10, 0, 0, tzinfo=UTC)

        guard = EconomicGuard("G-006", daily_budget=100.0, consumed_today=90.0, hard_limit_reached=True)
        guard.last_reset = old_time

        monkeypatch.setattr("zephyr.governance.escalation.escalation_models.datetime", _FakeDatetime(new_time))

        guard._maybe_reset()
        assert guard.consumed_today == 0.0
        assert guard.hard_limit_reached is False
        assert guard.last_reset == new_time

    def test_maybe_reset_same_day_noop(self, monkeypatch):
        old_time = datetime(2026, 5, 22, 10, 0, 0, tzinfo=UTC)
        same_day = datetime(2026, 5, 22, 23, 59, 59, tzinfo=UTC)

        guard = EconomicGuard("G-007", daily_budget=100.0, consumed_today=90.0, hard_limit_reached=True)
        guard.last_reset = old_time

        monkeypatch.setattr("zephyr.governance.escalation.escalation_models.datetime", _FakeDatetime(same_day))

        guard._maybe_reset()
        assert guard.consumed_today == 90.0
        assert guard.hard_limit_reached is True

    def test_zero_estimated_cost(self):
        guard = EconomicGuard("G-008", daily_budget=100.0, consumed_today=100.0)
        assert guard.can_proceed(estimated_cost=0.0) is True
        assert guard.hard_limit_reached is False

    def test_zero_daily_budget(self):
        guard = EconomicGuard("G-009", daily_budget=0.0, consumed_today=0.0)
        assert guard.can_proceed(estimated_cost=0.0) is True

    def test_zero_daily_budget_positive_cost(self):
        guard = EconomicGuard("G-010", daily_budget=0.0, consumed_today=0.0)
        assert guard.can_proceed(estimated_cost=1.0) is False
        assert guard.hard_limit_reached is True

    def test_can_proceed_triggers_reset(self, monkeypatch):
        old_time = datetime(2026, 5, 21, 10, 0, 0, tzinfo=UTC)
        new_time = datetime(2026, 5, 22, 10, 0, 0, tzinfo=UTC)

        guard = EconomicGuard("G-011", daily_budget=100.0, consumed_today=90.0, hard_limit_reached=True)
        guard.last_reset = old_time

        monkeypatch.setattr("zephyr.governance.escalation.escalation_models.datetime", _FakeDatetime(new_time))

        assert guard.can_proceed(estimated_cost=50.0) is True
        assert guard.consumed_today == 0.0
        assert guard.hard_limit_reached is False


class TestEscalationResult:
    def test_instantiation(self):
        event = EscalationEvent(event_id="evt-001")
        result = EscalationResult(
            event=event,
            escalated=True,
            new_level=EscalationLevel.L2_HUMAN_REVIEW,
            delegated_to="agent-007",
            circuit_broken=False,
            message="escalated successfully",
            suggestion="review the security alert",
        )
        assert result.event is event
        assert result.escalated is True
        assert result.new_level is EscalationLevel.L2_HUMAN_REVIEW
        assert result.delegated_to == "agent-007"
        assert result.circuit_broken is False
        assert result.message == "escalated successfully"
        assert result.suggestion == "review the security alert"

    def test_defaults(self):
        event = EscalationEvent(event_id="evt-002")
        result = EscalationResult(
            event=event,
            escalated=False,
            new_level=EscalationLevel.L0_SELF_HEAL,
        )
        assert result.delegated_to is None
        assert result.circuit_broken is False
        assert result.message == ""
        assert result.suggestion == ""


class TestDelegationRecord:
    def test_default_instantiation(self):
        record = DelegationRecord()
        assert isinstance(record.delegation_id, str)
        assert len(record.delegation_id) > 0
        assert record.from_owner == ""
        assert record.to_delegate == ""
        assert record.task_id is None
        assert record.strategy is DelegationStrategy.LOAD_BALANCED
        assert isinstance(record.created_at, datetime)
        assert record.expires_at is None
        assert record.accepted is False
        assert record.completed is False

    def test_custom_instantiation(self):
        now = datetime.now(UTC)
        expires = now + timedelta(hours=1)
        record = DelegationRecord(
            delegation_id="del-001",
            from_owner="owner-1",
            to_delegate="delegate-1",
            task_id="task-001",
            strategy=DelegationStrategy.EXPERTISE_MATCH,
            created_at=now,
            expires_at=expires,
            accepted=True,
            completed=True,
        )
        assert record.delegation_id == "del-001"
        assert record.from_owner == "owner-1"
        assert record.to_delegate == "delegate-1"
        assert record.task_id == "task-001"
        assert record.strategy is DelegationStrategy.EXPERTISE_MATCH
        assert record.created_at == now
        assert record.expires_at == expires
        assert record.accepted is True
        assert record.completed is True


class TestDefaultEscalationRules:
    def test_count(self):
        assert len(DEFAULT_ESCALATION_RULES) == 10

    def test_all_unique_rule_ids(self):
        rule_ids = [rule.rule_id for rule in DEFAULT_ESCALATION_RULES]
        assert len(rule_ids) == len(set(rule_ids))

    def test_various_categories(self):
        categories = {rule.category for rule in DEFAULT_ESCALATION_RULES}
        expected = {
            RuleCategory.AUTO_GUARD_FAILURE,
            RuleCategory.BUDGET_EXCEEDED,
            RuleCategory.DRIFT_DETECTED,
            RuleCategory.DEADLOCK,
            RuleCategory.TIMEOUT,
            RuleCategory.QUALITY_DEGRADATION,
            RuleCategory.SECURITY_VIOLATION,
            RuleCategory.OWNER_ABSENT,
            RuleCategory.CASCADE_FAILURE,
            RuleCategory.REWARD_HACKING_REBOUND,
        }
        assert categories == expected

    def test_expected_rule_ids(self):
        rule_ids = [rule.rule_id for rule in DEFAULT_ESCALATION_RULES]
        assert rule_ids == ["R001", "R002", "R003", "R004", "R005", "R006", "R007", "R008", "R009", "R010"]

    def test_various_target_levels(self):
        levels = {rule.target_level for rule in DEFAULT_ESCALATION_RULES}
        assert EscalationLevel.L1_AUTO_FIX in levels
        assert EscalationLevel.L2_HUMAN_REVIEW in levels
        assert EscalationLevel.L3_CRITICAL in levels
        assert EscalationLevel.L4_EMERGENCY in levels

    def test_rules_are_enabled_by_default(self):
        for rule in DEFAULT_ESCALATION_RULES:
            assert rule.enabled is True

    def test_security_violation_rule(self):
        rule = next(r for r in DEFAULT_ESCALATION_RULES if r.rule_id == "R007")
        assert rule.category is RuleCategory.SECURITY_VIOLATION
        assert rule.target_level is EscalationLevel.L4_EMERGENCY
        assert rule.priority == 100
        assert rule.cooldown_seconds == 30

    def test_reward_hacking_rebound_rule(self):
        rule = next(r for r in DEFAULT_ESCALATION_RULES if r.rule_id == "R010")
        assert rule.category is RuleCategory.REWARD_HACKING_REBOUND
        assert rule.target_level is EscalationLevel.L4_EMERGENCY
        assert rule.priority == 200
        assert rule.cooldown_seconds == 0
        assert rule.delegate_strategy is DelegationStrategy.NONE


class _FakeDatetime:
    def __init__(self, fixed_time):
        self._fixed_time = fixed_time

    def now(self, tz=None):
        return self._fixed_time

    def __getattr__(self, name):
        return getattr(datetime, name)
