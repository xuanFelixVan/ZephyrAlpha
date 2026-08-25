# [BLUEPRINT] MOD-TRADING-009 | docs/03_modules/_domain_trading/trading_order_aggregate/blueprint.md
# [MODULE] tests.trading.test_trading_order_aggregate
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_order_aggregate
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-TRADING-009 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-009 TradingOrder 订单核心聚合（AGG-TRD-01）单元测试.

覆盖: 注册/幂等键复用/order_id冲突Fail-Closed/运营状态机全链路/非法转换/
终态拒绝/领域事件发布(event_sink)/事件溯源append-only/sink异常不阻断/
输入校验(空order_id/非正数量).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.trading.trading_order_aggregate import (
    DuplicateOrderIdError,
    InvalidOrderTransitionError,
    InvalidTradingOrderInputError,
    OrderDomainEvent,
    TradingOrderBook,
    TradingOrderStatus,
)

TS = "2026-08-25T15:30:00+08:00"


def _book(sink=None) -> TradingOrderBook:
    return TradingOrderBook(event_sink=sink)


def _register(book: TradingOrderBook, order_id: str = "ORD-1", idem: str = "IDEM-1"):
    return book.register(
        order_id=order_id,
        idempotency_key=idem,
        symbol="600519.SH",
        side="BUY",
        quantity=Decimal("100"),
    )


class TestRegister:
    def test_register_initial_state(self):
        book = _book()
        order = _register(book)
        assert order.order_id == "ORD-1"
        assert order.status is TradingOrderStatus.RECEIVED
        assert order.events == ()

    def test_register_idempotent_same_key_returns_existing(self):
        book = _book()
        first = _register(book)
        book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)
        again = _register(book)
        assert again.order_id == first.order_id
        # 幂等命中返回既有聚合，不回退状态
        assert again.status is TradingOrderStatus.DISPATCHED

    def test_register_duplicate_order_id_different_key_fail_closed(self):
        book = _book()
        _register(book)
        with pytest.raises(DuplicateOrderIdError):
            _register(book, order_id="ORD-1", idem="IDEM-OTHER")

    def test_register_invalid_input(self):
        book = _book()
        with pytest.raises(InvalidTradingOrderInputError):
            book.register(
                order_id="",
                idempotency_key="IDEM-1",
                symbol="600519.SH",
                side="BUY",
                quantity=Decimal("100"),
            )
        with pytest.raises(InvalidTradingOrderInputError):
            book.register(
                order_id="ORD-2",
                idempotency_key="IDEM-2",
                symbol="600519.SH",
                side="BUY",
                quantity=Decimal("0"),
            )


class TestStateMachine:
    def test_happy_path_full_lifecycle(self):
        book = _book()
        _register(book)
        for target in (
            TradingOrderStatus.DISPATCHED,
            TradingOrderStatus.EXECUTING,
            TradingOrderStatus.FILLED,
            TradingOrderStatus.SETTLING,
            TradingOrderStatus.SETTLED,
            TradingOrderStatus.RECONCILED,
        ):
            order = book.transition("ORD-1", target, TS)
        assert order.status is TradingOrderStatus.RECONCILED
        assert len(order.events) == 6

    def test_illegal_transition_fail_closed(self):
        book = _book()
        _register(book)
        with pytest.raises(InvalidOrderTransitionError):
            book.transition("ORD-1", TradingOrderStatus.SETTLED, TS)

    def test_terminal_status_rejects_further_transition(self):
        book = _book()
        _register(book)
        book.transition("ORD-1", TradingOrderStatus.CANCELLED, TS)
        with pytest.raises(InvalidOrderTransitionError):
            book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)

    def test_branch_rejected_from_received(self):
        book = _book()
        _register(book)
        order = book.transition("ORD-1", TradingOrderStatus.REJECTED, TS)
        assert order.status is TradingOrderStatus.REJECTED

    def test_cancelled_from_executing(self):
        book = _book()
        _register(book)
        book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)
        book.transition("ORD-1", TradingOrderStatus.EXECUTING, TS)
        order = book.transition("ORD-1", TradingOrderStatus.CANCELLED, TS)
        assert order.status is TradingOrderStatus.CANCELLED

    def test_transition_unknown_order_fail_closed(self):
        book = _book()
        with pytest.raises(InvalidTradingOrderInputError):
            book.transition("ORD-NONE", TradingOrderStatus.DISPATCHED, TS)


class TestDomainEvents:
    def test_event_published_to_sink(self):
        seen: list[OrderDomainEvent] = []
        book = _book(sink=seen.append)
        _register(book)
        book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS, note="派出")
        assert len(seen) == 1
        event = seen[0]
        assert event.order_id == "ORD-1"
        assert event.from_status is TradingOrderStatus.RECEIVED
        assert event.to_status is TradingOrderStatus.DISPATCHED
        assert event.occurred_at == TS

    def test_events_append_only_replay(self):
        book = _book()
        _register(book)
        book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)
        book.transition("ORD-1", TradingOrderStatus.EXECUTING, TS)
        events = book.events_of("ORD-1")
        assert [e.to_status for e in events] == [
            TradingOrderStatus.DISPATCHED,
            TradingOrderStatus.EXECUTING,
        ]
        # 事件溯源: 回放可重建状态
        assert events[-1].to_status is TradingOrderStatus.EXECUTING

    def test_sink_exception_does_not_block(self):
        def _boom(_event):
            raise RuntimeError("sink down")

        book = _book(sink=_boom)
        _register(book)
        order = book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)
        assert order.status is TradingOrderStatus.DISPATCHED
        assert len(order.events) == 1

    def test_event_immutable(self):
        book = _book()
        _register(book)
        order = book.transition("ORD-1", TradingOrderStatus.DISPATCHED, TS)
        with pytest.raises(AttributeError):
            order.events[0].to_status = TradingOrderStatus.FILLED  # type: ignore[misc]
