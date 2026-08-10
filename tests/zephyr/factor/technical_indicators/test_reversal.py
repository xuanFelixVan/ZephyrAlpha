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
