# [A_test] module_id: SRC-TST-0133 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-290 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT GCT集成契约测试."""

from __future__ import annotations

from zephyr.governance.bridges.alerts import BudgetAlert, BudgetSeverity
from zephyr.governance.escalation.contracts import EscalationContracts
from zephyr.governance.escalation.result_types import RollbackResult, RollbackStatus, ValidationResult
from zephyr.infrastructure.a2a_protocol import A2ACommunication, MessageType


class TestGCT003RollbackToEscalation:
    def test_rollback_result_needs_escalation(self):
        result = RollbackResult(
            rollback_id="RB-001",
            target="module_x",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.FAIL,
        )
        assert result.needs_escalation is True

    def test_rollback_result_no_escalation(self):
        result = RollbackResult(
            rollback_id="RB-002",
            target="module_y",
            status=RollbackStatus.SUCCESS,
            validation_result=ValidationResult.PASS,
        )
        assert result.needs_escalation is False

    def test_escalation_on_rollback_failure(self):
        contracts = EscalationContracts()
        result = RollbackResult(
            rollback_id="RB-FAIL",
            target="critical_module",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.FAIL,
        )
        response = contracts.on_rollback_failure(result)
        assert response["escalated"] is True
        assert response["priority"] == "P1"


class TestGCT004EscalationToRBAC:
    def test_escalation_contracts_defined(self):
        contracts = EscalationContracts()
        assert hasattr(contracts, "on_rollback_failure")
        assert hasattr(contracts, "on_budget_alert")
        assert hasattr(contracts, "on_a2a_failure")


class TestGCT005DriftToRollback:
    def test_drift_event_importable(self):
        from zephyr.gov_drift.events import ManagedDriftEvent

        assert ManagedDriftEvent is not None

    def test_drift_fix_handler(self):
        from zephyr.governance.drift_fix import DriftFixHandler
        from zephyr.gov_drift.events import ManagedDriftEvent

        event = ManagedDriftEvent(drift_id="DR-001", target="module_a", auto_fixable=True, fix_suggestion="revert to baseline")
        handler = DriftFixHandler()
        result = handler.on_drift_fix(event)
        assert result["fixed"] is True


class TestGCT006BudgetToEscalation:
    def test_budget_alert_critical(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="BA-001",
            burn_rate=0.95,
            threshold=0.8,
            remaining=0.0,
            session_id="sess_1",
        )
        assert alert.severity == BudgetSeverity.CRITICAL

    def test_budget_alert_warning(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="BA-002",
            burn_rate=0.85,
            threshold=0.8,
            remaining=1000.0,
        )
        assert alert.severity == BudgetSeverity.WARNING


class TestGCT007SpecToRBACAudit:
    def test_agent_spec_registry(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability, SpecRegistry

        registry = SpecRegistry()
        cap = AgentCapability(agent_id="agent_007", capabilities=["read", "write"])
        registry.register(cap)
        assert cap.agent_id == "agent_007"

    def test_capability_scope_restricted(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability
        from zephyr.security.access_control.capability_check import verify_capability_scope

        cap = AgentCapability(agent_id="rogue", capabilities=["destroy"])
        result = verify_capability_scope(cap)
        assert result["approved"] is False


class TestGCT008A2AToRBACEscalation:
    def test_a2a_communication_created(self):
        comm = A2ACommunication(
            a2a_id="A2A-001",
            from_agent_id="orchestrator",
            to_agent_id="worker",
            message_type=MessageType.QUERY,
        )
        assert comm.a2a_id == "A2A-001"
        assert comm.status == "PENDING"

    def test_verify_a2a_pair_allowed(self):
        from zephyr.security.access_control.a2a_check import verify_a2a_pair

        result = verify_a2a_pair("orchestrator", "worker")
        assert result["approved"] is True

    def test_verify_a2a_pair_blocked(self):
        from zephyr.security.access_control.a2a_check import verify_a2a_pair

        result = verify_a2a_pair("rogue_agent", "worker")
        assert result["approved"] is False
