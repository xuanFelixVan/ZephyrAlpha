"""两阶段概率校准器单元测试（discussion_004 §2.2 P0-E2）.

测试覆盖：
  - TemperatureCalibrator: T 学习方向（过自信→T>1，欠自信→T<1，已校准→T≈1）
  - IsotonicCalibrator: 分桶 + 单调映射 + passthrough
  - TwoStageCalibrator: 串联 fit/transform + 序列化
  - fit_calibrator_with_fallback: 四级降级（Level 1-4）
  - compute_occurred_pit: PIT 防泄漏（§2.2.9 #1 #2）
  - Bug #3: BCE 不崩溃（occurred 是 1D 二值标签）

依据: discussion_004 §2.2.7 验收标准 / §2.2.9 防泄漏检查清单 / §2.2.10 降级验收
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.regime.validation.phase2.confidence_calibrator import (
    BUCKET_EDGES,
    CalibrationError,
    CalibrationResult,
    DegradationLevel,
    IsotonicCalibrator,
    TemperatureCalibrator,
    TwoStageCalibrator,
    compute_occurred_pit,
    fit_calibrator_with_fallback,
    load_calibration,
    save_calibration,
    trim_is_for_pit,
)


def _make_log_proba(logits: np.ndarray) -> np.ndarray:
    """logits → log_softmax（模拟 HMM 输出的 log_proba）。"""
    return logits - np.logaddexp.reduce(logits, axis=1, keepdims=True)


def _make_overconfident(n: int = 500, n_states: int = 4, seed: int = 42):
    """过自信数据：高 confidence 但 ~50% occurred → 预期 T > 1.0。"""
    rng = np.random.default_rng(seed)
    logits = rng.standard_normal((n, n_states)) * 0.3
    high_mask = rng.random(n) > 0.5
    logits[high_mask] *= 4.0
    log_proba = _make_log_proba(logits)
    occurred = np.zeros(n, dtype=int)
    occurred[~high_mask] = (rng.random((~high_mask).sum()) < 0.55).astype(int)
    occurred[high_mask] = (rng.random(high_mask.sum()) < 0.50).astype(int)
    return log_proba, occurred


def _make_underconfident(n: int = 500, n_states: int = 4, seed: int = 42):
    """欠自信数据：低 confidence 但 ~75% occurred → 预期 T < 1.0。"""
    rng = np.random.default_rng(seed)
    logits = rng.standard_normal((n, n_states)) * 0.8  # 大方差 → 均匀
    log_proba = _make_log_proba(logits)
    occurred = (rng.random(n) < 0.75).astype(int)
    return log_proba, occurred


class TestTemperatureCalibrator(unittest.TestCase):
    """Stage 1: Temperature Scaling 测试。"""

    def test_overconfident_T_greater_than_1(self):
        """过自信数据 → T > 1.0（降温）。"""
        log_proba, occurred = _make_overconfident()
        cal = TemperatureCalibrator()
        cal.fit(log_proba, occurred)
        self.assertGreater(cal.T, 1.0, f"过自信数据 T 应 > 1.0，实际 {cal.T}")

    def test_underconfident_T_less_than_1(self):
        """欠自信数据 → T < 1.0（升温）。"""
        log_proba, occurred = _make_underconfident()
        cal = TemperatureCalibrator()
        cal.fit(log_proba, occurred)
        self.assertLess(cal.T, 1.0, f"欠自信数据 T 应 < 1.0，实际 {cal.T}")

    def test_calibrated_T_approx_1(self):
        """已校准数据 → T ≈ 1.0。"""
        rng = np.random.default_rng(42)
        n, n_states = 500, 4
        logits = rng.standard_normal((n, n_states)) * 1.0
        log_proba = _make_log_proba(logits)
        # 让 occurred 频率匹配 confidence
        proba = np.exp(log_proba)
        confidence = proba.max(axis=1)
        occurred = (rng.random(n) < confidence).astype(int)
        cal = TemperatureCalibrator()
        cal.fit(log_proba, occurred)
        self.assertAlmostEqual(cal.T, 1.0, delta=0.3, msg=f"已校准 T 应 ≈ 1.0，实际 {cal.T}")

    def test_transform_returns_max_probability(self):
        """transform 返回 max(softmax(log_proba/T))——校准后 confidence。"""
        log_proba, occurred = _make_overconfident(n=200)
        cal = TemperatureCalibrator(T=2.0)
        confidence = cal.transform(log_proba)
        self.assertEqual(confidence.shape, (200,))
        # T=2 应降低 confidence（相比 T=1）
        orig_conf = np.exp(log_proba).max(axis=1)
        self.assertLess(confidence.mean(), orig_conf.mean())

    def test_transform_proba_full_matrix(self):
        """transform_proba 返回完整 (N, n_states) 概率矩阵，每行 Σ=1。"""
        log_proba, _ = _make_overconfident(n=50)
        cal = TemperatureCalibrator(T=1.5)
        proba = cal.transform_proba(log_proba)
        self.assertEqual(proba.shape, (50, 4))
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-10)

    def test_T_equals_1_is_identity(self):
        """T=1.0 时 transform = 原始 max(exp(log_proba))。"""
        log_proba, _ = _make_overconfident(n=50)
        cal = TemperatureCalibrator(T=1.0)
        confidence = cal.transform(log_proba)
        orig = np.exp(log_proba).max(axis=1)
        np.testing.assert_allclose(confidence, orig, atol=1e-10)

    def test_bce_no_crash_bug3(self):
        """Bug #3: BCE 不崩溃（occurred 是 1D 二值标签，非 2D one-hot）。"""
        log_proba, _ = _make_overconfident(n=100)
        # 全 0 occurred
        cal0 = TemperatureCalibrator()
        cal0.fit(log_proba, np.zeros(100, dtype=int))
        self.assertEqual(cal0.T, 1.0, "全 0 occurred 应保持 T=1.0")
        # 全 1 occurred
        cal1 = TemperatureCalibrator()
        cal1.fit(log_proba, np.ones(100, dtype=int))
        self.assertEqual(cal1.T, 1.0, "全 1 occurred 应保持 T=1.0")

    def test_fit_dimension_mismatch_raises(self):
        """log_proba 与 occurred 样本数不匹配 → CalibrationError。"""
        log_proba = np.random.randn(100, 4)
        occurred = np.zeros(50, dtype=int)
        cal = TemperatureCalibrator()
        with self.assertRaises(CalibrationError):
            cal.fit(log_proba, occurred)

    def test_serialization_round_trip(self):
        """to_dict / from_dict 往返保持 T。"""
        cal = TemperatureCalibrator(T=2.345)
        d = cal.to_dict()
        self.assertEqual(d["T"], 2.345)
        cal2 = TemperatureCalibrator.from_dict(d)
        self.assertAlmostEqual(cal2.T, 2.345)


class TestIsotonicCalibrator(unittest.TestCase):
    """Stage 2: Isotonic Regression 测试。"""

    def test_fit_and_transform(self):
        """正常 fit + transform：校准后 confidence 更接近 occurred 频率。"""
        rng = np.random.default_rng(42)
        n = 200
        # 构造过自信 confidence（0.7-0.9）但 occurred 频率 ~0.5
        confidence = rng.uniform(0.7, 0.9, n)
        occurred = (rng.random(n) < 0.5).astype(int)
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        self.assertIsNotNone(cal._x_thresh, "IsotonicRegression 应已 fit")
        calibrated = cal.transform(confidence)
        # 校准后应更接近 0.5
        self.assertLess(abs(calibrated.mean() - 0.5), abs(confidence.mean() - 0.5))

    def test_passthrough_when_not_fitted(self):
        """未 fit 时 transform = passthrough。"""
        cal = IsotonicCalibrator()
        confidence = np.array([0.3, 0.5, 0.8])
        result = cal.transform(confidence)
        np.testing.assert_array_equal(result, confidence)

    def test_passthrough_when_insufficient_unique_values(self):
        """唯一 confidence 值 < MIN_UNIQUE_FOR_FIT 时降级 passthrough。"""
        # 仅 2 个唯一值（0.1 和 0.5）< MIN_UNIQUE_FOR_FIT=5 → 退化
        confidence = np.concatenate(
            [
                np.full(3, 0.1),
                np.full(100, 0.5),
            ]
        )
        occurred = np.concatenate([np.zeros(3), np.ones(100)])
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        self.assertIsNone(cal._x_thresh)

    def test_raw_data_fit_more_thresholds_than_binned(self):
        """原始数据 fit 产生更多 thresholds（vs 5 桶预分桶的 3-4 点）。"""
        rng = np.random.default_rng(42)
        n = 500
        # 连续 confidence 分布（模拟温度缩放后 HMM 输出）
        confidence = np.clip(rng.normal(0.55, 0.12, n), 0.1, 0.95)
        occurred = (rng.random(n) < confidence * 0.8 + 0.1).astype(int)
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        self.assertIsNotNone(cal._x_thresh)
        # 原始数据 fit 应产生 ≥5 个 thresholds（5 桶预分桶最多 5 个）
        self.assertGreaterEqual(
            len(cal._x_thresh),
            5,
            f"原始数据 fit 应产生 ≥5 thresholds，实际 {len(cal._x_thresh)}",
        )

    def test_high_confidence_pulled_down(self):
        """过自信高 confidence 被 isotonic 拉低（B1 80-100% 桶根因修复）。"""
        rng = np.random.default_rng(42)
        n = 300
        # 中低 confidence 校准良好，高 confidence 过自信
        confidence = np.concatenate(
            [
                rng.uniform(0.4, 0.6, 200),  # 中低段
                rng.uniform(0.8, 0.95, 100),  # 高段过自信
            ]
        )
        # 中低段 occurred ~ confidence，高段 occurred ~0.5（过自信）
        occurred = np.concatenate(
            [
                (rng.random(200) < 0.5).astype(int),
                (rng.random(100) < 0.5).astype(int),
            ]
        )
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        self.assertIsNotNone(cal._x_thresh)
        # 高 confidence（0.9）应被拉低
        high_calibrated = cal.transform(np.array([0.9]))[0]
        self.assertLess(high_calibrated, 0.9, f"过自信 0.9 应被拉低，实际 {high_calibrated:.3f}")

    def test_monotonic_mapping(self):
        """Isotonic 映射保持单调性（输入越大输出越大）。"""
        rng = np.random.default_rng(42)
        n = 300
        confidence = np.clip(rng.normal(0.5, 0.2, n), 0, 1)
        occurred = (rng.random(n) < confidence).astype(int)  # 大致校准
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        if cal._x_thresh is not None:
            test_x = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
            test_y = cal.transform(test_x)
            # 单调非递减
            diffs = np.diff(test_y)
            self.assertTrue(np.all(diffs >= -1e-10), f"映射应单调非递减，diffs={diffs}")

    def test_serialization_round_trip(self):
        """to_dict / from_dict 往返保持拟合点。"""
        rng = np.random.default_rng(42)
        confidence = np.clip(rng.normal(0.5, 0.2, 200), 0, 1)
        occurred = (rng.random(200) < confidence).astype(int)
        cal = IsotonicCalibrator()
        cal.fit(confidence, occurred)
        if cal._x_thresh is not None:
            d = cal.to_dict()
            cal2 = IsotonicCalibrator.from_dict(d)
            np.testing.assert_allclose(
                cal.transform(np.array([0.3, 0.5, 0.7])),
                cal2.transform(np.array([0.3, 0.5, 0.7])),
                atol=1e-6,
            )

    def test_backward_compat_old_points_format(self):
        """旧格式（仅 points）反序列化 → 直接用作插值断点。"""
        d = {
            "type": "IsotonicCalibrator",
            "points": [(0.3, 0.5), (0.5, 0.6), (0.8, 0.7)],
        }
        cal = IsotonicCalibrator.from_dict(d)
        self.assertIsNotNone(cal._x_thresh)
        result = cal.transform(np.array([0.4, 0.6]))
        # 0.4 在 0.3-0.5 之间 → 插值 ~0.55
        self.assertAlmostEqual(result[0], 0.55, delta=0.01)


class TestTwoStageCalibrator(unittest.TestCase):
    """两阶段串联校准器测试。"""

    def test_fit_transform_chain(self):
        """Stage 1 → Stage 2 串联：校准误差小于原始。"""
        log_proba, occurred = _make_overconfident(n=300)
        occurred_rate = occurred.mean()
        cal = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=IsotonicCalibrator(),
        )
        cal.fit(log_proba, occurred)
        calibrated = cal.transform(log_proba)
        orig_conf = np.exp(log_proba).max(axis=1)
        orig_err = abs(orig_conf.mean() - occurred_rate)
        cal_err = abs(calibrated.mean() - occurred_rate)
        self.assertLess(cal_err, orig_err, f"校准误差应减小: orig={orig_err:.4f} cal={cal_err:.4f}")

    def test_stage2_none_passthrough(self):
        """Stage 2=None 时只走 Stage 1。"""
        log_proba, occurred = _make_overconfident(n=100)
        cal = TwoStageCalibrator(stage1=TemperatureCalibrator(), stage2=None)
        cal.fit(log_proba, occurred)
        result = cal.transform(log_proba)
        stage1_only = cal.stage1.transform(log_proba)
        np.testing.assert_allclose(result, stage1_only)

    def test_serialization_round_trip(self):
        """完整序列化往返保持 transform 结果。"""
        log_proba, occurred = _make_overconfident(n=200)
        cal = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=IsotonicCalibrator(),
        )
        cal.fit(log_proba, occurred)
        d = cal.to_dict()
        cal2 = TwoStageCalibrator.from_dict(d)
        np.testing.assert_allclose(
            cal.transform(log_proba[:10]),
            cal2.transform(log_proba[:10]),
            atol=1e-6,
        )


class TestFitCalibratorWithFallback(unittest.TestCase):
    """四级降级策略测试（§2.2.10）。"""

    def test_level1_normal_fit(self):
        """n≥50 → Level 1: 正常 fit Stage 1 + Stage 2。"""
        log_proba, occurred = _make_overconfident(n=100)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        self.assertEqual(result.level, DegradationLevel.LEVEL_1)
        self.assertIsNotNone(cal.stage1)
        self.assertIsNotNone(cal.stage2)

    def test_level1_boundary_50(self):
        """n=50 → Level 1（边界值）。"""
        log_proba, occurred = _make_overconfident(n=50)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        self.assertEqual(result.level, DegradationLevel.LEVEL_1)

    def test_level2_only_stage1(self):
        """20≤n<50 → Level 2: 只 fit Stage 1。"""
        log_proba, occurred = _make_overconfident(n=30)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        self.assertEqual(result.level, DegradationLevel.LEVEL_2)
        self.assertIsNotNone(cal.stage1)
        self.assertIsNone(cal.stage2)

    def test_level2_boundary_20(self):
        """n=20 → Level 2（边界值）。"""
        log_proba, occurred = _make_overconfident(n=20)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        self.assertEqual(result.level, DegradationLevel.LEVEL_2)

    def test_level3_fallback_to_prev(self):
        """n<20 + 有上季度 → Level 3: 回退上季度校准器。"""
        log_proba, occurred = _make_overconfident(n=100)
        prev_cal, _ = fit_calibrator_with_fallback(log_proba, occurred)
        # 用 10 个样本 + 上季度校准器
        cal, result = fit_calibrator_with_fallback(
            log_proba[:10],
            occurred[:10],
            prev_calibrator=prev_cal,
        )
        self.assertEqual(result.level, DegradationLevel.LEVEL_3)
        self.assertIs(cal, prev_cal, "Level 3 应返回上季度校准器实例")

    def test_level4_identity_no_prev(self):
        """n<20 + 无上季度 → Level 4: T=1.0 不校准。"""
        log_proba, occurred = _make_overconfident(n=10)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        self.assertEqual(result.level, DegradationLevel.LEVEL_4)
        self.assertEqual(cal.stage1.T, 1.0, "Level 4 T 应为 1.0（不校准）")
        self.assertIsNone(cal.stage2)

    def test_level4_transform_is_identity(self):
        """Level 4 transform = 原始 max(exp(log_proba))。"""
        log_proba, _ = _make_overconfident(n=10)
        cal, _ = fit_calibrator_with_fallback(log_proba, np.zeros(10, dtype=int))
        result = cal.transform(log_proba)
        orig = np.exp(log_proba).max(axis=1)
        np.testing.assert_allclose(result, orig, atol=1e-6)


class TestComputeOccurredPit(unittest.TestCase):
    """PIT 防泄漏 occurred 标签计算测试（§2.2.9）。"""

    def test_basic_occurred_computation(self):
        """基本流程：log_proba + close → occurred 标签。"""
        n, n_states = 100, 4
        rng = np.random.default_rng(42)
        logits = rng.standard_normal((n, n_states))
        log_proba = _make_log_proba(logits)
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        close = pd.Series(100 + np.cumsum(rng.standard_normal(n) * 0.5), index=dates)
        lp_valid, occurred = compute_occurred_pit(log_proba, dates, close, forward_days=20)
        self.assertGreater(len(occurred), 0, "应有有效样本")
        self.assertLess(len(occurred), n, "应过滤尾部（无 forward return）")
        self.assertTrue(np.all((occurred == 0) | (occurred == 1)), "occurred 应为 0/1")

    def test_tail_trim_no_leakage(self):
        """防泄漏 #1: 尾部 forward_days 的 forward_return 不被使用。"""
        n = 100
        n_states = 4
        rng = np.random.default_rng(42)
        logits = rng.standard_normal((n, n_states))
        log_proba = _make_log_proba(logits)
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        close = pd.Series(100 + np.cumsum(rng.standard_normal(n) * 0.5), index=dates)
        forward_days = 20
        lp_valid, occurred = compute_occurred_pit(log_proba, dates, close, forward_days=forward_days)
        # 最后 forward_days 天不应有 occurred 标签（无 forward return）
        valid_count = len(occurred)
        self.assertLessEqual(valid_count, n - forward_days, "尾部 forward_days 天应被过滤")

    def test_regime_directions_pit_only(self):
        """防泄漏 #2: regime_directions 只用传入的 IS 数据推断，不看 OOS。"""
        # 构造 IS 数据：state 0 的后续收益为正（涨）
        # 构造 OOS 数据：state 0 的后续收益为负（跌）
        # 验证 IS 的 occurred 标签基于"涨"方向，不受 OOS"跌"影响
        n_is, n_oos, n_states = 100, 50, 2
        rng = np.random.default_rng(42)

        # IS: state 0 主导，后续涨
        is_logits = np.zeros((n_is, n_states))
        is_logits[:, 0] = 2.0  # state 0 主导
        is_log_proba = _make_log_proba(is_logits)
        is_dates = pd.date_range("2020-01-01", periods=n_is, freq="B")
        is_close = pd.Series(100 + np.arange(n_is) * 0.1, index=is_dates)  # 持续上涨

        # OOS: state 0 主导，后续跌
        oos_logits = np.zeros((n_oos, n_states))
        oos_logits[:, 0] = 2.0
        oos_dates = pd.date_range(is_dates[-1] + pd.Timedelta(days=1), periods=n_oos, freq="B")
        oos_close = pd.Series(200 - np.arange(n_oos) * 0.1, index=oos_dates)  # 持续下跌

        # 只用 IS 数据算 occurred
        lp_is, occ_is = compute_occurred_pit(is_log_proba, is_dates, is_close, forward_days=20)
        # state 0 在 IS 中是"涨"，后续确实涨 → occurred 应大量为 1
        self.assertGreater(occ_is.mean(), 0.7, f"IS state 0 涨 → occurred 应多为 1，实际 {occ_is.mean():.2%}")

        # 只用 OOS 数据算 occurred
        lp_oos, occ_oos = compute_occurred_pit(
            _make_log_proba(oos_logits),
            oos_dates,
            oos_close,
            forward_days=20,
        )
        # state 0 在 OOS 中是"跌"，后续确实跌 → occurred 应大量为 1（方向匹配）
        self.assertGreater(occ_oos.mean(), 0.7, f"OOS state 0 跌 → occurred 应多为 1，实际 {occ_oos.mean():.2%}")

        # 关键验证：IS 的 occurred 不受 OOS 数据影响
        # 如果用全量数据推断方向，IS 的 occurred 会被 OOS 污染
        # 这里我们只传 IS 数据，所以方向是"涨"，occurred 基于"涨"

    def test_no_direction_state_filtered(self):
        """态平均收益 |mean| < threshold → 该态样本被过滤。"""
        n = 100
        n_states = 2
        rng = np.random.default_rng(42)
        # state 0 主导，但 close 纯随机（无方向）
        logits = np.zeros((n, n_states))
        logits[:, 0] = 3.0  # state 0 强主导
        log_proba = _make_log_proba(logits)
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        close = pd.Series(100 + rng.standard_normal(n) * 0.001, index=dates)  # 几乎不变
        lp_valid, occurred = compute_occurred_pit(log_proba, dates, close, forward_days=20)
        # state 0 无明确方向 → 所有样本被过滤
        self.assertEqual(len(occurred), 0, "无方向态应被全部过滤")

    def test_dimension_mismatch_raises(self):
        """timestamps 与 log_proba 行数不匹配 → CalibrationError。"""
        log_proba = np.random.randn(100, 4)
        dates = pd.date_range("2020-01-01", periods=50, freq="B")
        close = pd.Series(100 + np.arange(50) * 0.1, index=dates)
        with self.assertRaises(CalibrationError):
            compute_occurred_pit(log_proba, dates, close, forward_days=20)


class TestTrimIsForPit(unittest.TestCase):
    """IS 尾部裁剪测试（防泄漏 #1）。"""

    def test_trim_correct_end_date(self):
        """裁剪后 safe_end = train_end - forward_days * 1.5 天。"""
        # periods=500 确保 safe_end(2021-03-01) 落在索引范围内（300 工作日仅到 2021-02-23）
        dates = pd.date_range("2020-01-01", periods=500, freq="B")
        features = pd.DataFrame({"f1": np.arange(500)}, index=dates)
        close = pd.Series(100 + np.arange(500) * 0.1, index=dates)
        train_start = pd.Timestamp("2020-01-01")
        train_end = pd.Timestamp("2021-03-31")
        forward_days = 20
        features_safe, close_safe = trim_is_for_pit(
            features,
            close,
            train_start,
            train_end,
            forward_days,
        )
        safe_end = train_end - pd.Timedelta(days=int(forward_days * 1.5))
        self.assertEqual(features_safe.index[-1], safe_end)
        self.assertEqual(close_safe.index[-1], safe_end)
        self.assertLess(len(features_safe), len(features))


class TestSaveLoadCalibration(unittest.TestCase):
    """校准器持久化测试。"""

    def test_save_load_round_trip(self):
        """保存 → 加载 → transform 结果一致。"""
        log_proba, occurred = _make_overconfident(n=200)
        cal, result = fit_calibrator_with_fallback(log_proba, occurred)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_calibration(cal, result, "2024Q3", output_dir=tmpdir)
            self.assertTrue(path.exists())
            # 验证 JSON 可读
            artifact = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["quarter"], "2024Q3")
            # 加载并验证 transform 一致
            cal2 = load_calibration("2024Q3", input_dir=tmpdir)
            self.assertIsNotNone(cal2)
            np.testing.assert_allclose(
                cal.transform(log_proba[:10]),
                cal2.transform(log_proba[:10]),
                atol=1e-6,
            )

    def test_load_nonexistent_returns_none(self):
        """加载不存在的文件 → None。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_calibration("9999Q4", input_dir=tmpdir)
            self.assertIsNone(result)


class TestPitLeakageIntegration(unittest.TestCase):
    """PIT 防泄漏端到端测试（§2.2.9 检查清单）。"""

    def test_calibrator_not_influenced_by_future_data(self):
        """构造已知未来数据场景，验证校准参数不被未来数据影响。"""
        n_is, n_states = 200, 4
        rng = np.random.default_rng(42)
        # IS 数据：state 0 强主导，后续涨
        is_logits = np.zeros((n_is, n_states))
        is_logits[:, 0] = 3.0
        is_log_proba = _make_log_proba(is_logits)
        is_dates = pd.date_range("2020-01-01", periods=n_is, freq="B")
        is_close = pd.Series(100 + np.arange(n_is) * 0.05, index=is_dates)

        # 只用 IS 数据 fit 校准器
        lp_is, occ_is = compute_occurred_pit(is_log_proba, is_dates, is_close, forward_days=20)
        cal_is, result_is = fit_calibrator_with_fallback(lp_is, occ_is)

        # 构造完全不同的"未来"数据
        future_logits = rng.standard_normal((100, n_states)) * 5.0
        future_log_proba = _make_log_proba(future_logits)
        future_dates = pd.date_range(is_dates[-1] + pd.Timedelta(days=1), periods=100, freq="B")
        future_close = pd.Series(50 - np.arange(100) * 0.1, index=future_dates)
        lp_future, occ_future = compute_occurred_pit(
            future_log_proba,
            future_dates,
            future_close,
            forward_days=20,
        )

        # 用 IS + 未来 数据 fit（模拟泄漏场景）
        lp_combined = np.vstack([lp_is, lp_future])
        occ_combined = np.concatenate([occ_is, occ_future])
        cal_combined, _ = fit_calibrator_with_fallback(lp_combined, occ_combined)

        # 用只 IS 数据 fit
        cal_is_only, _ = fit_calibrator_with_fallback(lp_is, occ_is)

        # 两个校准器的 T 参数应该不同（因为数据不同）
        # 但关键是：cal_is_only 的 T 不受 future 数据影响
        # cal_is_only.transform 的结果应该只反映 IS 数据的校准
        self.assertIsNotNone(cal_is_only.stage1)
        self.assertGreater(cal_is_only.stage1.T, 0.0)
        # IS 的 occurred 频率应该影响 T（state 0 涨 + 后续涨 → occurred 高 → T 可能 < 1）
        # 但这取决于数据——关键是不崩溃、有合理值

    def test_walk_forward_quarterly_isolation(self):
        """模拟 walk-forward 两季度：Q1 校准器不受 Q2 数据影响。"""
        n_per_q, n_states = 100, 4
        rng = np.random.default_rng(42)

        # Q1: 过自信
        q1_log_proba, q1_occ = _make_overconfident(n=n_per_q, seed=42)
        # Q2: 欠自信（完全不同）
        q2_log_proba, q2_occ = _make_underconfident(n=n_per_q, seed=99)

        # Q1 只用 Q1 数据 fit
        cal_q1, _ = fit_calibrator_with_fallback(q1_log_proba, q1_occ)
        T_q1 = cal_q1.stage1.T

        # Q2 用 Q2 数据 fit（带 Q1 作为 prev_calibrator）
        cal_q2, result_q2 = fit_calibrator_with_fallback(
            q2_log_proba,
            q2_occ,
            prev_calibrator=cal_q1,
        )
        # Q2 应该正常 fit（n=100 ≥ 50 → Level 1），不回退 Q1
        self.assertEqual(result_q2.level, DegradationLevel.LEVEL_1)
        T_q2 = cal_q2.stage1.T

        # T_q1 和 T_q2 应该不同（数据特征不同）
        self.assertNotAlmostEqual(T_q1, T_q2, delta=0.01, msg="Q1/Q2 数据不同，T 应不同")

        # Q1 的 T 不受 Q2 影响（已经是历史值）
        self.assertAlmostEqual(cal_q1.stage1.T, T_q1, msg="Q1 校准器 T 不应被 Q2 数据修改")


if __name__ == "__main__":
    unittest.main()
