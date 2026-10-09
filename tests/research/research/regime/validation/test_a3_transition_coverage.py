# [BLUEPRINT] MOD-REGIME-VAL | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""A3 状态转移路径覆盖正式统计单元测试（11_regime_backtest_validation_plan §4.1 A3）."""

from __future__ import annotations

import unittest

from zephyr.regime.validation.a3_transition_coverage import (
    A3CoverageError,
    compute_path_coverage,
)

# 4 态 + overlay 的 spec §4 合法路径样例（测试用，非生产真源）
SPEC_PATHS = {
    ("r1", "r12"),
    ("r2", "r12"),  # T1 震荡→BREAKOUT
    ("r4", "r11"),  # T2 熊市→RECOVERY
    ("r11", "r12"),  # T3 RECOVERY→BREAKOUT
    ("r3", "r4"),  # T5 牛市→熊市
    ("r4", "r10"),  # S1 恐慌触发
    ("r10", "r11"),  # S2 复苏确认
    ("r1", "r2"),
    ("r2", "r1"),  # 震荡互转
    ("r1", "r3"),
    ("r2", "r3"),
    ("r3", "r2"),
    ("r3", "r1"),  # 常规迁移
    ("r4", "r1"),
    ("r4", "r2"),
}


class TestComputePathCoverage(unittest.TestCase):
    def test_full_coverage_passes(self):
        """全部转移落在 spec 路径 → coverage=100% → 通过。"""
        seq = ["r1", "r1", "r2", "r2", "r3", "r4", "r10", "r11", "r12", "r12"]
        rep = compute_path_coverage(seq, SPEC_PATHS)
        self.assertEqual(rep.coverage, 1.0)
        self.assertTrue(rep.passed)
        # 自环 r1→r1/r2→r2/r12→r12 已剔除；6 次态间转移全部落在 spec 路径
        self.assertEqual(rep.total_transitions, 6)
        self.assertEqual(rep.covered_transitions, 6)
        self.assertEqual(rep.top_uncovered, ())

    def test_partial_coverage_fails(self):
        """含 spec 外路径（r3→r10 跳态 / r11→r1 回跳）拉低覆盖率 <80% → 不通过。"""
        seq = ["r1", "r3", "r10", "r11", "r1"]  # r3→r10 与 r11→r1 不在 spec
        rep = compute_path_coverage(seq, SPEC_PATHS)
        # 4 次转移, 2 次覆盖（r1→r3 / r10→r11）→ 50% < 80%
        self.assertAlmostEqual(rep.coverage, 0.5)
        self.assertFalse(rep.passed)
        self.assertEqual(len(rep.top_uncovered), 2)
        for u in rep.top_uncovered:
            self.assertEqual(u.count, 1)
            self.assertAlmostEqual(u.share, 0.25)
        uncovered_paths = {(u.from_state, u.to_state) for u in rep.top_uncovered}
        self.assertEqual(uncovered_paths, {("r3", "r10"), ("r11", "r1")})

    def test_self_loops_excluded_by_default(self):
        """长自环序列：仅 1 次真实转移，覆盖率按 1 次计。"""
        seq = ["r2"] * 50 + ["r3"] * 50
        rep = compute_path_coverage(seq, SPEC_PATHS)
        self.assertEqual(rep.total_transitions, 1)
        self.assertEqual(rep.coverage, 1.0)

    def test_self_loops_included_when_disabled(self):
        """exclude_self=False：自环计入分母且不在 spec → 覆盖率被稀释。"""
        seq = ["r2"] * 10 + ["r3"] * 10
        rep = compute_path_coverage(seq, SPEC_PATHS, exclude_self=False)
        self.assertEqual(rep.total_transitions, 19)
        self.assertLess(rep.coverage, 0.2)

    def test_single_state_sequence_vacuous_pass(self):
        """退化：单态持续（无任何转移）→ 空集真 coverage=1.0 → 通过。"""
        rep = compute_path_coverage(["r4"] * 100, SPEC_PATHS)
        self.assertEqual(rep.total_transitions, 0)
        self.assertEqual(rep.coverage, 1.0)
        self.assertTrue(rep.passed)
        self.assertEqual(rep.n_distinct_paths, 0)

    def test_integer_labels_supported(self):
        """HMM 原生整数标签（0-3）同样可用。"""
        allowed = {(0, 1), (1, 2), (2, 3)}
        rep = compute_path_coverage([0, 1, 2, 3, 3, 2], allowed)
        # 转移: 0→1,1→2,2→3 覆盖; 3→2 未覆盖 → 3/4
        self.assertAlmostEqual(rep.coverage, 0.75)
        self.assertFalse(rep.passed)

    def test_top_uncovered_sorted_by_count(self):
        seq = ["r3", "r10", "r3", "r10", "r3", "r11", "r1", "r10"]
        rep = compute_path_coverage(seq, SPEC_PATHS, top_n=5)
        counts = [u.count for u in rep.top_uncovered]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertEqual(rep.top_uncovered[0].count, 2)  # r3→r10 ×2

    def test_short_sequence_raises(self):
        with self.assertRaises(A3CoverageError):
            compute_path_coverage(["r1"], SPEC_PATHS)

    def test_empty_allowed_raises(self):
        with self.assertRaises(A3CoverageError):
            compute_path_coverage(["r1", "r2"], set())

    def test_bad_threshold_raises(self):
        with self.assertRaises(A3CoverageError):
            compute_path_coverage(["r1", "r2"], SPEC_PATHS, coverage_threshold=1.5)


if __name__ == "__main__":
    unittest.main()
