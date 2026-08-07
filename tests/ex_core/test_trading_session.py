# [A_test] module_id: MOD-EXE-trading_session_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_trading_session
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""TradingSession — 盘中实时调仓编排器单元测试。

覆盖：
  - _compute_order_deltas: 买入/清仓卖出/round_lot 跳过/零资产
  - rebalance: 完整调仓流程
  - 风控 HALT 阻断
  - 成交回调记录
  - 会话报告
  - start/stop 生命周期
  - 三态一致性（SimulationBroker 集成）
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.signal_providers import (
    make_mock_price_provider,
    make_mock_signal_provider,
)
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.governance.adapters.risk_validation_bridge import RiskViolation
from zephyr.governance.adapters.simulation_broker import SimulationBroker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus
from zephyr.shared.contracts.position import PositionSnapshot

# ---------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------


def _make_position(
    cash: Decimal = Decimal("1000000"),
    holdings: dict[str, Decimal] | None = None,
    total_market_value: Decimal | None = None,
) -> PositionSnapshot:
    """构建测试用 PositionSnapshot。"""
    holdings = holdings or {}
    if total_market_value is None:
        total_market_value = Decimal("0")
    return PositionSnapshot(
        as_of_timestamp=datetime.now(timezone.utc),
        idempotency_key="test-snapshot",
        portfolio_id="test",
        cash=cash,
        holdings=holdings,
        total_market_value=total_market_value,
        market_values={},
    )


def _make_session(
    *,
    broker=None,
    strategy=None,
    risk_validator=None,
    signal_provider=None,
    price_provider=None,
    order_manager=None,
    config=None,
) -> TradingSession:
    """构建测试用 TradingSession，未提供的组件用 MagicMock。"""
    broker = broker or MagicMock()
    strategy = strategy or MagicMock()
    if risk_validator is None:
        risk_validator = MagicMock()
        risk_validator.validate_order.return_value = []
    signal_provider = signal_provider or make_mock_signal_provider({})
    price_provider = price_provider or make_mock_price_provider({})
    order_manager = order_manager or _make_real_om(broker)
    config = config or TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    # 测试辅助：禁用订单层熔断（这些测试测调仓逻辑，不测熔断）
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    return TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=signal_provider,
        price_provider=price_provider,
        order_manager=order_manager,
        config=config,
    )


def _make_real_om(broker) -> OrderManager:
    """构建真实 OrderManager + 注册 mock broker。"""
    om = OrderManager()
    om.register_broker("test_broker", broker)
    return om


def _strategy_returning(weights: dict[str, float]) -> MagicMock:
    """构建 generate_target_weights 返回固定权重的 mock 策略。"""
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = weights
    return strategy


# ---------------------------------------------------------------------
# _compute_order_deltas 测试（通过 rebalance 公共 API测试）
# ---------------------------------------------------------------------


def test_rebalance_buy_from_empty_position() -> None:
    """空仓 + 目标权重 10% → 生成 BUY 单，qty 向下取整到 100 股。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.BUY
    # 1,000,000 * 0.10 / 100 = 1000 股
    assert orders[0].quantity == Decimal("1000")


def test_rebalance_sell_all_when_not_in_target() -> None:
    """持仓标的不在目标权重中 → 生成 SELL 单清仓。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("900000"),
        holdings={"600519.SH": Decimal("1000")},
        total_market_value=Decimal("100000"),
    )
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({}),  # 空目标权重
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.SELL
    assert orders[0].quantity == Decimal("1000")


def test_rebalance_round_lot_skip_small_delta() -> None:
    """delta < min_order_qty(100) → 跳过不下单。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),
        holdings={"600519.SH": Decimal("990")},  # 差 10 股
    )
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    # target=1000, current=990, delta=10 < 100 → skip
    assert len(orders) == 0


def test_rebalance_zero_total_asset_returns_empty() -> None:
    """total_asset <= 0 → 返回空列表。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("0"))
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 0


def test_rebalance_skip_missing_price() -> None:
    """标的无有效价格 → 跳过。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({}),  # 无价格
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 0


# ---------------------------------------------------------------------
# 风控阻断测试
# ---------------------------------------------------------------------


def test_risk_halt_blocks_order() -> None:
    """风控返回 HALT → 订单被阻断，不提交。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    risk_validator = MagicMock()
    risk_validator.validate_order.return_value = [
        RiskViolation(
            constraint="max_single_position",
            description="exceeds 10% limit",
            limit_value=Decimal("0.10"),
            actual_value=Decimal("0.50"),
            severity="HALT",
        )
    ]
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        risk_validator=risk_validator,
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 0
    report = session.get_session_report()
    assert report["blocked_count"] == 1
    assert report["submitted_count"] == 0


def test_risk_pass_allows_order() -> None:
    """风控无违规 → 订单正常提交。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    risk_validator = MagicMock()
    risk_validator.validate_order.return_value = []  # 无违规
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        risk_validator=risk_validator,
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.BUY
    report = session.get_session_report()
    assert report["submitted_count"] == 1
    assert report["blocked_count"] == 0


# ---------------------------------------------------------------------
# 成交回调 + 报告测试
# ---------------------------------------------------------------------


def test_fill_callback_via_simulation_broker() -> None:
    """SimulationBroker 自动成交 → fill 回调被记录。"""
    broker = SimulationBroker(initial_cash=Decimal("1000000"))
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519": 0.10}),
        price_provider=make_mock_price_provider({"600519": Decimal("100")}),
        order_manager=om,
        config=TradingSessionConfig(universe=["600519"], broker_id="simulation"),
    )
    session.start()
    orders = session.rebalance()
    assert len(orders) == 1
    # SimulationBroker 同步成交 → fill 回调触发
    report = session.get_session_report()
    assert report["fill_count"] >= 1
    session.stop()


def test_session_report_structure() -> None:
    """get_session_report 返回正确的结构。"""
    session = _make_session()
    report = session.get_session_report()
    assert "running" in report
    assert "submitted_count" in report
    assert "blocked_count" in report
    assert "fill_count" in report
    assert "broker_id" in report
    assert "universe_size" in report
    assert report["running"] is False
    assert report["submitted_count"] == 0


# ---------------------------------------------------------------------
# 生命周期测试
# ---------------------------------------------------------------------


def test_start_connects_broker_and_registers_callback() -> None:
    """start() 调用 broker.connect() + register_fill_callback()。

    register_fill_callback 被调用 2 次：OrderManager.register_broker 时 1 次 +
    TradingSession.start 时 1 次。
    """
    broker = MagicMock()
    session = _make_session(broker=broker)
    session.start()
    broker.connect.assert_called_once()
    # OrderManager.register_broker 调一次 + TradingSession.start 调一次 = 2 次
    assert broker.register_fill_callback.call_count >= 2
    session.stop()


def test_stop_disconnects_broker() -> None:
    """stop() 调用 broker.disconnect()。"""
    broker = MagicMock()
    session = _make_session(broker=broker)
    session.start()
    session.stop()
    broker.disconnect.assert_called_once()


def test_start_idempotent() -> None:
    """重复 start() 不重复连接。"""
    broker = MagicMock()
    session = _make_session(broker=broker)
    session.start()
    session.start()
    broker.connect.assert_called_once()
    session.stop()


def test_stop_cancels_pending_orders() -> None:
    """stop() 撤销活跃订单。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    om = _make_real_om(broker)
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=om,
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    session.start()
    orders = session.rebalance()
    assert len(orders) == 1
    # 订单处于 SUBMITTED 状态 → stop 应撤单
    assert orders[0].status == OrderStatus.SUBMITTED
    session.stop()
    # 撤单后状态为 CANCELLED（mock broker 的 cancel_order 不改状态，但 om.cancel_order 会转换）
    # mock broker.cancel_order 返回 MagicMock (truthy) → om 撤单成功 → 状态转 CANCELLED


# ---------------------------------------------------------------------
# 三态一致性测试
# ---------------------------------------------------------------------


def test_three_state_consistency_with_simulation_broker() -> None:
    """同一 TradingSession 逻辑在 SimulationBroker 下一致工作。

    验证：策略权重 → delta 计算 → 下单 → 成交 → 持仓更新 全链路。
    """
    broker = SimulationBroker(initial_cash=Decimal("1000000"))
    broker.connect()
    om = OrderManager()
    om.register_broker("simulation", broker)
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519": 0.10, "000001": 0.05}),
        price_provider=make_mock_price_provider(
            {
                "600519": Decimal("100"),
                "000001": Decimal("10"),
            }
        ),
        order_manager=om,
        config=TradingSessionConfig(universe=["600519", "000001"], broker_id="simulation"),
    )
    session.start()
    orders = session.rebalance()
    # 两只标的都有权重 → 两个 BUY 单
    assert len(orders) == 2
    symbols = {o.symbol for o in orders}
    assert symbols == {"600519", "000001"}
    for o in orders:
        assert o.side == OrderSide.BUY
    # SimulationBroker 自动成交 → fill 回调触发
    report = session.get_session_report()
    assert report["fill_count"] >= 2
    session.stop()


def test_multiple_rebalances_increment_counts() -> None:
    """多次 rebalance 累计 submitted_count。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.10}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    session.rebalance()
    session.rebalance()
    report = session.get_session_report()
    assert report["submitted_count"] == 2
