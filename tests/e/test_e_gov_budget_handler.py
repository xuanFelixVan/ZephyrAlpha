# [A_test] module_id: MOD-GOV_e_gov_budget_handler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gov_budget_handler
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

from zephyr.governance.ops_governance.budget_handler import on_budget_alert


class TestOnBudgetAlert:
    def test_warning_alert(self):
        alert = MagicMock()
        alert.alert_id = "BA-001"
        alert.session_id = "session-1"
        alert.severity.value = "WARNING"
        alert.__class__.__name__ = "BudgetAlert"

        from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

        alert.__class__ = BudgetAlert

        result = on_budget_alert(alert)
        assert result["escalated"] is True
        assert result["action"] == "notify"

    def test_critical_alert(self):
        alert = MagicMock()
        alert.alert_id = "BA-002"
        alert.session_id = "session-2"
        alert.severity.value = "CRITICAL"
        alert.__class__.__name__ = "BudgetAlert"

        from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

        alert.__class__ = BudgetAlert

        result = on_budget_alert(alert)
        assert result["escalated"] is True
        assert result["action"] == "escalate"
        assert result["priority"] == "P0"

    def test_invalid_alert_type(self):
        result = on_budget_alert("not_an_alert")
        assert result["escalated"] is False
        assert result["reason"] == "invalid_alert_type"
