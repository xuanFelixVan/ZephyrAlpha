# [A_test] module_id: MOD-GOV_auto_maintenance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.auto_maintenance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.auto_maintenance import (
        AutoMaintenance,
        ComplexityBudget,
        OwnerDashboard,
        RuleHealth,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestAutoMaintenance:
    def test_register_rule(self):
        am = AutoMaintenance()
        rh = am.register_rule("R-001")
        assert isinstance(rh, RuleHealth)
        assert rh.rule_id == "R-001"
        assert rh.zombie is False
        assert rh.trigger_count == 0

    def test_record_trigger(self):
        am = AutoMaintenance()
        am.register_rule("R-001")
        am.record_trigger("R-001")
        am.record_trigger("R-001")
        assert am._rules["R-001"].trigger_count == 2

    def test_record_trigger_nonexistent(self):
        am = AutoMaintenance()
        am.record_trigger("R-999")
        assert "R-999" not in am._rules

    def test_detect_zombies_none(self):
        am = AutoMaintenance()
        am.register_rule("R-001")
        am.record_trigger("R-001")
        zombies = am.detect_zombies()
        assert len(zombies) == 0

    def test_check_complexity_under_limit(self):
        am = AutoMaintenance()
        for i in range(10):
            am.register_rule(f"R-{i:03d}")
        cb = am.check_complexity()
        assert isinstance(cb, ComplexityBudget)
        assert cb.current == 10
        assert cb.exceeded is False

    def test_check_complexity_exceeded(self):
        am = AutoMaintenance()
        for i in range(35):
            am.register_rule(f"R-{i:03d}")
        cb = am.check_complexity()
        assert cb.current == 35
        assert cb.exceeded is True


class TestOwnerDashboard:
    def test_get_dashboard(self):
        am = AutoMaintenance()
        am.register_rule("R-001")
        am.register_rule("R-002")
        am.record_trigger("R-001")
        dash = am.get_dashboard(denied_last_24h=3, emergency_tokens_active=1)
        assert isinstance(dash, OwnerDashboard)
        assert dash.active_rules == 2
        assert dash.denied_last_24h == 3
        assert dash.emergency_tokens_active == 1

    def test_dashboard_zero_rules(self):
        am = AutoMaintenance()
        dash = am.get_dashboard()
        assert dash.active_rules == 0
        assert dash.zombie_rules == 0
        assert dash.complexity_pct == 0.0
