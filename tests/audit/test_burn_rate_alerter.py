# [A_test] module_id: SRC-TST-0475 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_burn_rate_alerter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.burn_rate_alerter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_burn_rate_alerter.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.burn_rate_alerter import (
    BurnRateAlerter,
    BurnWindow,
)


class TestBurnWindow:
    def test_default_construction(self):
        bw = BurnWindow(name="1h", window_seconds=3600, target_burn_rate=14.4)
        assert bw.name == "1h"
        assert bw.window_seconds == 3600
        assert bw.target_burn_rate == 14.4
        assert bw.current_burn_rate == 0.0
        assert bw.error_count == 0
        assert bw.total_count == 0

    def test_custom_construction(self):
        bw = BurnWindow(name="test", window_seconds=60, target_burn_rate=5.0, current_burn_rate=2.0)
        assert bw.current_burn_rate == 2.0


class TestBurnRateAlerter:
    def test_instantiation_default(self):
        alerter = BurnRateAlerter()
        assert alerter.slo_pct == 99.9
        assert len(alerter.windows) == 3

    def test_instantiation_custom_slo(self):
        alerter = BurnRateAlerter(slo_pct=99.5)
        assert alerter.slo_pct == 99.5

    def test_instantiation_default_windows(self):
        alerter = BurnRateAlerter()
        names = [w.name for w in alerter.windows]
        assert "1h" in names
        assert "6h" in names
        assert "3d" in names

    def test_record_success(self):
        alerter = BurnRateAlerter()
        alerter.record(success=True)
        for w in alerter.windows:
            assert w.total_count == 1
            assert w.error_count == 0

    def test_record_failure(self):
        alerter = BurnRateAlerter()
        alerter.record(success=False)
        for w in alerter.windows:
            assert w.total_count == 1
            assert w.error_count == 1

    def test_record_multiple(self):
        alerter = BurnRateAlerter()
        alerter.record(success=True)
        alerter.record(success=True)
        alerter.record(success=False)
        for w in alerter.windows:
            assert w.total_count == 3
            assert w.error_count == 1

    def test_alerts_empty_when_healthy(self):
        alerter = BurnRateAlerter()
        alerter.record(success=True)
        assert alerter.alerts() == []

    def test_alerts_triggered_on_high_error_rate(self):
        alerter = BurnRateAlerter(slo_pct=99.0)
        for _ in range(100):
            alerter.record(success=False)
        alerts = alerter.alerts()
        assert len(alerts) > 0

    def test_alerts_format_contains_window_name(self):
        alerter = BurnRateAlerter(slo_pct=99.0)
        for _ in range(100):
            alerter.record(success=False)
        alerts = alerter.alerts()
        for alert in alerts:
            assert any(name in alert for name in ["1h", "6h", "3d"])

    def test_record_mixed_updates_burn_rate(self):
        alerter = BurnRateAlerter(slo_pct=99.0)
        for _ in range(50):
            alerter.record(success=True)
        for _ in range(50):
            alerter.record(success=False)
        for w in alerter.windows:
            assert w.current_burn_rate > 0.0

    def test_record_zero_slo_budget(self):
        alerter = BurnRateAlerter(slo_pct=100.0)
        alerter.record(success=False)
        for w in alerter.windows:
            assert w.current_burn_rate == 0.0

    def test_custom_windows(self):
        custom_window = BurnWindow(name="5m", window_seconds=300, target_burn_rate=20.0)
        alerter = BurnRateAlerter(windows=[custom_window])
        assert len(alerter.windows) == 1
        assert alerter.windows[0].name == "5m"

    def test_alerts_returns_list(self):
        alerter = BurnRateAlerter()
        result = alerter.alerts()
        assert isinstance(result, list)

    def test_burn_rate_calculation_all_success(self):
        alerter = BurnRateAlerter(slo_pct=99.0)
        for _ in range(100):
            alerter.record(success=True)
        for w in alerter.windows:
            assert w.current_burn_rate == 0.0
