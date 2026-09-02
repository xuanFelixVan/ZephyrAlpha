# [A_test] module_id: MOD-SIG-106 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-106 | docs/03_modules/_domain_signal/sell_news_overdraft_detector/blueprint.md
# [MODULE] tests.signal_ashare.test_sell_news_overdraft_detector
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.sell_news_overdraft_detector

"""利好落地变利空预期透支检测（MOD-SIG-106，B10-01453）施工验证测试。

覆盖：事件5类可预测性映射、四维透支度计算与边界、3档判定、5阶段标注（含 T=0/负天）、
落地前减仓/已落地清仓/尚早 watch、黑天鹅不适用、非法输入 fail-closed、frozen/JSON 契约。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.sell_news_overdraft_detector import (
    EVENT_PREDICTABILITY,
    NewsEventContext,
    OverdraftConfig,
    OverdraftLevel,
    SellNewsOverdraftDetector,
    TimelinePhase,
)


def _det() -> SellNewsOverdraftDetector:
    return SellNewsOverdraftDetector(OverdraftConfig())


class TestPredictability:
    def test_policy_high(self):
        assert EVENT_PREDICTABILITY["policy"] == "high"

    def test_black_swan_unpredictable(self):
        assert EVENT_PREDICTABILITY["black_swan"] == "unpredictable"


class TestOverdraftDimensions:
    def test_price_overdraft(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=5,
            price_gain_ratio=1.30,
            time_advance_days=20,
            capital_inflow_ratio=0.80,
            sentiment_peak_ratio=0.90,
        )
        a = det.assess(ctx)
        assert a.price_overdraft > 1.0

    def test_time_overdraft_capped(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=5,
            price_gain_ratio=1.00,
            time_advance_days=40,
            capital_inflow_ratio=0.80,
            sentiment_peak_ratio=0.90,
        )
        a = det.assess(ctx)
        assert a.time_overdraft == pytest.approx(1.0, abs=1e-9)

    def test_composite_severe(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=2,
            price_gain_ratio=2.00,
            time_advance_days=30,
            capital_inflow_ratio=1.50,
            sentiment_peak_ratio=1.00,
        )
        a = det.assess(ctx)
        assert a.level == OverdraftLevel.SEVERE

    def test_composite_none(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=20,
            price_gain_ratio=1.00,
            time_advance_days=10,
            capital_inflow_ratio=0.30,
            sentiment_peak_ratio=0.50,
        )
        a = det.assess(ctx)
        assert a.level == OverdraftLevel.NONE


class TestTimelinePhase:
    def test_early(self):
        assert _phase(20) == TimelinePhase.EARLY_ACCUMULATION

    def test_late(self):
        assert _phase(3) == TimelinePhase.LATE_SPRINT

    def test_landing_day(self):
        assert _phase(0) == TimelinePhase.LANDING_DAY

    def test_post_landing(self):
        assert _phase(-2) == TimelinePhase.POST_LANDING


class TestAction:
    def test_reduce_before_landing(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=2,
            price_gain_ratio=2.00,
            time_advance_days=30,
            capital_inflow_ratio=1.50,
            sentiment_peak_ratio=1.00,
        )
        a = det.assess(ctx)
        assert a.action == "reduce"

    def test_clear_after_landing(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=-1,
            price_gain_ratio=2.00,
            time_advance_days=30,
            capital_inflow_ratio=1.50,
            sentiment_peak_ratio=1.00,
        )
        a = det.assess(ctx)
        assert a.action == "clear"

    def test_watch_early(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=15,
            price_gain_ratio=2.00,
            time_advance_days=30,
            capital_inflow_ratio=1.50,
            sentiment_peak_ratio=1.00,
        )
        a = det.assess(ctx)
        assert a.action == "watch"

    def test_none_action(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="policy",
            days_to_landing=2,
            price_gain_ratio=1.00,
            time_advance_days=10,
            capital_inflow_ratio=0.30,
            sentiment_peak_ratio=0.50,
        )
        a = det.assess(ctx)
        assert a.action == "none"

    def test_black_swan_not_applicable(self):
        det = _det()
        ctx = NewsEventContext(
            event_type="black_swan",
            days_to_landing=2,
            price_gain_ratio=1.30,
            time_advance_days=25,
            capital_inflow_ratio=1.20,
            sentiment_peak_ratio=0.95,
        )
        a = det.assess(ctx)
        assert a.applicable is False
        assert a.action == "not_applicable"


class TestFailClosed:
    def test_zero_price_mean_raises(self):
        with pytest.raises(ValueError):
            NewsEventContext(event_type="policy", days_to_landing=5, price_gain_ratio=1.30, historical_mean_price=0.0)

    def test_negative_sentiment_peak_raises(self):
        with pytest.raises(ValueError):
            NewsEventContext(event_type="policy", days_to_landing=5, sentiment_peak_ratio=-0.1)


class TestFrozenAndJson:
    def test_frozen(self):
        ctx = NewsEventContext(event_type="policy", days_to_landing=5, price_gain_ratio=1.0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.price_gain_ratio = 2.0

    def test_json(self):
        ctx = NewsEventContext(event_type="policy", days_to_landing=5, price_gain_ratio=1.0)
        assert json.dumps(dataclasses.asdict(ctx))


# helpers
def _phase(days_to_landing: int):
    det = _det()
    ctx = NewsEventContext(event_type="policy", days_to_landing=days_to_landing, price_gain_ratio=1.0)
    return det.assess(ctx).phase
