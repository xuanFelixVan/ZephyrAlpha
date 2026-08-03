# [A_test] module_id: SRC-TST-0476 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §5
# [MODULE] tests.test_burn_rate_monitor
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_burn_rate_monitor.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from zephyr.governance.ops_governance.budget_models import (
    BudgetAlert,
    BudgetDimension,
    BudgetPolicy,
)
from zephyr.governance.ops_governance.burn_rate_monitor import (
    BurnRateMonitor,
    BurnSeverity,
    BurnWindow,
)


class TestBurnSeverity:
    def test_all_members(self):
        assert BurnSeverity.NORMAL.value == "NORMAL"
        assert BurnSeverity.ELEVATED.value == "ELEVATED"
        assert BurnSeverity.HIGH.value == "HIGH"
        assert BurnSeverity.CRITICAL.value == "CRITICAL"

    def test_member_count(self):
        assert len(BurnSeverity) == 4


class TestBurnWindow:
    def test_creation(self):
        bw = BurnWindow(name="5min", duration_seconds=300)
        assert bw.name == "5min"
        assert bw.last_burn_rate == 0.0
        assert bw.severity == BurnSeverity.NORMAL

    def test_default_buffer(self):
        bw = BurnWindow(name="test", duration_seconds=60)
        assert len(bw.sample_buffer) == 0


class TestBurnRateMonitor:
    def test_instantiation(self):
        brm = BurnRateMonitor()
        assert brm.dimension == BudgetDimension.TOKEN

    def test_instantiation_cost_dimension(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.COST)
        assert brm.dimension == BudgetDimension.COST

    def test_initial_severity_normal(self):
        brm = BurnRateMonitor()
        assert brm.get_severity() == BurnSeverity.NORMAL

    def test_record_consumption(self):
        brm = BurnRateMonitor()
        brm.record_consumption(100.0)
        summary = brm.get_burn_summary()
        for win_data in summary.values():
            assert win_data["samples"] >= 1

    def test_record_consumption_with_timestamp(self):
        brm = BurnRateMonitor()
        ts = datetime.now(UTC)
        brm.record_consumption(50.0, timestamp=ts)
        summary = brm.get_burn_summary()
        total_samples = sum(v["samples"] for v in summary.values())
        assert total_samples >= 4

    def test_compute_burn_rates_normal(self):
        brm = BurnRateMonitor()
        brm.record_consumption(100.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        summary = brm.get_burn_summary()
        for win_data in summary.values():
            assert win_data["rate"] >= 0.0

    def test_compute_burn_rates_critical(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.TOKEN)
        for _ in range(10):
            brm.record_consumption(100_000.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        assert brm.get_severity() in (BurnSeverity.HIGH, BurnSeverity.CRITICAL)

    def test_compute_burn_rates_elevated(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.TOKEN)
        for _ in range(5):
            brm.record_consumption(100_000.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        assert brm.get_severity() in (BurnSeverity.ELEVATED, BurnSeverity.HIGH, BurnSeverity.CRITICAL)

    def test_detect_distribution_shift_first_call(self):
        brm = BurnRateMonitor()
        shift = brm.detect_distribution_shift()
        assert shift == 0.0

    def test_detect_distribution_shift_after_change(self):
        brm = BurnRateMonitor()
        brm.detect_distribution_shift()
        for _ in range(5):
            brm.record_consumption(500_000.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        shift = brm.detect_distribution_shift()
        assert shift >= 0.0

    def test_update_baseline(self):
        brm = BurnRateMonitor()
        brm.record_consumption(100.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        brm.update_baseline()
        assert brm.distribution_baseline is not None

    def test_generate_alert_normal_returns_none(self):
        brm = BurnRateMonitor()
        brm.record_consumption(1.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        policy = BudgetPolicy(policy_id="BP-001", dimension=BudgetDimension.TOKEN)
        alert = brm.generate_alert(policy)
        assert alert is None

    def test_generate_alert_elevated(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.TOKEN)
        for _ in range(10):
            brm.record_consumption(100_000.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        policy = BudgetPolicy(policy_id="BP-001", dimension=BudgetDimension.TOKEN)
        alert = brm.generate_alert(policy)
        if brm.get_severity() != BurnSeverity.NORMAL:
            assert alert is not None
            assert isinstance(alert, BudgetAlert)

    def test_get_burn_summary(self):
        brm = BurnRateMonitor()
        brm.record_consumption(100.0)
        summary = brm.get_burn_summary()
        assert "5min" in summary
        assert "30min" in summary
        assert "2h" in summary
        assert "24h" in summary

    def test_get_alerts_empty(self):
        brm = BurnRateMonitor()
        assert brm.get_alerts() == []

    def test_get_alerts_after_generation(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.TOKEN)
        for _ in range(10):
            brm.record_consumption(100_000.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        policy = BudgetPolicy(policy_id="BP-001", dimension=BudgetDimension.TOKEN)
        brm.generate_alert(policy)
        if brm.get_severity() != BurnSeverity.NORMAL:
            alerts = brm.get_alerts()
            assert len(alerts) >= 1

    def test_reset(self):
        brm = BurnRateMonitor()
        brm.record_consumption(100.0)
        brm.compute_burn_rates(daily_limit=1_000_000)
        brm.reset()
        assert brm.get_severity() == BurnSeverity.NORMAL
        summary = brm.get_burn_summary()
        for win_data in summary.values():
            assert win_data["samples"] == 0

    def test_cost_dimension_thresholds(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.COST)
        for _ in range(10):
            brm.record_consumption(5.0)
        brm.compute_burn_rates(daily_limit=50.0)
        sev = brm.get_severity()
        assert sev in (BurnSeverity.ELEVATED, BurnSeverity.HIGH, BurnSeverity.CRITICAL)

    def test_wasserstein_1d(self):
        brm = BurnRateMonitor()
        result = brm.wasserstein_1d([0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4])
        assert result == pytest.approx(0.0)

    def test_wasserstein_1d_different(self):
        brm = BurnRateMonitor()
        result = brm.wasserstein_1d([0.1, 0.2], [0.5, 0.6])
        assert result > 0.0

    def test_wasserstein_1d_empty(self):
        brm = BurnRateMonitor()
        assert brm.wasserstein_1d([], []) == 0.0

    def test_wasserstein_1d_mismatched_length(self):
        brm = BurnRateMonitor()
        assert brm.wasserstein_1d([0.1], [0.1, 0.2]) == 0.0

    def test_classify_burn_default_thresholds(self):
        brm = BurnRateMonitor(dimension=BudgetDimension.TIME)
        assert brm.classify_burn(0.1) == BurnSeverity.NORMAL
        assert brm.classify_burn(0.4) == BurnSeverity.ELEVATED
        assert brm.classify_burn(0.6) == BurnSeverity.HIGH
        assert brm.classify_burn(0.9) == BurnSeverity.CRITICAL
