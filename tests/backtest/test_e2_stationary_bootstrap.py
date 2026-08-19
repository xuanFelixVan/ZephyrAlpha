# -*- coding: utf-8 -*-
"""E2 stationary bootstrap 单元测试（11_regime_backtest_validation_plan §0.6.3/§4.3 C4）."""
from __future__ import annotations

import unittest

import numpy as np

from zephyr.backtest.regime_validation.e2_stationary_bootstrap import (
    E2BootstrapConfig,
    E2BootstrapError,
    annualized_sharpe,
    bootstrap_sharpe_difference,
    stationary_bootstrap_indices,
)


class TestStationaryBootstrapIndices(unittest.TestCase):
    """索引生成器核心逻辑。"""

    def test_indices_in_range_and_length(self):
        rng = np.random.default_rng(0)
        idx = stationary_bootstrap_indices(100, mean_block=10, rng=rng)
        self.assertEqual(len(idx), 100)
        self.assertTrue((idx >= 0).all() and (idx < 100).all())

    def test_reproducible_with_same_seed(self):
        i1 = stationary_bootstrap_indices(50, 5, np.random.default_rng(7))
        i2 = stationary_bootstrap_indices(50, 5, np.random.default_rng(7))
        np.testing.assert_array_equal(i1, i2)

    def test_mean_block_one_is_iid_resample(self):
        """mean_block=1 → p=1.0，每步都重开新块 = iid 有放回抽样。"""
        rng = np.random.default_rng(1)
        idx = stationary_bootstrap_indices(200, mean_block=1, rng=rng)
        # iid 抽样下相邻索引顺移的概率极低；统计顺移占比应远小于 50%
        continuation = np.mean(idx[1:] == (idx[:-1] + 1) % 200)
        self.assertLess(continuation, 0.2)

    def test_large_mean_block_mostly_continues(self):
        """mean_block 很大 → 几乎全部顺移（环形）。"""
        rng = np.random.default_rng(2)
        idx = stationary_bootstrap_indices(100, mean_block=10_000, rng=rng)
        continuation = np.mean(idx[1:] == (idx[:-1] + 1) % 100)
        self.assertGreater(continuation, 0.99)

    def test_n_too_small_raises(self):
        with self.assertRaises(E2BootstrapError):
            stationary_bootstrap_indices(1, 5, np.random.default_rng(0))

    def test_mean_block_zero_raises(self):
        with self.assertRaises(E2BootstrapError):
            stationary_bootstrap_indices(10, 0, np.random.default_rng(0))


class TestAnnualizedSharpe(unittest.TestCase):
    def test_constant_returns_zero_sharpe(self):
        """零波动退化：Sharpe=0。"""
        self.assertEqual(annualized_sharpe([0.001] * 50), 0.0)

    def test_too_short_returns_zero(self):
        self.assertEqual(annualized_sharpe([0.01]), 0.0)
        self.assertEqual(annualized_sharpe([]), 0.0)

    def test_positive_drift_positive_sharpe(self):
        rng = np.random.default_rng(3)
        rets = rng.normal(0.001, 0.01, 500)
        self.assertGreater(annualized_sharpe(rets), 0.0)


class TestBootstrapSharpeDifference(unittest.TestCase):
    """成对差值 bootstrap 主入口。"""

    def test_clearly_better_on_passes(self):
        """开组明显优于关组 → P(diff>0)≈1 → passed。"""
        rng = np.random.default_rng(10)
        off = rng.normal(0.0002, 0.01, 400)
        on = off + 0.0012  # 配对增量：开组系统性更优
        cfg = E2BootstrapConfig(n_boot=500, mean_block=10, seed=5)
        res = bootstrap_sharpe_difference(on, off, cfg)
        self.assertGreater(res.observed_diff, 0.0)
        self.assertGreater(res.prob_positive, 0.95)
        self.assertTrue(res.passed)
        self.assertLess(res.ci_lower, res.ci_upper)
        self.assertEqual(res.n_boot, 500)
        self.assertEqual(res.mean_block, 10)

    def test_clearly_worse_on_fails(self):
        """开组明显更差 → P(diff>0)≈0 → 不通过。"""
        rng = np.random.default_rng(11)
        off = rng.normal(0.0008, 0.01, 400)
        on = off - 0.0012
        cfg = E2BootstrapConfig(n_boot=500, mean_block=10, seed=6)
        res = bootstrap_sharpe_difference(on, off, cfg)
        self.assertLess(res.observed_diff, 0.0)
        self.assertLess(res.prob_positive, 0.05)
        self.assertFalse(res.passed)

    def test_identical_series_zero_diff(self):
        """退化：两组完全相同 → diff 恒 0，P(diff>0)=0 → 不通过（无效果即不显著）。"""
        rng = np.random.default_rng(12)
        rets = rng.normal(0.0005, 0.01, 300)
        cfg = E2BootstrapConfig(n_boot=200, mean_block=10, seed=7)
        res = bootstrap_sharpe_difference(rets, rets.copy(), cfg)
        self.assertAlmostEqual(res.observed_diff, 0.0, places=12)
        self.assertEqual(res.prob_positive, 0.0)
        self.assertFalse(res.passed)

    def test_empty_series_raises(self):
        with self.assertRaises(E2BootstrapError):
            bootstrap_sharpe_difference([], [0.01, 0.02])

    def test_length_mismatch_raises(self):
        with self.assertRaises(E2BootstrapError):
            bootstrap_sharpe_difference([0.01, 0.02, 0.03], [0.01, 0.02])

    def test_nan_raises(self):
        with self.assertRaises(E2BootstrapError):
            bootstrap_sharpe_difference([0.01, float("nan"), 0.02], [0.01, 0.02, 0.03])

    def test_n_boot_zero_raises(self):
        cfg = E2BootstrapConfig(n_boot=0)
        with self.assertRaises(E2BootstrapError):
            bootstrap_sharpe_difference([0.01, 0.02, 0.03], [0.01, 0.02, 0.03], cfg)


if __name__ == "__main__":
    unittest.main()
