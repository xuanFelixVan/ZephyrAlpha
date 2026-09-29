# [A_test] module_id: MOD-L06-001-SAGAO-test-wiring | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_trading_session_saga_wiring
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""F53 TradingSession × SagaSessionOrchestrator 接线测试（mock/tmp_path 隔离）。

覆盖（F53 处方：Saga=TradingSession 编排层封装，非第二提交通道）：
  - 注入即生效：rebalance 提交面成交的单全部进 Saga 跟踪（下单相位）
  - 未注入零变化：既有直连路径行为不变
  - 事件触发懒扫接 rebalance：到期在途单被补偿撤单（同一 OM 通道）
  - 单写者不冲突：track_order 每单恰一次；成交链入账与编排器观察互不干扰
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.saga_session_orchestrator import (
    CompensationOutcome,
    SagaPhase,
    SagaSessionOrchestrator,
)
from zephyr.ex_core.signal_providers import make_mock_price_provider, make_mock_signal_provider
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot

# ---------------------------------------------------------------------
# 桩件与辅助
# ---------------------------------------------------------------------


class _FakeClock:
    def __init__(self) -> None:
        self.now = datetime(2026, 9, 29, 10, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now = self.now + timedelta(seconds=seconds)


def _make_position(cash: Decimal = Decimal("1000000")) -> PositionSnapshot:
    return PositionSnapshot(
        as_of_timestamp=datetime.now(UTC),
        idempotency_key="test-snapshot-saga",
        portfolio_id="test",
        cash=cash,
        holdings={},
        total_market_value=Decimal("0"),
        market_values={},
    )


def _make_fill(order_id: str, qty: Decimal = Decimal("40")) -> Fill:
    return Fill(
        fill_id=f"f-{order_id}-1",
        fill_price=Decimal("100"),
        fill_timestamp=datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key=f"fik-{order_id}-1",
        order_id=order_id,
        strategy_id="trading_session",
        symbol="600519.SH",
    )


class _TrackSpyOrchestrator(SagaSessionOrchestrator):
    """track_order 计数间谍（单写者/单次登记断言用）。"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.track_calls: list[str] = []

    def track_order(self, order, side=None):  # type: ignore[override]
        self.track_calls.append(order.order_id)
        return super().track_order(order, side)


#: "不注入编排器" 哨兵（区别于 None=自动装配）
_NO_ORCH = object()


def _make_session(saga_orchestrator=None, *, clock: _FakeClock | None = None):
    """mock broker + 真 OM + SagaSessionOrchestrator 的测试会话。

    saga_orchestrator=哨兵 `_NO_ORCH` 表示"不注入"（既有直连路径基线）。
    """
    broker = MagicMock()
    broker.get_positions.return_value = _make_position()
    om = OrderManager()
    om.register_broker("test_broker", broker)
    if saga_orchestrator is _NO_ORCH:
        orch = None
    else:
        kwargs = {"order_timeout_seconds": 30.0}
        if clock is not None:
            kwargs["clock"] = clock
        orch = saga_orchestrator if saga_orchestrator is not None else SagaSessionOrchestrator(om, **kwargs)
    config = TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker")
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = {"600519.SH": 0.10}
    risk_validator = MagicMock()
    risk_validator.validate_order.return_value = []
    session = TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=om,
        config=config,
        saga_orchestrator=orch,
    )
    return session, om, broker


# ---------------------------------------------------------------------
# 注入即生效 / 未注入零变化
# ---------------------------------------------------------------------


def test_injected_orchestrator_tracks_submitted_orders() -> None:
    """注入即生效：rebalance 提交面成交的单全部进 Saga 跟踪（PLACED 相位）。"""
    session, om, _ = _make_session()
    orch = session.saga_orchestrator
    assert orch is not None
    orders = session.rebalance()
    assert len(orders) == 1
    assert orch.tracked_count == 1
    life = orch.get_lifecycle(orders[0].order_id)
    assert life is not None
    assert life.phase is SagaPhase.PLACED
    assert life.symbol == "600519.SH"
    assert orders[0].status is OrderStatus.SUBMITTED  # 提交面语义不变


def test_not_injected_keeps_legacy_behavior() -> None:
    """未注入零变化：不注入编排器，直连路径照常提交。"""
    session, om, _ = _make_session(_NO_ORCH)
    assert session.saga_orchestrator is None
    orders = session.rebalance()
    assert len(orders) == 1
    assert orders[0].status is OrderStatus.SUBMITTED


# ---------------------------------------------------------------------
# 事件触发懒扫接 rebalance（Saga 补偿语义挂接提交面）
# ---------------------------------------------------------------------


def test_rebalance_triggers_timeout_sweep_compensation() -> None:
    """rebalance 到达=事件：到期在途单经懒扫补偿撤单（CANCELLED，OM 同一通道）。"""
    clock = _FakeClock()
    session, om, _ = _make_session(clock=clock)
    orch = session.saga_orchestrator
    assert orch is not None
    orders = session.rebalance()
    assert len(orders) == 1
    submitted = orders[0]
    clock.advance(31.0)  # 越过 30s 在途超时线
    records = orch.sweep()  # 与 rebalance 循环头同款事件触发点（显式触发等价验证）
    assert len(records) == 1
    assert records[0].outcome is CompensationOutcome.CANCELLED
    assert submitted.status is OrderStatus.CANCELLED
    # 补偿后的下一轮 rebalance 不受挂账污染（delta 相对持仓重新计算）
    orders2 = session.rebalance()
    assert all(o.order_id != submitted.order_id for o in orders2)


def test_rebalance_sweep_runs_inside_session_loop() -> None:
    """懒扫内嵌 rebalance 主循环：到期单在下一轮 rebalance 时被自动补偿。"""
    clock = _FakeClock()
    session, om, _ = _make_session(clock=clock)
    orch = session.saga_orchestrator
    assert orch is not None
    first = session.rebalance()
    assert len(first) == 1
    clock.advance(31.0)
    second = session.rebalance()  # 事件到达→循环头懒扫→首轮单超时被撤
    assert first[0].status is OrderStatus.CANCELLED
    # 首轮单已撤，delta 未回补（资金预占面按现持仓重算）——无重复下单冲突
    assert all(o.order_id != first[0].order_id for o in second)


# ---------------------------------------------------------------------
# 单写者不冲突
# ---------------------------------------------------------------------


def test_track_exactly_once_per_order() -> None:
    """每单恰一次 track_order（重复回调不重复登记；fill 到达零二次登记）。"""
    broker = MagicMock()
    broker.get_positions.return_value = _make_position()
    om = OrderManager()
    om.register_broker("test_broker", broker)
    spy = _TrackSpyOrchestrator(om, order_timeout_seconds=30.0)
    config = TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker")
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = {"600519.SH": 0.10}
    risk_validator = MagicMock()
    risk_validator.validate_order.return_value = []
    session = TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=om,
        config=config,
        saga_orchestrator=spy,
    )
    orders = session.rebalance()
    assert len(orders) == 1
    assert spy.track_calls == [orders[0].order_id]
    # fill 到达（OM 回调面）不触发二次登记
    om._on_fill(_make_fill(orders[0].order_id))
    assert spy.track_calls == [orders[0].order_id]
    assert spy.get_lifecycle(orders[0].order_id).phase is SagaPhase.PARTIAL


def test_fill_booked_by_om_chain_only() -> None:
    """单写者：fill 入账唯一写者=OM 成交回调链（broker 派发面）；
    session 记录面与编排器观察面均零账本写。"""
    session, om, _ = _make_session()
    orders = session.rebalance()
    order = orders[0]
    session._on_fill(_make_fill(order.order_id))  # session 记录面（零账本写）
    assert order.filled_quantity == Decimal("0")  # session 面不改账
    assert len(session._fills) == 1
    om._on_fill(_make_fill(order.order_id))  # OM 成交链入账（生产=broker 派发）
    assert order.filled_quantity == Decimal("40")  # 唯一写者=OM
    assert order.status is OrderStatus.PARTIAL
    life = session.saga_orchestrator.get_lifecycle(order.order_id)
    assert life is not None and life.phase is SagaPhase.PARTIAL  # 编排器只推进相位
    assert life.to_report()["compensations"] == []  # 未触发任何补偿写
