# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""循环族技术指标测试（HT 系 5 指标，2026-09-14 批 3 新建）。

测试内容：
- 5 个 HT 指标全部注册（category=cycle，MOD-L02-029）
- 输出列契约（7 列）
- 数值边界：预热 63 根 NaN、主导周期钳位 [6,50]、正弦 ∈ [-1,1]、trendmode ∈ {0,1}
- 循环输入（已知周期正弦）应产出接近该周期的主导周期
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import cycle  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

HT_DCPERIOD = TechnicalIndicatorRegistry.get("ht_dcperiod")
HT_DCPHASE = TechnicalIndicatorRegistry.get("ht_dcphase")
HT_PHASOR = TechnicalIndicatorRegistry.get("ht_phasor")
HT_SINE = TechnicalIndicatorRegistry.get("ht_sine")
HT_TRENDMODE = TechnicalIndicatorRegistry.get("ht_trendmode")

EXPECTED = {
    "ht_dcperiod": ("主导周期", ["ht_dcperiod"]),
    "ht_dcphase": ("主导周期相位", ["ht_dcphase"]),
    "ht_phasor": ("同相正交分量", ["ht_ip", "ht_qp"]),
    "ht_sine": ("正弦波", ["ht_sine", "ht_leadsine"]),
    "ht_trendmode": ("趋势循环模式", ["ht_trendmode"]),
}


def _make_ohlcv(n: int = 150) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + rng.uniform(0.1, 0.5, n)
    low = close - rng.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


class TestHtRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("cycle")}
        for iid in EXPECTED:
            assert iid in metas, f"循环指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("cycle")) == len(EXPECTED) == 5

    def test_meta_contract(self):
        for iid, (name, cols) in EXPECTED.items():
            meta = TechnicalIndicatorRegistry.get(iid).meta
            assert meta.name == name
            assert meta.output_columns == cols


class TestHtNumeric:
    def test_warmup_63_nan(self):
        df = _make_ohlcv(120)
        result = HT_DCPERIOD().compute(df)
        assert result["ht_dcperiod"].iloc[:62].isna().all()
        assert result["ht_dcperiod"].iloc[63:].notna().all()

    def test_dcperiod_clamped(self):
        df = _make_ohlcv(200)
        result = HT_DCPERIOD().compute(df)
        valid = result["ht_dcperiod"].dropna()
        assert valid.between(6, 50).all()

    def test_sine_bounded(self):
        df = _make_ohlcv(200)
        result = HT_SINE().compute(df)
        assert result["ht_sine"].dropna().abs().max() <= 1.0 + 1e-9
        assert result["ht_leadsine"].dropna().abs().max() <= 1.0 + 1e-9

    def test_trendmode_binary(self):
        df = _make_ohlcv(200)
        result = HT_TRENDMODE().compute(df)
        assert result["ht_trendmode"].dropna().isin([0.0, 1.0]).all()

    def test_dominant_cycle_recovers_sinusoid_period(self):
        """已知 20 日正弦输入 → 主导周期应落入同量级窗口（相位累积口径 ±50%）。"""
        n = 300
        close = 100 + 5 * np.sin(np.arange(n) * 2 * np.pi / 20)
        df = pd.DataFrame({
            "open": close, "high": close, "low": close, "close": close, "volume": 1000.0,
        })
        result = HT_DCPERIOD().compute(df)
        tail = result["ht_dcperiod"].dropna().tail(50)
        assert 15 <= tail.median() <= 30, f"主导周期中位数 {tail.median():.1f} 偏离 20 过远"

    def test_phasor_columns(self):
        result = HT_PHASOR().compute(_make_ohlcv(150))
        assert list(result.columns) == ["ht_ip", "ht_qp"]
        assert result["ht_qp"].dropna().shape[0] > 0


class TestHtBoundaries:
    def test_empty_shortcircuit(self):
        for cls in (HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_TRENDMODE):
            assert cls().compute(pd.DataFrame(columns=["close"])).empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError):
            HT_DCPERIOD().compute(pd.DataFrame({"close2": [1.0] * 80}))

    def test_short_input_all_nan(self):
        """短于预热期（63）的输入全 NaN 不崩。"""
        df = pd.DataFrame({"close": np.linspace(100, 110, 40)})
        result = HT_DCPERIOD().compute(df)
        assert result["ht_dcperiod"].isna().all()
