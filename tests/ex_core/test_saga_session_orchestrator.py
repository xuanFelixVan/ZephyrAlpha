# [A_test] module_id: MOD-L06-001-SAGAO-test-orch | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_saga_session_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""F53 SagaSessionOrchestrator——补偿三态/生命周期相位/单写者契约单元测试。

覆盖（F53 处方：Saga=TradingSession 提交面编排层封装，非第二提交通道）：
  - 补偿三态：CANCELLED（超时撤单成功）/NOT_NEEDED（已终态）/FAILED（撤单
    失败且终态不可确认→升级人工对账）
  - 下单→部分成交→终态→对账 相位推进（OrderManager 回调事件驱动）
  - 超时补偿事件触发懒扫（时钟注入确定性判定，无 Timer）
  - 单写者契约：编排器零账本写（仅 OM cancel 通道）；重复登记幂等
  - 九态对账面：matched→RECONCILED；漂移→升级回调；批量词表外 fail-closed
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.saga_session_orchestrator import (
    CompensationOutcome,
    GuardVerdict,
    SagaPhase,
    SagaSessionOrchestrator,
)
from zephyr.shared.contracts.enums.order_enums import BrokerOrderState, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

# ---------------------------------------------------------------------
# 桩件与辅助
# ---------------------------------------------------------------------


class _FakeClock:
    """确定性时钟（事件触发懒扫的时序控制）。"""

    def __init__(self) -> None:
        self.now = datetime(2026, 9, 29, 10, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now = self.now + timedelta(seconds=seconds)


def _make_order(
    order_id: str = "ord-1",
    *,
    status: OrderStatus = OrderStatus.PENDING,
    filled_quantity: Decimal = Decimal("0"),
) -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"ik-{order_id}",
        symbol="600519.SH",
        strategy_id="saga_test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("100"),
        status=status,
        filled_quantity=filled_quantity,
        created_at=datetime.now(UTC),
    )


def _make_fill(order_id: str, qty: Decimal = Decimal("40")) -> Fill:
    return Fill(
        fill_id=f"f-{order_id}-1",
        fill_price=Decimal("100"),
        fill_timestamp=datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key=f"fik-{order_id}-1",
        order_id=order_id,
        strategy_id="saga_test",
        symbol="600519.SH",
    )


def _make_orchestrator(
    *,
    timeout_seconds: float = 30.0,
    clock: _FakeClock | None = None,
    on_drift=None,
) -> tuple[SagaSessionOrchestrator, OrderManager, _FakeClock]:
    """真实 OrderManager（无 broker 注册，撤单走纯本地面）+ 注入时钟的编排器。"""
    clock = clock or _FakeClock()
    om = OrderManager()
    orch = SagaSessionOrchestrator(
        om,
        order_timeout_seconds=timeout_seconds,
        on_drift=on_drift,
        clock=clock,
    )
    return orch, om, clock


def _register_via_om(om: OrderManager, order: Order) -> None:
    """把值对象订单注册进 OM 台账（模拟 session 提交后的登记面）。"""
    om.orders[order.order_id] = order


# ---------------------------------------------------------------------
# 补偿三态
# ---------------------------------------------------------------------


def test_compensation_cancelled_on_timeout() -> None:
    """补偿态一 CANCELLED：在途超时→懒扫撤单成功（OM 同一通道，状态机合法流转）。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=30.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    clock.advance(31.0)
    records = orch.sweep()
    assert len(records) == 1
    assert records[0].outcome is CompensationOutcome.CANCELLED
    assert order.status is OrderStatus.CANCELLED  # OM 状态机所写，非编排器
    life = orch.get_lifecycle(order.order_id)
    assert life is not None and life.phase is SagaPhase.TERMINAL
    # 重复懒扫幂等：终态不再补偿
    assert orch.sweep() == []


def test_compensation_not_needed_when_terminal() -> None:
    """终态先于 deadline 到达：懒扫零动作（终态由 fill 事件即时推进，无补账噪音）。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=30.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    life = orch.track_order(order, OrderSide.BUY)
    # 模拟成交链入账：OM._on_fill 更新台账并合法流转 FILLED（fill 事件→TERMINAL）
    om._on_fill(_make_fill(order.order_id, Decimal("100")))
    assert order.status is OrderStatus.FILLED
    assert life.phase is SagaPhase.TERMINAL
    clock.advance(31.0)
    assert orch.sweep() == []  # 已终态，deadline 到达也零补偿
    assert order.status is OrderStatus.FILLED  # 不改账


def test_compensation_not_needed_when_order_absent() -> None:
    """补偿态二 NOT_NEEDED（防御分支）：跟踪单不在 OM 台账（异常登记面）→
    无状态可补偿，NOT_NEEDED 留痕不炸。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=30.0)
    order = _make_order("ord-ghost")  # 故意不 _register_via_om
    orch.track_order(order, OrderSide.BUY)
    clock.advance(31.0)
    records = orch.sweep()
    assert len(records) == 1
    assert records[0].outcome is CompensationOutcome.NOT_NEEDED
    assert "不在册" in records[0].detail


def test_compensation_failed_escalates_reconciliation() -> None:
    """补偿态三 FAILED：撤单失败且终态不可确认→人工对账升级（吞成交漂移防线）。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=30.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    # 撤单失败注入：cancel 恒 False，get_order 恒返回在途（终态不可确认）
    om.cancel_order = lambda order_id: False  # type: ignore[method-assign]
    clock.advance(31.0)
    records = orch.sweep()
    assert len(records) == 1
    assert records[0].outcome is CompensationOutcome.FAILED
    assert "人工对账" in records[0].detail
    life = orch.get_lifecycle(order.order_id)
    assert life is not None and life.phase is SagaPhase.PLACED  # 未终态未对账，挂账待人工


def test_compensation_failed_then_recovered_when_terminal_arrives() -> None:
    """FAILED 分流治本：撤单失败但台账已终态→NOT_NEEDED 转对账（不吞成交）。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=30.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    # 首次 cancel 失败； OM 台账此间已由成交链入账转 FILLED
    orig_cancel = om.cancel_order

    def _cancel_then_filled(order_id: str) -> bool:
        om._on_fill(_make_fill(order_id, Decimal("100")))
        return orig_cancel(order_id)

    om.cancel_order = _cancel_then_filled  # type: ignore[method-assign]
    clock.advance(31.0)
    records = orch.sweep()
    assert len(records) == 1
    assert records[0].outcome is CompensationOutcome.NOT_NEEDED
    life = orch.get_lifecycle(order.order_id)
    assert life is not None and life.phase is SagaPhase.TERMINAL
    assert life.terminal_status is OrderStatus.FILLED


# ---------------------------------------------------------------------
# 生命周期相位（下单→部分成交→终态→对账）
# ---------------------------------------------------------------------


def test_lifecycle_partial_phase_progression() -> None:
    """下单→部分成交：OM fill 回调到达→PARTIAL 相位（编排器零账本写）。"""
    orch, om, _ = _make_orchestrator()
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    life = orch.track_order(order, OrderSide.BUY)
    assert life.phase is SagaPhase.PLACED
    om._on_fill(_make_fill(order.order_id, Decimal("40")))
    assert life.phase is SagaPhase.PARTIAL
    assert order.status is OrderStatus.PARTIAL  # OM 状态机写的
    assert order.filled_quantity == Decimal("40")  # OM 写的（单写者=成交链）


def test_lifecycle_terminal_via_order_event_and_nine_vocabulary() -> None:
    """终态经订单事件推进：撤单→TERMINAL，九态词表出口=单词 CANCELLED。"""
    orch, om, _ = _make_orchestrator()
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    life = orch.track_order(order, OrderSide.BUY)
    assert om.cancel_order(order.order_id) is True
    assert life.phase is SagaPhase.TERMINAL
    assert life.terminal_status is OrderStatus.CANCELLED
    report = life.to_report()
    assert report["nine_vocabulary"] == ["CANCELLED"]


def test_lifecycle_reconciled_phase_on_matched_terminal() -> None:
    """终态+对账一致→RECONCILED 相位（生命周期四相闭环）。"""
    orch, om, _ = _make_orchestrator()
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    life = orch.track_order(order, OrderSide.BUY)
    om._on_fill(_make_fill(order.order_id, Decimal("100")))
    verdict = orch.reconcile(order.order_id, BrokerOrderState.FILLED)
    assert verdict is not None and verdict.matched is True
    assert life.phase is SagaPhase.RECONCILED


def test_track_order_idempotent_and_late_terminal() -> None:
    """登记幂等：同单重复 track 同 saga_id；迟到登记已终态单直落 TERMINAL。"""
    orch, om, _ = _make_orchestrator()
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    life1 = orch.track_order(order, OrderSide.BUY)
    life2 = orch.track_order(order, OrderSide.SELL)  # 重复登记（side 不同也幂等）
    assert life1 is life2
    assert orch.tracked_count == 1
    terminal_order = _make_order("ord-term", status=OrderStatus.REJECTED)
    _register_via_om(om, terminal_order)
    life3 = orch.track_order(terminal_order, OrderSide.BUY)
    assert life3.phase is SagaPhase.TERMINAL
    assert life3.terminal_status is OrderStatus.REJECTED


# ---------------------------------------------------------------------
# 单写者契约（与 TradingSession 不冲突）
# ---------------------------------------------------------------------


def test_single_writer_no_ledger_writes() -> None:
    """单写者：编排器对在途订单零写——观察/登记/未到期懒扫全程状态不变。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=3600.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    # fill 到达/订单事件到达/多次懒扫——状态只允许 OM 成交链语义
    om._on_fill(_make_fill(order.order_id, Decimal("30")))
    orch.on_order_event(order)
    clock.advance(60.0)
    records = orch.sweep()  # 超时 3600s 未到，零补偿
    assert records == []
    assert order.status is OrderStatus.PARTIAL  # 仅 OM._on_fill 写过
    assert order.filled_quantity == Decimal("30")
    # 编排器无账本写面：不持 position_tracker、无 apply_fill 方法
    assert not hasattr(orch, "_position_tracker")
    assert not hasattr(orch, "apply_fill")


def test_single_writer_cancel_is_only_write_channel() -> None:
    """唯一写动作=补偿撤单且只走 OM.cancel_order 一次（无第二通道）。"""
    calls: list[str] = []
    orch, om, clock = _make_orchestrator(timeout_seconds=10.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    orig_cancel = om.cancel_order

    def _spy_cancel(order_id: str) -> bool:
        calls.append(order_id)
        return orig_cancel(order_id)

    om.cancel_order = _spy_cancel  # type: ignore[method-assign]
    clock.advance(11.0)
    orch.sweep()
    clock.advance(60.0)
    orch.sweep()
    assert calls == [order.order_id]  # 恰一次（终态后不再补偿）
    assert order.status is OrderStatus.CANCELLED


# ---------------------------------------------------------------------
# 九态对账面（升级回调/批量 fail-closed）
# ---------------------------------------------------------------------


def test_reconcile_drift_invokes_on_drift_callback() -> None:
    """对账漂移→升级回调承接（不改账本），在途单相位不变。"""
    drifts: list[object] = []
    orch, om, _ = _make_orchestrator(on_drift=drifts.append)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    verdict = orch.reconcile(order.order_id, BrokerOrderState.PARTIAL)
    assert verdict is not None and verdict.matched is False
    assert len(drifts) == 1
    assert drifts[0] is verdict
    assert orch.get_lifecycle(order.order_id).phase is SagaPhase.PLACED


def test_reconcile_all_unknown_state_fail_closed() -> None:
    """批量对账词表外：逐单吞没为漂移记录（不断言不断链，fail-closed 留痕）。"""
    orch, om, _ = _make_orchestrator()
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    verdicts = orch.reconcile_all({order.order_id: "GHOST_STATE"})
    assert len(verdicts) == 1
    assert verdicts[0].matched is False
    assert "fail-closed" in verdicts[0].detail


def test_reconcile_untracked_order_returns_none() -> None:
    """对账面只对在册跟踪订单负责：未登记单返回 None。"""
    orch, om, _ = _make_orchestrator()
    assert orch.reconcile("never-tracked", BrokerOrderState.FILLED) is None


# ---------------------------------------------------------------------
# 配置与时序纪律
# ---------------------------------------------------------------------


def test_invalid_timeout_rejected() -> None:
    """非正超时=配置错误 fail-fast。"""
    with pytest.raises(ValueError):
        SagaSessionOrchestrator(OrderManager(), order_timeout_seconds=0)
    with pytest.raises(ValueError):
        SagaSessionOrchestrator(OrderManager(), order_timeout_seconds=-1.0)


def test_sweep_event_triggered_only_no_timer() -> None:
    """懒扫纪律：无到期事件时 sweep 零动作；补偿仅由显式事件（fill/订单事件/
    rebalance→sweep 调用）触发——编排器无后台线程（事件触发红线）。"""
    orch, om, clock = _make_orchestrator(timeout_seconds=5.0)
    order = _make_order(status=OrderStatus.SUBMITTED)
    _register_via_om(om, order)
    orch.track_order(order, OrderSide.BUY)
    clock.advance(4.0)
    assert orch.sweep() == []  # 未到期
    clock.advance(2.0)
    assert len(orch.sweep()) == 1  # 到期后由下一个事件（本次显式 sweep）触发
    assert orch.get_lifecycle(order.order_id).phase is SagaPhase.TERMINAL
