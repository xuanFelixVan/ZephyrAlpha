# -*- coding: utf-8 -*-
"""边界单测：T+1 约束（GAP-010）

测试 A 股 T+1 交割规则下的卖出限制。
"""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderType


def _broker_with_positions(positions: list) -> MiniQmtBroker:
    """构造持仓查询被 mock 的 broker（不触碰真实 xttrader）。"""
    broker = MiniQmtBroker()
    broker._account = SimpleNamespace(account_id="test")
    broker._xttrader = MagicMock()
    broker._xttrader.query_stock_positions.return_value = positions
    return broker


class TestTPlusOne:
    """T+1 边界测试。"""

    def test_same_day_buy_cannot_sell(self):
        """当日买入的股票当天不能卖出（can_sell_volume=0 必须拦截，不可当 falsy 跳过）。"""
        broker = _broker_with_positions(
            [SimpleNamespace(stock_code="600000.SH", can_sell_volume=0)]
        )
        with pytest.raises(MiniQmtBrokerError) as exc:
            broker._check_t_plus_1("600000.SH", 100)
        assert exc.value.error_code == -2

    def test_next_day_buy_can_sell(self):
        """次日可以卖出前一日买入的股票（can_sell_volume 充足时放行）。"""
        broker = _broker_with_positions(
            [SimpleNamespace(stock_code="600000.SH", can_sell_volume=1000)]
        )
        broker._check_t_plus_1("600000.SH", 100)  # 不抛异常即通过

    def test_t0_fund_available_for_buy(self):
        """卖出回笼的资金可立即用于买入（T+0 资金）——买入路径不做 T+1 股数校验。"""
        broker = _broker_with_positions([])
        broker._check_t_plus_1 = MagicMock()  # 若被调用即说明买入路径误加 T+1
        buy = Order(
            idempotency_key="t-t0-buy",
            order_id="ord-t0",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="test",
            symbol="600000.SH",
            limit_price=Decimal("10.00"),
        )
        broker._validate_a_share_constraints(buy, prev_close=Decimal("10.00"))
        broker._check_t_plus_1.assert_not_called()

        # 卖出路径必须做 T+1 校验
        sell = Order(
            idempotency_key="t-t0-sell",
            order_id="ord-t1",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.SELL,
            strategy_id="test",
            symbol="600000.SH",
            limit_price=Decimal("10.00"),
        )
        broker._validate_a_share_constraints(sell, prev_close=Decimal("10.00"))
        broker._check_t_plus_1.assert_called_once_with("600000.SH", 100)
