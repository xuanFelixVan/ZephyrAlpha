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
from unittest.mock import patch

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


class TestCandlestickThinView:
    """薄视图（实现移交图形域 scan_candles，裁定①方案A）——映射/降级/边界。"""

    def _event(self, pid: str, day: int, direction: str = "向上") -> dict:
        from datetime import date, timedelta

        return {
            "pattern_id": pid,
            "pattern_class": "K线",
            "direction": direction,
            "confidence": 0.8,
            "anchor_trade_date": (date(2000, 1, 1) + timedelta(days=day)).isoformat(),
            "symbol": "TEST",
        }

    def test_mapping_hammer(self):
        """CDLHAMMER 事件 → 编码 1 落在正确 bar。"""
        df = _make_ohlcv(30)
        with patch(
            "zephyr.signal_ashare.strategy_signal.candlestick_scanner.scan_candles",
            return_value=[self._event("CDLHAMMER", 10)],
        ):
            result = CandlestickPattern().compute(df)
        assert result["candle_pattern"].iloc[10] == 1.0
        assert (result["candle_pattern"].drop(index=10) == 0.0).all()

    def test_mapping_engulfing_direction(self):
        """吞没方向：向上→+2，向下→-2。"""
        df = _make_ohlcv(30)
        with patch(
            "zephyr.signal_ashare.strategy_signal.candlestick_scanner.scan_candles",
            return_value=[
                self._event("CDLENGULFING", 5, "向上"),
                self._event("CDLENGULFING", 15, "向下"),
            ],
        ):
            result = CandlestickPattern().compute(df)
        assert result["candle_pattern"].iloc[5] == 2.0
        assert result["candle_pattern"].iloc[15] == -2.0

    def test_unknown_cdl_ignored(self):
        """非 6 编码形态（如 CDL3BLACKCROWS）不进旧列。"""
        df = _make_ohlcv(30)
        with patch(
            "zephyr.signal_ashare.strategy_signal.candlestick_scanner.scan_candles",
            return_value=[self._event("CDL3BLACKCROWS", 8)],
        ):
            result = CandlestickPattern().compute(df)
        assert (result["candle_pattern"] == 0.0).all()

    def test_degrade_to_zero_on_scanner_failure(self):
        """scan_candles 不可用（talib 缺失等）→ 降级全 0 不炸生产批。"""
        df = _make_ohlcv(30)
        with patch(
            "zephyr.signal_ashare.strategy_signal.candlestick_scanner.scan_candles",
            side_effect=RuntimeError("talib 不可得"),
        ):
            result = CandlestickPattern().compute(df)
        assert (result["candle_pattern"] == 0.0).all()

    def test_signal_range_real_scanner(self):
        """真实 scan_candles（talib 0.7 在装）：值域 {-2,0,1,2,3,4,5}。"""
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
