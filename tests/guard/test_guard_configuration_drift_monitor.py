# [A_test] module_id: SRC-TST-1083 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_guard_configuration_drift_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.guard_configuration_drift_monitor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_guard_configuration_drift_monitor.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.guard_configuration_drift_monitor import (
    GuardConfigSnapshot,
    GuardConfigurationDriftMonitor,
)


class TestGuardConfigSnapshot:
    def test_creation(self):
        snap = GuardConfigSnapshot(timestamp=1.0, config={"a": 1.0}, hash="abc", drift_from_golden=0.0)
        assert snap.config == {"a": 1.0}
        assert snap.drift_from_golden == 0.0

    def test_default_drift(self):
        snap = GuardConfigSnapshot(timestamp=2.0, config={}, hash="def")
        assert snap.drift_from_golden == 0.0


class TestGuardConfigurationDriftMonitor:
    def test_instantiation_defaults(self):
        mon = GuardConfigurationDriftMonitor()
        assert mon.golden_baseline == {}
        assert mon.golden_hash == ""
        assert mon.snapshots == []
        assert mon.drift_threshold == 0.15

    def test_establish_golden_baseline(self):
        mon = GuardConfigurationDriftMonitor()
        config = {"threshold_a": 0.8, "threshold_b": 0.5}
        h = mon.establish_golden_baseline(config)
        assert len(h) == 16
        assert mon.golden_baseline == config
        assert mon.golden_hash == h

    def test_establish_golden_baseline_deterministic(self):
        mon1 = GuardConfigurationDriftMonitor()
        mon2 = GuardConfigurationDriftMonitor()
        config = {"x": 1.0}
        assert mon1.establish_golden_baseline(config) == mon2.establish_golden_baseline(config)

    def test_take_snapshot_stable(self):
        mon = GuardConfigurationDriftMonitor()
        config = {"a": 1.0, "b": 2.0}
        mon.establish_golden_baseline(config)
        result = mon.take_snapshot(config)
        assert result["severity"] == "stable"
        assert result["drift"] == 0.0
        assert result["config_changed"] is False

    def test_take_snapshot_moderate_drift(self):
        mon = GuardConfigurationDriftMonitor()
        mon.establish_golden_baseline({"a": 1.0, "b": 2.0})
        result = mon.take_snapshot({"a": 1.0, "b": 4.0})
        assert result["severity"] == "moderate_drift"
        assert result["drift"] > mon.drift_threshold

    def test_take_snapshot_critical_drift(self):
        mon = GuardConfigurationDriftMonitor()
        mon.establish_golden_baseline({"a": 1.0, "b": 2.0})
        result = mon.take_snapshot({"a": 10.0, "b": 20.0})
        assert result["severity"] == "critical_drift"
        assert result["drift"] > 0.3

    def test_take_snapshot_new_keys(self):
        mon = GuardConfigurationDriftMonitor()
        mon.establish_golden_baseline({"a": 1.0})
        result = mon.take_snapshot({"a": 1.0, "new_key": 5.0})
        assert result["drift"] > 0.0

    def test_take_snapshot_no_baseline(self):
        mon = GuardConfigurationDriftMonitor()
        result = mon.take_snapshot({"a": 1.0})
        assert result["drift"] == 1.0

    def test_get_drift_trend_insufficient_data(self):
        mon = GuardConfigurationDriftMonitor()
        mon.establish_golden_baseline({"a": 1.0})
        mon.take_snapshot({"a": 1.0})
        trend = mon.get_drift_trend()
        assert trend["trend"] == "insufficient_data"

    def test_get_drift_trend_increasing(self):
        mon = GuardConfigurationDriftMonitor()
        mon.establish_golden_baseline({"a": 1.0})
        for i in range(5):
            mon.take_snapshot({"a": 1.0 + i * 0.5})
        trend = mon.get_drift_trend()
        assert trend["trend"] in ("monotonically_increasing", "fluctuating")

    def test_max_snapshots_truncation(self):
        mon = GuardConfigurationDriftMonitor(max_snapshots=5)
        mon.establish_golden_baseline({"a": 1.0})
        for i in range(10):
            mon.take_snapshot({"a": float(i)})
        assert len(mon.snapshots) <= 5

    def test_compute_drift_empty_configs(self):
        mon = GuardConfigurationDriftMonitor()
        drift = mon._compute_drift({}, {})
        assert drift == 0.0

    def test_compute_drift_identical_configs(self):
        mon = GuardConfigurationDriftMonitor()
        config = {"x": 1.0, "y": 2.0}
        drift = mon._compute_drift(config, config)
        assert drift == 0.0
