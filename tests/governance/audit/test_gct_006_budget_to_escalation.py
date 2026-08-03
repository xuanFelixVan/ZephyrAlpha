# [A_test] module_id: SRC-TST-0129 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-286 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_006_budget_to_escalation
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-286 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G-CT-006 — Budget → Escalation 集成测试."""

from __future__ import annotations


class TestGCT006BudgetToEscalation:
    """验证 budget-enforcer/alerts.py 的 BudgetAlert 可被 escalation/budget_handler.py 处理."""

    def test_budget_alert_creatable(self):
        from zephyr.governance.bridges.alerts import BudgetAlert

        a = BudgetAlert(alert_id="B001")
        assert a.alert_id == "B001"

    def test_budget_handler_accepts_alert(self):
        from zephyr.governance.bridges.alerts import BudgetAlert
        from zephyr.governance.ops_governance.budget_handler import on_budget_alert

        a = BudgetAlert(alert_id="B001")
        result = on_budget_alert(a)
        assert result is not None

    def test_budget_severity_enum(self):
        from zephyr.governance.bridges.alerts import BudgetSeverity

        assert BudgetSeverity.WARNING is not None
        assert BudgetSeverity.CRITICAL is not None
