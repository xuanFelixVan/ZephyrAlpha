# [BLUEPRINT] MOD-POS-017 | docs/03_modules/_domain_position/calendar_position_constraint/blueprint.md | §D-POSITION POS-17
# [TTL] permanent
# [A_test] module_id: MOD-POS-017 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.position.test_calendar_position_constraint
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""CalendarPositionConstraint (MOD-POS-017) 测试套件。

覆盖: 期权交割日/窗口期/年报预告/年报ST清零/半年报预告/股东空窗/财报发布/
       无约束日期/多约束叠加/标的级vs全标的否决/日期计算工具。
"""

from __future__ import annotations

from datetime import date

import pytest

from zephyr.position.core.calendar_position_constraint import (
    CalendarEventType,
    CalendarPositionAlert,
    CalendarPositionConstraint,
    ConstraintAction,
    InvalidCalendarInputError,
    PositionInfo,
)


@pytest.fixture
def constraint() -> CalendarPositionConstraint:
    return CalendarPositionConstraint()


# ──────────────────────────────────────────────────────────────────────────────
# 期权交割日
# ──────────────────────────────────────────────────────────────────────────────


class TestOptionExpiry:
    def test_fourth_wednesday_blocks_new(self, constraint: CalendarPositionConstraint):
        """期权交割日(第四个周三)→否决新开仓。"""
        # 2026年1月: 第一个周三=1月7日, 第四个=1月28日
        expiry = date(2026, 1, 28)
        alert = constraint.check(expiry)
        assert alert.block_new_positions is True
        assert any(
            c.event_type is CalendarEventType.INDEX_OPTION_EXPIRY and c.action is ConstraintAction.BLOCK_NEW
            for c in alert.active_constraints
        )

    def test_option_expiry_window_reduces_cap(self, constraint: CalendarPositionConstraint):
        """交割日前2天→仓位上限下调10%。"""
        expiry = date(2026, 1, 28)
        # 前2天
        alert = constraint.check(expiry.replace(day=26))
        assert alert.overall_cap_adjustment == pytest.approx(0.9)
        # 后1天
        alert2 = constraint.check(expiry.replace(day=29))
        assert alert2.overall_cap_adjustment == pytest.approx(0.9)

    def test_non_expiry_day_no_constraint(self, constraint: CalendarPositionConstraint):
        """非交割日且非窗口期→无约束。"""
        alert = constraint.check(date(2026, 2, 15))
        assert len(alert.active_constraints) == 0
        assert alert.overall_cap_adjustment == 1.0
        assert alert.block_new_positions is False

    def test_fourth_wednesday_calculation(self, constraint: CalendarPositionConstraint):
        """验证第四个周三计算正确。"""
        # 2026年3月: 3月1日是周日(6), 第一个周三=3月4日, 第四个=3月25日
        assert constraint._fourth_wednesday(2026, 3) == date(2026, 3, 25)
        # 2026年6月: 6月1日是周一(0), 第一个周三=6月3日, 第四个=6月24日
        assert constraint._fourth_wednesday(2026, 6) == date(2026, 6, 24)


# ──────────────────────────────────────────────────────────────────────────────
# 年报预告截止
# ──────────────────────────────────────────────────────────────────────────────


class TestAnnualForecastDeadline:
    def test_no_forecast_blocked_in_january(self, constraint: CalendarPositionConstraint):
        """1月26-31日: 未出预告个股否决新买入。"""
        positions = [
            PositionInfo("000001.SZ", has_forecast=False),
            PositionInfo("000002.SZ", has_forecast=True),
        ]
        alert = constraint.check(date(2026, 1, 28), positions)
        assert "000001.SZ" in alert.block_new_symbols
        assert "000002.SZ" not in alert.block_new_symbols

    def test_forecast_check_not_active_in_february(self, constraint: CalendarPositionConstraint):
        """2月不触发年报预告约束。"""
        positions = [PositionInfo("000001.SZ", has_forecast=False)]
        alert = constraint.check(date(2026, 2, 5), positions)
        assert "000001.SZ" not in alert.block_new_symbols

    def test_no_positions_no_constraint(self, constraint: CalendarPositionConstraint):
        """1月下旬(年报预告期)但无持仓→无约束。

        注: 避开期权交割日窗口(每月第四个周三±, 1月为26-29日),
        取1月30日(仍在年报预告期 day>=26, 但已出期权窗口)。
        """
        alert = constraint.check(date(2026, 1, 30))
        assert len(alert.active_constraints) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 年报+一季报截止
# ──────────────────────────────────────────────────────────────────────────────


class TestAnnualReportDeadline:
    def test_st_stock_force_clear_in_april(self, constraint: CalendarPositionConstraint):
        """4月下旬: ST股强制清零。"""
        positions = [
            PositionInfo("ST001.SZ", is_st=True),
            PositionInfo("000002.SZ", is_st=False),
        ]
        alert = constraint.check(date(2026, 4, 25), positions)
        assert "ST001.SZ" in alert.force_clear_symbols
        assert "000002.SZ" not in alert.force_clear_symbols
        assert alert.overall_cap_adjustment == 0.0  # ST清零=cap 0.0

    def test_st_check_not_active_in_may(self, constraint: CalendarPositionConstraint):
        """5月不触发ST清零。"""
        positions = [PositionInfo("ST001.SZ", is_st=True)]
        alert = constraint.check(date(2026, 5, 10), positions)
        assert "ST001.SZ" not in alert.force_clear_symbols


# ──────────────────────────────────────────────────────────────────────────────
# 半年报预告截止
# ──────────────────────────────────────────────────────────────────────────────


class TestInterimForecastDeadline:
    def test_no_forecast_blocked_in_july(self, constraint: CalendarPositionConstraint):
        """7月10-15日: 未出预告个股否决新买入。"""
        positions = [PositionInfo("000001.SZ", has_forecast=False)]
        alert = constraint.check(date(2026, 7, 12), positions)
        assert "000001.SZ" in alert.block_new_symbols

    def test_not_active_in_august(self, constraint: CalendarPositionConstraint):
        """8月不触发半年报预告约束。"""
        positions = [PositionInfo("000001.SZ", has_forecast=False)]
        alert = constraint.check(date(2026, 8, 5), positions)
        assert "000001.SZ" not in alert.block_new_symbols


# ──────────────────────────────────────────────────────────────────────────────
# 股东信息空窗期
# ──────────────────────────────────────────────────────────────────────────────


class TestShareholderBlackout:
    def test_micro_cap_tightened_in_november(self, constraint: CalendarPositionConstraint):
        """11月: 微盘股(<50亿)仓位上限收紧50%。"""
        positions = [
            PositionInfo("MICRO.SZ", market_cap_yi=30.0),
            PositionInfo("BIG.SZ", market_cap_yi=200.0),
        ]
        alert = constraint.check(date(2026, 11, 15), positions)
        assert any(
            c.action is ConstraintAction.TIGHTEN_CAP and "MICRO.SZ" in (c.affected_symbols or ())
            for c in alert.active_constraints
        )
        assert alert.overall_cap_adjustment == pytest.approx(0.5)

    def test_micro_cap_tightened_in_february(self, constraint: CalendarPositionConstraint):
        """2月也在空窗期内。"""
        positions = [PositionInfo("MICRO.SZ", market_cap_yi=20.0)]
        alert = constraint.check(date(2026, 2, 10), positions)
        assert alert.overall_cap_adjustment == pytest.approx(0.5)

    def test_not_active_in_summer(self, constraint: CalendarPositionConstraint):
        """7月不在空窗期。"""
        positions = [PositionInfo("MICRO.SZ", market_cap_yi=20.0)]
        alert = constraint.check(date(2026, 7, 5), positions)
        assert all(c.event_type is not CalendarEventType.SHAREHOLDER_BLACKOUT for c in alert.active_constraints)


# ──────────────────────────────────────────────────────────────────────────────
# 财报发布
# ──────────────────────────────────────────────────────────────────────────────


class TestEarningsRelease:
    def test_three_days_before_blocks_new(self, constraint: CalendarPositionConstraint):
        """财报发布前3天: 该标的禁止新建+上限下调。"""
        release = date(2026, 3, 20)
        positions = [PositionInfo("000001.SZ", earnings_release_date=release)]
        # 前3天
        alert = constraint.check(date(2026, 3, 17), positions)
        assert "000001.SZ" in alert.block_new_symbols
        assert alert.overall_cap_adjustment == pytest.approx(0.9)

    def test_one_day_before_blocks_new(self, constraint: CalendarPositionConstraint):
        """财报发布前1天也触发。"""
        release = date(2026, 3, 20)
        positions = [PositionInfo("000001.SZ", earnings_release_date=release)]
        alert = constraint.check(date(2026, 3, 19), positions)
        assert "000001.SZ" in alert.block_new_symbols

    def test_five_days_before_not_triggered(self, constraint: CalendarPositionConstraint):
        """财报发布前5天不触发(仅前3天)。"""
        release = date(2026, 3, 20)
        positions = [PositionInfo("000001.SZ", earnings_release_date=release)]
        alert = constraint.check(date(2026, 3, 15), positions)
        assert "000001.SZ" not in alert.block_new_symbols

    def test_no_earnings_date_skipped(self, constraint: CalendarPositionConstraint):
        """无财报发布日→跳过。"""
        positions = [PositionInfo("000001.SZ", earnings_release_date=None)]
        alert = constraint.check(date(2026, 3, 17), positions)
        assert all(c.event_type is not CalendarEventType.EARNINGS_RELEASE for c in alert.active_constraints)


# ──────────────────────────────────────────────────────────────────────────────
# 多约束叠加
# ──────────────────────────────────────────────────────────────────────────────


class TestMultipleConstraints:
    def test_option_expiry_and_st_clear_overlap(self, constraint: CalendarPositionConstraint):
        """期权交割日 + ST清零 同时触发。"""
        # 找一个1月下旬的期权交割日 + 4月下旬不行(不同月)
        # 用1月28日(期权交割) + 无ST约束 → 只期权
        # 用4月22日(第四个周三2026年4月) → 期权 + ST
        expiry_apr = constraint._fourth_wednesday(2026, 4)  # 2026年4月第四个周三
        positions = [PositionInfo("ST001.SZ", is_st=True)]
        alert = constraint.check(expiry_apr, positions)
        # 期权交割日 → block_new_positions
        assert alert.block_new_positions is True
        # ST清零 → force_clear
        assert "ST001.SZ" in alert.force_clear_symbols
        # overall_cap = min(1.0, 0.0) = 0.0
        assert alert.overall_cap_adjustment == 0.0

    def test_normal_day_no_constraints(self, constraint: CalendarPositionConstraint):
        """正常交易日无任何约束。

        注(W-P1-20): 原取 2026-05-15 恰为当年5月第三个周五(股指期货交割日,
        B10-01316 新增规则触发), 改取 2026-05-20(期权/期货窗口均外)。
        """
        positions = [
            PositionInfo("000001.SZ", is_st=False, market_cap_yi=100.0, has_forecast=True),
        ]
        alert = constraint.check(date(2026, 5, 20), positions)
        assert len(alert.active_constraints) == 0
        assert alert.overall_cap_adjustment == 1.0
        assert alert.block_new_positions is False
        assert len(alert.block_new_symbols) == 0
        assert len(alert.force_clear_symbols) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_non_date_raises(self, constraint: CalendarPositionConstraint):
        with pytest.raises(InvalidCalendarInputError, match="must be a date"):
            constraint.check("2026-01-01")  # type: ignore[arg-type]

    def test_empty_positions_normal_day(self, constraint: CalendarPositionConstraint):
        """无持仓的正常日→空约束(2026-05-15→20, 避开期货交割日, W-P1-20)。"""
        alert = constraint.check(date(2026, 5, 20), [])
        assert len(alert.active_constraints) == 0


# ──────────────────────────────────────────────────────────────────────────────
# CalendarPositionAlert 属性
# ──────────────────────────────────────────────────────────────────────────────


class TestAlertProperties:
    def test_empty_alert_defaults(self):
        alert = CalendarPositionAlert(check_date=date(2026, 5, 15))
        assert alert.overall_cap_adjustment == 1.0
        assert alert.block_new_positions is False
        assert alert.block_new_symbols == set()
        assert alert.force_clear_symbols == set()

    def test_third_friday_calculation(self, constraint: CalendarPositionConstraint):
        """验证第三周五(期货交割日)计算。"""
        # 2026年1月: 1月1日是周四(3), 第一个周五=1月2日, 第三个=1月16日
        assert constraint._third_friday(2026, 1) == date(2026, 1, 16)


# ── W-P1-20 扩展: 交割日参数化 + 节假日持币 (B10-01316/CAND-POS-004) ───────────────

from zephyr.position.core.calendar_position_constraint import CalendarConstraint  # noqa: E402


class TestFutureExpiryAndHolidayEffect:
    def test_future_expiry_day_block_new(self, constraint: CalendarPositionConstraint):
        """股指期货交割日(第三个周五)当天→否决新开仓。"""
        future_expiry = constraint._third_friday(2026, 1)  # 2026-01-16
        alert = constraint.check(future_expiry)
        assert alert.block_new_positions is True
        assert any(
            c.event_type is CalendarEventType.INDEX_FUTURE_EXPIRY and c.action is ConstraintAction.BLOCK_NEW
            for c in alert.active_constraints
        )

    def test_future_expiry_window_reduce_cap_and_twap(self, constraint: CalendarPositionConstraint):
        """交割日前2天~后1天: 仓位下调10%+TWAP切换建议。"""
        future_expiry = constraint._third_friday(2026, 1)
        # 前2天
        alert = constraint.check(future_expiry.replace(day=future_expiry.day - 2))
        assert alert.overall_cap_adjustment == pytest.approx(0.9)
        twap_constraints = [c for c in alert.active_constraints if c.execution_hint == "switch_to_twap"]
        assert len(twap_constraints) >= 1
        # 后1天
        alert2 = constraint.check(future_expiry.replace(day=future_expiry.day + 1))
        assert alert2.overall_cap_adjustment == pytest.approx(0.9)

    def test_holiday_effect_reduce_cap_and_raise_cash(self, constraint: CalendarPositionConstraint):
        """节假日窗口(节前2天+节后1天): 仓位下调10%+现金储备抬升建议。"""
        # 模拟端午节前第2天 2026-06-16 (假设端午节 06-18)
        holidays = {date(2026, 6, 18)}
        alert = constraint.check(date(2026, 6, 16), holiday_dates=holidays)
        assert alert.overall_cap_adjustment == pytest.approx(0.9)
        assert any(
            c.event_type is CalendarEventType.HOLIDAY_EFFECT and c.execution_hint == "raise_cash_reserve"
            for c in alert.active_constraints
        )
        # 节后第1天
        alert2 = constraint.check(date(2026, 6, 19), holiday_dates=holidays)
        assert alert2.overall_cap_adjustment == pytest.approx(0.9)

    def test_non_holiday_no_effect(self, constraint: CalendarPositionConstraint):
        """非节假日窗口无节假日效应约束。"""
        alert = constraint.check(date(2026, 5, 20), holiday_dates={date(2026, 6, 18)})
        assert all(c.event_type is not CalendarEventType.HOLIDAY_EFFECT for c in alert.active_constraints)
