# [A_test] module_id: SRC-TST-0391 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_autonomy_regressor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_autonomy_regressor.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.autonomy_regressor import AutonomyRegressor


class TestAutonomyRegressorInstantiation:
    def test_creates_instance(self):
        regressor = AutonomyRegressor()
        assert regressor is not None

    def test_is_correct_type(self):
        regressor = AutonomyRegressor()
        assert isinstance(regressor, AutonomyRegressor)

    def test_levels_attribute(self):
        regressor = AutonomyRegressor()
        assert regressor.LEVELS == ["autonomous", "auto_guard", "blocked"]


class TestShouldRegress:
    def test_low_confidence_triggers_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.2, error_count=0)
        assert result == "auto_guard"

    def test_high_error_count_triggers_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.9, error_count=6)
        assert result == "auto_guard"

    def test_stable_conditions_no_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.8, error_count=0)
        assert result == "autonomous"

    def test_low_confidence_from_auto_guard_to_blocked(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("auto_guard", confidence=0.1, error_count=0)
        assert result == "blocked"

    def test_blocked_stays_blocked_on_low_confidence(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("blocked", confidence=0.1, error_count=10)
        assert result == "blocked"

    def test_blocked_stays_blocked_on_high_errors(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("blocked", confidence=0.9, error_count=100)
        assert result == "blocked"

    def test_confidence_at_threshold_boundary_no_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.3, error_count=0)
        assert result == "autonomous"

    def test_error_count_at_boundary_no_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.9, error_count=5)
        assert result == "autonomous"

    def test_unknown_level_treated_as_first(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("unknown_level", confidence=0.1, error_count=0)
        assert result == "auto_guard"


class TestRegressionPath:
    def test_autonomous_path(self):
        regressor = AutonomyRegressor()
        path = regressor.regression_path("autonomous")
        assert path == ["autonomous", "auto_guard", "blocked"]

    def test_auto_guard_path(self):
        regressor = AutonomyRegressor()
        path = regressor.regression_path("auto_guard")
        assert path == ["auto_guard", "blocked"]

    def test_blocked_path(self):
        regressor = AutonomyRegressor()
        path = regressor.regression_path("blocked")
        assert path == ["blocked"]

    def test_unknown_level_returns_full_path(self):
        regressor = AutonomyRegressor()
        path = regressor.regression_path("nonexistent")
        assert path == ["autonomous", "auto_guard", "blocked"]


class TestBoundaryConditions:
    def test_confidence_zero_triggers_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.0, error_count=0)
        assert result == "auto_guard"

    def test_confidence_one_no_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=1.0, error_count=0)
        assert result == "autonomous"

    def test_negative_confidence_triggers_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=-1.0, error_count=0)
        assert result == "auto_guard"

    def test_zero_error_count_no_regression(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.9, error_count=0)
        assert result == "autonomous"

    def test_very_high_error_count(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.9, error_count=999)
        assert result == "auto_guard"

    def test_both_triggers_simultaneously(self):
        regressor = AutonomyRegressor()
        result = regressor.should_regress("autonomous", confidence=0.1, error_count=10)
        assert result == "auto_guard"

    def test_regression_path_length_decreases_with_level(self):
        regressor = AutonomyRegressor()
        assert len(regressor.regression_path("autonomous")) == 3
        assert len(regressor.regression_path("auto_guard")) == 2
        assert len(regressor.regression_path("blocked")) == 1
