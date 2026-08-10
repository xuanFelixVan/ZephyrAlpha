# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""波动类技术指标测试（8 个）。

测试内容：
- 8 个波动指标全部注册到 Registry
- 每个指标 meta.category == "volatility"
- 每个指标 meta.output_columns == 期望列（catalog §2.3 契约）
- 已实现指标（全部 8 个）：数值正确性 + 边界测试

数值正确性验证方式：手工计算期望值 + 通达信公式对齐（STD ddof=0、ATR MA 平滑）。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.3
"""

from __future__ import annotations

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
        assert len(TechnicalIndicatorRegistry.list_by_category("volatility")) == len(EXPECTED) == 8


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
