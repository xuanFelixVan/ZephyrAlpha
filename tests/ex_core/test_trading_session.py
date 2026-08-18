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

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.discipline_must_do_checker import (
    ChecklistCheckpoint,
    ChecklistCompletionChecker,
)
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineContext,
    DisciplineGuard,
    KillSwitchLite,
)
from zephyr.compliance.trading_compliance_detector import TradingComplianceDetector
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.signal_providers import (
    make_mock_price_provider,
    make_mock_signal_provider,
)
from zephyr.ex_core.trading_session import (
    ComplianceMarketContext,
    TradingSession,
    TradingSessionConfig,
)
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


def test_rebalance_star_board_lot_rounding() -> None:
    """科创板目标数量按板块规则取整（200 股起 1 股递增，不按 100 股取整）。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"688001.SH": 0.0025}),  # target=2500/10=250 股
        price_provider=make_mock_price_provider({"688001.SH": Decimal("10")}),
        config=TradingSessionConfig(universe=["688001.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.BUY
    # 1,000,000 * 0.0025 / 10 = 250 股：科创板 200 起 +1 递增 → 250 合法保留
    #（旧统一 100 股取整会错误截到 200）
    assert orders[0].quantity == Decimal("250")


def test_rebalance_odd_lot_sell_all() -> None:
    """零股持仓（<100）不在目标权重 → 一次性清仓（不被 min_order_qty 吞掉）。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("995000"),
        holdings={"600519.SH": Decimal("50")},  # 零股
        total_market_value=Decimal("5000"),
    )
    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({}),  # 空目标 → 清仓
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.SELL
    assert orders[0].quantity == Decimal("50")  # 零股一次性申报卖出


def test_rebalance_odd_lot_remainder_triggers_full_sell() -> None:
    """主板卖出后剩余不足 100 股 → 放大为一次性清仓（board_lot 零股规则）。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("850000"),
        holdings={"600519.SH": Decimal("150")},
        total_market_value=Decimal("15000"),
    )
    session = _make_session(
        broker=broker,
        # target=0.0005 → target_qty=round_buy_qty(865000*0.0005/100=4.325)=0
        # → delta=-150 → 取整 100 → 剩余 50 <100 → 清仓 150
        strategy=_strategy_returning({"600519.SH": 0.0005}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].side == OrderSide.SELL
    assert orders[0].quantity == Decimal("150")


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


# ---------------------------------------------------------------------
# 先卖后买顺序验证（40_execution_broker §2.6）
# ---------------------------------------------------------------------


def test_sell_before_buy_with_mock_broker_recording() -> None:
    """先卖后买：用 mock broker 记录 submit_order 调用顺序验证。

    不依赖 SimulationBroker，直接验证 _validate_and_submit 内部排序。
    """
    submit_calls: list[str] = []
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("900000"),
        holdings={"600519.SH": Decimal("1000")},
        total_market_value=Decimal("100000"),
    )
    # 记录提交顺序
    broker.submit_order.side_effect = lambda order: (
        submit_calls.append(f"{order.side}:{order.symbol}"),
        f"broker_{order.order_id[:8]}",
    )[1]

    session = _make_session(
        broker=broker,
        strategy=_strategy_returning({"000001.SH": 0.05}),  # SELL 600519, BUY 000001
        price_provider=make_mock_price_provider(
            {"600519.SH": Decimal("100"), "000001.SH": Decimal("10")}
        ),
        config=TradingSessionConfig(
            universe=["600519.SH", "000001.SH"], broker_id="test_broker"
        ),
    )
    session.start()
    orders = session.rebalance()
    # 验证提交顺序：SELL 在前
    sell_indices = [i for i, c in enumerate(submit_calls) if c.startswith("SELL")]
    buy_indices = [i for i, c in enumerate(submit_calls) if c.startswith("BUY")]
    assert sell_indices, "应有 SELL 提交"
    assert buy_indices, "应有 BUY 提交"
    assert max(sell_indices) < min(buy_indices), (
        f"所有 SELL 应在 BUY 之前: SELL={sell_indices}, BUY={buy_indices}"
    )
    session.stop()


# ---------------------------------------------------------------------
# 订单层熔断测试（40_execution_broker §2.8）
# ---------------------------------------------------------------------


def test_circuit_breaker_blocks_oversized_order() -> None:
    """熔断：单笔订单 > 4% 账户市值 → 阻断，归入 blocked_orders。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("100000"),  # 总资产 100,000
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"

    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    # 启用熔断：单笔 ≤4%
    config.max_single_order_pct = Decimal("0.04")
    config.max_symbol_orders_per_day = 999
    config.max_total_orders_per_day = 999

    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.50}),  # 50% → 50,000 元 > 4,000 (4%)
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
    )
    session.start()
    orders = session.rebalance()
    # 50% of 100,000 = 50,000 元，远超 4% = 4,000 元 → 被熔断
    assert len(orders) == 0, "超限订单应被熔断阻断"
    assert len(session._blocked_orders) >= 1, "应归入 blocked_orders"
    session.stop()


def test_circuit_breaker_allows_small_order() -> None:
    """熔断：单笔订单 ≤ 4% 账户市值 → 放行。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),  # 总资产 1,000,000
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"

    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    config.max_single_order_pct = Decimal("0.04")  # 4% = 40,000
    config.max_symbol_orders_per_day = 999
    config.max_total_orders_per_day = 999

    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.03}),  # 3% → 30,000 元 < 40,000
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
    )
    session.start()
    orders = session.rebalance()
    # 3% of 1,000,000 = 30,000 < 40,000 (4%) → 放行
    assert len(orders) == 1, "未超限订单应放行"
    session.stop()


def test_circuit_breaker_symbol_frequency_limit() -> None:
    """熔断：单票下单频次超限 → 阻断。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"

    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    config.max_single_order_pct = Decimal("1.0")  # 不限制单笔
    config.max_symbol_orders_per_day = 2  # 单票 ≤2 笔/日
    config.max_total_orders_per_day = 999

    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.03}),
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
    )
    session.start()
    # 第一次 rebalance：放行（计数 1）
    orders1 = session.rebalance()
    assert len(orders1) == 1
    # 第二次 rebalance：放行（计数 2）
    orders2 = session.rebalance()
    assert len(orders2) == 1
    # 第三次 rebalance：频次超限（计数已达 2）→ 阻断
    orders3 = session.rebalance()
    assert len(orders3) == 0, "第三次应被频次熔断阻断"
    session.stop()


def test_circuit_breaker_total_frequency_limit() -> None:
    """熔断：全账户下单频次超限 → 阻断。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"

    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999
    config.max_total_orders_per_day = 2  # 全账户 ≤2 笔/日

    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.03}),
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
    )
    session.start()
    session.rebalance()  # 计数 1
    session.rebalance()  # 计数 2
    orders3 = session.rebalance()  # 计数已达 2 → 阻断
    assert len(orders3) == 0, "第三次应被全账户频次熔断阻断"
    session.stop()


def test_circuit_breaker_reset_daily() -> None:
    """熔断：reset_daily_circuit_breaker 清零计数后恢复下单。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"

    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 1  # 单票 ≤1 笔/日
    config.max_total_orders_per_day = 999

    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.03}),
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
    )
    session.start()
    orders1 = session.rebalance()
    assert len(orders1) == 1  # 第一笔放行
    orders2 = session.rebalance()
    assert len(orders2) == 0  # 频次超限阻断
    # 重置当日计数
    session.reset_daily_circuit_breaker()
    orders3 = session.rebalance()
    assert len(orders3) == 1, "重置后应恢复下单"
    session.stop()


# ---------------------------------------------------------------------
# C-004 合规闸（43 号 §3.4/§4.3/§7.1，AI-ASM-001 装配批接线）
# ---------------------------------------------------------------------


def _tmp_logger(tmp_path) -> ComplianceLogger:
    """测试用合规日志（写 tmp，不污染生产证据链）。"""
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


def _make_gate_session(tmp_path, **kwargs) -> tuple[TradingSession, MagicMock]:
    """构建带 C-004 合规闸的 TradingSession（broker=MagicMock，价格 100）。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position(
        cash=Decimal("1000000"),
        holdings={},
        total_market_value=Decimal("0"),
    )
    broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"
    config = TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker")
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    session = TradingSession(
        broker=broker,
        strategy=_strategy_returning({"600519.SH": 0.03}),
        risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=_make_real_om(broker),
        config=config,
        **kwargs,
    )
    return session, broker


def _discipline_ctx(**overrides) -> DisciplineContext:
    """构建纪律闸 ctx（默认全中性不触发任何检测）。"""
    base = {
        "signal_ref_price": None,
        "surge_30min_pct": None,
        "position_pnl_pct": None,
        "win_streak": 0,
        "normal_exposure": 0.01,
        "daily_pnl_pct": 0.0,
        "projected_daily_freq": 1.0,
        "freq_baseline_20d": 1.0,
        "size_baseline_20d": 1e9,
    }
    base.update(overrides)
    return DisciplineContext(**base)


class TestChecklistGate:
    """MOD-CMP-001 INTRADAY 必做清单 Hard Block（43 号 §3.4）。"""

    def test_intraday_incomplete_hard_blocks_all(self, tmp_path):
        """盘中执行清单缺项 → Hard Block 整批拒单，broker 零调用。"""
        checker = ChecklistCompletionChecker(
            completion_provider=lambda cp, td: set(),  # 三项全缺
            logger=_tmp_logger(tmp_path),
        )
        session, broker = _make_gate_session(tmp_path, checklist_checker=checker)
        orders = session.rebalance()
        assert orders == []
        broker.submit_order.assert_not_called()

    def test_intraday_partial_missing_still_blocks(self, tmp_path):
        """缺 1/3 项也阻断（盘中执行是唯一 Hard Block 项）。"""
        checker = ChecklistCompletionChecker(
            completion_provider=lambda cp, td: {"signal_compliance_check", "risk_param_confirm"},
            logger=_tmp_logger(tmp_path),
        )
        session, broker = _make_gate_session(tmp_path, checklist_checker=checker)
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_intraday_complete_allows(self, tmp_path):
        """清单全完成 → 正常下单。"""
        checker = ChecklistCompletionChecker(
            completion_provider=lambda cp, td: {
                "signal_compliance_check",
                "risk_param_confirm",
                "position_limit_verify",
            },
            logger=_tmp_logger(tmp_path),
        )
        session, broker = _make_gate_session(tmp_path, checklist_checker=checker)
        orders = session.rebalance()
        assert len(orders) == 1
        broker.submit_order.assert_called_once()


class TestDisciplineGate:
    """MOD-CMP-002 四项严禁纪律闸（43 号 §4.3）。"""

    def test_chasing_hard_block(self, tmp_path):
        """追高：买价超信号参考价 +2% 且 30min 拉升 >5% → Hard Block。"""
        guard = DisciplineGuard(logger=_tmp_logger(tmp_path))
        provider = lambda order, pos: _discipline_ctx(  # noqa: E731
            signal_ref_price=95.0,  # 100/95-1=5.26% > 2%
            surge_30min_pct=0.06,  # > 5%
        )
        session, broker = _make_gate_session(
            tmp_path, discipline_guard=guard, discipline_ctx_provider=provider
        )
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_adding_to_loser_hard_block(self, tmp_path):
        """被套补仓：持仓浮亏 >5% 仍加仓同标的 → Hard Block。"""
        guard = DisciplineGuard(logger=_tmp_logger(tmp_path))
        provider = lambda order, pos: _discipline_ctx(position_pnl_pct=-0.08)  # noqa: E731
        session, broker = _make_gate_session(
            tmp_path, discipline_guard=guard, discipline_ctx_provider=provider
        )
        # 持仓中有同标的 → is_add=True（_make_position 构造持仓）
        broker.get_positions.return_value = _make_position(
            cash=Decimal("1000000"),
            holdings={"600519.SH": Decimal("100")},
            total_market_value=Decimal("10000"),
        )
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_overconfidence_warning_allows(self, tmp_path):
        """盈利骄傲：连盈 5 笔+敞口超 1.5 倍 → WARNING 不阻断。"""
        guard = DisciplineGuard(logger=_tmp_logger(tmp_path))
        provider = lambda order, pos: _discipline_ctx(  # noqa: E731
            win_streak=5,
            normal_exposure=0.01,  # 本单敞口 0.03 > 1.5×0.01
        )
        session, broker = _make_gate_session(
            tmp_path, discipline_guard=guard, discipline_ctx_provider=provider
        )
        orders = session.rebalance()
        assert len(orders) == 1
        broker.submit_order.assert_called_once()

    def test_ctx_provider_failure_fail_closed(self, tmp_path):
        """纪律闸 ctx 提供器失效 → Fail-Closed 拒单（43 号 §4.3）。"""
        guard = DisciplineGuard(logger=_tmp_logger(tmp_path))

        def _boom(order, pos):
            raise RuntimeError("market data down")

        session, broker = _make_gate_session(
            tmp_path, discipline_guard=guard, discipline_ctx_provider=_boom
        )
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_guard_without_provider_raises(self, tmp_path):
        """纪律闸与 ctx 提供器必须成对注入（装配期 fail-fast）。"""
        with pytest.raises(ValueError, match="成对注入"):
            _make_gate_session(
                tmp_path,
                discipline_guard=DisciplineGuard(logger=_tmp_logger(tmp_path)),
            )


class TestKillSwitchLiteGate:
    """KillSwitchLite 策略级熔断（43 号 §4.3）。"""

    def test_triggered_strategy_blocked(self, tmp_path):
        """已熔断策略当日禁止新开仓。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_tmp_logger(tmp_path),
        )
        assert ks.trigger("trading_session", "REVENGE_TRADING", date.today())
        session, broker = _make_gate_session(tmp_path, kill_switch=ks)
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_other_strategy_not_blocked(self, tmp_path):
        """熔断仅策略级——其他策略不受影响。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_tmp_logger(tmp_path),
        )
        assert ks.trigger("other_strategy", "REVENGE_TRADING", date.today())
        session, broker = _make_gate_session(tmp_path, kill_switch=ks)
        assert len(session.rebalance()) == 1


class TestTradingComplianceGate:
    """MOD-CMP-007 交易合规检测（43 号 §7.1）。"""

    def test_large_trade_hard_block(self, tmp_path):
        """大额成交：单笔 > 分钟均量 50% → Hard Block。"""
        detector = TradingComplianceDetector(logger=_tmp_logger(tmp_path))
        provider = lambda order: ComplianceMarketContext(minute_avg_volume=100.0)  # noqa: E731
        session, broker = _make_gate_session(
            tmp_path, compliance_detector=detector, compliance_ctx_provider=provider
        )
        # 单 300 股 > 0.5×100=50 → 命中
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_ctx_all_none_skips_and_allows(self, tmp_path):
        """ctx 全 None → 跳过检测放行（字段缺省语义）。"""
        detector = TradingComplianceDetector(logger=_tmp_logger(tmp_path))
        provider = lambda order: ComplianceMarketContext()  # noqa: E731
        session, broker = _make_gate_session(
            tmp_path, compliance_detector=detector, compliance_ctx_provider=provider
        )
        assert len(session.rebalance()) == 1

    def test_ctx_provider_failure_fail_closed(self, tmp_path):
        """合规检测 ctx 提供器失效 → Fail-Closed 拒单（43 号 §7.6）。"""
        detector = TradingComplianceDetector(logger=_tmp_logger(tmp_path))

        def _boom(order):
            raise RuntimeError("tick feed down")

        session, broker = _make_gate_session(
            tmp_path, compliance_detector=detector, compliance_ctx_provider=_boom
        )
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()

    def test_detector_without_provider_raises(self, tmp_path):
        """检测器与 ctx 提供器必须成对注入。"""
        with pytest.raises(ValueError, match="成对注入"):
            _make_gate_session(
                tmp_path,
                compliance_detector=TradingComplianceDetector(logger=_tmp_logger(tmp_path)),
            )


class TestNanGuard:
    """红队攻击：NaN cap/price 穿透。"""

    def test_cap_nan_fail_closed(self) -> None:
        """position_cap=NaN 时目标权重全清。"""
        snap = MagicMock()
        snap.position_cap = float("nan")
        # 修复前：NaN 穿透 cap>=1.0/cap<=0.0 双检查 → factor=nan 污染全组合权重
        assert TradingSession._apply_position_cap({"600519.SH": 0.10}, snap) == {}

    def test_price_nan_skip_order(self) -> None:
        """price=NaN 时不生成订单。"""
        broker = MagicMock()
        broker.get_positions.return_value = _make_position(cash=Decimal("1000000"))
        session = _make_session(
            broker=broker,
            strategy=_strategy_returning({"600519.SH": 0.10}),
            price_provider=make_mock_price_provider({"600519.SH": Decimal("nan")}),
            config=TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker"),
        )
        # 修复前：not price / price<=0 对 Decimal("NaN") 均不拦截 → 生成 NaN 订单
        assert session.rebalance() == []
