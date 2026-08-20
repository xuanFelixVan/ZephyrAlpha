# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""SellPositionLink 单元测试 (MOD-POS-016)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.sell_position_link import (
    InvalidSellPositionLinkInputError,
    PositionPnLState,
    PositionStateFeedback,
    PostBuyAlertLevel,
    SellPositionLink,
    ThresholdDirection,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 卖出阈值调整 ──────────────────────────────────────────────────────────────


def test_profit_loosens_threshold():
    """盈利 → 放宽阈值(×1.2)。"""
    link = SellPositionLink(profit_loosen_factor=1.2)
    adj = link.adjust_sell_threshold("000001.SZ", sell_threshold=0.05, pnl_ratio=0.12)
    assert adj.pnl_state == PositionPnLState.PROFIT
    assert adj.direction == ThresholdDirection.LOOSEN
    assert adj.factor == pytest.approx(1.2)
    assert adj.adjusted_threshold == pytest.approx(0.06)
    assert adj.delta > 0


def test_loss_tightens_threshold():
    """亏损 → 收紧阈值(×0.8)。"""
    link = SellPositionLink(loss_tighten_factor=0.8)
    adj = link.adjust_sell_threshold("000001.SZ", sell_threshold=0.05, pnl_ratio=-0.08)
    assert adj.pnl_state == PositionPnLState.LOSS
    assert adj.direction == ThresholdDirection.TIGHTEN
    assert adj.factor == pytest.approx(0.8)
    assert adj.adjusted_threshold == pytest.approx(0.04)
    assert adj.delta < 0


def test_breakeven_holds_threshold():
    """持平 → 不变(×1.0)。"""
    link = SellPositionLink(breakeven_tolerance=0.001)
    adj = link.adjust_sell_threshold("000001.SZ", sell_threshold=0.05, pnl_ratio=0.0005)
    assert adj.pnl_state == PositionPnLState.BREAKEVEN
    assert adj.direction == ThresholdDirection.HOLD
    assert adj.factor == pytest.approx(1.0)
    assert adj.adjusted_threshold == pytest.approx(0.05)


def test_adjusted_threshold_never_negative():
    """调整后阈值不可为负。"""
    link = SellPositionLink(loss_tighten_factor=0.1)
    adj = link.adjust_sell_threshold("000001.SZ", sell_threshold=0.01, pnl_ratio=-0.5)
    assert adj.adjusted_threshold >= 0


# ── 买入后即时验证 ────────────────────────────────────────────────────────────


def test_5min_drop_with_volume_spike_triggers_observe():
    """5min 跌破买入价>1%且放量 → OBSERVE。"""
    link = SellPositionLink()
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.85,  # 跌 1.5% > 1%
        minutes_since_entry=4,
        volume_ratio=1.8,  # > 1.5 放量
    )
    assert val.alert_level == PostBuyAlertLevel.OBSERVE
    assert "OBSERVE" in val.reason


def test_5min_drop_no_volume_spike_no_alert():
    """5min 跌破但未放量 → NORMAL。"""
    link = SellPositionLink()
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.85,
        minutes_since_entry=4,
        volume_ratio=1.2,  # < 1.5 未放量
    )
    assert val.alert_level == PostBuyAlertLevel.NORMAL


def test_5min_small_drop_no_alert():
    """5min 跌幅不足1% → NORMAL。"""
    link = SellPositionLink()
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.95,  # 跌 0.5% < 1%
        minutes_since_entry=3,
        volume_ratio=2.0,
    )
    assert val.alert_level == PostBuyAlertLevel.NORMAL


def test_15min_break_ma_triggers_reduce_50():
    """15min 跌破分时均线且反弹无力 → REDUCE_50。"""
    link = SellPositionLink(reduce_ma_minutes=15)
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.80,
        minutes_since_entry=12,
        intraday_ma=9.90,  # 分时均线
        current_ma=9.85,  # 当前均线 < 分时均线(反弹无力)
    )
    assert val.alert_level == PostBuyAlertLevel.REDUCE_50
    assert "REDUCE_50" in val.reason


def test_15min_above_ma_no_alert():
    """15min 价格在均线之上 → NORMAL。"""
    link = SellPositionLink()
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.95,
        minutes_since_entry=12,
        intraday_ma=9.90,
        current_ma=9.95,  # 当前均线 >= 分时均线
    )
    assert val.alert_level == PostBuyAlertLevel.NORMAL


def test_30min_reverse_exceeds_2atr_triggers_full_stop():
    """30min 反向运动 > 2×ATR → FULL_STOP。"""
    link = SellPositionLink(full_stop_atr_multiple=2.0)
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.60,  # 反向运动 0.40
        minutes_since_entry=25,
        atr=0.15,  # 2×ATR = 0.30 < 0.40
    )
    assert val.alert_level == PostBuyAlertLevel.FULL_STOP
    assert "FULL_STOP" in val.reason


def test_30min_reverse_below_2atr_no_alert():
    """30min 反向运动 < 2×ATR → NORMAL。"""
    link = SellPositionLink(full_stop_atr_multiple=2.0)
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.85,  # 反向运动 0.15
        minutes_since_entry=28,
        atr=0.15,  # 2×ATR = 0.30 > 0.15
    )
    assert val.alert_level == PostBuyAlertLevel.NORMAL


# ── 告警级别优先级 ────────────────────────────────────────────────────────────


def test_full_stop_priority_over_reduce_50():
    """FULL_STOP 优先级 > REDUCE_50: 同时满足时取 FULL_STOP。"""
    link = SellPositionLink()
    # 构造同时满足 30min FULL_STOP 和 15min REDUCE_50 的场景
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=9.50,  # 反向 0.50 > 2×ATR(0.15×2=0.30)
        minutes_since_entry=14,  # <= 15 且 <= 30
        intraday_ma=9.90,
        current_ma=9.80,
        atr=0.15,
    )
    assert val.alert_level == PostBuyAlertLevel.FULL_STOP


def test_normal_when_no_conditions_met():
    """所有条件均不满足 → NORMAL。"""
    link = SellPositionLink()
    val = link.validate_post_buy(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=10.05,  # 微涨
        minutes_since_entry=20,
    )
    assert val.alert_level == PostBuyAlertLevel.NORMAL


# ── 汇总反馈 ──────────────────────────────────────────────────────────────────


def test_build_feedback_aggregates():
    """build_feedback 汇总阈值调整与验证结果。"""
    link = SellPositionLink()
    adj = link.adjust_sell_threshold("A", 0.05, 0.10)
    val = link.validate_post_buy("A", 10.0, 9.5, 25, atr=0.15)
    feedback = link.build_feedback([adj], [val], now=T0)
    assert len(feedback.adjustments) == 1
    assert len(feedback.validations) == 1
    assert feedback.timestamp == T0
    assert feedback.has_alerts is True
    assert feedback.max_alert_level == PostBuyAlertLevel.FULL_STOP


def test_feedback_event_emitted_when_alerts():
    """有告警时发出反馈事件。"""
    link = SellPositionLink()
    received: list = []
    link.on_feedback(received.append)

    val = link.validate_post_buy("A", 10.0, 9.5, 25, atr=0.15)
    link.build_feedback([], [val], now=T0)
    assert len(received) == 1
    assert received[0].has_alerts is True


def test_no_event_when_no_alerts():
    """无告警时不发出反馈事件。"""
    link = SellPositionLink()
    received: list = []
    link.on_feedback(received.append)

    val = link.validate_post_buy("A", 10.0, 10.05, 20)
    link.build_feedback([], [val], now=T0)
    assert len(received) == 0


def test_listener_error_isolated():
    """监听器故障不影响主流程。"""
    link = SellPositionLink()

    def bad_listener(_fb):
        raise RuntimeError("boom")

    good_received: list = []
    link.on_feedback(bad_listener)
    link.on_feedback(good_received.append)

    val = link.validate_post_buy("A", 10.0, 9.5, 25, atr=0.15)
    feedback = link.build_feedback([], [val], now=T0)
    assert feedback.has_alerts is True
    assert len(good_received) == 1


def test_max_alert_level_empty():
    """无验证结果时 max_alert_level=NORMAL。"""
    feedback = PositionStateFeedback()
    assert feedback.max_alert_level == PostBuyAlertLevel.NORMAL
    assert feedback.has_alerts is False


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_invalid_profit_factor():
    with pytest.raises(InvalidSellPositionLinkInputError):
        SellPositionLink(profit_loosen_factor=0.9)


def test_invalid_loss_factor():
    with pytest.raises(InvalidSellPositionLinkInputError):
        SellPositionLink(loss_tighten_factor=1.5)


def test_invalid_entry_price():
    link = SellPositionLink()
    with pytest.raises(InvalidSellPositionLinkInputError):
        link.validate_post_buy("A", entry_price=0, current_price=10, minutes_since_entry=5)


def test_invalid_current_price():
    link = SellPositionLink()
    with pytest.raises(InvalidSellPositionLinkInputError):
        link.validate_post_buy("A", entry_price=10, current_price=-1, minutes_since_entry=5)


def test_invalid_negative_threshold():
    link = SellPositionLink()
    with pytest.raises(InvalidSellPositionLinkInputError):
        link.adjust_sell_threshold("A", sell_threshold=-0.1, pnl_ratio=0.1)


def test_invalid_volume_spike_ratio():
    with pytest.raises(InvalidSellPositionLinkInputError):
        SellPositionLink(volume_spike_ratio=0.5)


def test_price_change_ratio_property():
    """PostBuyValidation.price_change_ratio 正确计算。"""
    link = SellPositionLink()
    val = link.validate_post_buy("A", 10.0, 9.5, 20)
    assert val.price_change_ratio == pytest.approx(-0.05)
