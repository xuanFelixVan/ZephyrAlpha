# [A_test] module_id: MOD-GOV_budget_forecaster | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_budget_forecaster
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_budget_forecaster.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.capacity_assurance.budget_forecaster import BudgetForecast, BudgetForecaster


class TestBudgetForecast:
    def test_fields_assigned_correctly(self):
        bf = BudgetForecast(
            session_id="s-001",
            estimated_peak_tokens=1000,
            recommended_budget=1200,
            confidence=0.8,
        )
        assert bf.session_id == "s-001"
        assert bf.estimated_peak_tokens == 1000
        assert bf.recommended_budget == 1200
        assert bf.confidence == 0.8

    def test_confidence_is_float(self):
        bf = BudgetForecast(session_id="s", estimated_peak_tokens=0, recommended_budget=0, confidence=0.5)
        assert isinstance(bf.confidence, float)


class TestBudgetForecasterInstantiation:
    def test_can_create_forecaster(self):
        f = BudgetForecaster()
        assert f is not None

    def test_has_forecast_method(self):
        f = BudgetForecaster()
        assert callable(getattr(f, "forecast", None))


class TestBudgetForecasterForecast:
    def test_with_previous_usages_returns_budget(self):
        f = BudgetForecaster()
        result = f.forecast("s-001", "refactor", [1000, 2000, 3000])
        assert result.session_id == "s-001"
        assert result.estimated_peak_tokens == 3000
        assert result.recommended_budget == int(2000 * 1.2)
        assert result.confidence == 0.75

    def test_empty_usages_returns_default_budget(self):
        f = BudgetForecaster()
        result = f.forecast("s-002", "debug", [])
        assert result.estimated_peak_tokens == 8000
        assert result.recommended_budget == 8000

    def test_returns_budget_forecast_type(self):
        f = BudgetForecaster()
        result = f.forecast("s-003", "build", [500])
        assert isinstance(result, BudgetForecast)

    def test_single_usage_peak_equals_that_usage(self):
        f = BudgetForecaster()
        result = f.forecast("s-004", "test", [5000])
        assert result.estimated_peak_tokens == 5000
        assert result.recommended_budget == int(5000 * 1.2)

    def test_large_usages_dont_overflow(self):
        f = BudgetForecaster()
        result = f.forecast("s-005", "big", [10**9, 2 * 10**9])
        assert result.estimated_peak_tokens == 2 * 10**9
        assert result.recommended_budget == int(1.5 * 10**9 * 1.2)

    def test_session_id_preserved(self):
        f = BudgetForecaster()
        result = f.forecast("my-session", "task", [100])
        assert result.session_id == "my-session"
