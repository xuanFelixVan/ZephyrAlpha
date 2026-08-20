# -*- coding: utf-8 -*-
"""C2 极端事件回撤保护分析单元测试（11_regime_backtest_validation_plan §4.3 C2/§5）."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from zephyr.backtest.regime_validation.c2_extreme_event_protection import (
    C2ProtectionError,
    evaluate_extreme_event_protection,
    max_drawdown_of,
)


def _nav_from_returns(rets: list[float], start: str = "2020-01-01") -> pd.Series:
    idx = pd.bdate_range(start, periods=len(rets))
    return pd.Series(np.cumprod(1.0 + np.asarray(rets)), index=idx)


class TestMaxDrawdownOf(unittest.TestCase):
    def test_monotonic_up_zero_dd(self):
        self.assertEqual(max_drawdown_of([1.0, 1.1, 1.2, 1.3]), 0.0)

    def test_known_drawdown(self):
        # 峰值 1.2 → 谷底 0.9 → DD = 0.9/1.2-1 = -0.25
        self.assertAlmostEqual(max_drawdown_of([1.0, 1.2, 0.9, 1.1]), -0.25)

    def test_empty_returns_zero(self):
        self.assertEqual(max_drawdown_of([]), 0.0)


class TestEvaluateExtremeEventProtection(unittest.TestCase):
    def _two_crisis(self) -> tuple[pd.Series, pd.Series]:
        """两个危机时段：关组深跌（-40%），开组浅跌（-25%）+ 平时同涨。"""
        rng = np.random.default_rng(0)
        calm = rng.normal(0.001, 0.005, 100).tolist()
        crisis1 = [-0.06] * 10  # 关组累计深跌
        mid = rng.normal(0.001, 0.005, 60).tolist()
        crisis2 = [-0.05] * 10
        base_rets = calm + crisis1 + mid + crisis2
        exp_rets = (
            calm
            + [-0.035] * 10  # 开组危机 1 浅跌
            + mid
            + [-0.03] * 10  # 开组危机 2 浅跌
        )
        return _nav_from_returns(base_rets), _nav_from_returns(exp_rets)

    def test_protection_passes(self):
        nav_b, nav_e = self._two_crisis()
        idx = nav_b.index
        windows = [
            ("crisis1", idx[100], idx[109]),
            ("crisis2", idx[170], idx[179]),
        ]
        rep = evaluate_extreme_event_protection(nav_b, nav_e, windows)
        self.assertTrue(rep.passed)
        self.assertEqual(len(rep.events), 2)
        self.assertEqual(rep.skipped, ())
        self.assertGreater(rep.mean_improvement, 0.05)
        for e in rep.events:
            self.assertGreater(e.improvement, 0.0)
            self.assertLess(e.dd_baseline, e.dd_experiment)  # 关组跌更深

    def test_no_protection_fails(self):
        """开组跌得一样深 → 改善≈0 <5pp → 不通过。"""
        rng = np.random.default_rng(1)
        calm = rng.normal(0.001, 0.005, 50).tolist()
        crisis = [-0.05] * 10
        nav_b = _nav_from_returns(calm + crisis)
        nav_e = _nav_from_returns(calm + crisis)  # 完全相同
        idx = nav_b.index
        rep = evaluate_extreme_event_protection(nav_b, nav_e, [("c1", idx[50], idx[59])])
        self.assertFalse(rep.passed)
        self.assertAlmostEqual(rep.mean_improvement, 0.0, places=9)

    def test_sparse_window_skipped(self):
        """样本<2 的时段跳过并留痕；其余正常判定。"""
        nav_b, nav_e = self._two_crisis()
        idx = nav_b.index
        windows = [
            ("ghost", "2031-01-01", "2031-02-01"),  # 范围外 → 空切片
            ("crisis1", idx[100], idx[109]),
            ("crisis2", idx[170], idx[179]),
        ]
        rep = evaluate_extreme_event_protection(nav_b, nav_e, windows)
        self.assertEqual(rep.skipped, ("ghost",))
        self.assertEqual(len(rep.events), 2)
        self.assertTrue(rep.passed)

    def test_all_windows_sparse_raises(self):
        nav_b, nav_e = self._two_crisis()
        with self.assertRaises(C2ProtectionError):
            evaluate_extreme_event_protection(nav_b, nav_e, [("ghost", "2031-01-01", "2031-02-01")])

    def test_empty_windows_raises(self):
        nav_b, nav_e = self._two_crisis()
        with self.assertRaises(C2ProtectionError):
            evaluate_extreme_event_protection(nav_b, nav_e, [])

    def test_nan_nav_raises(self):
        nav_b, nav_e = self._two_crisis()
        nav_b = nav_b.copy()
        nav_b.iloc[5] = float("nan")
        with self.assertRaises(C2ProtectionError):
            evaluate_extreme_event_protection(nav_b, nav_e, [("c1", nav_b.index[100], nav_b.index[109])])

    def test_bad_threshold_raises(self):
        nav_b, nav_e = self._two_crisis()
        with self.assertRaises(C2ProtectionError):
            evaluate_extreme_event_protection(
                nav_b,
                nav_e,
                [("c1", nav_b.index[100], nav_b.index[109])],
                improvement_threshold=0.0,
            )


if __name__ == "__main__":
    unittest.main()
