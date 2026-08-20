"""MOD-SELL-000 持仓分级判定器 单元测试。"""

from __future__ import annotations

import pytest

from zephyr.position.core.position_drift_monitor import TriageLevel
from zephyr.sell_decision.core.position_triage import (
    InvalidTriageInputError,
    PositionTriage,
    SellPositionSnapshot,
    StrategyType,
)

# ── ATR 自适应分级 ──


def test_watch_when_close_to_stop():
    """距止损 < 1.5×ATR → WATCH。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.4)
    # atr=0.5 → watch_threshold = 1.5*0.5/10 = 0.075
    # distance = |10.4-9.8|/10 = 0.06 < 0.075
    level = PositionTriage.triage(pos, atr_value=0.5, stop_loss_price=9.8)
    assert level is TriageLevel.WATCH


def test_hold_when_deep_profit():
    """深度盈利 > 3×ATR 且远离止损 → HOLD。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=12.0)
    # pnl = 0.2 > 0.15, distance = 0.2 >= 0.075
    level = PositionTriage.triage(pos, atr_value=0.5, stop_loss_price=10.0)
    assert level is TriageLevel.HOLD


def test_monitor_when_middle():
    """中间状态 → MONITOR。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.8)
    # pnl = 0.08 < 0.15, distance = 0.13 >= 0.075
    level = PositionTriage.triage(pos, atr_value=0.5, stop_loss_price=9.5)
    assert level is TriageLevel.MONITOR


def test_watch_boundary_equal_not_triggered():
    """距止损恰好 = 1.5×ATR → 非 WATCH(严格小于)。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.75)
    # distance = 0.075, watch_threshold = 0.075 → 不小于, 不触发
    level = PositionTriage.triage(pos, atr_value=0.5, stop_loss_price=10.0)
    assert level is not TriageLevel.WATCH


# ── ATR 缺失降级 ──


def test_atr_none_defaults_monitor():
    """ATR缺失 → 降级默认MONITOR(spec §3.2正常持仓中间档)。"""
    pos = SellPositionSnapshot(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=10.3,
        strategy_type=StrategyType.SHORT_TERM,
    )
    level = PositionTriage.triage(pos, atr_value=None, stop_loss_price=10.0)
    assert level is TriageLevel.MONITOR


def test_atr_none_deep_profit_still_monitor():
    """ATR缺失即使深度盈利也不升HOLD(无法判定波动率, 保守中间档)。"""
    pos = SellPositionSnapshot(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=13.0,
        strategy_type=StrategyType.OTHER,
    )
    level = PositionTriage.triage(pos, atr_value=None, stop_loss_price=10.0)
    assert level is TriageLevel.MONITOR


def test_atr_zero_triggers_fallback():
    """ATR=0 同样降级MONITOR。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=13.0)
    level = PositionTriage.triage(pos, atr_value=0.0, stop_loss_price=10.0)
    assert level is TriageLevel.MONITOR


# ── 双向反馈 threshold_delta ──


def test_threshold_delta_relax_watch():
    """delta=+0.05(放宽) → watch 阈值降低, 原本 WATCH 变 MONITOR。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.4)
    level = PositionTriage.triage(pos, 0.5, 9.8, threshold_delta=0.05)
    # watch_threshold = 0.075-0.05 = 0.025, distance=0.06 >= 0.025 → 非 WATCH
    # hold_threshold = 0.15-0.05 = 0.10, pnl=0.04 < 0.10 → MONITOR
    assert level is TriageLevel.MONITOR


def test_threshold_delta_tighten():
    """delta=-0.02(收紧) → watch 阈值升高, 更容易进入 WATCH。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.4)
    level = PositionTriage.triage(pos, 0.5, 9.8, threshold_delta=-0.02)
    # watch_threshold = 0.075+0.02 = 0.095, distance=0.06 < 0.095 → WATCH
    assert level is TriageLevel.WATCH


def test_threshold_delta_capped():
    """delta 硬封顶 ±0.10。"""
    pos = SellPositionSnapshot(symbol="000001.SZ", entry_price=10.0, current_price=10.4)
    # delta=0.99 被封顶到 0.10: watch_threshold = 0.075-0.10 = -0.025
    # distance=0.06 >= -0.025 → 非 WATCH
    # hold_threshold = 0.15-0.10 = 0.05, pnl=0.04 < 0.05 → MONITOR
    level = PositionTriage.triage(pos, 0.5, 9.8, threshold_delta=0.99)
    assert level is TriageLevel.MONITOR


# ── 输入校验 ──


def test_empty_symbol_rejected():
    pos = SellPositionSnapshot(symbol="", entry_price=10.0, current_price=10.0)
    with pytest.raises(InvalidTriageInputError):
        PositionTriage.triage(pos, 0.5, 9.5)


def test_zero_entry_price_rejected():
    pos = SellPositionSnapshot(symbol="A", entry_price=0.0, current_price=10.0)
    with pytest.raises(InvalidTriageInputError):
        PositionTriage.triage(pos, 0.5, 9.5)


def test_negative_current_price_rejected():
    pos = SellPositionSnapshot(symbol="A", entry_price=10.0, current_price=-1.0)
    with pytest.raises(InvalidTriageInputError):
        PositionTriage.triage(pos, 0.5, 9.5)


def test_zero_stop_price_rejected():
    pos = SellPositionSnapshot(symbol="A", entry_price=10.0, current_price=10.0)
    with pytest.raises(InvalidTriageInputError):
        PositionTriage.triage(pos, 0.5, 0.0)
