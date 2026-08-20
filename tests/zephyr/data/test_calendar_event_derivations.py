# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_calendar_event_derivations
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-TEST-DATA-CALDERIV | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""event_type 派生函数单元测试（17 号 §2.4 待评估项，earnings_deadline 优先）。

覆盖:
  - earnings_deadline：4/30 交易日当日命中；10/31 周六 → 前移 10/30（周五）；
    8/31 周一命中；非交易日前移跨长假；范围过滤；空 by_month 空表
  - mlf_operation：8/15 周六 → 顺延 8/17 周一；9/15 周二当日命中；范围过滤
  - bond_futures_delivery：季月（3 月）第 2 个周五命中；非季月（4 月）无事件；
    交割日非交易日顺延；范围过滤
  - a50_futures_delivery：月末周一 → 倒数第 2 个工作日为上周五；
    月末周日 → 取周四；每年 12 个月全有事件
  - 行格式四元组 (date, event_type, description, "internal") 与既有派生一致

日期 weekday 锚点（2026 年实证）：2026-03-01 周日 / 2026-04-30 周四 /
2026-08-15 周六 / 2026-08-31 周一 / 2026-10-31 周六 / 2026-05-31 周日。
"""
from __future__ import annotations

import datetime

from zephyr.data.implementations.calendar_event_derivations import (
    derive_a50_futures_delivery,
    derive_bond_futures_delivery,
    derive_earnings_deadline,
    derive_mlf_operation,
)

D = datetime.date
RANGE = (D(2026, 1, 1), D(2026, 12, 31))


def _trading_days(year=2026):
    """合成 A 股交易日集合：全年全部周一~周五（节假日不剔，测试确定性优先）。"""
    days = set()
    d = D(year, 1, 1)
    while d.year == year:
        if d.weekday() < 5:
            days.add(d)
        d += datetime.timedelta(days=1)
    return days


def _by_month(trading_days):
    bm = {}
    for d in sorted(trading_days):
        key = (d.year, d.month)
        if key not in bm or d > bm[key]:
            bm[key] = d
    return bm


TD = _trading_days()
BM = _by_month(TD)


class TestEarningsDeadline:
    """优先项：财报披露截止窗口（17 号 §2.4）。"""

    def test_three_deadlines_per_year(self):
        rows = derive_earnings_deadline(BM, TD, *RANGE)
        dates = {r[0] for r in rows}
        assert dates == {D(2026, 4, 30), D(2026, 8, 31), D(2026, 10, 30)}

    def test_weekday_deadline_on_day(self):
        """4/30 周四=交易日 → 当日命中；8/31 周一 → 当日命中。"""
        rows = derive_earnings_deadline(BM, TD, D(2026, 4, 1), D(2026, 4, 30))
        assert [r[0] for r in rows] == [D(2026, 4, 30)]

    def test_saturday_deadline_moves_back(self):
        """10/31 周六 → 前移前一交易日 10/30 周五（非顺延， memo 口径）。"""
        rows = derive_earnings_deadline(BM, TD, D(2026, 10, 1), D(2026, 10, 31))
        assert len(rows) == 1
        assert rows[0][0] == D(2026, 10, 30)
        assert rows[0][0].weekday() == 4

    def test_holiday_gap_moves_back_over_gap(self):
        """4/26~5/4 连续非交易日（五一长假形态）→ 前移到 4/24 周五（4/25-26 为周末）。"""
        td = TD - {D(2026, 4, 26) + datetime.timedelta(days=i) for i in range(9)}
        rows = derive_earnings_deadline(BM, td, D(2026, 4, 1), D(2026, 4, 30))
        # 4/26~5/4 全剔 → 4/30 非交易日 → 前移到 4/24（周五，4/25 周六/4/26 周日均非交易日）
        assert rows[0][0] == D(2026, 4, 24)
        assert rows[0][0].weekday() == 4

    def test_range_filter(self):
        rows = derive_earnings_deadline(BM, TD, D(2026, 5, 1), D(2026, 7, 31))
        assert rows == []

    def test_empty_by_month(self):
        assert derive_earnings_deadline({}, TD, *RANGE) == []

    def test_row_format(self):
        rows = derive_earnings_deadline(BM, TD, *RANGE)
        for date_, event_type, desc, source in rows:
            assert isinstance(date_, datetime.date)
            assert event_type == "earnings_deadline"
            assert "财报披露截止" in desc
            assert source == "internal"


class TestMlfOperation:
    def test_saturday_postponed(self):
        """2026-08-15 周六 → 顺延 8/17 周一（与 LPR 同口径）。"""
        rows = derive_mlf_operation(BM, D(2026, 8, 1), D(2026, 8, 31))
        assert [r[0] for r in rows] == [D(2026, 8, 17)]
        assert rows[0][1] == "mlf_operation"

    def test_weekday_on_day(self):
        """2026-09-15 周二 → 当日命中。"""
        rows = derive_mlf_operation(BM, D(2026, 9, 1), D(2026, 9, 30))
        assert [r[0] for r in rows] == [D(2026, 9, 15)]

    def test_twelve_months(self):
        rows = derive_mlf_operation(BM, *RANGE)
        assert len(rows) == 12

    def test_range_filter(self):
        rows = derive_mlf_operation(BM, D(2026, 1, 16), D(2026, 2, 14))
        assert rows == []


class TestBondFuturesDelivery:
    def test_quarter_month_second_friday(self):
        """2026-03（季月）第 2 个周五 = 03-13（周五）→ 当日命中。"""
        rows = derive_bond_futures_delivery(BM, TD, D(2026, 3, 1), D(2026, 3, 31))
        assert [r[0] for r in rows] == [D(2026, 3, 13)]
        assert rows[0][1] == "bond_futures_delivery"

    def test_non_quarter_month_no_event(self):
        """4 月（非季月）→ 无事件（与股指期货每月第 3 周五不同机制）。"""
        rows = derive_bond_futures_delivery(BM, TD, D(2026, 4, 1), D(2026, 4, 30))
        assert rows == []

    def test_delivery_postponed_when_not_trading(self):
        """第 2 个周五非交易日 → 顺延下一交易日。"""
        td = TD - {D(2026, 3, 13)}  # 剔除交割周五
        rows = derive_bond_futures_delivery(BM, td, D(2026, 3, 1), D(2026, 3, 31))
        assert [r[0] for r in rows] == [D(2026, 3, 16)]  # 下周一

    def test_four_quarter_months_per_year(self):
        rows = derive_bond_futures_delivery(BM, TD, *RANGE)
        assert len(rows) == 4
        assert {r[0].month for r in rows} == {3, 6, 9, 12}


class TestA50FuturesDelivery:
    def test_month_end_monday(self):
        """2026-08-31 周一（月末）→ 倒数第 2 个工作日 = 8/28 周五。"""
        rows = derive_a50_futures_delivery(BM, D(2026, 8, 1), D(2026, 8, 31))
        assert [r[0] for r in rows] == [D(2026, 8, 28)]

    def test_month_end_sunday(self):
        """2026-05-31 周日（月末）→ 倒数：5/29 周五(1st)、5/28 周四(2nd)。"""
        rows = derive_a50_futures_delivery(BM, D(2026, 5, 1), D(2026, 5, 31))
        assert [r[0] for r in rows] == [D(2026, 5, 28)]

    def test_december(self):
        """12 月边界（month+1 进位）：2026-12-31 周四 → 倒数第 2 = 12/30 周三。"""
        rows = derive_a50_futures_delivery(BM, D(2026, 12, 1), D(2026, 12, 31))
        assert [r[0] for r in rows] == [D(2026, 12, 30)]

    def test_twelve_months(self):
        rows = derive_a50_futures_delivery(BM, *RANGE)
        assert len(rows) == 12
        for date_, event_type, desc, source in rows:
            assert event_type == "a50_futures_delivery"
            assert date_.weekday() < 5
            assert source == "internal"
