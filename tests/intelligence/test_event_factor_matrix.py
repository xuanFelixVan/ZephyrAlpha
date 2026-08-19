# [MODULE] tests.intelligence.test_event_factor_matrix
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_factor_matrix.py -q
"""test_event_factor_matrix.py — 六因子矩阵数值项单元测试（26 号 §2.4）。

覆盖：
  1. compute_dreport —— 提前/延后/同日
  2. compute_jump_on_pead —— 跳跃提取/正负抵消/drift 分离/空输入/非法阈值
  3. compute_overnight_trend —— 滚动均值口径/首值 NaN/满窗要求/长度不一致/窗口非法
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from zephyr.intelligence.event_factor_matrix import (
    EventFactorError,
    compute_dreport,
    compute_jump_on_pead,
    compute_overnight_trend,
)

# ============ 1. compute_dreport ============


class TestDReport:
    def test_early_disclosure_positive(self):
        # 截止 04-30，实际 04-10 → 提前 20 天
        assert compute_dreport(date(2026, 4, 30), date(2026, 4, 10)) == 20

    def test_late_disclosure_negative(self):
        assert compute_dreport(date(2026, 4, 30), date(2026, 5, 5)) == -5

    def test_same_day_zero(self):
        assert compute_dreport(date(2026, 4, 30), date(2026, 4, 30)) == 0


# ============ 2. compute_jump_on_pead ============


class TestJumpOnPead:
    def test_jump_extraction(self):
        # |0.05|, |-0.04| ≥ 3% → jump；0.01, -0.02, 0.005 → drift
        out = compute_jump_on_pead([0.05, 0.01, -0.04, -0.02, 0.005])
        assert out.jump_component == pytest.approx(0.01)   # 0.05 - 0.04
        assert out.drift_component == pytest.approx(-0.005)  # 0.01 - 0.02 + 0.005
        assert out.car_total == pytest.approx(0.005)

    def test_all_mild_no_jump(self):
        out = compute_jump_on_pead([0.01, -0.01, 0.02])
        assert out.jump_component == 0.0
        assert out.drift_component == pytest.approx(0.02)

    def test_boundary_exactly_threshold_is_jump(self):
        out = compute_jump_on_pead([0.03, -0.03])
        assert out.jump_component == pytest.approx(0.0)
        assert out.drift_component == 0.0

    def test_empty_input_zeros(self):
        out = compute_jump_on_pead([])
        assert (out.jump_component, out.drift_component, out.car_total) == (0.0, 0.0, 0.0)

    def test_custom_threshold(self):
        out = compute_jump_on_pead([0.02, 0.01], jump_threshold=0.015)
        assert out.jump_component == pytest.approx(0.02)

    def test_invalid_threshold_raises(self):
        with pytest.raises(EventFactorError):
            compute_jump_on_pead([0.05], jump_threshold=0.0)
        with pytest.raises(EventFactorError):
            compute_jump_on_pead([0.05], jump_threshold=-0.1)


# ============ 3. compute_overnight_trend ============


class TestOvernightTrend:
    def _series(self, vals: list[float]) -> pd.Series:
        return pd.Series(vals, index=pd.date_range("2026-07-01", periods=len(vals), freq="B"))

    def test_rolling_mean_values(self):
        # close 恒 100，open 恒 102 → 隔夜收益恒 2% → 趋势恒 2%
        closes = self._series([100.0] * 30)
        opens = self._series([102.0] * 30)
        trend = compute_overnight_trend(opens, closes, window=20)
        assert np.isnan(trend.iloc[0])  # 无前收
        # 有效隔夜收益自 index1 起，满 20 窗首个有效值在 index20
        assert np.isnan(trend.iloc[19])
        assert trend.iloc[20:].notna().all()
        assert trend.iloc[-1] == pytest.approx(0.02)

    def test_min_periods_requires_full_window(self):
        closes = self._series([100.0] * 25)
        opens = self._series([101.0] * 25)
        trend = compute_overnight_trend(opens, closes, window=20)
        # 有效隔夜收益从 index1 起，满 20 个需到 index20
        assert trend.iloc[:20].isna().all()
        assert trend.iloc[20:].notna().all()

    def test_length_mismatch_raises(self):
        with pytest.raises(EventFactorError):
            compute_overnight_trend(self._series([1.0] * 5), self._series([1.0] * 3))

    def test_invalid_window_raises(self):
        with pytest.raises(EventFactorError):
            compute_overnight_trend(self._series([1.0] * 5), self._series([1.0] * 5), window=0)

    def test_negative_trend_preserved(self):
        # open 恒低于前收 1% → 趋势 -1%（IC 为负的因子方向归下游，原值保留）
        closes = self._series([100.0] * 25)
        opens = self._series([99.0] * 25)
        trend = compute_overnight_trend(opens, closes, window=20)
        assert trend.iloc[-1] == pytest.approx(-0.01)
