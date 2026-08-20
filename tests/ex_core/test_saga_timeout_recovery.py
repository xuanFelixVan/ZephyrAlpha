# [A_test] module_id: MOD-EXE-saga_timeout_recovery_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md | §
# [MODULE] tests.ex_core.test_saga_timeout_recovery
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""OrderExecutionSaga 超时分支修复测试（裁定书 §三 P0-2，#ARCH-100，AI-RWIRE-001）。

修复点：步骤4成交确认超时 → 补偿撤单返回 False 时，强制查询订单终态——
  - 已成交：补走 step5 持仓更新 + step6 报告（不再吞掉成交导致持仓漂移）
  - 未成交/无法确认终态：保持 TIMEOUT 语义 + critical 告警（需人工对账）
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from zephyr.ex_core.audit_journal.auditor import ExecutionAuditLogger
from zephyr.ex_core.order_execution_saga import (
    OrderExecutionSaga,
    SagaConfig,
    SagaState,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface


class _FakeRiskValidator:
    """风控全放行。"""

    def validate_order(self, symbol, target_weight, current_holdings, limits):
        return []


def _empty_positions(portfolio_id: str) -> PositionSnapshot:
    return PositionSnapshot(
        as_of_timestamp=datetime.now(UTC),
        portfolio_id=portfolio_id,
        idempotency_key=portfolio_id,
        cash=Decimal("1000000"),
        gross_leverage=0.0,
        holdings={},
        market_values={},
        total_market_value=Decimal("0"),
    )


class CancelFailsFilledBroker(BrokerInterface):
    """不推 fill 回调 + 撤单 False + query 返回 FILLED——超时但实际已成交。"""

    @property
    def broker_id(self) -> str:
        return "timeout_filled"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        return f"bk-{order.order_id[:8]}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return False  # 券商端拒绝撤单（已成交）

    def query_order(self, broker_order_id: str) -> Order | None:
        return Order(
            order_id="unknown-local-id",
            idempotency_key="bk-query",
            symbol="600000.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10.00"),
            status=OrderStatus.FILLED,
            filled_quantity=Decimal("100"),
            avg_fill_price=Decimal("10.00"),
            broker_order_id=broker_order_id,
            created_at=datetime.now(UTC),
        )

    def get_positions(self) -> PositionSnapshot:
        return _empty_positions("timeout_filled")

    def register_fill_callback(self, callback) -> None:
        pass


class CancelFailsNotFilledBroker(BrokerInterface):
    """不推 fill 回调 + 撤单 False + query 返回 CANCELLED——超时且确未成交。"""

    @property
    def broker_id(self) -> str:
        return "timeout_not_filled"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        return f"bk-{order.order_id[:8]}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return False

    def query_order(self, broker_order_id: str) -> Order | None:
        return Order(
            order_id="unknown-local-id",
            idempotency_key="bk-query",
            symbol="600000.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10.00"),
            status=OrderStatus.CANCELLED,
            broker_order_id=broker_order_id,
            created_at=datetime.now(UTC),
        )

    def get_positions(self) -> PositionSnapshot:
        return _empty_positions("timeout_not_filled")

    def register_fill_callback(self, callback) -> None:
        pass


class CancelFailsQueryDownBroker(CancelFailsNotFilledBroker):
    """撤单 False + 券商查询也失效——终态无法确认。"""

    @property
    def broker_id(self) -> str:
        return "timeout_query_down"

    def query_order(self, broker_order_id: str) -> Order | None:
        raise ConnectionError("broker query down")


def _make_order() -> Order:
    return Order(
        order_id="test-saga-recovery-1",
        idempotency_key="key-saga-recovery-1",
        symbol="600000.SH",
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10.00"),
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
    )


def _make_saga(
    broker: BrokerInterface,
    tracker: PositionTracker,
    audit: ExecutionAuditLogger,
) -> OrderExecutionSaga:
    om = OrderManager()
    om.register_broker(broker.broker_id, broker)
    return OrderExecutionSaga(
        order_manager=om,
        risk_validator=_FakeRiskValidator(),
        position_tracker=tracker,
        audit_logger=audit,
        broker=broker,
        broker_id=broker.broker_id,
        config=SagaConfig(timeout_seconds=0.1, broker_id=broker.broker_id),
    )


class TestTimeoutRecovery:
    """超时 + 撤单失败 → 强制查询终态分支。"""

    def test_filled_order_recovers_to_completed(self) -> None:
        """超时但订单已成交：补走 step5/6——COMPLETED + 持仓真实更新 + 审计留痕。"""
        broker = CancelFailsFilledBroker()
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        audit = ExecutionAuditLogger()
        saga = _make_saga(broker, tracker, audit)

        result = saga.execute(_make_order(), OrderSide.BUY)

        assert result.state == SagaState.COMPLETED
        assert result.compensated is False
        assert result.fill is not None
        assert result.fill.fill_id.startswith("saga-fq-")
        assert "fill_confirm(force_query)" in result.steps_completed
        # 持仓真实更新（100 股 @10.00，现金扣 1000）
        assert tracker.holdings == {"600000.SH": Decimal("100")}
        assert tracker.cash == Decimal("999000")
        # 审计留痕：恢复来源可识别
        events = list(audit.query())
        fill_events = [r for r in events if r.event_type.value == "FILL_RECEIVED"]
        assert fill_events, "FILL_RECEIVED 审计事件缺失"
        assert any("force_query" in str(r.detail) for r in fill_events)

    def test_not_filled_keeps_timeout(self) -> None:
        """超时且确未成交：保持 TIMEOUT，持仓不变，不标记补偿。"""
        broker = CancelFailsNotFilledBroker()
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        audit = ExecutionAuditLogger()
        saga = _make_saga(broker, tracker, audit)

        result = saga.execute(_make_order(), OrderSide.BUY)

        assert result.state == SagaState.TIMEOUT
        assert result.fill is None
        assert result.compensated is False
        assert tracker.holdings == {}
        assert tracker.cash == Decimal("1000000")

    def test_query_unavailable_keeps_timeout_no_crash(self) -> None:
        """撤单失败 + 券商查询失效：保持 TIMEOUT，不抛异常（告警需人工对账）。"""
        broker = CancelFailsQueryDownBroker()
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        audit = ExecutionAuditLogger()
        saga = _make_saga(broker, tracker, audit)

        result = saga.execute(_make_order(), OrderSide.BUY)

        assert result.state == SagaState.TIMEOUT
        assert result.fill is None
        assert tracker.holdings == {}
