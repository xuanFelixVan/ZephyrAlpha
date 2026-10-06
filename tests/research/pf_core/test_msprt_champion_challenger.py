# [BLUEPRINT] MOD-PF-008 | docs/03_modules/_domain_portfolio_core/msprt_champion_challenger/blueprint.md | §
# [TESTS] tests/pf_core/test_msprt_champion_challenger.py
# [TTL] permanent
"""mSPRT Champion-Challenger 序贯晋升组件单元测试 (MOD-PF-008)。

设计真源: 61 号 design memo §3.3 纪律 1（高斯 mixture 闭式解 + Ville 边界 1/α=20 + 30 笔滚动窗）。
合成数据纪律: δ=0 零效应不误晋升 / δ>0 正确晋升 / δ<0 正确淘汰 / 阈值恰为 20 /
30 笔滚动窗语义 / 空序列与不足窗行为 / τ 标定 / log 似然比轨迹累加。
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from zephyr.pf_core.core.msprt_champion_challenger import (
    ChampionChallengerDecision,
    ChampionChallengerDeltaExtractor,
    MSPRTChampionChallenger,
    MSPRTStepResult,
)

SIGMA = 0.01  # 合成逐笔 delta 噪声尺度（收益差单位）


def _synthetic_deltas(effect: float, n: int, seed: int) -> np.ndarray:
    """合成逐笔 challenger−champion 收益差：N(effect, SIGMA²)。"""
    rng = np.random.default_rng(seed)
    return rng.normal(loc=effect, scale=SIGMA, size=n)


# ---------------------------------------------------------------------------
# 阈值与参数（Ville 边界）
# ---------------------------------------------------------------------------


class TestThresholds:
    def test_threshold_is_exactly_20_with_default_alpha(self) -> None:
        component = MSPRTChampionChallenger()
        assert component.alpha == 0.05
        assert component.threshold == 20.0

    def test_lower_boundary_is_exactly_alpha(self) -> None:
        component = MSPRTChampionChallenger()
        assert component.lower_boundary == 0.05
        assert component.lower_boundary == pytest.approx(1.0 / component.threshold)

    def test_threshold_follows_custom_alpha(self) -> None:
        component = MSPRTChampionChallenger(alpha=0.1)
        assert component.threshold == pytest.approx(10.0)

    def test_explicit_tau_overrides_calibration(self) -> None:
        component = MSPRTChampionChallenger(tau=0.5)
        assert component.tau == 0.5


# ---------------------------------------------------------------------------
# τ 标定（memo：≥5 个历史 OOS 效应量取 std，下限 0.1·median；冷启动 <5 兜底 0.2）
# ---------------------------------------------------------------------------


class TestTauCalibration:
    def test_cold_start_fallback_when_insufficient_history(self) -> None:
        assert MSPRTChampionChallenger.calibrate_tau([0.1, 0.2, 0.3, 0.4]) == 0.2
        assert MSPRTChampionChallenger.calibrate_tau([]) == 0.2

    def test_std_of_five_or_more_effects(self) -> None:
        effects = [0.1, 0.2, 0.3, 0.4, 0.5]
        expected = float(np.std(effects))  # memo: np.std 默认 ddof=0
        assert MSPRTChampionChallenger.calibrate_tau(effects) == pytest.approx(expected)

    def test_floor_protects_against_degenerate_tau(self) -> None:
        effects = [0.2, 0.2, 0.2, 0.2, 0.20001]
        floor = 0.1 * float(np.median(effects))
        assert MSPRTChampionChallenger.calibrate_tau(effects) == pytest.approx(floor)

    def test_constructor_calibrates_from_injected_history(self) -> None:
        effects = [0.1, 0.2, 0.3, 0.4, 0.5]
        component = MSPRTChampionChallenger(historical_effects=effects)
        assert component.tau == pytest.approx(float(np.std(effects)))

    def test_constructor_defaults_to_cold_start_tau(self) -> None:
        assert MSPRTChampionChallenger().tau == 0.2


# ---------------------------------------------------------------------------
# 合成数据序贯判定
# ---------------------------------------------------------------------------


class TestSequentialDecisions:
    def test_zero_effect_long_window_never_promotes(self) -> None:
        deltas = _synthetic_deltas(effect=0.0, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        for delta in deltas:  # update 逐笔全程观察 300 步（anytime-valid 长窗语义）
            step = component.update(float(delta))
            assert step.decision != ChampionChallengerDecision.PROMOTE_CHALLENGER
        assert len(component.trajectory) == 300

    def test_positive_effect_promotes(self) -> None:
        deltas = _synthetic_deltas(effect=0.005, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        result = component.evaluate(deltas)
        assert result.decision == ChampionChallengerDecision.PROMOTE_CHALLENGER
        assert result.m >= component.threshold
        assert result.mean_delta > 0.0

    def test_positive_effect_early_stops_before_sequence_end(self) -> None:
        deltas = _synthetic_deltas(effect=0.005, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        component.evaluate(deltas)
        assert len(component.trajectory) < 300

    def test_negative_effect_eliminates_and_never_promotes(self) -> None:
        deltas = _synthetic_deltas(effect=-0.005, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        result = component.evaluate(deltas)
        assert result.decision == ChampionChallengerDecision.ELIMINATE_CHALLENGER
        watcher = MSPRTChampionChallenger()
        for delta in deltas:  # 全程 300 步逐笔观察，任何时刻不得误晋升
            step = watcher.update(float(delta))
            assert step.decision != ChampionChallengerDecision.PROMOTE_CHALLENGER


# ---------------------------------------------------------------------------
# 30 笔滚动窗语义
# ---------------------------------------------------------------------------


class TestRollingWindow:
    def test_window_defaults_to_30(self) -> None:
        assert MSPRTChampionChallenger().window_size == 30

    def test_window_deltas_are_last_30_after_45_updates(self) -> None:
        deltas = _synthetic_deltas(effect=0.0, n=45, seed=7)
        component = MSPRTChampionChallenger()
        for delta in deltas:
            component.update(float(delta))
        assert component.n == 45
        assert component.window_deltas == pytest.approx(list(deltas[-30:]))

    def test_sigma_uses_only_last_30(self) -> None:
        # 前 15 笔巨噪（±100），后 30 笔微噪（±0.001）——若 σ 用全历史会被巨噪主导
        deltas = np.concatenate(
            [
                _synthetic_deltas(effect=0.0, n=15, seed=11) * 10_000.0,
                _synthetic_deltas(effect=0.0, n=30, seed=13) * 0.1,
            ]
        )
        component = MSPRTChampionChallenger()
        result = component.evaluate(deltas)
        expected_sigma = float(np.std(deltas[-30:]))
        assert result.sigma == pytest.approx(expected_sigma, rel=1e-6)
        assert result.sigma < 0.01


# ---------------------------------------------------------------------------
# 空序列 / 不足窗行为
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_sequence_retains_champion(self) -> None:
        component = MSPRTChampionChallenger()
        result = component.evaluate([])
        assert result.decision == ChampionChallengerDecision.RETAIN_CHAMPION
        assert result.n == 0
        assert result.m == 1.0
        assert result.log_m == 0.0
        assert component.trajectory == []

    def test_single_observation_retains_champion(self) -> None:
        component = MSPRTChampionChallenger()
        result = component.evaluate([0.01])
        assert result.decision == ChampionChallengerDecision.RETAIN_CHAMPION
        assert result.n == 1

    def test_no_terminal_decision_before_window_full(self) -> None:
        # 裁定 2 回归：强正效应（+1σ）前 29 笔（窗未满）不得终局判定——
        # 防 2-3 笔插值 σ 爆炸致 n=2 误晋升（memo max_sample_size 未定义的治本裁定）
        deltas = _synthetic_deltas(effect=0.01, n=29, seed=20260824)
        component = MSPRTChampionChallenger()
        for delta in deltas:
            step = component.update(float(delta))
            assert step.decision == ChampionChallengerDecision.RETAIN_CHAMPION

    def test_decision_enum_terminal_semantics(self) -> None:
        assert ChampionChallengerDecision.PROMOTE_CHALLENGER.is_terminal
        assert ChampionChallengerDecision.ELIMINATE_CHALLENGER.is_terminal
        assert not ChampionChallengerDecision.RETAIN_CHAMPION.is_terminal


# ---------------------------------------------------------------------------
# 似然比轨迹（闭式边际似然比累乘 / log 累加）
# ---------------------------------------------------------------------------


class TestLikelihoodTrajectory:
    def test_log_increments_telescope_to_final_log_m(self) -> None:
        deltas = _synthetic_deltas(effect=0.005, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        result = component.evaluate(deltas)
        total = sum(step.log_lr_increment for step in component.trajectory)
        assert total == pytest.approx(result.log_m, rel=1e-9)

    def test_m_equals_exp_log_m(self) -> None:
        deltas = _synthetic_deltas(effect=0.005, n=300, seed=20260824)
        component = MSPRTChampionChallenger()
        result = component.evaluate(deltas)
        assert result.m == pytest.approx(math.exp(result.log_m), rel=1e-9)

    def test_trajectory_steps_are_ordered_and_typed(self) -> None:
        deltas = _synthetic_deltas(effect=0.0, n=10, seed=3)
        component = MSPRTChampionChallenger()
        component.evaluate(deltas)
        assert len(component.trajectory) == 10
        for index, step in enumerate(component.trajectory, start=1):
            assert isinstance(step, MSPRTStepResult)
            assert step.n == index


# ---------------------------------------------------------------------------
# Delta 提取契约接口（ExecutionReport 对接位，Protocol 结构 seams）
# ---------------------------------------------------------------------------


class TestDeltaExtractorProtocol:
    def test_protocol_accepts_structural_implementation(self) -> None:
        class _PairDeltaExtractor:
            def extract_delta(self, champion_report: object, challenger_report: object) -> float:
                return 0.0

        assert isinstance(_PairDeltaExtractor(), ChampionChallengerDeltaExtractor)

    def test_protocol_rejects_non_conforming(self) -> None:
        class _NoMethod:
            pass

        assert not isinstance(_NoMethod(), ChampionChallengerDeltaExtractor)
