# [MODULE] tests.zephyr.data.calendar.test_market_calendar
# [DOMAIN] D_DATA
# [TESTS] src/zephyr/data/calendar/{base,ashare,crypto}.py + 消费点注入（scheduler/fusion/pit_query）
# [TTL] permanent
"""Market Calendar 市场日历抽象单测（CAND-CRYPTO-001 / 94号 §4.1 / W0）。

覆盖：
- ASHareCalendar 收编=委托真源（与 trading_calendar 结果逐日一致，零行为变化）
- CryptoCalendar 7×24 连续（跨周末连续日历日、全天单时段、恒开市）
- get_market_calendar 工厂（单例、未知市场 ValueError）
- fusion 4h 周期（SUPPORTED_FREQS 增量、UTC 00:00 锚定原生切桶、calendar 注入展开）
- 消费点注入等价性（scheduler 默认 None≡显式 A股；pit_query embargo 真历换算）
"""

from __future__ import annotations

import datetime

import pandas as pd
import pytest

from zephyr.data.calendar import (
    ASHareCalendar,
    CryptoCalendar,
    MarketCalendar,
    get_market_calendar,
)
from zephyr.data.multi_timeframe_fusion import SUPPORTED_FREQS, MultiTimeframeFusion

D = datetime.date
DT = datetime.datetime
T = datetime.time


class TestASHareCalendar:
    cal = ASHareCalendar()

    def test_market_identity(self) -> None:
        assert self.cal.market == "ashare"
        assert self.cal.timezone == "Asia/Shanghai"

    def test_is_trading_day_weekend_false(self) -> None:
        # 周六/周日恒非交易日（XSHG 精确历与 weekday 降级链结论一致）
        assert self.cal.is_trading_day(D(2026, 8, 29)) is False  # 周六
        assert self.cal.is_trading_day(D(2026, 8, 30)) is False  # 周日

    def test_delegate_matches_source(self) -> None:
        # 收编=薄封装委托：与真源 trading_calendar 结果严格一致（零行为变化断言）
        from zephyr.data import trading_calendar as tc

        start, end = D(2026, 8, 1), D(2026, 8, 31)
        assert self.cal.trading_days_in_range(start, end) == tc.trading_days_in_range(start, end)
        for d in (D(2026, 8, 3), D(2026, 8, 8), D(2026, 8, 14), D(2026, 8, 26)):
            assert self.cal.is_trading_day(d) == tc.is_trading_day(d)

    def test_session_windows_two_segments(self) -> None:
        assert self.cal.session_windows(D(2026, 8, 26)) == (
            (T(9, 30), T(11, 30)),
            (T(13, 0), T(15, 0)),
        )

    def test_is_open_at(self) -> None:
        # 2026-08-26 周三：XSHG 精确历与 weekday 降级均判交易日
        assert self.cal.is_open_at(DT(2026, 8, 26, 10, 0)) is True  # 早盘
        assert self.cal.is_open_at(DT(2026, 8, 26, 14, 0)) is True  # 午盘
        assert self.cal.is_open_at(DT(2026, 8, 26, 12, 30)) is False  # 午休
        assert self.cal.is_open_at(DT(2026, 8, 26, 16, 0)) is False  # 收盘后
        assert self.cal.is_open_at(DT(2026, 8, 29, 10, 0)) is False  # 周六

    def test_kline_agg_rule(self) -> None:
        r = self.cal.kline_agg_rule("120min")
        assert r.mode == "pair" and r.source_freq == "60min" and r.pair_count == 2
        assert self.cal.kline_agg_rule("60min").mode == "native"
        assert self.cal.kline_agg_rule("1d").mode == "native"
        with pytest.raises(ValueError):
            self.cal.kline_agg_rule("4h")  # A股 9 周期无 4h
        with pytest.raises(ValueError):
            self.cal.kline_agg_rule("3min")


class TestCryptoCalendar:
    cal = CryptoCalendar()

    def test_market_identity(self) -> None:
        assert self.cal.market == "crypto"
        assert self.cal.timezone == "UTC"

    def test_is_trading_day_always_true(self) -> None:
        for i in range(7):  # 周一~周日全覆盖
            assert self.cal.is_trading_day(D(2026, 8, 24) + datetime.timedelta(days=i)) is True

    def test_trading_days_in_range_continuous_over_weekend(self) -> None:
        # 7×24 核心断言：跨周末连续 7 天无断点
        days = self.cal.trading_days_in_range(D(2026, 8, 24), D(2026, 8, 30))
        assert days == [D(2026, 8, 24) + datetime.timedelta(days=i) for i in range(7)]

    def test_trading_days_empty_when_reversed(self) -> None:
        assert self.cal.trading_days_in_range(D(2026, 8, 30), D(2026, 8, 24)) == []

    def test_session_single_full_day_window(self) -> None:
        ws = self.cal.session_windows(D(2026, 8, 29))
        assert ws == ((T(0, 0), T.max),)

    def test_is_open_at_always_true(self) -> None:
        assert self.cal.is_open_at(DT(2026, 8, 29, 23, 59)) is True  # 周六午夜前
        assert self.cal.is_open_at(DT(2026, 8, 30, 0, 1)) is True  # 周日午夜后

    def test_kline_agg_rule_native_incl_4h(self) -> None:
        assert self.cal.kline_agg_rule("4h").mode == "native"
        assert self.cal.kline_agg_rule("120min").mode == "native"
        with pytest.raises(ValueError):
            self.cal.kline_agg_rule("3min")


class TestFactory:
    def test_singleton_per_market(self) -> None:
        assert get_market_calendar("ashare") is get_market_calendar("ashare")
        assert get_market_calendar("crypto") is get_market_calendar("crypto")

    def test_instance_types(self) -> None:
        assert isinstance(get_market_calendar("ashare"), ASHareCalendar)
        assert isinstance(get_market_calendar("crypto"), CryptoCalendar)

    def test_unknown_market_raises(self) -> None:
        with pytest.raises(ValueError):
            get_market_calendar("forex")


class TestInterfaceContract:
    def test_abc_not_instantiable(self) -> None:
        with pytest.raises(TypeError):
            MarketCalendar()  # type: ignore[abstract]


class TestFusion4h:
    """4h 周期（币 7×24 顺带支持）：SUPPORTED_FREQS 增量 + 原生切桶锚定日界。"""

    @staticmethod
    def _mk_60min_bars(start: str, n: int) -> pd.DataFrame:
        ts = pd.date_range(start, periods=n, freq="60min")
        return pd.DataFrame(
            {
                "timestamp": ts,
                "open": range(n),
                "high": range(n),
                "low": range(n),
                "close": range(n),
                "volume": 1,
            }
        )

    def test_4h_registered(self) -> None:
        assert SUPPORTED_FREQS["4h"] == 240

    def test_4h_native_bins_day_aligned(self) -> None:
        bars = self._mk_60min_bars("2026-08-24 00:00:00", 48)  # 连续 2 天
        result = MultiTimeframeFusion().resample(
            bars,
            "60min",
            "4h",
            expected_start=pd.Timestamp("2026-08-24 00:00:00"),
            expected_end=pd.Timestamp("2026-08-26 00:00:00"),
        )
        assert len(result.data) == 12  # 48 根 60min = 12 根 4h
        bin_hours = [t.hour for t in (result.data["timestamp"] - pd.Timedelta(hours=4))]
        assert bin_hours == [0, 4, 8, 12, 16, 20] * 2  # 桶起点跨午夜连续
        assert result.quality.coverage_ratio == 1.0

    def test_calendar_injection_expands_trading_days(self) -> None:
        bars = self._mk_60min_bars("2026-08-24 00:00:00", 48)
        fusion = MultiTimeframeFusion()
        # calendar 注入：CryptoCalendar 全自然日 → 无桶被过滤
        r1 = fusion.resample(
            bars,
            "60min",
            "4h",
            expected_start=pd.Timestamp("2026-08-24 00:00:00"),
            expected_end=pd.Timestamp("2026-08-26 00:00:00"),
            calendar=CryptoCalendar(),
        )
        assert len(r1.data) == 12
        # 显式 trading_days 永远优先于 calendar 展开
        r2 = fusion.resample(
            bars,
            "60min",
            "4h",
            trading_days=[D(2026, 8, 24)],
            expected_start=pd.Timestamp("2026-08-24 00:00:00"),
            expected_end=pd.Timestamp("2026-08-26 00:00:00"),
            calendar=CryptoCalendar(),
        )
        assert len(r2.data) == 6  # 仅保留 8-24 当天的 6 桶


class TestSchedulerInjection:
    """scheduler 注入式改造：默认 None ≡ 显式 A股日历（零行为变化）；币历恒交易日。"""

    def test_crypto_never_skips_trading_day_guard(self) -> None:
        from zephyr.data.scheduler import _schedule_should_skip

        # daily_kline 属 TRADING_DAY_GUARDED_SCHEDULES；币历下任何日期都不触发跳过
        assert _schedule_should_skip("daily_kline", {}, calendar=CryptoCalendar()) is False

    def test_default_none_equivalent_to_ashare(self) -> None:
        from zephyr.data.scheduler import _filter_schedule_tasks, _schedule_should_skip

        ashare = ASHareCalendar()
        for sched in ("daily_kline", "intraday_minute", "monthly_static"):
            assert _schedule_should_skip(sched, {}, None) == _schedule_should_skip(sched, {}, ashare)
        tasks = [{"task_id": "t1", "schedule": "daily_kline", "extra": {"trading_day_only": True}}]
        assert _filter_schedule_tasks(tasks, "daily_kline", None) == _filter_schedule_tasks(
            tasks, "daily_kline", ashare
        )
        # 币历恒交易日：trading_day_only 任务不过滤
        assert _filter_schedule_tasks(tasks, "daily_kline", CryptoCalendar()) == tasks


class TestPitQueryInjection:
    """pit_query 注入式改造：默认 None=自然日（逐字节一致）；注入后真历换算 INTERVAL。"""

    def test_default_none_embargo_identical(self) -> None:
        from zephyr.data.pit_query import FinancialPITQuery, PITQueryConfig

        q = FinancialPITQuery(PITQueryConfig(embargo_days=3))
        assert q._embargo_sql("2026-08-26") == " - INTERVAL 3 DAY"

    def test_zero_embargo_empty_clause(self) -> None:
        from zephyr.data.pit_query import FinancialPITQuery, PITQueryConfig

        q = FinancialPITQuery(PITQueryConfig(embargo_days=0), calendar=CryptoCalendar())
        assert q._embargo_sql("2026-08-26") == ""

    def test_crypto_embargo_equals_natural_days(self) -> None:
        from zephyr.data.pit_query import FinancialPITQuery, PITQueryConfig

        # 币 7×24：回退 3 交易日=自然日 3 天，与自然日口径一致
        q = FinancialPITQuery(PITQueryConfig(embargo_days=3), calendar=CryptoCalendar())
        assert q._embargo_sql("2026-08-26") == " - INTERVAL 3 DAY"

    def test_ashare_embargo_skips_weekend(self) -> None:
        from zephyr.data.pit_query import FinancialPITQuery, PITQueryConfig

        # qt=2026-08-24（周一，交易日）：回退 1 交易日=上周五 8-21 → k=3
        q = FinancialPITQuery(PITQueryConfig(embargo_days=1), calendar=ASHareCalendar())
        assert q._embargo_sql(D(2026, 8, 24)) == " - INTERVAL 3 DAY"
