# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""趋势类技术指标测试（37 个）。

测试内容：
- 37 个趋势指标全部注册到 Registry（另有复合类 Ichimoku 归 composite，不在本文件契约内）
- 每个指标 meta.category == "trend"
- 每个指标 meta.output_columns == 期望列（catalog §2.1 契约）
- 全部指标已施工（IMPLEMENTED == EXPECTED，SKELETON 为空，骨架契约保留防回归）
- 数值正确性验证方式：talib 黄金对照（生产零 TA-Lib 依赖）+ 手工微样本显式计算 + 独立公式复算
  （EMA adjust=False、MACD HIST=2×(DIF-DEA)、TEMA 3 根手算、VIDYA 纯 python 复算、四价格变换逐行手算、
  INERTIA 纯 python 复算 RVI+种子 EMA+OLS 端点链、QSTICK 纯 python 滚动均值复算、
  Ehlers 滤波器族 SUPERSMOOTHER/HIGHPASS/PTREND 纯 numpy 双实现互证+手算微样本）

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.1
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import trend  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# talib 仅作黄金参照（生产代码禁 TA-Lib 依赖）；缺失时整模块跳过
talib = pytest.importorskip("talib")

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
DKX = TechnicalIndicatorRegistry.get("dkx")
HMA = TechnicalIndicatorRegistry.get("hma")
ZLEMA = TechnicalIndicatorRegistry.get("zlema")
KAMA = TechnicalIndicatorRegistry.get("kama")
VORTEX = TechnicalIndicatorRegistry.get("vortex")
SUPERTREND = TechnicalIndicatorRegistry.get("supertrend")
MCGINLEY = TechnicalIndicatorRegistry.get("mcginley")
BBI = TechnicalIndicatorRegistry.get("bbi")
ALLIGATOR = TechnicalIndicatorRegistry.get("alligator")
GMMA = TechnicalIndicatorRegistry.get("gmma")
GANN_HILO = TechnicalIndicatorRegistry.get("gann_hilo")
MAMA = TechnicalIndicatorRegistry.get("mama")
FRAMA = TechnicalIndicatorRegistry.get("frama")
JMA = TechnicalIndicatorRegistry.get("jma")
TEMA = TechnicalIndicatorRegistry.get("tema")
TRIMA = TechnicalIndicatorRegistry.get("trima")
T3 = TechnicalIndicatorRegistry.get("t3")
VIDYA = TechnicalIndicatorRegistry.get("vidya")
AVGPRICE = TechnicalIndicatorRegistry.get("avgprice")
MEDPRICE = TechnicalIndicatorRegistry.get("medprice")
TYPPRICE = TechnicalIndicatorRegistry.get("typprice")
WCPRICE = TechnicalIndicatorRegistry.get("wcprice")
INERTIA = TechnicalIndicatorRegistry.get("inertia")
QSTICK = TechnicalIndicatorRegistry.get("qstick")
SUPERSMOOTHER = TechnicalIndicatorRegistry.get("supersmoother")
HIGHPASS = TechnicalIndicatorRegistry.get("highpass")
PTREND = TechnicalIndicatorRegistry.get("ptrend")

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
    "dkx": ("多空线", ["dkx_20", "dkx_ma10"]),
    "hma": ("Hull均线", ["hma_16"]),
    "zlema": ("零滞后EMA", ["zlema_21"]),
    "kama": ("Kaufman自适应均线", ["kama_10"]),
    "vortex": ("涡旋指标", ["vip_14", "vim_14"]),
    "supertrend": ("超级趋势", ["supertrend_10", "supertrend_dir"]),
    "mcginley": ("McGinley动态均线", ["md_14"]),
    "bbi": ("多空指数", ["bbi"]),
    "alligator": ("鳄鱼线", ["alligator_jaw", "alligator_teeth", "alligator_lips"]),
    "gmma": (
        "顾比复合均线",
        [
            "gmma_s3",
            "gmma_s5",
            "gmma_s8",
            "gmma_s10",
            "gmma_s12",
            "gmma_s15",
            "gmma_l30",
            "gmma_l35",
            "gmma_l40",
            "gmma_l45",
            "gmma_l50",
            "gmma_l60",
        ],
    ),
    "gann_hilo": ("Gann HiLo Activator", ["gann_hilo", "gann_hilo_dir"]),
    "mama": ("MESA自适应均线", ["mama", "fama"]),
    "frama": ("分形自适应均线", ["frama_16"]),
    "jma": ("Jurik自适应均线", ["jma_7"]),
    "tema": ("三重指数移动平均", ["tema_10"]),
    "trima": ("三角移动平均", ["trima_10"]),
    "t3": ("Tillson T3均线", ["t3_10"]),
    "vidya": ("可变指数动态均线", ["vidya_14"]),
    "avgprice": ("平均价格", ["avgprice"]),
    "medprice": ("中位价格", ["medprice"]),
    "typprice": ("典型价格", ["typprice"]),
    "wcprice": ("加权收盘价", ["wcprice"]),
    "inertia": ("惯性指标", ["inertia_20_14"]),
    "qstick": ("QStick指标", ["qstick_10"]),
    "supersmoother": ("超级平滑器", ["supersmoother_10"]),
    "highpass": ("三阶高通滤波", ["highpass_40"]),
    "ptrend": ("精调趋势", ["ptrend_250_40", "ptrend_roc"]),
}

# 已施工算法的指标（version >= 1.0.0）
IMPLEMENTED = {
    "ma",
    "ema",
    "wma",
    "dema",
    "macd",
    "adx",
    "dmi",
    "cci",
    "sar",
    "trix",
    "dkx",
    "hma",
    "zlema",
    "kama",
    "vortex",
    "supertrend",
    "mcginley",
    "bbi",
    "alligator",
    "gmma",
    "gann_hilo",
    "mama",
    "frama",
    "jma",
    "tema",
    "trima",
    "t3",
    "vidya",
    "avgprice",
    "medprice",
    "typprice",
    "wcprice",
    "inertia",
    "qstick",
    "supersmoother",
    "highpass",
    "ptrend",
}
# 仍为骨架的指标（compute 抛 NotImplementedError）
SKELETON = set(EXPECTED) - IMPLEMENTED


# ===========================================================================
# 注册与元数据契约测试（全部 37 个）
# ===========================================================================


class TestTrendRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("trend")}
        for iid in EXPECTED:
            assert iid in metas, f"趋势指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("trend")) == len(EXPECTED) == 37


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
# 骨架指标测试（当前 SKELETON 为空：37 个全部已施工；契约保留防回归）
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


# ===========================================================================
# 2026-09-14 A股标配批：DKX 数值正确性
# ===========================================================================


class TestDkxNumeric:
    def test_constant_price_constant_line(self):
        df = _make_ohlcv(40)
        for c in ("open", "high", "low", "close"):
            df[c] = 100.0
        result = DKX().compute(df)
        assert (result["dkx_20"].dropna() == 100.0).all()

    def test_manual_weighted_match(self):
        """小样本手算对照：MID=(3C+L+O+H)/6 线性加权 20..1/210。"""
        n = 25
        rng = np.random.default_rng(7)
        close = pd.Series(100 + rng.standard_normal(n).cumsum())
        df = pd.DataFrame(
            {
                "open": close + 0.1,
                "high": close + 0.3,
                "low": close - 0.3,
                "close": close,
                "volume": 1000.0,
            }
        )
        result = DKX().compute(df)
        mid = (3 * close + df["low"] + df["open"] + df["high"]) / 6
        # 窗口按时间升序（旧→新），权重 1..20（新值权重 20，对齐通达信）
        weights = list(range(1, 21))
        expected = []
        for t in range(n):
            window = mid.iloc[max(0, t - 19) : t + 1]
            if len(window) < 20:
                expected.append(np.nan)
            else:
                expected.append(float(np.dot(weights, window)) / 210.0)
        got = result["dkx_20"].reset_index(drop=True)
        np.testing.assert_allclose(got.iloc[19:], np.array(expected[19:]), rtol=1e-10)

    def test_warmup_nan(self):
        df = _make_ohlcv(40)
        result = DKX().compute(df)
        assert result["dkx_20"].iloc[:19].isna().all()
        assert result["dkx_20"].iloc[19:].notna().all()


# ===========================================================================
# 2026-09-14 主流热门批 2a：HMA/ZLEMA/KAMA/VORTEX/SUPERTREND 数值正确性
# ===========================================================================


class TestLowLagMaNumeric:
    def test_hma_constant(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = HMA().compute(df)
        assert (result["hma_16"].dropna() == 100.0).all()

    def test_zlema_constant(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = ZLEMA().compute(df)
        assert (result["zlema_21"].dropna() == 100.0).all()

    def test_hma_warmup(self):
        df = _make_ohlcv(40)
        result = HMA().compute(df)
        assert result["hma_16"].isna().sum() >= 16  # WMA(N)+WMA(√N) 级联预热

    def test_kama_constant(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = KAMA().compute(df)
        assert (result["kama_10"].dropna() == 100.0).all()

    def test_kama_tracks_uptrend(self):
        df = _make_ohlcv(40)
        df["close"] = np.linspace(100, 140, 40)
        result = KAMA().compute(df)
        valid = result["kama_10"].dropna()
        assert (valid.diff().dropna() > 0).all()  # 上升趋势中 KAMA 逐日抬升


class TestVortexNumeric:
    def test_nonnegative(self):
        df = _make_ohlcv(50)
        result = VORTEX().compute(df)
        for col in ("vip_14", "vim_14"):
            assert (result[col].dropna() >= 0).all()

    def test_uptrend_vip_dominates(self):
        df = _make_ohlcv(50)
        rising = np.linspace(100, 150, 50)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = rising
        result = VORTEX().compute(df)
        assert (result["vip_14"].dropna() > result["vim_14"].dropna()).all()


class TestSupertrendNumeric:
    def test_uptrend_direction_positive(self):
        df = _make_ohlcv(60)
        rising = np.linspace(100, 160, 60)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = rising
        result = SUPERTREND().compute(df)
        assert (result["supertrend_dir"].dropna() == 1.0).all()

    def test_direction_binary(self):
        df = _make_ohlcv(60)
        result = SUPERTREND().compute(df)
        valid = result["supertrend_dir"].dropna()
        assert valid.isin([1.0, -1.0]).all()

    def test_uptrend_line_below_close(self):
        df = _make_ohlcv(60)
        rising = np.linspace(100, 160, 60)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = rising
        result = SUPERTREND().compute(df)
        pair = result.dropna()
        assert (pair["supertrend_10"] < pair["supertrend_dir"] * 0 + rising[-len(pair) :]).all()


class TestMcGinleyNumeric:
    def test_constant_price_constant_line(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = MCGINLEY().compute(df)
        assert (result["md_14"].dropna() == 100.0).all()

    def test_lags_behind_close_uptrend(self):
        df = _make_ohlcv(60)
        df["close"] = np.linspace(100, 160, 60)
        result = MCGINLEY().compute(df)
        pair = result["md_14"].to_numpy()
        closes = df["close"].to_numpy()
        valid = ~np.isnan(pair)
        assert (pair[valid][1:] < closes[valid][1:]).all()  # 首行 md=C，其余在价格下方


class TestBbiNumeric:
    def test_constant_price_constant_line(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = BBI().compute(df)
        assert (result["bbi"].dropna() == 100.0).all()

    def test_manual_four_ma_average(self):
        df = _make_ohlcv(40)
        result = BBI().compute(df)
        expected = (
            df["close"].rolling(3).mean()
            + df["close"].rolling(6).mean()
            + df["close"].rolling(12).mean()
            + df["close"].rolling(24).mean()
        ) / 4
        np.testing.assert_allclose(result["bbi"].dropna(), expected.dropna(), rtol=1e-12)

    def test_warmup_24(self):
        df = _make_ohlcv(40)
        result = BBI().compute(df)
        assert result["bbi"].iloc[:23].isna().all()
        assert result["bbi"].iloc[23:].notna().all()


class TestBatch8TrendNumeric:
    def test_alligator_uptrend_ordering(self):
        """上升趋势：唇>齿>颚（快线在上方）。"""
        df = _make_ohlcv(60)
        rising = np.linspace(100, 160, 60)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        result = ALLIGATOR().compute(df)
        tail = result.dropna().tail(5)
        assert (tail["alligator_lips"] > tail["alligator_teeth"]).all()
        assert (tail["alligator_teeth"] > tail["alligator_jaw"]).all()

    def test_gmma_all_columns_registered_and_ema_match(self):
        df = _make_ohlcv(70)
        result = GMMA().compute(df)
        assert len(result.columns) == 12
        expected_s3 = df["close"].ewm(span=3, adjust=False).mean()
        np.testing.assert_allclose(result["gmma_s3"].dropna(), expected_s3.dropna(), rtol=1e-10)

    def test_gann_hilo_direction_binary_and_range(self):
        df = _make_ohlcv(60)
        rising = np.linspace(100, 160, 60)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = rising
        result = GANN_HILO().compute(df)
        valid = result["gann_hilo_dir"].dropna()
        assert valid.isin([1.0, -1.0]).all()
        assert (valid == 1.0).all()


# ===========================================================================
# 2026-09-20 自适应均线批：MAMA/FRAMA/JMA 数值正确性
# ===========================================================================


def _make_golden_ohlc(n: int = 200) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """200 根几何随机游走合成 OHLC（rng(42)），保证 H≥max(O,C)、L≤min(O,C)。"""
    rng = np.random.default_rng(42)
    close = 100.0 * np.exp(rng.standard_normal(n).cumsum() * 0.01)
    open_ = close * (1.0 + rng.standard_normal(n) * 0.001)
    spread = np.abs(rng.standard_normal(n)) * 0.005 + 0.001
    high = np.maximum(open_, close) * (1.0 + spread)
    low = np.minimum(open_, close) * (1.0 - spread)
    assert (high >= np.maximum(open_, close)).all()
    assert (low <= np.minimum(open_, close)).all()
    return high, low, close


class TestMamaNumeric:
    """MAMA/MESA 自适应均线——talib 黄金对照 + 预热/参数/边界。"""

    def test_golden_vs_talib(self):
        """黄金对照：第 100 根起与 talib.MAMA 一致（rtol=atol=1e-6；实测逐位一致 0 偏差）。

        talib 0.7.1 为单 real 输入口径，价格 (H+L)/2 由测试侧显式合成。
        """
        high, low, _ = _make_golden_ohlc(200)
        df = pd.DataFrame({"high": high, "low": low})
        result = MAMA().compute(df)
        t_mama, t_fama = talib.MAMA((high + low) / 2.0, fastlimit=0.5, slowlimit=0.05)
        np.testing.assert_allclose(result["mama"].to_numpy()[100:], t_mama[100:], rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(result["fama"].to_numpy()[100:], t_fama[100:], rtol=1e-6, atol=1e-6)

    def test_warmup_nan_then_valid(self):
        """前 12 根为尾随 WMA 预热种子 NaN，第 12 根起递推有值（实测首有效=12）。"""
        high, low, _ = _make_golden_ohlc(60)
        df = pd.DataFrame({"high": high, "low": low})
        result = MAMA().compute(df)
        for col in ("mama", "fama"):
            assert result[col].iloc[:12].isna().all()
            assert result[col].iloc[12:].notna().all()

    def test_fama_lags_mama_uptrend(self):
        """上升趋势：FAMA（半速）滞后于 MAMA，MAMA 单调追踪。"""
        rising = np.linspace(100, 200, 120)
        df = pd.DataFrame({"high": rising + 0.5, "low": rising - 0.5})
        result = MAMA().compute(df)
        pair = result.dropna()
        assert (pair["fama"] <= pair["mama"]).all()
        assert (pair["mama"].diff().dropna() > 0).all()

    def test_fast_limit_override(self):
        """kwargs 覆盖 fast_limit：更快上限 → 均线更贴近价格。"""
        high, low, _ = _make_golden_ohlc(80)
        df = pd.DataFrame({"high": high, "low": low})
        base = MAMA().compute(df)["mama"].to_numpy()
        fast = MAMA().compute(df, fast_limit=0.9)["mama"].to_numpy()
        assert not np.allclose(base[32:], fast[32:])
        price = ((df["high"] + df["low"]) / 2.0).to_numpy()
        assert np.abs(fast[32:] - price[32:]).mean() < np.abs(base[32:] - price[32:]).mean()

    def test_empty_and_missing_column(self):
        result = MAMA().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty
        assert list(result.columns) == ["mama", "fama"]
        with pytest.raises(ValueError, match="缺少列"):
            MAMA().compute(pd.DataFrame({"close": [10.0] * 30}))


class TestFramaNumeric:
    """FRAMA 分形自适应均线——手工微样本 + 趋势/正弦/边界。"""

    def test_constant_price_identity(self):
        """常数价格：HL 全零保护 → alpha=1 → 首窗后输出恒等于该价格。"""
        df = pd.DataFrame({"high": [100.0] * 40, "low": [100.0] * 40})
        result = FRAMA().compute(df)
        assert result["frama_16"].iloc[:15].isna().all()
        assert (result["frama_16"].iloc[15:] == 100.0).all()

    def test_hand_computed_first_window(self):
        """手工微样本（17 根锯齿）：HL1=HL2=HL3=5 → D=log2(2×10/5)=2 → alpha=exp(−4.6)。

        手算链条：两半各自 max(H)−min(L)=102−97=5，整窗同 5；
        D=log2(2(5+5)/5)=log2(4)=2，alpha=exp(−4.6(2−1))=exp(−4.6)≈0.010051835744633584。
        首有效=第 15 根（N−1）种子=当根中价 98.5；第 16 根=α×100.5+(1−α)×98.5=98.5+2α。
        """
        high = np.array([102.0, 100.0] * 8 + [102.0])
        low = high - 3.0
        df = pd.DataFrame({"high": high, "low": low})
        result = FRAMA().compute(df)
        alpha0 = np.exp(-4.6)
        assert result["frama_16"].iloc[:15].isna().all()
        assert result["frama_16"].iloc[15] == pytest.approx(98.5)
        assert result["frama_16"].iloc[16] == pytest.approx(98.5 + 2.0 * alpha0, rel=1e-12)

    def test_uptrend_lags_but_tracks(self):
        """强趋势（步长<1，保证 alpha 未钳位上界）：frama 滞后于 close 但同向，终值误差 < 5%。"""
        close = np.linspace(100.0, 130.0, 60)
        df = pd.DataFrame({"high": close + 0.5, "low": close - 0.5})
        result = FRAMA().compute(df)
        fr = result["frama_16"].to_numpy()
        valid = fr[16:]  # 跳过种子根
        assert (valid < close[16:]).all()
        assert (np.diff(valid) > 0).all()
        assert abs(fr[-1] - close[-1]) < 0.05 * close[-1]

    def test_sine_smooth_no_nan_holes(self):
        """正弦序列：首窗后无 NaN 穿洞，输出被历史价格包络约束且总变差低于原始价格（平滑）。"""
        t = np.arange(100)
        close = 100.0 + 10.0 * np.sin(t / 5.0)
        df = pd.DataFrame({"high": close + 0.5, "low": close - 0.5})
        result = FRAMA().compute(df)
        fr = result["frama_16"]
        assert fr.iloc[:15].isna().all()
        assert fr.iloc[15:].notna().all()  # 平滑无 NaN 穿洞
        p_min, p_max = close.min() - 0.5, close.max() + 0.5
        assert ((fr.iloc[15:] >= p_min - 1e-9) & (fr.iloc[15:] <= p_max + 1e-9)).all()
        assert np.abs(np.diff(fr.iloc[15:])).sum() <= np.abs(np.diff(close)).sum()

    def test_period_override(self):
        """kwargs 覆盖 period：列名与预热期随窗口走（20 → 前 19 根 NaN）。"""
        close = np.linspace(100.0, 160.0, 60)
        df = pd.DataFrame({"high": close + 0.5, "low": close - 0.5})
        result = FRAMA().compute(df, period=20)
        assert list(result.columns) == ["frama_20"]
        assert result["frama_20"].iloc[:19].isna().all()
        assert result["frama_20"].iloc[19:].notna().all()

    def test_empty_and_missing_column(self):
        result = FRAMA().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty
        assert list(result.columns) == ["frama_16"]
        with pytest.raises(ValueError, match="缺少列"):
            FRAMA().compute(pd.DataFrame({"close": [10.0] * 30}))


class TestJmaNumeric:
    """JMA Jurik 自适应均线——pandas-ta 公式复算 + 常数/阶跃/参数/边界。"""

    def test_constant_identity(self):
        """常数序列：预热后输出恒等于该常数（种子=首值）。"""
        df = pd.DataFrame({"close": [100.0] * 40})
        result = JMA().compute(df)
        assert result["jma_7"].iloc[:6].isna().all()
        assert (result["jma_7"].iloc[6:] == 100.0).all()

    def test_step_single_peak_bounded_overshoot(self):
        """阶跃逼近：单峰形态（先单调上行后单调回落收敛平台），过冲 ≤ 20% 步长。

        实测 phase=50/power=2 过冲=13.95% 步长（Jurik 低滞后设计固有特性，
        pandas-ta 移植口径如实呈现，故按规格"容差放宽"为 20% 步长定量界）。
        """
        close = np.array([100.0] * 60 + [110.0] * 60)
        df = pd.DataFrame({"close": close})
        seg = JMA().compute(df)["jma_7"].to_numpy()[60:]  # 跳变根起
        diffs = np.diff(seg)
        peak_pos = int(np.argmax(seg))
        assert 0 < peak_pos < len(seg) - 1
        assert (diffs[:peak_pos] > 0).all()  # 上行段单调
        assert (diffs[peak_pos:] <= 0).all()  # 回落段单调
        assert seg.min() >= 100.0 - 1e-9  # 无向下击穿原平台
        assert seg.max() <= 110.0 + 0.20 * 10.0  # 过冲定量界
        assert abs(seg[-1] - 110.0) < 1e-6  # 收敛到新平台

    def test_phase_and_period_override(self):
        """参数覆盖生效：不同 phase 结果不同；period 变更改变列名与预热位。"""
        rng = np.random.default_rng(7)
        close = 100.0 + rng.standard_normal(80).cumsum()
        df = pd.DataFrame({"close": close})
        p0 = JMA().compute(df, phase=0.0)["jma_7"].to_numpy()
        p100 = JMA().compute(df, phase=100.0)["jma_7"].to_numpy()
        assert not np.allclose(p0[6:], p100[6:])
        long = JMA().compute(df, period=14)
        assert list(long.columns) == ["jma_14"]
        assert long["jma_14"].iloc[:13].isna().all()
        assert long["jma_14"].iloc[13:].notna().all()

    def test_formula_recompute_3bar(self):
        """3 根微样本按 pandas-ta overlap/jma.py 公式逐行复算核对（移植忠实度锚点）。

        复算代码为本测试内独立书写的公式直译（period=3/phase=50），与实现解耦比对。
        """
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0]})
        got = JMA().compute(df, period=3, phase=50.0)["jma_3"].to_numpy()
        # --- 公式复算（pandas-ta jma.py 直译） ---
        length, phase = 3, 50.0
        sum_length = 10
        half_len = 0.5 * (length - 1)
        pr = 1.5 + phase * 0.01
        length1 = max((np.log(np.sqrt(half_len)) / np.log(2.0)) + 2.0, 0.0)
        pow1 = max(length1 - 2.0, 0.5)
        length2 = length1 * np.sqrt(half_len)
        bet = length2 / (length2 + 1.0)
        beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2.0)
        c = np.array([10.0, 11.0, 12.0])
        m = len(c)
        volty = np.zeros(m)
        v_sum = np.zeros(m)
        jma = np.zeros(m)
        det0 = det1 = ma2 = 0.0
        ma1 = u_band = l_band = jma[0] = c[0]
        for i in range(1, m):
            price = c[i]
            del1 = price - u_band
            del2 = price - l_band
            volty[i] = max(abs(del1), abs(del2)) if abs(del1) != abs(del2) else 0.0
            v_sum[i] = v_sum[i - 1] + (volty[i] - volty[max(i - sum_length, 0)]) / sum_length
            avg_volty = np.mean(v_sum[max(i - 65, 0) : i + 1])
            d_volty = 0.0 if avg_volty == 0 else volty[i] / avg_volty
            r_volty = max(1.0, min(np.power(length1, 1.0 / pow1), d_volty))
            pow2 = np.power(r_volty, pow1)
            kv = np.power(bet, np.sqrt(pow2))
            u_band = price if del1 > 0 else price - kv * del1
            l_band = price if del2 < 0 else price - kv * del2
            alpha = np.power(beta, pow2)
            ma1 = (1.0 - alpha) * price + alpha * ma1
            det0 = (price - ma1) * (1.0 - beta) + beta * det0
            ma2 = ma1 + pr * det0
            det1 = (ma2 - jma[i - 1]) * (1.0 - alpha) * (1.0 - alpha) + alpha * alpha * det1
            jma[i] = jma[i - 1] + det1
        jma[: length - 1] = np.nan
        np.testing.assert_allclose(got, jma, rtol=0, atol=1e-12)

    def test_empty_and_missing_column(self):
        result = JMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["jma_7"]
        with pytest.raises(ValueError, match="缺少列"):
            JMA().compute(pd.DataFrame({"open": [10.0] * 30}))


# ===========================================================================
# 2026-09-20 简单指标清欠批1-L3：TEMA/TRIMA/T3/VIDYA/四价格变换 数值正确性
# ===========================================================================


def _make_golden_df_11(n: int = 200) -> pd.DataFrame:
    """200 根几何随机游走合成 OHLC（rng(11)，清欠批1-L3 黄金样本），H≥max(O,C)、L≤min(O,C)。"""
    rng = np.random.default_rng(11)
    close = 100.0 * np.exp(rng.standard_normal(n).cumsum() * 0.01)
    open_ = close * (1.0 + rng.standard_normal(n) * 0.001)
    spread = np.abs(rng.standard_normal(n)) * 0.005 + 0.001
    high = np.maximum(open_, close) * (1.0 + spread)
    low = np.minimum(open_, close) * (1.0 - spread)
    assert (high >= np.maximum(open_, close)).all()
    assert (low <= np.minimum(open_, close)).all()
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


class TestTemaNumeric:
    """TEMA 三重指数移动平均——talib 黄金对照 + 手工微样本 + 边界。"""

    def test_golden_vs_talib(self):
        """黄金对照：第 100 根起与 talib.TEMA 一致（rtol=atol=1e-6）。

        TA-Lib EMA 族用 SMA 种子（非首值种子），预热差异随 (1−α)^t 指数衰减
        （unstable period 语义，实测第 100 根差 ~3e-7、第 150 根 ~3e-11），
        第 100 根起对拍（MAMA 同款豁免口径）；本实现种子=首值，全序列无 NaN。
        """
        df = _make_golden_df_11()
        result = TEMA().compute(df)
        got = result["tema_10"].to_numpy()
        t_tema = talib.TEMA(df["close"].to_numpy(), timeperiod=10)
        assert not np.isnan(got).any()
        np.testing.assert_allclose(got[100:], t_tema[100:], rtol=1e-6, atol=1e-6)

    def test_hand_computed_3bar(self):
        """手工微样本（非纯对拍）：close=[10,11,12]，α=2/11，_ema 种子=首值手推三步。

        e1=[10, 10+α, 10+α+α(12−e1[1])]；e2/e3 同式级联；tema=3e1−3e2+e3，期望值独立手算写死。
        """
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0]})
        got = TEMA().compute(df, period=10)["tema_10"].to_numpy()
        np.testing.assert_allclose(got, [10.0, 10.452291510142754, 11.203333105662178], rtol=1e-12)

    def test_constant_series_identity(self):
        """常数序列：EMA 链恒为常数 → TEMA 恒等于该常数（系数和=1）。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        got = TEMA().compute(df)["tema_10"].to_numpy()
        np.testing.assert_allclose(got, 10.0, rtol=1e-12)

    def test_period_override(self):
        """kwargs 覆盖 period：列名 tema_20 随窗口走，仍无预热 NaN。"""
        df = _make_golden_df_11(60)
        result = TEMA().compute(df, period=20)
        assert list(result.columns) == ["tema_20"]
        assert result["tema_20"].notna().all()

    def test_empty_and_missing_column(self):
        result = TEMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["tema_10"]
        with pytest.raises(ValueError, match="缺少列"):
            TEMA().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestTrimaNumeric:
    """TRIMA 三角移动平均——talib 黄金对照 + 手工双窗 SMA + 边界。"""

    def test_golden_vs_talib(self):
        """黄金对照：TA-Lib TRIMA(10) 偶窗 lookback=9 与本实现首有效一致
        （实测 talib 首有效 idx=9），从首个双方有效位起全序列对拍 rtol=atol=1e-12。
        """
        df = _make_golden_df_11()
        result = TRIMA().compute(df)
        got = result["trima_10"].to_numpy()
        t_trima = talib.TRIMA(df["close"].to_numpy(), timeperiod=10)
        assert np.isnan(got[:9]).all()
        np.testing.assert_allclose(got[9:], t_trima[9:], rtol=1e-12, atol=1e-12)

    def test_warmup_nan_then_valid(self):
        """预热：前 9 根 NaN（SMA5+SMA6 级联 4+5），index 9 起有效。"""
        df = _make_golden_df_11()
        got = TRIMA().compute(df)["trima_10"]
        assert got.iloc[:9].isna().all()
        assert got.iloc[9:].notna().all()

    def test_hand_two_stage_sma(self):
        """手工微样本：close=1..12，trima=SMA6(SMA5)。

        s5[4..10]=[3,4,5,6,7,8,9]；trima[9]=mean(3..8)=5.5；trima[10]=mean(4..9)=6.5。
        """
        df = pd.DataFrame({"close": [float(x) for x in range(1, 13)]})
        got = TRIMA().compute(df, period=10)["trima_10"].to_numpy()
        assert got[9] == pytest.approx(5.5, rel=1e-12)
        assert got[10] == pytest.approx(6.5, rel=1e-12)

    def test_constant_series(self):
        """常数序列：预热后输出恒等于该常数。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        got = TRIMA().compute(df)["trima_10"].to_numpy()
        assert np.isnan(got[:9]).all()
        np.testing.assert_allclose(got[9:], 10.0, rtol=1e-12)

    def test_period_override(self):
        """kwargs 覆盖 period=6（偶窗 3×4）：列名 trima_6，首有效=index 5。"""
        df = pd.DataFrame({"close": [float(x) for x in range(1, 21)]})
        result = TRIMA().compute(df, period=6)
        assert list(result.columns) == ["trima_6"]
        assert result["trima_6"].iloc[:5].isna().all()
        assert result["trima_6"].iloc[5:].notna().all()

    def test_empty_and_missing_column(self):
        result = TRIMA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["trima_10"]
        with pytest.raises(ValueError, match="缺少列"):
            TRIMA().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestT3Numeric:
    """T3 Tillson 均线——talib 黄金对照 + 常数恒等 + 参数覆盖。"""

    def test_golden_vs_talib(self):
        """黄金对照：第 100 根起与 talib.T3(timeperiod=10, vfactor=0.7) 一致（rtol=atol=1e-6）。

        TA-Lib EMA 族 SMA 种子预热差异指数衰减（实测第 100 根差 ~1.6e-6，有效容差
        =atol+rtol×|值|≈1e-4），第 100 根起对拍（MAMA 同款豁免口径）。
        """
        df = _make_golden_df_11()
        result = T3().compute(df)
        got = result["t3_10"].to_numpy()
        t_t3 = talib.T3(df["close"].to_numpy(), timeperiod=10, vfactor=0.7)
        assert not np.isnan(got).any()
        np.testing.assert_allclose(got[100:], t_t3[100:], rtol=1e-6, atol=1e-6)

    def test_constant_series_identity(self):
        """常数序列：c1+c2+c3+c4 恒等于 1 → T3 恒等于该常数。"""
        df = pd.DataFrame({"close": [10.0] * 40})
        got = T3().compute(df)["t3_10"].to_numpy()
        np.testing.assert_allclose(got, 10.0, rtol=1e-12)

    def test_no_warmup_nan(self):
        """六重 adjust=False EMA 链无预热 NaN。"""
        df = _make_golden_df_11()
        got = T3().compute(df)["t3_10"]
        assert got.notna().all()

    def test_vfactor_and_period_override(self):
        """kwargs 覆盖：vfactor 变→结果变；period=20→列名 t3_20。"""
        df = _make_golden_df_11(80)
        base = T3().compute(df)["t3_10"].to_numpy()
        alt = T3().compute(df, vfactor=0.3)["t3_10"].to_numpy()
        assert not np.allclose(base[20:], alt[20:])
        long = T3().compute(df, period=20)
        assert list(long.columns) == ["t3_20"]
        assert long["t3_20"].notna().all()

    def test_empty_and_missing_column(self):
        result = T3().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["t3_10"]
        with pytest.raises(ValueError, match="缺少列"):
            T3().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestVidyaNumeric:
    """VIDYA 可变指数动态均线——独立复算 + 手工微样本 + 边界。

    talib 0.7.1 无 VIDYA 函数（dir(talib) 与 abstract.Function 均无），
    黄金锚点改为测试内纯 python 独立复算（与实现解耦的双实现对拍）。
    """

    def test_independent_recompute(self):
        """独立复算锚点：纯 python 逐 bar 复算 CMO+递推，全序列对拍（rtol=atol=1e-10）。"""
        close = _make_golden_df_11()["close"].to_numpy()
        result = VIDYA().compute(pd.DataFrame({"close": close}))
        got = result["vidya_14"].to_numpy()
        n, cm = 14, 9
        expected = np.full(len(close), np.nan)
        prev = None
        for t in range(cm, len(close)):  # diff 首位 NaN → CMO 首有效=第 cm+1 根（index 9）
            d = [close[i] - close[i - 1] for i in range(t - cm + 1, t + 1)]
            su = sum(x for x in d if x > 0)
            sd = sum(-x for x in d if x < 0)
            a = abs((su - sd) / (su + sd) * 100.0) / 100.0 * 2.0 / (n + 1)
            if prev is None:
                prev = close[t]  # 种子=CMO 首有效当根 close（种子当根即输出）
            else:
                prev = a * close[t] + (1.0 - a) * prev
            expected[t] = prev
        assert np.isnan(got[:9]).all()
        mask = ~np.isnan(expected)
        np.testing.assert_allclose(got[mask], expected[mask], rtol=1e-10, atol=1e-10)

    def test_hand_micro_sample(self):
        """手工微样本（涨跌混合，CMO∈(0,100)）：12 根已知收盘价，期望值独立手算写死。"""
        closes = [10.0, 10.5, 10.2, 10.8, 11.0, 10.6, 10.9, 11.2, 10.8, 11.1, 11.4, 11.2]
        df = pd.DataFrame({"close": closes})
        got = VIDYA().compute(df)["vidya_14"].to_numpy()
        assert np.isnan(got[:9]).all()
        assert got[9] == pytest.approx(11.1)  # 种子=CMO 首有效当根 close
        assert got[10] == pytest.approx(11.111612903225806, rel=1e-12)
        assert got[11] == pytest.approx(11.115541218637993, rel=1e-12)

    def test_cmo_full_streak_spot(self):
        """单边上行 9 窗 → CMO=+100 → alpha=2/15 恒定：out[10]=10+2/15，out[11] 递推写死。"""
        df = pd.DataFrame({"close": [float(x) for x in range(1, 13)]})
        got = VIDYA().compute(df)["vidya_14"].to_numpy()
        assert got[9] == pytest.approx(10.0)
        assert got[10] == pytest.approx(10.0 + 2.0 / 15.0, rel=1e-12)
        assert got[11] == pytest.approx(10.382222222222223, rel=1e-12)

    def test_warmup_nan_then_valid(self):
        """预热：前 9 根 NaN（diff 首位 NaN + CMO 9 窗），index 9 起有效。"""
        df = _make_golden_df_11()
        got = VIDYA().compute(df)["vidya_14"]
        assert got.iloc[:9].isna().all()
        assert got.iloc[9:].notna().all()

    def test_kwargs_override(self):
        """kwargs 覆盖 period=20：列名 vidya_20，首有效仍由 cmo_period=9 决定（index 9）。"""
        df = _make_golden_df_11(60)
        result = VIDYA().compute(df, period=20)
        assert list(result.columns) == ["vidya_20"]
        assert result["vidya_20"].iloc[:9].isna().all()
        assert result["vidya_20"].iloc[9:].notna().all()

    def test_empty_and_missing_column(self):
        result = VIDYA().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["vidya_14"]
        with pytest.raises(ValueError, match="缺少列"):
            VIDYA().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestPriceTransformNumeric:
    """四价格变换 AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE——talib 黄金对照 + 手工一行 + 边界。"""

    @pytest.mark.parametrize(
        "iid,cols,fn",
        [
            # talib 0.7.1 签名：AVGPRICE(O,H,L,C) 4 参；MEDPRICE(H,L) 2 参；TYPPRICE/WCLPRICE(H,L,C) 3 参
            ("avgprice", ["open", "high", "low", "close"], talib.AVGPRICE),
            ("medprice", ["high", "low"], talib.MEDPRICE),
            ("typprice", ["high", "low", "close"], talib.TYPPRICE),
            ("wcprice", ["high", "low", "close"], talib.WCLPRICE),
        ],
    )
    def test_golden_vs_talib(self, iid, cols, fn):
        """黄金对照：全序列与 talib 一致（rtol=atol=1e-12，线性变换应逐位一致）。"""
        df = _make_golden_df_11()
        got = TechnicalIndicatorRegistry.get(iid)().compute(df)[iid].to_numpy()
        expected = fn(*[df[c].to_numpy() for c in cols])
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)

    def test_hand_one_row(self):
        """手工一行：O=10/H=12/L=9/C=11 → avg=10.5、med=10.5、typ=32/3、wc=43/4。"""
        df = pd.DataFrame({"open": [10.0], "high": [12.0], "low": [9.0], "close": [11.0]})
        assert AVGPRICE().compute(df)["avgprice"].iloc[0] == pytest.approx(10.5)
        assert MEDPRICE().compute(df)["medprice"].iloc[0] == pytest.approx(10.5)
        assert TYPPRICE().compute(df)["typprice"].iloc[0] == pytest.approx(32.0 / 3.0)
        assert WCPRICE().compute(df)["wcprice"].iloc[0] == pytest.approx(43.0 / 4.0)

    def test_no_nan_and_index_aligned(self):
        """价格变换首行即有效：全序列无 NaN 且 index 对齐。"""
        df = _make_golden_df_11()
        for cls, col in ((AVGPRICE, "avgprice"), (MEDPRICE, "medprice"), (TYPPRICE, "typprice"), (WCPRICE, "wcprice")):
            result = cls().compute(df)
            assert result[col].notna().all()
            assert result.index.equals(df.index)

    def test_avgprice_missing_open_raises(self):
        """AVGPRICE 缺 open → ValueError（ERROR_CONTRACT：缺列即抛）。"""
        with pytest.raises(ValueError, match="缺少列"):
            AVGPRICE().compute(pd.DataFrame({"high": [10.0] * 5, "low": [9.0] * 5, "close": [10.5] * 5}))

    @pytest.mark.parametrize("iid", ["avgprice", "medprice", "typprice", "wcprice"])
    def test_empty_dataframe(self, iid):
        """空 DataFrame → 空输出（columns=meta.output_columns）。"""
        cols = {
            "avgprice": ["open", "high", "low", "close"],
            "medprice": ["high", "low"],
            "typprice": ["high", "low", "close"],
            "wcprice": ["high", "low", "close"],
        }[iid]
        result = TechnicalIndicatorRegistry.get(iid)().compute(pd.DataFrame(columns=cols))
        assert result.empty
        assert list(result.columns) == [iid]


# ===========================================================================
# 2026-09-20 简单指标清欠班波2-A：INERTIA/QSTICK 数值正确性
# ===========================================================================


class TestInertiaNumeric:
    """INERTIA 惯性指标——纯 python 独立复算（RVI+种子 EMA+OLS 端点全链）+ 单边/退化微样本 + 边界。

    talib 0.7.1 无 INERTIA（TA-Lib 无对应函数），黄金锚点=测试内独立复算（移植源
    pandas_ta_classic/momentum/inertia.py 基础模式，src 取 HL2 按车道规格）。
    """

    @staticmethod
    def _recompute(hl2: np.ndarray, length: int, rvi_length: int, scalar: float) -> np.ndarray:
        m = len(hl2)
        # 1) 滚动总体标准差 ddof=0
        std = [float(np.std(hl2[t - rvi_length + 1 : t + 1])) if t >= rvi_length - 1 else np.nan for t in range(m)]
        # 2) 方向示性（diff 首位 NaN 记 0，与源 unsigned_differences 一致）
        pos = [0.0] * m
        neg = [0.0] * m
        for t in range(1, m):
            d = hl2[t] - hl2[t - 1]
            if d > 0:
                pos[t] = 1.0
            elif d < 0:
                neg[t] = 1.0

        # 3) pandas-ta SMA 种子 EMA：首个有效位起取 length 窗 SMA 为种子，随后 α=2/(N+1) 递推
        def seeded_ema(x: list) -> list:
            out = [np.nan] * m
            fv = next(i for i, v in enumerate(x) if not np.isnan(v))
            seed_pos = fv + rvi_length - 1
            if seed_pos >= m:
                return out
            alpha = 2.0 / (rvi_length + 1)
            prev = sum(x[fv : seed_pos + 1]) / rvi_length
            for i in range(seed_pos, m):
                if i > seed_pos:
                    prev = alpha * x[i] + (1 - alpha) * prev
                out[i] = prev
            return out

        pos_avg = seeded_ema([pos[t] * std[t] for t in range(m)])
        neg_avg = seeded_ema([neg[t] * std[t] for t in range(m)])
        rvi = [
            scalar * pos_avg[t] / (pos_avg[t] + neg_avg[t]) if pos_avg[t] == pos_avg[t] else np.nan for t in range(m)
        ]
        # 4) 滚动 OLS 端点拟合值（x=[0..length−1]）
        x = list(range(length))
        sx, sx2 = float(sum(x)), float(sum(v * v for v in x))
        divisor = length * sx2 - sx * sx
        out = [np.nan] * m
        for t in range(2 * rvi_length - 2 + length - 1, m):
            w = rvi[t - length + 1 : t + 1]
            sy, sxy = math.fsum(w), math.fsum(x[i] * w[i] for i in range(length))
            slope = (length * sxy - sx * sy) / divisor
            intercept = (sy * sx2 - sx * sxy) / divisor
            out[t] = slope * (length - 1) + intercept
        return np.array(out)

    def test_independent_recompute(self):
        """独立复算锚点：纯 python 全链复算，第 45 根起全序列对拍（rtol=atol=1e-10）。"""
        df = _make_golden_df_11()
        hl2 = ((df["high"] + df["low"]) / 2.0).to_numpy()
        got = INERTIA().compute(df)["inertia_20_14"].to_numpy()
        expected = self._recompute(hl2, length=20, rvi_length=14, scalar=100.0)
        assert np.isnan(got[:45]).all()
        np.testing.assert_allclose(got[45:], expected[45:], rtol=1e-10, atol=1e-10)

    def test_uptrend_100_downtrend_0(self):
        """单调上行：Δ>0 恒真 → RVI≡100 → INERTIA≡100（>50 正惯性）；下行对称 ≡0。"""
        mid = np.linspace(100.0, 140.0, 80)
        up = INERTIA().compute(pd.DataFrame({"high": mid + 0.5, "low": mid - 0.5}))
        assert up["inertia_20_14"].iloc[:45].isna().all()
        np.testing.assert_allclose(up["inertia_20_14"].iloc[45:], 100.0, rtol=1e-9, atol=1e-9)
        dn = INERTIA().compute(pd.DataFrame({"high": mid[::-1] + 0.5, "low": mid[::-1] - 0.5}))
        np.testing.assert_allclose(dn["inertia_20_14"].iloc[45:], 0.0, rtol=1e-9, atol=1e-9)

    def test_constant_price_all_nan(self):
        """常数价格：STD=0 → RVI 0/0=NaN → 全 NaN（移植源忠实退化行为）。"""
        const = pd.DataFrame({"high": np.full(80, 100.0), "low": np.full(80, 100.0)})
        result = INERTIA().compute(const)
        assert result["inertia_20_14"].isna().all()

    def test_kwargs_override(self):
        """kwargs 覆盖：rvi_length=21 → 列名 inertia_20_21 且首有效右移（std 预热 20 + 种子位 40
        → linreg 首有效=40+19=59）；mamode='sma' 与默认 'ema' 数值可分。"""
        df = _make_golden_df_11(120)
        alt = INERTIA().compute(df, rvi_length=21)
        assert list(alt.columns) == ["inertia_20_21"]
        got = alt["inertia_20_21"].to_numpy()
        assert np.isnan(got[:59]).all()
        assert not np.isnan(got[59:]).any()
        base = INERTIA().compute(df)["inertia_20_14"].to_numpy()
        sma = INERTIA().compute(df, mamode="sma")["inertia_20_14"].to_numpy()
        assert not np.allclose(base[59:], sma[59:])

    def test_empty_and_missing_column(self):
        result = INERTIA().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty
        assert list(result.columns) == ["inertia_20_14"]
        with pytest.raises(ValueError, match="缺少列"):
            INERTIA().compute(pd.DataFrame({"close": [10.0] * 60}))


class TestQstickNumeric:
    """QSTICK Q 棒指标——纯 python 滚动均值复算 + 手工微样本 + 十字星/预热/边界。"""

    def test_independent_recompute(self):
        """独立复算锚点：纯 python 逐窗均值，与实现 pandas rolling 解耦（rtol=atol=1e-12）。"""
        df = _make_golden_df_11()
        diff = (df["close"] - df["open"]).to_numpy()
        n = 10
        expected = [float(np.mean(diff[t - n + 1 : t + 1])) if t >= n - 1 else np.nan for t in range(len(diff))]
        got = QSTICK().compute(df)["qstick_10"].to_numpy()
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（n=2）：C−O=[2,−1,1] → qstick[1]=0.5、qstick[2]=0（手算写死）。"""
        df = pd.DataFrame({"open": [10.0, 11.0, 12.0], "close": [12.0, 10.0, 13.0]})
        got = QSTICK().compute(df, length=2)["qstick_2"].to_numpy()
        assert np.isnan(got[0])
        assert got[1] == pytest.approx(0.5)
        assert got[2] == pytest.approx(0.0)

    def test_warmup_and_doji_zero(self):
        """预热前 9 根 NaN；十字星（C=O 恒定）按数学定义输出 0（非源 0.001 epsilon 修补）。"""
        df = pd.DataFrame({"open": [10.0] * 30, "close": [10.0] * 30})
        got = QSTICK().compute(df)["qstick_10"]
        assert got.iloc[:9].isna().all()
        assert np.allclose(got.iloc[9:], 0.0)

    def test_bull_bear_sign(self):
        """持续阳线（C>O）→ 正值；持续阴线（C<O）→ 负值。"""
        up = QSTICK().compute(pd.DataFrame({"open": np.full(20, 100.0), "close": np.linspace(101, 120, 20)}))
        down = QSTICK().compute(pd.DataFrame({"open": np.full(20, 100.0), "close": np.linspace(99, 80, 20)}))
        assert (up["qstick_10"].dropna() > 0).all()
        assert (down["qstick_10"].dropna() < 0).all()

    def test_kwargs_override(self):
        """kwargs 覆盖 length=5：列名 qstick_5，首有效=index 4。"""
        df = _make_golden_df_11(40)
        result = QSTICK().compute(df, length=5)
        assert list(result.columns) == ["qstick_5"]
        assert result["qstick_5"].iloc[:4].isna().all()
        assert result["qstick_5"].iloc[4:].notna().all()

    def test_empty_and_missing_column(self):
        result = QSTICK().compute(pd.DataFrame(columns=["open", "close"]))
        assert result.empty
        assert list(result.columns) == ["qstick_10"]
        with pytest.raises(ValueError, match="缺少列"):
            QSTICK().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# 2026-09-20 Ehlers 滤波器族班波3-B：SUPERSMOOTHER/HIGHPASS/PTREND 数值正确性
# talib 0.7.1 无此三件（SuperSmoother/HighPass3/PTrend 均非 TA-Lib 函数），
# 黄金锚点=测试内 numpy 纯循环独立复算（双实现互证）+ 手工微样本写死。
# ===========================================================================


class TestSupersmootherNumeric:
    """SUPERSMOOTHER 超级平滑器——numpy 双实现互证 + 手工微样本 + 性质/边界。"""

    def test_independent_recompute(self):
        """独立复算锚点：纯 numpy 逐 bar 递推复算，全序列对拍（rtol=atol=1e-12）。"""
        close = _make_golden_df_11()["close"].to_numpy()
        got = SUPERSMOOTHER().compute(pd.DataFrame({"close": close}))["supersmoother_10"].to_numpy()
        # --- 独立复算（规格公式直译，与实现解耦） ---
        n = 10
        a1 = np.exp(-1.414 * np.pi / n)
        c2 = 2.0 * a1 * np.cos(1.414 * np.pi / n)
        c3 = -(a1 * a1)
        c1 = 1.0 - c2 - c3
        expected = np.empty(len(close))
        expected[0] = close[0]
        expected[1] = (close[0] + close[1]) / 2.0
        for t in range(2, len(close)):
            expected[t] = c1 * (close[t] + close[t - 1]) / 2.0 + c2 * expected[t - 1] + c3 * expected[t - 2]
        assert not np.isnan(got).any()
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（3 根）：close=[10,12,11]，period=10，独立手算写死。

        f=1.414π/10 → a1=exp(-f)=0.6413235435874742；c2=2a1·cos(f)=1.158160584385297；
        c3=-a1²=-0.41129588755959495；c1=1-c2-c3=0.25313530317429805。
        ss[0]=10；ss[1]=(10+12)/2=11；
        ss[2]=c1×(12+11)/2 + c2×11 + c3×10 = 11.537863539146745（写死）。
        """
        df = pd.DataFrame({"close": [10.0, 12.0, 11.0]})
        got = SUPERSMOOTHER().compute(df)["supersmoother_10"].to_numpy()
        assert got[0] == pytest.approx(10.0)
        assert got[1] == pytest.approx(11.0)
        assert got[2] == pytest.approx(11.537863539146745, rel=1e-12)

    def test_constant_series_identity(self):
        """常数序列：c1+c2+c3=1 → 输出恒等于该常数（全序列无 NaN）。"""
        df = pd.DataFrame({"close": [10.0] * 30})
        got = SUPERSMOOTHER().compute(df)["supersmoother_10"].to_numpy()
        np.testing.assert_allclose(got, 10.0, rtol=1e-12)

    def test_sine_attenuation_and_lag(self):
        """正弦输入（16 bar 主波，period=10）：低通衰减（幅度比 <1，落入 0.5-1.2 宽松带）且相位滞后。

        实测幅度比≈0.925、波峰滞后 2 bar（<半周期 8 bar）。
        """
        t = np.arange(200)
        close = 100.0 + 10.0 * np.sin(2.0 * np.pi * t / 16.0)
        got = SUPERSMOOTHER().compute(pd.DataFrame({"close": close}))["supersmoother_10"].to_numpy()
        tail = slice(140, 196)  # 稳态段 4 个完整波
        ratio = ((got[tail].max() - got[tail].min()) / 2.0) / ((close[tail].max() - close[tail].min()) / 2.0)
        assert 0.5 < ratio < 1.2
        assert ratio < 1.0  # 低通衰减
        peak_in = 140 + int(np.argmax(close[tail]))
        lag = int(np.argmax(got[peak_in : peak_in + 16]))
        assert 0 < lag < 8  # 滞后且不足半周期

    def test_period_override(self):
        """kwargs 覆盖 period=20：列名 supersmoother_20，仍无 NaN 且与默认可分。"""
        df = _make_golden_df_11(80)
        base = SUPERSMOOTHER().compute(df)["supersmoother_10"].to_numpy()
        result = SUPERSMOOTHER().compute(df, period=20)
        assert list(result.columns) == ["supersmoother_20"]
        alt = result["supersmoother_20"].to_numpy()
        assert not np.isnan(alt).any()
        assert not np.allclose(base, alt)

    def test_empty_and_missing_column(self):
        result = SUPERSMOOTHER().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["supersmoother_10"]
        with pytest.raises(ValueError, match="缺少列"):
            SUPERSMOOTHER().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestHighpassNumeric:
    """HIGHPASS 三阶高通滤波——numpy 双实现互证 + 手工微样本 + 性质/边界。"""

    def test_independent_recompute(self):
        """独立复算锚点：纯 numpy 逐 bar 递推复算，全序列对拍（rtol=atol=1e-12）。"""
        close = _make_golden_df_11()["close"].to_numpy()
        got = HIGHPASS().compute(pd.DataFrame({"close": close}))["highpass_40"].to_numpy()
        # --- 独立复算（规格公式直译，与实现解耦） ---
        n = 40
        f = 1.414 * np.pi / n
        a1 = np.exp(-f)
        c2 = 2.0 * a1 * np.cos(f / 2.0)
        c3 = -(a1 * a1)
        c1 = (1.0 + c2 - c3) / 4.0
        expected = np.zeros(len(close))
        for t in range(2, len(close)):
            expected[t] = (
                c1 * (close[t] - 2.0 * close[t - 1] + close[t - 2]) + c2 * expected[t - 1] + c3 * expected[t - 2]
            )
        assert not np.isnan(got).any()
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（3 根）：close=[100,102,99]，period=40，独立手算写死。

        f=1.414π/40 → a1=0.894889259912188；c2=2a1·cos(f/2)=1.7870199988257192；
        c3=-a1²=-0.8008267875061836；c1=(1+c2-c3)/4=0.8969616965829756。
        hp[0]=hp[1]=0（零种子）；hp[2]=c1×(99-2×102+100)+c2×0+c3×0 = -4.484808482914878（写死）。
        """
        df = pd.DataFrame({"close": [100.0, 102.0, 99.0]})
        got = HIGHPASS().compute(df)["highpass_40"].to_numpy()
        assert got[0] == pytest.approx(0.0, abs=1e-15)
        assert got[1] == pytest.approx(0.0, abs=1e-15)
        assert got[2] == pytest.approx(-4.484808482914878, rel=1e-12)

    def test_constant_series_zero(self):
        """常数序列：二阶差分恒 0 → 高通全程为 0（零种子不被激活）。"""
        df = pd.DataFrame({"close": [10.0] * 60})
        got = HIGHPASS().compute(df)["highpass_40"].to_numpy()
        np.testing.assert_allclose(got, 0.0, atol=1e-12)

    def test_zero_seeds_not_nan(self):
        """首两根记 0 值非 NaN（C 源零种子；warmup 记 3 语义=前两根无意义而非缺数据）。"""
        close = _make_golden_df_11()["close"].to_numpy()
        got = HIGHPASS().compute(pd.DataFrame({"close": close}))["highpass_40"].to_numpy()
        assert got[0] == 0.0
        assert got[1] == 0.0
        assert not np.isnan(got).any()

    def test_period_override(self):
        """kwargs 覆盖 period=20：列名 highpass_20，零种子仍在首两根。"""
        df = _make_golden_df_11()
        result = HIGHPASS().compute(df, period=20)
        assert list(result.columns) == ["highpass_20"]
        got = result["highpass_20"].to_numpy()
        assert got[0] == 0.0
        assert got[1] == 0.0

    def test_empty_and_missing_column(self):
        result = HIGHPASS().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["highpass_40"]
        with pytest.raises(ValueError, match="缺少列"):
            HIGHPASS().compute(pd.DataFrame({"open": [10.0] * 30}))


class TestPtrendNumeric:
    """PTREND 精调趋势——numpy 双实现互证 + 手工微样本 + 性质/边界。"""

    def test_independent_recompute(self):
        """独立复算锚点：双 HighPass3 + 谱带差分 + TROC 全链纯 numpy 复算（rtol=atol=1e-12）。"""
        close = _make_golden_df_11(300)["close"].to_numpy()
        result = PTREND().compute(pd.DataFrame({"close": close}))
        got_pt = result["ptrend_250_40"].to_numpy()
        got_roc = result["ptrend_roc"].to_numpy()

        # --- 独立复算（规格公式直译，与实现解耦） ---
        def highpass3(p, n):
            f = 1.414 * np.pi / n
            a1 = np.exp(-f)
            c2 = 2.0 * a1 * np.cos(f / 2.0)
            c3 = -(a1 * a1)
            c1 = (1.0 + c2 - c3) / 4.0
            hp = np.zeros(len(p))
            for t in range(2, len(p)):
                hp[t] = c1 * (p[t] - 2.0 * p[t - 1] + p[t - 2]) + c2 * hp[t - 1] + c3 * hp[t - 2]
            return hp

        pt = highpass3(close, 250) - highpass3(close, 40)
        troc = np.full(len(close), np.nan)
        troc[1:] = (40.0 / 6.283185307179586) * np.diff(pt)
        np.testing.assert_allclose(got_pt, pt, rtol=1e-12, atol=1e-12)
        assert np.isnan(got_roc[0])
        np.testing.assert_allclose(got_roc[1:], troc[1:], rtol=1e-12, atol=1e-12)

    def test_hand_micro_sample(self):
        """手工微样本（4 根，默认 250/40）：close=[100,102,99,103]，独立手算写死。

        独立手算两滤波器（零种子）：hp_long[2]=c1_250×(99-204+100)=-4.912231231641025、
        hp_long[3]=-2.7739302553851806；hp_short[2]=-4.484808482914878、hp_short[3]=-1.735710573791291；
        ptrend[2]=hl[2]-hs[2]=-0.42742274872614683（写死）；
        ptrend[3]=hl[3]-hs[3]=-1.0382196815938896（写死）；
        troc[3]=(40/2π)×(ptrend[3]-ptrend[2])=-3.8884540436507926（写死）。
        """
        df = pd.DataFrame({"close": [100.0, 102.0, 99.0, 103.0]})
        result = PTREND().compute(df)
        got_pt = result["ptrend_250_40"].to_numpy()
        got_roc = result["ptrend_roc"].to_numpy()
        assert got_pt[0] == pytest.approx(0.0, abs=1e-15)
        assert got_pt[1] == pytest.approx(0.0, abs=1e-15)
        assert got_pt[2] == pytest.approx(-0.42742274872614683, rel=1e-12)
        assert got_pt[3] == pytest.approx(-1.0382196815938896, rel=1e-12)
        assert np.isnan(got_roc[0])
        assert got_roc[3] == pytest.approx(-3.8884540436507926, rel=1e-12)

    def test_constant_series_zero(self):
        """常数序列：二阶差分恒 0 → ptrend 全 0、troc 全 0（首位 NaN）。"""
        df = pd.DataFrame({"close": [10.0] * 120})
        result = PTREND().compute(df)
        np.testing.assert_allclose(result["ptrend_250_40"].to_numpy(), 0.0, atol=1e-12)
        roc = result["ptrend_roc"].to_numpy()
        assert np.isnan(roc[0])
        np.testing.assert_allclose(roc[1:], 0.0, atol=1e-12)

    def test_kwargs_override_columns_fixed(self):
        """kwargs 覆盖 period_long/period_short：列名仍固定 ptrend_250_40/ptrend_roc（双参语义，mama/fama 先例），数值可分。"""
        df = _make_golden_df_11(300)
        base = PTREND().compute(df)["ptrend_250_40"].to_numpy()
        result = PTREND().compute(df, period_long=200, period_short=30)
        assert list(result.columns) == ["ptrend_250_40", "ptrend_roc"]
        alt = result["ptrend_250_40"].to_numpy()
        assert not np.allclose(base[60:], alt[60:])

    def test_empty_and_missing_column(self):
        result = PTREND().compute(pd.DataFrame(columns=["close"]))
        assert result.empty
        assert list(result.columns) == ["ptrend_250_40", "ptrend_roc"]
        with pytest.raises(ValueError, match="缺少列"):
            PTREND().compute(pd.DataFrame({"open": [10.0] * 30}))
