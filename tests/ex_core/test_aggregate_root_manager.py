# [BLUEPRINT] MOD-EX-049 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""Aggregate Root Manager 测试——执行域聚合根管理器。

覆盖: 订单创建/成交全链路/状态查询/持仓快照/开放订单/Facade协调行为。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.aggregate_root_manager import (
    AggregateManagerError,
    ExecutionAggregateManager,
    OrderState,
)
from zephyr.ex_core.fill_handler import FillHandler
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.repository_interface import (
    InMemoryOrderRepository,
    InMemoryPositionSnapshotRepository,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill

# ──────────────────────────────────────────────────────────────────────────────
# 工厂
# ──────────────────────────────────────────────────────────────────────────────


def make_fill(
    fill_id: str = "fill-1",
    order_id: str = "ord-1",
    symbol: str = "600000",
    qty: Decimal = Decimal("100"),
    price: Decimal = Decimal("10.00"),
    commission: Decimal = Decimal("5"),
    strategy_id: str = "test",
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key="key",
        order_id=order_id,
        strategy_id=strategy_id,
        symbol=symbol,
        commission=commission,
    )


def make_manager(
    initial_cash: Decimal = Decimal("1000000"),
    with_snapshot_repo: bool = False,
    fill_handler: FillHandler | None = None,
) -> ExecutionAggregateManager:
    return ExecutionAggregateManager(
        order_repo=InMemoryOrderRepository(),
        position_tracker=PositionTracker(initial_cash=initial_cash),
        fill_handler=fill_handler,
        position_snapshot_repo=(InMemoryPositionSnapshotRepository() if with_snapshot_repo else None),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 创建订单
# ──────────────────────────────────────────────────────────────────────────────


class TestCreateOrder:
    def test_create_order_persists(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        assert mgr.get_order(order.order_id) is order

    def test_create_order_fields(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "strat-1",
            OrderSide.SELL,
            OrderType.MARKET,
            Decimal("200"),
        )
        assert order.symbol == "600000"
        assert order.strategy_id == "strat-1"
        assert order.side == OrderSide.SELL
        assert order.order_type == OrderType.MARKET
        assert order.quantity == Decimal("200")
        assert order.limit_price is None
        assert order.status == OrderStatus.PENDING
        assert order.created_at is not None
        assert order.idempotency_key != ""

    def test_create_order_unique_ids(self):
        mgr = make_manager()
        o1 = mgr.create_order("600000", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        o2 = mgr.create_order("600000", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        assert o1.order_id != o2.order_id
        assert o1.idempotency_key != o2.idempotency_key

    def test_repo_count_increments(self):
        mgr = make_manager()
        assert mgr._order_repo.count() == 0
        mgr.create_order("600000", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        mgr.create_order("600001", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        assert mgr._order_repo.count() == 2


# ──────────────────────────────────────────────────────────────────────────────
# 成交全链路
# ──────────────────────────────────────────────────────────────────────────────


class TestProcessFill:
    def test_full_chain_single_fill(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        fill = make_fill(
            order_id=order.order_id,
            qty=Decimal("100"),
            price=Decimal("10.00"),
            commission=Decimal("5"),
        )

        summary = mgr.process_fill(fill, order)

        assert summary.is_complete is True
        assert order.filled_quantity == Decimal("100")
        assert order.status == OrderStatus.FILLED
        # 持仓更新
        snap = mgr.get_position_snapshot()
        assert snap.holdings["600000"] == Decimal("100")
        # 现金: 1000000 - 100*10 - 5 = 998995
        assert snap.cash == Decimal("998995")
        # 持久化（仓储里的订单状态已更新）
        assert mgr.get_order(order.order_id).status == OrderStatus.FILLED

    def test_partial_then_complete(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED

        f1 = make_fill(
            fill_id="f1",
            order_id=order.order_id,
            qty=Decimal("30"),
            price=Decimal("10.00"),
        )
        s1 = mgr.process_fill(f1, order)
        assert s1.is_complete is False
        assert order.status == OrderStatus.PARTIAL
        assert order.filled_quantity == Decimal("30")

        f2 = make_fill(
            fill_id="f2",
            order_id=order.order_id,
            qty=Decimal("70"),
            price=Decimal("11.00"),
        )
        s2 = mgr.process_fill(f2, order)
        assert s2.is_complete is True
        assert order.status == OrderStatus.FILLED
        # 加权均价: (30*10 + 70*11)/100 = 1070/100 = 10.70
        assert order.avg_fill_price == Decimal("10.70")

    def test_three_fills_accumulation(self):
        """蓝图 §8 用例：3笔fill → order FILLED + position 正确。"""
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED

        mgr.process_fill(
            make_fill(fill_id="f1", order_id=order.order_id, qty=Decimal("30"), price=Decimal("10.00")),
            order,
        )
        mgr.process_fill(
            make_fill(fill_id="f2", order_id=order.order_id, qty=Decimal("50"), price=Decimal("11.00")),
            order,
        )
        s3 = mgr.process_fill(
            make_fill(fill_id="f3", order_id=order.order_id, qty=Decimal("20"), price=Decimal("12.00")),
            order,
        )

        assert s3.is_complete is True
        assert order.status == OrderStatus.FILLED
        # (30*10 + 50*11 + 20*12)/100 = 1090/100 = 10.90
        assert order.avg_fill_price == Decimal("10.90")
        assert mgr.get_position_snapshot().holdings["600000"] == Decimal("100")

    def test_sell_fill_updates_cash(self):
        mgr = make_manager(initial_cash=Decimal("1000000"))
        # 先买入 100 股 @10（佣金5）
        buy = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        buy.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(fill_id="b1", order_id=buy.order_id, qty=Decimal("100"), price=Decimal("10.00")),
            buy,
        )
        # 卖出 60 股 @11（佣金5）
        sell = mgr.create_order(
            "600000",
            "test",
            OrderSide.SELL,
            OrderType.LIMIT,
            Decimal("60"),
            Decimal("11.00"),
        )
        sell.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(fill_id="s1", order_id=sell.order_id, qty=Decimal("60"), price=Decimal("11.00")),
            sell,
        )

        snap = mgr.get_position_snapshot()
        assert snap.holdings["600000"] == Decimal("40")  # 100-60
        # 现金: 1000000 - 1000 - 5 + 660 - 5 = 999650
        assert snap.cash == Decimal("999650")

    def test_process_fill_persists_order(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(make_fill(order_id=order.order_id, qty=Decimal("50")), order)

        stored = mgr.get_order(order.order_id)
        assert stored.filled_quantity == Decimal("50")
        assert stored.status == OrderStatus.PARTIAL

    def test_process_fill_returns_summary(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        summary = mgr.process_fill(
            make_fill(order_id=order.order_id, qty=Decimal("40"), price=Decimal("10.50"), commission=Decimal("3")),
            order,
        )
        assert summary.order_id == order.order_id
        assert summary.filled_quantity == Decimal("40")
        assert summary.remaining_quantity == Decimal("60")
        assert summary.avg_fill_price == Decimal("10.50")
        assert summary.total_commission == Decimal("3")
        assert summary.fill_count == 1


# ──────────────────────────────────────────────────────────────────────────────
# 订单状态查询
# ──────────────────────────────────────────────────────────────────────────────


class TestOrderStateQuery:
    def test_get_order_state_with_fill(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(make_fill(order_id=order.order_id, qty=Decimal("30")), order)

        state = mgr.get_order_state(order.order_id)
        assert isinstance(state, OrderState)
        assert state.order is order
        assert state.fill_summary is not None
        assert state.fill_summary.filled_quantity == Decimal("30")

    def test_get_order_state_no_fill(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        state = mgr.get_order_state(order.order_id)
        assert state is not None
        assert state.order is order
        assert state.fill_summary is None

    def test_get_order_state_unknown_returns_none(self):
        """蓝图 §8 用例：未知订单查询返回 None。"""
        mgr = make_manager()
        assert mgr.get_order_state("does-not-exist") is None

    def test_order_state_is_frozen(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(make_fill(order_id=order.order_id, qty=Decimal("30")), order)
        state = mgr.get_order_state(order.order_id)
        with pytest.raises(Exception):
            state.fill_summary = None  # type: ignore[misc]  # frozen dataclass


# ──────────────────────────────────────────────────────────────────────────────
# 持仓快照
# ──────────────────────────────────────────────────────────────────────────────


class TestPositionSnapshot:
    def test_get_position_snapshot(self):
        """蓝图 §8 用例：持仓快照查询返回正确 holdings/cash。"""
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(order_id=order.order_id, qty=Decimal("100"), price=Decimal("10.00")),
            order,
        )

        snap = mgr.get_position_snapshot()
        assert snap.holdings["600000"] == Decimal("100")
        assert snap.cash == Decimal("998995")
        assert snap.total_market_value == Decimal("1000")  # 100 * 10 (avg_cost)

    def test_save_position_snapshot_persists(self):
        """蓝图 §8 用例：持仓快照持久化 → position_repo 有记录。"""
        mgr = make_manager(with_snapshot_repo=True)
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(order_id=order.order_id, qty=Decimal("100"), price=Decimal("10.00")),
            order,
        )

        snap = mgr.save_position_snapshot()
        latest = mgr._position_snapshot_repo.get_latest(snap.portfolio_id)
        assert latest is snap
        assert mgr._position_snapshot_repo.count() == 1

    def test_save_position_snapshot_without_repo_raises(self):
        mgr = make_manager(with_snapshot_repo=False)
        with pytest.raises(AggregateManagerError):
            mgr.save_position_snapshot()

    def test_save_multiple_snapshots_history(self):
        mgr = make_manager(with_snapshot_repo=True)
        s1 = mgr.save_position_snapshot()
        s2 = mgr.save_position_snapshot()
        history = mgr._position_snapshot_repo.get_history(s1.portfolio_id)
        assert len(history) == 2
        assert history[0] is s1
        assert history[1] is s2


# ──────────────────────────────────────────────────────────────────────────────
# 开放订单
# ──────────────────────────────────────────────────────────────────────────────


class TestOpenOrders:
    def test_get_open_orders_filters(self):
        """蓝图 §8 用例：开放订单查询过滤正确。"""
        mgr = make_manager()
        o1 = mgr.create_order("600000", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        o2 = mgr.create_order("600001", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))
        o3 = mgr.create_order("600002", "s", OrderSide.BUY, OrderType.LIMIT, Decimal("10"))

        # o1 提交（SUBMITTED），o2 待提交（PENDING），o3 已成交（FILLED）
        o1.status = OrderStatus.SUBMITTED
        o3.status = OrderStatus.FILLED
        mgr._order_repo.save(o1)
        mgr._order_repo.save(o3)

        opens = mgr.get_open_orders()
        ids = {o.order_id for o in opens}
        assert o1.order_id in ids  # SUBMITTED
        assert o2.order_id in ids  # PENDING
        assert o3.order_id not in ids  # FILLED 不开放

    def test_get_open_orders_empty(self):
        mgr = make_manager()
        assert mgr.get_open_orders() == []

    def test_get_open_orders_after_fill(self):
        mgr = make_manager()
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(order_id=order.order_id, qty=Decimal("100"), price=Decimal("10.00")),
            order,
        )
        # 完全成交后不再开放
        assert mgr.get_open_orders() == []


# ──────────────────────────────────────────────────────────────────────────────
# Facade 行为
# ──────────────────────────────────────────────────────────────────────────────


class TestFacadeBehavior:
    def test_default_fill_handler_created(self):
        """不注入 fill_handler，内部应自动创建可用实例。"""
        mgr = make_manager(fill_handler=None)
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        summary = mgr.process_fill(
            make_fill(order_id=order.order_id, qty=Decimal("100")),
            order,
        )
        assert summary.is_complete is True

    def test_injected_fill_handler_shared(self):
        """注入共享的 fill_handler，成交记录对双方可见。"""
        shared = FillHandler()
        mgr = make_manager(fill_handler=shared)
        order = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        order.status = OrderStatus.SUBMITTED
        mgr.process_fill(make_fill(order_id=order.order_id, qty=Decimal("100")), order)
        # 共享 handler 应能查到 summary 和成交历史
        assert shared.get_summary(order.order_id) is not None
        assert len(shared.get_fills(order.order_id)) == 1

    def test_get_order_unknown_returns_none(self):
        mgr = make_manager()
        assert mgr.get_order("nope") is None

    def test_two_orders_independent_positions(self):
        """两笔不同标的的订单，持仓互不干扰。"""
        mgr = make_manager()
        o1 = mgr.create_order(
            "600000",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("100"),
            Decimal("10.00"),
        )
        o1.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(fill_id="f1", order_id=o1.order_id, symbol="600000", qty=Decimal("100"), price=Decimal("10.00")),
            o1,
        )
        o2 = mgr.create_order(
            "600001",
            "test",
            OrderSide.BUY,
            OrderType.LIMIT,
            Decimal("50"),
            Decimal("20.00"),
        )
        o2.status = OrderStatus.SUBMITTED
        mgr.process_fill(
            make_fill(fill_id="f2", order_id=o2.order_id, symbol="600001", qty=Decimal("50"), price=Decimal("20.00")),
            o2,
        )

        snap = mgr.get_position_snapshot()
        assert snap.holdings["600000"] == Decimal("100")
        assert snap.holdings["600001"] == Decimal("50")
        # 现金: 1000000 - 100*10 - 5 - 50*20 - 5 = 1000000 - 1000 - 5 - 1000 - 5 = 997990
        assert snap.cash == Decimal("997990")
