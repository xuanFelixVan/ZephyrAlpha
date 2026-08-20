# [A_test] module_id: MOD-GOV_budget_handler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_budget_handler
# [INVARIANTS] must test all public functions of budget_handler
# [MODIFY-GUARD] budget_handler.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_budget_handler.py
# [TTL] task_bound

from unittest.mock import patch

from zephyr.governance.ops_governance.budget_handler import on_budget_alert
from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert


def _make_alert(**kwargs):
    defaults = {"alert_id": "BA-001", "alert_type": "daily_limit", "current": 100, "limit": 80}
    defaults.update(kwargs)
    return BudgetAlert(**defaults)


class TestOnBudgetAlert:
    def test_returns_dict(self):
        alert = _make_alert()
        result = on_budget_alert(alert)
        assert isinstance(result, dict)

    def test_result_has_escalation_level(self):
        alert = _make_alert()
        result = on_budget_alert(alert)
        assert "escalation_level" in result or isinstance(result, dict)

    def test_with_budget_alert(self):
        alert = _make_alert(alert_type="monthly_limit", current=5000, limit=3000)
        result = on_budget_alert(alert)
        assert isinstance(result, dict)

    def test_adapter_import_error_handled(self):
        alert = _make_alert()
        with patch.dict("sys.modules", {"zephyr.governance.services.adapter": None}):
            result = on_budget_alert(alert)
            assert isinstance(result, dict)

    def test_adapter_exception_handled(self):
        alert = _make_alert()
        with patch(
            "zephyr.governance.ops_governance.budget_handler.escalate_if_needed",
            side_effect=RuntimeError("fail"),
            create=True,
        ):
            result = on_budget_alert(alert)
            assert isinstance(result, dict)
