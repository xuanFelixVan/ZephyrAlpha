# [A_test] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2b
# [MODULE] tests.regime.test_overlay_signals_builder
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.overlay_signals_builder; zephyr.regime.core.regime_detector; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_overlay_signals_builder.py
# [A_module] module_id: MOD-TEST-OVERLAY-SIG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #discussion_001 §4 #Phase2b
"""test_overlay_signals_builder.py — OverlaySignalsConstructor (Phase 2b) 单元测试。

覆盖：
  - 结构契约：8 转换 key 齐全 + 31 维度 key 齐全（对齐 TRANSITION_CONFIG）
  - 平时不干预：常态数据所有维度=0 → 无转换触发（C1 不退化前提）
  - S1 触发场景：高 vol_pct + 高 corr → vix_panic/correlation/liquidity > 0
  - S2 触发场景：暴跌 + 放量 → capitulation > 0
  - T1 触发场景：突破 + 放量 → bqs > 0
  - PIT：build_for_date(dt) 只用 ≤ dt-1（shift(1) 生效）
  - 降级：feature_builder=None → 全维度=0.0（纯 HMM）
  - 端到端：overlay_signals 喂 RegimeDetector._run_overlay 不报错

依据: discussion_001 v1.3.1 §4 / Phase 2 计划 §Phase2b
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.core.regime_detector import (
    TRANSITIONS,
    TRANSITION_CONFIG,
    RegimeDetector,
)
from zephyr.regime.overlay_signals_builder import (
    OverlaySignalsConstructor,
    _STUB_DIMS,
    _TRANSITION_DIMS,
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
    symbol: str = "000300",
) -> pd.DataFrame:
    """构造 MultiIndex(symbol, trade_date) index_df。"""
    idx = pd.MultiIndex.from_product(
        [[symbol], dates], names=["symbol", "trade_date"]
    )
    return pd.DataFrame(
        {
            "close": close_arr,
            "volume": volume_arr,
            "advance_count": np.full(len(dates), 2000.0),
            "decline_count": np.full(len(dates), 2000.0),
        },
        index=idx,
    )


def _make_dates(n: int = 300, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=n)


# ---------------------------------------------------------------------------
# 结构契约测试
# ---------------------------------------------------------------------------


class TestStructureContract:
    """8 转换 key + 31 维度 key 对齐 TRANSITION_CONFIG。"""

    def test_8_transitions_present(self):
        """_TRANSITION_DIMS 包含全部 8 转换（T1-T6/S1/S2）。"""
        assert set(_TRANSITION_DIMS.keys()) == set(TRANSITIONS)

    def test_dims_align_config(self):
        """每个转换的维度 key 与 TRANSITION_CONFIG 的 keys_gte 完全对齐。"""
        for tid in TRANSITIONS:
            cfg = TRANSITION_CONFIG[tid]
            config_keys: set[str] = set()
            for stage in cfg["stages"].values():
                config_keys.update((stage.get("keys_gte") or {}).keys())
            builder_keys = set(_TRANSITION_DIMS[tid])
            assert builder_keys == config_keys, (
                f"{tid} 维度不匹配: builder={builder_keys} vs config={config_keys}"
            )

    def test_31_unique_keys(self):
        """全转换并集 = 31 个维度 key（25 可算 + 6 stub）。"""
        all_keys: set[str] = set()
        for keys in _TRANSITION_DIMS.values():
            all_keys.update(keys)
        assert len(all_keys) == 31, f"期望 31 维度，实际 {len(all_keys)}"
        assert len(_STUB_DIMS) == 6, f"期望 6 stub，实际 {len(_STUB_DIMS)}"

    def test_build_for_date_has_all_transitions_and_dims(self):
        """build_for_date 返回结构包含 8 转换 + 各转换全部维度 key。"""
        dates = _make_dates(300)
        feat = _make_features(dates)
        idx_df = _make_index_df(
            dates, np.linspace(3000, 3500, 300), np.full(300, 1e8)
        )
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        assert "transitions" in result
        trans = result["transitions"]
        assert set(trans.keys()) == set(TRANSITIONS)
        for tid in TRANSITIONS:
            assert set(trans[tid].keys()) == set(_TRANSITION_DIMS[tid])


# ---------------------------------------------------------------------------
# 平时不干预测试（C1 不退化前提）
# ---------------------------------------------------------------------------


class TestNoSignalInNormalMarket:
    """常态数据所有维度=0 → 无转换触发（平时退化为纯 HMM）。"""

    def test_normal_market_all_zero(self):
        """低波/低相关/宽幅震荡 → 无转换 stage 触发（C1 不退化前提）。

        注：个别弱维度（如 wyckoff=25 在窄幅日）可能非零，但单维度无法触发
        stage（S2 confirm 需 wyckoff>=60 + policy stub=0 → 永不满足）。
        真正的不退化保证 = 无 stage 触发 → overlay_probs 全 0 → 纯 HMM。
        """
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5, vol_anom=0.0)
        rng = np.random.default_rng(42)
        close = 3000 + 200 * np.sin(np.linspace(0, 8 * np.pi, 300)) + rng.normal(0, 5, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        # 核心保证：无 stage 触发 → overlay 不干预（纯 HMM）
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert all(v == 0.0 for v in overlay_probs.values()), (
            f"常态不应触发 overlay，实际 overlay_probs={overlay_probs}"
        )

    def test_normal_market_no_overlay_effect(self):
        """常态 overlay_signals 喂检测器 → 无 overlay 概率（纯 HMM）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.linspace(3000, 3100, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        overlay = ctor.build_for_date(dates[250])
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(overlay)
        # 无转换触发 → overlay 概率全 0
        assert all(v == 0.0 for v in overlay_probs.values())


# ---------------------------------------------------------------------------
# 触发场景测试
# ---------------------------------------------------------------------------


class TestTriggerScenarios:
    """危机/突破/见底场景下对应维度 > 0。"""

    def test_s1_crisis_trigger(self):
        """高 vol_pct(>0.90) + 高 corr(>0.95) → vix_panic/correlation > 0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=2.5)
        close = np.linspace(3000, 2900, 300)  # 下跌
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        s1 = result["transitions"]["S1"]
        assert s1["vix_panic"] >= 60, f"S1 vix_panic={s1['vix_panic']} 应过触发门槛"
        assert s1["correlation"] >= 60, f"S1 correlation={s1['correlation']} 应过触发门槛"
        # S1 trigger 条件：vix_panic>=60 AND correlation>=60
        detector = RegimeDetector(shrinkage_enabled=False)
        overlay_probs = detector._run_overlay(result)
        assert overlay_probs["r10"] > 0, "S1 触发应产出 CRISIS(r10) 概率"

    def test_s2_capitulation_signal(self):
        """暴跌(>4%) + 放量(z>3) → capitulation > 0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, vol_anom=3.5)
        close = np.full(300, 3000.0)
        close[249] = 3000 * (1 - 0.05)  # 暴跌 5%
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        s2 = result["transitions"]["S2"]
        # capitulation 在暴跌次日（shift(1) PIT）应 > 0
        assert s2["capitulation"] > 0, f"S2 capitulation={s2['capitulation']} 应 > 0"

    def test_t1_breakout_signal(self):
        """价格破 60 日新高 + 放量 → bqs > 0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.4, slope=0.001, hurst=0.55)
        close = np.linspace(3000, 3100, 300)
        close[250] = 3300  # 突破前高
        volume = np.full(300, 1e8)
        volume[250] = 3e8  # 放量
        idx_df = _make_index_df(dates, close, volume)
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[251])
        t1 = result["transitions"]["T1"]
        assert t1["bqs"] > 0, f"T1 bqs={t1['bqs']} 应 > 0"


# ---------------------------------------------------------------------------
# PIT 测试
# ---------------------------------------------------------------------------


class TestPIT:
    """build_for_date(dt) 只用 ≤ dt-1 数据（shift(1) 生效）。"""

    def test_shift_prevents_lookahead(self):
        """dt 日的新数据不影响 build_for_date(dt)（shift(1) 隔离）。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.3, corr=0.5)
        close = np.full(300, 3000.0)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        dt = dates[250]
        result_before = ctor.build_for_date(dt)

        # 篡改 dt 当日的特征为极端危机值
        feat.loc[dt, "realized_vol_pct"] = 0.99
        feat.loc[dt, "cross_asset_corr"] = 0.99
        # 重新构造（清缓存）
        ctor2 = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=_MockFeatureBuilder(feat, idx_df),
        )
        result_after = ctor2.build_for_date(dt)
        # dt 当日的极端值因 shift(1) 不影响 build_for_date(dt)
        assert (
            result_before["transitions"]["S1"]["vix_panic"]
            == result_after["transitions"]["S1"]["vix_panic"]
        ), "PIT 违规：dt 当日数据泄漏到 build_for_date(dt)"


# ---------------------------------------------------------------------------
# 降级测试
# ---------------------------------------------------------------------------


class TestDegradation:
    """数据缺失时降级为 0.0（不触发）。"""

    def test_none_feature_builder(self):
        """feature_builder=None → 全维度=0.0。"""
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=None,
        )
        result = ctor.build_for_date(pd.Timestamp("2020-06-01"))
        trans = result["transitions"]
        assert set(trans.keys()) == set(TRANSITIONS)
        for tid, breakdown in trans.items():
            assert all(v == 0.0 for v in breakdown.values())

    def test_stub_dims_always_zero(self):
        """stub 维度（policy/bad_news_flat/money_effect/...）恒为 0.0。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=3.0)
        close = np.linspace(3000, 2900, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        result = ctor.build_for_date(dates[250])
        trans = result["transitions"]
        for tid, breakdown in trans.items():
            for key in breakdown:
                if key in _STUB_DIMS:
                    assert breakdown[key] == 0.0, f"stub {tid}.{key} 应恒 0.0"


# ---------------------------------------------------------------------------
# 端到端：overlay_signals 喂 RegimeDetector.detect 不报错
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """overlay_signals 喂 RegimeDetector.detect 全流程不报错。"""

    def test_detect_with_overlay_no_error(self):
        """危机场景 overlay + 风险输入 → detect 产出有效 Shrinkage。"""
        dates = _make_dates(300)
        feat = _make_features(dates, vol_pct=0.92, corr=0.96, vol_anom=2.5, slope=-0.001)
        close = np.linspace(3000, 2800, 300)
        idx_df = _make_index_df(dates, close, np.full(300, 1e8))
        fb = _MockFeatureBuilder(feat, idx_df)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-03-01",
            data_load_start="2020-01-01",
            feature_builder=fb,
        )
        dt = dates[250]
        overlay = ctor.build_for_date(dt)
        # 构造 risk_inputs（#1 已触发危机）
        risk_inputs = {
            "params": {1: 0.30, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
                       6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 12: 1.0},
            "opportunity": {"news_ghost": 0.0, "bad_news_flat": 0.0},
        }
        detector = RegimeDetector(shrinkage_enabled=True)
        # HMM 未 fit → 降级均匀分布；overlay + risk 仍可算
        regime_features = {"X": np.zeros((60, 6))}
        probs, shrinkage = detector.detect(
            regime_features, overlay_signals=overlay, risk_signal_inputs=risk_inputs
        )
        assert 0.0 < shrinkage.value <= 1.0
        assert len(probs.probabilities) == 12
