# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""循环族技术指标测试（HT 系 5 指标 + EBSW + CONTINUATION/GPRED；批 3 新建/班波2-A +1/班波5 +2）。

测试内容：
- 8 个循环指标全部注册（category=cycle，MOD-L02-029）
- 输出列契约（11 列）
- 数值边界：预热 63 根 NaN、主导周期钳位 [6,50]、正弦 ∈ [-1,1]、trendmode ∈ {0,1}
- 循环输入（已知周期正弦）应产出接近该周期的主导周期
- EBSW：独立复算 + 退化微样本 + 种子/预热/钳位边界（移植源 pandas_ta_classic/cycles/ebsw.py）
- CONTINUATION：独立复算 + CI 值域 [-1,1]/常数判零零保护/正弦 ±1 两态切换
  （移植源 mesasoftware.com/papers/Continuation Index.pdf，TASC 2025-09）
- GPRED：独立复算 + 正弦预测相关系数>0.9（灵魂断言）+ 常数退化 + gp_sig 有界
  （移植源 mesasoftware.com/papers/Linear Predictive Filters.pdf，TASC 2025-01）
"""

from __future__ import annotations

import math

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
CONTINUATION = TechnicalIndicatorRegistry.get("continuation")
GPRED = TechnicalIndicatorRegistry.get("gpred")

EXPECTED = {
    "ht_dcperiod": ("主导周期", ["ht_dcperiod"]),
    "ht_dcphase": ("主导周期相位", ["ht_dcphase"]),
    "ht_phasor": ("同相正交分量", ["ht_ip", "ht_qp"]),
    "ht_sine": ("正弦波", ["ht_sine", "ht_leadsine"]),
    "ht_trendmode": ("趋势循环模式", ["ht_trendmode"]),
    "ebsw": ("更优正弦波", ["ebsw_40"]),
    "continuation": ("延续指数", ["continuation_40"]),
    "gpred": ("Griffiths线性预测器", ["gp_sig", "gp_pred"]),
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
        assert len(TechnicalIndicatorRegistry.list_by_category("cycle")) == len(EXPECTED) == 8

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


# ===========================================================================
# 2026-09-20 清欠班波5：CONTINUATION/GPRED 数值正确性
# （mesasoftware.com Ehlers TASC 2025-09 / 2025-01 论文移植；talib 无此二件，
#   黄金锚=独立复算+性质断言）
# ===========================================================================


class TestContinuationNumeric:
    """CONTINUATION 延续指数——独立复算 + CI 值域/常数判零/正弦两态切换。"""

    @staticmethod
    def _usmoother(price: list[float], period: int) -> list[float]:
        """测试内独立书写的 UltimateSmoother（纯 list + math，与实现解耦）。"""
        q = math.exp(-1.414 * math.pi / period)
        c1 = 2 * q * math.cos(1.414 * math.pi / period)
        c2 = q * q
        a0 = (1 + c1 + c2) / 4
        us = list(price[:4]) + [0.0] * (len(price) - 4)
        for t in range(4, len(price)):
            us[t] = (
                (1 - a0) * price[t]
                + (2 * a0 - c1) * price[t - 1]
                + (c2 - a0) * price[t - 2]
                + c1 * us[t - 1]
                - c2 * us[t - 2]
            )
        return us

    @classmethod
    def _recompute(cls, close: np.ndarray, gamma: float, order: int, length: int) -> np.ndarray:
        """公式直译复算：US/Laguerre/滚动均值归一/逆费雪（纯 python 路径）。"""
        n = len(close)
        p = [float(x) for x in close]
        us_line = cls._usmoother(p, length)  # Laguerre L1 行用全长
        us = cls._usmoother(p, max(length // 2, 1))
        prev = [0.0] * (order + 1)
        lg: list[float] = []
        for t in range(n):
            cur = [0.0] * (order + 1)
            for k in range(2, order + 1):
                cur[k] = -gamma * prev[k - 1] + prev[k - 1] + gamma * prev[k]
            cur[1] = us_line[t]
            lg.append(sum(cur[1:]) / order)
            prev = cur
        out = [float("nan")] * n
        for t in range(length - 1, n):
            var = sum(abs(us[j] - lg[j]) for j in range(t - length + 1, t + 1)) / length
            if var > 1e-9 * (1 + abs(us[t])):  # 零保护（相对容差口径与实现一致）
                ref = max(-20.0, min(20.0, 2 * (us[t] - lg[t]) / var))
                out[t] = (math.exp(2 * ref) - 1) / (math.exp(2 * ref) + 1)
            else:
                out[t] = 0.0
        return np.array(out)

    def test_independent_recompute(self):
        """独立复算锚点：纯 python 递推全序列对拍（rtol=1e-10）。"""
        rng = np.random.default_rng(11)
        close = 100 + rng.standard_normal(120).cumsum()
        got = CONTINUATION().compute(pd.DataFrame({"close": close}))["continuation_40"].to_numpy()
        expected = self._recompute(close, gamma=0.8, order=8, length=40)
        np.testing.assert_allclose(got, expected, rtol=1e-10, atol=1e-12)

    def test_warmup_range_and_zero_protection(self):
        """预热：前 39 根 NaN（Variance 滚动窗）；值域 [-1,1]；常数输入尾段精确 0（零保护）。"""
        rng = np.random.default_rng(42)
        close = 100 + rng.standard_normal(200).cumsum()
        got = CONTINUATION().compute(pd.DataFrame({"close": close}))["continuation_40"]
        assert got.iloc[:39].isna().all()
        assert got.iloc[39:].notna().all()
        valid = got.dropna()
        assert valid.abs().max() <= 1.0 + 1e-9
        # 常数输入：Laguerre 零种子瞬态 ~180 根衰减后 Variance 判零 → CI 精确 0
        for const in (100.0, 3000.0):
            flat = CONTINUATION().compute(pd.DataFrame({"close": np.full(300, const)}))["continuation_40"]
            assert flat.iloc[:39].isna().all()
            assert (flat.iloc[200:] == 0.0).all()

    def test_sine_two_state_switching(self):
        """正弦输入 → CI 在 ±1 两态间切换（价格穿越 Laguerre 线处换向，宽松带：过零 ≥2）。"""
        n = 300
        close = 100 + 5 * np.sin(np.arange(n) * 2 * np.pi / 24)
        got = CONTINUATION().compute(pd.DataFrame({"close": close}))["continuation_40"].to_numpy()
        v = got[40:]
        signs = np.sign(v)
        cross = int(np.sum(signs[1:] * signs[:-1] < 0))
        assert cross >= 2, f"过零次数 {cross} < 2"
        assert v.max() > 0.9, f"未达 +1 态（max={v.max():.3f}）"
        assert v.min() < -0.9, f"未达 -1 态（min={v.min():.3f}）"

    def test_kwargs_gamma_keeps_column(self):
        """kwargs 覆盖 gamma → 列名固定 continuation_40（先例=ebsw_40），数值改变。"""
        rng = np.random.default_rng(7)
        close = 100 + rng.standard_normal(150).cumsum()
        df = pd.DataFrame({"close": close})
        alt = CONTINUATION().compute(df, gamma=0.4)
        assert list(alt.columns) == ["continuation_40"]
        base = CONTINUATION().compute(df)["continuation_40"].to_numpy()
        assert not np.allclose(base[40:], alt["continuation_40"].to_numpy()[40:])

    def test_empty_and_missing_column(self):
        result = CONTINUATION().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["continuation_40"]
        with pytest.raises(ValueError):
            CONTINUATION().compute(pd.DataFrame({"close2": [1.0] * 80}))


class TestGpredNumeric:
    """GPRED Griffiths 线性预测器——独立复算 + 正弦预测领先（灵魂断言）+ 退化/有界。"""

    @staticmethod
    def _recompute(
        close: np.ndarray, upper_bound: int, lower_bound: int, length: int, bars_fwd: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """公式直译复算：HighPass3/SuperSmoother/Peak 归一/Griffiths LMS（纯 python）。"""
        n = len(close)
        p = [float(x) for x in close]
        f = 1.414 * math.pi / upper_bound
        a1 = math.exp(-f)
        hc2 = 2 * a1 * math.cos(f / 2)
        hc3 = -(a1 * a1)
        hc1 = (1 + hc2 - hc3) / 4
        hp = [0.0] * n
        for t in range(2, n):
            hp[t] = hc1 * (p[t] - 2 * p[t - 1] + p[t - 2]) + hc2 * hp[t - 1] + hc3 * hp[t - 2]
        sa = math.exp(-1.414 * math.pi / lower_bound)
        sc2 = 2 * sa * math.cos(1.414 * math.pi / lower_bound)
        sc3 = -(sa * sa)
        sc1 = 1 - sc2 - sc3
        lp = list(hp[:2]) + [0.0] * (n - 2)  # t<2 种子取 HP 当根值
        for t in range(2, n):
            lp[t] = sc1 * (hp[t] + hp[t - 1]) / 2 + sc2 * lp[t - 1] + sc3 * lp[t - 2]
        signal = [0.0] * n
        peak = 0.1
        for t in range(n):
            peak *= 0.991
            if abs(lp[t]) > peak:
                peak = abs(lp[t])
            signal[t] = lp[t] / peak
        mu = 1 / length
        coef = [0.0] * (length + 1)
        xx = [0.0] * (length + 1)
        sig_out = [float("nan")] * n
        pred_out = [float("nan")] * n
        for t in range(length, n):
            for j in range(length + 1):
                xx[j] = signal[t - length + j]
            xbar = 0.0
            for count in range(1, length + 1):
                xbar += xx[length - count] * coef[count]
            err = xx[length] - xbar
            for count in range(1, length + 1):
                coef[count] += mu * err * xx[length - count]
            xpred = 0.0
            for advance in range(1, bars_fwd + 1):
                xpred = 0.0
                for count in range(1, length + 1):
                    xpred += xx[length + 1 - count] * coef[count]
                for count in range(advance, length - advance + 1):
                    xx[count] = xx[count + 1]
                for count in range(1, length):
                    xx[count] = xx[count + 1]
                xx[length] = xpred
            sig_out[t] = signal[t]
            pred_out[t] = xpred
        return np.array(sig_out), np.array(pred_out)

    def test_independent_recompute(self):
        """独立复算锚点：两列全序列对拍（rtol=1e-10）。"""
        rng = np.random.default_rng(11)
        close = 100 + rng.standard_normal(120).cumsum()
        got = GPRED().compute(pd.DataFrame({"close": close}))
        sig_exp, pred_exp = self._recompute(close, 40, 18, 18, 2)
        np.testing.assert_allclose(got["gp_sig"].to_numpy(), sig_exp, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(got["gp_pred"].to_numpy(), pred_exp, rtol=1e-10, atol=1e-12)

    def test_sine_prediction_leads_price(self):
        """灵魂断言：纯正弦输入下 gp_pred[t] 与 close[t+bars_fwd] 相关系数 >0.9（预测真领先）。"""
        n, bars_fwd = 300, 2
        close = 100 + 5 * np.sin(np.arange(n) * 2 * np.pi / 24)
        got = GPRED().compute(pd.DataFrame({"close": close}))
        for col in ("gp_sig", "gp_pred"):  # 预热：前 length=18 根 NaN
            assert got[col].iloc[:18].isna().all()
            assert got[col].iloc[18:].notna().all()
        pred = got["gp_pred"].to_numpy()
        t = np.arange(18, n - bars_fwd)
        corr = float(np.corrcoef(pred[t], close[t + bars_fwd])[0, 1])
        assert corr > 0.9, f"正弦预测相关系数 {corr:.4f} <= 0.9"

    def test_constant_flat_and_signal_bounds(self):
        """常数序列 → gp_pred 恒定（容差 1e-6）；随机游走 → gp_sig 全序列 ∈ [-1,1]。"""
        flat = GPRED().compute(pd.DataFrame({"close": np.full(100, 100.0)}))["gp_pred"].to_numpy()
        valid = flat[18:]
        assert np.allclose(valid, valid[0], atol=1e-6)
        rng = np.random.default_rng(42)
        close = 100 + rng.standard_normal(200).cumsum()
        sig = GPRED().compute(pd.DataFrame({"close": close}))["gp_sig"].dropna()
        assert sig.abs().max() <= 1.0 + 1e-9

    def test_columns_fixed_and_empty_missing(self):
        """kwargs 覆盖 bars_fwd → 列名固定 gp_sig/gp_pred（docstring 契约），数值改变。"""
        rng = np.random.default_rng(7)
        close = 100 + rng.standard_normal(150).cumsum()
        df = pd.DataFrame({"close": close})
        alt = GPRED().compute(df, bars_fwd=3)
        assert list(alt.columns) == ["gp_sig", "gp_pred"]
        base = GPRED().compute(df)["gp_pred"].to_numpy()[20:]
        alt_v = alt["gp_pred"].to_numpy()[20:]
        assert not np.allclose(base[~np.isnan(base)], alt_v[~np.isnan(alt_v)])
        empty = GPRED().compute(pd.DataFrame(columns=["close"]))
        assert empty.empty
        assert list(empty.columns) == ["gp_sig", "gp_pred"]
        with pytest.raises(ValueError):
            GPRED().compute(pd.DataFrame({"close2": [1.0] * 80}))
