# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l06_trade_execution.test_order_manager_and_simulation_broker
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l06_trade_execution/order_manager.py + adapters/simulation_broker.py
========================================================================================

覆盖矩阵：
  OrderManager:
    - create_order × 1
    - submit_order 无 broker 报错 × 1
    - cancel_order × 1
    - get_order × 1
    - get_open_orders × 1
    - order_count / fill_count × 1
  SimulationBroker:
    - connect / disconnect × 1
    - submit_order 未连接报错 × 1
    - broker_id × 1
    - get_positions × 1
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from zephyr.l06_trade_execution.adapters.simulation_broker import SimulationBroker
from zephyr.l06_trade_execution.broker_interface import BrokerInterface
from zephyr.l06_trade_execution.order_manager import OrderManager
from zephyr.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType


def _make_order(symbol="600519", side=OrderSide.BUY, qty=Decimal("100")) -> Order:
    return Order(
        order_id="test-o1",
        symbol=symbol,
        strategy_id="s1",
        side=side,
        order_type=OrderType.LIMIT,
        quantity=qty,
        limit_price=Decimal("100"),
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        broker_order_id=None,
        idempotency_key="test-idem-1",
    )


class TestOrderManager:
    def test_create_order(self):
        om = OrderManager()
        order = om.create_order(
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        assert om.order_count == 1
        assert order.symbol == "600519"
        assert order.status == OrderStatus.PENDING

    def test_submit_order_no_broker_raises(self):
        om = OrderManager()
        order = om.create_order(
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        with pytest.raises(ValueError, match="Broker not found"):
            om.submit_order(order.order_id, broker_id="simulation")

    def test_cancel_order(self):
        om = OrderManager()
        order = om.create_order(
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        assert om.cancel_order(order.order_id) is True
        found = om.get_order(order.order_id)
        assert found.status == OrderStatus.CANCELLED

    def test_get_open_orders(self):
        om = OrderManager()
        om.create_order(
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        assert len(om.get_open_orders()) == 1

    def test_counts(self):
        om = OrderManager()
        om.create_order(
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("100"),
        )
        assert om.order_count == 1
        assert om.fill_count == 0


class TestSimulationBroker:
    def test_connect_disconnect(self):
        broker = SimulationBroker()
        assert broker.connect() is True
        broker.disconnect()

    def test_submit_not_connected_raises(self):
        broker = SimulationBroker()
        order = _make_order()
        with pytest.raises(ConnectionError, match="not connected"):
            broker.submit_order(order)

    def test_broker_id(self):
        broker = SimulationBroker()
        assert broker.broker_id == "simulation"

    def test_get_positions(self):
        broker = SimulationBroker()
        broker.connect()
        pos = broker.get_positions()
        assert pos.portfolio_id == "simulation"
        broker.disconnect()

    def test_is_broker_interface(self):
        broker = SimulationBroker()
        assert isinstance(broker, BrokerInterface)
