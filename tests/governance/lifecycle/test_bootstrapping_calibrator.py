# [A_test] module_id: SRC-TST-0450 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_bootstrapping_calibrator
# [INVARIANTS] correction_factor >= 0; is_calibrated only True after min_data_points
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.bootstrapping_calibrator import (
    BootstrappingCalibrator,
    CalibrationPoint,
)


class TestCalibrationPoint:
    def test_creation(self):
        cp = CalibrationPoint(
            actual_tokens=100,
            estimated_tokens=80,
            actual_cost=0.5,
            estimated_cost=0.4,
            actual_time=2.0,
            estimated_time=1.5,
            error_ratio=1.25,
        )
        assert cp.actual_tokens == 100
        assert cp.error_ratio == 1.25

    def test_timestamp_auto_set(self):
        cp = CalibrationPoint(
            actual_tokens=10,
            estimated_tokens=10,
            actual_cost=0.0,
            estimated_cost=0.0,
            actual_time=0.0,
            estimated_time=1.0,
            error_ratio=1.0,
        )
        assert cp.timestamp > 0


class TestBootstrappingCalibrator:
    def test_instantiation_defaults(self):
        cal = BootstrappingCalibrator()
        assert cal.is_calibrated is False
        assert cal.correction_factor == 1.0
        assert cal.data_points() == 0

    def test_instantiation_custom(self):
        cal = BootstrappingCalibrator(min_data_points=5, duration_days=7)
        assert cal.data_points() == 0

    def test_record_returns_calibration_point(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        cp = cal.record(actual_tokens=100, estimated_tokens=100)
        assert isinstance(cp, CalibrationPoint)
        assert cp.actual_tokens == 100
        assert cal.data_points() == 1

    def test_not_calibrated_before_min_data_points(self):
        cal = BootstrappingCalibrator(min_data_points=5)
        cal.record(100, 100)
        cal.record(100, 100)
        cal.record(100, 100)
        cal.record(100, 100)
        assert cal.is_calibrated is False

    def test_calibrated_after_min_data_points(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        cal.record(100, 100)
        cal.record(100, 100)
        cal.record(100, 100)
        assert cal.is_calibrated is True

    def test_calibrate_estimate_before_calibration(self):
        cal = BootstrappingCalibrator(min_data_points=10)
        result = cal.calibrate_estimate(1000)
        assert result == 1000

    def test_calibrate_estimate_after_calibration(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        for _ in range(3):
            cal.record(actual_tokens=200, estimated_tokens=100, estimated_time=0.0)
        result = cal.calibrate_estimate(100)
        assert result != 100
        assert result > 0

    def test_correction_factor_updates(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        for _ in range(3):
            cal.record(actual_tokens=200, estimated_tokens=100, estimated_time=0.0)
        assert cal.correction_factor > 1.0

    def test_is_bootstrapping_initially_true(self):
        cal = BootstrappingCalibrator(min_data_points=100, duration_days=30)
        assert cal.is_bootstrapping() is True

    def test_is_bootstrapping_false_after_calibration(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        for _ in range(3):
            cal.record(100, 100)
        assert cal.is_bootstrapping() is False

    def test_get_hard_limit_multiplier_uncalibrated(self):
        cal = BootstrappingCalibrator(min_data_points=100)
        assert cal.get_hard_limit_multiplier() == 3.0

    def test_get_hard_limit_multiplier_calibrated(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        for _ in range(3):
            cal.record(200, 100)
        mult = cal.get_hard_limit_multiplier()
        assert 1.5 <= mult <= 3.0

    def test_reset(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        for _ in range(3):
            cal.record(100, 100)
        assert cal.is_calibrated is True
        cal.reset()
        assert cal.is_calibrated is False
        assert cal.data_points() == 0
        assert cal.correction_factor == 1.0

    def test_record_zero_estimated(self):
        cal = BootstrappingCalibrator(min_data_points=3)
        cp = cal.record(actual_tokens=100, estimated_tokens=0)
        assert cp.error_ratio == 1.0

    def test_days_elapsed_near_zero(self):
        cal = BootstrappingCalibrator()
        assert cal.days_elapsed() < 1.0
