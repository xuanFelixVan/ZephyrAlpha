# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""E3 参数敏感性 ±20% 网格分析单元测试（11_regime_backtest_validation_plan §4.4/§4.5 E3）."""

from __future__ import annotations

import unittest

from zephyr.backtest.regime_validation.e3_param_sensitivity import (
    E3PerturbationPoint,
    E3SensitivityError,
    analyze_param_sensitivity,
    perturb_pm20,
)


def _grid(baseline: float, changes: dict[str, tuple[float, float]]) -> list[E3PerturbationPoint]:
    """changes: {参数名: (−20% 效果, +20% 效果)}。"""
    return [
        E3PerturbationPoint(name=n, factor=f, effect=e)
        for n, (lo, hi) in changes.items()
        for f, e in ((0.8, lo), (1.2, hi))
    ]


class TestPerturbPm20(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(perturb_pm20(0.5), (0.4, 0.6))

    def test_zero(self):
        self.assertEqual(perturb_pm20(0.0), (0.0, 0.0))


class TestAnalyzeParamSensitivity(unittest.TestCase):
    def test_all_robust_passes(self):
        """全部参数相对变化 <30% → 稳健。"""
        baseline = 0.074  # C1 实测 MaxDD 改善 7.4pp
        pts = _grid(
            baseline,
            {
                "conf_t1": (0.070, 0.078),  # ±5%
                "resonance": (0.062, 0.081),  # ±10-16%
            },
        )
        rep = analyze_param_sensitivity(baseline, pts)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.cliff_params, ())
        self.assertLess(rep.max_rel_change, 0.30)
        self.assertEqual(len(rep.verdicts), 2)

    def test_cliff_param_detected(self):
        """存在悬崖参数（相对变化 ≥30%）→ 不通过 + 点名。"""
        baseline = 0.074
        pts = _grid(
            baseline,
            {
                "conf_t1": (0.070, 0.078),
                "recovery_cap": (0.010, 0.074),  # −20% 方向效果骤降 86%
            },
        )
        rep = analyze_param_sensitivity(baseline, pts)
        self.assertFalse(rep.passed)
        self.assertEqual(rep.cliff_params, ("recovery_cap",))
        verdict = {v.name: v for v in rep.verdicts}["recovery_cap"]
        self.assertFalse(verdict.robust)
        self.assertAlmostEqual(verdict.worst_effect, 0.010)

    def test_exactly_at_tolerance_is_cliff(self):
        """边界：相对变化恰 =30% → 非稳健（门槛为严格 <）。"""
        baseline = 0.10
        pts = [E3PerturbationPoint("p1", 0.8, 0.07)]  # |0.07-0.10|/0.10 = 0.30
        rep = analyze_param_sensitivity(baseline, pts, tolerance=0.30)
        self.assertFalse(rep.passed)
        self.assertEqual(rep.cliff_params, ("p1",))

    def test_zero_baseline_zero_perturbation_robust(self):
        """退化：基线效果=0 且扰动后仍≈0 → 相对变化 0 → 稳健。"""
        pts = _grid(0.0, {"p1": (0.0, 0.0)})
        rep = analyze_param_sensitivity(0.0, pts)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.max_rel_change, 0.0)

    def test_zero_baseline_nonzero_perturbation_cliff(self):
        """退化：基线=0 但扰动后非零 → 相对变化 inf → 悬崖。"""
        pts = [E3PerturbationPoint("p1", 1.2, 0.05)]
        rep = analyze_param_sensitivity(0.0, pts)
        self.assertFalse(rep.passed)
        self.assertEqual(rep.max_rel_change, float("inf"))

    def test_empty_points_raises(self):
        with self.assertRaises(E3SensitivityError):
            analyze_param_sensitivity(0.07, [])

    def test_bad_tolerance_raises(self):
        pts = [E3PerturbationPoint("p1", 0.8, 0.07)]
        with self.assertRaises(E3SensitivityError):
            analyze_param_sensitivity(0.07, pts, tolerance=0.0)

    def test_nan_effect_raises(self):
        pts = [E3PerturbationPoint("p1", 0.8, float("nan"))]
        with self.assertRaises(E3SensitivityError):
            analyze_param_sensitivity(0.07, pts)


if __name__ == "__main__":
    unittest.main()
