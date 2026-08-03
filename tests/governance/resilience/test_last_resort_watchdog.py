# [A_test] module_id: MOD-GOV_last_resort_watchdog | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_last_resort_watchdog
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_last_resort_watchdog.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.last_resort_watchdog import LastResortWatchdog


class TestLastResortWatchdogInstantiation:
    def test_creates_instance_not_active(self):
        wd = LastResortWatchdog()
        assert wd.active is False

    def test_initial_state_is_deactivated(self):
        wd = LastResortWatchdog()
        assert wd.activated is False


class TestActivate:
    def test_activate_sets_active_true(self):
        wd = LastResortWatchdog()
        wd.activate()
        assert wd.active is True

    def test_activate_idempotent(self):
        wd = LastResortWatchdog()
        wd.activate()
        wd.activate()
        assert wd.active is True


class TestEmergencyShutdown:
    def test_emergency_shutdown_returns_dict(self):
        wd = LastResortWatchdog()
        result = wd.emergency_shutdown()
        assert isinstance(result, dict)

    def test_emergency_shutdown_contains_action(self):
        wd = LastResortWatchdog()
        result = wd.emergency_shutdown()
        assert result["action"] == "EMERGENCY_SHUTDOWN"

    def test_emergency_shutdown_contains_reason(self):
        wd = LastResortWatchdog()
        result = wd.emergency_shutdown()
        assert result["reason"] == "last_resort_activated"

    def test_emergency_shutdown_safe_mode_true(self):
        wd = LastResortWatchdog()
        result = wd.emergency_shutdown()
        assert result["safe_mode"] is True

    def test_emergency_shutdown_activates_watchdog(self):
        wd = LastResortWatchdog()
        wd.emergency_shutdown()
        assert wd.active is True

    def test_emergency_shutdown_dict_has_three_keys(self):
        wd = LastResortWatchdog()
        result = wd.emergency_shutdown()
        assert len(result) == 3


class TestLastResortWatchdogBoundary:
    def test_activate_then_emergency_shutdown(self):
        wd = LastResortWatchdog()
        wd.activate()
        result = wd.emergency_shutdown()
        assert wd.active is True
        assert result["action"] == "EMERGENCY_SHUTDOWN"

    def test_emergency_shutdown_when_already_active(self):
        wd = LastResortWatchdog()
        wd.activate()
        result = wd.emergency_shutdown()
        assert wd.active is True
        assert result["safe_mode"] is True

    def test_no_reset_mechanism(self):
        wd = LastResortWatchdog()
        wd.activate()
        assert wd.active is True
        assert not hasattr(wd, "deactivate")
        assert not hasattr(wd, "reset")
