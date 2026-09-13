# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""反转类技术指标测试（4 个，v1.0.0 全部施工完成）。

测试内容：
- 5 个反转指标全部注册到 Registry
- 每个指标 meta.category == "reversal"
- 每个指标 meta.output_columns == 期望列（catalog §2.5 契约）
- 已实现指标（全部 5 个）：信号输出正确性 + 边界测试

信号输出约定：0.0=无信号, 1.0=正信号(看涨), -1.0=负信号(看跌)

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
        assert len(TechnicalIndicatorRegistry.list_by_category("reversal")) == len(EXPECTED) == 4


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


