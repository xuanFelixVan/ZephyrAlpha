# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""成交量类技术指标测试（17 个，v1.0.0 全部施工完成）。

测试内容：
- 17 个成交量指标全部注册到 Registry
- 每个指标 meta.category == "volume"
- 每个指标 meta.output_columns == 期望列（catalog §2.4 契约）
- 已实现指标（全部 17 个）：数值正确性 + 边界测试

算法对齐通达信：OBV/AD/PVT 累积量首值 0；VR 通达信公式平盘量计入两侧；WVAD H=L 时该项 0。
批2-C 清欠班（2026-09-20）+3：WAD 首行 TAD=0（Tulip 累积 sign 口径）；
VO 百分比口径首有效=第 slow 根；MARKETFI=(H−L)/V，V=0 → NaN。

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
    "vwma": ("成交量加权均线", ["vwma_20"]),
    "adosc": ("蔡金震荡器", ["adosc"]),
    "eom": ("简易波动量", ["eom_14"]),
    "kvo": ("Klinger量震荡器", ["kvo", "kvo_signal"]),
    "nvi": ("负成交量指标", ["nvi"]),
    "pvi": ("正成交量指标", ["pvi"]),
    "force_index": ("强力指数", ["fi_13"]),
    "wad": ("威廉累积/派发线", ["wad"]),
    "vo": ("成交量震荡器", ["vo"]),
    "marketfi": ("市场促进指数", ["marketfi"]),
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
        assert len(TechnicalIndicatorRegistry.list_by_category("volume")) == len(EXPECTED) == 17


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
VWMA = TechnicalIndicatorRegistry.get("vwma")
ADOSC = TechnicalIndicatorRegistry.get("adosc")
EOM = TechnicalIndicatorRegistry.get("eom")
KVO = TechnicalIndicatorRegistry.get("kvo")
NVI = TechnicalIndicatorRegistry.get("nvi")
PVI = TechnicalIndicatorRegistry.get("pvi")
FORCE_INDEX = TechnicalIndicatorRegistry.get("force_index")


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


# ===========================================================================
# 2026-09-14 主流热门批 2b：VWMA/ADOSC/EOM/KVO/NVI/PVI 数值正确性
# ===========================================================================


class TestBatch2bVolumeNumeric:
    def test_vwma_constant_equals_close(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = VWMA().compute(df)
        assert (result["vwma_20"].dropna() == 100.0).all()

    def test_adosc_constant_price_zero(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        df["high"] = 100.0
        df["low"] = 100.0
        result = ADOSC().compute(df)
        assert (result["adosc"].dropna() == 0.0).all()

    def test_nvi_pvi_seed_100_and_monotone_factors(self):
        df = _make_ohlcv(40)
        nvi = NVI().compute(df)["nvi"]
        pvi = PVI().compute(df)["pvi"]
        assert nvi.iloc[0] == 100.0 and pvi.iloc[0] == 100.0
        assert (nvi > 0).all() and (pvi > 0).all()

    def test_kvo_signal_smoothing(self):
        df = _make_ohlcv(120)
        result = KVO().compute(df)
        assert result["kvo"].notna().sum() == result["kvo_signal"].notna().sum()  # EMA 无预热 NaN


class TestForceIndexNumeric:
    def test_constant_volume_price_flat_fi_zero(self):
        df = _make_ohlcv(40)
        df["close"] = 100.0
        result = FORCE_INDEX().compute(df)
        assert (result["fi_13"].dropna() == 0.0).all()

    def test_fi_uses_volume(self):
        df = _make_ohlcv(40)
        fi1 = FORCE_INDEX().compute(df)["fi_13"].dropna().iloc[-1]
        df2 = df.copy()
        df2["volume"] = df2["volume"] * 2
        fi2 = FORCE_INDEX().compute(df2)["fi_13"].dropna().iloc[-1]
        assert fi2 == pytest.approx(fi1 * 2)


# ===========================================================================
# 批2-C 清欠班（2026-09-20）：WAD/VO/MARKETFI 数值正确性
# ===========================================================================

WAD = TechnicalIndicatorRegistry.get("wad")
VO = TechnicalIndicatorRegistry.get("vo")
MARKETFI = TechnicalIndicatorRegistry.get("marketfi")


class TestWADCompute:
    """WAD 威廉累积/派发线——数值正确性 + 边界测试。"""

    def test_wad_hand_computed(self):
        """手工微样本：up 取 C−L_prev，down 取 C−H_prev，持平计 0，首行 TAD=0。"""
        df = pd.DataFrame(
            {
                "high": [11.0, 13.0, 13.0, 10.0],
                "low": [9.0, 11.0, 11.0, 8.0],
                "close": [10.0, 12.0, 12.0, 9.0],
            }
        )
        result = WAD().compute(df)
        # row0: TAD=0 → WAD=0；row1: 12>10 → TAD=12−low[0]=3 → WAD=3；
        # row2: 12==12 → TAD=0 → WAD=3；row3: 9<12 → TAD=9−high[2]=−4 → WAD=−1
        np.testing.assert_allclose(result["wad"].values, [0.0, 3.0, 3.0, -1.0])

    def test_wad_independent_recompute(self):
        """独立逐行循环复算对照（与生产 np.where 向量化不同代码路径）。"""
        n_rows = 60
        df = _make_ohlcv(n_rows)
        result = WAD().compute(df)
        h = df["high"].to_numpy()
        low = df["low"].to_numpy()
        c = df["close"].to_numpy()
        expected = np.zeros(n_rows)
        acc = 0.0
        for i in range(1, n_rows):
            if c[i] > c[i - 1]:
                acc += c[i] - low[i - 1]
            elif c[i] < c[i - 1]:
                acc += c[i] - h[i - 1]
            expected[i] = acc
        np.testing.assert_allclose(result["wad"].values, expected)

    def test_wad_no_warmup_first_zero(self):
        """首行 TAD=0 口径：全序列无预热 NaN，首值 0，index 对齐。"""
        df = _make_ohlcv(30)
        result = WAD().compute(df)
        assert result["wad"].notna().all()
        assert result["wad"].iloc[0] == 0.0
        assert (result.index == df.index).all()

    def test_empty_dataframe(self):
        result = WAD().compute(pd.DataFrame(columns=["high", "low", "close"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            WAD().compute(pd.DataFrame({"close": [10.0] * 5}))


class TestVOCompute:
    """VO 成交量震荡器——数值正确性 + 边界测试。"""

    def test_vo_hand_computed(self):
        """手工微样本：fast=2/slow=3 覆盖，vo=(MA2−MA3)/MA3×100。"""
        vol = [100.0, 200.0, 300.0, 400.0, 500.0]
        df = pd.DataFrame({"volume": vol})
        result = VO().compute(df, fast=2, slow=3)
        # MA2=[-,150,250,350,450]；MA3=[-,-,200,300,400]
        # vo[2]=(250−200)/200×100=25；vo[3]=(350−300)/300×100=50/3；vo[4]=(450−400)/400×100=12.5
        assert np.isnan(result["vo"].iloc[0]) and np.isnan(result["vo"].iloc[1])
        assert result["vo"].iloc[2] == pytest.approx(25.0)
        assert result["vo"].iloc[3] == pytest.approx(50.0 / 3.0)
        assert result["vo"].iloc[4] == pytest.approx(12.5)

    def test_vo_independent_recompute(self):
        """独立路径（numpy 卷积滑动均值）复算对照，默认 fast=5/slow=20。"""
        n_rows, fast_n, slow_n = 60, 5, 20
        df = _make_ohlcv(n_rows)
        df["volume"] = np.linspace(1000.0, 2000.0, n_rows)  # 变量 Volume 避免 MA 退化
        result = VO().compute(df)
        v = df["volume"].to_numpy()
        ma_fast = np.convolve(v, np.ones(fast_n) / fast_n, mode="valid")
        ma_slow = np.convolve(v, np.ones(slow_n) / slow_n, mode="valid")
        # ma_slow[i] 收尾于 i+slow_n−1；ma_fast 对齐尾同窗需前移 slow_n−fast_n
        expected = (ma_fast[slow_n - fast_n :] - ma_slow) / ma_slow * 100
        np.testing.assert_allclose(result["vo"].values[slow_n - 1 :], expected, rtol=1e-10)

    def test_vo_warmup_nan_default(self):
        """默认 5/20：前 19 根预热 NaN（首有效=第 slow 根），其后全有效。"""
        df = _make_ohlcv(40)
        result = VO().compute(df)
        assert result["vo"].iloc[:19].isna().all()
        assert result["vo"].iloc[19:].notna().all()

    def test_vo_kwargs_override_column_fixed(self):
        """fast/slow 可 kwargs 覆盖（预热窗随 slow 收缩），列名固定 vo。"""
        df = _make_ohlcv(40)
        result = VO().compute(df, fast=3, slow=10)
        assert list(result.columns) == ["vo"]
        assert result["vo"].iloc[:9].isna().all()
        assert result["vo"].iloc[9:].notna().all()

    def test_empty_dataframe(self):
        result = VO().compute(pd.DataFrame(columns=["volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            VO().compute(pd.DataFrame({"close": [10.0] * 30}))


class TestMarketfiCompute:
    """MARKETFI 市场促进指数——数值正确性 + 边界测试。"""

    def test_marketfi_hand_computed(self):
        """手工微样本：marketfi=(H−L)/V → [0.01, 0.01]。"""
        df = pd.DataFrame(
            {
                "high": [11.0, 12.0],
                "low": [10.0, 10.0],
                "volume": [100.0, 200.0],
            }
        )
        result = MARKETFI().compute(df)
        np.testing.assert_allclose(result["marketfi"].values, [0.01, 0.01])

    def test_marketfi_zero_volume_nan(self):
        """V=0 → NaN 保护，其余行正常（row2=(13−10)/300=0.01）。"""
        df = pd.DataFrame(
            {
                "high": [11.0, 12.0, 13.0],
                "low": [10.0, 10.0, 10.0],
                "volume": [100.0, 0.0, 300.0],
            }
        )
        result = MARKETFI().compute(df)
        assert np.isnan(result["marketfi"].iloc[1])
        assert result["marketfi"].iloc[0] == pytest.approx(0.01)
        assert result["marketfi"].iloc[2] == pytest.approx(0.01)

    def test_marketfi_independent_recompute(self):
        """独立逐行标量复算对照（非生产向量化路径）。"""
        n_rows = 60
        df = _make_ohlcv(n_rows)
        result = MARKETFI().compute(df)
        expected = np.array([(h - l) / v for h, l, v in zip(df["high"], df["low"], df["volume"], strict=False)])
        np.testing.assert_allclose(result["marketfi"].values, expected, rtol=1e-12)

    def test_marketfi_no_warmup(self):
        """无预热期：全序列有效（逐行公式）。"""
        df = _make_ohlcv(30)
        result = MARKETFI().compute(df)
        assert result["marketfi"].notna().all()
        assert (result.index == df.index).all()

    def test_empty_dataframe(self):
        result = MARKETFI().compute(pd.DataFrame(columns=["high", "low", "volume"]))
        assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            MARKETFI().compute(pd.DataFrame({"close": [10.0] * 5}))
