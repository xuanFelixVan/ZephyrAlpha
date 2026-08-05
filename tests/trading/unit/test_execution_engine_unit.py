# [A_test] module_id: MOD-GOV_execution_engine_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-637 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_execution_engine_unit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""ExecutionEngine — 风控拒绝与 TWAP 主路径单元测试。"""


from decimal import Decimal

import pytest

from zephyr.ex_core.execution_engine import AlgoType, ExecutionConfig, ExecutionEngine
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_sor.core.algo_trading_engine import AlgoTradingEngine
from zephyr.ex_sor.core.market_context_provider import StaticMarketContextProvider
from zephyr.governance.adapters.simulation_broker import SimulationBroker
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.trading.trading_contracts.execution.order import OrderSide, OrderType


def _make_engine(*, kill_switch: bool = False) -> tuple[ExecutionEngine, OrderManager]:
    broker = SimulationBroker()
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    rv = DefaultRiskValidator(kill_switch_active=kill_switch)
    return ExecutionEngine(order_manager=om, risk_validator=rv), om


def _make_algo_engine(
    *,
    last_price: Decimal | str = Decimal("100"),
    adv: Decimal | str = Decimal("100000"),
    twap_slices: int = 5,
) -> tuple[ExecutionEngine, OrderManager]:
    """构造注入了 G7 (AlgoTradingEngine + StaticMarketContextProvider) 的引擎。"""
    broker = SimulationBroker()
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    rv = DefaultRiskValidator(kill_switch_active=False)
    algo = AlgoTradingEngine()
    provider = StaticMarketContextProvider.from_values(
        symbol="600519",
        last_price=last_price,
        adv=adv,
        bid_price=Decimal("99.9"),
        ask_price=Decimal("100.1"),
    )
    engine = ExecutionEngine(
        order_manager=om,
        risk_validator=rv,
        config=ExecutionConfig(twap_slices=twap_slices, twap_window_minutes=30),
        algo_engine=algo,
        market_ctx_provider=provider,
    )
    return engine, om


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
    info = engine.algo_orders.get(order.order_id)
    assert info is not None
    assert info["algo"] == "twap"


# ── G7 智能订单路由接入测试 (MOD-XS-005 + MOD-XS-006, 2026-08-05) ──


def test_twap_sliced_generates_child_orders_with_conservation() -> None:
    """G7 接入: TWAP 注入 algo_engine 后生成 5 切片子订单, 数量守恒。"""
    engine, om = _make_algo_engine(twap_slices=5)
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1000"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    broker_oid = engine.execute_order(order, AlgoType.TWAP, "simulation")

    info = engine.algo_orders[order.order_id]
    assert info["sliced"] is True
    assert info["algo"] == "twap"
    assert info["slice_count"] == 5
    assert len(info["child_orders"]) == 5
    assert len(info["broker_order_ids"]) == 5
    # 守恒: 子订单量和 == 母订单量
    child_sum = sum(Decimal(c["quantity"]) for c in info["child_orders"])
    assert child_sum == order.quantity
    # 返回首个子订单 broker_id
    assert broker_oid == info["broker_order_ids"][0]
    # plan 审计字段存在
    assert "plan" in info
    assert info["plan"]["algo_type"] == "TWAP"


def test_vwap_sliced_uses_volume_profile_periods() -> None:
    """G7 接入: VWAP 按 §13.2 日内分布切片 (默认 4 时段), 数量守恒。"""
    engine, om = _make_algo_engine()
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1000"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    engine.execute_order(order, AlgoType.VWAP, "simulation")

    info = engine.algo_orders[order.order_id]
    assert info["sliced"] is True
    assert info["algo"] == "vwap"
    # 默认 volume_profile 4 时段 → 切片数 <= 4
    assert 1 <= info["slice_count"] <= 4
    child_sum = sum(Decimal(c["quantity"]) for c in info["child_orders"])
    assert child_sum == order.quantity


def test_iceberg_sliced_hides_display_quantity() -> None:
    """G7 接入: ICEBERG 每片 ≤ display_quantity (末片除外), 数量守恒。"""
    engine, om = _make_algo_engine()
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1000"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    engine.execute_order(order, AlgoType.ICEBERG, "simulation")

    info = engine.algo_orders[order.order_id]
    assert info["sliced"] is True
    assert info["algo"] == "iceberg"
    child_sum = sum(Decimal(c["quantity"]) for c in info["child_orders"])
    assert child_sum == order.quantity
    # ICEBERG 应产生多个切片 (>1, 1000 股 / display=100 → 多片)
    assert info["slice_count"] > 1


def test_sliced_order_too_large_raises_value_error() -> None:
    """G7 接入: 订单 > 15% ADV → OrderTooLargeError → ValueError (§13.1)。"""
    # adv=1000, order=1000 → 100% ADV, 远超 15% 上限
    engine, om = _make_algo_engine(adv=Decimal("1000"))
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1000"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    with pytest.raises(ValueError, match="algo plan generation failed"):
        engine.execute_order(order, AlgoType.TWAP, "simulation")
    # 失败时不写入 algo_orders (无脏数据)
    assert order.order_id not in engine.algo_orders


def test_backward_compat_no_injection_submits_whole_order() -> None:
    """向后兼容: 未注入 algo_engine → 整笔提交, sliced=False。"""
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
    info = engine.algo_orders[order.order_id]
    assert info["sliced"] is False
    assert info["broker_order_ids"] == [broker_oid]


def test_market_algo_never_slices() -> None:
    """MARKET 算法直提交, 不走切片路径 (即使注入 algo_engine)。"""
    engine, om = _make_algo_engine()
    order = om.create_order(
        symbol="600519",
        strategy_id="u1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("100"),
        broker_id="simulation",
    )
    broker_oid = engine.execute_order(order, AlgoType.MARKET, "simulation")
    assert broker_oid
    # MARKET 不记录 algo_orders (与原行为一致)
    assert order.order_id not in engine.algo_orders
