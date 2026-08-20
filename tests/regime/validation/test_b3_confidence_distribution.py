# -*- coding: utf-8 -*-
"""B3 置信度合理性分析单元测试（11_regime_backtest_validation_plan §4.2 B3）."""

from __future__ import annotations

import unittest

import numpy as np

from zephyr.regime.validation.b3_confidence_distribution import (
    B3ConfidenceError,
    analyze_confidence_distribution,
)


def _spread(n: int = 400) -> np.ndarray:
    """四档均有覆盖的合理分布（30/30/25/15%）。"""
    rng = np.random.default_rng(0)
    return np.concatenate(
        [
            rng.uniform(0.30, 0.59, int(n * 0.30)),
            rng.uniform(0.61, 0.79, int(n * 0.30)),
            rng.uniform(0.81, 0.94, int(n * 0.25)),
            rng.uniform(0.96, 1.00, n - int(n * 0.30) - int(n * 0.30) - int(n * 0.25)),
        ]
    )


class TestAnalyzeConfidenceDistribution(unittest.TestCase):
    def test_balanced_distribution_passes(self):
        rep = analyze_confidence_distribution(_spread())
        self.assertTrue(rep.passed)
        self.assertEqual(rep.dead_buckets, ())
        self.assertLess(rep.low_share, 0.40)
        self.assertLess(rep.high_share, 0.50)
        self.assertAlmostEqual(sum(rep.bucket_shares), 1.0, places=9)
        self.assertEqual(rep.n, 400)
        # 分位数单调
        self.assertLessEqual(rep.p10, rep.p25)
        self.assertLessEqual(rep.p25, rep.median)
        self.assertLessEqual(rep.median, rep.p75)
        self.assertLessEqual(rep.p75, rep.p90)

    def test_chronically_low_confidence_fails(self):
        """长期低置信（<60% 占比 70% > 40%）→ 节流器变急停器 → 不合理。"""
        rng = np.random.default_rng(1)
        vals = np.concatenate(
            [
                rng.uniform(0.25, 0.55, 350),
                rng.uniform(0.61, 0.79, 50),
                rng.uniform(0.81, 0.94, 50),
                rng.uniform(0.96, 1.0, 50),
            ]
        )
        rep = analyze_confidence_distribution(vals)
        self.assertFalse(rep.passed)
        self.assertGreater(rep.low_share, 0.40)

    def test_chronically_high_confidence_fails(self):
        """长期高置信（>95% 占比 60% > 50%）→ 四档形同虚设 → 不合理。"""
        rng = np.random.default_rng(2)
        vals = np.concatenate(
            [
                rng.uniform(0.30, 0.55, 50),
                rng.uniform(0.61, 0.79, 50),
                rng.uniform(0.81, 0.94, 100),
                rng.uniform(0.96, 1.0, 300),
            ]
        )
        rep = analyze_confidence_distribution(vals)
        self.assertFalse(rep.passed)
        self.assertGreater(rep.high_share, 0.50)

    def test_dead_bucket_fails(self):
        """死档（80-95% 桶为空）→ 不合理。"""
        rng = np.random.default_rng(3)
        vals = np.concatenate(
            [
                rng.uniform(0.30, 0.55, 150),
                rng.uniform(0.61, 0.79, 150),
                rng.uniform(0.96, 1.0, 100),
            ]
        )
        rep = analyze_confidence_distribution(vals)
        self.assertFalse(rep.passed)
        self.assertIn("mid_high(e2-e3)", rep.dead_buckets)

    def test_custom_edges_for_production_bands(self):
        """生产档界（0.15/0.30/0.50）下同一分布重判：边界可配。"""
        rng = np.random.default_rng(4)
        vals = np.concatenate(
            [
                rng.uniform(0.26, 0.29, 100),  # 4 态均匀带（0.15-0.30）
                rng.uniform(0.31, 0.49, 150),  # 30-50%
                rng.uniform(0.51, 0.90, 150),  # ≥50%
            ]
        )
        rep = analyze_confidence_distribution(vals, edges=(0.15, 0.30, 0.50), low_share_max=0.40, high_share_max=0.60)
        self.assertEqual(rep.n, 400)
        self.assertLess(rep.low_share, 0.40)

    def test_uniform_constant_degenerate(self):
        """退化：全部同值 → 单桶 100%，三死档 → 不合理。"""
        rep = analyze_confidence_distribution([0.7] * 100)
        self.assertFalse(rep.passed)
        self.assertEqual(len(rep.dead_buckets), 3)
        self.assertEqual(rep.bucket_shares[1], 1.0)

    def test_empty_raises(self):
        with self.assertRaises(B3ConfidenceError):
            analyze_confidence_distribution([])

    def test_out_of_range_raises(self):
        with self.assertRaises(B3ConfidenceError):
            analyze_confidence_distribution([0.5, 1.1])

    def test_bad_edges_raises(self):
        with self.assertRaises(B3ConfidenceError):
            analyze_confidence_distribution([0.5] * 10, edges=(0.8, 0.6, 0.95))

    def test_bad_share_threshold_raises(self):
        with self.assertRaises(B3ConfidenceError):
            analyze_confidence_distribution([0.5] * 10, low_share_max=1.5)


if __name__ == "__main__":
    unittest.main()
