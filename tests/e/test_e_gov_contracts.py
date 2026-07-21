# [A_test] module_id: MOD-GOV_e_gov_contracts | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gov_contracts
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

from unittest.mock import MagicMock

from zephyr.governance.escalation.contracts import EscalationContracts


class TestEscalationContractsOnRollbackFailure:
    def test_no_escalation_needed(self):
        ec = EscalationContracts()
        result = MagicMock()
        result.needs_escalation = False
        result.rollback_id = "RB-001"
        output = ec.on_rollback_failure(result)
        assert output["escalated"] is False
        assert output["reason"] == "no_escalation_needed"
        assert output["rollback_id"] == "RB-001"

    def test_escalated_with_failed_status(self):
        ec = EscalationContracts()
        result = MagicMock()
        result.needs_escalation = True
        result.rollback_id = "RB-002"
        result.target = "module_x"
        result.status.value = "FAILED"
        result.validation_result.value = "NOT_VALIDATED"
        result.error_detail = "critical error"
        output = ec.on_rollback_failure(result)
        assert output["escalated"] is True
        assert output["priority"] == "P1"
        assert output["ticket_id"] == "ESC-RB-002"

    def test_escalated_with_success_status(self):
        ec = EscalationContracts()
        result = MagicMock()
        result.needs_escalation = True
        result.rollback_id = "RB-003"
        result.target = "module_y"
        result.status.value = "SUCCESS"
        result.validation_result.value = "VALIDATED"
        result.error_detail = ""
        output = ec.on_rollback_failure(result)
        assert output["escalated"] is True
        assert output["priority"] == "P2"


class TestEscalationContractsOnBudgetAlert:
    def test_invalid_alert_type(self):
        ec = EscalationContracts()
        output = ec.on_budget_alert("not_a_budget_alert")
        assert output["escalated"] is False
        assert output["reason"] == "invalid_alert_type"

    def test_warning_severity(self):
        from unittest.mock import MagicMock

        ec = EscalationContracts()
        with MagicMock() as mock_budget:
            from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

            mock_budget.__class__ = BudgetAlert
            mock_budget.alert_id = "BA-001"
            mock_budget.session_id = "session-1"
            mock_budget.severity.value = "WARNING"

            output = ec.on_budget_alert(mock_budget)
            assert output["escalated"] is True
            assert output["action"] == "notify"
            assert "ticket_id" not in output

    def test_critical_severity(self):
        from unittest.mock import MagicMock

        ec = EscalationContracts()
        with MagicMock() as mock_budget:
            from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

            mock_budget.__class__ = BudgetAlert
            mock_budget.alert_id = "BA-002"
            mock_budget.session_id = "session-2"
            mock_budget.severity.value = "CRITICAL"

            output = ec.on_budget_alert(mock_budget)
            assert output["escalated"] is True
            assert output["action"] == "escalate"
            assert output["ticket_id"] == "ESC-BUDGET-BA-002"
            assert output["priority"] == "P0"


class TestEscalationContractsOnA2AFailure:
    def test_with_all_attributes(self):
        ec = EscalationContracts()
        comm = MagicMock()
        comm.a2a_id = "a2a-001"
        comm.from_agent_id = "agent-a"
        comm.to_agent_id = "agent-b"
        output = ec.on_a2a_failure(comm)
        assert output["escalated"] is True
        assert output["a2a_id"] == "a2a-001"
        assert output["from_agent"] == "agent-a"
        assert output["to_agent"] == "agent-b"
        assert output["ticket_id"] == "ESC-A2A-a2a-001"

    def test_missing_attributes(self):
        ec = EscalationContracts()
        comm = type("Empty", (), {})()
        output = ec.on_a2a_failure(comm)
        assert output["escalated"] is True
        assert output["a2a_id"] == ""
        assert output["ticket_id"] == "ESC-A2A-unknown"
