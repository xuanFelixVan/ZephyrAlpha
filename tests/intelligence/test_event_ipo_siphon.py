# [MODULE] tests.intelligence.test_event_ipo_siphon
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_ipo_siphon.py -q
"""test_event_ipo_siphon.py — IPO 虹吸量化算法单元测试（26 号 §2.5a）。

覆盖：
  1. compute_ipo_siphon_coefficient —— 四级分级边界（1%/2%/3%）/长鑫案例锚点/退化输入
  2. ipo_siphon_position_adjustment —— 窗口分支（前3-5天/前1-2天/上市后0-5天/期外）/级别门控
"""
from __future__ import annotations

import pytest

from zephyr.intelligence.event_ipo_siphon import (
    ACTION_ACCELERATE_ENTRY,
    ACTION_HOLD_CASH,
    ACTION_NORMAL,
    ACTION_REDUCE_EXISTING,
    SIPHON_LEVEL_EXTREME,
    SIPHON_LEVEL_MODERATE,
    SIPHON_LEVEL_NEGLIGIBLE,
    SIPHON_LEVEL_SEVERE,
    compute_ipo_siphon_coefficient,
    ipo_siphon_position_adjustment,
)

# ============ 1. compute_ipo_siphon_coefficient ============


class TestSiphonCoefficient:
    def test_negligible_below_1pct(self):
        ratio, level = compute_ipo_siphon_coefficient(200.0, 27000.0)  # 0.74%
        assert ratio == pytest.approx(200.0 / 27000.0)
        assert level == SIPHON_LEVEL_NEGLIGIBLE

    def test_moderate_band(self):
        _, level = compute_ipo_siphon_coefficient(400.0, 27000.0)  # 1.48%
        assert level == SIPHON_LEVEL_MODERATE

    def test_severe_band_changxin_anchor(self):
        # 长鑫锚点：666 亿 / 27000 亿 ≈ 2.47% → SEVERE（memo §2.5a 实证）
        ratio, level = compute_ipo_siphon_coefficient(666.0, 27000.0)
        assert ratio == pytest.approx(0.0247, abs=1e-4)
        assert level == SIPHON_LEVEL_SEVERE

    def test_extreme_above_3pct(self):
        _, level = compute_ipo_siphon_coefficient(900.0, 27000.0)  # 3.33%
        assert level == SIPHON_LEVEL_EXTREME

    def test_boundary_exactly_1pct_is_moderate(self):
        _, level = compute_ipo_siphon_coefficient(270.0, 27000.0)  # 恰好 1%
        assert level == SIPHON_LEVEL_MODERATE

    def test_boundary_exactly_2pct_is_severe(self):
        _, level = compute_ipo_siphon_coefficient(540.0, 27000.0)
        assert level == SIPHON_LEVEL_SEVERE

    def test_boundary_exactly_3pct_is_extreme(self):
        _, level = compute_ipo_siphon_coefficient(810.0, 27000.0)
        assert level == SIPHON_LEVEL_EXTREME

    def test_zero_market_volume_degrades(self):
        ratio, level = compute_ipo_siphon_coefficient(666.0, 0.0)
        assert (ratio, level) == (0.0, SIPHON_LEVEL_NEGLIGIBLE)

    def test_negative_market_volume_degrades(self):
        _, level = compute_ipo_siphon_coefficient(666.0, -100.0)
        assert level == SIPHON_LEVEL_NEGLIGIBLE

    def test_negative_raise_clamped_zero(self):
        ratio, level = compute_ipo_siphon_coefficient(-50.0, 27000.0)
        assert ratio == 0.0
        assert level == SIPHON_LEVEL_NEGLIGIBLE


# ============ 2. ipo_siphon_position_adjustment ============


class TestPositionAdjustment:
    def test_accelerate_entry_window(self):
        for d in (3, 4, 5):
            action, reason = ipo_siphon_position_adjustment(d, SIPHON_LEVEL_SEVERE, "长鑫科技")
            assert action == ACTION_ACCELERATE_ENTRY
            assert "布局窗口" in reason

    def test_hold_cash_window(self):
        for d in (1, 2):
            action, reason = ipo_siphon_position_adjustment(d, SIPHON_LEVEL_EXTREME, "长鑫科技")
            assert action == ACTION_HOLD_CASH
            assert "25%" in reason
            assert "长鑫科技" in reason

    def test_reduce_existing_window(self):
        for d in (-5, -3, 0):
            action, _ = ipo_siphon_position_adjustment(d, SIPHON_LEVEL_SEVERE)
            assert action == ACTION_REDUCE_EXISTING

    def test_outside_window_normal(self):
        assert ipo_siphon_position_adjustment(6, SIPHON_LEVEL_SEVERE)[0] == ACTION_NORMAL
        assert ipo_siphon_position_adjustment(-6, SIPHON_LEVEL_SEVERE)[0] == ACTION_NORMAL

    def test_moderate_always_normal(self):
        for d in (4, 1, 0, -3):
            assert ipo_siphon_position_adjustment(d, SIPHON_LEVEL_MODERATE)[0] == ACTION_NORMAL

    def test_negligible_always_normal(self):
        action, reason = ipo_siphon_position_adjustment(2, SIPHON_LEVEL_NEGLIGIBLE)
        assert action == ACTION_NORMAL
        assert "可忽略" in reason

    def test_extreme_same_windows_as_severe(self):
        assert ipo_siphon_position_adjustment(4, SIPHON_LEVEL_EXTREME)[0] == ACTION_ACCELERATE_ENTRY
        assert ipo_siphon_position_adjustment(0, SIPHON_LEVEL_EXTREME)[0] == ACTION_REDUCE_EXISTING
