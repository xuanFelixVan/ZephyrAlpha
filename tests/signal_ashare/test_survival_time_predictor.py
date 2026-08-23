# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §3
# [TTL] permanent
"""Survival 止盈止损时间预测（BM-SEL-15，MOD-SIG-045）单元测试——KM 基线 + Weibull AFT MLE 回参。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.survival_time_predictor import (
    WeibullAFTModel,
    kaplan_meier,
)


def _simulate_weibull(mu: float, sigma: float, n: int, seed: int) -> np.ndarray:
    """逆 CDF 采样：log T = μ + σ·W，W 标准最小极值分布。"""
    rng = np.random.default_rng(seed)
    u = rng.uniform(1e-9, 1.0 - 1e-9, n)
    w = np.log(-np.log(1.0 - u))
    return np.exp(mu + sigma * w)


class TestKaplanMeier:
    def test_known_curve(self):
        """durations=[2,3,4,5], events=[1,1,0,1]：S(2)=0.75, S(3)=0.5, S(5)=0。"""
        curve = kaplan_meier([2, 3, 4, 5], [1, 1, 0, 1])
        assert curve.times == (2.0, 3.0, 5.0)
        assert curve.survival == (pytest.approx(0.75), pytest.approx(0.5), pytest.approx(0.0))
        assert curve.n_at_risk_start == 4

    def test_survival_at_step(self):
        curve = kaplan_meier([2, 3, 4, 5], [1, 1, 0, 1])
        assert curve.survival_at(1.0) == 1.0
        assert curve.survival_at(2.5) == pytest.approx(0.75)
        assert curve.survival_at(4.0) == pytest.approx(0.5)

    def test_median(self):
        curve = kaplan_meier([2, 3, 4, 5], [1, 1, 0, 1])
        assert curve.median_time() == pytest.approx(3.0)  # 首个 S≤0.5

    def test_median_none_when_above_half(self):
        """全删失（无事件点）→ 空曲线 → 中位 None。"""
        curve = kaplan_meier([10, 20, 30], [0, 0, 0])
        assert curve.times == ()
        assert curve.median_time() is None

    def test_monotone_nonincreasing(self):
        rng = np.random.default_rng(31)
        d = rng.exponential(5.0, 100)
        e = rng.binomial(1, 0.8, 100)
        curve = kaplan_meier(d, e)
        sv = list(curve.survival)
        assert sv == sorted(sv, reverse=True)

    def test_input_validation(self):
        with pytest.raises(ValueError):
            kaplan_meier([1, 2], [1])  # 长度不一致
        with pytest.raises(ValueError):
            kaplan_meier([], [])  # 空
        with pytest.raises(ValueError):
            kaplan_meier([0.0, 2.0], [1, 1])  # 非正 duration
        with pytest.raises(ValueError):
            kaplan_meier([1.0, 2.0], [1, 2])  # event ∉ {0,1}


class TestWeibullAFT:
    def test_recovers_params_no_censor(self):
        """无删失合成数据回参：μ=ln10, σ=0.5。"""
        mu, sigma = np.log(10.0), 0.5
        t = _simulate_weibull(mu, sigma, 800, seed=41)
        m = WeibullAFTModel().fit(t, [1] * 800)
        assert m.intercept == pytest.approx(mu, abs=0.08)
        assert m.sigma == pytest.approx(sigma, abs=0.06)
        assert m.median_time() == pytest.approx(10.0 * (np.log(2) ** 0.5), rel=0.10)

    def test_recovers_covariate_effect(self):
        """含协变量：μ = 2.0 + 0.5x → coef ≈ 0.5。"""
        rng = np.random.default_rng(43)
        n = 1200
        x = rng.normal(0.0, 1.0, n)
        w = np.log(-np.log(1.0 - rng.uniform(1e-9, 1 - 1e-9, n)))
        t = np.exp(2.0 + 0.5 * x + 0.4 * w)
        m = WeibullAFTModel().fit(t, [1] * n, covariates=[[v] for v in x])
        assert m.coef is not None
        assert m.coef[0] == pytest.approx(0.5, abs=0.08)
        assert m.intercept == pytest.approx(2.0, abs=0.08)

    def test_right_censoring_fit(self):
        """右删失 30% 仍能收敛且参数不失真。"""
        mu, sigma = np.log(8.0), 0.6
        rng = np.random.default_rng(47)
        t_true = _simulate_weibull(mu, sigma, 1000, seed=47)
        censor = rng.uniform(2.0, 15.0, 1000)
        observed = np.minimum(t_true, censor)
        events = (t_true <= censor).astype(int)
        m = WeibullAFTModel().fit(observed, events)
        assert m.intercept == pytest.approx(mu, abs=0.15)
        assert 0.0 < m.prob_event_within(5.0) < 1.0

    def test_prediction_monotonicity(self):
        t = _simulate_weibull(np.log(10.0), 0.5, 500, seed=53)
        m = WeibullAFTModel().fit(t, [1] * 500)
        assert m.survival_prob(5.0) > m.survival_prob(10.0)  # S 随 t 递减
        assert m.prob_event_within(10.0) > m.prob_event_within(5.0)  # 事件概率随 horizon 递增
        assert m.expected_time() > m.median_time()  # Weibull 均值>中位（σ=0.5 族）

    def test_covariate_shift_changes_prediction(self):
        """协变量正向 → 持有期更长（xβ 大 → median 大）。"""
        rng = np.random.default_rng(59)
        n = 1000
        x = rng.normal(0.0, 1.0, n)
        w = np.log(-np.log(1.0 - rng.uniform(1e-9, 1 - 1e-9, n)))
        t = np.exp(2.0 + 0.6 * x + 0.4 * w)
        m = WeibullAFTModel().fit(t, [1] * n, covariates=[[v] for v in x])
        assert m.median_time([1.0]) > m.median_time([-1.0])

    def test_predict_x_without_covariates_raises(self):
        t = _simulate_weibull(np.log(10.0), 0.5, 300, seed=61)
        m = WeibullAFTModel().fit(t, [1] * 300)
        with pytest.raises(ValueError):
            m.median_time([1.0])

    def test_input_validation(self):
        with pytest.raises(ValueError):
            WeibullAFTModel().fit([1, -2], [1, 1])
        with pytest.raises(ValueError):
            WeibullAFTModel().fit([1, 2], [1, 0], covariates=[[1.0]])
