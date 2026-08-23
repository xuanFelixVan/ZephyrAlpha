# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [TTL] permanent
"""收益率条件密度预测（BM-SEL-13，MOD-SIG-043）单元测试——矩/分位数/条件桶/CRPS/降级。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.conditional_density_predictor import (
    ConditionalDensityConfig,
    conditional_density,
    crps_empirical,
)


class TestUnconditional:
    def test_moments_on_known_samples(self):
        rng = np.random.default_rng(5)
        samples = rng.normal(0.001, 0.02, 500)
        cfg = ConditionalDensityConfig(window=500)  # 覆盖全样本，避开默认 trailing 250 截断
        out = conditional_density(samples, config=cfg)
        assert out.condition == "ALL"
        assert out.n_samples == 500
        assert out.mean == pytest.approx(0.001, abs=0.005)
        assert out.std == pytest.approx(0.02, abs=0.005)
        assert abs(out.skewness) < 0.5
        assert out.degraded is False

    def test_quantile_grid_monotone(self):
        rng = np.random.default_rng(9)
        cfg = ConditionalDensityConfig(window=2500)  # 覆盖全样本，避开 trailing 截断
        out = conditional_density(rng.normal(size=2000), config=cfg)
        qs = out.quantiles
        keys = sorted(qs)
        assert [qs[k] for k in keys] == sorted(qs[k] for k in keys)  # 分位值随水平单调
        assert qs[0.5] == pytest.approx(0.0, abs=0.06)  # 标准正态中位≈0（抽样噪声 ~0.03）

    def test_window_truncation(self):
        cfg = ConditionalDensityConfig(window=100)
        samples = list(np.linspace(-0.01, 0.01, 400))
        out = conditional_density(samples, config=cfg)
        assert out.n_samples == 100  # trailing 截断

    def test_var_cvar_tail(self):
        rng = np.random.default_rng(3)
        out = conditional_density(rng.normal(0.0, 0.02, 1000))
        assert out.var_95 < 0.0  # 左尾亏损
        assert out.cvar_95 <= out.var_95  # CVaR 不浅于 VaR

    def test_density_summary_contract(self):
        rng = np.random.default_rng(21)
        samples = rng.standard_t(df=4, size=800) * 0.02  # 厚尾
        out = conditional_density(samples)
        summary = out.density_summary()
        assert summary.neg_skewness == max(0.0, -out.skewness)
        assert summary.excess_kurtosis == pytest.approx(max(0.0, out.excess_kurtosis))
        assert summary.forward_var_pct == pytest.approx(abs(out.var_95) * 100.0)
        assert summary.excess_kurtosis > 0.5  # t(4) 超额峰度显著为正

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            conditional_density([0.01])


class TestConditional:
    def _two_regime_samples(self):
        rng = np.random.default_rng(17)
        low = rng.normal(0.0, 0.01, 200)
        high = rng.normal(0.0, 0.05, 200)
        returns = np.concatenate([low, high])
        conditions = ["LOW"] * 200 + ["HIGH"] * 200
        return returns, conditions

    def test_condition_buckets_differ(self):
        returns, conditions = self._two_regime_samples()
        cfg = ConditionalDensityConfig(window=500, min_samples=60)  # window 覆盖全样本 400
        low = conditional_density(returns, conditions, condition="LOW", config=cfg)
        high = conditional_density(returns, conditions, condition="HIGH", config=cfg)
        assert low.degraded is False and high.degraded is False
        assert high.std > low.std * 2  # 高波动桶 std 显著更大

    def test_small_bucket_falls_back_degraded(self):
        returns, conditions = self._two_regime_samples()
        conditions = conditions + ["RARE"] * 5
        returns = np.concatenate([returns, np.zeros(5)])
        out = conditional_density(returns, conditions, condition="RARE")
        assert out.degraded is True
        assert out.n_samples == 250  # 回退全样本（trailing window=250 截断后）

    def test_condition_required_when_conditions_given(self):
        returns, conditions = self._two_regime_samples()
        with pytest.raises(ValueError):
            conditional_density(returns, conditions)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            conditional_density([0.01] * 10, ["A"] * 5, condition="A")


class TestCrps:
    def test_known_value(self):
        """samples=[1,2,3], y=2：E|X−y|=2/3，E|X−X'|=8/9 → CRPS=2/3−4/9=2/9。"""
        assert crps_empirical([1.0, 2.0, 3.0], 2.0) == pytest.approx(2.0 / 9.0)

    def test_perfect_point_mass(self):
        """常数样本命中实际值 → CRPS=0。"""
        assert crps_empirical([2.0, 2.0, 2.0], 2.0) == pytest.approx(0.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            crps_empirical([], 1.0)
