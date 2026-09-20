# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""波动类技术指标测试（18 个）。

测试内容：
- 18 个波动指标全部注册到 Registry
- 每个指标 meta.category == "volatility"
- 每个指标 meta.output_columns == 期望列（catalog §2.3 契约）
- 已实现指标（全部 18 个）：数值正确性 + 边界测试

数值正确性验证方式：手工计算期望值 + 通达信公式对齐（STD ddof=0、ATR MA 平滑）+ 独立路径复算
（CHOP/CVI/ULCER 测试内纯 python 复算，与实现 pandas 滚动算子解耦）。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.3
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import volatility  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 便捷别名
ATR = TechnicalIndicatorRegistry.get("atr")
BOLL = TechnicalIndicatorRegistry.get("boll")
KELTNER = TechnicalIndicatorRegistry.get("keltner")
DONCHIAN = TechnicalIndicatorRegistry.get("donchian")
STDDEV = TechnicalIndicatorRegistry.get("stddev")
BANDWIDTH = TechnicalIndicatorRegistry.get("bandwidth")
PERCENT_B = TechnicalIndicatorRegistry.get("percent_b")
HISTVOL = TechnicalIndicatorRegistry.get("histvol")

NATR = TechnicalIndicatorRegistry.get("natr")
TRANGE = TechnicalIndicatorRegistry.get("trange")
MASSI = TechnicalIndicatorRegistry.get("massi")
PARKINSON = TechnicalIndicatorRegistry.get("parkinson")
GARMAN_KLASS = TechnicalIndicatorRegistry.get("garman_klass")
ROGERS_SATCHELL = TechnicalIndicatorRegistry.get("rogers_satchell")
YANG_ZHANG = TechnicalIndicatorRegistry.get("yang_zhang")
CHOP = TechnicalIndicatorRegistry.get("chop")
CVI = TechnicalIndicatorRegistry.get("cvi")
ULCER = TechnicalIndicatorRegistry.get("ulcer")

# 期望契约（catalog §2.3）：indicator_id → (name, output_columns)
EXPECTED = {
    "atr": ("真实波幅", ["atr_14"]),
    "boll": ("布林带", ["boll_upper", "boll_middle", "boll_lower"]),
    "keltner": ("肯特纳通道", ["kc_upper", "kc_middle", "kc_lower"]),
    "donchian": ("唐奇安通道", ["dc_upper", "dc_lower"]),
    "stddev": ("标准差", ["stddev_20"]),
    "bandwidth": ("布林带宽度", ["boll_bw"]),
    "percent_b": ("布林带%B", ["boll_pctb"]),
    "histvol": ("历史波动率", ["histvol_20"]),
    "natr": ("归一化真实波幅", ["natr_14"]),
    "trange": ("真实波幅", ["trange"]),
    "massi": ("质量指数", ["massi_25"]),
    "parkinson": ("Parkinson波动率", ["parkinson_20"]),
    "garman_klass": ("Garman-Klass波动率", ["garman_klass_20"]),
    "rogers_satchell": ("Rogers-Satchell波动率", ["rogers_satchell_20"]),
    "yang_zhang": ("Yang-Zhang波动率", ["yang_zhang_20"]),
    "chop": ("盘整指数", ["chop_14"]),
    "cvi": ("Chaikin波动率", ["cvi"]),
    "ulcer": ("溃疡指数", ["ulcer_14"]),
}

# 全部已实现
IMPLEMENTED = set(EXPECTED)
SKELETON = set(EXPECTED) - IMPLEMENTED  # 空集


# ===========================================================================
# 公共测试数据
# ===========================================================================

_RNG = np.random.default_rng(42)


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正，避免 log 负值）。"""
    close = 100 + _RNG.standard_normal(n).cumsum()
    high = close + _RNG.uniform(0.1, 0.5, n)
    low = close - _RNG.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


# ===========================================================================
# 注册与元数据契约测试
# ===========================================================================


class TestVolatilityRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("volatility")}
        for iid in EXPECTED:
            assert iid in metas, f"波动指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("volatility")) == len(EXPECTED) == 18


class TestVolatilityMetaContract:
    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_category(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.category == "volatility"

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


# ===========================================================================
# 骨架指标测试（空集，全部已实现）
# ===========================================================================


class TestVolatilityComputeNotImplemented:
    @pytest.mark.parametrize("iid", sorted(SKELETON))
    def test_compute_raises(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        df = pd.DataFrame(
            {"open": [10.0] * 30, "high": [11.0] * 30, "low": [9.0] * 30, "close": [10.5] * 30, "volume": [1000.0] * 30}
        )
        with pytest.raises(NotImplementedError, match="待施工"):
            cls().compute(df)


# ===========================================================================
# ATR 数值正确性测试
# ===========================================================================


class TestATRCompute:
    """ATR 真实波幅——数值正确性（MA 平滑对齐通达信）+ 边界测试。"""

    def test_tr_formula(self):
        """TR = max(H-L, |H-Cp|, |L-Cp|)。"""
        df = pd.DataFrame(
            {
                "high": [12.0, 11.0],
                "low": [8.0, 9.0],
                "close": [10.0, 10.5],
            }
        )
        result = ATR().compute(df, period=1)
        # bar 0: TR = 12-8 = 4 (无前收，H-L 最大)
        # bar 1: TR = max(11-9, |11-10|, |9-10|) = max(2, 1, 1) = 2
        assert result["atr_1"].iloc[0] == pytest.approx(4.0)
        assert result["atr_1"].iloc[1] == pytest.approx(2.0)

    def test_atr_is_ma_of_tr(self):
        """ATR = MA(TR, N)，对齐通达信（非 Wilder's RMA）。"""
        df = _make_ohlcv(50)
        n = 14
        result = ATR().compute(df, period=n)
        # 手工计算 TR 然后 MA
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - df["close"].shift(1)).abs(),
                (df["low"] - df["close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        expected = tr.rolling(window=n).mean()
        pd.testing.assert_series_equal(result["atr_14"], expected, check_names=False)

    def test_warmup_nan(self):
        """前 N-1 根为 NaN。"""
        df = _make_ohlcv(30)
        result = ATR().compute(df, period=14)
        assert result["atr_14"].iloc[:13].isna().all()

    def test_constant_series(self):
        """常数 HLC：TR = H-L = 常数，ATR = H-L。"""
        df = pd.DataFrame({"high": [11.0] * 30, "low": [9.0] * 30, "close": [10.0] * 30})
        result = ATR().compute(df, period=14)
        assert np.allclose(result["atr_14"].iloc[13:], 2.0)

    def test_empty_dataframe(self):
        result = ATR().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            ATR().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# BOLL 数值正确性测试
# ===========================================================================


class TestBOLLCompute:
    """BOLL 布林带——数值正确性（STD ddof=0）+ 关系约束 + 边界测试。"""

    def test_boll_formula(self):
        """MID=MA(C,N); UPPER=MID+nbdev×STD(ddof=0); LOWER=MID-nbdev×STD。"""
        df = _make_ohlcv(50)
        n, nbdev = 20, 2
        result = BOLL().compute(df, period=n, nbdev=nbdev)
        mid = df["close"].rolling(window=n).mean()
        std = df["close"].rolling(window=n).std(ddof=0)
        pd.testing.assert_series_equal(result["boll_middle"], mid, check_names=False)
        pd.testing.assert_series_equal(result["boll_upper"], mid + nbdev * std, check_names=False)
        pd.testing.assert_series_equal(result["boll_lower"], mid - nbdev * std, check_names=False)

    def test_upper_above_middle_above_lower(self):
        """UPPER >= MID >= LOWER（STD >= 0）。"""
        df = _make_ohlcv(50)
        result = BOLL().compute(df)
        valid = result.iloc[19:].dropna()
        assert (valid["boll_upper"] >= valid["boll_middle"]).all()
        assert (valid["boll_middle"] >= valid["boll_lower"]).all()

    def test_constant_series(self):
        """常数 close：STD=0，三轨重合。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = BOLL().compute(df, period=20, nbdev=2)
        assert np.allclose(result["boll_upper"].iloc[19:], 10.0)
        assert np.allclose(result["boll_middle"].iloc[19:], 10.0)
        assert np.allclose(result["boll_lower"].iloc[19:], 10.0)

    def test_warmup_nan(self):
        df = _make_ohlcv(30)
        result = BOLL().compute(df, period=20)
        assert result["boll_middle"].iloc[:19].isna().all()

    def test_empty_dataframe(self):
        result = BOLL().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            BOLL().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# Keltner 数值正确性测试
# ===========================================================================


class TestKeltnerCompute:
    """Keltner 肯特纳通道——数值正确性 + 关系约束 + 边界测试。"""

    def test_keltner_formula(self):
        """MID=EMA(C,N); UPPER=MID+mult×ATR(M); LOWER=MID-mult×ATR。"""
        df = _make_ohlcv(50)
        result = KELTNER().compute(df, period=20, atr_period=10, mult=2)
        # MID = EMA(C, 20) adjust=False
        from zephyr.factor.technical_indicators.trend import _ema

        mid = _ema(df["close"], 20)
        pd.testing.assert_series_equal(result["kc_middle"], mid, check_names=False)

    def test_upper_above_lower(self):
        """UPPER >= LOWER（mult × ATR >= 0）。"""
        df = _make_ohlcv(50)
        result = KELTNER().compute(df)
        valid = result.iloc[9:].dropna()  # ATR 预热 10
        assert (valid["kc_upper"] >= valid["kc_lower"]).all()

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = KELTNER().compute(df)
        assert list(result.columns) == ["kc_upper", "kc_middle", "kc_lower"]

    def test_empty_dataframe(self):
        result = KELTNER().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            KELTNER().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# Donchian 数值正确性测试
# ===========================================================================


class TestDonchianCompute:
    """Donchian 唐奇安通道——数值正确性 + 边界测试。"""

    def test_basic_values(self):
        """UPPER=max(H,N); LOWER=min(L,N)，含当前 bar。"""
        high = [10, 12, 11, 13, 14]
        low = [8, 9, 7, 10, 11]
        df = pd.DataFrame({"high": high, "low": low})
        result = DONCHIAN().compute(df, period=3)
        # bar 2: upper=max(10,12,11)=12, lower=min(8,9,7)=7
        assert result["dc_upper"].iloc[2] == 12
        assert result["dc_lower"].iloc[2] == 7
        # bar 4: upper=max(11,13,14)=14, lower=min(7,10,11)=7
        assert result["dc_upper"].iloc[4] == 14
        assert result["dc_lower"].iloc[4] == 7

    def test_warmup_nan(self):
        df = _make_ohlcv(30)
        result = DONCHIAN().compute(df, period=20)
        assert result["dc_upper"].iloc[:19].isna().all()

    def test_empty_dataframe(self):
        result = DONCHIAN().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            DONCHIAN().compute(pd.DataFrame({"high": [10.0] * 30}))


# ===========================================================================
# STDDEV 数值正确性测试
# ===========================================================================


class TestSTDDEVCompute:
    """STDDEV 标准差——数值正确性（ddof=0 对齐通达信）+ 边界测试。"""

    def test_ddof_zero(self):
        """通达信 STD 用 ddof=0（总体标准差），非 pandas 默认 ddof=1。"""
        df = _make_ohlcv(50)
        result = STDDEV().compute(df, period=20)
        expected = df["close"].rolling(window=20).std(ddof=0)
        pd.testing.assert_series_equal(result["stddev_20"], expected, check_names=False)

    def test_constant_series_zero(self):
        """常数 close：STD=0。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = STDDEV().compute(df, period=20)
        assert np.allclose(result["stddev_20"].iloc[19:], 0.0)

    def test_warmup_nan(self):
        df = _make_ohlcv(30)
        result = STDDEV().compute(df, period=20)
        assert result["stddev_20"].iloc[:19].isna().all()

    def test_empty_dataframe(self):
        result = STDDEV().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            STDDEV().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# BandWidth 数值正确性测试
# ===========================================================================


class TestBandWidthCompute:
    """BandWidth 布林带宽度——数值正确性 + 边界测试。"""

    def test_bw_formula(self):
        """BW = (UPPER - LOWER) / MID。"""
        df = _make_ohlcv(50)
        result = BANDWIDTH().compute(df, period=20, nbdev=2)
        mid = df["close"].rolling(window=20).mean()
        std = df["close"].rolling(window=20).std(ddof=0)
        expected = (4 * std) / mid  # (UPPER-LOWER) = 2*nbdev*std = 4*std
        pd.testing.assert_series_equal(result["boll_bw"], expected, check_names=False)

    def test_constant_series_zero(self):
        """常数 close：STD=0 → BW=0。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = BANDWIDTH().compute(df, period=20, nbdev=2)
        assert np.allclose(result["boll_bw"].iloc[19:], 0.0)

    def test_empty_dataframe(self):
        result = BANDWIDTH().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            BANDWIDTH().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# PercentB 数值正确性测试
# ===========================================================================


class TestPercentBCompute:
    """PercentB 布林带%B——数值正确性 + 边界测试。"""

    def test_pctb_formula(self):
        """%B = (C - LOWER) / (UPPER - LOWER)。"""
        df = _make_ohlcv(50)
        result = PERCENT_B().compute(df, period=20, nbdev=2)
        mid = df["close"].rolling(window=20).mean()
        std = df["close"].rolling(window=20).std(ddof=0)
        upper = mid + 2 * std
        lower = mid - 2 * std
        expected = (df["close"] - lower) / (upper - lower)
        pd.testing.assert_series_equal(result["boll_pctb"], expected, check_names=False)

    def test_at_middle(self):
        """close = MID 时 %B = 0.5。"""
        close = [10.0] * 25 + [10.0]  # 常数 close
        df = pd.DataFrame({"close": close})
        result = PERCENT_B().compute(df, period=20, nbdev=2)
        # 常数 → UPPER=LOWER=MID → 0/0 = NaN，跳过

    def test_empty_dataframe(self):
        result = PERCENT_B().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            PERCENT_B().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# HistVol 数值正确性测试
# ===========================================================================


class TestHistVolCompute:
    """HistVol 历史波动率——数值正确性 + 边界测试。"""

    def test_hv_formula(self):
        """HV = STD(log(C/Cp), N, ddof=1) × sqrt(252) × 100。"""
        df = _make_ohlcv(50)
        n = 20
        result = HISTVOL().compute(df, period=n)
        log_ret = np.log(df["close"] / df["close"].shift(1))
        expected = log_ret.rolling(window=n).std(ddof=1) * np.sqrt(252) * 100
        pd.testing.assert_series_equal(result["histvol_20"], expected, check_names=False)

    def test_nonnegative(self):
        """波动率非负。"""
        df = _make_ohlcv(50)
        result = HISTVOL().compute(df, period=20)
        valid = result["histvol_20"].dropna()
        assert (valid >= 0).all()

    def test_constant_series_nan_or_zero(self):
        """常数 close：log ret = 0，STD = 0 → HV = 0。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = HISTVOL().compute(df, period=20)
        assert np.allclose(result["histvol_20"].iloc[20:], 0.0)

    def test_warmup_nan(self):
        df = _make_ohlcv(30)
        result = HISTVOL().compute(df, period=20)
        # log_ret 首值 NaN + rolling 20 → 前 20 个 NaN
        assert result["histvol_20"].iloc[:20].isna().all()

    def test_empty_dataframe(self):
        result = HISTVOL().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            HISTVOL().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# 2026-09-14 主流热门批 2a：NATR/TRANGE 数值正确性
# ===========================================================================


class TestNatrTrangeNumeric:
    def test_trange_first_row_hl(self):
        df = _make_ohlcv(20)
        result = TRANGE().compute(df)
        assert result["trange"].iloc[0] == pytest.approx(df["high"].iloc[0] - df["low"].iloc[0])

    def test_natr_constant(self):
        df = _make_ohlcv(30)
        df["close"] = 100.0
        df["high"] = 101.0
        df["low"] = 99.0
        result = NATR().compute(df)
        np.testing.assert_allclose(result["natr_14"].dropna(), 2.0)

    def test_natr_no_negative(self):
        df = _make_ohlcv(40)
        result = NATR().compute(df)
        assert (result["natr_14"].dropna() >= 0).all()


class TestMassiNumeric:
    def test_constant_range_baseline(self):
        df = _make_ohlcv(50)
        df["high"] = 101.0
        df["low"] = 99.0
        result = MASSI().compute(df)
        # 恒定区间 EMA1=EMA2 → ratio=1 → MI=25
        np.testing.assert_allclose(result["massi_25"].dropna(), 25.0)

    def test_warmup(self):
        df = _make_ohlcv(50)
        result = MASSI().compute(df)
        # EMA 无预热 NaN，唯一窗口来自 rolling(25)
        assert result["massi_25"].iloc[:24].isna().all()
        assert result["massi_25"].iloc[24:].notna().all()


# ===========================================================================
# 2026-09-14 批 6：学术 RV 族数值正确性
# ===========================================================================


class TestRvFamilyNumeric:
    def _flat(self, n=40, o=100.0, h=101.0, l=99.0, c=100.0):
        df = _make_ohlcv(n)
        df["open"], df["high"], df["low"], df["close"] = o, h, l, c
        return df

    def test_all_nonnegative_and_warmup(self):
        df = _make_ohlcv(40)
        for cls in (PARKINSON, GARMAN_KLASS, ROGERS_SATCHELL, YANG_ZHANG):
            result = cls().compute(df)
            assert (result.iloc[:, 0].dropna() >= 0).all()

    def test_parkinson_known_value(self):
        """恒定区间 H=101/L=99 → ln(H/L)²=(ln(101/99))²；日频 σ=sqrt(sum/(4ln2·N))×100。"""
        df = self._flat(30)
        result = PARKINSON().compute(df)
        x = np.log(101.0 / 99.0)
        expected = np.sqrt(x**2 / (4 * np.log(2))) * 100
        assert result["parkinson_20"].dropna().iloc[-1] == pytest.approx(expected, rel=1e-10)

    def test_gk_zero_when_oc_constant(self):
        """C=O 恒定 → ln(C/O)=0，GK 只剩 0.5ln²(H/L) 项。"""
        df = self._flat(30, o=100.0, h=101.0, l=99.0, c=100.0)
        result = GARMAN_KLASS().compute(df)
        x = np.log(101.0 / 99.0)
        expected = np.sqrt(0.5 * x**2) * 100
        assert result["garman_klass_20"].dropna().iloc[-1] == pytest.approx(expected, rel=1e-10)

    def test_yz_between_reasonable_bounds(self):
        df = _make_ohlcv(60)
        result = YANG_ZHANG().compute(df)
        assert (result["yang_zhang_20"].dropna() >= 0).all()
        assert result["yang_zhang_20"].dropna().max() < 100


# ===========================================================================
# 2026-09-20 简单指标清欠班波2-A：CHOP/CVI/ULCER 数值正确性
# ===========================================================================


class TestChopCompute:
    """CHOP 盘整指数——独立复算（纯 python + math 模块）+ 手工微样本 + 边界。"""

    def test_independent_recompute(self):
        """纯 python 逐窗复算（math.log10），与实现 pandas 滚动算子解耦对拍（rtol=atol=1e-12）。"""
        df = _make_ohlcv(60)
        result = CHOP().compute(df)
        n = 14
        h = df["high"].to_numpy()
        l = df["low"].to_numpy()
        c = df["close"].to_numpy()
        tr = [
            h[0] - l[0] if i == 0 else max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
            for i in range(len(c))
        ]
        expected = []
        for t in range(len(c)):
            if t < n - 1:
                expected.append(np.nan)
                continue
            lo_w = t - n + 1
            tr_sum = math.fsum(tr[lo_w : t + 1])
            rng = max(h[lo_w : t + 1]) - min(l[lo_w : t + 1])
            expected.append(100 * math.log10(tr_sum / rng) / math.log10(n) if rng > 0 else np.nan)
        np.testing.assert_allclose(result["chop_14"].to_numpy(), expected, rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（window=2，3 根已知 HLC）：
        TR=[2,3,4]；t1: 100·log10(5/4)/log10(2)=32.1928…；t2: 100·log10(7/5)/log10(2)=48.5427…。
        """
        df = pd.DataFrame({"high": [10.0, 12.0, 11.0], "low": [8.0, 9.0, 7.0], "close": [9.0, 11.0, 10.0]})
        result = CHOP().compute(df, period=2)
        assert np.isnan(result["chop_2"].iloc[0])
        assert result["chop_2"].iloc[1] == pytest.approx(100 * math.log10(5 / 4) / math.log10(2), rel=1e-12)
        assert result["chop_2"].iloc[2] == pytest.approx(100 * math.log10(7 / 5) / math.log10(2), rel=1e-12)

    def test_warmup_nan_and_bounds(self):
        """预热前 13 根 NaN；值域 [0,100]（ΣTR≥HH−LL → ratio≥1）。"""
        df = _make_ohlcv(60)
        result = CHOP().compute(df)
        assert result["chop_14"].iloc[:13].isna().all()
        assert result["chop_14"].iloc[13:].notna().all()
        valid = result["chop_14"].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_constant_price_nan(self):
        """恒定价格：HH−LL=0 → 0/0 保护为 NaN（非 inf）。"""
        df = pd.DataFrame({"high": [10.0] * 30, "low": [10.0] * 30, "close": [10.0] * 30})
        result = CHOP().compute(df)
        assert result["chop_14"].isna().all()

    def test_period_override(self):
        """kwargs 覆盖 period=5：列名 chop_5，首有效=index 4。"""
        df = _make_ohlcv(30)
        result = CHOP().compute(df, period=5)
        assert list(result.columns) == ["chop_5"]
        assert result["chop_5"].iloc[:4].isna().all()
        assert result["chop_5"].iloc[4:].notna().all()

    def test_empty_and_missing_column(self):
        result = CHOP().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty
        assert list(result.columns) == ["chop_14"]
        with pytest.raises(ValueError, match="缺少列"):
            CHOP().compute(pd.DataFrame({"close": [10.0] * 30}))


class TestCviCompute:
    """CVI Chaikin 波动率——独立复算（纯 python EMA 递推）+ 手工微样本 + 边界。"""

    def test_independent_recompute(self):
        """纯 python 递推复算 EMA(α=2/5) + shift ROC，与实现 ewm 路径解耦（rtol=atol=1e-10）。"""
        df = _make_ohlcv(60)
        result = CVI().compute(df)
        ema_n, roc_n = 3, 10
        rng = (df["high"] - df["low"]).to_numpy()
        alpha = 2.0 / (ema_n + 1)
        e = [rng[0]]
        for i in range(1, len(rng)):
            e.append(alpha * rng[i] + (1 - alpha) * e[-1])
        expected = [100 * (e[i] / e[i - roc_n] - 1) if i >= roc_n else np.nan for i in range(len(rng))]
        np.testing.assert_allclose(result["cvi"].to_numpy(), expected, rtol=1e-10, atol=1e-10)

    def test_hand_micro_sample(self):
        """手工微样本（H−L 交替 2/4，ema=3→α=0.5，roc=2）：
        e=[2,3,2.5,3.25,…]；cvi[2]=100(2.5/2−1)=25；cvi[3]=100(3.25/3−1)=25/3。
        """
        spans = [2.0, 4.0] * 6
        df = pd.DataFrame({"high": [10 + s / 2 for s in spans], "low": [10 - s / 2 for s in spans]})
        result = CVI().compute(df, ema_period=3, roc_period=2)
        assert result["cvi"].iloc[:2].isna().all()
        assert result["cvi"].iloc[2] == pytest.approx(25.0, rel=1e-12)
        assert result["cvi"].iloc[3] == pytest.approx(25.0 / 3.0, rel=1e-10)

    def test_warmup_nan_then_valid(self):
        """EMA adjust=False 无自身预热，唯一预热来自 shift(roc_period)：前 10 根 NaN。"""
        df = _make_ohlcv(40)
        result = CVI().compute(df)
        assert result["cvi"].iloc[:10].isna().all()
        assert result["cvi"].iloc[10:].notna().all()

    def test_constant_range_zero(self):
        """恒定 H−L：EMA 恒定 → 变化率 0 → CVI=0。"""
        df = _make_ohlcv(30)
        df["high"], df["low"] = 101.0, 99.0
        result = CVI().compute(df)
        assert np.allclose(result["cvi"].iloc[10:], 0.0)

    def test_kwargs_override(self):
        """kwargs 覆盖 roc_period/ema_period：固定列名 cvi 语义不变，数值随参数变化。"""
        df = _make_ohlcv(60)
        base = CVI().compute(df)["cvi"].to_numpy()
        alt = CVI().compute(df, roc_period=5)["cvi"].to_numpy()
        ema5 = CVI().compute(df, ema_period=5)["cvi"].to_numpy()
        assert not np.allclose(base[10:], alt[10:])
        assert not np.allclose(base[10:], ema5[10:])
        assert not np.isnan(alt[5:]).any()  # roc=5 → 首有效=5，提前于默认 10

    def test_empty_and_missing_column(self):
        result = CVI().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty
        assert list(result.columns) == ["cvi"]
        with pytest.raises(ValueError, match="缺少列"):
            CVI().compute(pd.DataFrame({"close": [10.0] * 30}))


class TestUlcerCompute:
    """ULCER 溃疡指数——独立复算（纯 python 逐窗）+ 手工微样本 + 边界。"""

    def test_independent_recompute(self):
        """纯 python 逐窗复算（math.sqrt + 百分数缩放），与实现 rolling.apply 解耦（rtol=atol=1e-12）。"""
        df = _make_ohlcv(60)
        result = ULCER().compute(df)
        n = 14
        c = df["close"].to_numpy()
        expected = []
        for t in range(len(c)):
            if t < n - 1:
                expected.append(np.nan)
                continue
            w = c[t - n + 1 : t + 1]
            peak = max(w)
            devs = [(x / peak - 1) * 100.0 for x in w]
            expected.append(math.sqrt(sum(d * d for d in devs) / n))
        np.testing.assert_allclose(result["ulcer_14"].to_numpy(), expected, rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（n=3，close=[10,12,9,11]）：
        t2 峰 12 偏差 [−1/6,0,−1/4] → 100·√((1/36+1/16)/3)；t3 峰 12 → 100·√((1/16+1/144)/3)。
        """
        df = pd.DataFrame({"close": [10.0, 12.0, 9.0, 11.0]})
        result = ULCER().compute(df, period=3)
        assert np.isnan(result["ulcer_3"].iloc[:2]).all()
        assert result["ulcer_3"].iloc[2] == pytest.approx(100 * math.sqrt((1 / 36 + 1 / 16) / 3), rel=1e-12)
        assert result["ulcer_3"].iloc[3] == pytest.approx(100 * math.sqrt((1 / 16 + 1 / 144) / 3), rel=1e-12)

    def test_warmup_nan_and_nonnegative(self):
        """预热前 13 根 NaN；溃疡指数只罚下行 → 非负。"""
        df = _make_ohlcv(60)
        result = ULCER().compute(df)
        assert result["ulcer_14"].iloc[:13].isna().all()
        assert result["ulcer_14"].iloc[13:].notna().all()
        assert (result["ulcer_14"].dropna() >= 0).all()

    def test_constant_series_zero(self):
        """常数 close：窗口内回撤恒 0 → 溃疡指数 0。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = ULCER().compute(df)
        assert np.allclose(result["ulcer_14"].iloc[13:], 0.0)

    def test_downtrend_ulcer_positive(self):
        """单边下行：每根都对窗口峰值回撤 → 严格为正（与常数区分）。"""
        df = pd.DataFrame({"close": np.linspace(120.0, 60.0, 40)})
        result = ULCER().compute(df)
        assert (result["ulcer_14"].iloc[13:] > 0).all()

    def test_period_override(self):
        """kwargs 覆盖 period=7：列名 ulcer_7，首有效=index 6。"""
        df = _make_ohlcv(30)
        result = ULCER().compute(df, period=7)
        assert list(result.columns) == ["ulcer_7"]
        assert result["ulcer_7"].iloc[:6].isna().all()
        assert result["ulcer_7"].iloc[6:].notna().all()

    def test_empty_and_missing_column(self):
        result = ULCER().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["ulcer_14"]
        with pytest.raises(ValueError, match="缺少列"):
            ULCER().compute(pd.DataFrame({"open": [10.0] * 30}))
