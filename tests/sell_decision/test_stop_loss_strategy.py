# [BLUEPRINT] MOD-SELL-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SELL-005 止损策略族 单元测试。"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.position_triage import SellPositionSnapshot, StrategyType
from zephyr.sell_decision.core.stop_loss_strategy import (
    PositionPhase,
    SellStopLossInputError,
    StopLossStrategy,
    TimeStopSignal,
)

# 测试用最高收盘价回调: N=10 → 11.0, N=22 → 12.0
_HIGHEST = {10: 11.0, 22: 12.0}


def _highest_close_fn(n: int) -> float:
    return _HIGHEST[n]


def _pos(
    current: float = 10.4,
    strategy_type: StrategyType = StrategyType.OTHER,
) -> SellPositionSnapshot:
    return SellPositionSnapshot(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=current,
        strategy_type=strategy_type,
    )


# ── Chandelier 止损: 亏损区/盈利区 ──


def test_loss_phase_chandelier():
    """亏损区: N=10, M=3.0 → 11.0 - 3.0×0.5 = 9.5(OTHER不调整M)。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(),
        atr_value=0.5,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    assert price == pytest.approx(9.5)


def test_profit_phase_chandelier():
    """盈利区: N=22, M=2.0 → 12.0 - 2.0×0.5 = 11.0。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(current=11.0),
        atr_value=0.5,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.PROFIT,
    )
    assert price == pytest.approx(11.0)


# ── 策略类型 M 值调整 ──


def test_trend_strategy_m_widened():
    """趋势策略 M+0.5: 11.0 - 3.5×0.5 = 9.25。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(strategy_type=StrategyType.TREND),
        atr_value=0.5,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    assert price == pytest.approx(9.25)


def test_mean_reversion_m_tightened():
    """均值回归 M-0.5: 11.0 - 2.5×0.5 = 9.75。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(strategy_type=StrategyType.MEAN_REVERSION),
        atr_value=0.5,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    assert price == pytest.approx(9.75)


def test_short_term_m_unchanged():
    """短线 M 不调整: 11.0 - 3.0×0.5 = 9.5。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(strategy_type=StrategyType.SHORT_TERM),
        atr_value=0.5,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    assert price == pytest.approx(9.5)


# ── ATR 缺失降级 ──


def test_atr_none_fallback_short_term():
    """ATR缺失+短线 → 固定4%: 10.0×0.96 = 9.6。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(strategy_type=StrategyType.SHORT_TERM),
        atr_value=None,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    assert price == pytest.approx(9.6)


def test_atr_none_fallback_long_term():
    """ATR缺失+非短线 → 固定8%: 10.0×0.92 = 9.2。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(strategy_type=StrategyType.TREND),
        atr_value=None,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.PROFIT,
    )
    assert price == pytest.approx(9.2)


def test_atr_zero_fallback():
    """ATR=0 同样降级固定%。"""
    price = StopLossStrategy.compute_stop_loss(
        _pos(),
        atr_value=0.0,
        highest_close_fn=_highest_close_fn,
        phase=PositionPhase.LOSS,
    )
    # OTHER 走非短线分支 8%
    assert price == pytest.approx(9.2)


# ── 输入校验 ──


def test_empty_symbol_rejected():
    pos = SellPositionSnapshot(symbol="", entry_price=10.0, current_price=10.0)
    with pytest.raises(SellStopLossInputError):
        StopLossStrategy.compute_stop_loss(pos, 0.5, _highest_close_fn, PositionPhase.LOSS)


def test_non_callable_highest_close_rejected():
    with pytest.raises(SellStopLossInputError):
        StopLossStrategy.compute_stop_loss(
            _pos(),
            0.5,
            None,
            PositionPhase.LOSS,  # type: ignore[arg-type]
        )


def test_invalid_phase_rejected():
    with pytest.raises(SellStopLossInputError):
        StopLossStrategy.compute_stop_loss(
            _pos(),
            0.5,
            _highest_close_fn,
            "loss",  # type: ignore[arg-type]
        )


# ── 时间止损(第⑦类信号源) ──


def test_time_stop_triggered():
    """5天未移动1×ATR → FORCE_EXIT_EVALUATION。"""
    # entry=10, current=10.3, favorable=0.3 < atr=0.5, days=5
    sig = StopLossStrategy.check_time_stop(_pos(current=10.3), 0.5, 5)
    assert sig is TimeStopSignal.FORCE_EXIT_EVALUATION


def test_time_stop_not_triggered_when_moved():
    """5天已移动>=1×ATR → None。"""
    sig = StopLossStrategy.check_time_stop(_pos(current=10.6), 0.5, 5)
    assert sig is None


def test_time_stop_not_triggered_when_days_short():
    """持仓不足5天 → None(即使未移动)。"""
    sig = StopLossStrategy.check_time_stop(_pos(current=10.3), 0.5, 4)
    assert sig is None


def test_time_stop_atr_none_fallback():
    """ATR缺失降级固定1%阈值: entry×0.01=0.1。"""
    # favorable=0.05 < 0.1, days=5 → 触发
    sig = StopLossStrategy.check_time_stop(_pos(current=10.05), None, 5)
    assert sig is TimeStopSignal.FORCE_EXIT_EVALUATION


def test_time_stop_atr_none_not_triggered():
    """ATR缺失但移动>1% → None。"""
    sig = StopLossStrategy.check_time_stop(_pos(current=10.3), None, 5)
    assert sig is None


def test_time_stop_negative_days_rejected():
    with pytest.raises(SellStopLossInputError):
        StopLossStrategy.check_time_stop(_pos(), 0.5, -1)
