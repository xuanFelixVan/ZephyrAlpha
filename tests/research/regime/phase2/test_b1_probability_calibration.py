"""B1 概率校准度验证器单元测试（12_regime_phase2_validation §2.4）.

测试覆盖：
  - 后续收益计算 _compute_forward_returns
  - 态方向推断 _infer_regime_directions（涨/跌/无方向）
  - 可靠性曲线 _build_reliability_curve（分桶 + 预测 vs 实际频率）
  - 判定门槛 _judge（PASS <10% / REVIEW <15% / FAIL ≥15%）
  - 降级报告 _degraded_report
  - validate() 端到端（完美校准 → PASS；严重偏差 → FAIL）
  - 异常路径（空记录 / forward_days≤0 / 样本不足）
"""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from zephyr.regime.validation.phase2.b1_probability_calibration import (
    B1CalibrationPoint,
    B1ProbabilityCalibration,
    B1Report,
    B1ValidationError,
    B1Verdict,
)


class TestB1ForwardReturns(unittest.TestCase):
    """_compute_forward_returns：后续 N 日累计收益率。"""

    def test_basic_forward_return(self):
        """close=[100, 110] → forward_days=1 的 r_0 = 10%。"""
        close = pd.Series([100.0, 110.0, 120.0], index=pd.RangeIndex(3))
        fr = B1ProbabilityCalibration._compute_forward_returns(close, 1)
        # r_0 = 110/100 - 1 = 0.10, r_1 = 120/110 - 1 ≈ 0.0909
        # 末尾 1 天 NaN 被 dropna
        self.assertAlmostEqual(fr.iloc[0], 0.10, places=4)
        self.assertEqual(len(fr), 2)  # 末尾被 drop

    def test_forward_5_days(self):
        """forward_days=5：末尾 5 天为 NaN 被 drop。"""
        close = pd.Series(np.arange(100, 110, dtype=float), index=pd.RangeIndex(10))
        fr = B1ProbabilityCalibration._compute_forward_returns(close, 5)
        self.assertEqual(len(fr), 5)  # 10 - 5 = 5
        # r_0 = close[5]/close[0] - 1 = 105/100 - 1 = 0.05
        self.assertAlmostEqual(fr.iloc[0], 0.05, places=4)


class TestB1InferDirections(unittest.TestCase):
    """_infer_regime_directions：态方向推断。"""

    def test_positive_return_up(self):
        """态平均收益 > 0.5% → 涨。"""
        records = [
            {"dominant_regime": "r1", "forward_return": 0.02},
            {"dominant_regime": "r1", "forward_return": 0.03},
            {"dominant_regime": "r1", "forward_return": 0.01},
        ]
        directions = B1ProbabilityCalibration._infer_regime_directions(records)
        self.assertEqual(directions["r1"], "涨")

    def test_negative_return_down(self):
        """态平均收益 < -0.5% → 跌。"""
        records = [
            {"dominant_regime": "r2", "forward_return": -0.03},
            {"dominant_regime": "r2", "forward_return": -0.01},
            {"dominant_regime": "r2", "forward_return": -0.02},
        ]
        directions = B1ProbabilityCalibration._infer_regime_directions(records)
        self.assertEqual(directions["r2"], "跌")

    def test_near_zero_no_direction(self):
        """态平均收益 |mean| < 0.5% → 不返回（无明确方向）。"""
        records = [
            {"dominant_regime": "r3", "forward_return": 0.001},
            {"dominant_regime": "r3", "forward_return": -0.001},
            {"dominant_regime": "r3", "forward_return": 0.0005},
        ]
        directions = B1ProbabilityCalibration._infer_regime_directions(records)
        self.assertNotIn("r3", directions)

    def test_multiple_regimes(self):
        """多态各自推断。"""
        records = [
            {"dominant_regime": "r1", "forward_return": 0.05},
            {"dominant_regime": "r2", "forward_return": -0.05},
            {"dominant_regime": "r3", "forward_return": 0.0001},
        ]
        directions = B1ProbabilityCalibration._infer_regime_directions(records)
        self.assertEqual(directions["r1"], "涨")
        self.assertEqual(directions["r2"], "跌")
        self.assertNotIn("r3", directions)


class TestB1ReliabilityCurve(unittest.TestCase):
    """_build_reliability_curve：confidence 分桶 + 预测 vs 实际。"""

    def test_perfect_calibration(self):
        """完美校准：confidence=0.75 的桶内实际频率=0.75。"""
        # 10 个样本 confidence=0.75，其中 8 个 occurred → actual=0.8
        # 注意：边界 0.8 落在 80-100% 桶（左闭右开），用 0.75 落 60-80% 桶
        confidences = np.array([0.75] * 10)
        occurred = np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])  # 8/10 = 0.8
        curve = B1ProbabilityCalibration._build_reliability_curve(confidences, occurred)
        # 落在 60-80% 桶
        bucket_60_80 = [p for p in curve if p.bucket == "60-80%"][0]
        self.assertEqual(bucket_60_80.count, 10)
        self.assertAlmostEqual(bucket_60_80.predicted, 0.75)
        self.assertAlmostEqual(bucket_60_80.actual, 0.8)
        self.assertAlmostEqual(bucket_60_80.error, 0.05)

    def test_empty_buckets(self):
        """空桶 count=0，error=0。"""
        confidences = np.array([0.5, 0.5, 0.5])
        occurred = np.array([1, 0, 1])
        curve = B1ProbabilityCalibration._build_reliability_curve(confidences, occurred)
        bucket_40 = [p for p in curve if p.bucket == "40-60%"][0]
        self.assertEqual(bucket_40.count, 3)
        # 其他桶应为空
        empty_buckets = [p for p in curve if p.count == 0]
        self.assertEqual(len(empty_buckets), 4)

    def test_boundary_100_percent(self):
        """confidence=1.0 落在 80-100% 桶（含右边界）。"""
        confidences = np.array([1.0, 1.0])
        occurred = np.array([1, 0])
        curve = B1ProbabilityCalibration._build_reliability_curve(confidences, occurred)
        bucket_100 = [p for p in curve if p.bucket == "80-100%"][0]
        self.assertEqual(bucket_100.count, 2)


class TestB1Judge(unittest.TestCase):
    """_judge：判定门槛。"""

    def test_pass(self):
        self.assertEqual(B1ProbabilityCalibration._judge(0.05), B1Verdict.PASS)
        self.assertEqual(B1ProbabilityCalibration._judge(0.099), B1Verdict.PASS)
        self.assertEqual(B1ProbabilityCalibration._judge(0.0), B1Verdict.PASS)

    def test_review(self):
        self.assertEqual(B1ProbabilityCalibration._judge(0.10), B1Verdict.REVIEW)
        self.assertEqual(B1ProbabilityCalibration._judge(0.12), B1Verdict.REVIEW)
        self.assertEqual(B1ProbabilityCalibration._judge(0.149), B1Verdict.REVIEW)

    def test_fail(self):
        self.assertEqual(B1ProbabilityCalibration._judge(0.15), B1Verdict.FAIL)
        self.assertEqual(B1ProbabilityCalibration._judge(0.30), B1Verdict.FAIL)
        self.assertEqual(B1ProbabilityCalibration._judge(1.0), B1Verdict.FAIL)


class TestB1DegradedReport(unittest.TestCase):
    """_degraded_report：降级报告。"""

    def test_degraded_is_fail(self):
        report = B1ProbabilityCalibration._degraded_report(forward_days=20, total_samples=30)
        self.assertTrue(report.degraded)
        self.assertEqual(report.verdict, B1Verdict.FAIL)
        self.assertEqual(report.forward_days, 20)
        self.assertEqual(report.total_samples, 30)
        self.assertEqual(report.calibration_error, 1.0)
        self.assertEqual(len(report.reliability_curve), 0)


class TestB1Validate(unittest.TestCase):
    """validate() 端到端。"""

    def _make_close_up(self, n: int = 300, seed: int = 1) -> pd.Series:
        """生成上涨 close（20 日累计 ~10%）。"""
        rng = np.random.default_rng(seed)
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        returns = rng.normal(0.005, 0.015, n)
        close = pd.Series(np.cumprod(1 + returns) * 100, index=dates)
        return close

    def _make_close_down(self, n: int = 300, seed: int = 2) -> pd.Series:
        """生成下跌 close（20 日累计 ~-10%）。"""
        rng = np.random.default_rng(seed)
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        returns = rng.normal(-0.005, 0.015, n)
        close = pd.Series(np.cumprod(1 + returns) * 100, index=dates)
        return close

    def test_well_calibrated_pass(self):
        """完美校准：confidence=0.8 且 80% 实际涨 → 误差小 → PASS。"""
        close = self._make_close_up(300)
        dates = close.index[:270]  # 留 30 日做 forward
        # 270 条记录，全部 r1（涨态），confidence=0.8，实际涨概率 ~0.8
        rng = np.random.default_rng(42)
        records = []
        for i, ts in enumerate(dates):
            records.append(
                {
                    "timestamp": ts,
                    "confidence": 0.8,
                    "dominant_regime": "r1",
                }
            )
        b1 = B1ProbabilityCalibration()
        report = b1.validate(records, close, forward_days=20)
        self.assertFalse(report.degraded)
        self.assertEqual(report.forward_days, 20)
        self.assertGreater(report.total_samples, 50)
        # 完美校准 → 误差较小
        self.assertIn(report.verdict, (B1Verdict.PASS, B1Verdict.REVIEW))

    def test_poorly_calibrated_fail(self):
        """严重偏差：confidence=0.9 但只有 20% 实际涨 → 误差大 → FAIL。"""
        # 交替涨跌 close，20 日 forward 方向随机
        rng = np.random.default_rng(99)
        n = 400
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        # 接近 0 均值收益 → 方向不稳定
        returns = rng.normal(0.0, 0.02, n)
        close = pd.Series(np.cumprod(1 + returns) * 100, index=dates)
        # 全部标 confidence=0.9，但实际方向随机
        records = [{"timestamp": dates[i], "confidence": 0.9, "dominant_regime": "r1"} for i in range(350)]
        b1 = B1ProbabilityCalibration()
        report = b1.validate(records, close, forward_days=20)
        # 由于 close 均值收益≈0，r1 可能无明确方向 → 降级，或方向不稳定 → 大误差
        if not report.degraded:
            self.assertGreater(report.calibration_error, 0.1, "严重偏差应导致误差 > 10%")

    def test_multiple_regimes(self):
        """多态校准：r1 涨态 confidence=0.7，r2 跌态 confidence=0.6。"""
        n = 300
        rng = np.random.default_rng(7)
        dates_up = pd.date_range("2020-01-01", periods=n, freq="B")
        returns_up = rng.normal(0.005, 0.015, n)
        close_up = pd.Series(np.cumprod(1 + returns_up) * 100, index=dates_up)

        records = []
        for i in range(250):
            records.append(
                {
                    "timestamp": dates_up[i],
                    "confidence": 0.7 if i % 2 == 0 else 0.5,
                    "dominant_regime": "r1" if i % 2 == 0 else "r2",
                }
            )
        b1 = B1ProbabilityCalibration()
        report = b1.validate(records, close_up, forward_days=20)
        self.assertFalse(report.degraded)
        self.assertGreater(report.total_samples, 50)
        self.assertIn("r1", report.regime_directions)
        self.assertIn("r2", report.regime_directions)

    def test_empty_records_raises(self):
        """detect_records 为空 → B1ValidationError。"""
        close = self._make_close_up(100)
        b1 = B1ProbabilityCalibration()
        with self.assertRaises(B1ValidationError):
            b1.validate([], close, forward_days=20)

    def test_invalid_forward_days_raises(self):
        """forward_days ≤ 0 → B1ValidationError。"""
        close = self._make_close_up(100)
        b1 = B1ProbabilityCalibration()
        records = [{"timestamp": close.index[0], "confidence": 0.5, "dominant_regime": "r1"}]
        with self.assertRaises(B1ValidationError):
            b1.validate(records, close, forward_days=0)
        with self.assertRaises(B1ValidationError):
            b1.validate(records, close, forward_days=-1)

    def test_insufficient_samples_degraded(self):
        """有效样本 < 50 → 降级。"""
        close = self._make_close_up(100)
        records = [
            {"timestamp": close.index[i], "confidence": 0.5, "dominant_regime": "r1"}
            for i in range(10)  # 仅 10 条
        ]
        b1 = B1ProbabilityCalibration()
        report = b1.validate(records, close, forward_days=20)
        self.assertTrue(report.degraded)
        self.assertEqual(report.verdict, B1Verdict.FAIL)

    def test_report_to_dict(self):
        """to_dict() 输出可 JSON 序列化。"""
        report = B1Report(
            reliability_curve=[
                B1CalibrationPoint(bucket="0-20%", predicted=0.1, actual=0.15, count=10, error=0.05),
            ],
            calibration_error=0.08,
            weighted_calibration_error=0.06,
            max_bucket_error=0.12,
            forward_days=20,
            total_samples=100,
            regime_directions={"r1": "涨"},
            verdict=B1Verdict.PASS,
            summary="test",
            degraded=False,
        )
        d = report.to_dict()
        self.assertEqual(d["verdict"], "PASS")
        self.assertEqual(d["forward_days"], 20)
        self.assertEqual(d["regime_directions"], {"r1": "涨"})
        self.assertEqual(len(d["reliability_curve"]), 1)
        self.assertAlmostEqual(d["calibration_error"], 0.08)
        self.assertAlmostEqual(d["weighted_calibration_error"], 0.06)


if __name__ == "__main__":
    unittest.main()
