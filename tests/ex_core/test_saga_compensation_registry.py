# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md
# [MODULE] tests.ex_core.test_saga_compensation_registry
# [DOMAIN] D_EX_CORE
# [TTL] permanent
"""SagaCompensationRegistry 单元测试 — F53 夜战批

覆盖（三态判据：每步 成功不触发 / 失败触发 / 补偿回滚语义）:
    注册面: 注册/只读/非幂等拒绝/空 step 拒绝
    执行面: 逆序执行 / 单动作异常不阻断 / 空表零记录 / 永不抛
    集成面: OrderExecutionSaga 三补偿点接线（step5 失败/异常路径/超时终判）
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from zephyr.ex_core.order_execution_saga import (
    OrderExecutionSaga,
    SagaConfig,
    SagaState,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.saga_compensation_registry import (
    CompensationAction,
    SagaCompensationContext,
    SagaCompensationOutcome,
    SagaCompensationRegistry,
)

# Saga 级集成测试的通用 Fake 组件（复用既有测试件的 FakeRiskValidator 模式，防克隆整抄=独立小实现）


class _PassValidator:
    """全通过风控校验器。"""

    def validate_order(self, symbol, target_weight, current_holdings, limits):
        return []

    def validate_portfolio(self, holdings, market_values, total_nav, limits):
        return []


class _InstantFillBroker:
    """即时成交 mock 券商（不实连）。"""

    def __init__(self) -> None:
        self.broker_id = "mock-sim"
        self._callbacks: list[Any] = []
        self._orders: dict[str, Any] = {}
        self.cancel_calls: list[str] = []

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def submit_order(self, order):
        from zephyr.shared.contracts.fill import Fill

        broker_oid = f"bk-{order.order_id[:8]}"
        self._orders[broker_oid] = order
        fill = Fill(
            fill_id=f"fill-{order.order_id[:8]}",
            fill_price=order.limit_price or Decimal("10.00"),
            fill_timestamp=_utcnow(),
            filled_quantity=order.quantity,
            idempotency_key=f"fill-{order.idempotency_key}",
            order_id=order.order_id,
            strategy_id=order.strategy_id,
            symbol=order.symbol,
            commission=Decimal("1"),
        )
        for cb in list(self._callbacks):
            cb(fill)
        return broker_oid

    def cancel_order(self, broker_order_id: str) -> bool:
        self.cancel_calls.append(broker_order_id)
        return broker_order_id in self._orders

    def query_order(self, broker_order_id):
        return self._orders.get(broker_order_id)

    def get_positions(self):
        from datetime import UTC, datetime

        from zephyr.shared.contracts.position import PositionSnapshot

        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="mock-sim",
            idempotency_key="mock-sim",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        self._callbacks.append(callback)


def _utcnow():
    from datetime import UTC, datetime

    return datetime.now(UTC)


def _make_order(symbol: str = "600000.SH"):
    import time
    from datetime import UTC, datetime

    from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
    from zephyr.shared.contracts.order import Order

    nonce = int(time.time() * 1000) % 1000000
    return Order(
        order_id=f"t-reg-{symbol}-{nonce}",
        symbol=symbol,
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10.00"),
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        idempotency_key=f"key-{nonce}",
    )


def _make_ctx(saga_id: str = "s1") -> SagaCompensationContext:
    return SagaCompensationContext(
        saga_id=saga_id,
        order_id="o1",
        symbol="600000.SH",
        side="BUY",
        state="ORDER_SUBMITTED",
        error=None,
        fill=None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册面
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistryRegistration:
    def test_register_and_readback(self):
        reg = SagaCompensationRegistry()
        a1 = CompensationAction("a1", lambda ctx: None)
        a2 = CompensationAction("a2", lambda ctx: None)
        reg.register("order_submit", a1)
        reg.register("order_submit", a2)
        assert reg.actions_for("order_submit") == (a1, a2)
        assert reg.registered_steps == ("order_submit",)

    def test_unknown_step_empty(self):
        reg = SagaCompensationRegistry()
        assert reg.actions_for("nope") == ()

    def test_non_idempotent_rejected(self):
        reg = SagaCompensationRegistry()
        with pytest.raises(ValueError, match="幂等"):
            reg.register("order_submit", CompensationAction("bad", lambda ctx: None, idempotent=False))

    def test_uncallable_rejected(self):
        with pytest.raises(ValueError, match="不可调用"):
            CompensationAction("bad", "not-callable")  # type: ignore[arg-type]

    def test_empty_step_rejected(self):
        reg = SagaCompensationRegistry()
        with pytest.raises(ValueError, match="step"):
            reg.register("", CompensationAction("a", lambda ctx: None))

    def test_clear(self):
        reg = SagaCompensationRegistry()
        reg.register("order_submit", CompensationAction("a", lambda ctx: None))
        reg.clear()
        assert reg.registered_steps == ()


# ──────────────────────────────────────────────────────────────────────────────
# 执行面（三态判据核心）
# ──────────────────────────────────────────────────────────────────────────────


class TestRunCompensations:
    def test_success_step_no_compensation_called(self):
        """成功态：动作已注册但步骤未进补偿序列 → 不触发。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        reg.register("order_submit", CompensationAction("cleanup", lambda ctx: calls.append("x")))
        reg.run_compensations([], _make_ctx())  # 空步骤序列=全部成功，零补偿
        assert calls == []

    def test_failure_triggers_reverse_order(self):
        """失败态：已完成步骤逆序补偿（后完成先补偿）。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        reg.register("risk_check", CompensationAction("undo_risk", lambda ctx: calls.append("risk")))
        reg.register("order_submit", CompensationAction("undo_submit", lambda ctx: calls.append("submit")))
        reg.run_compensations(["risk_check", "order_submit"], _make_ctx())
        assert calls == ["submit", "risk"]

    def test_lifo_within_step(self):
        """同步骤多动作按注册逆序（LIFO）执行。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        reg.register("position_update", CompensationAction("first", lambda ctx: calls.append("1")))
        reg.register("position_update", CompensationAction("second", lambda ctx: calls.append("2")))
        reg.run_compensations(["position_update"], _make_ctx())
        assert calls == ["2", "1"]

    def test_action_exception_captured_not_raised(self):
        """补偿回滚态：动作自身抛异常=FAILED 记录，不阻断其余动作、不外抛。"""
        reg = SagaCompensationRegistry()

        def _boom(ctx):
            raise RuntimeError("boom")

        calls: list[str] = []
        reg.register("order_submit", CompensationAction("boom", _boom))
        reg.register("order_submit", CompensationAction("after", lambda ctx: calls.append("after")))
        records = reg.run_compensations(["order_submit"], _make_ctx())
        # 逆序：after 先执行成功，boom 后执行失败
        assert [(r.action_name, r.outcome) for r in records] == [
            ("after", SagaCompensationOutcome.EXECUTED),
            ("boom", SagaCompensationOutcome.FAILED),
        ]
        assert "boom" in records[1].error
        assert calls == ["after"]

    def test_context_passed_to_action(self):
        reg = SagaCompensationRegistry()
        seen: dict[str, Any] = {}
        reg.register(
            "fill_confirm",
            CompensationAction("peek", lambda ctx: seen.update(order_id=ctx.order_id, state=ctx.state)),
        )
        reg.run_compensations(["fill_confirm"], _make_ctx("s42"))
        assert seen == {"order_id": "o1", "state": "ORDER_SUBMITTED"}

    def test_run_never_raises_on_registry_edge(self):
        """空注册表执行=零记录（Saga 零行为变化的注册表侧前提）。"""
        reg = SagaCompensationRegistry()
        assert reg.run_compensations(["risk_check", "report"], _make_ctx()) == []


# ──────────────────────────────────────────────────────────────────────────────
# 集成面：OrderExecutionSaga 三补偿点
# ──────────────────────────────────────────────────────────────────────────────


def _make_saga(broker, tracker=None, registry=None) -> OrderExecutionSaga:
    om = OrderManager()
    om.register_broker(broker.broker_id, broker)
    return OrderExecutionSaga(
        order_manager=om,
        risk_validator=_PassValidator(),
        position_tracker=tracker or PositionTracker(initial_cash=Decimal("1000000")),
        audit_logger=_StubAudit(),
        broker=broker,
        broker_id=broker.broker_id,
        config=SagaConfig(timeout_seconds=5.0, broker_id=broker.broker_id),
        compensation_registry=registry,
    )


class _StubAudit:
    """审计桩：只收集事件。"""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log(self, event_type, order_id, symbol, source, details=None):
        self.events.append((event_type.value if hasattr(event_type, "value") else str(event_type), details))


class _ExplodingPositionTracker(PositionTracker):
    """step5 首次入账必失败、回滚入账放行的持仓跟踪器（三态：失败→回滚成功）。"""

    def __init__(self, initial_cash: Decimal) -> None:
        super().__init__(initial_cash=initial_cash)
        self.forward_calls = 0

    def apply_fill(self, fill, side):
        self.forward_calls += 1
        if self.forward_calls == 1:
            raise RuntimeError("position update exploded")
        return super().apply_fill(fill, side)


class TestSagaIntegration:
    def test_step5_failure_runs_registry_compensations(self):
        """step5 失败：内建持仓回滚后，注册表动作按逆序触发。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        reg.register("position_update", CompensationAction("release_reserve", lambda ctx: calls.append("release")))
        reg.register("fill_confirm", CompensationAction("mark_pending", lambda ctx: calls.append("mark")))
        broker = _InstantFillBroker()
        tracker = _ExplodingPositionTracker(initial_cash=Decimal("1000000"))
        saga = _make_saga(broker, tracker=tracker, registry=reg)
        result = saga.execute(_make_order(), _buy_side())
        assert result.state == SagaState.COMPENSATED
        assert result.compensated  # 内建持仓回滚已成功
        # 逆序（最新先补偿）：失败步骤 position_update 的动作先于 fill_confirm 的动作
        assert calls == ["release", "mark"]

    def test_success_path_skips_registry(self):
        """成功态：全六步走完，注册表动作零触发（零行为变化）。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        for step in ("risk_check", "order_submit", "position_update"):
            reg.register(step, CompensationAction(f"c-{step}", lambda ctx, s=step: calls.append(s)))
        broker = _InstantFillBroker()
        saga = _make_saga(broker, registry=reg)
        result = saga.execute(_make_order(), _buy_side())
        assert result.state == SagaState.COMPLETED
        assert not result.compensated
        assert calls == []

    def test_timeout_concluded_timeout_runs_registry(self):
        """超时终判 TIMEOUT（撤单成功、无成交恢复）：注册表动作触发。"""
        reg = SagaCompensationRegistry()
        calls: list[str] = []
        reg.register("order_submit", CompensationAction("cleanup", lambda ctx: calls.append("cleanup")))
        broker = _NeverFillBroker()
        saga = _make_saga(broker, registry=reg)
        config_timeout = SagaConfig(timeout_seconds=0.2, broker_id=broker.broker_id)
        om = OrderManager()
        om.register_broker(broker.broker_id, broker)
        saga2 = OrderExecutionSaga(
            order_manager=om,
            risk_validator=_PassValidator(),
            position_tracker=PositionTracker(initial_cash=Decimal("1000000")),
            audit_logger=_StubAudit(),
            broker=broker,
            broker_id=broker.broker_id,
            config=config_timeout,
            compensation_registry=reg,
        )
        result = saga2.execute(_make_order(), _buy_side())
        # 超时→撤单成功：终态=COMPENSATED（超时态被成功补偿覆盖，与既有用例口径一致）
        assert result.state == SagaState.COMPENSATED
        assert result.compensated  # 内建撤单已执行
        assert calls == ["cleanup"]

    def test_no_registry_zero_behavior_change(self):
        """未注入注册表：既有路径零变化（回归锁）。"""
        broker = _InstantFillBroker()
        saga = _make_saga(broker, registry=None)
        result = saga.execute(_make_order(), _buy_side())
        assert result.state == SagaState.COMPLETED


class _NeverFillBroker:
    """永不成交 mock 券商（超时路径，撤单成功可被取消）。"""

    def __init__(self) -> None:
        self.broker_id = "mock-slow"
        self._orders: dict[str, Any] = {}

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def submit_order(self, order):
        broker_oid = f"bk-{order.order_id[:8]}"
        self._orders[broker_oid] = order
        return broker_oid

    def cancel_order(self, broker_order_id: str) -> bool:
        return broker_order_id in self._orders

    def query_order(self, broker_order_id):
        return self._orders.get(broker_order_id)

    def get_positions(self):
        from datetime import UTC, datetime

        from zephyr.shared.contracts.position import PositionSnapshot

        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="mock-slow",
            idempotency_key="mock-slow",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        return None


def _buy_side():
    from zephyr.shared.contracts.enums.order_enums import OrderSide

    return OrderSide.BUY
