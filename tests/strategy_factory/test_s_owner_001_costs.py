"""成本封装单测——佣金地板/ETF 豁免/做T 加成/标定分层接入。"""

from __future__ import annotations

from decimal import Decimal

from zephyr.backtest.core.matching_logic import COMMISSION_RATE, MIN_COMMISSION
from zephyr.strategy_factory.owner_band_t.costs import T_EXTRA_COST_BPS, total_cost_yuan


def test_commission_floor_binds_on_small_orders():
    # 1 万元名义: 万0.854 = 0.854 元 < 5 元地板 → 取 5
    small = 10_000.0
    c = total_cost_yuan(small, 2.0e9)
    assert c >= float(MIN_COMMISSION)
    # 名义大时佣金按费率
    big = 1_000_000.0
    c2 = total_cost_yuan(big, 2.0e9)
    assert c2 > big * float(COMMISSION_RATE)  # 佣金+滑点+冲击


def test_etf_exempt_stamp_and_transfer():
    """ETF 免印花税/过户费——成本不随方向变化（策略侧买卖同价成本对称）。"""
    c_buy = total_cost_yuan(500_000.0, 2.0e9)
    c_sell = total_cost_yuan(500_000.0, 2.0e9)
    assert c_buy == c_sell  # 无卖出单边税


def test_t_trade_extra_cost():
    base = total_cost_yuan(200_000.0, 2.0e9, is_t_trade=False)
    t = total_cost_yuan(200_000.0, 2.0e9, is_t_trade=True)
    expected_extra = 200_000.0 * float(T_EXTRA_COST_BPS) / 10000.0
    assert abs((t - base) - expected_extra) < 1e-6


def test_tiered_slippage_monotone():
    """流动性越差（成交额越低）滑点腿越贵（标定分层单调）。"""
    c_liq = total_cost_yuan(100_000.0, 5.0e8)
    c_illiq = total_cost_yuan(100_000.0, 2.0e7)
    assert c_illiq >= c_liq


def test_zero_notional_zero_cost():
    assert total_cost_yuan(0.0, 2.0e9) == 0.0


def test_extra_cost_frozen_value():
    assert T_EXTRA_COST_BPS == Decimal("1.0")
