# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l06_trade_execution.test_execution_engine_deep
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l06_trade_execution/execution_engine.py — 深度测试
=============================================================================================================

覆盖矩阵：
  ExecutionEngine:
    - execute_order MARKET 路径 × 1
    - execute_order VWAP 路径 × 1
    - execute_order 风控拒绝（非 kill_switch）× 1
    - execute_batch 部分失败 × 1
    - select_broker 评分排序 × 1
    - update_broker_score × 1
    - get_engine_run_record × 1
    - ExecutionConfig 默认值 × 1
    - ExecutionEngineRunRecord fill_rate × 2
"""
from __future__ import annotations


from decimal import Decimal

import pytest
from zephyr.l06_trade_execution.adapters.simulation_broker import SimulationBroker
from zephyr.l06_trade_execution.execution_engine import (
    AlgoType,
    ExecutionConfig,
    ExecutionEngine,
    ExecutionEngineRunRecord,
)
from zephyr.l06_trade_execution.order_manager import OrderManager
from zephyr.trading_contracts.execution.order import Order, OrderSide, OrderType


def _make_engine(kill_switch: bool = False) -> tuple[ExecutionEngine, OrderManager]:
    from zephyr.l04_risk_management.implementations.default_risk_validator import DefaultRiskValidator
    broker = SimulationBroker()
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    rv = DefaultRiskValidator(kill_switch_active=kill_switch)
    return ExecutionEngine(order_manager=om, risk_validator=rv), om


def _make_order(om: OrderManager, **kwargs) -> Order:
    defaults = dict(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    defaults.update(kwargs)
    return om.create_order(**defaults)


class TestExecutionEngineOrderExecution:
    """订单执行路径测试"""

    def test_execute_market_order(self):
        engine, om = _make_engine()
        order = _make_order(om, quantity=Decimal("100"))
        broker_oid = engine.execute_order(order, AlgoType.MARKET, "simulation")
        assert broker_oid
        record = engine.get_engine_run_record(order.order_id)
        assert record is None  # MARKET 不创建 record

    def test_execute_vwap_order(self):
        engine, om = _make_engine()
        order = _make_order(om, symbol="000858", side=OrderSide.SELL, quantity=Decimal("200"), limit_price=Decimal("50"))
        broker_oid = engine.execute_order(order, AlgoType.VWAP, "simulation")
        assert broker_oid
        info = engine._algo_orders.get(order.order_id)
        assert info is not None
        assert info["algo"] == "vwap"

    def test_execute_order_risk_rejection(self):
        engine, om = _make_engine()
        # 构造一个会触发风控拒绝的订单（超大数量）
        order = _make_order(om, quantity=Decimal("99999999"))
        with pytest.raises(ValueError, match="risk validator"):
            engine.execute_order(order, AlgoType.MARKET, "simulation")


class TestExecutionEngineBatch:
    """批量执行测试"""

    def test_execute_batch_partial_failure(self):
        engine, om = _make_engine()
        order1 = _make_order(om, quantity=Decimal("100"))
        order2 = _make_order(om, symbol="000858", quantity=Decimal("99999999"))  # 会触发风控拒绝
        broker_oids = engine.execute_batch([order1, order2], AlgoType.MARKET)
        # order1 成功，order2 失败 → 返回列表长度为 1
        assert len(broker_oids) == 1


class TestExecutionEngineBrokerRouting:
    """经纪商路由测试"""

    def test_select_broker_returns_best(self):
        engine, om = _make_engine()
        # 初始时返回默认 simulation
        broker_id = engine.select_broker(None)  # type: ignore[arg-type]
        assert broker_id == "simulation"

    def test_update_broker_score(self):
        engine, om = _make_engine()
        engine.update_broker_score("broker_a", 0.9)
        engine.update_broker_score("broker_a", 0.8)
        # 评分 = 1.0 * 0.9 + 0.9 * 0.1 = 0.99, then 0.99 * 0.9 + 0.8 * 0.1 = 0.971
        score = engine._broker_scores["broker_a"]
        assert score == pytest.approx(0.971)

        best = engine.select_broker(None)  # type: ignore[arg-type]
        assert best == "broker_a"


class TestExecutionEngineRunRecord:
    """执行记录测试"""

    def test_fill_rate_full(self):
        record = ExecutionEngineRunRecord(
            report_id="r1",
            order_id="o1",
            symbol="600519",
            algo_type="twap",
            total_quantity=Decimal("1000"),
            filled_quantity=Decimal("1000"),
            avg_fill_price=Decimal("100"),
            target_price=Decimal("100"),
            slippage_bps=Decimal("1"),
            commission=Decimal("30"),
            start_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            end_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            status="filled",
        )
        assert record.fill_rate == pytest.approx(1.0)

    def test_fill_rate_partial(self):
        record = ExecutionEngineRunRecord(
            report_id="r2",
            order_id="o2",
            symbol="600519",
            algo_type="twap",
            total_quantity=Decimal("1000"),
            filled_quantity=Decimal("500"),
            avg_fill_price=Decimal("100"),
            target_price=Decimal("100"),
            slippage_bps=Decimal("1"),
            commission=Decimal("15"),
            start_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            end_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            status="partial",
        )
        assert record.fill_rate == pytest.approx(0.5)

    def test_fill_rate_zero(self):
        record = ExecutionEngineRunRecord(
            report_id="r3",
            order_id="o3",
            symbol="600519",
            algo_type="twap",
            total_quantity=Decimal("0"),
            filled_quantity=Decimal("0"),
            avg_fill_price=Decimal("0"),
            target_price=Decimal("100"),
            slippage_bps=Decimal("0"),
            commission=Decimal("0"),
            start_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            end_time=__import__("datetime").datetime.now(__import__("datetime").UTC),
            status="pending",
        )
        assert record.fill_rate == pytest.approx(0.0)


class TestExecutionConfig:
    """执行配置测试"""

    def test_default_values(self):
        config = ExecutionConfig()
        assert config.default_algo == AlgoType.TWAP
        assert config.twap_window_minutes == 30
        assert config.twap_slices == 10
        assert config.max_slippage_bps == Decimal("5")
        assert config.participation_rate == pytest.approx(0.10)
        assert config.min_order_qty == Decimal("100")
        assert config.round_lot == 100
