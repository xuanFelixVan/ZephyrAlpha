# [BLUEPRINT] MOD-REGIME-VAL | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""A4 特征重要性 Permutation 主轨单元测试（11_regime_backtest_validation_plan §4.1 A4）."""

from __future__ import annotations

import unittest

import numpy as np

from zephyr.regime.validation.a4_feature_importance import (
    A4ImportanceError,
    permutation_importance_windows,
)


def _corr_score(X: np.ndarray) -> float:
    """|corr(c0,c1)|：只对 c0/c1 的时序配对敏感（排列任一列即破坏）。"""
    if X.shape[0] < 3:
        return 0.0
    c = np.corrcoef(X[:, 0], X[:, 1])[0, 1]
    return float(abs(c))


def _make_pair(T: int, seed: int = 0) -> np.ndarray:
    """c0=c1 完全相关 + 时序结构（排列会破坏相关性）。"""
    rng = np.random.default_rng(seed)
    base = np.cumsum(rng.normal(0, 1, T))  # 随机游走，强时序结构
    noise = rng.normal(0, 1, T)
    return np.column_stack([base, base.copy(), noise])


class TestPermutationImportanceWindows(unittest.TestCase):
    def test_two_driver_features_pass(self):
        """F=3 但 score 只吃 c0/c1：两驱动特征 top-2 恒稳 + 占比达标 → 稳定通过需无可忽略特征。

        本用例 c2 为纯噪声（重要性≈0 → 可忽略）→ 验证可忽略特征检测判不通过。
        """
        X = _make_pair(300)
        rep = permutation_importance_windows(
            _corr_score,
            X,
            windows=[(0, 150), (150, 300)],
            n_repeats=4,
            seed=1,
            feature_names=["vol", "slope", "noise"],
        )
        self.assertEqual(rep.n_windows, 2)
        self.assertEqual(set(rep.top2_features), {"vol", "slope"})
        self.assertGreaterEqual(rep.top2_stability, 0.99)  # 两驱动各窗口均 top-2
        self.assertIn("noise", rep.negligible_features)
        self.assertFalse(rep.passed)  # 存在可忽略特征 → 降维候选警告

    def test_all_features_drive_score_pass(self):
        """F=2 双驱动：top-2=全部特征，稳定性=1.0，无可忽略 → 通过。"""
        X = _make_pair(240)[:, :2]
        rep = permutation_importance_windows(
            _corr_score,
            X,
            windows=[(0, 120), (120, 240)],
            n_repeats=4,
            seed=2,
            feature_names=["vol", "slope"],
        )
        self.assertTrue(rep.passed)
        self.assertEqual(rep.top2_stability, 1.0)
        self.assertEqual(rep.negligible_features, ())
        for share in rep.importance_share:
            self.assertGreater(share, 0.01)

    def test_rotating_driver_unstable(self):
        """驱动特征跨窗口轮换（W1:c0 / W2:c2 / W3:c3 分别与 c1 相关）→ top-2 稳定性 <70% → 不通过。"""
        rng = np.random.default_rng(5)
        W = 120
        blocks = []
        for w in range(3):
            base = np.cumsum(rng.normal(0, 1, W))
            cols = [rng.normal(0, 1, W) for _ in range(4)]
            cols[1] = base.copy()  # c1 有结构
            cols[[0, 2, 3][w]] = base.copy()  # 本窗口唯一驱动列
            blocks.append(np.column_stack(cols))
        X = np.vstack(blocks)

        def score(Xw: np.ndarray) -> float:
            best = 0.0
            for j in (0, 2, 3):
                c = abs(np.corrcoef(Xw[:, j], Xw[:, 1])[0, 1])
                best = max(best, c)
            return best

        rep = permutation_importance_windows(
            score,
            X,
            windows=[(0, W), (W, 2 * W), (2 * W, 3 * W)],
            n_repeats=4,
            seed=3,
            feature_names=["f0", "f1", "f2", "f3"],
        )
        self.assertIn("f1", rep.top2_features)
        self.assertLess(rep.top2_stability, 0.70)
        self.assertFalse(rep.passed)

    def test_reproducible_same_seed(self):
        X = _make_pair(120)
        r1 = permutation_importance_windows(_corr_score, X, n_repeats=3, seed=9)
        r2 = permutation_importance_windows(_corr_score, X, n_repeats=3, seed=9)
        self.assertEqual(r1.mean_importance, r2.mean_importance)

    def test_importance_direction(self):
        """驱动特征重要性为正且显著大于噪声特征。"""
        X = _make_pair(200)
        rep = permutation_importance_windows(_corr_score, X, n_repeats=4, seed=4)
        self.assertGreater(rep.mean_importance[0], 0.3)
        self.assertGreater(rep.mean_importance[1], 0.3)
        self.assertLess(rep.mean_importance[2], 0.1)

    def test_1d_matrix_raises(self):
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, np.zeros(10))

    def test_single_feature_raises(self):
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, np.zeros((10, 1)))

    def test_nan_raises(self):
        X = _make_pair(50)
        X[3, 0] = float("nan")
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, X)

    def test_bad_window_raises(self):
        X = _make_pair(50)
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, X, windows=[(40, 60)])

    def test_short_window_raises(self):
        X = _make_pair(50)
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, X, windows=[(0, 1)])

    def test_bad_repeats_raises(self):
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, _make_pair(20), n_repeats=0)

    def test_feature_names_mismatch_raises(self):
        with self.assertRaises(A4ImportanceError):
            permutation_importance_windows(_corr_score, _make_pair(20), feature_names=["a", "b"])


if __name__ == "__main__":
    unittest.main()
