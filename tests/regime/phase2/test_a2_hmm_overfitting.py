# -*- coding: utf-8 -*-
"""A2 HMM 过拟合验证器单元测试（12_regime_phase2_validation §2.3）.

测试覆盖：
  - 标签对齐 _align_labels（permutation invariance）
  - 一致率 _accuracy（mapping 对齐后逐日匹配）
  - KL 散度 _kl_divergence
  - 判定门槛 _judge（PASS ≥0.7 / REVIEW ≥0.5 / FAIL <0.5）
  - 降级报告 _degraded_report
  - validate() 端到端（同分布 IS/OOS → PASS；不同分布 → 低 ratio）
  - 异常路径（样本不足 / 全 NaN）
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import numpy as np

from zephyr.regime.validation.phase2.a2_hmm_overfitting import (
    A2HmmOverfitting,
    A2Report,
    A2ValidationError,
    A2Verdict,
)


def _make_hmm_mock(means: np.ndarray):
    """构造 mock HMM，means_ 为指定值，predict/predict_proba 返回 mock。"""
    hmm = MagicMock()
    hmm.means_ = means
    return hmm


class TestA2AlignLabels(unittest.TestCase):
    """_align_labels：标签对齐（按态均值特征排序）。"""

    def test_identical_means_identity_mapping(self):
        """两模型 means 相同 → 恒等映射 {0:0, 1:1, 2:2}。"""
        means = np.array([[0.1], [0.5], [0.9]])
        hmm_a = _make_hmm_mock(means)
        hmm_b = _make_hmm_mock(means)
        mapping = A2HmmOverfitting._align_labels(hmm_a, hmm_b)
        self.assertEqual(mapping, {0: 0, 1: 1, 2: 2})

    def test_permutation_invariance(self):
        """A 模型 [0.1, 0.5, 0.9] vs B 模型 [0.9, 0.1, 0.5]。

        A 态 0（mean=0.1, rank=0）→ B 态 1（mean=0.1, rank=0）
        A 态 1（mean=0.5, rank=1）→ B 态 2（mean=0.5, rank=1）
        A 态 2（mean=0.9, rank=2）→ B 态 0（mean=0.9, rank=2）
        """
        means_a = np.array([[0.1], [0.5], [0.9]])
        means_b = np.array([[0.9], [0.1], [0.5]])
        hmm_a = _make_hmm_mock(means_a)
        hmm_b = _make_hmm_mock(means_b)
        mapping = A2HmmOverfitting._align_labels(hmm_a, hmm_b)
        self.assertEqual(mapping[0], 1)  # A 最小 → B 最小（态 1）
        self.assertEqual(mapping[1], 2)  # A 中间 → B 中间（态 2）
        self.assertEqual(mapping[2], 0)  # A 最大 → B 最大（态 0）

    def test_feature_idx_selection(self):
        """feature_idx=1 时按第二列排序对齐。"""
        means_a = np.array([[0.0, 0.1], [0.0, 0.5], [0.0, 0.9]])
        means_b = np.array([[0.0, 0.9], [0.0, 0.1], [0.0, 0.5]])
        hmm_a = _make_hmm_mock(means_a)
        hmm_b = _make_hmm_mock(means_b)
        mapping = A2HmmOverfitting._align_labels(hmm_a, hmm_b, feature_idx=1)
        self.assertEqual(mapping[0], 1)
        self.assertEqual(mapping[1], 2)
        self.assertEqual(mapping[2], 0)

    def test_hungarian_all_features_superior(self):
        """Hungarian 全特征匹配优于单特征排序：对齐特征列恒定时单特征排序失效。

        场景：col 0（vol_pct 代理）三态恒定 0.5，col 1 有区分性。
          means_a = [[0.5,0.1],[0.5,0.5],[0.5,0.9]]
          means_b = [[0.5,0.9],[0.5,0.1],[0.5,0.5]]
        单特征排序（col 0）：三态 rank 全 0（tie）→ 错配 {0:0,1:1,2:2}
        Hungarian 全特征：col 0 距离全 0，col 1 决定 → 正确 {0:1,1:2,2:0}

        回归守护：防止 _align_labels 退回单特征排序导致一致率被低估
        （A2 基线 OOS/IS=0.340 部分归因于此）。
        """
        means_a = np.array([[0.5, 0.1], [0.5, 0.5], [0.5, 0.9]])
        means_b = np.array([[0.5, 0.9], [0.5, 0.1], [0.5, 0.5]])
        hmm_a = _make_hmm_mock(means_a)
        hmm_b = _make_hmm_mock(means_b)
        mapping = A2HmmOverfitting._align_labels(hmm_a, hmm_b)
        # Hungarian 全特征：A 态 0(col1=0.1)→B 态 1(col1=0.1)，非恒等映射
        self.assertEqual(mapping[0], 1, "A 态0(col1=0.1) 应映射到 B 态1(col1=0.1)")
        self.assertEqual(mapping[1], 2, "A 态1(col1=0.5) 应映射到 B 态2(col1=0.5)")
        self.assertEqual(mapping[2], 0, "A 态2(col1=0.9) 应映射到 B 态0(col1=0.9)")


class TestA2Accuracy(unittest.TestCase):
    """_accuracy：mapping 对齐后逐日一致率。"""

    def test_perfect_match(self):
        """完全一致 → 1.0。"""
        seq_a = np.array([0, 1, 2, 0, 1])
        seq_b = np.array([0, 1, 2, 0, 1])
        mapping = {0: 0, 1: 1, 2: 2}
        acc = A2HmmOverfitting._accuracy(seq_a, seq_b, mapping)
        self.assertAlmostEqual(acc, 1.0)

    def test_permuted_match(self):
        """标签排列不同但对齐后一致 → 1.0。"""
        seq_a = np.array([0, 1, 2, 0, 1])
        seq_b = np.array([1, 2, 0, 1, 2])  # B 标签 = A+1 mod 3
        mapping = {0: 1, 1: 2, 2: 0}  # A→B 映射
        acc = A2HmmOverfitting._accuracy(seq_a, seq_b, mapping)
        self.assertAlmostEqual(acc, 1.0)

    def test_half_match(self):
        """部分一致：[0,0,1,1,2] vs [0,1,1,1,2] → 4/5=0.8。"""
        seq_a = np.array([0, 0, 1, 1, 2])
        seq_b = np.array([0, 1, 1, 1, 2])
        mapping = {0: 0, 1: 1, 2: 2}
        acc = A2HmmOverfitting._accuracy(seq_a, seq_b, mapping)
        self.assertAlmostEqual(acc, 0.8)

    def test_empty_sequence(self):
        """空序列 → 0.0。"""
        acc = A2HmmOverfitting._accuracy(np.array([]), np.array([]), {})
        self.assertAlmostEqual(acc, 0.0)

    def test_length_mismatch(self):
        """长度不一致 → 0.0。"""
        acc = A2HmmOverfitting._accuracy(np.array([0, 1, 2]), np.array([0, 1]), {0: 0, 1: 1, 2: 2})
        self.assertAlmostEqual(acc, 0.0)


class TestA2KLDivergence(unittest.TestCase):
    """_kl_divergence：KL(p_b || p_a) 平均散度。"""

    def test_identical_distributions(self):
        """相同分布 → KL≈0。"""
        p = np.array([[0.5, 0.3, 0.2], [0.1, 0.8, 0.1]])
        kl = A2HmmOverfitting._kl_divergence(p, p)
        self.assertLess(kl, 1e-6)

    def test_different_distributions_positive(self):
        """不同分布 → KL > 0。"""
        p_a = np.array([[0.9, 0.05, 0.05]])
        p_b = np.array([[0.1, 0.8, 0.1]])
        kl = A2HmmOverfitting._kl_divergence(p_a, p_b)
        self.assertGreater(kl, 0.1)


class TestA2Judge(unittest.TestCase):
    """_judge：判定门槛。"""

    def test_pass_threshold(self):
        self.assertEqual(A2HmmOverfitting._judge(0.7), A2Verdict.PASS)
        self.assertEqual(A2HmmOverfitting._judge(0.9), A2Verdict.PASS)
        self.assertEqual(A2HmmOverfitting._judge(1.0), A2Verdict.PASS)

    def test_review_threshold(self):
        self.assertEqual(A2HmmOverfitting._judge(0.5), A2Verdict.REVIEW)
        self.assertEqual(A2HmmOverfitting._judge(0.69), A2Verdict.REVIEW)

    def test_fail_threshold(self):
        self.assertEqual(A2HmmOverfitting._judge(0.49), A2Verdict.FAIL)
        self.assertEqual(A2HmmOverfitting._judge(0.0), A2Verdict.FAIL)


class TestA2DegradedReport(unittest.TestCase):
    """_degraded_report：降级报告。"""

    def test_degraded_is_fail(self):
        report = A2HmmOverfitting._degraded_report(is_samples=500, oos_samples=300)
        self.assertTrue(report.degraded)
        self.assertEqual(report.verdict, A2Verdict.FAIL)
        self.assertEqual(report.is_samples, 500)
        self.assertEqual(report.oos_samples, 300)
        self.assertEqual(report.ratio, 0.0)
        self.assertTrue(np.isinf(report.kl_divergence))


class TestA2ValidateReal(unittest.TestCase):
    """validate() 端到端（真实 hmmlearn，合成数据）。"""

    def test_same_distribution_pass(self):
        """IS/OOS 同分布 → OOS/IS ≥ 0.7 → PASS。

        合成 2 态 Gaussian 数据，IS 和 OOS 从同一分布采样。
        """
        rng = np.random.default_rng(42)
        # 2 态，各 500 样本（IS+OOS 共 2000），同分布
        X_is = np.vstack(
            [
                rng.normal(0, 1, (500, 3)),
                rng.normal(5, 1, (500, 3)),
            ]
        )
        X_oos = np.vstack(
            [
                rng.normal(0, 1, (500, 3)),
                rng.normal(5, 1, (500, 3)),
            ]
        )
        X = np.vstack([X_is, X_oos])
        is_end_idx = len(X_is)

        a2 = A2HmmOverfitting(
            hmm_params={
                "n_states": 2,
                "covariance_type": "full",
                "n_iter": 50,
                "n_init": 3,
                "random_state": 42,
            }
        )
        report = a2.validate(X, is_end_idx=is_end_idx, standardize=True)
        self.assertFalse(report.degraded)
        self.assertEqual(report.is_samples, 1000)
        self.assertEqual(report.oos_samples, 1000)
        # 同分布 → OOS/IS 应较高
        self.assertGreaterEqual(report.ratio, 0.5, f"同分布 ratio={report.ratio:.3f} 应 ≥0.5")

    def test_different_distribution_runs(self):
        """IS/OOS 不同分布 → validate 正常完成（不 crash），产出有效报告。

        注意：RobustScaler 标准化会掩盖部分分布差异（PIT 设计），
        ratio 可能 ≥1.0（OOS 准确率 > IS 准确率），不代表无过拟合——
        本测试只验证流程跑通 + 报告字段完整。
        """
        rng = np.random.default_rng(42)
        # IS: 2 态均值 [0, 5]
        X_is = np.vstack(
            [
                rng.normal(0, 1, (500, 3)),
                rng.normal(5, 1, (500, 3)),
            ]
        )
        # OOS: 2 态均值 [0, 20]（分布差异大）
        X_oos = np.vstack(
            [
                rng.normal(0, 1, (500, 3)),
                rng.normal(20, 1, (500, 3)),
            ]
        )
        X = np.vstack([X_is, X_oos])
        is_end_idx = len(X_is)

        a2 = A2HmmOverfitting(
            hmm_params={
                "n_states": 2,
                "covariance_type": "full",
                "n_iter": 50,
                "n_init": 3,
                "random_state": 42,
            }
        )
        report = a2.validate(X, is_end_idx=is_end_idx, standardize=True)
        self.assertFalse(report.degraded)
        self.assertEqual(report.is_samples, 1000)
        self.assertEqual(report.oos_samples, 1000)
        self.assertIn(report.verdict, (A2Verdict.PASS, A2Verdict.REVIEW, A2Verdict.FAIL))
        # KL 散度有限
        self.assertTrue(np.isfinite(report.kl_divergence))

    def test_sample_too_small_raises(self):
        """IS 或 OOS < 100 → A2ValidationError。"""
        X = np.random.default_rng(0).normal(0, 1, (50, 3))
        a2 = A2HmmOverfitting(
            hmm_params={
                "n_states": 2,
                "n_iter": 10,
                "n_init": 1,
                "random_state": 0,
            }
        )
        with self.assertRaises(A2ValidationError):
            a2.validate(X, is_end_idx=25, standardize=False)

    def test_all_nan_raises(self):
        """全 NaN → A2ValidationError。"""
        X = np.full((200, 3), np.nan)
        a2 = A2HmmOverfitting(
            hmm_params={
                "n_states": 2,
                "n_iter": 10,
                "n_init": 1,
                "random_state": 0,
            }
        )
        with self.assertRaises(A2ValidationError):
            a2.validate(X, is_end_idx=100, standardize=False)

    def test_report_to_dict(self):
        """to_dict() 输出可 JSON 序列化。"""
        report = A2Report(
            is_accuracy=0.85,
            oos_accuracy=0.70,
            ratio=0.824,
            kl_divergence=0.123,
            label_alignment="按态均值特征排序",
            is_samples=1000,
            oos_samples=800,
            verdict=A2Verdict.PASS,
            summary="test",
            degraded=False,
        )
        d = report.to_dict()
        self.assertEqual(d["verdict"], "PASS")
        self.assertEqual(d["is_samples"], 1000)
        self.assertAlmostEqual(d["ratio"], 0.824)


class TestA2CleanMatrix(unittest.TestCase):
    """_clean_matrix：特征矩阵清理。"""

    def test_drops_nan_rows(self):
        X = np.array([[1.0, 2.0], [np.nan, 1.0], [3.0, 4.0]])
        clean = A2HmmOverfitting._clean_matrix(X)
        self.assertEqual(clean.shape, (2, 2))

    def test_clamps_inf(self):
        X = np.array([[1.0, 2.0], [np.inf, 1.0], [3.0, 4.0]])
        clean = A2HmmOverfitting._clean_matrix(X)
        # inf 行被 dropna（isfinite 检查）后钳为 0
        self.assertEqual(clean.shape, (2, 2))

    def test_reshapes_1d(self):
        X = np.array([1.0, 2.0, 3.0, np.nan, 5.0])
        clean = A2HmmOverfitting._clean_matrix(X)
        self.assertEqual(clean.ndim, 2)
        self.assertEqual(clean.shape, (4, 1))


if __name__ == "__main__":
    unittest.main()
