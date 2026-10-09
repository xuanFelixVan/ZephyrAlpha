# [BLUEPRINT] MOD-REGIME-VAL | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""E1 walk-forward MaxDD 改善 CV 正式统计单元测试（11_regime_backtest_validation_plan §4.5 E1/§5）."""

from __future__ import annotations

import unittest

from zephyr.regime.validation.e1_walkforward_cv import (
    E1WalkForwardCVError,
    compute_improvement_cv,
    improvements_from_pairs,
)


class TestImprovementsFromPairs(unittest.TestCase):
    def test_positive_convention(self):
        """正值约定（0.22=22% 回撤）：改善 = base − exp。"""
        imps = improvements_from_pairs([(0.2221, 0.1485)])
        self.assertAlmostEqual(imps[0], 0.0736)

    def test_negative_convention(self):
        """负值约定（-0.22）：绝对值统一后同上。"""
        imps = improvements_from_pairs([(-0.2221, -0.1485)])
        self.assertAlmostEqual(imps[0], 0.0736)

    def test_worsening_negative(self):
        imps = improvements_from_pairs([(0.10, 0.15)])
        self.assertAlmostEqual(imps[0], -0.05)


class TestComputeImprovementCV(unittest.TestCase):
    def test_stable_windows_pass(self):
        """46 窗口小幅波动（CV≈0.1）→ 稳定。"""
        improvements = [0.074 + (i % 5 - 2) * 0.002 for i in range(46)]
        rep = compute_improvement_cv(improvements)
        self.assertTrue(rep.passed)
        self.assertLess(rep.cv, 0.5)
        self.assertEqual(rep.n_windows, 46)
        self.assertGreater(rep.mean_improvement, 0.0)

    def test_volatile_windows_fail(self):
        """改善剧烈波动（正负交替，CV>0.5）→ 不稳定。"""
        improvements = [0.10 if i % 2 == 0 else -0.02 for i in range(46)]
        rep = compute_improvement_cv(improvements)
        self.assertFalse(rep.passed)
        self.assertGreaterEqual(rep.cv, 0.5)

    def test_constant_improvement_cv_zero(self):
        """退化：所有窗口改善完全相同 → std=0 → CV=0 → 稳定。"""
        rep = compute_improvement_cv([0.074] * 46)
        self.assertAlmostEqual(rep.cv, 0.0, places=9)
        self.assertTrue(rep.passed)

    def test_zero_mean_nonzero_std_cv_inf(self):
        """退化：均值=0 但 std>0 → CV=inf → 不稳定。"""
        rep = compute_improvement_cv([0.05, -0.05, 0.05, -0.05])
        self.assertEqual(rep.cv, float("inf"))
        self.assertFalse(rep.passed)

    def test_zero_mean_zero_std_cv_zero(self):
        """退化：全零改善 → CV=0 → 稳定（形式上）。"""
        rep = compute_improvement_cv([0.0, 0.0, 0.0])
        self.assertEqual(rep.cv, 0.0)
        self.assertTrue(rep.passed)

    def test_boundary_cv_exactly_threshold_fails(self):
        """边界：CV 恰 =0.5 → 非稳定（门槛为严格 <）。"""
        # [0.25, 0.50, 0.75]：mean=0.5, std(ddof=1)=0.25 → CV=0.5（二进制精确值）
        rep = compute_improvement_cv([0.25, 0.50, 0.75])
        self.assertEqual(rep.cv, 0.5)
        self.assertFalse(rep.passed)

    def test_too_few_windows_raises(self):
        with self.assertRaises(E1WalkForwardCVError):
            compute_improvement_cv([0.074])

    def test_nan_raises(self):
        with self.assertRaises(E1WalkForwardCVError):
            compute_improvement_cv([0.07, float("nan"), 0.08])

    def test_bad_threshold_raises(self):
        with self.assertRaises(E1WalkForwardCVError):
            compute_improvement_cv([0.07, 0.08], cv_threshold=0.0)


if __name__ == "__main__":
    unittest.main()
