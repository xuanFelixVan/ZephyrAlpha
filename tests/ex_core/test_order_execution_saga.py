# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""OrderExecutionSaga 单元测试 — MOD-EX-057 / D-EX-CORE-57

覆盖: 六步完整流程 / 风控拒绝 / 信号失效 / 下单被拒 / 成交超时 / 持仓回滚 /
      补偿幂等 / 超时配置 / 审计记录 / 并发安全 / SagaResult frozen / 信号跳过
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.audit_journal.auditor import ExecutionAuditLogger
from zephyr.ex_core.order_execution_saga import (
    OrderExecutionSaga,
    SagaConfig,
    SagaResult,
    SagaState,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

# ──────────────────────────────────────────────────────────────────────────────
# Fake 组件
# ──────────────────────────────────────────────────────────────────────────────


class FakeRiskValidator:
    """可配置的风控校验器（通过/拒绝）。"""

    def __init__(self, reject: bool = False, severity: str = "HALT"):
        self._reject = reject
        self._severity = severity

    def validate_order(self, symbol, target_weight, current_holdings, limits):
        from zephyr.governance.adapters.risk_validation_bridge import RiskViolation

        if self._reject:
            return [
                RiskViolation(
                    constraint="test_constraint",
                    description="test rejection",
                    limit_value=Decimal("0.10"),
                    actual_value=Decimal("0.50"),
                    severity=self._severity,
                )
            ]
        return []

    def validate_portfolio(self, holdings, market_values, total_nav, limits):
        return []


class InstantFillBroker(BrokerInterface):
    """即时成交券商——submit_order 时同步触发 fill 回调。"""

    def __init__(self, fill_price: Decimal = Decimal("10.00"), commission: Decimal = Decimal("3")):
        self._fill_price = fill_price
        self._commission = commission
        self._callbacks: list[Any] = []
        self._orders: dict[str, Order] = {}
        self._connected = False

    @property
    def broker_id(self) -> str:
        return "fake"

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def submit_order(self, order: Order) -> str:
        broker_oid = f"bk-{order.order_id[:8]}"
        self._orders[broker_oid] = order
        # 同步触发 fill 回调
        fill = Fill(
            fill_id=f"fill-{order.order_id[:8]}",
            fill_price=self._fill_price,
            fill_timestamp=datetime.now(UTC),
            filled_quantity=order.quantity,
            idempotency_key=f"fill-{order.idempotency_key}",
            order_id=order.order_id,
            strategy_id=order.strategy_id,
            symbol=order.symbol,
            commission=self._commission,
        )
        for cb in self._callbacks:
            cb(fill)
        return broker_oid

    def cancel_order(self, broker_order_id: str) -> bool:
        if broker_order_id in self._orders:
            order = self._orders[broker_order_id]
            if order.status in (OrderStatus.SUBMITTED, OrderStatus.PENDING, OrderStatus.PARTIAL):
                order.status = OrderStatus.CANCELLED
                return True
        return False

    def query_order(self, broker_order_id: str) -> Order | None:
        return self._orders.get(broker_order_id)

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="fake",
            idempotency_key="fake",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        self._callbacks.append(callback)


class NeverFillBroker(BrokerInterface):
    """永不成交券商——用于超时测试。"""

    @property
    def broker_id(self) -> str:
        return "slow"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        return f"bk-{order.order_id[:8]}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="slow",
            idempotency_key="slow",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


class RejectBroker(BrokerInterface):
    """拒绝下单的券商——submit_order 抛异常。"""

    @property
    def broker_id(self) -> str:
        return "reject"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        raise RuntimeError("broker rejected order")

    def cancel_order(self, broker_order_id: str) -> bool:
        return False

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="reject",
            idempotency_key="reject",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────────────


def make_order(
    symbol: str = "600000.SH",
    side: OrderSide = OrderSide.BUY,
    qty: Decimal = Decimal("100"),
    price: Decimal = Decimal("10.00"),
) -> Order:
    """创建测试用 Order 值对象。"""
    return Order(
        order_id=f"test-{symbol}-{int(time.time() * 1000) % 100000}",
        symbol=symbol,
        strategy_id="test",
        side=side,
        order_type=OrderType.LIMIT,
        quantity=qty,
        limit_price=price,
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        idempotency_key=f"key-{symbol}-{int(time.time() * 1000) % 100000}",
    )


def make_saga(
    broker: BrokerInterface,
    risk_validator: Any = None,
    position_tracker: PositionTracker | None = None,
    audit_logger: ExecutionAuditLogger | None = None,
    config: SagaConfig | None = None,
    signal_confirmer: Any = None,
    rejection_executor: Any = None,
) -> OrderExecutionSaga:
    """构建测试用 Saga（默认全部通过）。"""
    om = OrderManager()
    om.register_broker("fake", broker)
    if hasattr(broker, "broker_id") and broker.broker_id != "fake":
        om.register_broker(broker.broker_id, broker)

    return OrderExecutionSaga(
        order_manager=om,
        risk_validator=risk_validator or FakeRiskValidator(),
        position_tracker=position_tracker or PositionTracker(initial_cash=Decimal("1000000")),
        audit_logger=audit_logger or ExecutionAuditLogger(),
        broker=broker,
        broker_id=broker.broker_id,
        config=config or SagaConfig(timeout_seconds=5.0, broker_id=broker.broker_id),
        signal_confirmer=signal_confirmer,
        rejection_executor=rejection_executor,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 完整成功流程
# ──────────────────────────────────────────────────────────────────────────────


class TestSuccessFlow:
    """六步全过, state=COMPLETED, fill 非 None。"""

    def test_complete_saga_buy(self):
        broker = InstantFillBroker(fill_price=Decimal("10.50"))
        saga = make_saga(broker)
        order = make_order(qty=Decimal("100"), price=Decimal("10.00"))

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPLETED
        assert result.fill is not None
        assert result.fill.fill_price == Decimal("10.50")
        assert result.fill.filled_quantity == Decimal("100")
        assert result.compensated is False
        assert result.error is None
        assert "risk_check" in result.steps_completed
        assert "order_submit" in result.steps_completed
        assert "fill_confirm" in result.steps_completed
        assert "position_update" in result.steps_completed

    def test_complete_saga_sell(self):
        broker = InstantFillBroker(fill_price=Decimal("11.00"))
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        # 先买入建仓
        buy_fill = Fill(
            fill_id="pre-fill",
            fill_price=Decimal("10.00"),
            fill_timestamp=datetime.now(UTC),
            filled_quantity=Decimal("200"),
            idempotency_key="pre",
            order_id="pre",
            strategy_id="test",
            symbol="600000.SH",
            commission=Decimal("3"),
        )
        tracker.apply_fill(buy_fill, OrderSide.BUY)

        saga = make_saga(broker, position_tracker=tracker)
        order = make_order(qty=Decimal("100"), price=Decimal("11.00"))

        result = saga.execute(order, OrderSide.SELL)

        assert result.state == SagaState.COMPLETED
        assert result.fill is not None
        assert result.side == "SELL"

    def test_position_updated_after_saga(self):
        """Saga 完成后 PositionTracker 持仓正确更新。"""
        broker = InstantFillBroker(fill_price=Decimal("10.00"), commission=Decimal("5"))
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        saga = make_saga(broker, position_tracker=tracker)
        order = make_order(qty=Decimal("100"), price=Decimal("10.00"))

        saga.execute(order, OrderSide.BUY)

        assert tracker.holdings["600000.SH"] == Decimal("100")
        assert tracker.avg_costs["600000.SH"] == Decimal("10.00")
        # cash = 1000000 - 100*10 - 5 = 998995
        assert tracker.cash == Decimal("998995")

    def test_duration_recorded(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.duration_ms >= 0  # 同步 broker 可能 <1ms
        assert result.duration_ms < 5000  # 应远小于5s
        assert result.started_at <= result.completed_at


# ──────────────────────────────────────────────────────────────────────────────
# 风控拒绝
# ──────────────────────────────────────────────────────────────────────────────


class TestRiskRejection:
    """step1 fail, state=RISK_REJECTED, 无下单。"""

    def test_risk_rejected_halts_saga(self):
        broker = InstantFillBroker()
        saga = make_saga(broker, risk_validator=FakeRiskValidator(reject=True))
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.RISK_REJECTED
        assert result.fill is None
        assert "risk_check" not in result.steps_completed
        assert result.compensated is False
        assert "risk" in (result.error or "").lower()

    def test_risk_warning_does_not_block(self):
        """severity=WARN 不阻断（仅 HALT 阻断）。"""
        broker = InstantFillBroker()
        saga = make_saga(broker, risk_validator=FakeRiskValidator(reject=True, severity="WARN"))
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPLETED
        assert result.fill is not None


# ──────────────────────────────────────────────────────────────────────────────
# 信号确认
# ──────────────────────────────────────────────────────────────────────────────


class TestSignalConfirm:
    """step2 信号确认。"""

    def test_signal_invalid_aborts(self):
        broker = InstantFillBroker()
        saga = make_saga(broker, signal_confirmer=lambda o: False)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.SIGNAL_INVALID
        assert result.fill is None
        assert "order_submit" not in result.steps_completed

    def test_signal_confirmed_continues(self):
        broker = InstantFillBroker()
        saga = make_saga(broker, signal_confirmer=lambda o: True)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPLETED
        assert "signal_confirm" in result.steps_completed

    def test_signal_confirmer_none_skips_step(self):
        """signal_confirmer=None 时跳过 step2。"""
        broker = InstantFillBroker()
        saga = make_saga(broker, signal_confirmer=None)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPLETED
        assert any("signal_confirm" in s for s in result.steps_completed)


# ──────────────────────────────────────────────────────────────────────────────
# 下单被拒
# ──────────────────────────────────────────────────────────────────────────────


class TestOrderRejection:
    """step3 fail, state=ORDER_REJECTED。"""

    def test_broker_rejects_order(self):
        broker = RejectBroker()
        saga = make_saga(broker)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        assert result.fill is None
        assert "submit" in (result.error or "").lower()


# ──────────────────────────────────────────────────────────────────────────────
# 成交超时
# ──────────────────────────────────────────────────────────────────────────────


class TestFillTimeout:
    """step4 timeout, state=TIMEOUT+COMPENSATED, 撤单。"""

    def test_timeout_cancels_order(self):
        broker = NeverFillBroker()
        saga = make_saga(
            broker,
            config=SagaConfig(timeout_seconds=0.2, broker_id="slow"),
        )
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPENSATED
        assert result.fill is None
        assert result.compensated is True
        assert "timeout" in (result.error or "").lower()

    def test_custom_timeout_respected(self):
        broker = NeverFillBroker()
        saga = make_saga(
            broker,
            config=SagaConfig(timeout_seconds=0.1, broker_id="slow"),
        )
        order = make_order()

        start = time.monotonic()
        result = saga.execute(order, OrderSide.BUY)
        elapsed = time.monotonic() - start

        # 应在 ~0.1s 后超时（留容差）
        assert elapsed < 0.5
        assert result.state == SagaState.COMPENSATED

    def test_timeout_does_not_update_position(self):
        """超时后持仓不应变化。"""
        broker = NeverFillBroker()
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        saga = make_saga(
            broker,
            position_tracker=tracker,
            config=SagaConfig(timeout_seconds=0.1, broker_id="slow"),
        )
        order = make_order()

        saga.execute(order, OrderSide.BUY)

        assert tracker.cash == Decimal("1000000")
        assert len(tracker.holdings) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 超时恢复链成本不可得门禁（AI-R2 红队 ATK-6）
# ──────────────────────────────────────────────────────────────────────────────


class _FilledNoPriceBroker(BrokerInterface):
    """超时后撤单失败、查询返回已成交但均价缺失（市价单数据缺口场景）。"""

    def __init__(self) -> None:
        self._terminal: Order | None = None

    @property
    def broker_id(self) -> str:
        return "noprice"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        broker_oid = f"bk-{order.order_id[:8]}"
        # 已成交但 avg_fill_price=None（broker 数据缺口）
        self._terminal = Order(
            order_id=order.order_id,
            symbol=order.symbol,
            strategy_id=order.strategy_id,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            limit_price=order.limit_price,
            status=OrderStatus.FILLED,
            created_at=order.created_at,
            broker_order_id=broker_oid,
            idempotency_key=order.idempotency_key,
            filled_quantity=order.quantity,
            avg_fill_price=None,
        )
        return broker_oid

    def cancel_order(self, broker_order_id: str) -> bool:
        return False  # 撤单失败（已成交）

    def query_order(self, broker_order_id: str) -> Order | None:
        return self._terminal

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="noprice",
            idempotency_key="noprice",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


class TestRecoverFilledOrderZeroPriceGuard:
    """红队（AI-R2 ATK-6）：市价单超时恢复，成本价不可得 → 不按 0 价入账。

    实证（修复前）：recovered_price=avg_fill_price or limit_price or 0 →
    Fill(price=0) → apply_fill 成本 0 入账 → 后续卖出 realized_pnl 全虚盈。
    修复后：宁缺账（critical 告警人工对账，对账链以券商为准兜底）不错账。
    """

    def test_zero_cost_recovery_rejected(self):
        broker = _FilledNoPriceBroker()
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        saga = make_saga(
            broker,
            position_tracker=tracker,
            config=SagaConfig(timeout_seconds=0.2, broker_id="noprice"),
        )
        # 市价单：limit_price=None（成本兜底链最后一环也缺失）
        order = Order(
            order_id="atk6-mkt",
            symbol="600000.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1000"),
            limit_price=None,
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
            idempotency_key="atk6-mkt",
        )

        result = saga.execute(order, OrderSide.BUY)

        # 修复前：COMPLETED + apply_fill(price=0)；修复后：保持 TIMEOUT 语义人工对账
        assert result.state == SagaState.TIMEOUT
        assert result.fill is None
        assert len(tracker.holdings) == 0  # 成本 0 的持仓未入账
        assert tracker.cash == Decimal("1000000")


# ──────────────────────────────────────────────────────────────────────────────
# 持仓更新失败 + 补偿回滚
# ──────────────────────────────────────────────────────────────────────────────


class TestPositionUpdateFailure:
    """step5 fail, state=COMPENSATED, 持仓回滚。"""

    def test_position_update_failure_compensates(self):
        broker = InstantFillBroker(fill_price=Decimal("10.00"))
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        # 用 mock 让 apply_fill 第二次调用（持仓回滚）时正常, 第一次抛异常
        original_apply = tracker.apply_fill
        call_count = [0]

        def failing_apply(fill, side):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("position update failed")
            return original_apply(fill, side)

        tracker.apply_fill = failing_apply  # type: ignore[method-assign]
        saga = make_saga(broker, position_tracker=tracker)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.COMPENSATED
        assert result.compensated is True
        assert "position update failed" in (result.error or "")


# ──────────────────────────────────────────────────────────────────────────────
# SagaResult 不可变
# ──────────────────────────────────────────────────────────────────────────────


class TestSagaResultFrozen:
    """SagaResult frozen dataclass 不可变。"""

    def test_result_is_frozen(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        with pytest.raises(AttributeError):
            result.state = SagaState.TIMEOUT  # type: ignore[misc]

    def test_result_has_all_fields(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.saga_id is not None
        assert result.order_id is not None
        assert result.symbol == "600000.SH"
        assert result.side == "BUY"
        assert result.state == SagaState.COMPLETED
        assert isinstance(result.steps_completed, tuple)
        assert result.fill is not None
        assert result.error is None
        assert result.compensated is False
        assert result.started_at is not None
        assert result.completed_at is not None
        assert isinstance(result.duration_ms, float)


# ──────────────────────────────────────────────────────────────────────────────
# 审计记录
# ──────────────────────────────────────────────────────────────────────────────


class TestAuditRecords:
    """每步事件记入 ExecutionAuditLogger。"""

    def test_success_logs_all_events(self):
        broker = InstantFillBroker()
        audit = ExecutionAuditLogger()
        saga = make_saga(broker, audit_logger=audit)
        order = make_order()

        saga.execute(order, OrderSide.BUY)

        # 成功流程应记录: ORDER_CREATED + ORDER_SUBMITTED + FILL_RECEIVED + ORDER_FILLED
        event_types = [r.event_type.value for r in audit.query()]
        assert "ORDER_CREATED" in event_types
        assert "ORDER_SUBMITTED" in event_types
        assert "FILL_RECEIVED" in event_types
        assert "ORDER_FILLED" in event_types

    def test_timeout_logs_cancelled(self):
        broker = NeverFillBroker()
        audit = ExecutionAuditLogger()
        saga = make_saga(
            broker,
            audit_logger=audit,
            config=SagaConfig(timeout_seconds=0.1, broker_id="slow"),
        )
        order = make_order()

        saga.execute(order, OrderSide.BUY)

        event_types = [r.event_type.value for r in audit.query()]
        assert "ORDER_EXPIRED" in event_types  # 超时事件
        assert "ORDER_CANCELLED" in event_types  # 补偿撤单

    def test_risk_rejected_logs_rejection(self):
        broker = InstantFillBroker()
        audit = ExecutionAuditLogger()
        saga = make_saga(broker, risk_validator=FakeRiskValidator(reject=True), audit_logger=audit)
        order = make_order()

        saga.execute(order, OrderSide.BUY)

        event_types = [r.event_type.value for r in audit.query()]
        assert "ORDER_REJECTED" in event_types

    def test_audit_chain_valid(self):
        """审计链完整性校验通过。"""
        broker = InstantFillBroker()
        audit = ExecutionAuditLogger()
        saga = make_saga(broker, audit_logger=audit)
        order = make_order()

        saga.execute(order, OrderSide.BUY)

        ok, break_at = audit.verify_chain()
        assert ok is True
        assert break_at is None


# ──────────────────────────────────────────────────────────────────────────────
# 并发安全
# ──────────────────────────────────────────────────────────────────────────────


class TestConcurrency:
    """多笔 Saga 并发执行。"""

    def test_concurrent_sagas(self):
        """多笔 Saga 并发执行, 各自独立完成。"""
        broker = InstantFillBroker(fill_price=Decimal("10.00"))
        tracker = PositionTracker(initial_cash=Decimal("10000000"))
        saga = make_saga(broker, position_tracker=tracker)

        results: list[SagaResult] = []
        errors: list[Exception] = []

        def run_saga(symbol: str):
            try:
                order = make_order(symbol=symbol)
                results.append(saga.execute(order, OrderSide.BUY))
            except Exception as exc:  # noqa: BLE001 — 并发测试工作线程收集一切异常到 errors 列表, 由主线程断言
                errors.append(exc)

        threads = [threading.Thread(target=run_saga, args=(f"60000{i}.SH",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 5
        assert all(r.state == SagaState.COMPLETED for r in results)

        # 每个标的应有 100 股
        for i in range(5):
            assert tracker.holdings[f"60000{i}.SH"] == Decimal("100")


# ──────────────────────────────────────────────────────────────────────────────
# 状态机验证
# ──────────────────────────────────────────────────────────────────────────────


class TestStateMachine:
    """Saga 状态机流转验证。"""

    def test_all_states_are_distinct(self):
        """所有状态值唯一。"""
        values = [s.value for s in SagaState]
        assert len(values) == len(set(values))

    def test_state_count(self):
        """7 成功状态 + 5 失败/补偿状态 = 12。"""
        assert len(list(SagaState)) == 12

    def test_success_states_order(self):
        """成功状态按流程顺序。"""
        success_order = [
            SagaState.INIT,
            SagaState.RISK_PASSED,
            SagaState.SIGNAL_CONFIRMED,
            SagaState.ORDER_SUBMITTED,
            SagaState.FILL_RECEIVED,
            SagaState.POSITION_UPDATED,
            SagaState.COMPLETED,
        ]
        # 验证这些状态都存在
        for s in success_order:
            assert s in SagaState

    def test_failure_states(self):
        """失败/补偿状态。"""
        failure_states = [
            SagaState.RISK_REJECTED,
            SagaState.SIGNAL_INVALID,
            SagaState.ORDER_REJECTED,
            SagaState.TIMEOUT,
            SagaState.COMPENSATED,
        ]
        for s in failure_states:
            assert s in SagaState


# ──────────────────────────────────────────────────────────────────────────────
# 红队：SagaConfig 超时校验（P1）
# ──────────────────────────────────────────────────────────────────────────────


class TestSagaConfigValidation:
    """SagaConfig.__post_init__ 拒绝极端/非法超时值。"""

    def test_timeout_inf_rejected(self):
        with pytest.raises(ValueError, match="正有限数"):
            SagaConfig(timeout_seconds=float("inf"))

    def test_timeout_nan_rejected(self):
        with pytest.raises(ValueError, match="正有限数"):
            SagaConfig(timeout_seconds=float("nan"))

    def test_timeout_zero_rejected(self):
        with pytest.raises(ValueError, match="正有限数"):
            SagaConfig(timeout_seconds=0.0)

    def test_timeout_negative_rejected(self):
        with pytest.raises(ValueError, match="正有限数"):
            SagaConfig(timeout_seconds=-1.0)

    def test_timeout_over_5s_rejected(self):
        with pytest.raises(ValueError, match="≤5s"):
            SagaConfig(timeout_seconds=5.1)

    def test_timeout_valid_accepted(self):
        cfg = SagaConfig(timeout_seconds=5.0)
        assert cfg.timeout_seconds == 5.0
        cfg2 = SagaConfig(timeout_seconds=0.5)
        assert cfg2.timeout_seconds == 0.5


# ──────────────────────────────────────────────────────────────────────────────
# 红队：_FillCollector 非法 fill 拒收（P1）
# ──────────────────────────────────────────────────────────────────────────────


def _make_fill(
    order_id: str,
    qty: Decimal = Decimal("100"),
    price: Decimal = Decimal("10.00"),
    fill_id: str = "rt-fill",
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key=f"idem-{fill_id}",
        order_id=order_id,
        strategy_id="test",
        symbol="600000.SH",
    )


class TestFillCollectorGuard:
    """_FillCollector 对 qty/price 非法的 fill 拒收（不 set event）。"""

    def test_invalid_fill_qty_zero_not_collected(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        collector(_make_fill("ord-1", qty=Decimal("0")))
        assert not collector.collected

    def test_invalid_fill_qty_negative_not_collected(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        collector(_make_fill("ord-1", qty=Decimal("-10")))
        assert not collector.collected

    def test_invalid_fill_qty_over_order_not_collected(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        collector(_make_fill("ord-1", qty=Decimal("200")))
        assert not collector.collected

    def test_invalid_fill_price_nan_not_collected(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        collector(_make_fill("ord-1", price=Decimal("NaN")))
        assert not collector.collected

    def test_valid_fill_collected(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        fill = _make_fill("ord-1", qty=Decimal("100"), price=Decimal("10.00"))
        collector(fill)
        assert collector.collected
        assert collector.wait(timeout=0.1) is fill

    def test_other_order_fill_ignored(self):
        from zephyr.ex_core.order_execution_saga import _FillCollector

        collector = _FillCollector("ord-1", Decimal("100"))
        collector(_make_fill("ord-other"))
        assert not collector.collected


# ──────────────────────────────────────────────────────────────────────────────
# 红队：execute 终态订单重复执行守卫（P2）
# ──────────────────────────────────────────────────────────────────────────────


class TestExecuteTerminalStateGuard:
    """已处终态（FILLED/CANCELLED/REJECTED）的订单拒绝重复执行。"""

    def test_execute_filled_order_rejected(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()
        order.status = OrderStatus.FILLED

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.SIGNAL_INVALID
        assert result.error is not None
        assert "终态" in result.error
        assert result.steps_completed == ()

    def test_execute_cancelled_order_rejected(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()
        order.status = OrderStatus.CANCELLED

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.SIGNAL_INVALID
        assert "终态" in (result.error or "")

    def test_execute_rejected_order_rejected(self):
        broker = InstantFillBroker()
        saga = make_saga(broker)
        order = make_order()
        order.status = OrderStatus.REJECTED

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.SIGNAL_INVALID
        assert "终态" in (result.error or "")


# ──────────────────────────────────────────────────────────────────────────────
# 拒单分类实际动作 Saga 接管（40 号 §6.1 gap 4，A14 Phase 2）
# ──────────────────────────────────────────────────────────────────────────────


class _CodedRejectBroker(BrokerInterface):
    """submit_order 抛带 int error_code 异常的券商（模拟 xttrader 拒单）。"""

    def __init__(self, error_code: int | None):
        self._error_code = error_code

    @property
    def broker_id(self) -> str:
        return "coded-reject"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        exc = RuntimeError(f"broker rejected (code={self._error_code})")
        exc.error_code = self._error_code  # type: ignore[attr-defined]
        raise exc

    def cancel_order(self, broker_order_id: str) -> bool:
        return False

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="coded-reject",
            idempotency_key="coded-reject",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


class TestRejectionExecutorTakeover:
    """gap 4：注入 RejectionActionExecutor 后 Saga 接管拒单分类实际动作。"""

    def test_alert_freeze_freezes_strategy(self):
        """error 54（资金不足）→ ALERT_FREEZE 实际动作：策略新开仓冻结。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        alerts: list[tuple[str, dict]] = []
        executor = RejectionActionExecutor(alert_sink=lambda m, c: alerts.append((m, c)))
        saga = make_saga(_CodedRejectBroker(54), rejection_executor=executor)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        assert executor.is_strategy_frozen(order.strategy_id)
        assert alerts, "ALERT_FREEZE 应触发告警"

    def test_alert_reconcile_triggers(self):
        """error 55（持仓不足）→ ALERT_RECONCILE 实际动作：触发持仓对账。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        triggered: list[tuple[str, str]] = []
        executor = RejectionActionExecutor(reconcile_trigger=lambda s, y: triggered.append((s, y)))
        saga = make_saga(_CodedRejectBroker(55), rejection_executor=executor)

        result = saga.execute(make_order(), OrderSide.SELL)

        assert result.state == SagaState.ORDER_REJECTED
        assert triggered == [("test", "600000.SH")]

    def test_retry_once_invokes_injected_retry_fn(self):
        """error 53（价格不合法）→ RETRY_ONCE：调用装配层注入的 retry_fn。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        retried: list[str] = []
        executor = RejectionActionExecutor(retry_fn=lambda o, e: retried.append(o.order_id) or "bo-retry")
        saga = make_saga(_CodedRejectBroker(53), rejection_executor=executor)

        result = saga.execute(make_order(), OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        assert len(retried) == 1

    def test_abandon_for_limit_up(self):
        """error 50（涨停）→ ABANDON：不重试不冻结，仅留痕。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        executor = RejectionActionExecutor()
        saga = make_saga(_CodedRejectBroker(50), rejection_executor=executor)
        order = make_order()

        result = saga.execute(order, OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        assert not executor.is_strategy_frozen(order.strategy_id)

    def test_no_executor_keeps_mvp_behavior(self):
        """未注入 executor：既有 MVP 行为（仅审计留痕，不崩溃）。"""
        audit = ExecutionAuditLogger()
        saga = make_saga(_CodedRejectBroker(54), audit_logger=audit)

        result = saga.execute(make_order(), OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        rejected = [r for r in audit.query() if r.event_type.value == "ORDER_REJECTED"]
        assert rejected
        assert rejected[0].detail.get("rejection_action") is None

    def test_non_int_error_code_conservative_abandon(self):
        """无 int error_code（本地异常）→ 保守 ABANDON 留痕。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        executor = RejectionActionExecutor()
        saga = make_saga(_CodedRejectBroker(None), rejection_executor=executor)

        result = saga.execute(make_order(), OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED

    def test_executor_exception_swallowed(self):
        """执行器自身异常吞没，不阻断 Saga 主流程（拒单处置不得引发二次事故）。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        def _boom(order, error):
            raise RuntimeError("retry_fn exploded")

        executor = RejectionActionExecutor(retry_fn=_boom)
        saga = make_saga(_CodedRejectBroker(53), rejection_executor=executor)

        result = saga.execute(make_order(), OrderSide.BUY)

        assert result.state == SagaState.ORDER_REJECTED
        assert "order submit failed" in (result.error or "")

    def test_audit_records_rejection_outcome(self):
        """审计 detail 留痕分类动作与结果。"""
        from zephyr.ex_core.rejection_action_handler import RejectionActionExecutor

        audit = ExecutionAuditLogger()
        executor = RejectionActionExecutor()
        saga = make_saga(_CodedRejectBroker(54), audit_logger=audit, rejection_executor=executor)

        saga.execute(make_order(), OrderSide.BUY)

        rejected = [r for r in audit.query() if r.event_type.value == "ORDER_REJECTED"]
        assert rejected[0].detail.get("rejection_action") == "ALERT_FREEZE"
        assert rejected[0].detail.get("rejection_outcome") == "frozen"
