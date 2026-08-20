# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""C3 节流归因分析单元测试（11_regime_backtest_validation_plan §4.3 C3）."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from zephyr.backtest.regime_validation.c3_throttle_attribution import (
    C3AttributionError,
    attribute_throttle,
)


def _records(spec: dict[str, tuple[int, float, float, float]]) -> pd.DataFrame:
    """spec: {state: (days, mean_shrinkage, mean_ret_base, mean_ret_exp)}（同态内逐日常数）。"""
    rows = []
    for state, (days, shr, rb, re) in spec.items():
        for _ in range(days):
            rows.append({"state": state, "shrinkage": shr, "ret_baseline": rb, "ret_experiment": re})
    return pd.DataFrame(rows)


class TestAttributeThrottle(unittest.TestCase):
    def test_defensive_states_dominate_pass(self):
        """避免损失全部来自 r4+r10（防御态），r3 牛均值 0.95 → 通过。"""
        df = _records(
            {
                "r1": (100, 0.95, 0.0005, 0.0005),  # 震荡：开/关无差
                "r2": (140, 0.92, 0.0006, 0.0006),
                "r3": (60, 0.95, 0.0020, 0.0020),  # 牛市：不缩也无差
                "r4": (80, 0.50, -0.0015, -0.0006),  # 熊市：节流避免损失
                "r10": (20, 0.30, -0.0080, -0.0025),  # CRISIS：强节流
            }
        )
        rep = attribute_throttle(df)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.total_days, 400)
        self.assertAlmostEqual(rep.defensive_share, 1.0)
        self.assertAlmostEqual(rep.bull_mean_shrinkage, 0.95)
        # 状态按天数降序
        self.assertEqual([s.state for s in rep.states], ["r2", "r1", "r4", "r3", "r10"])
        self.assertGreater(rep.total_avoided, 0.0)

    def test_bull_state_contributes_most_fails(self):
        """改善主要来自 r3 牛市（收缩方向错误信号）→ 防御贡献 <60% → 不通过。"""
        df = _records(
            {
                "r3": (100, 0.90, -0.0010, -0.0002),  # 牛市态"贡献"了大头（异常）
                "r4": (100, 0.50, -0.0010, -0.0008),  # 防御态只贡献小头
            }
        )
        rep = attribute_throttle(df)
        self.assertFalse(rep.passed)
        self.assertLess(rep.defensive_share, 0.60)
        # r3 份额 = 0.0008/(0.0008+0.0002) = 80%
        r3 = next(s for s in rep.states if s.state == "r3")
        self.assertAlmostEqual(r3.contribution_share, 0.8)

    def test_bull_over_shrunk_fails(self):
        """r3 平均 Shrinkage 0.70 < 0.85（牛市被乱缩）→ 不通过。"""
        df = _records(
            {
                "r3": (60, 0.70, 0.0020, 0.0020),
                "r4": (100, 0.50, -0.0015, -0.0005),
            }
        )
        rep = attribute_throttle(df)
        self.assertFalse(rep.passed)
        self.assertAlmostEqual(rep.bull_mean_shrinkage, 0.70)

    def test_no_bull_state_vacuous_pass(self):
        """无 r3 样本 → 牛市条款 vacuous 通过，仅看防御贡献。"""
        df = _records(
            {
                "r1": (50, 0.95, 0.0005, 0.0005),
                "r4": (100, 0.50, -0.0015, -0.0005),
            }
        )
        rep = attribute_throttle(df)
        self.assertIsNone(rep.bull_mean_shrinkage)
        self.assertTrue(rep.passed)

    def test_throttle_hurt_overall_fails(self):
        """退化：节流总体净伤害（avoided 全负）→ 正部和=0 → 防御份额=0 → 不通过。"""
        df = _records(
            {
                "r3": (50, 0.90, 0.0020, 0.0010),  # 牛市被缩少赚
                "r4": (50, 0.50, -0.0010, -0.0012),  # 熊市也没保护到
            }
        )
        rep = attribute_throttle(df)
        self.assertFalse(rep.passed)
        self.assertEqual(rep.defensive_share, 0.0)
        self.assertLess(rep.total_avoided, 0.0)

    def test_contribution_shares_sum_to_one(self):
        df = _records(
            {
                "r1": (30, 0.95, 0.0005, 0.0002),
                "r4": (70, 0.50, -0.0015, -0.0005),
                "r10": (20, 0.30, -0.0080, -0.0030),
            }
        )
        rep = attribute_throttle(df)
        self.assertAlmostEqual(sum(s.contribution_share for s in rep.states), 1.0, places=9)

    def test_missing_column_raises(self):
        df = pd.DataFrame({"state": ["r1"], "shrinkage": [0.9]})
        with self.assertRaises(C3AttributionError):
            attribute_throttle(df)

    def test_empty_df_raises(self):
        df = pd.DataFrame(columns=["state", "shrinkage", "ret_baseline", "ret_experiment"])
        with self.assertRaises(C3AttributionError):
            attribute_throttle(df)

    def test_nan_raises(self):
        df = _records({"r4": (10, 0.5, -0.001, -0.0005)})
        df.loc[0, "ret_baseline"] = np.nan
        with self.assertRaises(C3AttributionError):
            attribute_throttle(df)

    def test_shrinkage_above_one_raises(self):
        df = _records({"r4": (10, 1.2, -0.001, -0.0005)})
        with self.assertRaises(C3AttributionError):
            attribute_throttle(df)


if __name__ == "__main__":
    unittest.main()
