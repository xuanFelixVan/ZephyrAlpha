# -*- coding: utf-8 -*-
"""B2 CRPS 概率预测技能单元测试（11_regime_backtest_validation_plan §4.2 B2）."""
from __future__ import annotations

import unittest

import numpy as np

from zephyr.regime.validation.b2_crps import (
    B2CRPSError,
    crps_categorical,
    evaluate_crps,
)


class TestCrpsCategorical(unittest.TestCase):
    def test_perfect_prediction_zero(self):
        """概率全部押中结局 → CRPS=0。"""
        self.assertAlmostEqual(crps_categorical([0.0, 1.0, 0.0, 0.0], 1), 0.0)

    def test_uniform_outcome_zero(self):
        """4 态均匀分布 + 结局 0：CDF(0.25,0.5,0.75,1) vs 指示(1,1,1,1)。"""
        expected = 0.75**2 + 0.50**2 + 0.25**2 + 0.0**2
        self.assertAlmostEqual(crps_categorical([0.25] * 4, 0), expected)

    def test_uniform_outcome_last(self):
        """结局在最后一态：指示 (0,0,0,1)。"""
        expected = 0.25**2 + 0.50**2 + 0.75**2 + 0.0**2
        self.assertAlmostEqual(crps_categorical([0.25] * 4, 3), expected)

    def test_confident_wrong_high_crps(self):
        """自信押错（[0.9,0.1] 结局=1）→ CRPS 高。"""
        val = crps_categorical([0.9, 0.1], 1)
        self.assertAlmostEqual(val, 0.9**2 + 0.0**2)
        self.assertGreater(val, 0.5)

    def test_probs_not_sum_one_raises(self):
        with self.assertRaises(B2CRPSError):
            crps_categorical([0.5, 0.4], 0)

    def test_negative_prob_raises(self):
        with self.assertRaises(B2CRPSError):
            crps_categorical([1.2, -0.2], 0)

    def test_outcome_out_of_range_raises(self):
        with self.assertRaises(B2CRPSError):
            crps_categorical([0.5, 0.5], 2)


class TestEvaluateCrps(unittest.TestCase):
    def _skilled(self, n: int = 200) -> tuple[np.ndarray, np.ndarray]:
        """80% 态 0 / 20% 态 1，模型逐样本高置信押中 → 有技能。"""
        rng = np.random.default_rng(0)
        outcomes = (rng.random(n) < 0.2).astype(int)
        P = np.where(
            outcomes[:, None] == 0,
            np.array([0.9, 0.05, 0.05]),
            np.array([0.05, 0.9, 0.05]),
        )
        return P, outcomes

    def test_skilled_model_passes(self):
        P, y = self._skilled()
        rep = evaluate_crps(P, y)
        self.assertTrue(rep.passed)
        self.assertLess(rep.crps_model, rep.crps_climatology)
        self.assertGreater(rep.skill, 0.5)
        self.assertEqual(rep.n_samples, 200)
        self.assertEqual(rep.n_states, 3)

    def test_uniform_model_fails(self):
        """恒预测均匀分布 → 差于 climatology（结局集中）→ 无技能。"""
        P, y = self._skilled()
        P_uniform = np.full_like(P, 1.0 / 3.0)
        rep = evaluate_crps(P_uniform, y)
        self.assertFalse(rep.passed)
        self.assertLess(rep.skill, 0.0)

    def test_climatology_copy_is_zero_skill(self):
        """模型=经验频率常数 → model==clim → 不通过（不优于基准）。"""
        P, y = self._skilled()
        freq = np.bincount(y, minlength=3) / len(y)
        P_clim = np.tile(freq, (len(y), 1))
        rep = evaluate_crps(P_clim, y)
        self.assertFalse(rep.passed)
        self.assertAlmostEqual(rep.skill, 0.0, places=9)

    def test_single_class_outcomes_raises(self):
        """退化：结局全同 → climatology CRPS=0 → 无法评估技能 → 抛错。"""
        P = np.tile([0.8, 0.1, 0.1], (50, 1))
        with self.assertRaises(B2CRPSError):
            evaluate_crps(P, np.zeros(50, dtype=int))

    def test_length_mismatch_raises(self):
        P, y = self._skilled(20)
        with self.assertRaises(B2CRPSError):
            evaluate_crps(P, y[:-1])

    def test_outcome_out_of_range_raises(self):
        P, y = self._skilled(20)
        y[0] = 7
        with self.assertRaises(B2CRPSError):
            evaluate_crps(P, y)

    def test_1d_prob_matrix_raises(self):
        with self.assertRaises(B2CRPSError):
            evaluate_crps(np.zeros(10), np.zeros(10, dtype=int))


if __name__ == "__main__":
    unittest.main()
