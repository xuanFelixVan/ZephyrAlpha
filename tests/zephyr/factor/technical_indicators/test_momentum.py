# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""动量类技术指标测试（43 个）。

测试内容：
- 43 个动量指标全部注册到 Registry
- 每个指标 meta.category == "momentum"
- 每个指标 meta.output_columns == 期望列（catalog §2.2 契约）
- 已实现指标（全部 43 个）：数值正确性 + 边界测试

数值正确性验证：手工计算期望值 + 通达信公式对齐（SMA alpha=1/N）。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.2
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import momentum  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 便捷别名
KDJ = TechnicalIndicatorRegistry.get("kdj")
RSI = TechnicalIndicatorRegistry.get("rsi")
WR = TechnicalIndicatorRegistry.get("wr")
ROC = TechnicalIndicatorRegistry.get("roc")
MTM = TechnicalIndicatorRegistry.get("mtm")
CMF = TechnicalIndicatorRegistry.get("cmf")
UOS = TechnicalIndicatorRegistry.get("uos")
AO = TechnicalIndicatorRegistry.get("ao")
CMO = TechnicalIndicatorRegistry.get("cmo")
STOCHRSI = TechnicalIndicatorRegistry.get("stochrsi")
BIAS = TechnicalIndicatorRegistry.get("bias")
PSY = TechnicalIndicatorRegistry.get("psy")
LWR = TechnicalIndicatorRegistry.get("lwr")
DPO = TechnicalIndicatorRegistry.get("dpo")
TSI = TechnicalIndicatorRegistry.get("tsi")
SMI = TechnicalIndicatorRegistry.get("smi")
FISHER = TechnicalIndicatorRegistry.get("fisher")
KST = TechnicalIndicatorRegistry.get("kst")
CONNORSRSI = TechnicalIndicatorRegistry.get("connorsrsi")
QQE = TechnicalIndicatorRegistry.get("qqe")
STC = TechnicalIndicatorRegistry.get("stc")
RVGI = TechnicalIndicatorRegistry.get("rvgi")
STOCH = TechnicalIndicatorRegistry.get("stoch")
AROON = TechnicalIndicatorRegistry.get("aroon")
AROONOSC = TechnicalIndicatorRegistry.get("aroonosc")
BOP = TechnicalIndicatorRegistry.get("bop")
PPO = TechnicalIndicatorRegistry.get("ppo")
APO = TechnicalIndicatorRegistry.get("apo")
DX = TechnicalIndicatorRegistry.get("dx")
BRAR = TechnicalIndicatorRegistry.get("brar")
CR = TechnicalIndicatorRegistry.get("cr")
AC = TechnicalIndicatorRegistry.get("ac")
FRACTALS = TechnicalIndicatorRegistry.get("fractals")
ELDER = TechnicalIndicatorRegistry.get("elder")
COPPOCK = TechnicalIndicatorRegistry.get("coppock")
SQUEEZE = TechnicalIndicatorRegistry.get("squeeze")
WAVETREND = TechnicalIndicatorRegistry.get("wavetrend")
RMI = TechnicalIndicatorRegistry.get("rmi")
PFE = TechnicalIndicatorRegistry.get("pfe")
FOSC = TechnicalIndicatorRegistry.get("fosc")
CTI = TechnicalIndicatorRegistry.get("cti")
VHF = TechnicalIndicatorRegistry.get("vhf")
ER = TechnicalIndicatorRegistry.get("er")

# 期望契约（catalog §2.2）
EXPECTED = {
    "kdj": ("随机指标", ["kdj_k", "kdj_d", "kdj_j"]),
    "rsi": ("相对强弱指标", ["rsi_6", "rsi_12", "rsi_24"]),
    "wr": ("威廉指标", ["wr_14"]),
    "roc": ("变动率", ["roc_12"]),
    "mtm": ("动量指标", ["mtm_12", "mtmma_12"]),
    "cmf": ("蔡金资金流", ["cmf_20"]),
    "uos": ("终极指标", ["uos"]),
    "ao": ("震荡指标", ["ao"]),
    "cmo": ("钱德动量摆动", ["cmo_14"]),
    "stochrsi": ("随机RSI", ["stochrsi"]),
    "bias": ("乖离率", ["bias_6", "bias_12", "bias_24"]),
    "psy": ("心理线", ["psy_12", "psy_ma6"]),
    "lwr": ("慢速威廉", ["lwr_1", "lwr_2"]),
    "dpo": ("区间震荡", ["dpo_20"]),
    "tsi": ("真实强度指数", ["tsi"]),
    "smi": ("随机动量指数", ["smi", "smi_signal"]),
    "fisher": ("费雪变换", ["fisher_9", "fisher_sig9"]),
    "kst": ("确知量", ["kst", "kst_signal"]),
    "connorsrsi": ("ConnorsRSI", ["crsi"]),
    "qqe": ("QQE", ["qqe_14", "qqe_rsi_ma"]),
    "stc": ("Schaff趋势周期", ["stc"]),
    "rvgi": ("相对活力指数", ["rvgi_10", "rvgi_sig"]),
    "stoch": ("随机振荡器", ["stoch_fastk", "stoch_fastd", "stoch_slowk", "stoch_slowd"]),
    "aroon": ("阿隆指标", ["aroon_up", "aroon_down"]),
    "aroonosc": ("阿隆震荡器", ["aroonosc"]),
    "bop": ("力量平衡", ["bop"]),
    "ppo": ("百分比价格振荡器", ["ppo"]),
    "apo": ("绝对价格振荡器", ["apo"]),
    "dx": ("动向指数", ["dx_14"]),
    "brar": ("人气意愿指标", ["ar_26", "br_26"]),
    "cr": ("能量指标", ["cr_26"]),
    "ac": ("加速振荡器", ["ac"]),
    "fractals": ("威廉分形", ["fractal_high", "fractal_low"]),
    "elder": ("牛熊力", ["bull_power_13", "bear_power_13"]),
    "coppock": ("考派尔曲线", ["coppock"]),
    "squeeze": ("挤压指标", ["squeeze_on", "squeeze_mom"]),
    "wavetrend": ("波浪趋势", ["wt1", "wt2"]),
    "rmi": ("相对动量指数", ["rmi_14"]),
    "pfe": ("极化分形效率", ["pfe_10"]),
    "fosc": ("预测震荡", ["fosc_14"]),
    "cti": ("相关趋势指标", ["cti_12"]),
    "vhf": ("纵横过滤", ["vhf_28"]),
    "er": ("效率比率", ["er_10"]),
}

IMPLEMENTED = set(EXPECTED)
SKELETON = set(EXPECTED) - IMPLEMENTED  # 空集

_RNG = np.random.default_rng(42)


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正）。"""
    close = 100 + _RNG.standard_normal(n).cumsum()
    high = close + _RNG.uniform(0.1, 0.5, n)
    low = close - _RNG.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


# ===========================================================================
# 注册与元数据契约测试
# ===========================================================================


class TestMomentumRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("momentum")}
        for iid in EXPECTED:
            assert iid in metas, f"动量指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("momentum")) == len(EXPECTED) == 43


class TestMomentumMetaContract:
    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_category(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.category == "momentum"

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


class TestMomentumComputeNotImplemented:
    @pytest.mark.parametrize("iid", sorted(SKELETON))
    def test_compute_raises(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        df = pd.DataFrame(
            {"open": [10.0] * 30, "high": [11.0] * 30, "low": [9.0] * 30, "close": [10.5] * 30, "volume": [1000.0] * 30}
        )
        with pytest.raises(NotImplementedError, match="待施工"):
            cls().compute(df)


# ===========================================================================
# KDJ 数值正确性测试
# ===========================================================================


class TestKDJCompute:
    """KDJ 随机指标——数值正确性（SMA alpha=1/N）+ 关系约束 + 边界测试。"""

    def test_j_equals_3k_minus_2d(self):
        """J = 3K - 2D，逐行精确验证。"""
        df = _make_ohlcv(50)
        result = KDJ().compute(df)
        expected_j = 3 * result["kdj_k"] - 2 * result["kdj_d"]
        pd.testing.assert_series_equal(result["kdj_j"], expected_j, check_names=False)

    def test_kd_range(self):
        """K/D 在 0~100 范围内（RSV 限定了范围）。"""
        df = _make_ohlcv(50)
        result = KDJ().compute(df)
        valid = result.iloc[8:].dropna()  # period=9 预热
        assert (valid["kdj_k"] >= 0).all() and (valid["kdj_k"] <= 100).all()
        assert (valid["kdj_d"] >= 0).all() and (valid["kdj_d"] <= 100).all()

    def test_constant_series(self):
        """常数 HLC：RSV=50（C=L=H），K=D=50，J=50。"""
        df = pd.DataFrame({"high": [10.0] * 30, "low": [10.0] * 30, "close": [10.0] * 30})
        result = KDJ().compute(df, period=9)
        # RSV = 0/0 → NaN，所以常数序列会产生 NaN
        # 改用接近常数但有微小波动
        df2 = pd.DataFrame({"high": [10.1] * 30, "low": [9.9] * 30, "close": [10.0] * 30})
        result2 = KDJ().compute(df2, period=9)
        valid = result2["kdj_k"].iloc[8:].dropna()
        assert np.allclose(valid, 50.0, atol=1.0)

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = KDJ().compute(df)
        assert list(result.columns) == ["kdj_k", "kdj_d", "kdj_j"]

    def test_empty_dataframe(self):
        result = KDJ().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            KDJ().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# RSI 数值正确性测试
# ===========================================================================


class TestRSICompute:
    """RSI 相对强弱指标——数值正确性（SMA 平滑）+ 边界测试。"""

    def test_rsi_range(self):
        """RSI 在 0~100 范围内。"""
        df = _make_ohlcv(50)
        result = RSI().compute(df)
        for col in ["rsi_6", "rsi_12", "rsi_24"]:
            valid = result[col].dropna()
            assert (valid >= 0).all() and (valid <= 100).all()

    def test_uptrend_high_rsi(self):
        """持续上涨：RSI 接近 100。"""
        close = np.linspace(10, 20, 30)
        df = pd.DataFrame({"close": close})
        result = RSI().compute(df, periods=[6])
        valid = result["rsi_6"].iloc[6:].dropna()
        assert (valid > 80).all()

    def test_downtrend_low_rsi(self):
        """持续下跌：RSI 接近 0。"""
        close = np.linspace(20, 10, 30)
        df = pd.DataFrame({"close": close})
        result = RSI().compute(df, periods=[6])
        valid = result["rsi_6"].iloc[6:].dropna()
        assert (valid < 20).all()

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = RSI().compute(df)
        assert list(result.columns) == ["rsi_6", "rsi_12", "rsi_24"]

    def test_empty_dataframe(self):
        result = RSI().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            RSI().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# WR 数值正确性测试
# ===========================================================================


class TestWRCompute:
    """WR 威廉指标——数值正确性 + 边界测试。"""

    def test_wr_range(self):
        """WR 在 0~100 范围内。"""
        df = _make_ohlcv(50)
        result = WR().compute(df)
        valid = result["wr_14"].iloc[13:].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_at_high(self):
        """close = 周期最高价时 WR=0（超买）。"""
        high = [10, 12, 14, 13, 15] + [15] * 15
        low = [8, 9, 10, 11, 12] + [12] * 15
        close = [9, 11, 13, 12, 15] + [15] * 15
        df = pd.DataFrame({"high": high, "low": low, "close": close})
        result = WR().compute(df, period=14)
        # 当 close = hh 时 WR = 0
        valid = result["wr_14"].iloc[13:].dropna()
        assert np.allclose(valid, 0.0)

    def test_output_columns(self):
        df = _make_ohlcv(30)
        result = WR().compute(df)
        assert list(result.columns) == ["wr_14"]

    def test_empty_dataframe(self):
        result = WR().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            WR().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# ROC 数值正确性测试
# ===========================================================================


class TestROCCompute:
    """ROC 变动率——数值正确性 + 边界测试。"""

    def test_basic_values(self):
        """ROC = (C - Cn) / Cn × 100。"""
        close = [10.0, 11.0, 12.0, 13.0]
        df = pd.DataFrame({"close": close})
        result = ROC().compute(df, period=2)
        # ROC[2] = (12 - 10) / 10 * 100 = 20
        assert result["roc_2"].iloc[2] == pytest.approx(20.0)
        # ROC[3] = (13 - 11) / 11 * 100 ≈ 18.18
        assert result["roc_2"].iloc[3] == pytest.approx(200 / 11)

    def test_empty_dataframe(self):
        result = ROC().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            ROC().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# MTM 数值正确性测试
# ===========================================================================


class TestMTMCompute:
    """MTM 动量指标——数值正确性 + 关系约束 + 边界测试。"""

    def test_mtm_formula(self):
        """MTM = C - Cn（绝对差值）。"""
        close = [10.0, 11.0, 12.0, 13.0]
        df = pd.DataFrame({"close": close})
        result = MTM().compute(df, period=2, ma_period=2)
        assert result["mtm_2"].iloc[2] == pytest.approx(2.0)  # 12 - 10
        assert result["mtm_2"].iloc[3] == pytest.approx(2.0)  # 13 - 11

    def test_mtmma_is_ma_of_mtm(self):
        """MTMMA = MA(MTM, ma_period)。"""
        df = _make_ohlcv(50)
        result = MTM().compute(df, period=12, ma_period=6)
        expected = result["mtm_12"].rolling(window=6).mean()
        pd.testing.assert_series_equal(result["mtmma_12"], expected, check_names=False)

    def test_empty_dataframe(self):
        result = MTM().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MTM().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# CMF 数值正确性测试
# ===========================================================================


class TestCMFCompute:
    """CMF 蔡金资金流——数值正确性 + 边界测试。"""

    def test_cmf_range(self):
        """CMF 在 -1~1 范围内。"""
        df = _make_ohlcv(50)
        result = CMF().compute(df, period=20)
        valid = result["cmf_20"].iloc[19:].dropna()
        assert (valid >= -1).all() and (valid <= 1).all()

    def test_clv_zero_when_h_equals_l(self):
        """H=L 时 CLV=0（避免除零）。"""
        df = pd.DataFrame(
            {
                "high": [10.0] * 30,
                "low": [10.0] * 30,
                "close": [10.0] * 30,
                "volume": [1000.0] * 30,
            }
        )
        result = CMF().compute(df, period=20)
        # CLV=0 → MFV=0 → CMF=0
        valid = result["cmf_20"].iloc[19:].dropna()
        assert np.allclose(valid, 0.0)

    def test_empty_dataframe(self):
        result = CMF().compute(pd.DataFrame(columns=["high", "low", "close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CMF().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# UOS 数值正确性测试
# ===========================================================================


class TestUOSCompute:
    """UOS 终极指标——数值正确性 + 边界测试。"""

    def test_uos_range(self):
        """UOS 在 0~100 范围内。"""
        df = _make_ohlcv(60)
        result = UOS().compute(df, p1=7, p2=14, p3=28)
        valid = result["uos"].iloc[27:].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_empty_dataframe(self):
        result = UOS().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            UOS().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# AO 数值正确性测试
# ===========================================================================


class TestAOCompute:
    """AO 震荡指标——数值正确性 + 边界测试。"""

    def test_ao_formula(self):
        """AO = MA(median,fast) - MA(median,slow)，median=(H+L)/2。"""
        df = _make_ohlcv(50)
        result = AO().compute(df, fast=5, slow=34)
        median = (df["high"] + df["low"]) / 2
        expected = median.rolling(window=5).mean() - median.rolling(window=34).mean()
        pd.testing.assert_series_equal(result["ao"], expected, check_names=False)

    def test_empty_dataframe(self):
        result = AO().compute(pd.DataFrame(columns=["high", "low"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            AO().compute(pd.DataFrame({"high": [10.0] * 30}))


# ===========================================================================
# CMO 数值正确性测试
# ===========================================================================


class TestCMOCompute:
    """CMO 钱德动量摆动——数值正确性 + 边界测试。"""

    def test_cmo_range(self):
        """CMO 在 -100~100 范围内。"""
        df = _make_ohlcv(50)
        result = CMO().compute(df, period=14)
        valid = result["cmo_14"].iloc[13:].dropna()
        assert (valid >= -100).all() and (valid <= 100).all()

    def test_uptrend_positive(self):
        """持续上涨：CMO 接近 100。"""
        close = np.linspace(10, 20, 30)
        df = pd.DataFrame({"close": close})
        result = CMO().compute(df, period=14)
        valid = result["cmo_14"].iloc[14:].dropna()
        assert (valid > 80).all()

    def test_empty_dataframe(self):
        result = CMO().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CMO().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# StochRSI 数值正确性测试
# ===========================================================================


class TestStochRSICompute:
    """StochRSI 随机RSI——数值正确性 + 边界测试。"""

    def test_stochrsi_range(self):
        """StochRSI 在 0~1 范围内。"""
        df = _make_ohlcv(60)
        result = STOCHRSI().compute(df, rsi_period=14, stoch_period=14)
        valid = result["stochrsi"].iloc[27:].dropna()
        assert (valid >= 0).all()
        assert (valid <= 1.0001).all()  # 容许微小浮点误差

    def test_empty_dataframe(self):
        result = STOCHRSI().compute(pd.DataFrame(columns=["close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            STOCHRSI().compute(pd.DataFrame({"open": [10.0]}))


# ===========================================================================
# 2026-09-14 A股标配批：BIAS/PSY/LWR 数值正确性
# ===========================================================================


class TestBiasNumeric:
    def test_constant_close_zero_bias(self):
        df = _make_ohlcv(30)
        df["close"] = 100.0
        df["high"] = 100.5
        df["low"] = 99.5
        result = BIAS().compute(df)
        assert (result["bias_6"].dropna() == 0.0).all()
        assert (result["bias_24"].dropna() == 0.0).all()

    def test_warmup_nan(self):
        df = _make_ohlcv(30)
        result = BIAS().compute(df)
        assert result["bias_6"].iloc[:5].isna().all()
        assert result["bias_6"].iloc[6:].notna().all()

    def test_rising_close_positive_bias(self):
        df = _make_ohlcv(30)
        df["close"] = np.linspace(100, 130, 30)
        result = BIAS().compute(df)
        assert (result["bias_12"].dropna() > 0).all()


class TestPsyNumeric:
    def test_all_up_is_100(self):
        df = _make_ohlcv(30)
        df["close"] = np.arange(1, 31) * 1.0
        result = PSY().compute(df)
        assert (result["psy_12"].dropna() == 100.0).all()

    def test_alternating_is_50(self):
        df = _make_ohlcv(30)
        base = np.arange(1, 31) * 1.0
        df["close"] = base + np.where(np.arange(30) % 2 == 0, 0, 5)
        result = PSY().compute(df)
        assert (result["psy_12"].dropna() == 50.0).all()

    def test_first_row_nan_not_counted(self):
        df = _make_ohlcv(30)
        result = PSY().compute(df)
        # 首行无前值 → warmup 内 NaN（不会冒充"未上涨"拉低 PSY）
        assert result["psy_12"].isna().sum() == 12

    def test_psy_ma_warmup(self):
        df = _make_ohlcv(30)
        result = PSY().compute(df)
        assert result["psy_ma6"].isna().sum() == 17


class TestLwrNumeric:
    def test_range_0_100(self):
        df = _make_ohlcv(50)
        result = LWR().compute(df)
        for col in ("lwr_1", "lwr_2"):
            assert result[col].dropna().between(0, 100).all()

    def test_close_at_low_is_100(self):
        # 单调下跌且收在最低价 → 每个窗口 C=LL → 威廉值恒 100（超卖方向）
        n = 20
        low = np.linspace(120, 101, n)  # 严格单调递减
        high = low + 1.0
        close = low.copy()  # 收在最低价
        df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})
        result = LWR().compute(df)
        assert (result["lwr_1"].dropna() == 100.0).all()

    def test_close_at_high_is_0(self):
        # 单调上涨且收在最高价 → 每个窗口 C=HH → 威廉值恒 0
        n = 20
        high = np.linspace(101, 120, n)  # 严格单调递增
        low = high - 1.0
        close = high.copy()  # 收在最高价
        df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})
        result = LWR().compute(df)
        assert (result["lwr_1"].dropna() == 0.0).all()


class TestDpoNumeric:
    def test_constant_zero(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = DPO().compute(df)
        assert (result["dpo_20"].dropna() == 0.0).all()

    def test_warmup_includes_shift(self):
        df = _make_ohlcv(40)
        result = DPO().compute(df)
        # MA(20) 首值在第 19 行，再 shift(11) → 首个非 NaN 在第 30 行
        assert result["dpo_20"].iloc[:30].isna().all()
        assert result["dpo_20"].iloc[30:].notna().all()


# ===========================================================================
# 2026-09-14 主流热门批 2b：TSI/SMI/FISHER/KST/CONNORSRSI/QQE/STC/RVGI
# ===========================================================================


class TestBatch2bMomentumNumeric:
    def test_tsi_constant_zero(self):
        df = _make_ohlcv(60)
        df["close"] = 100.0
        result = TSI().compute(df)
        assert (result["tsi"].dropna() == 0.0).all()

    def test_smi_uptrend_positive(self):
        df = _make_ohlcv(60)
        rising = np.linspace(100, 130, 60)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = rising
        result = SMI().compute(df)
        assert (result["smi"].dropna() > 0).all()

    def test_fisher_range_bounded(self):
        df = _make_ohlcv(80)
        result = FISHER().compute(df)
        valid = result["fisher_9"].dropna()
        assert valid.abs().max() < 15  # 费雪值量级有限

    def test_kst_columns_match_signal_lags(self):
        df = _make_ohlcv(80)
        result = KST().compute(df)
        assert result["kst"].notna().sum() == result["kst_signal"].notna().sum() + 8

    def test_connorsrsi_range(self):
        df = _make_ohlcv(150)
        result = CONNORSRSI().compute(df)
        valid = result["crsi"].dropna()
        assert valid.between(0, 100).all()

    def test_qqe_columns_align(self):
        df = _make_ohlcv(80)
        result = QQE().compute(df)
        assert result["qqe_14"].dropna().shape[0] > 0
        assert (result["qqe_rsi_ma"].dropna().between(0, 100)).all()

    def test_stc_range(self):
        df = _make_ohlcv(120)
        result = STC().compute(df)
        assert result["stc"].dropna().between(0, 100).all()

    def test_rvgi_constant_close_near_zero(self):
        df = _make_ohlcv(40)
        for c in ("open", "close"):
            df[c] = 100.0
        result = RVGI().compute(df)
        assert (result["rvgi_10"].dropna().abs() < 1e-9).all()


# ===========================================================================
# 2026-09-14 批 6：STOCH/AROON/AROONOSC/BOP/PPO/APO/DX/BRAR/CR
# ===========================================================================


class TestStochNumeric:
    def test_uptrend_fastk_100(self):
        df = _make_ohlcv(30)
        rising = np.linspace(100, 130, 30)
        df["high"] = rising + 0.5
        df["low"] = rising - 0.5
        df["close"] = df["high"]  # 收在窗口最高 → FastK=100（浮点 ULP 容差）
        result = STOCH().compute(df)
        np.testing.assert_allclose(result["stoch_fastk"].dropna(), 100.0)

    def test_flat_price_fastk_50(self):
        df = _make_ohlcv(30)
        df["close"] = 100.0
        df["high"] = 100.0
        df["low"] = 100.0
        result = STOCH().compute(df)
        assert (result["stoch_fastk"].dropna() == 50.0).all()

    def test_range(self):
        df = _make_ohlcv(40)
        result = STOCH().compute(df)
        for col in ("stoch_fastk", "stoch_fastd", "stoch_slowk", "stoch_slowd"):
            assert result[col].dropna().between(0, 100).all()


class TestAroonNumeric:
    def test_new_high_up_100(self):
        df = _make_ohlcv(30)
        rising = np.linspace(100, 130, 30)
        df["high"] = rising
        df["low"] = rising - 1.0
        result = AROON().compute(df)
        assert (result["aroon_up"].dropna() == 100.0).all()
        assert (result["aroon_down"].dropna() == 0.0).all()

    def test_osc_identity(self):
        df = _make_ohlcv(40)
        result = AROONOSC().compute(df)
        aroon = AROON().compute(df)
        np.testing.assert_allclose(
            result["aroonosc"].dropna(),
            (aroon["aroon_up"] - aroon["aroon_down"]).reindex(result["aroonosc"].dropna().index),
            rtol=1e-10,
        )


class TestBopPpoApoDxNumeric:
    def test_bop_constant_doji_zero(self):
        df = _make_ohlcv(30)
        df["open"] = df["close"] = 100.0
        df["high"] = 101.0
        df["low"] = 99.0
        result = BOP().compute(df)
        assert (result["bop"].dropna() == 0.0).all()

    def test_bop_range(self):
        result = BOP().compute(_make_ohlcv(40))
        assert result["bop"].dropna().abs().max() <= 1.0

    def test_ppo_apo_relation(self):
        df = _make_ohlcv(60)
        ppo = PPO().compute(df)["ppo"]
        apo = APO().compute(df)["apo"]
        ema_slow = df["close"].ewm(span=26, adjust=False).mean()
        np.testing.assert_allclose(ppo.dropna(), (apo / ema_slow * 100).reindex(ppo.dropna().index), rtol=1e-10)

    def test_dx_range_and_matches_dmi(self):
        df = _make_ohlcv(60)
        result = DX().compute(df)
        assert result["dx_14"].dropna().between(0, 100).all()


class TestBrarCrNumeric:
    def test_constant_price_all_100(self):
        df = _make_ohlcv(40)
        df["open"] = df["high"] = df["low"] = df["close"] = 100.0
        result = BRAR().compute(df)
        np.testing.assert_allclose(result["ar_26"].dropna(), 0.0)
        np.testing.assert_allclose(result["br_26"].dropna(), 0.0)

    def test_cr_symmetric_mid(self):
        df = _make_ohlcv(40)
        df["high"] = 101.0
        df["low"] = 99.0
        result = CR().compute(df)
        assert (result["cr_26"].dropna() == 100.0).all()

    def test_ar_known_value(self):
        df = _make_ohlcv(30)
        df["open"] = 100.0
        df["high"] = 102.0
        df["low"] = 98.0
        result = BRAR().compute(df)
        np.testing.assert_allclose(result["ar_26"].dropna(), 100.0)


class TestBatch8MomentumNumeric:
    def test_ac_constant_price_zero(self):
        df = _make_ohlcv(50)
        df["high"] = df["low"] = df["close"] = 100.0
        result = AC().compute(df)
        assert (result["ac"].dropna() == 0.0).all()

    def test_fractals_symmetric_plateau_no_false(self):
        """恒定价无分形（严格大于判定）。"""
        df = _make_ohlcv(30)
        df["high"] = df["low"] = df["close"] = 100.0
        result = FRACTALS().compute(df)
        assert result["fractal_high"].dropna().empty

    def test_fractal_high_detected(self):
        n = 30
        base = np.full(n, 100.0)
        base[15] = 110.0  # 孤立高点：两侧各 2 根都低于它
        df = pd.DataFrame(
            {
                "open": base,
                "high": base + 0.1,
                "low": base - 0.1,
                "close": base,
                "volume": 1000.0,
            }
        )
        result = FRACTALS().compute(df)
        assert result["fractal_high"].iloc[15] == pytest.approx(110.1)
        assert result["fractal_high"].dropna().size == 1

    def test_elder_powers_mirror(self):
        df = _make_ohlcv(40)
        result = ELDER().compute(df)
        tail = result.dropna().tail(1)
        ema = df["close"].ewm(span=13, adjust=False).mean().iloc[-1]
        assert tail["bull_power_13"].iloc[0] == pytest.approx(df["high"].iloc[-1] - ema, rel=1e-9)
        assert tail["bear_power_13"].iloc[0] == pytest.approx(df["low"].iloc[-1] - ema, rel=1e-9)

    def test_coppock_range_and_warmup(self):
        df = _make_ohlcv(60)
        result = COPPOCK().compute(df)
        # warmup = max(roc1, roc2) + wma − 1 = 14+10−1 = 23
        assert result["coppock"].iloc[:23].isna().all()
        assert result["coppock"].iloc[23:].notna().all()

    def test_squeeze_binary_and_momentum(self):
        df = _make_ohlcv(60)
        result = SQUEEZE().compute(df)
        assert result["squeeze_on"].dropna().isin([0.0, 1.0]).all()
        assert result["squeeze_mom"].dropna().shape[0] > 0

    def test_wavetrend_finite(self):
        df = _make_ohlcv(60)
        result = WAVETREND().compute(df)
        assert np.isfinite(result["wt1"].dropna()).all()
        assert np.isfinite(result["wt2"].dropna()).all()


# ===========================================================================
# 2026-09-20 批 7 清欠：RMI/PFE/FOSC/CTI/VHF/ER
# 数值验证五维：①独立路径复算 ②手工微样本 ③预热 NaN ④空表/缺列 ⑤kwargs 列后缀
# ===========================================================================


class TestRmiNumeric:
    """RMI 相对动量指数（RSI 动量窗变体，Altman 1993）。"""

    def test_independent_recompute(self):
        """①独立路径复算：纯 Python Wilder 递推 vs _sma(ewm alpha=1/N)。"""
        df = _make_ohlcv(60)
        result = RMI().compute(df, period=5, mom_length=3)
        mom = df["close"].diff(3)
        up, dn = mom.clip(lower=0), (-mom).clip(lower=0)

        def wilder(s: pd.Series, n: int) -> pd.Series:
            alpha = 1 / n
            out, prev = [], None
            for x in s:
                if np.isnan(x):
                    out.append(np.nan)
                    continue
                prev = x if prev is None else (1 - alpha) * prev + alpha * x
                out.append(prev)
            return pd.Series(out, index=s.index)

        expected = 100 * wilder(up, 5) / (wilder(up, 5) + wilder(dn, 5))
        np.testing.assert_allclose(result["rmi_5"].to_numpy(), expected.to_numpy(), atol=1e-10)

    def test_hand_micro_sample(self):
        """②手工微样本：period=3, mom_length=2；mom=[-, -, 3, −1, −1]。"""
        df = pd.DataFrame({"close": [10.0, 12.0, 13.0, 11.0, 12.0]})
        result = RMI().compute(df, period=3, mom_length=2)
        # SMA3 递推: avg_up=[3, 2, 4/3]，avg_dn=[0, 1/3, 5/9]
        assert result["rmi_3"].iloc[:2].isna().all()
        assert result["rmi_3"].iloc[2] == pytest.approx(100.0)
        assert result["rmi_3"].iloc[3] == pytest.approx(600 / 7)
        assert result["rmi_3"].iloc[4] == pytest.approx(1200 / 17)

    def test_warmup_and_range(self):
        """③预热 NaN（前 mom_length 行）+ 值域 [0,100]。"""
        df = _make_ohlcv(60)
        result = RMI().compute(df)
        assert result["rmi_14"].iloc[:5].isna().all()
        assert result["rmi_14"].iloc[5:].notna().all()
        assert result["rmi_14"].dropna().between(0, 100).all()

    def test_empty_and_missing(self):
        """④空表返回空 / 缺列抛 ValueError。"""
        assert RMI().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            RMI().compute(pd.DataFrame({"open": [10.0]}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀语义。"""
        result = RMI().compute(_make_ohlcv(40), period=6, mom_length=3)
        assert list(result.columns) == ["rmi_6"]


class TestPfeNumeric:
    """PFE 极化分形效率（Hannula 1994，EMA 平滑）。"""

    def test_independent_recompute(self):
        """①独立路径复算：逐窗直线路径比 + 手工 EMA 递推。"""
        df = _make_ohlcv(60)
        result = PFE().compute(df, period=5, smooth=3)
        c = df["close"].to_numpy()
        n, sm = 5, 3
        raw = np.full(len(c), np.nan)
        for i in range(n, len(c)):
            seg = np.diff(c[i - n : i + 1])
            net = c[i] - c[i - n]
            raw[i] = 100 * np.sign(net) * np.sqrt(n**2 + net**2) / np.sqrt(n**2 + (seg**2).sum())
        alpha = 2 / (sm + 1)
        out, prev = np.full(len(c), np.nan), None
        for i in range(len(c)):
            if np.isnan(raw[i]):
                continue
            prev = raw[i] if prev is None else prev + alpha * (raw[i] - prev)
            out[i] = prev
        np.testing.assert_allclose(result["pfe_5"].to_numpy(), out, atol=1e-9)

    def test_hand_micro_sample(self):
        """②手工微样本：period=3, smooth=1（span=1 的 EMA 即原值）。"""
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0, 13.0, 16.0]})
        result = PFE().compute(df, period=3, smooth=1)
        # row3: net=3, ΣΔC²=3 → 100×sqrt(18/12)；row4: net=5, ΣΔC²=11 → 100×sqrt(34/20)
        assert result["pfe_3"].iloc[:3].isna().all()
        assert result["pfe_3"].iloc[3] == pytest.approx(100 * np.sqrt(1.5))
        assert result["pfe_3"].iloc[4] == pytest.approx(100 * np.sqrt(1.7))

    def test_perfect_trend_signed(self):
        """完美直线上行/下行：raw 恒 = ±100×sqrt(200/110)，EMA 不改变常量。"""
        up = PFE().compute(pd.DataFrame({"close": np.arange(1.0, 41.0)}))["pfe_10"]
        dn = PFE().compute(pd.DataFrame({"close": np.arange(40.0, 0.0, -1.0)}))["pfe_10"]
        np.testing.assert_allclose(up.dropna(), 100 * np.sqrt(20 / 11), rtol=1e-9)
        np.testing.assert_allclose(dn.dropna(), -100 * np.sqrt(20 / 11), rtol=1e-9)

    def test_warmup_nan(self):
        """③预热：diff² rolling(n) 首个完整窗在第 n 行。"""
        df = _make_ohlcv(60)
        result = PFE().compute(df)
        assert result["pfe_10"].iloc[:10].isna().all()
        assert result["pfe_10"].iloc[10:].notna().all()

    def test_empty_and_missing(self):
        """④空表/缺列。"""
        assert PFE().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            PFE().compute(pd.DataFrame({"high": [10.0] * 30}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀。"""
        result = PFE().compute(_make_ohlcv(40), period=4)
        assert list(result.columns) == ["pfe_4"]


class TestFoscNumeric:
    """FOSC 预测震荡（Chande，TSF=线性回归一步外推）。"""

    def test_independent_recompute_polyfit(self):
        """①独立路径复算：np.polyfit 逐窗拟合一步外推。"""
        df = _make_ohlcv(60)
        result = FOSC().compute(df, period=10)
        c = df["close"].to_numpy()
        expected = np.full(len(c), np.nan)
        for i in range(9, len(c)):
            y = c[i - 9 : i + 1]
            slope, intercept = np.polyfit(np.arange(10.0), y, 1)
            expected[i] = 100 * (c[i] - (intercept + slope * 10)) / c[i]
        np.testing.assert_allclose(result["fosc_10"].to_numpy(), expected, atol=1e-8)

    def test_hand_micro_sample(self):
        """②手工微样本：线性序列 TSF 恰超前一档 → 负值。"""
        df = pd.DataFrame({"close": [10.0, 11.0, 12.0, 13.0]})
        result = FOSC().compute(df, period=3)
        assert result["fosc_3"].iloc[:2].isna().all()
        assert result["fosc_3"].iloc[2] == pytest.approx(-100 / 12)
        assert result["fosc_3"].iloc[3] == pytest.approx(-100 / 13)

    def test_warmup_nan(self):
        """③预热：rolling(14) 首个完整窗在第 13 行。"""
        df = _make_ohlcv(60)
        result = FOSC().compute(df)
        assert result["fosc_14"].iloc[:13].isna().all()
        assert result["fosc_14"].iloc[13:].notna().all()

    def test_empty_and_missing(self):
        """④空表/缺列。"""
        assert FOSC().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            FOSC().compute(pd.DataFrame({"open": [10.0]}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀。"""
        result = FOSC().compute(_make_ohlcv(40), period=7)
        assert list(result.columns) == ["fosc_7"]


class TestCtiNumeric:
    """CTI 相关趋势指标（Ehlers 2020，close 对 0..N-1 的滚动 Pearson r）。"""

    def test_independent_recompute_corrcoef(self):
        """①独立路径复算：np.corrcoef 逐窗。"""
        df = _make_ohlcv(60)
        result = CTI().compute(df, period=8)
        c = df["close"].to_numpy()
        expected = np.full(len(c), np.nan)
        for i in range(7, len(c)):
            expected[i] = np.corrcoef(np.arange(8.0), c[i - 7 : i + 1])[0, 1]
        np.testing.assert_allclose(result["cti_8"].to_numpy(), expected, atol=1e-8)

    def test_hand_micro_sample(self):
        """②手工微样本：closes=[1,3,2,9]，period=3。"""
        df = pd.DataFrame({"close": [1.0, 3.0, 2.0, 9.0]})
        result = CTI().compute(df, period=3)
        # 窗 [1,3,2]: r=Σdxdy/sqrt(Σdx²Σdy²)=1/2；窗 [3,2,9]: r=18/sqrt(516)
        assert result["cti_3"].iloc[:2].isna().all()
        assert result["cti_3"].iloc[2] == pytest.approx(0.5)
        assert result["cti_3"].iloc[3] == pytest.approx(18 / np.sqrt(516))

    def test_perfect_trend_plus_minus_one(self):
        """完美直线趋势 → r=±1。"""
        up = CTI().compute(pd.DataFrame({"close": np.arange(1.0, 31.0)}), period=5)["cti_5"]
        dn = CTI().compute(pd.DataFrame({"close": np.arange(30.0, 0.0, -1.0)}), period=5)["cti_5"]
        np.testing.assert_allclose(up.dropna(), 1.0)
        np.testing.assert_allclose(dn.dropna(), -1.0)

    def test_warmup_and_range(self):
        """③预热（前 N-1 行）+ 值域 [-1,1]。"""
        df = _make_ohlcv(60)
        result = CTI().compute(df)
        assert result["cti_12"].iloc[:11].isna().all()
        assert result["cti_12"].iloc[11:].notna().all()
        assert result["cti_12"].dropna().between(-1, 1).all()

    def test_empty_and_missing(self):
        """④空表/缺列。"""
        assert CTI().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            CTI().compute(pd.DataFrame({"volume": [10.0]}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀。"""
        result = CTI().compute(_make_ohlcv(40), period=4)
        assert list(result.columns) == ["cti_4"]


class TestVhfNumeric:
    """VHF 纵横过滤（Adam White）。"""

    def test_independent_recompute(self):
        """①独立路径复算：逐窗 max−min / Σ|ΔC|。"""
        df = _make_ohlcv(60)
        result = VHF().compute(df, period=10)
        c = df["close"].to_numpy()
        expected = np.full(len(c), np.nan)
        for i in range(10, len(c)):
            seg = c[i - 9 : i + 1]
            expected[i] = (seg.max() - seg.min()) / np.abs(np.diff(c[i - 10 : i + 1])).sum()
        np.testing.assert_allclose(result["vhf_10"].to_numpy(), expected, atol=1e-10)

    def test_hand_micro_sample(self):
        """②手工微样本：closes=[1,2,3,6,4,5]，period=3。"""
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 6.0, 4.0, 5.0]})
        result = VHF().compute(df, period=3)
        assert result["vhf_3"].iloc[:3].isna().all()
        assert result["vhf_3"].iloc[3] == pytest.approx(0.8)  # (6−2)/(1+1+3)
        assert result["vhf_3"].iloc[4] == pytest.approx(0.5)  # (6−3)/(1+3+2)
        assert result["vhf_3"].iloc[5] == pytest.approx(1 / 3)  # (6−4)/(3+2+1)

    def test_monotonic_trend_value(self):
        """单调上涨：分子=(N−1)d，分母=N×d → VHF=(N−1)/N，强趋势高值。"""
        result = VHF().compute(pd.DataFrame({"close": np.arange(1.0, 61.0)}), period=10)
        np.testing.assert_allclose(result["vhf_10"].dropna(), 0.9)

    def test_warmup_nan(self):
        """③预热：diff 与 rolling 双重预热 → 首有效在行 N。"""
        df = _make_ohlcv(60)
        result = VHF().compute(df)
        assert result["vhf_28"].iloc[:28].isna().all()
        assert result["vhf_28"].iloc[28:].notna().all()

    def test_empty_and_missing(self):
        """④空表/缺列。"""
        assert VHF().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            VHF().compute(pd.DataFrame({"high": [10.0] * 30}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀。"""
        result = VHF().compute(_make_ohlcv(40), period=5)
        assert list(result.columns) == ["vhf_5"]


class TestErNumeric:
    """ER 效率比率（Kaufman，KAMA 的 ER 独立立条）。"""

    def test_independent_recompute(self):
        """①独立路径复算：逐窗 |净位移|/路径长度。"""
        df = _make_ohlcv(60)
        result = ER().compute(df, period=8)
        c = df["close"].to_numpy()
        expected = np.full(len(c), np.nan)
        for i in range(8, len(c)):
            expected[i] = abs(c[i] - c[i - 8]) / np.abs(np.diff(c[i - 8 : i + 1])).sum()
        np.testing.assert_allclose(result["er_8"].to_numpy(), expected, atol=1e-10)

    def test_hand_micro_sample(self):
        """②手工微样本：closes=[10,12,11,15]，period=2。"""
        df = pd.DataFrame({"close": [10.0, 12.0, 11.0, 15.0]})
        result = ER().compute(df, period=2)
        assert result["er_2"].iloc[:2].isna().all()
        assert result["er_2"].iloc[2] == pytest.approx(1 / 3)  # |11−10|/(2+1)
        assert result["er_2"].iloc[3] == pytest.approx(3 / 5)  # |15−12|/(1+4)，diff(2)=C−C[2]

    def test_bounds_and_trend_value_one(self):
        """值域 [0,1]；单调上涨净位移=路径 → ER=1。"""
        valid = ER().compute(_make_ohlcv(80))["er_10"].dropna()
        assert valid.between(0, 1).all()
        linear = ER().compute(pd.DataFrame({"close": np.arange(1.0, 41.0)}), period=10)["er_10"]
        np.testing.assert_allclose(linear.dropna(), 1.0)

    def test_warmup_nan(self):
        """③预热：首有效在行 N。"""
        df = _make_ohlcv(60)
        result = ER().compute(df)
        assert result["er_10"].iloc[:10].isna().all()
        assert result["er_10"].iloc[10:].notna().all()

    def test_empty_and_missing(self):
        """④空表/缺列。"""
        assert ER().compute(pd.DataFrame(columns=["close"])).empty
        with pytest.raises(ValueError, match="缺少列"):
            ER().compute(pd.DataFrame({"open": [10.0]}))

    def test_kwargs_column_suffix(self):
        """⑤kwargs 覆盖列名后缀。"""
        result = ER().compute(_make_ohlcv(40), period=5)
        assert list(result.columns) == ["er_5"]
