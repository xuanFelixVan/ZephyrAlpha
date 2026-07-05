# [A_test] module_id: SRC-TST-1208 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §test
# [MODULE] zephyr.l06_trade_execution
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l06_trade_execution.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

l06 = pytest.importorskip("zephyr.ex_core", reason="ex_core not importable")

from zephyr.ex_core.execution_engine import (
    AlgoType,
    ExecutionConfig,
    ExecutionEngine,
    ExecutionEngineRunRecord,
)
from zephyr.ex_core.order_manager import OrderAction, OrderManager

from zephyr.ex_core.adapters.broker_interface import BrokerInterface
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.risk.risk_validator_protocol import (
    ViolationDetail,
)


def _make_order(
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=Decimal("100"),
    order_type=OrderType.MARKET,
    limit_price=None,
    order_id=None,
) -> Order:
    return Order(
        order_id=order_id or "ord-001",
        symbol=symbol,
        strategy_id="strat-1",
        side=side,
        order_type=order_type,
        quantity=quantity,
        limit_price=limit_price,
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        broker_order_id=None,
        idempotency_key="ik-001",
    )


class _PermissiveRiskValidator:
    def validate_order(self, symbol, target_weight, current_holdings, limits):
        return []

    def validate_portfolio(self, holdings, market_values, total_nav, limits):
        return []


class _BlockingRiskValidator:
    def validate_order(self, symbol, target_weight, current_holdings, limits):
        return [
            ViolationDetail(
                constraint="position_limit",
                description="exceeds limit",
                limit_value=Decimal("0.1"),
                actual_value=Decimal("0.2"),
                severity="HALT",
            )
        ]

    def validate_portfolio(self, holdings, market_values, total_nav, limits):
        return []


class TestBrokerInterface:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            BrokerInterface()

    def test_register_fill_callback_noop(self):
        class _ConcreteBroker(BrokerInterface):
            @property
            def broker_id(self):
                return "test"

            def connect(self):
                return True

            def disconnect(self):
                return None

            def submit_order(self, order):
                return "bo-1"

            def cancel_order(self, broker_order_id):
                return True

            def query_order(self, broker_order_id):
                return None

            def get_positions(self):
                from zephyr.trading.trading_contracts.execution.position import PositionSnapshot

                return PositionSnapshot(
                    as_of_timestamp=datetime.now(UTC),
                    portfolio_id="test",
                    idempotency_key="ik",
                )

        b = _ConcreteBroker()
        b.register_fill_callback(lambda f: None)

    def test_broker_id_property(self):
        class _ConcreteBroker(BrokerInterface):
            @property
            def broker_id(self):
                return "my_broker"

            def connect(self):
                return True

            def disconnect(self):
                return None

            def submit_order(self, order):
                return "bo-1"

            def cancel_order(self, broker_order_id):
                return True

            def query_order(self, broker_order_id):
                return None

            def get_positions(self):
                from zephyr.trading.trading_contracts.execution.position import PositionSnapshot

                return PositionSnapshot(
                    as_of_timestamp=datetime.now(UTC),
                    portfolio_id="test",
                    idempotency_key="ik",
                )

        b = _ConcreteBroker()
        assert b.broker_id == "my_broker"


class TestOrderManager:
    def test_create_order(self):
        om = OrderManager()
        order = om.create_order(
            symbol="AAPL",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
        )
        assert order.symbol == "AAPL"
        assert order.status == OrderStatus.PENDING
        assert om.order_count == 1

    def test_get_order(self):
        om = OrderManager()
        order = om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        retrieved = om.get_order(order.order_id)
        assert retrieved is order

    def test_get_order_nonexistent(self):
        om = OrderManager()
        assert om.get_order("nonexistent") is None

    def test_cancel_order(self):
        om = OrderManager()
        order = om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        result = om.cancel_order(order.order_id)
        assert result is True
        assert order.status == OrderStatus.CANCELLED

    def test_cancel_nonexistent_order(self):
        om = OrderManager()
        assert om.cancel_order("nonexistent") is False

    def test_cancel_filled_order_fails(self):
        om = OrderManager()
        order = om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        order.status = OrderStatus.FILLED
        assert om.cancel_order(order.order_id) is False

    def test_get_open_orders(self):
        om = OrderManager()
        om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        om.create_order("GOOG", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("50"))
        assert len(om.get_open_orders()) == 2

    def test_get_orders_by_status(self):
        om = OrderManager()
        om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        pending = om.get_orders_by_status(OrderStatus.PENDING)
        assert len(pending) == 1

    def test_register_broker(self):
        om = OrderManager()
        mock_broker = MagicMock(spec=BrokerInterface)
        mock_broker.register_fill_callback = MagicMock()
        om.register_broker("sim", mock_broker)
        mock_broker.register_fill_callback.assert_called_once()

    def test_submit_order_no_broker(self):
        om = OrderManager()
        order = om.create_order("AAPL", "s1", OrderSide.BUY, OrderType.MARKET, Decimal("100"))
        with pytest.raises(ValueError, match="Broker not found"):
            om.submit_order(order.order_id, "nonexistent")

    def test_submit_order_not_found(self):
        om = OrderManager()
        with pytest.raises(ValueError, match="Order not found"):
            om.submit_order("nonexistent", "sim")

    def test_fill_count_zero(self):
        om = OrderManager()
        assert om.fill_count == 0

    def test_register_fill_callback(self):
        om = OrderManager()
        callback = MagicMock()
        om.register_fill_callback(callback)
        assert callback in om._fill_callbacks


class TestExecutionConfig:
    def test_defaults(self):
        c = ExecutionConfig()
        assert c.default_algo == AlgoType.TWAP
        assert c.twap_window_minutes == 30
        assert c.twap_slices == 10

    def test_custom(self):
        c = ExecutionConfig(default_algo=AlgoType.MARKET)
        assert c.default_algo == AlgoType.MARKET


class TestAlgoType:
    def test_values(self):
        assert AlgoType.MARKET.value == "market"
        assert AlgoType.TWAP.value == "twap"
        assert AlgoType.VWAP.value == "vwap"
        assert AlgoType.ICEBERG.value == "iceberg"


class TestExecutionEngineRunRecord:
    def test_fill_rate_normal(self):
        r = ExecutionEngineRunRecord(
            report_id="r1",
            order_id="o1",
            symbol="AAPL",
            algo_type="twap",
            total_quantity=Decimal("100"),
            filled_quantity=Decimal("80"),
            avg_fill_price=Decimal("100"),
            target_price=Decimal("99"),
            slippage_bps=Decimal("10"),
            commission=Decimal("5"),
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            status="partial",
        )
        assert abs(r.fill_rate - 0.8) < 1e-9

    def test_fill_rate_zero_total(self):
        r = ExecutionEngineRunRecord(
            report_id="r1",
            order_id="o1",
            symbol="AAPL",
            algo_type="twap",
            total_quantity=Decimal("0"),
            filled_quantity=Decimal("0"),
            avg_fill_price=Decimal("100"),
            target_price=Decimal("99"),
            slippage_bps=Decimal("0"),
            commission=Decimal("0"),
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            status="filled",
        )
        assert r.fill_rate == 0.0


class TestExecutionEngine:
    def _make_engine(self, validator=None):
        om = OrderManager()
        mock_broker = MagicMock(spec=BrokerInterface)
        mock_broker.register_fill_callback = MagicMock()
        mock_broker.submit_order = MagicMock(return_value="bo-1")
        om.register_broker("simulation", mock_broker)
        v = validator or _PermissiveRiskValidator()
        return ExecutionEngine(order_manager=om, risk_validator=v), om

    def test_execute_order_market(self):
        engine, om = self._make_engine()
        order = _make_order()
        om._orders[order.order_id] = order
        result = engine.execute_order(order, algo=AlgoType.MARKET)
        assert result == "bo-1"

    def test_execute_order_twap(self):
        engine, om = self._make_engine()
        order = _make_order()
        om._orders[order.order_id] = order
        result = engine.execute_order(order, algo=AlgoType.TWAP)
        assert result == "bo-1"

    def test_execute_order_vwap(self):
        engine, om = self._make_engine()
        order = _make_order()
        om._orders[order.order_id] = order
        result = engine.execute_order(order, algo=AlgoType.VWAP)
        assert result == "bo-1"

    def test_execute_order_blocked_by_risk(self):
        engine, _ = self._make_engine(validator=_BlockingRiskValidator())
        order = _make_order()
        with pytest.raises(ValueError, match="rejected by risk"):
            engine.execute_order(order)

    def test_execute_batch(self):
        engine, om = self._make_engine()
        orders = [_make_order(order_id="o1"), _make_order(order_id="o2")]
        for o in orders:
            om._orders[o.order_id] = o
        results = engine.execute_batch(orders)
        assert len(results) == 2

    def test_execute_batch_partial_failure(self):
        engine, _ = self._make_engine(validator=_BlockingRiskValidator())
        orders = [_make_order(order_id="o1")]
        results = engine.execute_batch(orders)
        assert len(results) == 0

    def test_select_broker_default(self):
        engine, _ = self._make_engine()
        engine.update_broker_score("simulation", 0.9)
        order = _make_order()
        selected = engine.select_broker(order)
        assert selected == "simulation"

    def test_update_broker_score(self):
        engine, _ = self._make_engine()
        engine.update_broker_score("sim_a", 0.8)
        engine.update_broker_score("sim_a", 0.6)
        assert engine._broker_scores["sim_a"] > 0

    def test_get_engine_run_record_none(self):
        engine, _ = self._make_engine()
        assert engine.get_engine_run_record("nonexistent") is None


class TestOrderAction:
    def test_values(self):
        assert OrderAction.SUBMIT.value == "submit"
        assert OrderAction.CANCEL.value == "cancel"
        assert OrderAction.MODIFY.value == "modify"


class TestSimulationBroker:
    @pytest.fixture(autouse=True)
    def _import_broker(self):
        self.SimulationBroker = pytest.importorskip(
            "zephyr.ex_core.adapters.simulation_broker",
            reason="simulation_broker not importable",
        ).SimulationBroker

    def test_connect(self):
        b = self.SimulationBroker()
        assert b.connect() is True

    def test_disconnect(self):
        b = self.SimulationBroker()
        b.connect()
        b.disconnect()

    def test_submit_order_not_connected(self):
        b = self.SimulationBroker()
        order = _make_order()
        with pytest.raises(ConnectionError):
            b.submit_order(order)

    def test_submit_order_connected(self):
        b = self.SimulationBroker()
        b.connect()
        order = _make_order(limit_price=Decimal("100"))
        broker_id = b.submit_order(order)
        assert broker_id.startswith("sim-")

    def test_cancel_order(self):
        b = self.SimulationBroker()
        b.connect()
        order = _make_order(limit_price=Decimal("100"))
        broker_id = b.submit_order(order)
        assert b.cancel_order(broker_id) is True

    def test_cancel_nonexistent(self):
        b = self.SimulationBroker()
        assert b.cancel_order("nonexistent") is False

    def test_query_order(self):
        b = self.SimulationBroker()
        b.connect()
        order = _make_order(limit_price=Decimal("100"))
        broker_id = b.submit_order(order)
        result = b.query_order(broker_id)
        assert result is not None

    def test_query_nonexistent(self):
        b = self.SimulationBroker()
        assert b.query_order("nonexistent") is None

    def test_get_positions(self):
        b = self.SimulationBroker()
        b.connect()
        order = _make_order(limit_price=Decimal("100"))
        b.submit_order(order)
        pos = b.get_positions()
        assert pos.portfolio_id == "simulation"

    def test_register_fill_callback(self):
        b = self.SimulationBroker()
        callback = MagicMock()
        b.register_fill_callback(callback)
        assert callback in b._fill_callbacks

    def test_broker_id_prop(self):
        b = self.SimulationBroker()
        assert b.broker_id_prop == "simulation"

    def test_supports_realtime_fills(self):
        b = self.SimulationBroker()
        assert b.supports_realtime_fills is True

    def test_get_fills(self):
        b = self.SimulationBroker()
        b.connect()
        order = _make_order(limit_price=Decimal("100"))
        b.submit_order(order)
        fills = b.get_fills()
        assert len(fills) == 1
