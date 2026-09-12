# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.3
# [TTL] permanent
"""选股漏斗第四层 事件驱动分布筛选（BM-SEL-19，MOD-SIG-049）单元测试——含门控/衰减/截断/跳过用例。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.event_driven_screener import (
    EventCategory,
    EventImpactRecord,
    EventScreenConfig,
    event_halflife_days,
    screen_events,
)


def _rec(symbol: str, **kw) -> EventImpactRecord:
    return EventImpactRecord(symbol=symbol, **kw)


class TestHalflife:
    @pytest.mark.parametrize(
        ("cat", "expected"),
        [
            (EventCategory.EARNINGS, 4.0),
            (EventCategory.MERGER, 2.0),
            (EventCategory.POLICY, 5.0),
            (EventCategory.SUDDEN, 2.0),
            (EventCategory.IPO, 4.0),
            (EventCategory.GEO, 10.0),
        ],
    )
    def test_category_halflife(self, cat, expected):
        assert event_halflife_days(cat) == pytest.approx(expected)

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            event_halflife_days("UNKNOWN")


class TestScreenEvents:
    def test_no_event_records_all_kept(self):
        out = screen_events([_rec("A"), _rec("B")])
        assert out.kept == ("A", "B")
        assert out.weights == {"A": 1.0, "B": 1.0}
        assert out.skipped is False

    def test_source_not_ready_skips_layer(self):
        """没事件数据源 → skipped 直通不筛（含利空标的也保留）。"""
        recs = [_rec("NEG", has_event=True, direction=-1, confidence=0.9)]
        out = screen_events(recs, event_source_ready=False)
        assert out.skipped is True
        assert out.kept == ("NEG",)

    def test_negative_event_excluded(self):
        recs = [
            _rec("NEG", has_event=True, direction=-1, strength=0.8, confidence=0.9),
            _rec("POS", has_event=True, direction=1, strength=0.8, confidence=0.9),
        ]
        out = screen_events(recs)
        assert out.kept == ("POS",)
        assert out.excluded["NEG"] == "event:negative"

    def test_low_confidence_treated_as_no_event(self):
        """confidence<0.7 → 视为无事件：不剔除也不加权。"""
        recs = [_rec("LOWCONF", has_event=True, direction=-1, strength=1.0, confidence=0.5)]
        out = screen_events(recs)
        assert out.kept == ("LOWCONF",)
        assert out.weights["LOWCONF"] == 1.0

    def test_extreme_reaction_excluded_both_directions(self):
        """PEAD Inversion：|reaction|>3% 不追涨不杀跌。"""
        recs = [
            _rec("EXUP", has_event=True, direction=1, strength=0.9, confidence=0.9, reaction_pct=4.5),
            _rec("EXDN", has_event=True, direction=-1, strength=0.9, confidence=0.9, reaction_pct=-4.5),
            _rec("MILD", has_event=True, direction=1, strength=0.9, confidence=0.9, reaction_pct=1.5),
        ]
        out = screen_events(recs)
        assert out.kept == ("MILD",)
        assert out.excluded["EXUP"].startswith("event:extreme_reaction")
        assert "EXDN" in out.excluded  # 利空先命中 negative 排除（顺序优先）

    def test_conduction_risk_excluded(self):
        recs = [
            _rec("RISKY", has_event=True, direction=1, strength=0.5, confidence=0.9, conduction_risk=0.8),
            _rec("SAFE", has_event=True, direction=1, strength=0.5, confidence=0.9, conduction_risk=0.3),
        ]
        out = screen_events(recs)
        assert out.kept == ("SAFE",)
        assert out.excluded["RISKY"] == "event:conduction_risk"

    def test_weight_decays_with_age(self):
        young = screen_events([_rec("Y", has_event=True, direction=1, strength=1.0, confidence=0.9, age_days=0)])
        old = screen_events([_rec("O", has_event=True, direction=1, strength=1.0, confidence=0.9, age_days=4)])
        assert young.weights["Y"] == pytest.approx(2.0)  # 1 + 1×1×2^0
        assert old.weights["O"] == pytest.approx(1.5)  # 业绩半衰期 4 天 → 2^(−1)=0.5

    def test_capacity_truncation_by_weight(self):
        cfg = EventScreenConfig(capacity_target=2)
        recs = [
            _rec("NOEVT"),
            _rec("WEAK", has_event=True, direction=1, strength=0.2, confidence=0.9),
            _rec("STRONG", has_event=True, direction=1, strength=1.0, confidence=0.9),
        ]
        out = screen_events(recs, config=cfg)
        assert out.truncated is True
        assert out.kept == ("STRONG", "WEAK")

    def test_degraded_only_negative_excluded(self):
        recs = [
            _rec("NEG", has_event=True, direction=-1, confidence=0.9),
            _rec("EXUP", has_event=True, direction=1, confidence=0.9, reaction_pct=9.0),
            _rec("RISKY", conduction_risk=0.99),
        ]
        out = screen_events(recs, degraded=True)
        assert out.degraded is True
        assert set(out.kept) == {"EXUP", "RISKY"}
        assert set(out.excluded) == {"NEG"}

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError):
            screen_events([_rec("A")], config=EventScreenConfig(capacity_target=0))

    def test_empty_input(self):
        out = screen_events([])
        assert out.kept == ()
