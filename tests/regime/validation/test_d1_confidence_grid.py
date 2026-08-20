# -*- coding: utf-8 -*-
"""D1 ConfidenceSignal 四档 ±20% 网格分析单元测试（11_regime_backtest_validation_plan §0.5.7 D1）."""

from __future__ import annotations

import unittest

from zephyr.regime.validation.d1_confidence_grid import (
    DEFAULT_CONFIDENCE_BANDS,
    D1ConfidenceGridError,
    apply_confidence_bands,
    run_d1_threshold_grid,
)


class TestApplyConfidenceBands(unittest.TestCase):
    """单点映射（镜像 detector 四档语义）。"""

    def test_band_boundaries(self):
        self.assertEqual(apply_confidence_bands(0.60), 1.0)  # ≥0.50 满部署
        self.assertEqual(apply_confidence_bands(0.50), 1.0)  # 边界命中高档
        self.assertEqual(apply_confidence_bands(0.40), 0.9)  # 30-50%
        self.assertEqual(apply_confidence_bands(0.30), 0.9)
        self.assertEqual(apply_confidence_bands(0.20), 0.8)  # 15-30%
        self.assertEqual(apply_confidence_bands(0.15), 0.8)
        self.assertEqual(apply_confidence_bands(0.10), 0.7)  # <15% 防御档
        self.assertEqual(apply_confidence_bands(0.0), 0.7)

    def test_empty_bands_fallback(self):
        self.assertEqual(apply_confidence_bands(0.5, bands=()), 1.0)


class TestRunD1ThresholdGrid(unittest.TestCase):
    def test_uniform_high_confidence_robust(self):
        """全部 max(P)=0.9（远高于扰动后任何档界）→ 均值不变 → 稳健。"""
        rep = run_d1_threshold_grid([0.9] * 100)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.max_rel_change, 0.0)
        self.assertAlmostEqual(rep.baseline_mean, 1.0)
        # 默认档界间距足够，27 组合全合法
        self.assertEqual(rep.n_skipped, 0)
        self.assertEqual(len(rep.points), 27)

    def test_baseline_point_included(self):
        """网格含基线点（factor 全 1.0），其 rel_change=0。"""
        rep = run_d1_threshold_grid([0.45] * 50)
        base_points = [p for p in rep.points if p.thresholds == (0.50, 0.30, 0.15)]
        self.assertEqual(len(base_points), 1)
        self.assertEqual(base_points[0].rel_change, 0.0)
        self.assertAlmostEqual(base_points[0].mean_confidence, rep.baseline_mean)

    def test_mass_near_boundary_moves_bands(self):
        """全部 max(P)=0.32：基线落 0.9 档；t2×1.2=0.36 后跌落到 0.8 档。"""
        rep = run_d1_threshold_grid([0.32] * 80)
        moved = [p for p in rep.points if abs(p.thresholds[1] - 0.36) < 1e-9 and abs(p.thresholds[0] - 0.50) < 1e-9]
        self.assertTrue(moved)
        for p in moved:
            self.assertAlmostEqual(p.mean_confidence, 0.8)
        self.assertAlmostEqual(rep.baseline_mean, 0.9)

    def test_wide_coef_bands_can_fail(self):
        """自定义宽系数档（1.0→0.4 大跳变）：质量集中档界上方 → 扰动后均值骤降 ≥30% → 敏感。"""
        wide_bands = ((0.50, 1.0), (0.30, 0.4), (0.15, 0.3), (0.0, 0.2))
        rep = run_d1_threshold_grid([0.55] * 60, bands=wide_bands)
        self.assertFalse(rep.passed)
        self.assertGreaterEqual(rep.max_rel_change, 0.30)

    def test_close_bands_produce_skips(self):
        """档界间距 < 扰动幅度时部分组合非严格降序 → 跳过计数 >0。"""
        close_bands = ((0.31, 1.0), (0.30, 0.9), (0.15, 0.8), (0.0, 0.7))
        rep = run_d1_threshold_grid([0.9] * 30, bands=close_bands)
        self.assertGreater(rep.n_skipped, 0)
        self.assertLess(len(rep.points), 27)

    def test_band_shares_sum_to_one(self):
        rep = run_d1_threshold_grid([0.6, 0.4, 0.2, 0.1] * 25)
        for p in rep.points:
            self.assertAlmostEqual(sum(p.band_shares), 1.0, places=9)

    def test_empty_series_raises(self):
        with self.assertRaises(D1ConfidenceGridError):
            run_d1_threshold_grid([])

    def test_out_of_range_raises(self):
        with self.assertRaises(D1ConfidenceGridError):
            run_d1_threshold_grid([0.5, 1.2])

    def test_nan_raises(self):
        with self.assertRaises(D1ConfidenceGridError):
            run_d1_threshold_grid([0.5, float("nan")])

    def test_bad_bands_raises(self):
        with self.assertRaises(D1ConfidenceGridError):
            run_d1_threshold_grid([0.5] * 10, bands=((0.3, 1.0), (0.5, 0.9)))

    def test_bad_pct_raises(self):
        with self.assertRaises(D1ConfidenceGridError):
            run_d1_threshold_grid([0.5] * 10, pct=0.0)


if __name__ == "__main__":
    unittest.main()
