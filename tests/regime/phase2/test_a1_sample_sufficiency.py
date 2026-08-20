# -*- coding: utf-8 -*-
"""A1 样本充足性验证器单元测试（12_regime_phase2_validation §2.1）."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import numpy as np

from zephyr.regime.validation.phase2.a1_sample_sufficiency import (
    A1Overall,
    A1SampleSufficiency,
    A1StateVerdict,
    A1ValidationError,
)


def _make_detector_mock(state_seq: np.ndarray, n_states: int = 4, score: float = -100.0):
    """构造 mock detector，_hmm_model.predict 返回指定序列.

    state_seq 长度必须 == 特征矩阵行数 T（predict(X) 返回 (T,) 标签）。
    """
    detector = MagicMock()
    detector._hmm_model = MagicMock()
    seq = np.asarray(state_seq)
    detector._hmm_model.predict.return_value = seq
    detector._hmm_model.score.return_value = score
    return detector


def _make_X(n_rows: int, seed: int = 0) -> np.ndarray:
    """生成 (n_rows, 6) 随机特征矩阵（无 NaN，mock 不关心值）。"""
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, size=(n_rows, 6))


class TestA1SampleSufficiency(unittest.TestCase):
    """A1 验证器核心逻辑测试。"""

    def test_all_sufficient_pass(self):
        """4 态各 ≥100 天 → PASS。"""
        # 4 态 × 150 天 = 600 样本，每态均衡
        seq = np.repeat(np.arange(4), 150)
        np.random.default_rng(0).shuffle(seq)
        detector = _make_detector_mock(seq)
        X = _make_X(len(seq))
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        self.assertEqual(report.overall, A1Overall.PASS)
        self.assertEqual(report.total_samples, 600)
        self.assertFalse(report.degraded)
        self.assertEqual(len(report.state_stats), 4)
        for s in report.state_stats:
            self.assertEqual(s.verdict, A1StateVerdict.SUFFICIENT)
            self.assertEqual(s.action, "独立建模")

    def test_one_insufficient_fail(self):
        """存在 <50 天态 → FAIL。"""
        seq = np.concatenate(
            [
                np.repeat(0, 200),
                np.repeat(1, 200),
                np.repeat(2, 200),
                np.repeat(3, 30),  # 不足
            ]
        )
        detector = _make_detector_mock(seq)
        X = _make_X(len(seq))
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        self.assertEqual(report.overall, A1Overall.FAIL)
        insuff = report.insufficient_states
        self.assertEqual(insuff, ["r4"])
        self.assertEqual(report.min_state_count, 30)

    def test_moderate_only_review(self):
        """存在 50-100 天态但无 <50 → REVIEW。"""
        seq = np.concatenate(
            [
                np.repeat(0, 200),
                np.repeat(1, 200),
                np.repeat(2, 200),
                np.repeat(3, 70),  # 中等
            ]
        )
        detector = _make_detector_mock(seq)
        X = _make_X(len(seq))
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        self.assertEqual(report.overall, A1Overall.REVIEW)
        moderate = [s.state for s in report.state_stats if s.verdict is A1StateVerdict.MODERATE]
        self.assertEqual(moderate, ["r4"])

    def test_nan_rows_dropped(self):
        """含 NaN 的行被 dropna 清除。"""
        X = np.array(
            [
                [np.nan, 1, 2, 3, 4, 5],  # warmup NaN 行，应丢
                [1, 2, 3, 4, 5, 6],
                [np.nan, np.nan, 1, 2, 3, 4],  # 应丢
                [2, 3, 4, 5, 6, 7],
            ]
        )
        seq = np.array([0, 1])  # 2 行解码
        detector = _make_detector_mock(seq)
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        # 2 样本 → 所有态 <50 → FAIL（但报告应正常生成，不抛异常）
        self.assertEqual(report.total_samples, 2)
        self.assertEqual(report.overall, A1Overall.FAIL)

    def test_inf_clamped(self):
        """Inf 值被钳为 0，不抛异常。"""
        X = np.full((200, 6), 1.0)
        X[5, 0] = np.inf
        X[10, 2] = -np.inf
        seq = np.repeat(np.arange(4), 23)[:200]  # 4 态分布
        detector = _make_detector_mock(seq)
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        self.assertFalse(report.degraded)

    def test_insufficient_samples_raises(self):
        """样本 <100 抛 A1ValidationError。"""
        X = np.random.default_rng(0).normal(size=(50, 6))
        a1 = A1SampleSufficiency()
        with self.assertRaises(A1ValidationError):
            a1.validate(X, standardize=False)

    def test_all_nan_raises(self):
        """全 NaN 矩阵抛 A1ValidationError。"""
        X = np.full((200, 6), np.nan)
        a1 = A1SampleSufficiency()
        with self.assertRaises(A1ValidationError):
            a1.validate(X, standardize=False)

    def test_wrong_dims_raises(self):
        """3D 矩阵抛 A1ValidationError。"""
        X = np.zeros((10, 6, 2))
        a1 = A1SampleSufficiency()
        with self.assertRaises(A1ValidationError):
            a1.validate(X, standardize=False)

    def test_to_dict_serializable(self):
        """to_dict 可序列化。"""
        seq = np.repeat(np.arange(4), 100)
        detector = _make_detector_mock(seq)
        X = _make_X(len(seq))
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        d = report.to_dict()
        self.assertIn("state_stats", d)
        self.assertIn("overall", d)
        self.assertEqual(d["overall"], "PASS")
        # JSON 可序列化
        import json

        json.dumps(d)

    def test_min_state_count_property(self):
        """min_state_count 属性。"""
        seq = np.concatenate([np.repeat(i, 100) for i in range(3)] + [np.repeat(3, 55)])
        detector = _make_detector_mock(seq)
        X = _make_X(len(seq))
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X, standardize=False)
        self.assertEqual(report.min_state_count, 55)


if __name__ == "__main__":
    unittest.main()
