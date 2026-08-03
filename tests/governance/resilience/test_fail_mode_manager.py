# [A_test] module_id: MOD-GOV_fail_mode_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_fail_mode_manager
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_fail_mode_manager.py
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.governance.resilience_governance.fail_mode_manager import (
    FailMode,
    FailModeManager,
    FailModeState,
    HealthCheck,
)


class TestFailModeState:
    def test_default_values(self):
        state = FailModeState(mode=FailMode.OPEN, reason="test")
        assert state.mode == FailMode.OPEN
        assert state.reason == "test"
        assert state.recoverable is True
        assert state.auto_recovery_at is None
        assert isinstance(state.since, float)

    def test_custom_values(self):
        ts = time.time() + 300
        state = FailModeState(
            mode=FailMode.CLOSED,
            reason="overloaded",
            since=ts,
            recoverable=False,
            auto_recovery_at=ts + 600,
        )
        assert state.mode == FailMode.CLOSED
        assert state.recoverable is False
        assert state.auto_recovery_at == ts + 600


class TestHealthCheck:
    def test_default_values(self):
        hc = HealthCheck(component="test_comp", healthy=True, detail="ok")
        assert hc.component == "test_comp"
        assert hc.healthy is True
        assert hc.detail == "ok"
        assert hc.latency_ms == 0.0
        assert isinstance(hc.checked_at, float)

    def test_custom_latency(self):
        hc = HealthCheck(component="x", healthy=False, detail="slow", latency_ms=500.0)
        assert hc.latency_ms == 500.0
        assert hc.healthy is False


class TestFailModeManager:
    def test_init_default_open(self):
        mgr = FailModeManager()
        assert mgr.current_mode() == FailMode.OPEN

    def test_init_custom_mode(self):
        mgr = FailModeManager(default_mode=FailMode.CLOSED)
        assert mgr.current_mode() == FailMode.CLOSED

    def test_health_check_healthy(self):
        mgr = FailModeManager()
        hc = mgr.record_health_check("budget_engine", True, "ok")
        assert hc.healthy is True
        assert hc.component == "budget_engine"

    def test_health_check_unhealthy_increments_fail_count(self):
        mgr = FailModeManager()
        mgr.record_health_check("budget_engine", False, "down")
        mgr.record_health_check("budget_engine", False, "still down")
        assert mgr.component_fail_count("budget_engine") == 2

    def test_evaluate_no_checks_returns_current(self):
        mgr = FailModeManager(default_mode=FailMode.OPEN)
        state = mgr.evaluate()
        assert state.mode == FailMode.OPEN

    def test_evaluate_one_unhealthy_degraded(self):
        mgr = FailModeManager()
        mgr.record_health_check("budget_engine", False, "down")
        state = mgr.evaluate()
        assert state.mode == FailMode.DEGRADED

    def test_evaluate_two_unhealthy_closed(self):
        mgr = FailModeManager()
        mgr.record_health_check("budget_engine", False, "down")
        mgr.record_health_check("model_router", False, "down")
        state = mgr.evaluate()
        assert state.mode == FailMode.CLOSED

    def test_evaluate_three_critical_fails_dead(self):
        mgr = FailModeManager()
        for comp in ["budget_engine", "model_router", "timeout_guard"]:
            for _ in range(3):
                mgr.record_health_check(comp, False, "fail")
        state = mgr.evaluate()
        assert state.mode == FailMode.DEAD

    def test_evaluate_all_healthy_recovers_to_open(self):
        mgr = FailModeManager(default_mode=FailMode.CLOSED)
        mgr.record_health_check("budget_engine", True, "ok")
        mgr.record_health_check("model_router", True, "ok")
        state = mgr.evaluate()
        assert state.mode == FailMode.OPEN

    def test_should_recover_open_mode(self):
        mgr = FailModeManager()
        assert mgr.should_recover() is True

    def test_should_recover_auto_recovery_at_future(self):
        mgr = FailModeManager(default_mode=FailMode.CLOSED)
        mgr.state.auto_recovery_at = time.time() + 9999
        assert mgr.should_recover() is False

    def test_should_recover_auto_recovery_at_past(self):
        mgr = FailModeManager(default_mode=FailMode.CLOSED)
        mgr.state.auto_recovery_at = time.time() - 1
        assert mgr.should_recover() is True

    def test_auto_recover(self):
        mgr = FailModeManager(default_mode=FailMode.DEAD)
        mgr.record_health_check("budget_engine", False, "down")
        mgr.auto_recover()
        assert mgr.state.mode == FailMode.OPEN
        assert mgr.component_fail_count("budget_engine") == 0

    def test_recent_checks(self):
        mgr = FailModeManager()
        for i in range(25):
            mgr.record_health_check("comp", True, f"check {i}")
        recent = mgr.recent_checks(n=5)
        assert len(recent) == 5

    def test_recent_checks_default_n(self):
        mgr = FailModeManager()
        for i in range(25):
            mgr.record_health_check("comp", True, f"check {i}")
        recent = mgr.recent_checks()
        assert len(recent) == 20

    def test_component_fail_count_missing(self):
        mgr = FailModeManager()
        assert mgr.component_fail_count("nonexistent") == 0

    def test_reset(self):
        mgr = FailModeManager()
        mgr.record_health_check("budget_engine", False, "down")
        mgr.reset()
        assert mgr.current_mode() == FailMode.OPEN
        assert mgr.component_fail_count("budget_engine") == 0
        assert mgr.recent_checks() == []

    def test_components_list_exists(self):
        assert isinstance(FailModeManager.COMPONENTS, list)
        assert len(FailModeManager.COMPONENTS) > 0
