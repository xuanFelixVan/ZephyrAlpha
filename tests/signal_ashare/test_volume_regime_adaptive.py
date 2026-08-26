# [BLUEPRINT] MOD-SIG-129 | docs/03_modules/_domain_signal/volume_regime_adaptive/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-129 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_volume_regime_adaptive
# [TESTS] src/zephyr/signal_ashare/volume_regime_adaptive.py
"""MOD-SIG-129 单元测试：volume_regime_adaptive 量能体制自适应策略。

蓝图验收（B10-01445/CAND-TESTB-045，A1 模块23）：
量能三态（vol/MA20：缩量<0.7/平量0.7-1.3/放量>1.3，极端分位标记）+
量能×体制 3×3 策略矩阵查找表（参数注入）+ 查找表查询接口 + 极端分位护栏。
全内存注入，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.volume_regime_adaptive",
    reason="volume_regime_adaptive not importable",
)

from zephyr.signal_ashare.volume_regime_adaptive import (  # noqa: E402
    AdaptiveDecision,
    MarketRegime,
    StrategyParams,
    VolumeRegimeAdaptive,
    VolumeRegimeError,
    VolumeSignal,
    VolumeState,
)

_CELL = {
    (MarketRegime.TREND, VolumeState.SHRINK): StrategyParams(0.2, "flat", "趋势缩量观望"),
    (MarketRegime.TREND, VolumeState.FLAT): StrategyParams(0.5, "long", "趋势平量跟随"),
    (MarketRegime.TREND, VolumeState.SPIKE): StrategyParams(0.8, "long", "趋势放量加仓"),
    (MarketRegime.MEAN_REVERSION, VolumeState.SHRINK): StrategyParams(0.3, "long", "回归缩量低吸"),
    (MarketRegime.MEAN_REVERSION, VolumeState.FLAT): StrategyParams(0.4, "flat", "回归平量等待"),
    (MarketRegime.MEAN_REVERSION, VolumeState.SPIKE): StrategyParams(0.1, "short", "回归放量反向"),
    (MarketRegime.CHOPPY, VolumeState.SHRINK): StrategyParams(0.1, "flat", "混沌缩量空仓"),
    (MarketRegime.CHOPPY, VolumeState.FLAT): StrategyParams(0.2, "flat", "混沌平量轻仓"),
    (MarketRegime.CHOPPY, VolumeState.SPIKE): StrategyParams(0.3, "flat", "混沌放量避险"),
}


def _adapter(**kwargs) -> VolumeRegimeAdaptive:
    kwargs.setdefault("strategy_matrix", _CELL)
    return VolumeRegimeAdaptive(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 量能三态分类（边界归平量）
# ──────────────────────────────────────────────────────────────────────────────


class TestClassify:
    def test_shrink(self) -> None:
        sig = _adapter().classify(60.0, 100.0)
        assert sig.state is VolumeState.SHRINK
        assert sig.ratio == pytest.approx(0.6)

    def test_flat_boundary_low(self) -> None:
        assert _adapter().classify(70.0, 100.0).state is VolumeState.FLAT  # 恰 0.7 归平量

    def test_flat_mid(self) -> None:
        assert _adapter().classify(100.0, 100.0).state is VolumeState.FLAT

    def test_flat_boundary_high(self) -> None:
        assert _adapter().classify(130.0, 100.0).state is VolumeState.FLAT  # 恰 1.3 归平量

    def test_spike(self) -> None:
        assert _adapter().classify(131.0, 100.0).state is VolumeState.SPIKE

    def test_custom_thresholds(self) -> None:
        ad = _adapter(shrink_threshold=0.5, spike_threshold=2.0)
        assert ad.classify(60.0, 100.0).state is VolumeState.FLAT  # 0.6 ∈ [0.5,2.0]

    def test_invalid_volume_raises(self) -> None:
        ad = _adapter()
        for bad in (-1.0, float("nan"), float("inf"), "x", None, True):
            with pytest.raises(VolumeRegimeError):
                ad.classify(bad, 100.0)

    def test_invalid_ma20_raises(self) -> None:
        ad = _adapter()
        for bad in (0.0, -1.0, float("nan"), float("inf")):
            with pytest.raises(VolumeRegimeError):
                ad.classify(100.0, bad)


# ──────────────────────────────────────────────────────────────────────────────
# 极端分位标记
# ──────────────────────────────────────────────────────────────────────────────


class TestPercentile:
    def test_extreme_high_flagged(self) -> None:
        history = [10.0] * 99 + [50.0]
        sig = _adapter().classify(100.0, 100.0, history)  # 100 为历史最大 → 分位 100
        assert sig.percentile == pytest.approx(100.0)
        assert sig.is_extreme is True

    def test_extreme_low_flagged(self) -> None:
        history = [100.0] * 99 + [90.0]
        sig = _adapter().classify(10.0, 100.0, history)  # 10 低于全部历史 → 分位 0
        assert sig.percentile == pytest.approx(0.0)
        assert sig.is_extreme is True

    def test_mid_percentile_not_extreme(self) -> None:
        history = list(range(1, 101))  # 1..100
        sig = _adapter().classify(50.0, 100.0, history)
        assert sig.percentile == pytest.approx(50.0)
        assert sig.is_extreme is False

    def test_no_history_no_percentile(self) -> None:
        sig = _adapter().classify(100.0, 100.0)
        assert sig.percentile is None
        assert sig.is_extreme is False

    def test_empty_history_raises(self) -> None:
        with pytest.raises(VolumeRegimeError):
            _adapter().classify(100.0, 100.0, [])

    def test_bad_history_value_raises(self) -> None:
        with pytest.raises(VolumeRegimeError):
            _adapter().classify(100.0, 100.0, [1.0, -2.0])


# ──────────────────────────────────────────────────────────────────────────────
# 3×3 查找表（构造期校验 + 查询）
# ──────────────────────────────────────────────────────────────────────────────


class TestMatrix:
    def test_query_all_nine_cells(self) -> None:
        ad = _adapter()
        for regime in MarketRegime:
            for state in VolumeState:
                assert ad.query(regime, state) is _CELL[(regime, state)]

    def test_missing_cell_raises(self) -> None:
        bad = dict(_CELL)
        del bad[(MarketRegime.TREND, VolumeState.SPIKE)]
        with pytest.raises(VolumeRegimeError):
            _adapter(strategy_matrix=bad)

    def test_extra_key_raises(self) -> None:
        bad = dict(_CELL)
        bad[(VolumeState.FLAT, MarketRegime.TREND)] = StrategyParams(0.5, "long")  # 轴序颠倒的非法键
        with pytest.raises(VolumeRegimeError):
            _adapter(strategy_matrix=bad)

    def test_wrong_cell_type_raises(self) -> None:
        bad = dict(_CELL)
        bad[(MarketRegime.CHOPPY, VolumeState.FLAT)] = {"position_pct": 0.2}
        with pytest.raises(VolumeRegimeError):
            _adapter(strategy_matrix=bad)

    def test_bad_cell_params_raise(self) -> None:
        with pytest.raises(VolumeRegimeError):
            StrategyParams(1.5, "long")  # 仓位越界
        with pytest.raises(VolumeRegimeError):
            StrategyParams(0.5, "buy")  # 方向词表外

    def test_query_unknown_axis_raises(self) -> None:
        ad = _adapter()
        with pytest.raises(VolumeRegimeError):
            ad.query("trend", VolumeState.FLAT)
        with pytest.raises(VolumeRegimeError):
            ad.query(MarketRegime.TREND, "flat")


# ──────────────────────────────────────────────────────────────────────────────
# 自适应查询（护栏）
# ──────────────────────────────────────────────────────────────────────────────


class TestAdapt:
    def test_normal_path_unguarded(self) -> None:
        history = [float(i) for i in range(1, 201)]  # 1..200，120 落在 60 分位
        dec = _adapter().adapt(MarketRegime.TREND, 120.0, 100.0, history)
        assert isinstance(dec, AdaptiveDecision)
        assert dec.signal.state is VolumeState.FLAT
        assert dec.guarded is False
        assert dec.effective_params is dec.params
        assert dec.effective_params.position_pct == pytest.approx(0.5)

    def test_extreme_guard_halves_position(self) -> None:
        history = [10.0] * 99 + [50.0]
        dec = _adapter().adapt(MarketRegime.TREND, 200.0, 100.0, history)  # 放量+极端分位
        assert dec.signal.state is VolumeState.SPIKE
        assert dec.guarded is True
        assert dec.params.position_pct == pytest.approx(0.8)      # 原格值保留
        assert dec.effective_params.position_pct == pytest.approx(0.4)  # 护栏减半
        assert dec.effective_params.direction == dec.params.direction

    def test_determinism(self) -> None:
        history = list(range(1, 101))
        ad = _adapter()
        d1 = ad.adapt(MarketRegime.CHOPPY, 130.0, 100.0, history)
        d2 = ad.adapt(MarketRegime.CHOPPY, 130.0, 100.0, history)
        assert d1 == d2
