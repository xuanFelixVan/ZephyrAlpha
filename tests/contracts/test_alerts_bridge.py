# [A_test] module_id: MOD-GOV_alerts_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_alerts_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.bridges.alerts import BudgetAlert, BudgetSeverity, BudgetType


class TestBudgetSeverity:
    def test_enum_values(self):
        assert BudgetSeverity.WARNING.value == "WARNING"
        assert BudgetSeverity.CRITICAL.value == "CRITICAL"

    def test_enum_members(self):
        assert len(list(BudgetSeverity)) == 2


class TestBudgetType:
    def test_enum_values(self):
        assert BudgetType.TOKEN.value == "TOKEN"
        assert BudgetType.TIME.value == "TIME"
        assert BudgetType.MEMORY.value == "MEMORY"
        assert BudgetType.API_CALLS.value == "API_CALLS"

    def test_enum_members(self):
        assert len(list(BudgetType)) == 4


class TestBudgetAlert:
    def test_creation_defaults(self):
        alert = BudgetAlert(alert_id="a1")
        assert alert.alert_id == "a1"
        assert alert.severity == BudgetSeverity.WARNING
        assert alert.budget_type == BudgetType.TOKEN
        assert alert.burn_rate == 0.0
        assert alert.remaining_budget == 0.0

    def test_creation_custom(self):
        alert = BudgetAlert(
            alert_id="a2",
            session_id="sess1",
            budget_type=BudgetType.TIME,
            burn_rate=0.9,
            burn_rate_threshold=0.8,
            remaining_budget=100.0,
            severity=BudgetSeverity.CRITICAL,
        )
        assert alert.session_id == "sess1"
        assert alert.budget_type == BudgetType.TIME
        assert alert.severity == BudgetSeverity.CRITICAL

    def test_from_burn_rate_critical(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br1",
            burn_rate=0.95,
            threshold=0.8,
            remaining=0,
        )
        assert alert.severity == BudgetSeverity.CRITICAL

    def test_from_burn_rate_warning(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br2",
            burn_rate=0.85,
            threshold=0.8,
            remaining=500.0,
        )
        assert alert.severity == BudgetSeverity.WARNING

    def test_from_burn_rate_below_threshold(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br3",
            burn_rate=0.5,
            threshold=0.8,
            remaining=1000.0,
        )
        assert alert.severity == BudgetSeverity.WARNING

    def test_from_burn_rate_with_session(self):
        alert = BudgetAlert.from_burn_rate(
            alert_id="br4",
            burn_rate=0.9,
            threshold=0.8,
            remaining=50.0,
            session_id="sess2",
            budget_type=BudgetType.MEMORY,
        )
        assert alert.session_id == "sess2"
        assert alert.budget_type == BudgetType.MEMORY

    def test_detected_at_auto_set(self):
        alert = BudgetAlert(alert_id="a3")
        assert len(alert.detected_at) > 0


class TestBridgeReexport:
    def test_all_exports_available(self):
        from zephyr.governance.bridges.alerts import __all__

        assert "BudgetAlert" in __all__
        assert "BudgetSeverity" in __all__
        assert "BudgetType" in __all__

    def test_reexported_classes_match_source(self):
        from zephyr.shared.contracts.escalation.budget_alert import (
            BudgetAlert as SrcAlert,
        )
        from zephyr.shared.contracts.escalation.budget_alert import (
            BudgetSeverity as SrcSeverity,
        )
        from zephyr.shared.contracts.escalation.budget_alert import (
            BudgetType as SrcType,
        )

        assert BudgetAlert is SrcAlert
        assert BudgetSeverity is SrcSeverity
        assert BudgetType is SrcType
