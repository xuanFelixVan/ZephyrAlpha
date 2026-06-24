# [A_test] module_id: SRC-TST-1353 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_owner_health_monitor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_owner_health_monitor.py

import time

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.owner_health_monitor", reason="owner_health_monitor not available"
)
OwnerHealthMonitor = mod.OwnerHealthMonitor


class TestOwnerHealthMonitor:
    def test_instantiation(self):
        ohm = OwnerHealthMonitor()
        assert ohm._dismissals == 0
        assert ohm._total_alerts == 0

    def test_check_healthy(self):
        ohm = OwnerHealthMonitor()
        ohm.record_alert()
        result = ohm.check()
        assert result["state"] == "HEALTHY"
        assert result["dismissal_rate"] == 0.0
        assert result["auto_response_enabled"] is False

    def test_check_critical_dismissal_rate(self):
        ohm = OwnerHealthMonitor()
        for _ in range(7):
            ohm.record_alert()
            ohm.record_dismissal()
        for _ in range(3):
            ohm.record_alert()
        result = ohm.check()
        assert result["dismissal_rate"] == 0.7
        assert result["state"] == "CRITICALLY_LOW"
        assert result["auto_response_enabled"] is True

    def test_touch_resets_idle(self):
        ohm = OwnerHealthMonitor()
        ohm._last_active = time.time() - 2000
        ohm.touch()
        result = ohm.check()
        assert result["state"] in ("HEALTHY", "COMPLACENT")

    def test_check_complacent(self):
        ohm = OwnerHealthMonitor()
        ohm._last_active = time.time() - 2000
        ohm.record_alert()
        result = ohm.check()
        assert result["state"] == "COMPLACENT"
        assert result["auto_response_enabled"] is True

    def test_constants(self):
        assert OwnerHealthMonitor.ALERT_DISMISSAL_CRITICAL == 0.30
        assert OwnerHealthMonitor.RESPONSE_DELAY_CRITICAL == 1800
