"""MOD-SELL-015 止损猎杀防护器 单元测试。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.sell_signal_collector import SellDirection
from zephyr.sell_decision.core.stop_hunting_protector import (
    AdjustedStopLevel,
    InvalidStopHuntInputError,
    SoftStopState,
    StopHuntingProtector,
    StopHuntOffsetDirection,
)

T0 = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


# ── 止损位偏移 ──


def test_adjust_stop_below_default_offset():
    """默认偏移2% BELOW → 止损位下移。"""
    p = StopHuntingProtector()
    r = p.adjust_stop_level("000001.SZ", 10.00, now=T0)
    assert r.adjusted_stop == pytest.approx(9.80)
    assert r.offset_direction is StopHuntOffsetDirection.BELOW
    assert r.offset_pct == pytest.approx(0.02)
    assert r.soft_stop_state is SoftStopState.NORMAL
    assert r.confirmed is False


def test_adjust_stop_above_direction():
    """ABOVE 方向 → 止损位上移。"""
    p = StopHuntingProtector()
    r = p.adjust_stop_level("A", 10.00, direction=StopHuntOffsetDirection.ABOVE, now=T0)
    assert r.adjusted_stop == pytest.approx(10.20)


def test_adjust_stop_custom_offset():
    """自定义偏移比例 1%。"""
    p = StopHuntingProtector()
    r = p.adjust_stop_level("A", 10.00, offset_pct=0.01, now=T0)
    assert r.adjusted_stop == pytest.approx(9.90)


def test_adjust_stop_records_original():
    """记录原始止损位。"""
    p = StopHuntingProtector()
    r = p.adjust_stop_level("A", 10.00, now=T0)
    assert r.original_stop == 10.00
    assert r.adjusted_stop == pytest.approx(9.80)


# ── 软止损状态机 ──


def test_soft_stop_normal_to_observing():
    """NORMAL + 价格触及止损位 → OBSERVING。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.75, 9.76, SoftStopState.NORMAL, now=T0)
    assert r.soft_stop_state is SoftStopState.OBSERVING
    assert r.confirmed is False
    assert r.direction is SellDirection.REDUCE
    assert r.confidence == pytest.approx(0.5)


def test_soft_stop_normal_stays_when_above():
    """NORMAL + 价格>止损位 → 保持 NORMAL。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.90, 9.85, SoftStopState.NORMAL, now=T0)
    assert r.soft_stop_state is SoftStopState.NORMAL
    assert r.confidence == pytest.approx(0.0)


def test_soft_stop_observing_to_confirmed():
    """OBSERVING + 收盘价<止损位 → CONFIRMED(执行清仓)。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.70, 9.75, SoftStopState.OBSERVING, now=T0)
    assert r.soft_stop_state is SoftStopState.CONFIRMED
    assert r.confirmed is True
    assert r.direction is SellDirection.CLEAR
    assert r.confidence == pytest.approx(1.0)


def test_soft_stop_observing_to_cleared():
    """OBSERVING + 价格回升 → CLEARED(解除)。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.85, 9.82, SoftStopState.OBSERVING, now=T0)
    assert r.soft_stop_state is SoftStopState.CLEARED
    assert r.confirmed is False
    assert r.confidence == pytest.approx(0.0)


def test_soft_stop_observing_stays_when_in_range():
    """OBSERVING + 价格≤止损位且收盘价≥止损位 → 保持 OBSERVING。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.78, 9.80, SoftStopState.OBSERVING, now=T0)
    # current=9.78 <= stop=9.80, close=9.80 >= stop=9.80 → 保持 OBSERVING
    assert r.soft_stop_state is SoftStopState.OBSERVING


def test_soft_stop_confirmed_is_terminal():
    """CONFIRMED 是终态(保持)。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.90, 9.85, SoftStopState.CONFIRMED, now=T0)
    assert r.soft_stop_state is SoftStopState.CONFIRMED


def test_soft_stop_cleared_to_observing_retrigger():
    """CLEARED + 价格再次触及止损位 → 重新 OBSERVING。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.75, 9.76, SoftStopState.CLEARED, now=T0)
    assert r.soft_stop_state is SoftStopState.OBSERVING


def test_soft_stop_cleared_stays_when_above():
    """CLEARED + 价格>止损位 → NORMAL。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.90, 9.85, SoftStopState.CLEARED, now=T0)
    assert r.soft_stop_state is SoftStopState.NORMAL


def test_soft_stop_equal_price_triggers_observing():
    """价格==止损位 → 触发 OBSERVING(≤判定)。"""
    p = StopHuntingProtector()
    r = p.evaluate_soft_stop("A", 9.80, 9.80, 9.80, SoftStopState.NORMAL, now=T0)
    assert r.soft_stop_state is SoftStopState.OBSERVING


# ── 输入校验 ──


def test_invalid_empty_symbol_adjust():
    with pytest.raises(InvalidStopHuntInputError, match="symbol"):
        StopHuntingProtector().adjust_stop_level("", 10.00)


def test_invalid_stop_zero_adjust():
    with pytest.raises(InvalidStopHuntInputError, match="original_stop"):
        StopHuntingProtector().adjust_stop_level("A", 0)


def test_invalid_offset_overflow_adjust():
    with pytest.raises(InvalidStopHuntInputError, match="offset_pct"):
        StopHuntingProtector().adjust_stop_level("A", 10.00, offset_pct=1.5)


def test_invalid_empty_symbol_soft_stop():
    with pytest.raises(InvalidStopHuntInputError, match="symbol"):
        StopHuntingProtector().evaluate_soft_stop("", 9.80, 9.70, 9.75)


def test_invalid_price_zero_soft_stop():
    with pytest.raises(InvalidStopHuntInputError, match="current_price"):
        StopHuntingProtector().evaluate_soft_stop("A", 9.80, 0, 9.75)


def test_invalid_close_zero_soft_stop():
    with pytest.raises(InvalidStopHuntInputError, match="close_price"):
        StopHuntingProtector().evaluate_soft_stop("A", 9.80, 9.70, 0)


# ── 构造器校验 ──


def test_protector_invalid_offset_zero():
    with pytest.raises(InvalidStopHuntInputError, match="default_offset_pct"):
        StopHuntingProtector(default_offset_pct=0)


def test_protector_invalid_offset_too_large():
    with pytest.raises(InvalidStopHuntInputError, match="default_offset_pct"):
        StopHuntingProtector(default_offset_pct=0.2)


# ── AdjustedStopLevel 校验 ──


def test_result_invalid_confidence_overflow():
    with pytest.raises(InvalidStopHuntInputError, match="confidence"):
        AdjustedStopLevel(
            symbol="A",
            original_stop=10.0,
            adjusted_stop=9.8,
            offset_pct=0.02,
            offset_direction=StopHuntOffsetDirection.BELOW,
            soft_stop_state=SoftStopState.NORMAL,
            confirmed=False,
            confidence=1.5,
            direction=SellDirection.REPLACE,
        )


def test_result_invalid_original_stop_zero():
    with pytest.raises(InvalidStopHuntInputError, match="original_stop"):
        AdjustedStopLevel(
            symbol="A",
            original_stop=0,
            adjusted_stop=9.8,
            offset_pct=0.02,
            offset_direction=StopHuntOffsetDirection.BELOW,
            soft_stop_state=SoftStopState.NORMAL,
            confirmed=False,
            confidence=0.0,
            direction=SellDirection.REPLACE,
        )


# ── 事件回调 ──


def test_on_adjusted_callback_invoked():
    """防护结果生成触发回调。"""
    received: list[AdjustedStopLevel] = []
    p = StopHuntingProtector()
    p.on_adjusted(received.append)
    p.adjust_stop_level("A", 10.00, now=T0)
    assert len(received) == 1


def test_on_adjusted_callback_failure_isolated():
    """回调异常不阻断。"""

    def bad_cb(_):
        raise RuntimeError("boom")

    p = StopHuntingProtector()
    p.on_adjusted(bad_cb)
    r = p.adjust_stop_level("A", 10.00, now=T0)
    assert r.adjusted_stop == pytest.approx(9.80)


# ── 时钟注入 ──


def test_custom_clock_injection():
    fixed = datetime(2025, 1, 1, tzinfo=timezone.utc)
    p = StopHuntingProtector(clock=lambda: fixed)
    r = p.adjust_stop_level("A", 10.00)
    assert r.timestamp == fixed


# ── 端到端流程 ──


def test_full_soft_stop_lifecycle():
    """完整软止损生命周期: NORMAL→OBSERVING→CONFIRMED。"""
    p = StopHuntingProtector()
    # ① 调整止损位
    adjusted = p.adjust_stop_level("A", 10.00, now=T0)
    stop = adjusted.adjusted_stop  # 9.80
    # ② 价格触及 → OBSERVING
    r1 = p.evaluate_soft_stop("A", stop, 9.75, 9.76, SoftStopState.NORMAL, now=T0)
    assert r1.soft_stop_state is SoftStopState.OBSERVING
    # ③ 收盘确认跌破 → CONFIRMED
    r2 = p.evaluate_soft_stop("A", stop, 9.70, 9.72, SoftStopState.OBSERVING, now=T0)
    assert r2.soft_stop_state is SoftStopState.CONFIRMED
    assert r2.confirmed is True
