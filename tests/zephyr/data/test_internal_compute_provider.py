# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""InternalComputeProvider 多周期逻辑测试。

测试内容（纯函数逻辑，不依赖 CH 连接）：
- _aggregate_120min: 60min 两根聚合为 120min（OHLCV 规则）
- _build_row: 列映射含 period/trade_time/symbol
- _PERIOD_MAP: 9 周期全覆盖
- symbol 前导零保留（回归测试：pd.read_csv dtype=str 修复）

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_build_plan.md §3-§4
"""

from __future__ import annotations

import datetime

import numpy as np
import pandas as pd
import pytest

from zephyr.data.implementations.internal_compute_provider import (
    _PERIOD_MAP,
    ALL_PERIODS,
    InternalComputeProvider,
)

# ===========================================================================
# _PERIOD_MAP 完整性测试
# ===========================================================================


class TestPeriodMap:
    def test_nine_periods_covered(self):
        """9 个周期全部映射。"""
        expected = {"1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly"}
        assert set(_PERIOD_MAP.keys()) == expected

    def test_120min_uses_60min_source(self):
        """120min 无原生表，源表指向 kline_60min。"""
        assert _PERIOD_MAP["120min"][0] == "c1_market.kline_60min"

    def test_intraday_flag(self):
        """日内周期 is_intraday=True，日/周/月=False。"""
        for p in ["1min", "5min", "15min", "30min", "60min", "120min"]:
            assert _PERIOD_MAP[p][2] is True, f"{p} 应为日内"
        for p in ["daily", "weekly", "monthly"]:
            assert _PERIOD_MAP[p][2] is False, f"{p} 应为非日内"

    def test_all_periods_order(self):
        """ALL_PERIODS 先日/周/月，后分钟（全量回算顺序）。"""
        assert ALL_PERIODS[0] == "daily"
        assert ALL_PERIODS[:3] == ["daily", "weekly", "monthly"]


# ===========================================================================
# _aggregate_120min 测试
# ===========================================================================


class TestAggregate120min:
    """120min 聚合——60min 两根合并。"""

    @staticmethod
    def _make_60min(n_symbols=1, n_days=1, bars_per_day=4):
        """生成 60min 测试数据（每日 bars_per_day 根）。"""
        rows = []
        base_time = pd.Timestamp("2026-08-10 09:30:00")
        times = [
            base_time,
            base_time + pd.Timedelta("1h"),
            base_time + pd.Timedelta("3h"),
            base_time + pd.Timedelta("4h"),
        ]
        for s in range(n_symbols):
            for d in range(n_days):
                for b in range(bars_per_day):
                    rows.append(
                        {
                            "trade_date": datetime.date(2026, 8, 10 + d),
                            "trade_time": times[b] + pd.Timedelta(days=d),
                            "symbol": f"{s:06d}",
                            "open": 10.0 + b,
                            "high": 10.5 + b,
                            "low": 9.5 + b,
                            "close": 10.0 + b + 0.5,
                            "volume": 100.0 * (b + 1),
                            "amount": 1000.0 * (b + 1),
                        }
                    )
        return pd.DataFrame(rows)

    def test_four_bars_to_two(self):
        """4 根 60min → 2 根 120min。"""
        df = self._make_60min(bars_per_day=4)
        result = InternalComputeProvider._aggregate_120min(df)
        assert len(result) == 2

    def test_ohlcv_aggregation(self):
        """open=首根 open, high=max, low=min, close=末根 close, volume=sum。"""
        df = self._make_60min(bars_per_day=4)
        result = InternalComputeProvider._aggregate_120min(df)
        # 第 1 根 120min = bar0+bar1
        r0 = result.iloc[0]
        assert r0["open"] == 10.0  # bar0 open
        assert r0["high"] == 11.5  # max(10.5, 11.5)
        assert r0["low"] == 9.5  # min(9.5, 10.5)
        assert r0["close"] == 11.5  # bar1 close (10.0+1+0.5)
        assert r0["volume"] == 300.0  # 100+200

    def test_trade_time_is_first_bar(self):
        """120min 的 trade_time = 首根 60min 的 trade_time。"""
        df = self._make_60min(bars_per_day=4)
        result = InternalComputeProvider._aggregate_120min(df)
        # bar0=09:30, bar1=10:30, bar2=12:30, bar3=13:30
        # 第 1 根 120min = bar0+bar1 → trade_time=09:30
        assert result.iloc[0]["trade_time"] == pd.Timestamp("2026-08-10 09:30:00")
        # 第 2 根 120min = bar2+bar3 → trade_time=12:30（bar2 时间）
        assert result.iloc[1]["trade_time"] == pd.Timestamp("2026-08-10 12:30:00")

    def test_multi_symbol(self):
        """多标的聚合正确分组。"""
        df = self._make_60min(n_symbols=3, bars_per_day=4)
        result = InternalComputeProvider._aggregate_120min(df)
        assert len(result) == 6  # 3 symbols × 2 bars
        assert set(result["symbol"].unique()) == {"000000", "000001", "000002"}

    def test_odd_bars_not_dropped(self):
        """奇数根（异常）：最后一根单独成 120min，不丢弃。"""
        df = self._make_60min(bars_per_day=3)  # 3 根 → 2 组（0,1）+（2）
        result = InternalComputeProvider._aggregate_120min(df)
        assert len(result) == 2

    def test_empty_dataframe(self):
        """空 DataFrame → 空结果。"""
        df = pd.DataFrame(
            columns=["trade_date", "trade_time", "symbol", "open", "high", "low", "close", "volume", "amount"]
        )
        result = InternalComputeProvider._aggregate_120min(df)
        assert result.empty


# ===========================================================================
# _build_row 测试
# ===========================================================================


class TestBuildRow:
    """_build_row 列映射——含 period/trade_time/symbol。"""

    def test_daily_row(self):
        """日线行：trade_time=午夜，period=daily。"""
        columns = ["trade_date", "trade_time", "symbol", "period", "ma_5", "obv", "data_source"]
        bar_ts = pd.Timestamp("2026-08-10")
        row_data = pd.Series({"ma_5": 11.2, "obv": 889060.0})
        row = InternalComputeProvider()._build_row(bar_ts, "000001", "daily", row_data, columns)
        assert row[0] == datetime.date(2026, 8, 10)  # trade_date
        assert row[1] == datetime.datetime(2026, 8, 10, 0, 0, 0)  # trade_time 午夜
        assert row[2] == "000001"  # symbol（前导零保留）
        assert row[3] == "daily"  # period
        assert row[4] == 11.2  # ma_5
        assert row[5] == 889060.0  # obv
        assert row[6] == "internal"  # data_source

    def test_intraday_row(self):
        """日内行：trade_time=K线时间，period=60min。"""
        columns = ["trade_date", "trade_time", "symbol", "period", "ma_5"]
        bar_ts = pd.Timestamp("2026-08-10 10:30:00")
        row_data = pd.Series({"ma_5": 11.2})
        row = InternalComputeProvider()._build_row(bar_ts, "600000", "60min", row_data, columns)
        assert row[0] == datetime.date(2026, 8, 10)
        assert row[1] == datetime.datetime(2026, 8, 10, 10, 30, 0)  # 精确时间
        assert row[2] == "600000"
        assert row[3] == "60min"

    def test_nan_to_none(self):
        """NaN 指标值 → None（CH Nullable 列）。"""
        columns = ["trade_date", "trade_time", "symbol", "period", "ma_5"]
        bar_ts = pd.Timestamp("2026-08-10")
        row_data = pd.Series({"ma_5": float("nan")})
        row = InternalComputeProvider()._build_row(bar_ts, "000001", "daily", row_data, columns)
        assert row[4] is None

    def test_symbol_leading_zeros(self):
        """symbol 前导零保留（回归测试核心）。"""
        columns = ["trade_date", "trade_time", "symbol", "period", "data_source"]
        for sym in ["000001", "000002", "600000", "300001"]:
            row = InternalComputeProvider()._build_row(
                pd.Timestamp("2026-08-10"), sym, "daily", pd.Series(dtype=float), columns
            )
            assert row[2] == sym, f"symbol {sym} 前导零被剥离！"


# ===========================================================================
# symbol 前导零回归测试（dtype=str 修复）
# ===========================================================================


class TestSymbolLeadingZerosRegression:
    """回归测试：pd.read_csv dtype=str 防止 symbol 前导零剥离。

    Bug 背景：_read_kline_data 原用 pd.read_csv(dtype=None) 自动推断，
    将 '000001' 当整数解析为 1，剥离前导零。修复：dtype=str 全部读为字符串。
    """

    def test_read_csv_preserves_leading_zeros(self):
        """模拟 TSV 解析：dtype=str 保留前导零。"""
        from io import StringIO

        tsv = "000001\t2026-08-10\t11.19\t11.30\t11.10\t11.29\t100000\n"
        tsv += "000002\t2026-08-10\t3.20\t3.25\t3.18\t3.22\t200000\n"

        # 修复前（dtype=None）：symbol 被推断为整数
        df_buggy = pd.read_csv(StringIO(tsv), sep="\t", header=None)
        # 000001 → 1（整数推断剥离前导零）
        assert str(df_buggy.iloc[0, 0]) == "1", "测试前提：dtype=None 确实剥离前导零"

        # 修复后（dtype=str）：symbol 保留前导零
        df_fixed = pd.read_csv(StringIO(tsv), sep="\t", header=None, dtype=str)
        assert df_fixed.iloc[0, 0] == "000001", "dtype=str 应保留前导零"
        assert df_fixed.iloc[1, 0] == "000002"

    def test_numeric_conversion_after_dtype_str(self):
        """dtype=str 后数值列需显式 to_numeric 转换。"""
        from io import StringIO

        tsv = "000001\t11.19\t100000\n"
        df = pd.read_csv(StringIO(tsv), sep="\t", header=None, dtype=str)
        df.columns = ["symbol", "close", "volume"]
        # 转换前：字符串
        assert df["close"].dtype == object
        # 转换后：浮点
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        assert df["close"].dtype == np.float64
        assert df["close"].iloc[0] == pytest.approx(11.19)
        assert df["symbol"].iloc[0] == "000001"  # symbol 仍为字符串
