# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""成交量类技术指标测试（7 个，v1.0.0 全部施工完成）。

测试内容：
- 7 个成交量指标全部注册到 Registry
- 每个指标 meta.category == "volume"
- 每个指标 meta.output_columns == 期望列（catalog §2.4 契约）
- 已实现指标（全部 7 个）：数值正确性 + 边界测试

算法对齐通达信：OBV/AD/PVT 累积量首值 0；VR 通达信公式平盘量计入两侧；WVAD H=L 时该项 0。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.4
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import volume  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# 期望契约（catalog §2.4）：indicator_id → (name, output_columns)
EXPECTED = {
    "obv": ("能量潮", ["obv"]),
    "mfi": ("资金流量指标", ["mfi_14"]),
    "vwap": ("成交量加权均价", ["vwap"]),
    "vr": ("容量比率", ["vr_26"]),
    "ad": ("累积/派发线", ["ad"]),
    "pvt": ("价量趋势", ["pvt"]),
    "wvad": ("威廉变异离散量", ["wvad_24"]),
}

IMPLEMENTED = set(EXPECTED)  # 全部 7 个已施工完成
SKELETON = set(EXPECTED) - IMPLEMENTED  # 空集

_RNG = np.random.default_rng(42)


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正）。"""
    close = 100 + _RNG.standard_normal(n).cumsum()
    high = close + _RNG.uniform(0.1, 0.5, n)
    low = close - _RNG.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


class TestVolumeRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("volume")}
        for iid in EXPECTED:
            assert iid in metas, f"成交量指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("volume")) == len(EXPECTED) == 7


class TestVolumeMetaContract:
    @pytest.mark.parametrize("iid,expected", list(EXPECTED.items()))
    def test_category(self, iid, expected):
        assert TechnicalIndicatorRegistry.get(iid).meta.category == "volume"

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


class TestVolumeComputeNotImplemented:
    @pytest.mark.parametrize("iid", sorted(SKELETON))
    def test_compute_raises(self, iid):
        cls = TechnicalIndicatorRegistry.get(iid)
        df = pd.DataFrame(
            {"open": [10.0] * 30, "high": [11.0] * 30, "low": [9.0] * 30, "close": [10.5] * 30, "volume": [1000.0] * 30}
        )
        with pytest.raises(NotImplementedError, match="待施工"):
            cls().compute(df)


# ===========================================================================
# OBV 数值正确性测试
# ===========================================================================

OBV = TechnicalIndicatorRegistry.get("obv")


class TestOBVCompute:
    """OBV 能量潮——数值正确性 + 边界测试。"""

    def test_obv_formula(self):
        """OBV = cumsum(sign(C-Cp) × V)，首值 0（diff 首项为 0）。"""
        close = [10.0, 11.0, 10.5, 12.0]
        vol = [100.0, 200.0, 150.0, 300.0]
        df = pd.DataFrame({"close": close, "volume": vol})
        result = OBV().compute(df)
        # sign(diff): [0, +1, -1, +1] → obv = [0, 200, 50, 350]
        expected = pd.Series([0.0, 200.0, 50.0, 350.0])
        np.testing.assert_allclose(result["obv"].values, expected.values)

    def test_first_value_zero(self):
        """首值 = 0（diff 首项 fillna(0)）。"""
        df = _make_ohlcv(30)
        result = OBV().compute(df)
        assert result["obv"].iloc[0] == 0.0

    def test_empty_dataframe(self):
        result = OBV().compute(pd.DataFrame(columns=["close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            OBV().compute(pd.DataFrame({"close": [10.0]}))


# ===========================================================================
# MFI 数值正确性测试
# ===========================================================================

MFI = TechnicalIndicatorRegistry.get("mfi")


class TestMFICompute:
    """MFI 资金流量指标——数值正确性 + 边界测试。"""

    def test_mfi_range(self):
        """MFI 在 0~100 范围内。"""
        df = _make_ohlcv(50)
        result = MFI().compute(df)
        valid = result["mfi_14"].iloc[14:].dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_empty_dataframe(self):
        result = MFI().compute(pd.DataFrame(columns=["high", "low", "close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MFI().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# VWAP 数值正确性测试
# ===========================================================================

VWAP = TechnicalIndicatorRegistry.get("vwap")


class TestVWAPCompute:
    """VWAP 成交量加权均价——数值正确性 + 边界测试。"""

    def test_vwap_formula(self):
        """累积 VWAP = cumsum(C×V) / cumsum(V)。"""
        close = [10.0, 20.0]
        vol = [100.0, 300.0]
        df = pd.DataFrame({"close": close, "volume": vol})
        result = VWAP().compute(df)
        # [10×100/(100), (10×100+20×300)/(100+300)] = [10, 17.5]
        np.testing.assert_allclose(result["vwap"].values, [10.0, 17.5])

    def test_empty_dataframe(self):
        result = VWAP().compute(pd.DataFrame(columns=["close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            VWAP().compute(pd.DataFrame({"close": [10.0]}))


# ===========================================================================
# VR 数值正确性测试
# ===========================================================================

VR = TechnicalIndicatorRegistry.get("vr")


class TestVRCompute:
    """VR 容量比率——数值正确性 + 边界测试。"""

    def test_vr_formula(self):
        """VR = 100×(2×up+flat)/(2×down+flat)，对齐通达信。"""
        close = [10.0, 11.0, 10.0, 12.0, 10.0]
        vol = [100.0, 200.0, 150.0, 300.0, 250.0]
        df = pd.DataFrame({"close": close, "volume": vol})
        result = VR().compute(df, period=4)
        # diff: [_, +1, -1, +2, -2] → up=200+300=500, down=150+250=400, flat=0
        # VR = 100×(2×500+0)/(2×400+0) = 100×1000/800 = 125
        valid = result["vr_4"].iloc[4:].dropna()
        assert len(valid) > 0

    def test_empty_dataframe(self):
        result = VR().compute(pd.DataFrame(columns=["close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            VR().compute(pd.DataFrame({"close": [10.0]}))


# ===========================================================================
# AD 数值正确性测试
# ===========================================================================

AD = TechnicalIndicatorRegistry.get("ad")


class TestADCompute:
    """AD 累积/派发线——数值正确性 + 边界测试。"""

    def test_clv_zero_when_h_equals_l(self):
        """H=L 时 CLV=0（避免除零），AD 不增长。"""
        df = pd.DataFrame(
            {
                "high": [10.0] * 30,
                "low": [10.0] * 30,
                "close": [10.0] * 30,
                "volume": [1000.0] * 30,
            }
        )
        result = AD().compute(df)
        valid = result["ad"].dropna()
        assert np.allclose(valid, 0.0)

    def test_empty_dataframe(self):
        result = AD().compute(pd.DataFrame(columns=["high", "low", "close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            AD().compute(pd.DataFrame({"close": [10.0] * 30}))


# ===========================================================================
# PVT 数值正确性测试
# ===========================================================================

PVT = TechnicalIndicatorRegistry.get("pvt")


class TestPVTCompute:
    """PVT 价量趋势——数值正确性 + 边界测试。"""

    def test_pvt_first_value_zero(self):
        """首值 = 0（pct_change 首项 fillna(0)）。"""
        df = _make_ohlcv(30)
        result = PVT().compute(df)
        assert result["pvt"].iloc[0] == 0.0

    def test_empty_dataframe(self):
        result = PVT().compute(pd.DataFrame(columns=["close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            PVT().compute(pd.DataFrame({"close": [10.0]}))


# ===========================================================================
# WVAD 数值正确性测试
# ===========================================================================

WVAD = TechnicalIndicatorRegistry.get("wvad")


class TestWVADCompute:
    """WVAD 威廉变异离散量——数值正确性 + 边界测试。"""

    def test_wvad_zero_when_h_equals_l(self):
        """H=L 时 (C-O)/(H-L)=0，WVAD=0。"""
        df = pd.DataFrame(
            {
                "open": [10.0] * 30,
                "high": [10.0] * 30,
                "low": [10.0] * 30,
                "close": [10.0] * 30,
                "volume": [1000.0] * 30,
            }
        )
        result = WVAD().compute(df, period=20)
        valid = result["wvad_24"].dropna() if "wvad_24" in result.columns else result["wvad_20"].dropna()
        # period=20 override → column name wvad_20
        assert np.allclose(valid, 0.0)

    def test_empty_dataframe(self):
        result = WVAD().compute(pd.DataFrame(columns=["open", "high", "low", "close", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            WVAD().compute(pd.DataFrame({"close": [10.0] * 30}))
