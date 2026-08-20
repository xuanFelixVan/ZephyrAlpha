# -*- coding: utf-8 -*-
"""E4 交易成本敏感性 0-50bps 分析单元测试（11_regime_backtest_validation_plan §4.5 E4）."""

from __future__ import annotations

import unittest

from zephyr.backtest.regime_validation.e4_cost_sensitivity import (
    E4CostPoint,
    E4CostSensitivityError,
    analyze_cost_sensitivity,
)


def _design_grid(effects: list[float]) -> list[E4CostPoint]:
    """§4.5 E4 设计网格 0/2/5/10/50bps。"""
    costs = [0.0, 2.0, 5.0, 10.0, 50.0]
    return [E4CostPoint(cost_bps=c, effect=e) for c, e in zip(costs, effects, strict=True)]


class TestAnalyzeCostSensitivity(unittest.TestCase):
    def test_all_positive_consistent_passes(self):
        """0-50bps 全网格效果为正 → 方向一致 → 稳健。"""
        rep = analyze_cost_sensitivity(_design_grid([0.074, 0.072, 0.070, 0.066, 0.041]))
        self.assertTrue(rep.passed)
        self.assertTrue(rep.direction_consistent)
        self.assertEqual(rep.direction, 1)
        self.assertTrue(rep.covers_design_range)
        self.assertAlmostEqual(rep.min_effect, 0.041)
        self.assertAlmostEqual(rep.max_effect, 0.074)
        # 输出按成本升序
        self.assertEqual([p.cost_bps for p in rep.points], [0.0, 2.0, 5.0, 10.0, 50.0])

    def test_all_negative_consistent_but_flagged(self):
        """全负 = 方向一致（节流稳定为负效果）→ passed 但 direction=-1。"""
        rep = analyze_cost_sensitivity(_design_grid([-0.01, -0.02, -0.02, -0.03, -0.05]))
        self.assertTrue(rep.direction_consistent)
        self.assertEqual(rep.direction, -1)
        self.assertTrue(rep.passed)

    def test_sign_flip_inconsistent_fails(self):
        """高成本点效果翻负 → 方向不一致 → 不稳健。"""
        rep = analyze_cost_sensitivity(_design_grid([0.074, 0.070, 0.065, 0.060, -0.005]))
        self.assertFalse(rep.passed)
        self.assertEqual(rep.direction, 0)

    def test_zero_effect_inconsistent(self):
        """退化：某点效果恰为 0 → 非同号 → 不一致。"""
        rep = analyze_cost_sensitivity(_design_grid([0.074, 0.070, 0.0, 0.060, 0.040]))
        self.assertFalse(rep.direction_consistent)

    def test_partial_coverage_warns_not_fails(self):
        """网格未覆盖 0-50bps 设计范围 → covers_design_range=False 但仍按方向判定。"""
        pts = [E4CostPoint(0.0, 0.07), E4CostPoint(10.0, 0.06)]
        rep = analyze_cost_sensitivity(pts)
        self.assertTrue(rep.passed)
        self.assertFalse(rep.covers_design_range)

    def test_unsorted_input_sorted(self):
        pts = [E4CostPoint(50.0, 0.04), E4CostPoint(0.0, 0.07), E4CostPoint(10.0, 0.06)]
        rep = analyze_cost_sensitivity(pts)
        self.assertEqual([p.cost_bps for p in rep.points], [0.0, 10.0, 50.0])

    def test_too_few_points_raises(self):
        with self.assertRaises(E4CostSensitivityError):
            analyze_cost_sensitivity([E4CostPoint(0.0, 0.07)])

    def test_duplicate_cost_raises(self):
        pts = [E4CostPoint(5.0, 0.07), E4CostPoint(5.0, 0.06)]
        with self.assertRaises(E4CostSensitivityError):
            analyze_cost_sensitivity(pts)

    def test_bad_range_raises(self):
        with self.assertRaises(E4CostSensitivityError):
            analyze_cost_sensitivity(_design_grid([0.07] * 5), cost_min=50.0, cost_max=0.0)

    def test_nan_effect_raises(self):
        with self.assertRaises(E4CostSensitivityError):
            analyze_cost_sensitivity([E4CostPoint(0.0, float("nan")), E4CostPoint(50.0, 0.04)])


if __name__ == "__main__":
    unittest.main()
