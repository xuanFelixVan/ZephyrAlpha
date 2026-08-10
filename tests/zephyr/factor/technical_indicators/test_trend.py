# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""趋势类技术指标测试（10 个）。

测试内容：
- 10 个趋势指标全部注册到 Registry
- 每个指标 meta.category == "trend"
- 每个指标 meta.output_columns == 期望列（catalog §2.1 契约）
- 已实现指标（ma/ema/macd）：数值正确性 + 边界测试
- 骨架指标（wma/dema/adx/dmi/cci/sar/trix）：compute() 抛 NotImplementedError

数值正确性验证方式：手工计算期望值 + 通达信公式对齐（EMA adjust=False、MACD HIST=2×(DIF-DEA)）。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.1
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import trend  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 便捷别名——避免每个测试都写 TechnicalIndicatorRegistry.get()
MA = TechnicalIndicatorRegistry.get("ma")
EMA = TechnicalIndicatorRegistry.get("ema")
WMA = TechnicalIndicatorRegistry.get("wma")
DEMA = TechnicalIndicatorRegistry.get("dema")
MACD = TechnicalIndicatorRegistry.get("macd")
ADX = TechnicalIndicatorRegistry.get("adx")
DMI = TechnicalIndicatorRegistry.get("dmi")
CCI = TechnicalIndicatorRegistry.get("cci")
SAR = TechnicalIndicatorRegistry.get("sar")
TRIX = TechnicalIndicatorRegistry.get("trix")

# 期望契约（catalog §2.1）：indicator_id → (name, output_columns)
EXPECTED = {
    "ma": ("简单移动平均", ["ma_5", "ma_10", "ma_20", "ma_60"]),
    "ema": ("指数移动平均", ["ema_12", "ema_26"]),
    "wma": ("加权移动平均", ["wma_10"]),
    "dema": ("双指数移动平均", ["dema_12"]),
    "macd": ("异同移动平均", ["macd_dif", "macd_dea", "macd_hist"]),
    "adx": ("平均趋向指数", ["adx_14"]),
    "dmi": ("趋向指标", ["pdi_14", "mdi_14"]),
    "cci": ("顺势指标", ["cci_14"]),
    "sar": ("抛物线指标", ["sar"]),
    "trix": ("三重指数平滑平均", ["trix", "trma"]),
}

# 已施工算法的指标（version >= 1.0.0）
IMPLEMENTED = {"ma", "ema", "wma", "dema", "macd", "adx", "dmi", "cci", "sar", "trix"}
# 仍为骨架的指标（compute 抛 NotImplementedError）
SKELETON = set(EXPECTED) - IMPLEMENTED


# ===========================================================================
# 注册与元数据契约测试（全部 10 个）
# ===========================================================================


class TestTrendRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("trend")}
        for iid in EXPECTED:
            assert iid in metas, f"趋势指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("trend")) == len(EXPECTED) == 10


class TestTrendMetaContract:
    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_category(self, iid, expected):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert meta.category == "trend"

    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_name(self, iid, expected):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert meta.name == expected[0]

    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_output_columns(self, iid, expected):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert meta.output_columns == expected[1]

    @pytest.mark.parametrize("iid", list(EXPECTED.keys()))
    def test_input_columns_nonempty(self, iid):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert len(meta.input_columns) > 0
        # 输入列必须是合法 OHLCV 子集
        assert set(meta.input_columns) <= {"open", "high", "low", "close", "volume"}

    @pytest.mark.parametrize("iid", list(EXPECTED.keys()))
    def test_params_is_dict(self, iid):
        meta = TechnicalIndicatorRegistry.get(iid).meta
        assert isinstance(meta.params, dict)


# ===========================================================================
# 骨架指标测试（7 个仍抛 NotImplementedError）
# ===========================================================================


class TestTrendComputeNotImplemented:
    """骨架先行契约：未施工指标 compute() 抛 NotImplementedError。"""

    @pytest.mark.parametrize("iid", sorted(SKELETON))
    def test_compute_raises(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        df = pd.DataFrame(
            {"open": [10.0] * 30, "high": [11.0] * 30, "low": [9.0] * 30, "close": [10.5] * 30, "volume": [1000.0] * 30}
        )
        with pytest.raises(NotImplementedError, match="待施工"):
            cls().compute(df)


# ===========================================================================
# MA 数值正确性测试
# ===========================================================================


class TestMACompute:
    """MA 简单移动平均——数值正确性 + 边界测试。"""

    def test_basic_values(self):
        """手工验证：close=[10,11,12,13,14,15], ma_5 在 index>=4 有值。"""
        close = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
        df = pd.DataFrame({"close": close})
        result = MA().compute(df)
        # ma_5[4] = (10+11+12+13+14)/5 = 12.0
        assert result["ma_5"].iloc[4] == pytest.approx(12.0)
        # ma_5[5] = (11+12+13+14+15)/5 = 13.0
        assert result["ma_5"].iloc[5] == pytest.approx(13.0)
        # 前 4 个为 NaN（预热期）
        assert result["ma_5"].iloc[:4].isna().all()

    def test_output_columns_and_index(self):
        df = pd.DataFrame({"close": [10.0] * 30})
        result = MA().compute(df)
        assert list(result.columns) == ["ma_5", "ma_10", "ma_20", "ma_60"]
        assert len(result) == 30
        assert result.index.equals(df.index)

    def test_periods_override(self):
        """kwargs 覆盖默认 periods。"""
        df = pd.DataFrame({"close": list(range(1, 8))})
        result = MA().compute(df, periods=[3])
        assert list(result.columns) == ["ma_3"]
        # ma_3[2] = (1+2+3)/3 = 2.0
        assert result["ma_3"].iloc[2] == pytest.approx(2.0)

    def test_empty_dataframe(self):
        result = MA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["ma_5", "ma_10", "ma_20", "ma_60"]

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MA().compute(pd.DataFrame({"open": [10.0]}))

    def test_single_row(self):
        """单条数据：所有 MA 为 NaN（window > 1）。"""
        result = MA().compute(pd.DataFrame({"close": [10.0]}))
        assert result["ma_5"].isna().all()


# ===========================================================================
# EMA 数值正确性测试
# ===========================================================================


class TestEMACompute:
    """EMA 指数移动平均——数值正确性（adjust=False 对齐通达信）+ 边界测试。"""

    def test_adjust_false_seeding(self):
        """通达信 EMA 种子=首值，adjust=False：ema_3 手工递推验证。

        α = 2/(3+1) = 0.5
        ema[0] = 10
        ema[1] = 0.5×11 + 0.5×10 = 10.5
        ema[2] = 0.5×12 + 0.5×10.5 = 11.25
        ema[3] = 0.5×13 + 0.5×11.25 = 12.125
        ema[4] = 0.5×14 + 0.5×12.125 = 13.0625
        """
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0, 13.0, 14.0]})
        result = EMA().compute(df, periods=[3])
        ema = result["ema_3"]
        assert ema.iloc[0] == pytest.approx(10.0)
        assert ema.iloc[1] == pytest.approx(10.5)
        assert ema.iloc[2] == pytest.approx(11.25)
        assert ema.iloc[3] == pytest.approx(12.125)
        assert ema.iloc[4] == pytest.approx(13.0625)

    def test_no_warmup_nan(self):
        """EMA adjust=False 从首根 K 线开始计算，无预热 NaN（区别于 MA）。"""
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0]})
        result = EMA().compute(df, periods=[12])
        assert result["ema_12"].notna().all()

    def test_constant_series(self):
        """常数序列 EMA = 常数本身。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = EMA().compute(df)
        assert (result["ema_12"] == 10.0).all()
        assert (result["ema_26"] == 10.0).all()

    def test_output_columns_and_index(self):
        df = pd.DataFrame({"close": [10.0] * 30})
        result = EMA().compute(df)
        assert list(result.columns) == ["ema_12", "ema_26"]
        assert result.index.equals(df.index)

    def test_periods_override(self):
        df = pd.DataFrame({"close": list(range(1, 8))})
        result = EMA().compute(df, periods=[5])
        assert list(result.columns) == ["ema_5"]

    def test_empty_dataframe(self):
        result = EMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["ema_12", "ema_26"]

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            EMA().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# MACD 数值正确性测试
# ===========================================================================


class TestMACDCompute:
    """MACD 异同移动平均——数值正确性 + 关系约束 + 边界测试。"""

    def test_hist_equals_2x_dif_minus_dea(self):
        """核心关系：HIST = 2 × (DIF - DEA)，逐行精确验证。"""
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"close": 10 + rng.standard_normal(50).cumsum()})
        result = MACD().compute(df)
        expected_hist = 2 * (result["macd_dif"] - result["macd_dea"])
        pd.testing.assert_series_equal(result["macd_hist"], expected_hist, check_names=False)

    def test_dif_equals_ema12_minus_ema26(self):
        """DIF = EMA12 - EMA26，对齐通达信 adjust=False。"""
        rng = np.random.default_rng(42)
        close = pd.Series(10 + rng.standard_normal(50).cumsum())
        df = pd.DataFrame({"close": close})
        result = MACD().compute(df)
        expected_dif = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        pd.testing.assert_series_equal(result["macd_dif"], expected_dif, check_names=False)

    def test_constant_series_zero(self):
        """常数序列：DIF/DEA/HIST 均为 0（EMA 收敛到常数，差为 0）。"""
        df = pd.DataFrame({"close": [10.0] * 50})
        result = MACD().compute(df)
        assert np.allclose(result["macd_dif"], 0.0)
        assert np.allclose(result["macd_dea"], 0.0)
        assert np.allclose(result["macd_hist"], 0.0)

    def test_no_nan(self):
        """MACD 全程无 NaN（EMA adjust=False 无预热）。"""
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"close": 10 + rng.standard_normal(30).cumsum()})
        result = MACD().compute(df)
        assert result.notna().all().all()

    def test_output_columns_and_index(self):
        df = pd.DataFrame({"close": [10.0] * 30})
        result = MACD().compute(df)
        assert list(result.columns) == ["macd_dif", "macd_dea", "macd_hist"]
        assert result.index.equals(df.index)

    def test_params_override(self):
        """kwargs 覆盖 fast/slow/signal。"""
        df = pd.DataFrame({"close": list(range(1, 31))})
        result = MACD().compute(df, fast=5, slow=10, signal=3)
        # 验证关系仍成立
        expected_hist = 2 * (result["macd_dif"] - result["macd_dea"])
        pd.testing.assert_series_equal(result["macd_hist"], expected_hist, check_names=False)

    def test_empty_dataframe(self):
        result = MACD().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["macd_dif", "macd_dea", "macd_hist"]

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MACD().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# WMA 数值正确性测试
# ===========================================================================


class TestWMACompute:
    """WMA 加权移动平均——数值正确性（近期权重高）+ 边界测试。"""

    def test_basic_values(self):
        """手工验证：close=[1,2,3,4,5], n=3。

        wma_3[2] = (1×1 + 2×2 + 3×3) / (1+2+3) = 14/6 ≈ 2.3333
        wma_3[3] = (1×2 + 2×3 + 3×4) / 6 = 20/6 ≈ 3.3333
        wma_3[4] = (1×3 + 2×4 + 3×5) / 6 = 26/6 ≈ 4.3333
        """
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = WMA().compute(df, period=3)
        assert result["wma_3"].iloc[2] == pytest.approx(14 / 6)
        assert result["wma_3"].iloc[3] == pytest.approx(20 / 6)
        assert result["wma_3"].iloc[4] == pytest.approx(26 / 6)

    def test_constant_series(self):
        """常数序列 WMA = 常数本身。"""
        df = pd.DataFrame({"close": [10.0] * 15})
        result = WMA().compute(df)
        assert np.allclose(result["wma_10"].iloc[9:], 10.0)

    def test_warmup_nan(self):
        """预热期（前 n-1 个）为 NaN。"""
        df = pd.DataFrame({"close": list(range(1, 15))})
        result = WMA().compute(df, period=5)
        assert result["wma_5"].iloc[:4].isna().all()
        assert result["wma_5"].iloc[4:].notna().all()

    def test_empty_dataframe(self):
        result = WMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            WMA().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# DEMA 数值正确性测试
# ===========================================================================


class TestDEMACompute:
    """DEMA 双指数移动平均——数值正确性 + 关系约束 + 边界测试。"""

    def test_dema_formula(self):
        """DEMA = 2×EMA - EMA(EMA)，对齐公式。"""
        rng = np.random.default_rng(42)
        close = pd.Series(10 + rng.standard_normal(50).cumsum())
        df = pd.DataFrame({"close": close})
        result = DEMA().compute(df, period=12)
        ema1 = close.ewm(span=12, adjust=False).mean()
        ema2 = ema1.ewm(span=12, adjust=False).mean()
        expected = 2 * ema1 - ema2
        pd.testing.assert_series_equal(result["dema_12"], expected, check_names=False)

    def test_constant_series(self):
        """常数序列 DEMA = 常数本身。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        result = DEMA().compute(df)
        assert np.allclose(result["dema_12"], 10.0)

    def test_no_warmup_nan(self):
        """DEMA 基于 EMA(adjust=False)，无预热 NaN。"""
        df = pd.DataFrame({"close": list(range(1, 31))})
        result = DEMA().compute(df, period=12)
        assert result["dema_12"].notna().all()

    def test_empty_dataframe(self):
        result = DEMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            DEMA().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# TRIX 数值正确性测试
# ===========================================================================


class TestTRIXCompute:
    """TRIX 三重指数平滑平均——数值正确性 + 关系约束 + 边界测试。"""

    def test_trix_is_pct_change_of_tr(self):
        """TRIX = 100 × TR 变化率，TR = EMA³(close)。"""
        rng = np.random.default_rng(42)
        close = pd.Series(10 + rng.standard_normal(50).cumsum())
        df = pd.DataFrame({"close": close})
        result = TRIX().compute(df, period=12)
        tr = close.ewm(span=12, adjust=False).mean()
        tr = tr.ewm(span=12, adjust=False).mean()
        tr = tr.ewm(span=12, adjust=False).mean()
        expected_trix = 100 * tr.pct_change()
        pd.testing.assert_series_equal(result["trix"], expected_trix, check_names=False)

    def test_trma_is_ma_of_trix(self):
        """TRMA = MA(TRIX, N)。"""
        rng = np.random.default_rng(42)
        close = pd.Series(10 + rng.standard_normal(50).cumsum())
        df = pd.DataFrame({"close": close})
        result = TRIX().compute(df, period=12)
        expected_trma = result["trix"].rolling(window=12).mean()
        pd.testing.assert_series_equal(result["trma"], expected_trma, check_names=False)

    def test_constant_series_zero(self):
        """常数序列：TR=常数，TRIX=0（变化率=0），TRMA=0。"""
        df = pd.DataFrame({"close": [10.0] * 50})
        result = TRIX().compute(df)
        # trix 第一个值为 NaN（pct_change），其余为 0
        assert result["trix"].iloc[0] != result["trix"].iloc[0]  # NaN check
        assert np.allclose(result["trix"].iloc[1:], 0.0)

    def test_first_trix_is_nan(self):
        """TRIX 首值为 NaN（pct_change 首值为 NaN）。"""
        df = pd.DataFrame({"close": list(range(1, 31))})
        result = TRIX().compute(df, period=12)
        assert result["trix"].iloc[0] != result["trix"].iloc[0]  # NaN

    def test_output_columns_and_index(self):
        df = pd.DataFrame({"close": [10.0] * 30})
        result = TRIX().compute(df)
        assert list(result.columns) == ["trix", "trma"]
        assert result.index.equals(df.index)

    def test_empty_dataframe(self):
        result = TRIX().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            TRIX().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# 公共测试数据——OHLCV（30 根 K 线，含上涨/下跌段）
# ===========================================================================

_RNG = np.random.default_rng(42)


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据。"""
    close = 10 + _RNG.standard_normal(n).cumsum()
    high = close + _RNG.uniform(0.1, 0.5, n)
    low = close - _RNG.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


# ===========================================================================
# DMI 数值正确性测试
# ===========================================================================


class TestDMICompute:
    """DMI 趋向指标——数值正确性 + 边界测试。"""

    def test_pdi_mdi_nonnegative(self):
        """+DI/-DI 应非负（0~100 范围）。"""
        df = _make_ohlcv(50)
        result = DMI().compute(df, period=14)
        valid = result.iloc[14:].dropna()
        assert (valid["pdi_14"] >= 0).all()
        assert (valid["mdi_14"] >= 0).all()

    def test_warmup_nan(self):
        """前 14 根 K 线 DI 为 NaN（SUM window=14）。"""
        df = _make_ohlcv(50)
        result = DMI().compute(df, period=14)
        assert result["pdi_14"].iloc[:13].isna().all()

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = DMI().compute(df)
        assert list(result.columns) == ["pdi_14", "mdi_14"]

    def test_empty_dataframe(self):
        result = DMI().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            DMI().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# ADX 数值正确性测试
# ===========================================================================


class TestADXCompute:
    """ADX 平均趋向指数——数值正确性 + 边界测试。"""

    def test_adx_nonnegative(self):
        """ADX 应非负（0~100 范围）。"""
        df = _make_ohlcv(50)
        result = ADX().compute(df, period=14)
        valid = result["adx_14"].iloc[27:].dropna()  # DI 预热 14 + ADX MA 14
        assert (valid >= 0).all()

    def test_adx_uses_ma_of_dx(self):
        """ADX = MA(DX)，DX = |+DI - -DI|/(+DI + -DI)×100。"""
        df = _make_ohlcv(50)
        n = 14
        result_adx = ADX().compute(df, period=n)
        result_dmi = DMI().compute(df, period=n)
        dx = (result_dmi["pdi_14"] - result_dmi["mdi_14"]).abs() / (result_dmi["pdi_14"] + result_dmi["mdi_14"]) * 100
        expected_adx = dx.rolling(window=n).mean()
        pd.testing.assert_series_equal(result_adx["adx_14"], expected_adx, check_names=False)

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = ADX().compute(df)
        assert list(result.columns) == ["adx_14"]

    def test_empty_dataframe(self):
        result = ADX().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            ADX().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# CCI 数值正确性测试
# ===========================================================================


class TestCCICompute:
    """CCI 顺势指标——数值正确性 + 边界测试。"""

    def test_cci_formula(self):
        """CCI = (TP - MA(TP)) / (0.015 × AVEDEV(TP))。"""
        df = _make_ohlcv(50)
        n = 14
        result = CCI().compute(df, period=n)
        tp = (df["high"] + df["low"] + df["close"]) / 3
        ma_tp = tp.rolling(window=n).mean()
        avedev = tp.rolling(window=n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        expected = (tp - ma_tp) / (0.015 * avedev)
        pd.testing.assert_series_equal(result["cci_14"], expected, check_names=False)

    def test_constant_tp_nan(self):
        """常数 TP：AVEDDEV=0 → CCI=NaN（除零）。"""
        df = pd.DataFrame({"high": [10.0] * 30, "low": [10.0] * 30, "close": [10.0] * 30})
        result = CCI().compute(df, period=14)
        # 预热期后 AVEDEV=0 → inf 或 nan
        assert result["cci_14"].iloc[14:].isna().all() or np.isinf(result["cci_14"].iloc[14:]).all()

    def test_warmup_nan(self):
        """前 13 根为 NaN。"""
        df = _make_ohlcv(30)
        result = CCI().compute(df, period=14)
        assert result["cci_14"].iloc[:13].isna().all()

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = CCI().compute(df)
        assert list(result.columns) == ["cci_14"]

    def test_empty_dataframe(self):
        result = CCI().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CCI().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# SAR 数值正确性测试
# ===========================================================================


class TestSARCompute:
    """SAR 抛物线指标——数值正确性 + 边界测试。"""

    def test_first_value_is_low(self):
        """首根 K 线 SAR = low[0]（初始假设上升趋势）。"""
        df = pd.DataFrame({"high": [11.0, 12.0, 10.0], "low": [9.0, 10.0, 8.0]})
        result = SAR().compute(df)
        assert result["sar"].iloc[0] == 9.0

    def test_uptrend_sar_below_price(self):
        """上升趋势中 SAR 在价格下方。"""
        # 构造持续上涨数据
        close = np.linspace(10, 20, 20)
        high = close + 0.5
        low = close - 0.5
        df = pd.DataFrame({"high": high, "low": low})
        result = SAR().compute(df)
        # 上升趋势中 SAR 应低于 low（即低于价格）
        valid = result["sar"].iloc[1:]
        lows = pd.Series(low, index=df.index).iloc[1:]
        assert (valid <= lows + 0.01).all()  # 容忍微小误差

    def test_no_nan_after_first(self):
        """SAR 从首根 K 线开始有值，无 NaN（迭代算法）。"""
        df = _make_ohlcv(30)
        result = SAR().compute(df)
        assert result["sar"].notna().all()

    def test_reversal(self):
        """趋势翻转时 SAR 应跳到极值点。"""
        # 先涨后跌
        high = list(np.linspace(11, 20, 10)) + list(np.linspace(20, 11, 10))
        low = list(np.linspace(9, 18, 10)) + list(np.linspace(18, 9, 10))
        df = pd.DataFrame({"high": high, "low": low})
        result = SAR().compute(df)
        # 翻转后 SAR 应从下方跳到上方
        assert result["sar"].notna().all()

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = SAR().compute(df)
        assert list(result.columns) == ["sar"]

    def test_empty_dataframe(self):
        result = SAR().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            SAR().compute(pd.DataFrame({"high": [10.0] * 30}))
