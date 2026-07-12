# [A_test] module_id: SRC-TST-1332 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_operational_seasonality
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.operational_seasonality
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_operational_seasonality.py
# [TTL] task_bound

from datetime import datetime
from unittest.mock import patch

from zephyr.feedback_loop.diagnosers.operational_seasonality import (
    OperationalSeasonality,
    OpMode,
)


class TestOpMode:
    def test_weekday_value(self):
        assert OpMode.WEEKDAY.value == "WEEKDAY"

    def test_weekend_value(self):
        assert OpMode.WEEKEND.value == "WEEKEND"

    def test_month_end_value(self):
        assert OpMode.MONTH_END.value == "MONTH_END"

    def test_quarter_end_value(self):
        assert OpMode.QUARTER_END.value == "QUARTER_END"

    def test_year_end_value(self):
        assert OpMode.YEAR_END.value == "YEAR_END"

    def test_holiday_value(self):
        assert OpMode.HOLIDAY.value == "HOLIDAY"

    def test_all_modes_count(self):
        assert len(OpMode) == 6


class TestOperationalSeasonalityInstantiation:
    def test_default_instantiation(self):
        os_ = OperationalSeasonality()
        assert os_.mode == OpMode.WEEKDAY
        assert "WEEKEND" in os_.threshold_multipliers

    def test_custom_mode(self):
        os_ = OperationalSeasonality(mode=OpMode.WEEKEND)
        assert os_.mode == OpMode.WEEKEND

    def test_custom_multipliers(self):
        os_ = OperationalSeasonality(threshold_multipliers={"WEEKEND": 0.5})
        assert os_.threshold_multipliers["WEEKEND"] == 0.5


class TestAutoMode:
    def test_auto_mode_weekday(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 5, 20, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = os_.auto_mode()
            assert result == OpMode.WEEKDAY

    def test_auto_mode_weekend(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 5, 23, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = os_.auto_mode()
            assert result == OpMode.WEEKEND

    def test_auto_mode_month_end(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 5, 28, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = os_.auto_mode()
            assert result == OpMode.MONTH_END

    def test_auto_mode_quarter_end(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 6, 28, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = os_.auto_mode()
            assert result == OpMode.QUARTER_END

    def test_auto_mode_year_end(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 12, 28, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = os_.auto_mode()
            assert result == OpMode.YEAR_END

    def test_auto_mode_updates_internal_mode(self):
        os_ = OperationalSeasonality()
        with patch("zephyr.trading.feedback_loop.diagnosers.operational_seasonality.datetime") as mock_dt:
            mock_now = datetime(2026, 5, 23, 10, 0, 0)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            os_.auto_mode()
            assert os_.mode == OpMode.WEEKEND


class TestMultiplier:
    def test_weekday_multiplier_default(self):
        os_ = OperationalSeasonality(mode=OpMode.WEEKDAY)
        assert os_.multiplier == 1.0

    def test_weekend_multiplier(self):
        os_ = OperationalSeasonality(mode=OpMode.WEEKEND)
        assert os_.multiplier == 0.7

    def test_quarter_end_multiplier(self):
        os_ = OperationalSeasonality(mode=OpMode.QUARTER_END)
        assert os_.multiplier == 0.3

    def test_year_end_multiplier(self):
        os_ = OperationalSeasonality(mode=OpMode.YEAR_END)
        assert os_.multiplier == 0.2

    def test_holiday_multiplier_default(self):
        os_ = OperationalSeasonality(mode=OpMode.HOLIDAY)
        assert os_.multiplier == 1.0
