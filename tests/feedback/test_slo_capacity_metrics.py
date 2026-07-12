# [A_test] module_id: SRC-TST-1662 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_slo_capacity_metrics
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.slo_capacity_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_slo_capacity_metrics.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.slo_capacity_metrics import (
    SLOCapacityMetrics,
    SLOWindow,
)


class TestSLOWindowInstantiation:
    def test_default_instantiation(self):
        w = SLOWindow(window_hours=1.0)
        assert w.window_hours == 1.0
        assert w.error_count == 0
        assert w.total_count == 0
        assert w.target_burn_rate == 1.0

    def test_custom_values(self):
        w = SLOWindow(window_hours=6.0, error_count=5, total_count=100, target_burn_rate=6.0)
        assert w.error_count == 5
        assert w.total_count == 100


class TestSLOWindowBurnRate:
    def test_burn_rate_zero_total(self):
        w = SLOWindow(window_hours=1.0)
        assert w.burn_rate == 0.0

    def test_burn_rate_calculation(self):
        w = SLOWindow(window_hours=1.0, error_count=10, total_count=100)
        assert w.burn_rate == pytest.approx(0.1)

    def test_burn_rate_no_errors(self):
        w = SLOWindow(window_hours=1.0, error_count=0, total_count=100)
        assert w.burn_rate == 0.0


class TestSLOWindowAlert:
    def test_no_alert_below_target(self):
        w = SLOWindow(window_hours=1.0, error_count=1, total_count=100, target_burn_rate=14.4)
        assert w.alert is False

    def test_alert_above_target(self):
        w = SLOWindow(window_hours=1.0, error_count=50, total_count=100, target_burn_rate=0.1)
        assert w.alert is True

    def test_no_alert_at_exact_target(self):
        w = SLOWindow(window_hours=1.0, error_count=10, total_count=100, target_burn_rate=0.1)
        assert w.alert is False


class TestSLOCapacityMetricsInstantiation:
    def test_default_instantiation(self):
        scm = SLOCapacityMetrics()
        assert scm.slo_pct == 99.9
        assert scm.total_requests == 0
        assert scm.total_errors == 0
        assert "1h" in scm.windows
        assert "6h" in scm.windows
        assert "3d" in scm.windows


class TestRecord:
    def test_record_success(self):
        scm = SLOCapacityMetrics()
        scm.record(success=True)
        assert scm.total_requests == 1
        assert scm.total_errors == 0

    def test_record_failure(self):
        scm = SLOCapacityMetrics()
        scm.record(success=False)
        assert scm.total_requests == 1
        assert scm.total_errors == 1

    def test_record_failure_updates_windows(self):
        scm = SLOCapacityMetrics()
        scm.record(success=False)
        for w in scm.windows.values():
            assert w.error_count == 1
            assert w.total_count == 1

    def test_record_success_does_not_update_windows(self):
        scm = SLOCapacityMetrics()
        scm.record(success=True)
        for w in scm.windows.values():
            assert w.error_count == 0
            assert w.total_count == 0

    def test_record_mixed(self):
        scm = SLOCapacityMetrics()
        scm.record(success=True)
        scm.record(success=True)
        scm.record(success=False)
        assert scm.total_requests == 3
        assert scm.total_errors == 1


class TestErrorBudgetRemainingPct:
    def test_full_budget_when_no_requests(self):
        scm = SLOCapacityMetrics()
        assert scm.error_budget_remaining_pct() == 100.0

    def test_budget_decreases_with_errors(self):
        scm = SLOCapacityMetrics(slo_pct=99.0)
        for _ in range(100):
            scm.record(success=True)
        scm.record(success=False)
        remaining = scm.error_budget_remaining_pct()
        assert 0.0 < remaining < 100.0

    def test_budget_exhausted(self):
        scm = SLOCapacityMetrics(slo_pct=99.0)
        for _ in range(200):
            scm.record(success=False)
        remaining = scm.error_budget_remaining_pct()
        assert remaining == 0.0

    def test_budget_never_negative(self):
        scm = SLOCapacityMetrics(slo_pct=99.0)
        for _ in range(500):
            scm.record(success=False)
        remaining = scm.error_budget_remaining_pct()
        assert remaining >= 0.0


class TestExhaustionAlerts:
    def test_no_alerts_when_healthy(self):
        scm = SLOCapacityMetrics()
        for _ in range(100):
            scm.record(success=True)
        assert scm.exhaustion_alerts() == []

    def test_alerts_with_low_target_burn_rate(self):
        from zephyr.feedback_loop.diagnosers.slo_capacity_metrics import SLOWindow

        scm = SLOCapacityMetrics(windows={"1h": SLOWindow(1.0, target_burn_rate=0.5)})
        for _ in range(10):
            scm.record(success=False)
        alerts = scm.exhaustion_alerts()
        assert len(alerts) > 0

    def test_alert_format_contains_burn_rate(self):
        scm = SLOCapacityMetrics()
        for _ in range(50):
            scm.record(success=False)
        alerts = scm.exhaustion_alerts()
        for alert in alerts:
            assert "burn" in alert


class TestSLOCapacityMetricsBoundaries:
    def test_zero_slo_pct_all_errors_exhausts_budget(self):
        scm = SLOCapacityMetrics(slo_pct=0.0)
        for _ in range(10):
            scm.record(success=False)
        assert scm.error_budget_remaining_pct() == 0.0

    def test_100_slo_pct_zero_budget(self):
        scm = SLOCapacityMetrics(slo_pct=100.0)
        scm.record(success=True)
        assert scm.error_budget_remaining_pct() == 0.0

    def test_single_request_no_errors(self):
        scm = SLOCapacityMetrics(slo_pct=99.9)
        scm.record(success=True)
        assert scm.error_budget_remaining_pct() == 100.0
