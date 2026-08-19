# [A_test] module_id: MOD-GOV_test_correlation_block_bootstrap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_block_bootstrap
# [TESTS] src/zephyr/factor/analysis/correlation_block_bootstrap.py
# [TTL] task_bound
"""23 号 memo §3.2 multivariate stationary block-bootstrap 引擎测试。

裁定真源：23_strategy_correlation_validation.md §3.2——
  Politis-Romano stationary bootstrap + Patton-Politis-White (2009) 自动块长 +
  2000× 同步行重采样 + Fisher z 参数 CI 互验。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis.correlation_block_bootstrap import (
    MIN_OBS,
    bootstrap_correlation_ci,
    fisher_z_ci,
    ppw_block_size,
    stationary_bootstrap_indices,
)


def _ar1(n: int, phi: float, rng: np.random.Generator) -> np.ndarray:
    x = np.empty(n)
    x[0] = 0.0
    eps = rng.normal(0.0, 1.0, n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + eps[t]
    return x


class TestPPWBlockSize:
    def test_white_noise_small_block(self):
        rng = np.random.default_rng(5)
        panel = rng.normal(0, 1, (400, 3))
        b = ppw_block_size(panel)
        b_max = int(np.ceil(min(3 * np.sqrt(400), 400 / 3)))
        assert 1 <= b <= b_max
        assert b <= 5  # 白噪声无自相关 → 小块长

    def test_persistent_ar1_larger_than_noise(self):
        rng = np.random.default_rng(9)
        noise = rng.normal(0, 1, 800)
        persistent = _ar1(800, 0.9, rng)
        assert ppw_block_size(persistent.reshape(-1, 1)) > ppw_block_size(noise.reshape(-1, 1))

    def test_constant_column_degrades_to_one(self):
        panel = np.column_stack([np.ones(100), np.random.default_rng(2).normal(0, 1, 100)])
        assert ppw_block_size(panel) >= 1  # 常数列退化 b=1，不崩溃

    def test_insufficient_sample_rejected(self):
        with pytest.raises(ValueError):
            ppw_block_size(np.random.default_rng(1).normal(0, 1, (3, 2)))


class TestStationaryBootstrapIndices:
    def test_length_and_range(self):
        rng = np.random.default_rng(13)
        idx = stationary_bootstrap_indices(120, 5, rng)
        assert len(idx) == 120
        assert idx.min() >= 0 and idx.max() < 120

    def test_block_structure_preserved(self):
        """平均块长 50 时相邻索引连续比例应显著高于块长 1（时序结构保留）。"""
        n = 400
        rng = np.random.default_rng(17)
        idx_block = stationary_bootstrap_indices(n, 50, rng)
        idx_iid = stationary_bootstrap_indices(n, 1, rng)
        cont_block = np.mean(np.diff(idx_block) == 1)
        cont_iid = np.mean(np.diff(idx_iid) == 1)
        assert cont_block > cont_iid

    def test_invalid_n_rejected(self):
        with pytest.raises(ValueError):
            stationary_bootstrap_indices(0, 5, np.random.default_rng(1))


class TestFisherZCI:
    def test_zero_rho_symmetric(self):
        lo, hi = fisher_z_ci(0.0, 103, 0.90)
        assert lo == pytest.approx(-hi)
        # hi = tanh(z_α/√(n−3))，非 z 本身
        assert hi == pytest.approx(np.tanh(1.644853626951472 / np.sqrt(100)), rel=1e-6)

    def test_small_n_rejected(self):
        with pytest.raises(ValueError):
            fisher_z_ci(0.5, 3)


class TestBootstrapCorrelationCI:
    @staticmethod
    def _panel(t: int = 200) -> pd.DataFrame:
        rng = np.random.default_rng(23)
        factor = rng.normal(0, 1, t)
        s1 = np.sqrt(0.7) * factor + np.sqrt(0.3) * rng.normal(0, 1, t)
        s2 = np.sqrt(0.7) * factor + np.sqrt(0.3) * rng.normal(0, 1, t)  # ρ(s1,s2)=0.7
        s3 = rng.normal(0, 1, t)  # 独立
        return pd.DataFrame({"s1": s1, "s2": s2, "s3": s3})

    def test_ci_covers_true_correlation(self):
        panel = self._panel()
        res = bootstrap_correlation_ci(panel, n_bootstrap=300, seed=99)
        pair = res.pearson[("s1", "s2")]
        assert pair.point == pytest.approx(0.7, abs=0.10)
        assert pair.ci_lower <= 0.7 <= pair.ci_upper
        assert pair.prob_above_threshold > 0.5  # P(ρ>0.6) 显著
        assert pair.ci_lower <= pair.point <= pair.ci_upper

    def test_independent_pair_low_prob(self):
        panel = self._panel()
        res = bootstrap_correlation_ci(panel, n_bootstrap=300, seed=100)
        pair = res.pearson[("s1", "s3")]
        assert abs(pair.point) < 0.2
        assert pair.prob_above_threshold < 0.5

    def test_fisher_ci_cross_check_present(self):
        panel = self._panel()
        res = bootstrap_correlation_ci(panel, n_bootstrap=100, seed=101)
        pair = res.spearman[("s1", "s2")]
        assert pair.fisher_ci_lower < pair.fisher_ci_upper
        assert res.block_size >= 1 and res.n_bootstrap == 100 and res.n_obs == 200

    def test_seed_reproducible(self):
        panel = self._panel()
        r1 = bootstrap_correlation_ci(panel, n_bootstrap=100, seed=7)
        r2 = bootstrap_correlation_ci(panel, n_bootstrap=100, seed=7)
        assert r1.pearson[("s1", "s2")].ci_lower == r2.pearson[("s1", "s2")].ci_lower

    def test_degenerate_inputs_rejected(self):
        with pytest.raises(ValueError):  # 样本不足
            bootstrap_correlation_ci(pd.DataFrame({"a": [0.1, 0.2], "b": [0.1, 0.3]}))
        with pytest.raises(ValueError):  # 列数<2
            bootstrap_correlation_ci(pd.DataFrame({"a": np.random.default_rng(1).normal(0, 1, 50)}))
        with pytest.raises(ValueError):  # NaN
            bootstrap_correlation_ci(
                pd.DataFrame({"a": [0.1] * 20 + [np.nan], "b": [0.1] * 21})
            )

    def test_min_obs_boundary(self):
        """T=MIN_OBS 边界可用；T=MIN_OBS-1 拒绝。"""
        rng = np.random.default_rng(31)
        panel = pd.DataFrame({"a": rng.normal(0, 1, MIN_OBS), "b": rng.normal(0, 1, MIN_OBS)})
        res = bootstrap_correlation_ci(panel, n_bootstrap=10, seed=1)
        assert res.n_obs == MIN_OBS
