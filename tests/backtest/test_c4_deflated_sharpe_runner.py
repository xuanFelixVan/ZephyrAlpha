# -*- coding: utf-8 -*-
"""C4 Deflated Sharpe 跑批封装入口单元测试（11_regime_backtest_validation_plan §0.6.3/§4.3 C4）."""

from __future__ import annotations

import unittest

import numpy as np

from zephyr.backtest.regime_validation.c4_deflated_sharpe_runner import (
    C4DeflatedSharpeError,
    run_deflated_sharpe_batch,
)


def _drift_returns(n: int, mean: float, std: float, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    return rng.normal(mean, std, n).tolist()


class TestRunDeflatedSharpeBatch(unittest.TestCase):
    def test_strong_drift_significant_passes(self):
        """强正漂移（SR 高 + 样本足）→ 最优变体 DSR≥0.95 → passed。"""
        variants = {
            "shrink_on": _drift_returns(750, 0.0015, 0.01, 0),
            "shrink_off": _drift_returns(750, 0.0012, 0.01, 1),
        }
        rep = run_deflated_sharpe_batch(variants)
        self.assertEqual(rep.num_variants, 2)
        self.assertEqual(rep.num_trials, 2)  # 默认=变体数
        self.assertEqual(rep.best_variant, "shrink_on")
        self.assertTrue(rep.is_significant)
        self.assertTrue(rep.passed)
        self.assertGreater(rep.best_dsr, 0.95)
        # 按年化 Sharpe 降序
        sharpes = [v.sharpe_annualized for v in rep.variants]
        self.assertEqual(sharpes, sorted(sharpes, reverse=True))

    def test_zero_drift_not_significant(self):
        """零均值噪声 → Sharpe≈0 → DSR 不显著 → 不通过（效果可能是运气）。"""
        variants = {"noise": _drift_returns(500, 0.0, 0.01, 2)}
        rep = run_deflated_sharpe_batch(variants)
        self.assertEqual(rep.num_trials, 1)
        self.assertFalse(rep.is_significant)
        self.assertFalse(rep.passed)

    def test_more_trials_deflates_dsr(self):
        """同一序列：num_trials 越大（试过越多变体）→ DSR 越低（多重比较打折）。"""
        rets = _drift_returns(750, 0.0012, 0.01, 3)
        few = run_deflated_sharpe_batch({"a": rets}, num_trials=1)
        many = run_deflated_sharpe_batch({"a": rets}, num_trials=100)
        self.assertGreater(few.best_dsr, many.best_dsr)
        self.assertEqual(many.num_trials, 100)

    def test_best_variant_is_max_sharpe(self):
        """best_variant = 年化 Sharpe 最高者（非 DSR 最高者）。"""
        variants = {
            "weak": _drift_returns(400, 0.0005, 0.01, 4),
            "strong": _drift_returns(400, 0.0018, 0.01, 5),
            "mid": _drift_returns(400, 0.0010, 0.01, 6),
        }
        rep = run_deflated_sharpe_batch(variants)
        self.assertEqual(rep.best_variant, "strong")
        self.assertEqual(rep.variants[0].name, "strong")
        self.assertEqual(rep.variants[-1].name, "weak")

    def test_empty_variants_raises(self):
        with self.assertRaises(C4DeflatedSharpeError):
            run_deflated_sharpe_batch({})

    def test_short_series_raises(self):
        with self.assertRaises(C4DeflatedSharpeError):
            run_deflated_sharpe_batch({"a": [0.01, 0.02]})

    def test_nan_series_raises(self):
        with self.assertRaises(C4DeflatedSharpeError):
            run_deflated_sharpe_batch({"a": [0.01, float("nan"), 0.02, 0.03]})

    def test_bad_num_trials_raises(self):
        with self.assertRaises(C4DeflatedSharpeError):
            run_deflated_sharpe_batch({"a": _drift_returns(50, 0.001, 0.01, 7)}, num_trials=0)


if __name__ == "__main__":
    unittest.main()
