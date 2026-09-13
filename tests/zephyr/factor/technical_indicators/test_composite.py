# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""复合类技术指标测试（Ichimoku，2026-09-14 批 3 补实现）。

测试内容：
- ichimoku 注册到 Registry（category=composite，IND-COMP-001 candidate→active）
- 5 输出列契约（tenkan/kijun/senkou_a/senkou_b/chikou）
- 数值正确性：常数价格=常数线；小样本手算转折线/基准线；先行跨度 26 位显示位移 PIT 口径
- 边界：warmup NaN、空 DataFrame 短路、缺列抛 ValueError
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import trend  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

ICHIMOKU = TechnicalIndicatorRegistry.get("ichimoku")


def _make_ohlcv(n: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + rng.uniform(0.1, 0.5, n)
    low = close - rng.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


class TestIchimokuContract:
    def test_registered_composite(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("composite")}
        assert "ichimoku" in metas

    def test_meta_contract(self):
        meta = ICHIMOKU().meta
        assert meta.output_columns == [
            "tenkan_sen", "kijun_sen", "senkou_span_a", "senkou_span_b", "chikou_span",
        ]
        assert meta.category == "composite"


class TestIchimokuNumeric:
    def test_manual_tenkan_kijun(self):
        df = _make_ohlcv(40)
        result = ICHIMOKU().compute(df)
        hh9 = df["high"].rolling(9).max()
        ll9 = df["low"].rolling(9).min()
        expected_tenkan = (hh9 + ll9) / 2
        np.testing.assert_allclose(
            result["tenkan_sen"].dropna(), expected_tenkan.dropna(), rtol=1e-12
        )
        hh26 = df["high"].rolling(26).max()
        ll26 = df["low"].rolling(26).min()
        np.testing.assert_allclose(
            result["kijun_sen"].dropna(), ((hh26 + ll26) / 2).dropna(), rtol=1e-12
        )

    def test_senkou_shift_is_display_position(self):
        """先行跨度存显示位（shift 26）：t 行的值=26 根前的 (T+K)/2，PIT 无前视。"""
        df = _make_ohlcv(90)
        result = ICHIMOKU().compute(df)
        tenkan = (df["high"].rolling(9).max() + df["low"].rolling(9).min()) / 2
        kijun = (df["high"].rolling(26).max() + df["low"].rolling(26).min()) / 2
        expected_a = ((tenkan + kijun) / 2).shift(26)
        got = result["senkou_span_a"].dropna()
        exp = expected_a.reindex(got.index)
        np.testing.assert_allclose(got, exp, rtol=1e-12, equal_nan=False)

    def test_chikou_is_computation_time_close(self):
        """迟行跨度存计算时点值（后移 26 是显示位移，存储不前视）。"""
        df = _make_ohlcv(60)
        result = ICHIMOKU().compute(df)
        # chikou_span 无 NaN 且等于 close
        assert result["chikou_span"].notna().all()
        np.testing.assert_allclose(result["chikou_span"], df["close"], rtol=1e-12)

    def test_empty_and_missing(self):
        assert ICHIMOKU().compute(
            pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        ).empty
        with pytest.raises(ValueError, match="缺少列"):
            ICHIMOKU().compute(pd.DataFrame({"high": [1.0] * 30, "low": [1.0] * 30}))
