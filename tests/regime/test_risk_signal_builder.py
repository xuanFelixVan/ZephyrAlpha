# [A_test] module_id: MOD-TEST-RISK-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5.3 Phase2a
# [MODULE] tests.regime.test_risk_signal_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.risk_signal_builder; zephyr.regime.core.regime_detector; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_risk_signal_builder.py
# [A_module] module_id: MOD-TEST-RISK-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #discussion_001 §5.3 #Phase2a #C1-shrinkage-comparator
"""test_risk_signal_builder.py — RiskSignalConstructor (Phase 2a) 单元测试。

覆盖：
  - 结构契约：13 参数 key 齐全（11 risk #1-10/#12 + 2 opportunity #11/#13 stub）
  - 平时不干预：常态低波 → #1=1.0 → RegimeDetector._compute_risk_signal=1.0（C1 不退化前提）
  - #1 门控（核心机制）：#1=1.0 时附加参数不参与；#1<1.0 时附加参数加深收缩
  - 危机触发：高波 + 下跌 → #1<1.0（realized_vol_coef 复刻 Phase 1 危机地板）
  - PIT：build_for_date(dt) 只用 ≤ dt-1（shift(1) 生效）
  - 降级：feature_builder=None → 全参数=1.0（保守不下调）
  - 端到端：risk_inputs 喂 RegimeDetector._compute_risk_signal 不报错

依据: discussion_001 v1.3.1 §5.3.3 / Phase 2 计划 §Phase2a
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.regime_detector import RegimeDetector
from zephyr.regime.risk_signal_builder import (
    _ACTIVE_PARAMS,
    _RISK_PARAM_IDS,
    RiskSignalConstructor,
)

# ---------------------------------------------------------------------------
# Mock feature_builder
# ---------------------------------------------------------------------------


class _MockFeatureBuilder:
    """最小化 mock，模拟 RegimeFeatureBuilder 的 build_features + get_index_kline。"""

    def __init__(self, features: pd.DataFrame, index_df: pd.DataFrame) -> None:
        self._features = features
        self._index_df = index_df

    def build_features(self) -> pd.DataFrame:
        return self._features

    def get_index_kline(self) -> pd.DataFrame:
        return self._index_df


def _make_features(
    dates: pd.DatetimeIndex,
    vol_pct: float = 0.3,
    hurst: float = 0.5,
    slope: float = 0.0,
    corr: float = 0.5,
    ad_ratio: float = 0.0,
    vol_anom: float = 0.0,
) -> pd.DataFrame:
    """构造 HMM 6 特征 DataFrame（常量填充，用于受控测试）。"""
    n = len(dates)
    return pd.DataFrame(
        {
            "realized_vol_pct": np.full(n, vol_pct),
            "hurst_dfa": np.full(n, hurst),
            "kalman_slope": np.full(n, slope),
            "cross_asset_corr": np.full(n, corr),
            "ad_ratio": np.full(n, ad_ratio),
            "volume_anomaly": np.full(n, vol_anom),
        },
        index=dates,
    )


def _make_index_df(
    dates: pd.DatetimeIndex,
    close_arr: np.ndarray,
    volume_arr: np.ndarray,
    high_arr: np.ndarray | None = None,
    low_arr: np.ndarray | None = None,
    symbol: str = "000300",
) -> pd.DataFrame:
    """构造 MultiIndex(symbol, trade_date) index_df。"""
    idx = pd.MultiIndex.from_product([[symbol], dates], names=["symbol", "trade_date"])
    data: dict[str, np.ndarray] = {
        "close": close_arr,
        "volume": volume_arr,
    }
    if high_arr is not None:
        data["high"] = high_arr
    if low_arr is not None:
        data["low"] = low_arr
    return pd.DataFrame(data, index=idx)


def _make_dates(n: int = 300, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=n)


# ---------------------------------------------------------------------------
# 结构契约测试
# ---------------------------------------------------------------------------


class TestStructureContract:
    """13 参数 key + active/stub 划分对齐设计。"""

    def test_risk_param_ids_complete(self):
        """_RISK_PARAM_IDS = [1..10, 12]（11 个风险参数，#11/#13 属 opportunity）。"""
        assert _RISK_PARAM_IDS == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]

    def test_active_params_count(self):
        """_ACTIVE_PARAMS = 9 个有效参数（#4/#12 stub=1.0；Phase 2c #8 升级为有效）。"""
        assert {1, 2, 3, 5, 6, 7, 8, 9, 10} == _ACTIVE_PARAMS
        assert len(_ACTIVE_PARAMS) == 9

    def test_build_for_date_has_all_params(self):
        """build_for_date 返回 params 含 11 个 id + opportunity 含 2 个 stub。"""
        dates = _make_dates(300)
        feat = _make_features(dates)
        idx_df = _make_index_df(dates, np.linspace(3000, 3500, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        assert "params" in result
        assert "opportunity" in result
        params = result["params"]
        # 11 个风险参数 id
        assert set(params.keys()) == set(_RISK_PARAM_IDS)
        # opportunity 2 个 stub
        opp = result["opportunity"]
        assert set(opp.keys()) == {"news_ghost", "bad_news_flat"}
        assert opp["news_ghost"] == 0.0
        assert opp["bad_news_flat"] == 0.0

    def test_all_params_in_valid_range(self):
        """所有参数系数 ∈ [0.30, 1.00]（INVARIANTS）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.95, slope=-0.5)  # 危机态
        idx_df = _make_index_df(dates, np.linspace(3500, 3000, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        for pid, coef in result["params"].items():
            assert 0.30 <= coef <= 1.00, f"参数 #{pid}={coef} 越界 [0.30, 1.00]"


# ---------------------------------------------------------------------------
# 平时不干预测试（C1 不退化前提）
# ---------------------------------------------------------------------------


class TestNormalMarketNoIntervention:
    """常态低波 → #1=1.0 → RegimeDetector._compute_risk_signal=1.0（纯 HMM）。"""

    def test_normal_market_primary_is_one(self):
        """低波常态（vol_pct<0.75）→ #1=1.0（realized_vol_coef 正常档）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, slope=0.0)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        assert result["params"][1] == 1.0, "常态 #1 应为 1.0（不干预）"

    def test_normal_market_risk_signal_is_one(self):
        """常态 → #1=1.0 → _compute_risk_signal=1.0（#1 门控，附加参数不参与）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, slope=0.0)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        risk_inputs = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        assert risk == 1.0, f"常态 RiskSignal 应=1.0（#1 门控），实际 {risk}"


# ---------------------------------------------------------------------------
# #1 门控测试（核心机制）
# ---------------------------------------------------------------------------


class TestPrimaryGating:
    """#1 门控：#1=1.0 时附加参数不参与；#1<1.0 时附加参数加深收缩。

    这是 Phase 2a 治本此前 Sharpe 0.2678→0.2464 退化的核心机制。
    """

    def test_primary_one_ignores_additional_params(self):
        """#1=1.0（非危机）时，即使附加参数 <1.0 也不参与 → RiskSignal=1.0。

        构造 #1=1.0 但 #6/#7 等 <1.0 的场景，验证 #1 门控屏蔽附加参数。
        """
        risk_inputs = {
            "params": {1: 1.0, 2: 0.5, 6: 0.4, 7: 0.3, 10: 0.6},  # #1=1.0 但附加<1.0
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        assert risk == 1.0, f"#1=1.0 时应屏蔽附加参数，RiskSignal=1.0，实际 {risk}"

    def test_primary_below_one_additional_deepens(self):
        """#1<1.0（危机）时，附加参数加深收缩（min(all) ≤ #1）。"""
        # 仅 #1=0.5 → RiskSignal = 0.5（无附加参数）
        risk_only_primary = {
            "params": {1: 0.5},
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        # #1=0.5 + 附加 #7=0.3 → RiskSignal = min(0.5, 0.3) = 0.3（加深）
        risk_with_additional = {
            "params": {1: 0.5, 7: 0.3},
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        r1 = detector._compute_risk_signal(risk_only_primary)
        r2 = detector._compute_risk_signal(risk_with_additional)
        assert r1 == pytest.approx(0.5, abs=1e-6), f"仅 #1=0.5 应得 0.5，实际 {r1}"
        # min(0.5, 0.3)=0.3，共振惩罚 anomaly_count=2 → 1-0.05*1=0.95 → 0.3*0.95=0.285
        # 但 RiskSignal 下限 0.30（max(0.30, ...)）→ 钳制为 0.30
        assert r2 < r1, f"附加参数应加深收缩（r2={r2} < r1={r1}）"
        assert r2 == pytest.approx(0.30, abs=1e-6), (
            f"#1=0.5+#7=0.3: min=0.3×共振0.95=0.285 被 0.30 下限钳制 → 0.30，实际 {r2}"
        )

    def test_opportunity_recovery_capped(self):
        """#11/#13 机会恢复上限 +0.25（不能把危机完全抵消）。"""
        risk_inputs = {
            "params": {1: 0.3, 7: 0.3},  # 深度危机
            "opportunity": {"news_ghost": 0.5, "bad_news_flat": 0.5},  # 超 0.25 上限
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        # min(0.3,0.3)=0.3, resonance=0.95, recovery=min(1.0,0.25)=0.25 → 0.3*0.95+0.25=0.535
        assert 0.30 <= risk <= 0.60, f"机会恢复后应∈[0.30,0.60]，实际 {risk}"

    def test_empty_risk_inputs_returns_one(self):
        """空 risk_inputs → 降级 1.0（保守不下调）。"""
        detector = RegimeDetector(shrinkage_enabled=True)
        assert detector._compute_risk_signal({}) == 1.0
        assert detector._compute_risk_signal(None) == 1.0
        assert detector._compute_risk_signal({"params": {}}) == 1.0


# ---------------------------------------------------------------------------
# 危机触发测试（#1 复刻 Phase 1 危机地板）
# ---------------------------------------------------------------------------


class TestCrisisTrigger:
    """高波 + 下跌 → #1<1.0（realized_vol_coef 复刻 Phase 1 _build_feature_risk）。"""

    @pytest.mark.parametrize(
        "vol_pct,slope,expected",
        [
            (0.95, -0.5, 0.30),  # 极端高波 + 暴跌 → 危机 0.30
            (0.95, 0.5, 0.60),  # 极端高波 + 未跌 → 0.60
            (0.80, -0.3, 0.50),  # 高波 + 下跌 → 偏危机 0.50
            (0.80, 0.3, 0.80),  # 高波 + 未跌 → 0.80
            (0.30, -0.5, 1.00),  # 低波（即使下跌）→ 正常 1.00
            (0.30, 0.3, 1.00),  # 低波 + 未跌 → 正常 1.00
        ],
    )
    def test_realized_vol_coef_mapping(self, vol_pct, slope, expected):
        """#1 realized_vol_coef 5 档映射与 Phase 1 _build_feature_risk 逐档对齐。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=vol_pct, slope=slope)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        assert result["params"][1] == pytest.approx(expected, abs=1e-6), (
            f"vol_pct={vol_pct}, slope={slope} → #1 应={expected}，实际 {result['params'][1]}"
        )

    def test_crisis_risk_signal_below_one(self):
        """危机态（高波+下跌）→ #1<1.0 → RiskSignal<1.0（收缩生效）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.95, slope=-0.5)
        idx_df = _make_index_df(dates, np.linspace(3500, 3000, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        risk_inputs = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        assert risk < 1.0, f"危机态 RiskSignal 应<1.0，实际 {risk}"
        assert risk >= 0.30, f"RiskSignal 下限 0.30，实际 {risk}"


# ---------------------------------------------------------------------------
# PIT 测试
# ---------------------------------------------------------------------------


class TestPIT:
    """build_for_date(dt) 只用 ≤ dt-1 数据（shift(1) 生效）。"""

    def test_pit_shift_one_effective(self):
        """dt 日的 #1 系数应来自 dt-1 的特征（shift(1)），而非 dt 当日。

        构造前半段低波、后半段危机的特征序列，验证边界日 dt 的 #1 取的是
        dt-1（低波→1.0）而非 dt（危机→0.3）。
        """
        n = 300
        dates = _make_dates(n)
        # 前 200 天低波，第 200 天起危机
        vol_pct = np.where(np.arange(n) < 200, 0.3, 0.95)
        slope = np.where(np.arange(n) < 200, 0.0, -0.5)
        feat = pd.DataFrame(
            {
                "realized_vol_pct": vol_pct,
                "hurst_dfa": np.full(n, 0.5),
                "kalman_slope": slope,
                "cross_asset_corr": np.full(n, 0.5),
                "ad_ratio": np.zeros(n),
                "volume_anomaly": np.zeros(n),
            },
            index=dates,
        )
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, n), np.full(n, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        # dt = 第 200 天（危机首日），shift(1) → #1 取第 199 天（低波→1.0）
        dt = dates[200]
        result = ctor.build_for_date(dt)
        assert result["params"][1] == 1.0, (
            f"PIT：dt={dt.date()} 的 #1 应取 dt-1（低波→1.0），"
            f"实际 {result['params'][1]}（若取 dt 当日危机→0.3 说明 shift(1) 失效）"
        )
        # dt = 第 201 天，shift(1) → #1 取第 200 天（危机→0.3）
        dt2 = dates[201]
        result2 = ctor.build_for_date(dt2)
        assert result2["params"][1] == 0.3, (
            f"PIT：dt={dt2.date()} 的 #1 应取 dt-1（危机→0.3），实际 {result2['params'][1]}"
        )


# ---------------------------------------------------------------------------
# 降级测试
# ---------------------------------------------------------------------------


class TestDegradation:
    """feature_builder=None / build_features 失败 → 全参数降级 1.0。"""

    def test_none_feature_builder_all_one(self):
        """feature_builder=None → 所有参数=1.0（保守不下调）。"""
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=None,
        )
        result = ctor.build_for_date(pd.Timestamp("2020-06-01"))
        for pid in _RISK_PARAM_IDS:
            assert result["params"][pid] == 1.0, (
                f"无 feature_builder 时 #{pid} 应降级 1.0，实际 {result['params'][pid]}"
            )

    def test_degraded_risk_signal_is_one(self):
        """降级场景 → RiskSignal=1.0（不误杀）。"""
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=None,
        )
        risk_inputs = ctor.build_for_date(pd.Timestamp("2020-06-01"))
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        # 全参数 1.0 → #1=1.0 → 门控返回 1.0
        assert risk == 1.0

    def test_build_features_failure_degrades(self):
        """build_features 抛异常 → 全参数降级 1.0（降级友好，不抛错）。"""

        class _BrokenBuilder:
            def build_features(self):
                raise RuntimeError("模拟 ClickHouse 不可用")

            def get_index_kline(self):
                return pd.DataFrame()

        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=_BrokenBuilder(),
        )
        result = ctor.build_for_date(pd.Timestamp("2020-06-01"))
        for pid in _RISK_PARAM_IDS:
            assert result["params"][pid] == 1.0


# ---------------------------------------------------------------------------
# 端到端测试
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """risk_inputs 喂 RegimeDetector._compute_risk_signal 不报错 + Shrinkage 链跑通。"""

    def test_full_shrinkage_chain_normal(self):
        """常态 → risk=1.0 → Shrinkage = confidence × 1.0 = confidence（不被风险压低）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, slope=0.0)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        risk_inputs = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        # Shrinkage 链：confidence × risk
        confidence = 0.85  # 模拟值
        shrinkage = detector._compute_shrinkage(confidence, risk)
        assert shrinkage.value == pytest.approx(confidence * risk, abs=1e-6)
        assert shrinkage.value <= 1.0

    def test_full_shrinkage_chain_crisis(self):
        """危机 → risk<1.0 → Shrinkage < confidence（风险节流生效）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.95, slope=-0.5)
        idx_df = _make_index_df(dates, np.linspace(3500, 3000, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        risk_inputs = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=True)
        risk = detector._compute_risk_signal(risk_inputs)
        assert risk < 1.0
        confidence = 0.85
        shrinkage = detector._compute_shrinkage(confidence, risk)
        assert shrinkage.value < confidence, "危机态 Shrinkage 应被风险压低"
        assert shrinkage.value >= 0.30 * confidence  # 风险下限 0.30 × confidence

    def test_caching_idempotent(self):
        """_precompute 缓存：多次 build_for_date 不重复计算（返回一致）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, slope=0.0)
        idx_df = _make_index_df(dates, np.linspace(3000, 3100, 300), np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = RiskSignalConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        r1 = ctor.build_for_date(dates[250])
        r2 = ctor.build_for_date(dates[250])
        assert r1 == r2, "缓存应保证同一 dt 多次调用结果一致"
        # 不同 dt 也可正常取（缓存命中）
        r3 = ctor.build_for_date(dates[200])
        assert set(r3["params"].keys()) == set(_RISK_PARAM_IDS)
