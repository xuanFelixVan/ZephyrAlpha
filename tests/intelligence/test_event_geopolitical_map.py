# [MODULE] tests.intelligence.test_event_geopolitical_map
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_geopolitical_map.py -q
"""test_event_geopolitical_map.py — 地缘事件→板块传导映射单元测试（26 号 §2.5b）。

覆盖：
  1. 五类映射表完整性（beneficiary/victim/rising_half_life 结构）
  2. map_geopolitical_event_to_sectors —— 已知标签/未知标签/event_score 公式
     （权重 1.4×方向×情绪×衰减）/rising 窗内外/sentiment 裁剪
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.event_geopolitical_map import (
    GEOPOLITICAL_SECTOR_MAP,
    map_geopolitical_event_to_sectors,
)

# ============ 1. 映射表完整性 ============


class TestMapIntegrity:
    def test_five_event_types(self):
        assert set(GEOPOLITICAL_SECTOR_MAP) == {
            "middle_east_conflict",
            "trade_war_escalation",
            "currency_depreciation",
            "commodity_price_surge",
            "tech_sanctions",
        }

    def test_each_entry_structure(self):
        for tag, m in GEOPOLITICAL_SECTOR_MAP.items():
            assert m["beneficiary_sectors"], tag
            assert isinstance(m["victim_sectors"], list), tag
            assert m["transmission_logic"], tag
            hl = m["rising_half_life_days"].split("-")
            assert int(hl[0]) >= 1, tag


# ============ 2. map_geopolitical_event_to_sectors ============


class TestMapGeopoliticalEvent:
    def test_middle_east_conflict_beneficiaries(self):
        b, v, score = map_geopolitical_event_to_sectors("middle_east_conflict", 0.8)
        assert "油气开采" in b and "黄金" in b and "军工" in b
        assert "航空" in v
        assert score > 0

    def test_unknown_tag_returns_empty(self):
        assert map_geopolitical_event_to_sectors("unknown_event", 0.8) == ([], [], 0.0)

    def test_event_score_formula_rising_window(self):
        # 1.4 × 1 × 0.5 × 1.0（rising 窗内）× 1.0
        _, _, score = map_geopolitical_event_to_sectors("trade_war_escalation", 0.5, days_since_event=0)
        assert score == pytest.approx(1.4 * 0.5 * 1.0)

    def test_event_score_decayed_after_rising_window(self):
        # tech_sanctions rising_hl 下限 10：day 11 → 衰减 0.5
        _, _, score = map_geopolitical_event_to_sectors("tech_sanctions", 0.5, days_since_event=11)
        assert score == pytest.approx(1.4 * 0.5 * 0.5)

    def test_event_score_at_rising_boundary(self):
        # currency_depreciation rising_hl 下限 3：day 3 仍在窗内
        _, _, score = map_geopolitical_event_to_sectors("currency_depreciation", 1.0, days_since_event=3)
        assert score == pytest.approx(1.4 * 1.0 * 1.0)

    def test_negative_sentiment_gives_negative_score(self):
        _, _, score = map_geopolitical_event_to_sectors("middle_east_conflict", -0.6)
        assert score == pytest.approx(1.4 * -0.6)

    def test_sentiment_clipped(self):
        _, _, score = map_geopolitical_event_to_sectors("middle_east_conflict", 5.0)
        assert score == pytest.approx(1.4 * 1.0)

    def test_zero_sentiment_zero_score(self):
        _, _, score = map_geopolitical_event_to_sectors("middle_east_conflict", 0.0)
        assert score == 0.0
