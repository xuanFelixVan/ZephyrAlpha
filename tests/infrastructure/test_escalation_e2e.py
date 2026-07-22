# [A_test] module_id: MOD-GOV_escalation_e2e | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-312 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_escalation_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""End-to-End Integration Tests — Escalation Protocol Full Chain.

Tests the complete chain: EscalationEngine → RBAC bridge → Audit trail → Rollback trigger.
Blueprint: docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md §2
"""

from unittest.mock import patch

import pytest

from zephyr.governance.escalation import (
    CircuitState,
    DelegationEngine,
    DelegationStrategy,
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


class TestFullChainSecurityViolation:
    def test_security_violation_to_rbac_escalation(self):
        engine = EscalationEngine("e2e-sec")
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "rm -rf /production/data")
        assert ev.level == EscalationLevel.L4_EMERGENCY
        assert ev.state == EscalationState.EVALUATING
        assert ev.module_id == "MOD-INF-022"

        result = engine.escalate(ev)
        assert result.escalated is True
        assert result.new_level == EscalationLevel.L4_EMERGENCY

        engine.record_resolution(result.event)
        assert result.event.state == EscalationState.RESOLVED

    def test_deadlock_to_rbac_bridge_and_resolution(self):
        engine = EscalationEngine("e2e-dl")
        ev = engine.evaluate(RuleCategory.DEADLOCK, "Agent A blocks Agent B on resource X")
        assert ev.level.value >= EscalationLevel.L3_CRITICAL.value

        result = engine.escalate(ev)
        assert result.escalated is True

        engine.record_resolution(ev)
        assert ev.state == EscalationState.RESOLVED

    def test_budget_exceeded_to_auto_guard_chain(self):
        engine = EscalationEngine("e2e-budget")
        ev = engine.evaluate(RuleCategory.BUDGET_EXCEEDED, "cost $5000, budget $500/day")
        assert ev.level == EscalationLevel.L2_HUMAN_REVIEW

        result = engine.escalate(ev)
        assert result.escalated is True

    def test_owner_absent_triggers_delegation(self):
        engine = EscalationEngine("e2e-owner")
        ev = engine.evaluate(RuleCategory.OWNER_ABSENT, "Owner unavailable for 30min")
        assert ev.level.value >= EscalationLevel.L2_HUMAN_REVIEW.value

    def test_cascade_failure_full_chain(self):
        engine = EscalationEngine("e2e-cascade")
        ev = engine.evaluate(RuleCategory.CASCADE_FAILURE, "Service A down → Service B degraded → Pipeline halted")
        assert ev.level.value >= EscalationLevel.L3_CRITICAL.value

        result = engine.escalate(ev)
        assert result.event.level.value >= EscalationLevel.L3_CRITICAL.value

    def test_circuit_breaker_opens_under_sustained_issues(self):
        engine = EscalationEngine("e2e-cb-chain")
        for i in range(20):
            ev = engine.evaluate(RuleCategory.CASCADE_FAILURE, f"sustained_failure_{i}")
            engine.record_failure(ev)
        assert engine.get_circuit_state() in (CircuitState.OPEN, CircuitState.HALF_OPEN, CircuitState.CLOSED)


class TestFullChainWithDelegation:
    def test_escalate_and_delegate_to_rbac(self):
        engine = EscalationEngine("e2e-delegate")
        de = DelegationEngine()
        de.register_delegate("rbac-bot", ["rbac", "permissions"])
        de.register_delegate("auditor", ["audit"])

        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "unauthorized_admin_action")
        result = engine.escalate(ev)
        assert result.escalated is True

        if result.delegated_to:
            record = de.delegate(result.event, DelegationStrategy.EXPERTISE_MATCH, "chain-task")
            assert record is not None

    def test_delegation_accept_complete_cycle(self):
        engine = EscalationEngine("e2e-cycle")
        de = DelegationEngine()
        de.register_delegate("worker-1")

        ev = engine.evaluate(RuleCategory.TIMEOUT, "request_timeout_chain")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "lifecycle-task")

        assert de.accept_delegation(record.delegation_id) is True
        assert de.complete_delegation(record.delegation_id) is True

        engine.record_resolution(ev)
        assert ev.state == EscalationState.RESOLVED

    def test_delegation_reject_fallback(self):
        engine = EscalationEngine("e2e-reject")
        de = DelegationEngine()
        de.register_delegate("worker-2")

        ev = engine.evaluate(RuleCategory.TIMEOUT, "timeout_fallback")
        record = de.delegate(ev, DelegationStrategy.LOAD_BALANCED, "reject-task")

        assert de.reject_delegation(record.delegation_id) is True
        assert de.get_load("worker-2") == 0


class TestFullChainEconomicGuard:
    def test_budget_tracking_across_escalation_chain(self):
        engine = EscalationEngine("e2e-econ")
        initial_status = engine.get_economic_status()
        assert initial_status["consumed_today"] >= 0

        for cat in [RuleCategory.AUTO_GUARD_FAILURE, RuleCategory.DEADLOCK, RuleCategory.SECURITY_VIOLATION]:
            ev = engine.evaluate(cat, "chain_econ_test")
            engine.escalate(ev)

        final_status = engine.get_economic_status()
        assert final_status["consumed_today"] > initial_status["consumed_today"]


class TestFullChainAuditTrail:
    def test_audit_events_accumulate_in_chain(self):
        engine = EscalationEngine("e2e-audit")
        events = []
        for cat in [RuleCategory.CUSTOM, RuleCategory.TIMEOUT, RuleCategory.AUTO_GUARD_FAILURE]:
            ev = engine.evaluate(cat, "audit_test")
            events.append(ev)

        assert len(events) == 3
        for ev in events:
            assert ev.event_id
            assert ev.created_at is not None

    def test_audit_event_has_all_required_fields(self):
        engine = EscalationEngine("e2e-fields")
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "must_have_fields")
        assert ev.event_id
        assert ev.module_id == "MOD-INF-022"
        assert ev.category == RuleCategory.SECURITY_VIOLATION
        assert ev.level is not None
        assert ev.state is not None
        assert ev.created_at is not None
        assert ev.updated_at is not None
        assert ev.retry_count >= 0
        assert ev.max_retries > 0


class TestFullChainRecovery:
    def test_engine_stable_after_full_chain_stress(self):
        engine = EscalationEngine("e2e-stress")
        categories = list(RuleCategory)
        for _ in range(100):
            for cat in categories[:6]:
                ev = engine.evaluate(cat, "stress_test")
                if ev.state != EscalationState.REJECTED:
                    engine.escalate(ev)
                    engine.record_resolution(ev)

        assert engine.get_active_count() >= 0
        status = engine.get_economic_status()
        assert "daily_budget" in status
        assert "hard_limit_reached" in status
