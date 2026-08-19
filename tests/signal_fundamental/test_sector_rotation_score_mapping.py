# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.1 v1.1.16
# [TTL] permanent
"""板块轮动 score 映射公式单元测试——含 memo 原文示例复算与边界用例。"""
from __future__ import annotations

import pytest

from zephyr.signal_ashare.sector_rrg import RRGQuadrant
from zephyr.signal_fundamental.sector_rotation_score_mapping import (
    PULLBACK_QUALITY_BONUS,
    SECTOR_QUADRANT_BASE,
    map_sector_rotation_score,
)


class TestMemoExamples:
    """memo §3.1 原文两例复算。"""

    def test_leading_full_clamp(self):
        # Leading(0.8) + 强度 80(0.16) + 回踩 A(0.15) = 1.11 → clamp → 1.0
        score = map_sector_rotation_score(RRGQuadrant.LEADING, 80.0, "A")
        assert score == pytest.approx(1.0)

    def test_improving_mid(self):
        # Improving(0.6) + 强度 50(0.10) + 回踩 B(0.05) = 0.75
        score = map_sector_rotation_score(RRGQuadrant.IMPROVING, 50.0, "B")
        assert score == pytest.approx(0.75)


class TestQuadrantBase:
    def test_base_values_cover_all_quadrants(self):
        assert SECTOR_QUADRANT_BASE[RRGQuadrant.LEADING] == 0.8
        assert SECTOR_QUADRANT_BASE[RRGQuadrant.IMPROVING] == 0.6
        assert SECTOR_QUADRANT_BASE[RRGQuadrant.WEAKENING] == 0.3
        assert SECTOR_QUADRANT_BASE[RRGQuadrant.LAGGING] == 0.1
        assert len(SECTOR_QUADRANT_BASE) == 4

    def test_quadrant_ordering(self):
        s_lead = map_sector_rotation_score(RRGQuadrant.LEADING, 50.0)
        s_impr = map_sector_rotation_score(RRGQuadrant.IMPROVING, 50.0)
        s_weak = map_sector_rotation_score(RRGQuadrant.WEAKENING, 50.0)
        s_lagg = map_sector_rotation_score(RRGQuadrant.LAGGING, 50.0)
        assert s_lead > s_impr > s_weak > s_lagg

    def test_string_quadrant_case_insensitive(self):
        assert map_sector_rotation_score("leading", 50.0) == map_sector_rotation_score(
            RRGQuadrant.LEADING, 50.0
        )
        assert map_sector_rotation_score("LEADING", 50.0) == map_sector_rotation_score(
            "Leading", 50.0
        )


class TestQualityBonus:
    def test_bonus_values(self):
        assert PULLBACK_QUALITY_BONUS == {"A": 0.15, "B": 0.05, "C": -0.05}

    def test_none_quality_neutral(self):
        assert map_sector_rotation_score(
            RRGQuadrant.LEADING, 50.0, None
        ) == pytest.approx(0.8 + 0.1)

    def test_lowercase_quality_accepted(self):
        assert map_sector_rotation_score(
            RRGQuadrant.LEADING, 50.0, "a"
        ) == pytest.approx(map_sector_rotation_score(RRGQuadrant.LEADING, 50.0, "A"))

    def test_invalid_quality_raises(self):
        with pytest.raises(ValueError):
            map_sector_rotation_score(RRGQuadrant.LEADING, 50.0, "D")


class TestBoundaries:
    def test_strength_clipped(self):
        s100 = map_sector_rotation_score(RRGQuadrant.IMPROVING, 100.0)
        s_over = map_sector_rotation_score(RRGQuadrant.IMPROVING, 150.0)
        s_neg = map_sector_rotation_score(RRGQuadrant.IMPROVING, -20.0)
        s0 = map_sector_rotation_score(RRGQuadrant.IMPROVING, 0.0)
        assert s_over == pytest.approx(s100)
        assert s_neg == pytest.approx(s0)

    def test_lower_clamp(self):
        # Lagging(0.1) + 强度 0 + 回踩 C(-0.05) = 0.05（不触底）
        score = map_sector_rotation_score(RRGQuadrant.LAGGING, 0.0, "C")
        assert score == pytest.approx(0.05)
        assert 0.0 <= score <= 1.0

    def test_invalid_quadrant_raises(self):
        with pytest.raises(ValueError):
            map_sector_rotation_score("UNKNOWN", 50.0)
        with pytest.raises(ValueError):
            map_sector_rotation_score(123, 50.0)
