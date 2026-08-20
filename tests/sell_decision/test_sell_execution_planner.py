# [BLUEPRINT] MOD-SELL-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SELL-019 卖出执行编排器 单元测试。"""

from __future__ import annotations

from datetime import date, time

import pytest

from zephyr.sell_decision.core.sell_execution_planner import (
    InvalidExecutionPlanInputError,
    LimitDownPosition,
    LiquidationPosition,
    SellExecutionPlanner,
    SellExecutionSignal,
    SellOrderAction,
)

_TODAY = date(2026, 8, 13)


# ── schedule_sell_order: 强制清仓 ──


def test_kill_switch_market_order_now():
    """Kill Switch → 任何时段市价单立即执行。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.KILL_SWITCH, time(10, 0))
    assert plan.action is SellOrderAction.MARKET_ORDER_NOW
    assert plan.order_type == "MARKET"


def test_black_swan_market_order_now():
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.BLACK_SWAN, time(14, 58))
    assert plan.action is SellOrderAction.MARKET_ORDER_NOW


def test_breakout_fail_k_market_order_now():
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.BREAKOUT_FAIL_K, time(9, 45))
    assert plan.action is SellOrderAction.MARKET_ORDER_NOW


def test_kill_switch_limit_down_still_market():
    """Kill Switch 遇跌停仍市价单(挂跌停价排队, P0)。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.KILL_SWITCH, time(10, 0), is_limit_down=True)
    assert plan.action is SellOrderAction.MARKET_ORDER_NOW
    assert "跌停" in plan.window_note


# ── schedule_sell_order: 止损盘中立即 ──


def test_atr_stop_limit_order_before_1457():
    """ATR止损 14:00 → 限价单立即(可撤改挂)。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.ATR_STOP, time(14, 0))
    assert plan.action is SellOrderAction.LIMIT_ORDER_NOW
    assert plan.order_type == "LIMIT"


def test_chandelier_stop_closing_auction_after_1457():
    """Chandelier止损 14:58 → 收盘竞价单(不可撤)。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.CHANDELIER_STOP, time(14, 58))
    assert plan.action is SellOrderAction.CLOSING_AUCTION_LIMIT


def test_support_broken_boundary_1457():
    """支撑破位恰好14:57 → 收盘竞价单(<为前)。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.SUPPORT_BROKEN, time(14, 57))
    assert plan.action is SellOrderAction.CLOSING_AUCTION_LIMIT


# ── schedule_sell_order: 跌停约束 ──


def test_atr_stop_limit_down_queued():
    """止损遇跌停 → 不提交, 排队次日集合竞价。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.ATR_STOP, time(10, 0), is_limit_down=True)
    assert plan.action is SellOrderAction.LIMIT_DOWN_QUEUE
    assert plan.order_type == "NONE"


def test_trailing_tp_limit_down_queued():
    """止盈遇跌停 → 同样排队。"""
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.TRAILING_TP, time(10, 0), is_limit_down=True)
    assert plan.action is SellOrderAction.LIMIT_DOWN_QUEUE


# ── schedule_sell_order: 止盈尾盘集中 ──


def test_trailing_tp_tail_batch():
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.TRAILING_TP, time(10, 0))
    assert plan.action is SellOrderAction.TAIL_BATCH_14_50
    assert plan.order_type == "LIMIT"


def test_rebalance_tail_batch():
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.REBALANCE, time(14, 52))
    assert plan.action is SellOrderAction.TAIL_BATCH_14_50


def test_sentiment_ebb_tail_batch():
    plan = SellExecutionPlanner.schedule_sell_order(SellExecutionSignal.SENTIMENT_EBB, time(11, 0))
    assert plan.action is SellOrderAction.TAIL_BATCH_14_50


# ── schedule_sell_order: T+1 约束 ──


def test_t1_blocked_for_today_buy():
    """当日买入 → BLOCKED_T1(任何信号)。"""
    plan = SellExecutionPlanner.schedule_sell_order(
        SellExecutionSignal.ATR_STOP,
        time(10, 0),
        buy_date=_TODAY,
        today=_TODAY,
    )
    assert plan.action is SellOrderAction.BLOCKED_T1


def test_t1_blocked_even_kill_switch():
    """当日买入即使 Kill Switch 也卖不了(交易所物理约束)。"""
    plan = SellExecutionPlanner.schedule_sell_order(
        SellExecutionSignal.KILL_SWITCH,
        time(10, 0),
        buy_date=_TODAY,
        today=_TODAY,
    )
    assert plan.action is SellOrderAction.BLOCKED_T1


def test_t1_pass_for_yesterday_buy():
    """昨日买入 → 正常走信号映射。"""
    plan = SellExecutionPlanner.schedule_sell_order(
        SellExecutionSignal.ATR_STOP,
        time(10, 0),
        buy_date=date(2026, 8, 12),
        today=_TODAY,
    )
    assert plan.action is SellOrderAction.LIMIT_ORDER_NOW


# ── schedule_sell_order: 输入校验 ──


def test_invalid_signal_type_rejected():
    with pytest.raises(InvalidExecutionPlanInputError):
        SellExecutionPlanner.schedule_sell_order(
            "ATR_STOP",
            time(10, 0),  # type: ignore[arg-type]
        )


def test_invalid_current_time_rejected():
    with pytest.raises(InvalidExecutionPlanInputError):
        SellExecutionPlanner.schedule_sell_order(
            SellExecutionSignal.ATR_STOP,
            "10:00",  # type: ignore[arg-type]
        )


# ── rank_limit_down_orders ──


def test_limit_down_rank_urgency_first():
    """紧迫度最高的排最前(Kill Switch > 止损 > 止盈)。"""
    positions = [
        LimitDownPosition("A", 0.3, -0.05, 100000),  # 止盈级
        LimitDownPosition("B", 1.0, -0.02, 50000),  # Kill Switch
        LimitDownPosition("C", 0.6, -0.08, 80000),  # 止损级
    ]
    ranked = SellExecutionPlanner.rank_limit_down_orders(positions)
    assert [p.symbol for p in ranked] == ["B", "C", "A"]


def test_limit_down_rank_loss_tiebreak():
    """同紧迫度 → 亏损最大的先排。"""
    positions = [
        LimitDownPosition("A", 0.6, -0.03, 100000),
        LimitDownPosition("B", 0.6, -0.09, 50000),
    ]
    ranked = SellExecutionPlanner.rank_limit_down_orders(positions)
    assert [p.symbol for p in ranked] == ["B", "A"]


def test_limit_down_rank_value_tiebreak():
    """同紧迫度同亏损 → 大仓先排。"""
    positions = [
        LimitDownPosition("A", 0.6, -0.05, 50000),
        LimitDownPosition("B", 0.6, -0.05, 200000),
    ]
    ranked = SellExecutionPlanner.rank_limit_down_orders(positions)
    assert [p.symbol for p in ranked] == ["B", "A"]


# ── rank_kill_switch_liquidation ──


def test_liquidation_low_liquidity_first():
    """流动性差的先卖(防封死跌停)。"""
    positions = [
        LiquidationPosition("A", 0.9, 100000, -0.05),  # 流动性好
        LiquidationPosition("B", 0.2, 50000, -0.02),  # 流动性差
        LiquidationPosition("C", 0.5, 80000, -0.08),  # 中等
    ]
    ranked = SellExecutionPlanner.rank_kill_switch_liquidation(positions)
    assert [p.symbol for p in ranked] == ["B", "C", "A"]


def test_liquidation_value_tiebreak():
    """同流动性 → 大仓先卖。"""
    positions = [
        LiquidationPosition("A", 0.5, 50000, -0.05),
        LiquidationPosition("B", 0.5, 200000, -0.05),
    ]
    ranked = SellExecutionPlanner.rank_kill_switch_liquidation(positions)
    assert [p.symbol for p in ranked] == ["B", "A"]


def test_liquidation_loss_tiebreak():
    """同流动性同仓位 → 亏损最大的先卖。"""
    positions = [
        LiquidationPosition("A", 0.5, 100000, -0.02),
        LiquidationPosition("B", 0.5, 100000, -0.09),
    ]
    ranked = SellExecutionPlanner.rank_kill_switch_liquidation(positions)
    assert [p.symbol for p in ranked] == ["B", "A"]


def test_liquidation_empty_list():
    """空列表 → 空结果。"""
    assert SellExecutionPlanner.rank_kill_switch_liquidation([]) == []
