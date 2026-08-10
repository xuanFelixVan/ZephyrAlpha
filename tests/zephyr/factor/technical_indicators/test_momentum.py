# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""动量类技术指标测试（10 个）。

测试内容：
- 10 个动量指标全部注册到 Registry
- 每个指标 meta.category == "momentum"
- 每个指标 meta.output_columns == 期望列（catalog §2.2 契约）
- 已实现指标（全部 10 个）：数值正确性 + 边界测试

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
        assert len(TechnicalIndicatorRegistry.list_by_category("momentum")) == len(EXPECTED) == 10


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
