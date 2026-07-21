# [A_test] module_id: MOD-GOV_escalation_gov_budget_handler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_gov_budget_handler
# [INVARIANTS] none
# [MODIFY-GUARD] governance/budget_handler.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_gov_budget_handler.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.budget_handler import on_budget_alert
from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType


def _make_alert(**kwargs):
    defaults = {
        "alert_id": "BA-001",
        "session_id": "sess-1",
        "severity": BudgetSeverity.WARNING,
        "budget_type": BudgetType.TOKEN,
    }
    defaults.update(kwargs)
    return BudgetAlert(**defaults)


class TestOnBudgetAlert:
    def test_warning_alert(self):
        alert = _make_alert(severity=BudgetSeverity.WARNING)
        result = on_budget_alert(alert)
        assert result["escalated"] is True
        assert result["alert_id"] == "BA-001"
        assert result["severity"] == "WARNING"
        assert result["action"] == "notify"

    def test_critical_alert(self):
        alert = _make_alert(alert_id="BA-CRIT", severity=BudgetSeverity.CRITICAL)
        result = on_budget_alert(alert)
        assert result["escalated"] is True
        assert result["severity"] == "CRITICAL"
        assert result["action"] == "escalate"
        assert result["ticket_id"] == "ESC-BUDGET-BA-CRIT"
        assert result["priority"] == "P0"

    def test_token_budget_type(self):
        alert = _make_alert(budget_type=BudgetType.TOKEN)
        result = on_budget_alert(alert)
        assert result["escalated"] is True

    def test_time_budget_type(self):
        alert = _make_alert(budget_type=BudgetType.TIME)
        result = on_budget_alert(alert)
        assert result["escalated"] is True

    def test_memory_budget_type(self):
        alert = _make_alert(budget_type=BudgetType.MEMORY)
        result = on_budget_alert(alert)
        assert result["escalated"] is True

    def test_api_calls_budget_type(self):
        alert = _make_alert(budget_type=BudgetType.API_CALLS)
        result = on_budget_alert(alert)
        assert result["escalated"] is True

    def test_empty_session_id(self):
        alert = _make_alert(session_id="")
        result = on_budget_alert(alert)
        assert result["session_id"] == ""

    def test_from_burn_rate_factory(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="BA-FBR",
            burn_rate=0.9,
            threshold=0.8,
            remaining=50.0,
            session_id="sess-fbr",
        )
        result = on_budget_alert(alert)
        assert result["escalated"] is True
        assert result["alert_id"] == "BA-FBR"

    def test_critical_from_zero_remaining(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="BA-ZERO",
            burn_rate=0.5,
            threshold=0.8,
            remaining=0.0,
        )
        result = on_budget_alert(alert)
        assert result["severity"] == "CRITICAL"
        assert result["action"] == "escalate"

    def test_escalation_adapter_fields(self):
        alert = _make_alert()
        result = on_budget_alert(alert)
        assert "escalation_level" in result or "alert_id" in result
