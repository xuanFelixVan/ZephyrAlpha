# [A_test] module_id: MOD-TEST-SYNTH-VIX | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2c
# [MODULE] tests.regime.test_synthetic_vix
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.market_features; zephyr.regime.overlay_signals_builder; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_synthetic_vix.py
# [A_module] module_id: MOD-TEST-SYNTH-VIX | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #Phase2c #P0-synthetic-vix
"""test_synthetic_vix.py — 合成 VIX（synthetic_vix_pct）单元测试。

覆盖（P0 验证目标）：
  - synthetic_vix_pct 函数行为：
      * 值域 ∈ [0, 1]
      * warmup 期 NaN（前 hv_window + pct_window 日）
      * 危机期（持续大跌）分位飙升 > 0.8
      * 牛市期（持续上涨）分位低
      * 与 realized_vol_pct 互补：高波非危机 vol_pct 高但 vix_pct 低
  - _compute_vix_pct 后备逻辑：
      * 期权 IV 缺失 → 回退合成 VIX（非空返回）
      * feature_builder=None 且期权缺失 → 返回 None
      * 注入 S1 vix_panic：危机期 vix_pct 使 s1_vix_panic_score 达 85（过门槛）

依据: 12_regime_phase2_validation §9 P0 / Phase 2 计划 §Phase2c
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.market_features import realized_vol_pct
from zephyr.regime.features.overlay_features import s1_vix_panic_score
from zephyr.regime.features.synthetic_vix import synthetic_vix_pct
from zephyr.regime.overlay_signals_builder import OverlaySignalsConstructor

# ---------------------------------------------------------------------------
# 测试数据构造
# ---------------------------------------------------------------------------


def _make_crisis_close(n: int = 600, seed: int = 42) -> pd.Series:
    """危机场景：前 350 日低波动平稳，后 250 日持续大跌。

    保证 warmup（20+250=270 日）之后，正常期与危机期都有足够非 NaN 样本对比。
    """
    rng = np.random.default_rng(seed)
    returns = np.concatenate(
        [
            rng.normal(0.0005, 0.005, 350),  # 平稳期：小正漂移，低波动
            rng.normal(-0.015, 0.010, 250),  # 危机期：持续大跌，高下行波动
        ]
    )
    close = 100.0 * np.exp(np.cumsum(returns))
    dates = pd.bdate_range("2018-01-01", periods=n)
    return pd.Series(close, index=dates, name="close")


def _make_crisis_then_rebound(n: int = 600, seed: int = 11) -> pd.Series:
    """危机 + 反弹场景：前 300 日持续大跌（高下行波动），后 300 日持续大涨
    （总波动相同但下行占比小）→ 反弹期 vix_pct 应明显低于 vol_pct（互补性）。"""
    rng = np.random.default_rng(seed)
    returns = np.concatenate(
        [
            rng.normal(-0.015, 0.012, 300),  # 危机：大跌，高下行波动
            rng.normal(0.015, 0.012, 300),  # 反弹：大涨，下行占比小但总波动相同
        ]
    )
    close = 100.0 * np.exp(np.cumsum(returns))
    dates = pd.bdate_range("2018-01-01", periods=n)
    return pd.Series(close, index=dates, name="close")


def _make_index_df(close: pd.Series, symbol: str = "000300") -> pd.DataFrame:
    """单标的 close → MultiIndex(symbol, trade_date) DataFrame。"""
    dates = close.index
    idx = pd.MultiIndex.from_product([[symbol], dates], names=["symbol", "trade_date"])
    return pd.DataFrame({"close": close.values, "volume": np.full(len(dates), 1e8)}, index=idx)


def _make_features(dates: pd.DatetimeIndex, vol_pct: float = 0.3) -> pd.DataFrame:
    """最小 HMM 6 特征 DataFrame（_precompute 需要，常量填充）。"""
    n = len(dates)
    return pd.DataFrame(
        {
            "realized_vol_pct": np.full(n, vol_pct),
            "hurst_dfa": np.full(n, 0.5),
            "kalman_slope": np.full(n, 0.0),
            "cross_asset_corr": np.full(n, 0.5),
            "ad_ratio": np.full(n, 0.0),
            "volume_anomaly": np.full(n, 0.0),
        },
        index=dates,
    )


class _MockFeatureBuilder:
    """最小 mock：仅暴露 _compute_vix_pct 后备路径所需方法。"""

    def __init__(self, index_df: pd.DataFrame, features: pd.DataFrame) -> None:
        self._index_df = index_df
        self._features = features

    def build_features(self) -> pd.DataFrame:
        return self._features

    def get_index_kline(self) -> pd.DataFrame:
        return self._index_df

    def get_option_iv_surface(self) -> pd.DataFrame | None:
        return None  # 期权缺失 → 触发合成 VIX 后备


# ---------------------------------------------------------------------------
# synthetic_vix_pct 函数行为测试
# ---------------------------------------------------------------------------


class TestSyntheticVixPct:
    """synthetic_vix_pct 纯函数测试。"""

    def test_value_range_in_unit_interval(self) -> None:
        """值域 ∈ [0, 1]（非 NaN 部分）。"""
        vix = synthetic_vix_pct(_make_crisis_close())
        valid = vix.dropna()
        assert len(valid) > 0
        assert (valid >= 0).all() and (valid <= 1).all()

    def test_warmup_is_nan(self) -> None:
        """前 hv_window + pct_window - 1 日为 NaN（rank 需满窗口）。"""
        close = _make_crisis_close()
        hv, pct = 20, 250
        vix = synthetic_vix_pct(close, hv_window=hv, pct_window=pct)
        # 前 hv+pct-1 日（250 日 rank 需 250 个样本，含当日）应全 NaN
        warmup = vix.iloc[: hv + pct - 1]
        assert warmup.isna().all(), "warmup 期应全 NaN"
        # warmup 之后应有非 NaN
        assert vix.iloc[hv + pct :].notna().any()

    def test_crisis_spike_in_single_series(self) -> None:
        """核心：单序列内危机期（后段）分位显著高于平稳期，且出现 > 0.8 飙升。

        rank(pct=True) 是相对自身的分位——平稳期下行波动稳定 → 分位≈0.5；
        危机期下行波动飙升（相对历史平稳期）→ 分位飙高。
        """
        close = _make_crisis_close()  # 前 350 日平稳，后 250 日危机
        vix = synthetic_vix_pct(close)
        # warmup≈270 日；平稳段非 NaN 约 [270, 350)，危机段 [350, 600)
        calm = vix.iloc[270:350].dropna()
        crisis = vix.iloc[350:].dropna()
        assert (crisis > 0.8).any(), "危机期应出现 vix_pct > 0.8 的飙升点"
        assert crisis.median() > calm.median() + 0.15, (
            f"危机期中位分位 {crisis.median():.3f} 应高于平稳期 {calm.median():.3f}"
        )

    def test_complementary_to_vol_pct(self) -> None:
        """互补性：反弹期（上行主导）vol_pct 分位高于 vix_pct（下行占比小）。

        危机+反弹序列：危机段建立高波动历史，反弹段总波动相近但下行占比小
        → vol_pct 分位中高、vix_pct 分位低，体现下行半偏差的危机特异性。
        """
        close = _make_crisis_then_rebound()
        vol_pct = realized_vol_pct(close).dropna()
        vix_pct = synthetic_vix_pct(close).dropna()
        # 反弹期（后 200 日）
        vol_rebound = vol_pct.iloc[-200:]
        vix_rebound = vix_pct.iloc[-200:]
        assert vix_rebound.median() < vol_rebound.median() - 0.1, (
            f"反弹期 vix_pct {vix_rebound.median():.3f} 应明显低于 "
            f"vol_pct {vol_rebound.median():.3f}（下行占比小 → 互补）"
        )

    def test_constant_price_uniform_output(self) -> None:
        """恒定价格：下行波动恒为 0 → 所有非 NaN 分位相等（rank 平均分位）。"""
        n = 400
        close = pd.Series(np.full(n, 100.0), index=pd.bdate_range("2020-01-01", periods=n))
        vix = synthetic_vix_pct(close).dropna()
        assert vix.nunique() == 1, f"恒定输入应输出全相等的分位，实际有 {vix.nunique()} 个不同值"

    def test_custom_windows_respected(self) -> None:
        """自定义窗口参数生效：小窗口 warmup 更短。"""
        close = _make_crisis_close()
        vix_default = synthetic_vix_pct(close, hv_window=20, pct_window=250)
        vix_short = synthetic_vix_pct(close, hv_window=10, pct_window=100)
        # 短窗口首个非 NaN 应早于默认窗口
        first_default = vix_default.dropna().index[0]
        first_short = vix_short.dropna().index[0]
        assert first_short < first_default, "短窗口 warmup 应更短"


# ---------------------------------------------------------------------------
# _compute_vix_pct 后备逻辑测试
# ---------------------------------------------------------------------------


class TestComputeVixPctFallback:
    """OverlaySignalsConstructor._compute_vix_pct 后备逻辑（期权缺失 → 合成 VIX）。"""

    def test_fallback_to_synthetic_when_option_missing(self) -> None:
        """期权 IV 缺失 + feature_builder 有效 → 返回合成 VIX（非空）。"""
        close = _make_crisis_close()
        index_df = _make_index_df(close)
        features = _make_features(close.index)
        mock = _MockFeatureBuilder(index_df, features)
        ctor = OverlaySignalsConstructor(
            backtest_start=str(close.index[0].date()),
            backtest_end=str(close.index[-1].date()),
            data_load_start=str(close.index[0].date()),
            feature_builder=mock,
        )
        result = ctor._compute_vix_pct(close.index)
        assert result is not None, "期权缺失时应回退合成 VIX，不应返回 None"
        assert not result.empty
        assert result.notna().any()

    def test_returns_none_when_no_feature_builder(self) -> None:
        """feature_builder=None 且期权缺失 → 返回 None（无数据源）。"""
        dates = pd.bdate_range("2020-01-01", periods=300)
        ctor = OverlaySignalsConstructor(
            backtest_start="2020-01-01",
            backtest_end="2021-01-01",
            data_load_start="2020-01-01",
            feature_builder=None,
        )
        assert ctor._compute_vix_pct(dates) is None

    def test_fallback_crisis_spike(self) -> None:
        """后备合成 VIX 在危机期出现飙升点（验证端到端链路有效）。"""
        close = _make_crisis_close()
        index_df = _make_index_df(close)
        features = _make_features(close.index)
        mock = _MockFeatureBuilder(index_df, features)
        ctor = OverlaySignalsConstructor(
            backtest_start=str(close.index[0].date()),
            backtest_end=str(close.index[-1].date()),
            data_load_start=str(close.index[0].date()),
            feature_builder=mock,
        )
        vix = ctor._compute_vix_pct(close.index).dropna()
        crisis_late = vix.iloc[-200:]
        assert (crisis_late > 0.8).any(), "后备合成 VIX 危机期应飙升 > 0.8"

    def test_injection_raises_s1_vix_panic_above_threshold(self) -> None:
        """合成 VIX 注入后，危机期 s1_vix_panic_score 应达 85（过 60 门槛）。"""
        close = _make_crisis_close()
        vol_pct = realized_vol_pct(close)
        vix_pct = synthetic_vix_pct(close)
        score = s1_vix_panic_score(vol_pct, vix_pct)
        crisis_late = score.iloc[-200:]
        # 危机期 vix_pct 飙升 > 0.90 → score=85（过 vix_panic>=60 trigger 门槛）
        assert (crisis_late >= 85).any(), f"危机期 vix_pct 注入后 s1_vix_panic 应达 85，实际最大 {crisis_late.max()}"

    def test_synth_vix_reaches_extreme_panic(self) -> None:
        """危机期合成 VIX 注入后 s1_vix_panic 出现 100 分（极端恐慌 >0.95）。

        证明合成 VIX 在危机早期（下行波动相对历史飙升）能触发 S1 最高档，
        这是纯 vol_pct（总波动率）在同样数据下未必达到的极端信号。
        """
        close = _make_crisis_close()
        vol_pct = realized_vol_pct(close)
        vix_pct = synthetic_vix_pct(close)
        score = s1_vix_panic_score(vol_pct, vix_pct)
        crisis = score.iloc[-250:]
        assert (crisis == 100).any(), f"危机期应出现 s1_vix_panic=100 的极端恐慌点，实际最大 {crisis.max()}"
