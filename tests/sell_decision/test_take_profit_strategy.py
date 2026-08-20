# [BLUEPRINT] MOD-SELL-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SELL-004 止盈策略族 单元测试。"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.position_triage import SellPositionSnapshot, StrategyType
from zephyr.sell_decision.core.take_profit_strategy import (
    InvalidTakeProfitInputError,
    TakeProfitStrategy,
)

# 测试用最高收盘价回调: N=10 → 11.0, N=22 → 12.0
_HIGHEST = {10: 11.0, 22: 12.0}


def _highest_close_fn(n: int) -> float:
    return _HIGHEST[n]


def _pos(
    current: float,
    strategy_type: StrategyType = StrategyType.OTHER,
) -> SellPositionSnapshot:
    return SellPositionSnapshot(
        symbol="000001.SZ",
        entry_price=10.0,
        current_price=current,
        strategy_type=strategy_type,
    )


# ── phase 自动判定 ──


def test_loss_phase_when_profit_below_1atr():
    """盈利<1×ATR → loss 宽 trailing: 11.0-3.0×0.5=9.5。"""
    # entry=10, current=10.4, pnl=0.04 < atr_pct=0.05
    price = TakeProfitStrategy.compute_exit_price(_pos(current=10.4), 0.5, _highest_close_fn)
    assert price == pytest.approx(9.5)


def test_profit_phase_when_profit_above_1atr():
    """盈利>1×ATR → profit 紧 trailing: 12.0-2.0×0.5=11.0。"""
    # pnl=0.06 > atr_pct=0.05
    price = TakeProfitStrategy.compute_exit_price(_pos(current=10.6), 0.5, _highest_close_fn)
    assert price == pytest.approx(11.0)


def test_profit_phase_boundary_equal_1atr():
    """盈利恰好=1×ATR → profit(>=判定)。"""
    # pnl=0.05 >= atr_pct=0.05 → profit
    price = TakeProfitStrategy.compute_exit_price(_pos(current=10.5), 0.5, _highest_close_fn)
    assert price == pytest.approx(11.0)


# ── 策略类型 M 调整(经005核心传导) ──


def test_trend_strategy_wider_exit():
    """趋势策略 loss phase M=3.5: 11.0-3.5×0.5=9.25。"""
    price = TakeProfitStrategy.compute_exit_price(
        _pos(current=10.4, strategy_type=StrategyType.TREND),
        0.5,
        _highest_close_fn,
    )
    assert price == pytest.approx(9.25)


# ── ATR 缺失降级 ──


def test_atr_none_fallback_short():
    """ATR缺失+短线 → 4%: 10.0×0.96=9.6。"""
    price = TakeProfitStrategy.compute_exit_price(
        _pos(current=10.4, strategy_type=StrategyType.SHORT_TERM),
        None,
        _highest_close_fn,
    )
    assert price == pytest.approx(9.6)


def test_atr_none_fallback_medium():
    """ATR缺失+中长线 → 8%: 10.0×0.92=9.2。"""
    price = TakeProfitStrategy.compute_exit_price(_pos(current=10.4), None, _highest_close_fn)
    assert price == pytest.approx(9.2)


def test_atr_zero_fallback():
    """ATR=0 同样降级固定%。"""
    price = TakeProfitStrategy.compute_exit_price(_pos(current=10.4), 0.0, _highest_close_fn)
    assert price == pytest.approx(9.2)


# ── 输入校验 ──


def test_empty_symbol_rejected():
    pos = SellPositionSnapshot(symbol="", entry_price=10.0, current_price=10.0)
    with pytest.raises(InvalidTakeProfitInputError):
        TakeProfitStrategy.compute_exit_price(pos, 0.5, _highest_close_fn)


def test_zero_entry_rejected():
    pos = SellPositionSnapshot(symbol="A", entry_price=0.0, current_price=10.0)
    with pytest.raises(InvalidTakeProfitInputError):
        TakeProfitStrategy.compute_exit_price(pos, 0.5, _highest_close_fn)


def test_non_callable_fn_rejected():
    with pytest.raises(InvalidTakeProfitInputError):
        TakeProfitStrategy.compute_exit_price(
            _pos(current=10.4),
            0.5,
            None,  # type: ignore[arg-type]
        )
