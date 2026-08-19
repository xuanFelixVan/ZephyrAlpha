# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.2-§3.10
# [TTL] permanent
"""情绪周期×交易决策标准函数集单元测试——含边界/退化用例（28 号 §3.2-§3.10）。"""
from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.sentiment_cycle import (
    EFFECTIVE_COMBINATIONS_60,
    PHASE_CHARACTERISTICS,
    PHASE_DISCIPLINE,
    REGIME_STATES_12,
    SENTIMENT_REGIME_MAPPING,
    SENTIMENT_TO_REGIME_MAP,
    STRATEGY_DEPLOYMENT_MATRIX,
    SentimentHawkesParams,
    SentimentLocatorInput,
    SentimentPhase,
    analyze_sentiment_driven_correlation,
    apply_phase_discipline,
    apply_sentiment_position_soft_influence,
    apply_sentiment_soft_influence,
    classify_sentiment_phase,
    combine_sentiment_regime,
    compute_hawkes_intensity,
    compute_sentiment_correlation_driver,
    compute_sentiment_temperature,
    compute_strategy_deployment,
    detect_phase_transition,
    estimate_hawkes_branching_ratio,
    evaluate_locator_accuracy,
    get_effective_combinations,
    get_phase_trading_discipline,
    get_strategy_deployment_by_phase,
    locate_sentiment_phase,
    map_sentiment_to_regime,
    validate_sentiment_hidden_driver,
    validate_sentiment_regime_map,
)


def _locator_input(**kw) -> SentimentLocatorInput:
    base = dict(
        limit_up_count=60, limit_down_count=2, explosion_count=15,
        consecutive_ladder={2: 10, 3: 5, 4: 2}, yesterday_consecutive={2: 8, 3: 4},
        daban_next_day_premium=0.03, avg_turnover_rate=3.0,
        market_amount_ratio_vs_ma20=1.2, dragon_tiger_net_buy_ratio=0.13,
        northbound_net_inflow=30.0,
    )
    base.update(kw)
    return SentimentLocatorInput(**base)


def _concentrated_prior(phase: SentimentPhase, prob: float = 0.9) -> dict[SentimentPhase, float]:
    """集中先验（情绪惯性）：主导阶段 prob，其余均分——使后验置信度 >0.6 不触发兜底。"""
    rest = (1.0 - prob) / 4.0
    return {p: (prob if p == phase else rest) for p in SentimentPhase}


class TestPhaseDefinitions:
    def test_five_phases_complete(self):
        assert len(list(SentimentPhase)) == 5
        assert set(PHASE_CHARACTERISTICS) == set(SentimentPhase)
        assert set(PHASE_DISCIPLINE) == set(SentimentPhase)

    def test_deployment_matrix_15_cells(self):
        assert len(STRATEGY_DEPLOYMENT_MATRIX) == 15
        for s in ("daban", "multifactor", "event_driven"):
            for p in SentimentPhase:
                assert (s, p) in STRATEGY_DEPLOYMENT_MATRIX

    def test_effective_combinations_60(self):
        assert len(EFFECTIVE_COMBINATIONS_60) == 60
        assert len(get_effective_combinations()) == 60
        assert len(get_effective_combinations(phase_filter=SentimentPhase.FREEZING)) == 12
        assert len(get_effective_combinations(regime_filter="CRISIS")) == 5


class TestTemperature:
    def test_hot_market_high_score(self):
        out = compute_sentiment_temperature(
            limit_up_count=90, limit_down_count=2, explosion_count=5,
            sealed_limit_up_count=85, consecutive_ladder={2: 20, 3: 10, 4: 5, 5: 3, 6: 2, 7: 1},
            advance_count=4000, decline_count=800,
        )
        assert out.score >= 70.0
        assert out.phase_hint in (SentimentPhase.CONSENSUS, SentimentPhase.EBING)
        assert abs(sum(out.weighted_scores.values()) * 100.0 - out.score) < 1e-6

    def test_cold_market_low_score(self):
        out = compute_sentiment_temperature(
            limit_up_count=5, limit_down_count=45, explosion_count=10,
            sealed_limit_up_count=3, consecutive_ladder={},
            advance_count=500, decline_count=4200,
        )
        assert out.score < 40.0

    def test_degenerate_zero_inputs(self):
        out = compute_sentiment_temperature(
            limit_up_count=0, limit_down_count=0, explosion_count=0,
            sealed_limit_up_count=0, consecutive_ladder={},
            advance_count=0, decline_count=0,
        )
        assert 0.0 <= out.score <= 100.0  # 除零安全

    def test_score_bounded(self):
        out = compute_sentiment_temperature(
            limit_up_count=500, limit_down_count=0, explosion_count=0,
            sealed_limit_up_count=500, consecutive_ladder={9: 3},
            advance_count=5000, decline_count=1,
            historical_peak_limit_up=100,
        )
        assert out.score <= 100.0


class TestPhaseTransition:
    def test_insufficient_data_returns_none(self):
        sig = detect_phase_transition(
            SentimentPhase.FREEZING, [0.5, 0.4], [5, 8], [1, 2], 3, 0,
        )
        assert sig.transition_type == "none"
        assert sig.is_actionable is False

    def test_bottom_reversal_actionable(self):
        sig = detect_phase_transition(
            SentimentPhase.FREEZING,
            explosion_rate_series=[0.50, 0.50, 0.50, 0.50, 0.50, 0.30],  # 骤降 0.20
            limit_up_count_series=[10, 10, 10, 10, 10, 20],  # 回暖 ×2.0
            consecutive_height_series=[1, 1, 1, 1, 1, 3],  # 突破 +2
            limit_down_count=5, nuclear_button_count=0,
        )
        assert sig.transition_type == "bottom_reversal"
        assert sig.is_actionable is True
        assert sig.confidence == pytest.approx(1.0)
        assert sig.to_phase == SentimentPhase.STARTING

    def test_top_divergence_actionable(self):
        sig = detect_phase_transition(
            SentimentPhase.CONSENSUS,
            explosion_rate_series=[0.15, 0.15, 0.15, 0.15, 0.15, 0.32],  # 攀升 0.17
            limit_up_count_series=[90, 90, 90, 90, 90, 60],
            consecutive_height_series=[7, 7, 7, 7, 7, 3],  # 0.43 ≤0.6
            limit_down_count=60, nuclear_button_count=12,  # 双确认
        )
        assert sig.transition_type == "top_divergence"
        assert sig.is_actionable is True
        assert sig.to_phase == SentimentPhase.EBING

    def test_leading_only_not_actionable(self):
        sig = detect_phase_transition(
            SentimentPhase.CONSENSUS,
            explosion_rate_series=[0.15, 0.15, 0.15, 0.15, 0.15, 0.32],
            limit_up_count_series=[90, 90, 90, 90, 90, 60],
            consecutive_height_series=[7, 7, 7, 7, 7, 3],
            limit_down_count=5, nuclear_button_count=0,  # 无确认
        )
        assert sig.transition_type == "top_divergence"
        assert sig.is_actionable is False
        assert sig.confidence == pytest.approx(0.5)

    def test_other_phase_no_transition(self):
        sig = detect_phase_transition(
            SentimentPhase.FERMENTING,
            explosion_rate_series=[0.2] * 6, limit_up_count_series=[60] * 6,
            consecutive_height_series=[5] * 6, limit_down_count=2, nuclear_button_count=0,
        )
        assert sig.transition_type == "none"


class TestLocator:
    def test_prob_sums_to_one(self):
        out = locate_sentiment_phase(_locator_input())
        assert sum(out.phase_prob.values()) == pytest.approx(1.0)
        assert out.dominant_phase == max(out.phase_prob, key=out.phase_prob.get)
        assert out.confidence == pytest.approx(out.phase_prob[out.dominant_phase])

    def test_fermenting_market(self):
        out = locate_sentiment_phase(_locator_input(
            yesterday_phase_prob=_concentrated_prior(SentimentPhase.FERMENTING),
        ))
        assert out.dominant_phase == SentimentPhase.FERMENTING
        assert out.is_tradable is True
        assert out.fallback_triggered is False
        assert 0.0 <= out.position_scale <= 1.0

    def test_uniform_prior_dilutes_confidence_and_falls_back(self):
        # 无先验（均匀 0.2）+ 证据不集中 → max(P)<0.6 → 兜底回退收缩态（spec 行为）
        out = locate_sentiment_phase(_locator_input())
        assert out.fallback_triggered is True
        assert out.dominant_phase in (SentimentPhase.FREEZING, SentimentPhase.EBING)
        assert out.position_scale <= 0.3

    def test_fallback_on_low_confidence(self):
        # 矛盾输入 + 高阈值 → 兜底回退收缩态
        out = locate_sentiment_phase(_locator_input(
            limit_up_count=25, limit_down_count=12, explosion_count=18,
            daban_next_day_premium=0.0, market_amount_ratio_vs_ma20=0.9,
        ), confidence_threshold=0.999)
        assert out.fallback_triggered is True
        assert out.dominant_phase in (SentimentPhase.FREEZING, SentimentPhase.EBING)
        assert out.position_scale <= 0.3
        assert out.is_tradable is False

    def test_explosion_rate_circuit_breaker(self):
        # 炸板率 >70% 且置信度充足（集中先验不触发兜底）→ 强制不可交易 + scale ≤0.1
        out = locate_sentiment_phase(_locator_input(
            limit_up_count=60, limit_down_count=2, explosion_count=150,
            daban_next_day_premium=0.03, market_amount_ratio_vs_ma20=1.2,
            yesterday_phase_prob=_concentrated_prior(SentimentPhase.FERMENTING),
        ))
        assert out.fallback_triggered is False
        assert out.is_tradable is False
        assert out.position_scale <= 0.1

    def test_classify_wrapper_delegates(self):
        inp = _locator_input()
        a = classify_sentiment_phase(inp)
        b = locate_sentiment_phase(inp)
        assert a.dominant_phase == b.dominant_phase
        assert a.confidence == pytest.approx(b.confidence)


class TestDiscipline:
    def test_get_discipline_all_phases(self):
        for p in SentimentPhase:
            d = get_phase_trading_discipline(p)
            assert d.phase == p

    def test_new_open_blocked_in_consensus(self):
        out = locate_sentiment_phase(_locator_input())
        # 强制构造疯狂主导输出
        out.dominant_phase = SentimentPhase.CONSENSUS
        adj, allowed, reason = apply_phase_discipline("daban", 0.6, out, is_new_open=True)
        assert allowed is False and adj == 0.0

    def test_position_scaling_and_affinity(self):
        out = locate_sentiment_phase(_locator_input(
            yesterday_phase_prob=_concentrated_prior(SentimentPhase.FERMENTING),
        ))  # 主升主导且不触发兜底
        adj, allowed, _ = apply_phase_discipline("daban", 1.0, out, is_new_open=True)
        assert allowed is True
        assert 0.0 < adj <= 1.0


class TestRegimeMapping:
    def test_validate_default_map_ok(self):
        assert validate_sentiment_regime_map() == []

    def test_validate_detects_problems(self):
        bad = {SentimentPhase.FREEZING: {"UNKNOWN-STATE": 0.9}}
        problems = validate_sentiment_regime_map(bad)  # type: ignore[arg-type]
        assert any("缺阶段映射" in p for p in problems)
        assert any("未知 regime 态" in p for p in problems)
        assert any("软影响上限" in p for p in problems)

    def test_regime_states_12(self):
        assert len(REGIME_STATES_12) == 12

    def test_soft_influence_renormalizes(self):
        regime_prob = {s: 1.0 / 12 for s in REGIME_STATES_12}
        sentiment = locate_sentiment_phase(_locator_input())
        adjusted = apply_sentiment_soft_influence(regime_prob, sentiment)
        assert sum(adjusted.values()) == pytest.approx(1.0)
        # 主升主导 → Bull-Medium 概率被上调
        if sentiment.dominant_phase == SentimentPhase.FERMENTING:
            assert adjusted["Bull-Medium"] > regime_prob["Bull-Medium"]

    def test_soft_influence_empty_prob_safe(self):
        sentiment = locate_sentiment_phase(_locator_input())
        assert apply_sentiment_soft_influence({}, sentiment) == {}

    def test_combine_multiplicative(self):
        sentiment = locate_sentiment_phase(_locator_input())
        regime_prob = {"Bull-Low": 0.6, "Bull-Medium": 0.4}
        shrink_map = {"Bull-Low": 1.0, "Bull-Medium": 0.8}
        directive = combine_sentiment_regime(
            "daban", 0.8, sentiment, regime_prob, shrink_map,
        )
        assert 0.0 <= directive.combined_position_scale <= 1.0
        assert directive.regime_state == "Bull-Low"
        # 乘法叠加：combined ≤ sentiment_adjusted（shrinkage ≤1 时）
        assert directive.combined_position_scale <= directive.position_scale_sentiment + 1e-9

    def test_combine_low_shrinkage_blocks_new_open(self):
        sentiment = locate_sentiment_phase(_locator_input())
        directive = combine_sentiment_regime(
            "daban", 0.8, sentiment, {"CRISIS": 1.0}, {"CRISIS": 0.2},
        )
        assert directive.allow_new_open is False
        assert directive.throttle_factor <= 0.2

    def test_position_soft_influence_fallback_cap(self):
        out = locate_sentiment_phase(_locator_input(
            limit_up_count=25, limit_down_count=12, explosion_count=18,
            daban_next_day_premium=0.0, market_amount_ratio_vs_ma20=0.9,
        ), confidence_threshold=0.999)
        adj, rationale = apply_sentiment_position_soft_influence("daban", 1.0, out)
        assert adj <= 0.2
        assert "fallback=True" in rationale

    def test_map_sentiment_to_regime_wrapper(self):
        sentiment = locate_sentiment_phase(_locator_input())
        regime_prob = {s: 1.0 / 12 for s in REGIME_STATES_12}
        out = map_sentiment_to_regime(regime_prob, sentiment)
        assert sum(out["regime_prob_adjusted"].values()) == pytest.approx(1.0)
        assert out["dominant_phase"] == sentiment.dominant_phase
        expected = SENTIMENT_REGIME_MAPPING[sentiment.dominant_phase][out["dominant_regime"]]
        assert out["combined_position_scale"] == pytest.approx(expected)

    def test_sentiment_to_regime_map_values(self):
        assert SENTIMENT_TO_REGIME_MAP[SentimentPhase.STARTING] == {"RECOVERY": +0.20}
        assert set(SENTIMENT_TO_REGIME_MAP) == set(SentimentPhase)


class TestDeployment:
    def test_single_strategy_lookup(self):
        pol = get_strategy_deployment_by_phase(SentimentPhase.FERMENTING, "daban")
        assert pol.position_scale == 0.7
        assert pol.allow_new_open is True

    def test_all_strategies_lookup(self):
        out = compute_strategy_deployment(SentimentPhase.FREEZING)
        assert set(out) == {"daban", "multifactor", "event_driven"}
        assert out["daban"].position_scale == 0.0
        assert out["multifactor"].allow_new_open is True


class TestHawkes:
    def test_intensity_decays_with_time(self):
        params = SentimentHawkesParams(lambda_0=0.5, alpha=1.0, beta=0.5, critical_ratio=2.0)
        i1 = compute_hawkes_intensity([1.0], params, t=1.5)
        i2 = compute_hawkes_intensity([1.0], params, t=5.0)
        assert i1 > i2 > params.lambda_0
        assert compute_hawkes_intensity([], params, t=1.0) == params.lambda_0

    def test_branching_ratio(self):
        params = SentimentHawkesParams(lambda_0=0.5, alpha=0.6, beta=1.0, critical_ratio=0.6)
        assert estimate_hawkes_branching_ratio([], params) == pytest.approx(0.6)
        bad = SentimentHawkesParams(lambda_0=0.5, alpha=1.0, beta=0.0, critical_ratio=float("inf"))
        assert estimate_hawkes_branching_ratio([], bad) == float("inf")

    def test_correlation_driver(self):
        lam = [0.5, 0.8, 1.2, 0.6, 0.4, 1.5, 1.1, 0.7]
        returns = {"daban": [l * 0.01 for l in lam], "multifactor": [0.001] * 8}
        drivers = compute_sentiment_correlation_driver(returns, lam)
        assert drivers["daban"] == pytest.approx(1.0)
        assert drivers["multifactor"] == 0.0  # 零方差 → 0

    def test_block_bootstrap_significance(self):
        rng = np.random.default_rng(7)
        n = 120
        lam = rng.gamma(2.0, 0.5, size=n).tolist()
        strong = {"daban": (np.array(lam) * 0.02 + rng.normal(0, 0.002, n)).tolist()}
        result = analyze_sentiment_driven_correlation(
            strong, lam, n_bootstrap=100, block_size=5,
        )
        assert result["observed_rho"]["daban"] > 0.6
        assert result["is_significant"]["daban"] is True
        assert result["p_value"]["daban"] < 0.05
        assert result["n_bootstrap"] == 100

    def test_block_bootstrap_degenerate(self):
        # 常量强度 → ρ=0，不显著；不崩溃
        result = analyze_sentiment_driven_correlation(
            {"s": [0.01, 0.02, 0.0, -0.01]}, [1.0, 1.0, 1.0, 1.0],
            n_bootstrap=10, block_size=2,
        )
        assert result["observed_rho"]["s"] == 0.0
        assert result["is_significant"]["s"] is False


class TestHiddenDriverValidation:
    def test_stratified_correlation_drop_passes(self):
        rng = np.random.default_rng(3)
        n_per_phase = 40
        returns, phases = {"a": [], "b": []}, []
        for _p in SentimentPhase:
            ra = rng.normal(0, 0.01, n_per_phase)
            rb = rng.normal(0, 0.01, n_per_phase)  # 各阶段内独立 → 分层 ρ 低
            returns["a"].extend(ra.tolist())
            returns["b"].extend(rb.tolist())
            phases.extend([_p] * n_per_phase)
        results = validate_sentiment_hidden_driver(returns, phases)
        assert all(r.n_days == 40 for r in results.values())
        assert all(r.is_pass for r in results.values())

    def test_rare_phase_skipped(self):
        returns = {"a": [0.01] * 10, "b": [0.02] * 10}
        phases = [SentimentPhase.FREEZING] * 10
        results = validate_sentiment_hidden_driver(returns, phases)
        assert results[SentimentPhase.FREEZING].n_days == 10
        assert results[SentimentPhase.FREEZING].is_pass is False
        assert results[SentimentPhase.FREEZING].correlation_matrix == {}


class TestAccuracyEvaluator:
    def test_exact_and_adjacent(self):
        order = list(SentimentPhase)
        pred = [order[0], order[1], order[2], order[3]]
        actual = [order[0], order[2], order[2], order[4]]
        out = evaluate_locator_accuracy(pred, actual)
        assert out["accuracy"] == pytest.approx(0.5)
        assert out["adjacent_tolerance_rate"] == pytest.approx(0.5)
        assert out["n_samples"] == 4.0

    def test_degenerate_inputs(self):
        assert evaluate_locator_accuracy([], [])["n_samples"] == 0.0
        out = evaluate_locator_accuracy([SentimentPhase.FREEZING], [])
        assert out["accuracy"] == 0.0
