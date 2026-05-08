"""ExecutionEngine — 风控拒绝与 TWAP 主路径单元测试。"""
from __future__ import annotations


from decimal import Decimal

import pytest
from zephyr.l04_risk_management.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.l06_trade_execution.adapters.simulation_broker import SimulationBroker
from zephyr.l06_trade_execution.execution_engine import AlgoType, ExecutionEngine
from zephyr.l06_trade_execution.order_manager import OrderManager
from zephyr.shared.contracts.execution.order import OrderSide, OrderType


def _make_engine(*, kill_switch: bool = False) -> tuple[ExecutionEngine, OrderManager]:
    broker = SimulationBroker()
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    rv = DefaultRiskValidator(kill_switch_active=kill_switch)
    return ExecutionEngine(order_manager=om, risk_validator=rv), om


def test_execution_engine_rejects_when_kill_switch_active() -> None:
    engine, om = _make_engine(kill_switch=True)
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    with pytest.raises(ValueError, match="risk validator"):
        engine.execute_order(order, AlgoType.MARKET, "simulation")


def test_execution_engine_twap_submits_via_order_manager() -> None:
    engine, om = _make_engine(kill_switch=False)
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    broker_oid = engine.execute_order(order, AlgoType.TWAP, "simulation")
    assert broker_oid
    info = engine._algo_orders.get(order.order_id)
    assert info is not None
    assert info["algo"] == "twap"
