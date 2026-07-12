# [A_test] module_id: SRC-TST-1246 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_market_calendar
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.market_calendar
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_market_calendar.py
# [TTL] task_bound

from zephyr.feedback_loop.collectors.market_calendar import MarketCalendar


class TestMarketCalendarInstantiation:
    def test_default_empty_holidays(self):
        cal = MarketCalendar()
        assert cal.holidays == set()

    def test_explicit_holidays(self):
        cal = MarketCalendar(holidays={"2026-01-01", "2026-12-25"})
        assert len(cal.holidays) == 2


class TestMarketCalendarIsTradingDay:
    def test_trading_day_when_not_holiday(self):
        cal = MarketCalendar(holidays={"2026-01-01"})
        assert cal.is_trading_day("2026-01-02") is True

    def test_not_trading_day_when_holiday(self):
        cal = MarketCalendar(holidays={"2026-01-01"})
        assert cal.is_trading_day("2026-01-01") is False

    def test_trading_day_empty_holidays(self):
        cal = MarketCalendar()
        assert cal.is_trading_day("2026-05-22") is True


class TestMarketCalendarBoundaries:
    def test_is_trading_day_with_empty_string(self):
        cal = MarketCalendar(holidays={""})
        assert cal.is_trading_day("") is False

    def test_is_trading_day_empty_string_not_in_holidays(self):
        cal = MarketCalendar()
        assert cal.is_trading_day("") is True

    def test_multiple_holidays(self):
        holidays = {"2026-01-01", "2026-07-04", "2026-12-25"}
        cal = MarketCalendar(holidays=holidays)
        assert cal.is_trading_day("2026-01-01") is False
        assert cal.is_trading_day("2026-07-04") is False
        assert cal.is_trading_day("2026-12-25") is False
        assert cal.is_trading_day("2026-03-15") is True

    def test_holiday_set_immutability(self):
        cal = MarketCalendar(holidays={"2026-01-01"})
        cal.holidays.add("2026-07-04")
        assert cal.is_trading_day("2026-07-04") is False
