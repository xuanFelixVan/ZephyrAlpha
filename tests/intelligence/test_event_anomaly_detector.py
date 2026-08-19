# [MODULE] tests.intelligence.test_event_anomaly_detector
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_anomaly_detector.py -q
"""test_event_anomaly_detector.py — detect_anomaly 单元测试（26 号 §2.5 国盛异动雷达）。

覆盖：
  1. 双条件判定 —— corr<0 且 |excess|>3% 才异动；单条件不满足不异动
  2. 方向分类 —— positive/negative
  3. 退化路径 —— 序列过短/末窗口零方差/NaN 输入 → degraded 不抛
  4. 契约违反 —— 长度不一致/window<2/非数值 → EventAnomalyError
  5. 阈值参数化 —— corr/excess 阈值可调（G23 校准入口）
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from zephyr.intelligence.event_anomaly_detector import (
    ANOMALY_TYPE_NEGATIVE,
    ANOMALY_TYPE_NONE,
    ANOMALY_TYPE_POSITIVE,
    EventAnomalyError,
    detect_anomaly,
)


def _neg_corr_series(n: int = 40, excess: float = 0.002) -> tuple[list[float], list[float]]:
    """构造负相关且个股超额显著的序列：个股每根 +excess，基准反向下行。"""
    stock = [excess] * n
    bench = [-excess * 0.5] * n
    # 叠加交替扰动使末窗口相关系数为负且非零方差
    for i in range(n):
        jitter = 0.001 * (1 if i % 2 == 0 else -1)
        stock[i] += jitter
        bench[i] -= jitter
    return stock, bench


# ============ 1. 双条件判定 ============


class TestDualCondition:
    def test_anomaly_when_neg_corr_and_excess(self):
        stock, bench = _neg_corr_series()
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.rolling_corr < 0
        assert out.excess_return > 0.03
        assert out.is_anomaly is True
        assert out.anomaly_type == ANOMALY_TYPE_POSITIVE
        assert out.degraded is False

    def test_no_anomaly_when_positively_correlated(self):
        # 同向联动（corr>0）即使涨幅大也不算异动——防大盘联动误判
        n = 40
        base = [0.001 * (1 if i % 2 == 0 else -1) + 0.002 for i in range(n)]
        stock = [r * 2.0 for r in base]  # 个股放大版，excess 大
        out = detect_anomaly("600000.SH", stock, base)
        assert out.rolling_corr > 0
        assert out.is_anomaly is False
        assert out.anomaly_type == ANOMALY_TYPE_NONE

    def test_no_anomaly_when_excess_below_threshold(self):
        # 负相关但超额不足 3%（0.0003/根 × 40 根 ≈ 1.8%）
        stock, bench = _neg_corr_series(excess=0.0003)
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.rolling_corr < 0
        assert abs(out.excess_return) < 0.03
        assert out.is_anomaly is False


# ============ 2. 方向分类 ============


class TestDirection:
    def test_negative_anomaly(self):
        # 个股持续下跌、基准反向上涨 → 负超额 + 负相关 → negative
        n = 40
        stock = [-0.002 + 0.001 * (1 if i % 2 == 0 else -1) for i in range(n)]
        bench = [0.001 - 0.001 * (1 if i % 2 == 0 else -1) for i in range(n)]
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.is_anomaly is True
        assert out.anomaly_type == ANOMALY_TYPE_NEGATIVE
        assert out.excess_return < -0.03


# ============ 3. 退化路径 ============


class TestDegraded:
    def test_short_series_degraded(self):
        out = detect_anomaly("600000.SH", [0.01] * 10, [0.01] * 10)
        assert out.is_anomaly is False
        assert out.degraded is True
        assert math.isnan(out.rolling_corr)

    def test_exactly_window_plus_one_ok(self):
        stock, bench = _neg_corr_series(n=21)
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.degraded is False

    def test_zero_variance_window_degraded(self):
        n = 40
        stock = [0.001] * n  # 常数序列 → 零方差
        bench = [0.001 * (1 if i % 2 == 0 else -1) for i in range(n)]
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.is_anomaly is False
        assert out.degraded is True

    def test_nan_input_degraded(self):
        stock, bench = _neg_corr_series()
        stock[5] = float("nan")
        out = detect_anomaly("600000.SH", stock, bench)
        assert out.is_anomaly is False
        assert out.degraded is True


# ============ 4. 契约违反 ============


class TestContract:
    def test_length_mismatch_raises(self):
        with pytest.raises(EventAnomalyError):
            detect_anomaly("600000.SH", [0.01] * 30, [0.01] * 20)

    def test_window_too_small_raises(self):
        with pytest.raises(EventAnomalyError):
            detect_anomaly("600000.SH", [0.01] * 30, [0.01] * 30, window=1)

    def test_non_numeric_raises(self):
        with pytest.raises(EventAnomalyError):
            detect_anomaly("600000.SH", ["a"] * 30, [0.01] * 30)


# ============ 5. 阈值参数化（G23 校准入口）============


class TestThresholds:
    def test_custom_excess_threshold(self):
        stock, bench = _neg_corr_series(excess=0.001)  # 累计超额 ~4% > 3%? 0.001*40≈4.1%
        out_default = detect_anomaly("600000.SH", stock, bench)
        out_strict = detect_anomaly("600000.SH", stock, bench, excess_threshold=0.10)
        assert out_default.is_anomaly is True
        assert out_strict.is_anomaly is False

    def test_custom_corr_threshold(self):
        # 弱正相关（corr∈(0,1)）在默认 0.0 阈值下不异动，放宽到 0.9 可异动
        n = 40
        rng = np.random.default_rng(42)
        common = rng.normal(0, 0.001, n)
        stock = common + rng.normal(0, 0.004, n) + 0.003
        bench = common + rng.normal(0, 0.004, n)
        out = detect_anomaly("600000.SH", stock.tolist(), bench.tolist(), corr_threshold=0.999)
        # corr<0.999 几乎必真；excess 由 +0.003 漂移推动
        assert out.rolling_corr < 0.999
        assert out.excess_return > 0.03
        assert out.is_anomaly is True
