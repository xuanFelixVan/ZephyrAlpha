# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""反转类技术指标测试（5 个，v1.0.0 全部施工完成）。

测试内容：
- 5 个反转指标全部注册到 Registry
- 每个指标 meta.category == "reversal"
- 每个指标 meta.output_columns == 期望列（catalog §2.5 契约）
- 已实现指标（全部 5 个）：信号输出正确性 + 边界测试

信号输出约定：0.0=无信号, 1.0=正信号(看涨), -1.0=负信号(看跌)
K线形态编码：0=无, 1=锤子, 2=看涨吞没, -2=看跌吞没, 3=启明星, 4=黄昏星, 5=十字星

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import reversal  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 期望契约（catalog §2.5）：indicator_id → (name, output_columns)
EXPECTED = {
    "candlestick_pattern": ("K线形态", ["candle_pattern"]),
    "rsi_divergence": ("RSI背离", ["rsi_divergence"]),
    "macd_divergence": ("MACD背离", ["macd_divergence"]),
    "boll_breakout": ("布林带突破", ["boll_breakout"]),
    "vol_price_divergence": ("量价背离", ["vol_price_div"]),
}

IMPLEMENTED = set(EXPECTED)  # 全部 5 个已施工完成
SKELETON = set(EXPECTED) - IMPLEMENTED  # 空集

_RNG = np.random.default_rng(42)


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正）。"""
    close = 100 + _RNG.standard_normal(n).cumsum()
    high = close + _RNG.uniform(0.1, 0.5, n)
    low = close - _RNG.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


class TestReversalRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("reversal")}
        for iid in EXPECTED:
            assert iid in metas, f"反转指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("reversal")) == len(EXPECTED) == 5


class TestReversalMetaContract:
    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_category(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.category == "reversal"

    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_name(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.name == expected[0]

    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_output_columns(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.output_columns == expected[1]

    @pytest.mark.parametrize("iid", list(EXPECTED.keys()))
    def test_input_columns_valid(self, iid):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert len(meta.input_columns) > 0
        assert set(meta.input_columns) <= {"open", "high", "low", "close", "volume"}

    @pytest.mark.parametrize("iid", list(EXPECTED.keys()))
    def test_params_is_dict(self, iid):
        assert isinstance(TechnicalIndicatorRegistry.get(iid).meta.params, dict)


class TestReversalComputeNotImplemented:
    @pytest.mark.parametrize("iid", sorted(SKELETON))
    def test_compute_raises(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        df = pd.DataFrame(
            {"open": [10.0] * 30, "high": [11.0] * 30, "low": [9.0] * 30, "close": [10.5] * 30, "volume": [1000.0] * 30}
        )
        with pytest.raises(NotImplementedError, match="待施工"):
            cls().compute(df)


# ===========================================================================
# CandlestickPattern 信号正确性测试
# ===========================================================================

CandlestickPattern = TechnicalIndicatorRegistry.get("candlestick_pattern")


class TestCandlestickPatternCompute:
    """K线形态识别——信号编码正确性 + 边界测试。"""

    def test_doji_pattern(self):
        """十字星：实体 < 10% 振幅 → 编码 5。"""
        df = pd.DataFrame(
            {
                "open": [10.0] * 30,
                "close": [10.01] * 30,
                "high": [10.5] * 30,
                "low": [9.5] * 30,
            }
        )
        result = CandlestickPattern().compute(df)
        # body=0.01, range=1.0 → 0.01/1.0=0.01 < 0.1 → doji
        assert (result["candle_pattern"] == 5.0).all()

    def test_signal_range(self):
        """形态编码在 {-2, 0, 1, 2, 3, 4, 5} 范围内。"""
        df = _make_ohlcv(50)
        result = CandlestickPattern().compute(df)
        valid = result["candle_pattern"].dropna().unique()
        assert set(valid) <= {-2.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0}

    def test_empty_dataframe(self):
        result = CandlestickPattern().compute(pd.DataFrame(columns=["open", "high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CandlestickPattern().compute(pd.DataFrame({"close": [10.0]}))


# ===========================================================================
# RSI Divergence 信号正确性测试
# ===========================================================================

RSIDivergence = TechnicalIndicatorRegistry.get("rsi_divergence")


class TestRSIDivergenceCompute:
    """RSI背离——信号正确性 + 边界测试。"""

    def test_signal_values(self):
        """信号值 ∈ {-1, 0, 1}。"""
        df = _make_ohlcv(60)
        result = RSIDivergence().compute(df)
        valid = result["rsi_divergence"].dropna().unique()
        assert set(valid) <= {-1.0, 0.0, 1.0}

    def test_empty_dataframe(self):
        result = RSIDivergence().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            RSIDivergence().compute(pd.DataFrame({"open": [10.0]}))


def _double_top_close(n: int = 60, weak_second: bool = True) -> pd.Series:
    """构造双峰价格（峰分别在 bar20 / bar40，间距 20 恰在默认 lookback=20 内）。

    weak_second=True（背离场景）：第一峰 bar10-20 每日 +1.0 连涨至 111（RSI≈100），
      第二峰 bar31-40 每日 +0.65 缓涨至 111.5（10 涨 0.65 + 前置 2 跌 0.5，RSI≈87）
      → 价新高 111.5>111 + RSI 较低 = 顶背离。
    weak_second=False（确认场景）：第一峰混合涨跌至 104（RSI≈70），
      第二峰 bar31-40 每日 +2.0 强势连涨至 119（RSI≈97 更高）→ RSI 同步确认，非背离。
    """
    vals = [100.0] * 10
    if weak_second:
        vals += [100.0 + i * 1.0 for i in range(1, 12)]  # bar10..20 → 峰 111（连涨）
        vals += [111.0 - i * 0.5 for i in range(1, 11)]  # bar21..30 → 106
        step2 = 0.65
    else:
        v = 100.0
        for i in range(1, 12):  # bar10..20 混合涨跌 → 峰 104
            v += 1.0 if i % 2 else -0.4
            vals.append(v)
        vals += [104.0 - i * 0.5 for i in range(1, 11)]  # bar21..30 → 99
        step2 = 2.0
    base2 = vals[-1]
    vals += [base2 + i * step2 for i in range(1, 11)]  # bar31..40 → 第二峰
    peak2 = vals[-1]
    vals += [peak2 - i * 0.5 for i in range(1, 10)]  # bar41..49 回落
    vals += [peak2 - 4.5] * (n - len(vals))
    return pd.Series(vals[:n], dtype=float)


def _double_bottom_close(n: int = 60, strong_second: bool = True) -> pd.Series:
    """构造双谷价格：bar20 急跌谷 89（RSI≈0），bar40 缓跌谷 88.5（RSI≈22 较高）。

    → 价新低 88.5<89 + RSI 较高 = 底背离。段间衔接一律用 vals[-1]，防硬编码错位。
    """
    vals = [100.0] * 10
    vals += [100.0 - i * 1.0 for i in range(1, 12)]  # bar10..20 → 谷 89（连跌）
    base1 = vals[-1]
    vals += [base1 + i * 0.5 for i in range(1, 11)]  # bar21..30 → 94
    step2 = 0.55 if strong_second else 1.2
    base2 = vals[-1]
    vals += [base2 - i * step2 for i in range(1, 11)]  # bar31..40 → 第二谷
    trough2 = vals[-1]
    vals += [trough2 + i * 0.5 for i in range(1, 10)]  # bar41..49 回升
    vals += [trough2 + 4.5] * (n - len(vals))
    return pd.Series(vals[:n], dtype=float)


class TestRSIDivergencePeakTrough:
    """RSI 背离峰谷检测升级（16 catalog §7④：简化趋势对比→峰谷检测）。

    顶背离=价格更高峰 + RSI 较低峰；底背离=价格更低谷 + RSI 较高谷；
    信号标在确认点（第二峰/谷 + peak_order，居中窗口确认无前视）。
    """

    def test_bearish_divergence_detected(self):
        close = _double_top_close(60, weak_second=True)
        df = pd.DataFrame({"close": close})
        sig = RSIDivergence().compute(df)["rsi_divergence"]
        # 第二峰 bar40 + peak_order(3) = bar43 标 1（顶背离）
        assert sig.iloc[43] == 1.0
        assert (sig == 1.0).sum() == 1

    def test_no_divergence_when_rsi_confirms(self):
        close = _double_top_close(60, weak_second=False)  # 第二峰更强 → RSI 同步新高
        df = pd.DataFrame({"close": close})
        sig = RSIDivergence().compute(df)["rsi_divergence"]
        assert (sig == 1.0).sum() == 0

    def test_bullish_divergence_detected(self):
        close = _double_bottom_close(60, strong_second=True)
        df = pd.DataFrame({"close": close})
        sig = RSIDivergence().compute(df)["rsi_divergence"]
        assert sig.iloc[43] == -1.0
        assert (sig == -1.0).sum() == 1

    def test_peaks_beyond_lookback_ignored(self):
        # 双峰间距 20 > lookback=10 → 不构成背离
        close = _double_top_close(60, weak_second=True)
        df = pd.DataFrame({"close": close})
        sig = RSIDivergence().compute(df, lookback=10)["rsi_divergence"]
        assert (sig != 0.0).sum() == 0

    def test_flat_series_no_signal(self):
        df = pd.DataFrame({"close": [100.0] * 60})
        sig = RSIDivergence().compute(df)["rsi_divergence"]
        assert (sig == 0.0).all()


# ===========================================================================
# MACD Divergence 信号正确性测试
# ===========================================================================

MACDDivergence = TechnicalIndicatorRegistry.get("macd_divergence")


class TestMACDDivergenceCompute:
    """MACD背离——信号正确性 + 边界测试。"""

    def test_signal_values(self):
        """信号值 ∈ {-1, 0, 1}。"""
        df = _make_ohlcv(60)
        result = MACDDivergence().compute(df)
        valid = result["macd_divergence"].dropna().unique()
        assert set(valid) <= {-1.0, 0.0, 1.0}

    def test_empty_dataframe(self):
        result = MACDDivergence().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MACDDivergence().compute(pd.DataFrame({"open": [10.0]}))


class TestMACDDivergencePeakTrough:
    """MACD 背离峰谷检测（价格峰谷 vs HIST 值，信号标在峰确认点）。"""

    def test_bearish_divergence_detected(self):
        close = _double_top_close(80, weak_second=True)
        df = pd.DataFrame({"close": close})
        sig = MACDDivergence().compute(df)["macd_divergence"]
        # 价更高峰 + HIST 较低 → 顶背离，标在 bar43（第二峰确认点）
        assert sig.iloc[43] == 1.0
        assert (sig == 1.0).sum() == 1

    def test_bullish_divergence_detected(self):
        close = _double_bottom_close(80, strong_second=True)
        df = pd.DataFrame({"close": close})
        sig = MACDDivergence().compute(df)["macd_divergence"]
        assert sig.iloc[43] == -1.0
        assert (sig == -1.0).sum() == 1


# ===========================================================================
# BOLL Breakout 信号正确性测试
# ===========================================================================

BOLLBreakout = TechnicalIndicatorRegistry.get("boll_breakout")


class TestBOLLBreakoutCompute:
    """布林带突破——信号正确性 + 边界测试。"""

    def test_signal_values(self):
        """信号值 ∈ {-1, 0, 1}。"""
        df = _make_ohlcv(60)
        result = BOLLBreakout().compute(df)
        valid = result["boll_breakout"].dropna().unique()
        assert set(valid) <= {-1.0, 0.0, 1.0}

    def test_empty_dataframe(self):
        result = BOLLBreakout().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            BOLLBreakout().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# Volume-Price Divergence 信号正确性测试
# ===========================================================================

VolPriceDivergence = TechnicalIndicatorRegistry.get("vol_price_divergence")


class TestVolPriceDivergenceCompute:
    """量价背离——信号正确性 + 边界测试。"""

    def test_signal_values(self):
        """信号值 ∈ {-1, 0, 1}。"""
        df = _make_ohlcv(60)
        result = VolPriceDivergence().compute(df)
        valid = result["vol_price_div"].dropna().unique()
        assert set(valid) <= {-1.0, 0.0, 1.0}

    def test_empty_dataframe(self):
        result = VolPriceDivergence().compute(pd.DataFrame(columns=["close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            VolPriceDivergence().compute(pd.DataFrame({"close": [10.0]}))
