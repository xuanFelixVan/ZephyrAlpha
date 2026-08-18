# [A_test] module_id: MOD-GOV_escalation_contracts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_contracts
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_contracts.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.contracts import EscalationContracts
from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType
from zephyr.shared.contracts.rollback_types import RollbackResult, RollbackStatus, ValidationResult


class TestEscalationContractsInstantiation:
    def test_create_instance(self):
        ec = EscalationContracts()
        assert ec is not None

    def test_has_on_rollback_failure(self):
        ec = EscalationContracts()
        assert callable(getattr(ec, "on_rollback_failure", None))

    def test_has_on_budget_alert(self):
        ec = EscalationContracts()
        assert callable(getattr(ec, "on_budget_alert", None))

    def test_has_on_a2a_failure(self):
        ec = EscalationContracts()
        assert callable(getattr(ec, "on_a2a_failure", None))


class TestOnRollbackFailure:
    def test_no_escalation_needed(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="rb-001",
            target="file_a.py",
            status=RollbackStatus.SUCCESS,
            validation_result=ValidationResult.PASS,
        )
        response = ec.on_rollback_failure(result)
        assert response["escalated"] is False
        assert response["reason"] == "no_escalation_needed"

    def test_escalation_on_failed_status(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="rb-002",
            target="file_b.py",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.PENDING,
            error_detail="disk full",
        )
        response = ec.on_rollback_failure(result)
        assert response["escalated"] is True
        assert response["rollback_id"] == "rb-002"
        assert response["target"] == "file_b.py"
        assert response["priority"] == "P1"
        assert response["ticket_id"] == "ESC-rb-002"

    def test_escalation_on_failed_validation(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="rb-003",
            target="file_c.py",
            status=RollbackStatus.PARTIAL,
            validation_result=ValidationResult.FAIL,
        )
        response = ec.on_rollback_failure(result)
        assert response["escalated"] is True
        assert response["priority"] == "P2"

    def test_rollback_id_in_response(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="rb-unique",
            target="target.py",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.PENDING,
        )
        response = ec.on_rollback_failure(result)
        assert response["rollback_id"] == "rb-unique"

    def test_error_detail_propagated(self):
        ec = EscalationContracts()
        result = RollbackResult(
            rollback_id="rb-004",
            target="file_d.py",
            status=RollbackStatus.FAILED,
            validation_result=ValidationResult.PENDING,
            error_detail="permission denied",
        )
        response = ec.on_rollback_failure(result)
        assert response["error_detail"] == "permission denied"


class TestOnBudgetAlert:
    def test_invalid_alert_type(self):
        ec = EscalationContracts()
        response = ec.on_budget_alert("not_a_budget_alert")
        assert response["escalated"] is False
        assert response["reason"] == "invalid_alert_type"

    def test_warning_alert(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="ba-001",
            session_id="sess-001",
            severity=BudgetSeverity.WARNING,
            budget_type=BudgetType.TOKEN,
        )
        response = ec.on_budget_alert(alert)
        assert response["escalated"] is True
        assert response["action"] == "notify"
        assert response["severity"] == "WARNING"

    def test_critical_alert(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="ba-002",
            session_id="sess-002",
            severity=BudgetSeverity.CRITICAL,
            budget_type=BudgetType.TIME,
        )
        response = ec.on_budget_alert(alert)
        assert response["escalated"] is True
        assert response["action"] == "escalate"
        assert response["severity"] == "CRITICAL"
        assert response["priority"] == "P0"
        assert response["ticket_id"] == "ESC-BUDGET-ba-002"

    def test_alert_id_in_response(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="ba-unique",
            session_id="sess-003",
            severity=BudgetSeverity.WARNING,
        )
        response = ec.on_budget_alert(alert)
        assert response["alert_id"] == "ba-unique"

    def test_session_id_in_response(self):
        ec = EscalationContracts()
        alert = BudgetAlert(
            alert_id="ba-003",
            session_id="sess-unique",
            severity=BudgetSeverity.WARNING,
        )
        response = ec.on_budget_alert(alert)
        assert response["session_id"] == "sess-unique"


class TestOnA2AFailure:
    def test_basic_a2a_failure(self):
        ec = EscalationContracts()

        class FakeCommunication:
            a2a_id = "a2a-001"
            from_agent_id = "agent_a"
            to_agent_id = "agent_b"

        response = ec.on_a2a_failure(FakeCommunication())
        assert response["escalated"] is True
        assert response["a2a_id"] == "a2a-001"
        assert response["from_agent"] == "agent_a"
        assert response["to_agent"] == "agent_b"
        assert response["action"] == "retry_or_degrade"
        assert response["ticket_id"] == "ESC-A2A-a2a-001"

    def test_a2a_failure_missing_attributes(self):
        ec = EscalationContracts()

        class MinimalCommunication:
            a2a_id = "a2a-002"

        response = ec.on_a2a_failure(MinimalCommunication())
        assert response["escalated"] is True
        assert response["from_agent"] == ""
        assert response["to_agent"] == ""

    def test_a2a_failure_no_attributes(self):
        ec = EscalationContracts()
        response = ec.on_a2a_failure(object())
        assert response["escalated"] is True
        assert response["a2a_id"] == ""
        assert response["ticket_id"] == "ESC-A2A-unknown"

    def test_a2a_ticket_id_format(self):
        ec = EscalationContracts()

        class Comm:
            a2a_id = "xyz-999"

        response = ec.on_a2a_failure(Comm())
        assert response["ticket_id"] == "ESC-A2A-xyz-999"
