# -*- coding: utf-8 -*-
"""D3 聚合公式参数扰动分析单元测试（11_regime_backtest_validation_plan §0.5.7 D3）."""

from __future__ import annotations

import unittest

from zephyr.regime.validation.d3_aggregation_perturbation import (
    D3AggregationError,
    aggregate_risk_signal,
    run_d3_perturbation,
)


class TestAggregateRiskSignal(unittest.TestCase):
    """聚合公式镜像（含 #1 门控 / min 聚合 / 共振 / 恢复 / clamp）。"""

    def test_empty_params_degrades_to_one(self):
        self.assertEqual(aggregate_risk_signal({}), 1.0)

    def test_primary_gating(self):
        """#1=1.0（无风险）→ 附加参数不参与，直接 1.0。"""
        self.assertEqual(aggregate_risk_signal({1: 1.0, 2: 0.3}), 1.0)

    def test_single_anomaly_no_resonance(self):
        """单异常参数：共振=1.0（max(0, 1−1)=0 不扣）。"""
        self.assertAlmostEqual(aggregate_risk_signal({1: 0.9}), 0.9)

    def test_two_anomalies_resonance_step(self):
        """两异常：共振=1−0.05×1=0.95，risk=min×0.95。"""
        self.assertAlmostEqual(aggregate_risk_signal({1: 0.9, 2: 0.8}), 0.8 * 0.95)

    def test_resonance_floor_binds(self):
        """多异常：共振下限 ×0.80 兜底。"""
        params = {i: 0.7 for i in [1, 2, 3, 4, 5, 6]}
        # anomaly=6 → 1−0.05×5=0.75 → floor 0.80
        self.assertAlmostEqual(aggregate_risk_signal(params), 0.7 * 0.80)

    def test_recovery_added_and_capped(self):
        """机会恢复叠加且封顶 +0.25。"""
        base = aggregate_risk_signal({1: 0.9}, opportunity={"news_ghost": 0.10})
        self.assertAlmostEqual(base, 0.9 + 0.10)
        capped = aggregate_risk_signal({1: 0.9}, opportunity={"news_ghost": 0.20, "bad_news_flat": 0.20})
        self.assertAlmostEqual(capped, 1.0)  # 0.9+0.25=1.15 → clamp 1.00

    def test_lower_clamp(self):
        """risk 下限 0.30。"""
        params = {i: 0.31 for i in [1, 2, 3, 4]}
        # base=0.31, anomaly=4 → resonance 0.85 → 0.2635 → clamp 0.30
        self.assertAlmostEqual(aggregate_risk_signal(params), 0.30)

    def test_matches_production_formula(self):
        """与 regime_detector._compute_risk_signal 生产实现逐点一致。"""
        try:
            from zephyr.regime.core.regime_detector import RegimeDetector
        except ImportError:
            self.skipTest("regime_detector 依赖不可用")
        detector = RegimeDetector(shrinkage_enabled=False)
        cases = [
            {"params": {1: 0.85, 2: 1.0, 5: 0.6}},
            {"params": {1: 0.7, 3: 0.8, 12: 0.9}, "opportunity": {"news_ghost": 0.10, "bad_news_flat": 0.05}},
            {"params": {1: 1.0, 7: 0.5}},
            {"params": {}},
        ]
        for risk_inputs in cases:
            prod = detector._compute_risk_signal(risk_inputs)  # noqa: SLF001
            mine = aggregate_risk_signal(risk_inputs.get("params") or {}, risk_inputs.get("opportunity"))
            self.assertAlmostEqual(mine, prod, places=12, msg=f"不一致: {risk_inputs}")


class TestRunD3Perturbation(unittest.TestCase):
    def test_gated_series_fully_robust(self):
        """全部 #1=1.0（门控未触发）→ RiskSignal 恒 1.0，扰动零影响 → 稳健。"""
        series = [{"params": {1: 1.0, 2: 0.5}}] * 30
        rep = run_d3_perturbation(series)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.max_rel_change, 0.0)
        self.assertAlmostEqual(rep.baseline_mean, 1.0)
        self.assertEqual(len(rep.points), 4)  # 2 参数 × 2 方向

    def test_mild_series_robust(self):
        """温和收缩序列：生产 clamp 结构下扰动影响天然 <30% → 稳健。"""
        series = [{"params": {1: 0.9, 2: 0.7}}] * 20 + [{"params": {1: 0.8}, "opportunity": {"news_ghost": 0.10}}] * 20
        rep = run_d3_perturbation(series)
        self.assertTrue(rep.passed)
        self.assertLess(rep.max_rel_change, 0.30)
        for p in rep.points:
            self.assertGreater(p.share_contracted, 0.0)

    def test_strict_tolerance_forces_fail(self):
        """严格 tolerance=5% 下机会恢复主导序列应判敏感（验证判定机制生效）。

        序列 risk=0.35+0.24=0.59；recovery_cap×0.8=0.20 → recovery 压到 0.20
        → risk=0.55，相对变化 6.8% > 5%。
        """
        series = [{"params": {1: 0.35}, "opportunity": {"news_ghost": 0.24}}] * 40
        rep = run_d3_perturbation(series, tolerance=0.05)
        self.assertFalse(rep.passed)
        self.assertGreaterEqual(rep.max_rel_change, 0.05)

    def test_recovery_cap_direction(self):
        """recovery_cap ×0.8 降低含机会项序列的均值（方向正确，且结果低于 clamp 上限）。"""
        series = [{"params": {1: 0.6}, "opportunity": {"news_ghost": 0.20, "bad_news_flat": 0.20}}] * 25
        # 基线: 0.6×1.0 + min(0.4, 0.25)=0.25 → 0.85; cap×0.8=0.2 → 0.6+0.2=0.80
        rep = run_d3_perturbation(series)
        self.assertAlmostEqual(rep.baseline_mean, 0.85)
        cap_down = [p for p in rep.points if p.param == "recovery_cap" and p.factor == 0.8]
        self.assertEqual(len(cap_down), 1)
        self.assertLess(cap_down[0].mean_risk, rep.baseline_mean)
        self.assertAlmostEqual(cap_down[0].mean_risk, 0.80)

    def test_empty_series_raises(self):
        with self.assertRaises(D3AggregationError):
            run_d3_perturbation([])

    def test_bad_pct_raises(self):
        with self.assertRaises(D3AggregationError):
            run_d3_perturbation([{"params": {1: 0.9}}], pct=-0.2)


if __name__ == "__main__":
    unittest.main()
