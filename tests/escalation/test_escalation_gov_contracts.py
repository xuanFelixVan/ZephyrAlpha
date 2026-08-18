# [A_test] module_id: MOD-GOV_escalation_gov_contracts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_gov_contracts
# [INVARIANTS] none
# [MODIFY-GUARD] governance/contracts.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_gov_contracts.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.governance.escalation.contracts import EscalationContracts
from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity
from zephyr.shared.contracts.rollback_types import RollbackResult, RollbackStatus, ValidationResult


class TestEscalationContractsInit:
    def test_instantiation(self):
        ec = EscalationContracts()
        assert ec is not None


class TestOnRollbackFailure:
    def test_no_escalation_needed(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="RB-001",
            target="/some/path",
            status=RollbackStatus.SUCCESS,
            validation_result=ValidationResult.PASS,
        )
        out = ec.on_rollback_failure(result)
        assert out["escalated"] is False
        assert out["reason"] == "no_escalation_needed"
        assert out["rollback_id"] == "RB-001"

    def test_escalation_on_failed_status(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="RB-002",
            target="/critical/path",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.PENDING,
            error_detail="disk full",
        )
        out = ec.on_rollback_failure(result)
        assert out["escalated"] is True
        assert out["rollback_id"] == "RB-002"
        assert out["target"] == "/critical/path"
        assert out["status"] == "FAILED"
        assert out["error_detail"] == "disk full"
        assert out["ticket_id"] == "ESC-RB-002"
        assert out["priority"] == "P1"

    def test_escalation_on_fail_validation(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="RB-003",
            target="/other/path",
            status=RollbackStatus.PARTIAL,
            validation_result=ValidationResult.FAIL,
        )
        out = ec.on_rollback_failure(result)
        assert out["escalated"] is True
        assert out["priority"] == "P2"

    def test_escalation_both_failed(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="RB-004",
            target="/path",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.FAIL,
            error_detail="total failure",
        )
        out = ec.on_rollback_failure(result)
        assert out["escalated"] is True
        assert out["priority"] == "P1"

    def test_empty_rollback_id(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="",
            target="/path",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.PENDING,
        )
        out = ec.on_rollback_failure(result)
        assert out["escalated"] is True
        assert out["ticket_id"] == "ESC-"


class TestOnBudgetAlert:
    def test_warning_alert(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="BA-001",
            session_id="sess-1",
            severity=BudgetSeverity.WARNING,
        )
        out = ec.on_budget_alert(alert)
        assert out["escalated"] is True
        assert out["alert_id"] == "BA-001"
        assert out["session_id"] == "sess-1"
        assert out["severity"] == "WARNING"
        assert out["action"] == "notify"
        assert "ticket_id" not in out

    def test_critical_alert(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="BA-002",
            session_id="sess-2",
            severity=BudgetSeverity.CRITICAL,
        )
        out = ec.on_budget_alert(alert)
        assert out["escalated"] is True
        assert out["severity"] == "CRITICAL"
        assert out["action"] == "escalate"
        assert out["ticket_id"] == "ESC-BUDGET-BA-002"
        assert out["priority"] == "P0"

    def test_invalid_alert_type(self):
        ec = EscalationContracts()
        out = ec.on_budget_alert("not_an_alert")
        assert out["escalated"] is False
        assert out["reason"] == "invalid_alert_type"

    def test_invalid_alert_none(self):
        ec = EscalationContracts()
        out = ec.on_budget_alert(None)
        assert out["escalated"] is False
        assert out["reason"] == "invalid_alert_type"

    def test_invalid_alert_dict(self):
        ec = EscalationContracts()
        out = ec.on_budget_alert({"alert_id": "x"})
        assert out["escalated"] is False


class TestOnA2AFailure:
    def test_basic_failure(self):
        ec = EscalationContracts()
        comm = MagicMock()
        comm.a2a_id = "A2A-001"
        comm.from_agent_id = "agent-A"
        comm.to_agent_id = "agent-B"
        out = ec.on_a2a_failure(comm)
        assert out["escalated"] is True
        assert out["a2a_id"] == "A2A-001"
        assert out["from_agent"] == "agent-A"
        assert out["to_agent"] == "agent-B"
        assert out["action"] == "retry_or_degrade"
        assert out["ticket_id"] == "ESC-A2A-A2A-001"

    def test_missing_attributes(self):
        ec = EscalationContracts()
        comm = MagicMock(spec=[])
        out = ec.on_a2a_failure(comm)
        assert out["escalated"] is True
        assert out["a2a_id"] == ""
        assert out["from_agent"] == ""
        assert out["to_agent"] == ""
        assert out["ticket_id"] == "ESC-A2A-unknown"

    def test_empty_a2a_id(self):
        ec = EscalationContracts()
        comm = MagicMock()
        comm.a2a_id = ""
        comm.from_agent_id = "agent-X"
        comm.to_agent_id = "agent-Y"
        out = ec.on_a2a_failure(comm)
        assert out["ticket_id"] == "ESC-A2A-"
