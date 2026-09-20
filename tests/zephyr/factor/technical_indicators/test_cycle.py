# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""循环族技术指标测试（HT 系 5 指标 + EBSW，批 3 新建/清欠班波2-A +1）。

测试内容：
- 6 个循环指标全部注册（category=cycle，MOD-L02-029）
- 输出列契约（8 列）
- 数值边界：预热 63 根 NaN、主导周期钳位 [6,50]、正弦 ∈ [-1,1]、trendmode ∈ {0,1}
- 循环输入（已知周期正弦）应产出接近该周期的主导周期
- EBSW：独立复算 + 退化微样本 + 种子/预热/钳位边界（移植源 pandas_ta_classic/cycles/ebsw.py）
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
EBSW = TechnicalIndicatorRegistry.get("ebsw")

EXPECTED = {
    "ht_dcperiod": ("主导周期", ["ht_dcperiod"]),
    "ht_dcphase": ("主导周期相位", ["ht_dcphase"]),
    "ht_phasor": ("同相正交分量", ["ht_ip", "ht_qp"]),
    "ht_sine": ("正弦波", ["ht_sine", "ht_leadsine"]),
    "ht_trendmode": ("趋势循环模式", ["ht_trendmode"]),
    "ebsw": ("更优正弦波", ["ebsw_40"]),
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
        assert len(TechnicalIndicatorRegistry.list_by_category("cycle")) == len(EXPECTED) == 6

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
        df = pd.DataFrame(
            {
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 1000.0,
            }
        )
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


# ===========================================================================
# 2026-09-20 清欠班波2-A：EBSW 数值正确性（pandas_ta_classic/cycles/ebsw.py 移植）
# ===========================================================================


class TestEbswNumeric:
    """EBSW 更优正弦波——独立复算（纯 python 递推）+ 退化微样本 + 种子/预热/钳位边界。"""

    @staticmethod
    def _recompute(close: np.ndarray, length: int, bars: int) -> np.ndarray:
        """测试内独立书写的公式直译（与实现解耦的纯 python 复算）。"""
        m = close.size
        out = np.full(m, np.nan)
        if length - 1 < m:
            out[length - 1] = 0.0
        alpha1 = (1 - np.sin(360 / length)) / np.cos(360 / length)
        a1 = np.exp(-np.sqrt(2) * np.pi / bars)
        b1 = 2 * a1 * np.cos(np.sqrt(2) * 180 / bars)
        c2, c3 = b1, -a1 * a1
        c1 = 1 - c2 - c3
        lc = lhp = fh0 = fh1 = 0.0
        for i in range(length, m):
            hp = 0.5 * (1 + alpha1) * (close[i] - lc) + alpha1 * lhp
            filt = c1 * (hp + lhp) / 2 + c2 * fh1 + c3 * fh0
            wave = (filt + fh1 + fh0) / 3
            pwr = (filt * filt + fh1 * fh1 + fh0 * fh0) / 3
            out[i] = wave / np.sqrt(pwr) if pwr > 0 else 0.0
            fh0, fh1 = fh1, filt
            lhp, lc = hp, close[i]
        return out

    def test_independent_recompute(self):
        """独立复算锚点：纯 python 递推全序列对拍（rtol=atol=1e-12）。"""
        rng = np.random.default_rng(11)
        close = 100 + rng.standard_normal(120).cumsum()
        df = pd.DataFrame({"close": close})
        got = EBSW().compute(df)["ebsw_40"].to_numpy()
        expected = self._recompute(close, 40, 10)
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)

    def test_hand_degenerate_micro(self):
        """手工微样本（length=3/bars=2，close=[1,2,3,4]）：
        第 length−1=2 根种子 0.0；i=3 单项 Filt → Wave/√Pwr=(Filt/3)/(Filt/√3)=1/√3（手推写死）。
        """
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0]})
        got = EBSW().compute(df, length=3, bars=2)["ebsw_3"].to_numpy()
        assert np.isnan(got[:2]).all()
        assert got[2] == 0.0
        assert got[3] == pytest.approx(1.0 / np.sqrt(3.0), rel=1e-12)

    def test_warmup_seed_and_bounds(self):
        """预热：前 39 根 NaN；第 39 根种子 0.0；其后有效且钳位 [-1,1]（Cauchy–Schwarz 界）。"""
        rng = np.random.default_rng(42)
        close = 100 + rng.standard_normal(120).cumsum()
        df = pd.DataFrame({"close": close})
        got = EBSW().compute(df)["ebsw_40"]
        assert got.iloc[:39].isna().all()
        assert got.iloc[39] == 0.0
        assert got.iloc[40:].notna().all()
        valid = got.dropna()
        assert valid.abs().max() <= 1.0 + 1e-9

    def test_kwargs_override(self):
        """kwargs 覆盖：length=20 → 列名 ebsw_20、种子位 index 19；bars 变更改变数值。"""
        rng = np.random.default_rng(7)
        close = 100 + rng.standard_normal(80).cumsum()
        df = pd.DataFrame({"close": close})
        short = EBSW().compute(df, length=20)
        assert list(short.columns) == ["ebsw_20"]
        assert short["ebsw_20"].iloc[:19].isna().all()
        assert short["ebsw_20"].iloc[19] == 0.0
        base = EBSW().compute(df)["ebsw_40"].to_numpy()
        alt = EBSW().compute(df, bars=5)["ebsw_40"].to_numpy()
        assert not np.allclose(base[40:], alt[40:])

    def test_empty_and_missing_column(self):
        result = EBSW().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["ebsw_40"]
        with pytest.raises(ValueError):
            EBSW().compute(pd.DataFrame({"close2": [1.0] * 80}))
