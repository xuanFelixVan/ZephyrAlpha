# [A_test] module_id: SRC-TST-0306 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §12
# [MODULE] tests.test_alerts
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_alerts.py
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.bridges.alerts import BudgetAlert, BudgetSeverity, BudgetType


class TestBudgetSeverity:
    def test_enum_values(self):
        assert BudgetSeverity.WARNING == "WARNING"
        assert BudgetSeverity.CRITICAL == "CRITICAL"

    def test_enum_members(self):
        members = list(BudgetSeverity)
        assert len(members) == 2


class TestBudgetType:
    def test_enum_values(self):
        assert BudgetType.TOKEN == "TOKEN"
        assert BudgetType.TIME == "TIME"
        assert BudgetType.MEMORY == "MEMORY"
        assert BudgetType.API_CALLS == "API_CALLS"

    def test_enum_members(self):
        members = list(BudgetType)
        assert len(members) == 4


class TestBudgetAlert:
    def test_creation_defaults(self):
        alert = BudgetAlert(alert_id="test-001")
        assert alert.alert_id == "test-001"
        assert alert.session_id == ""
        assert alert.budget_type == BudgetType.TOKEN
        assert alert.severity == BudgetSeverity.WARNING
        assert alert.burn_rate == 0.0
        assert alert.remaining_budget == 0.0

    def test_creation_with_all_fields(self):
        alert = BudgetAlert(
            alert_id="test-002",
            session_id="sess-1",
            budget_type=BudgetType.API_CALLS,
            burn_rate=0.9,
            burn_rate_threshold=0.8,
            remaining_budget=10.0,
            severity=BudgetSeverity.CRITICAL,
        )
        assert alert.session_id == "sess-1"
        assert alert.budget_type == BudgetType.API_CALLS
        assert alert.burn_rate == 0.9
        assert alert.severity == BudgetSeverity.CRITICAL

    def test_from_burn_rate_critical_when_remaining_zero(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br-001",
            burn_rate=0.5,
            threshold=0.8,
            remaining=0.0,
        )
        assert alert.severity == BudgetSeverity.CRITICAL

    def test_from_burn_rate_warning_when_over_threshold(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br-002",
            burn_rate=0.9,
            threshold=0.8,
            remaining=50.0,
        )
        assert alert.severity == BudgetSeverity.WARNING

    def test_from_burn_rate_warning_when_under_threshold(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br-003",
            burn_rate=0.3,
            threshold=0.8,
            remaining=100.0,
        )
        assert alert.severity == BudgetSeverity.WARNING

    def test_from_burn_rate_with_session_and_type(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br-004",
            burn_rate=0.9,
            threshold=0.8,
            remaining=0.0,
            session_id="s-1",
            budget_type=BudgetType.API_CALLS,
        )
        assert alert.session_id == "s-1"
        assert alert.budget_type == BudgetType.API_CALLS

    def test_detected_at_auto_set(self):
        alert = BudgetAlert(alert_id="dt-001")
        assert alert.detected_at != ""

    def test_negative_remaining_is_critical(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br-neg",
            burn_rate=0.1,
            threshold=0.8,
            remaining=-5.0,
        )
        assert alert.severity == BudgetSeverity.CRITICAL
