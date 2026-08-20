# [BLUEPRINT] MOD-EX-056 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""Repository Interface 测试——执行域仓储接口。

覆盖: OrderRepository / PositionSnapshotRepository 抽象接口 + 内存实现 + 工厂。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.repository_interface import (
    InMemoryOrderRepository,
    InMemoryPositionSnapshotRepository,
    OrderRepository,
    PositionSnapshotRepository,
    RepositoryError,
    create_order_repository,
    create_position_snapshot_repository,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot

# ──────────────────────────────────────────────────────────────────────────────
# 工厂
# ──────────────────────────────────────────────────────────────────────────────


def make_order(
    order_id: str = "ord-001",
    status: OrderStatus = OrderStatus.SUBMITTED,
    quantity: Decimal = Decimal("100"),
) -> Order:
    return Order(
        order_id=order_id,
        symbol="600000",
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("10.00"),
        status=status,
        created_at=datetime.now(UTC),
        idempotency_key="key",
    )


def make_snapshot(
    portfolio_id: str = "pf-001",
    timestamp: datetime | None = None,
    cash: Decimal = Decimal("1000000"),
    holdings: dict | None = None,
) -> PositionSnapshot:
    return PositionSnapshot(
        as_of_timestamp=timestamp or datetime.now(UTC),
        idempotency_key="snap-key",
        portfolio_id=portfolio_id,
        cash=cash,
        holdings=holdings or {"600000": Decimal("100")},
        market_values={"600000": Decimal("1000")},
        total_market_value=Decimal("1000"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# ABC 不可实例化
# ──────────────────────────────────────────────────────────────────────────────


class TestAbstract:
    def test_order_repo_abc_cannot_instantiate(self):
        with pytest.raises(TypeError):
            OrderRepository()

    def test_position_repo_abc_cannot_instantiate(self):
        with pytest.raises(TypeError):
            PositionSnapshotRepository()


# ──────────────────────────────────────────────────────────────────────────────
# InMemoryOrderRepository
# ──────────────────────────────────────────────────────────────────────────────


class TestInMemoryOrderRepository:
    def test_save_and_get(self):
        repo = InMemoryOrderRepository()
        order = make_order(order_id="ord-1")
        repo.save(order)
        assert repo.get("ord-1") is order

    def test_get_not_found(self):
        repo = InMemoryOrderRepository()
        assert repo.get("nonexistent") is None

    def test_save_overwrites(self):
        """相同 order_id save 两次，get 返回最新。"""
        repo = InMemoryOrderRepository()
        order1 = make_order(order_id="ord-1", status=OrderStatus.PENDING)
        repo.save(order1)

        order2 = make_order(order_id="ord-1", status=OrderStatus.FILLED)
        repo.save(order2)

        result = repo.get("ord-1")
        assert result is order2
        assert result.status == OrderStatus.FILLED

    def test_get_by_status(self):
        repo = InMemoryOrderRepository()
        repo.save(make_order(order_id="o1", status=OrderStatus.PENDING))
        repo.save(make_order(order_id="o2", status=OrderStatus.FILLED))
        repo.save(make_order(order_id="o3", status=OrderStatus.PENDING))

        pending = repo.get_by_status(OrderStatus.PENDING)
        assert len(pending) == 2
        filled = repo.get_by_status(OrderStatus.FILLED)
        assert len(filled) == 1

    def test_get_open_orders(self):
        repo = InMemoryOrderRepository()
        repo.save(make_order(order_id="o1", status=OrderStatus.PENDING))
        repo.save(make_order(order_id="o2", status=OrderStatus.SUBMITTED))
        repo.save(make_order(order_id="o3", status=OrderStatus.PARTIAL))
        repo.save(make_order(order_id="o4", status=OrderStatus.FILLED))
        repo.save(make_order(order_id="o5", status=OrderStatus.CANCELLED))

        open_orders = repo.get_open_orders()
        assert len(open_orders) == 3
        open_ids = {o.order_id for o in open_orders}
        assert open_ids == {"o1", "o2", "o3"}

    def test_get_all(self):
        repo = InMemoryOrderRepository()
        repo.save(make_order(order_id="o1"))
        repo.save(make_order(order_id="o2"))
        assert len(repo.get_all()) == 2

    def test_delete(self):
        repo = InMemoryOrderRepository()
        repo.save(make_order(order_id="o1"))
        assert repo.delete("o1") is True
        assert repo.get("o1") is None
        assert repo.delete("o1") is False  # 已删除

    def test_delete_not_found(self):
        repo = InMemoryOrderRepository()
        assert repo.delete("nonexistent") is False

    def test_count(self):
        repo = InMemoryOrderRepository()
        assert repo.count() == 0
        repo.save(make_order(order_id="o1"))
        repo.save(make_order(order_id="o2"))
        assert repo.count() == 2
        repo.delete("o1")
        assert repo.count() == 1

    def test_empty_repo_queries(self):
        repo = InMemoryOrderRepository()
        assert repo.get_all() == []
        assert repo.get_open_orders() == []
        assert repo.get_by_status(OrderStatus.FILLED) == []
        assert repo.count() == 0


# ──────────────────────────────────────────────────────────────────────────────
# InMemoryPositionSnapshotRepository
# ──────────────────────────────────────────────────────────────────────────────


class TestInMemoryPositionSnapshotRepository:
    def test_save_and_get_latest(self):
        repo = InMemoryPositionSnapshotRepository()
        ts = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
        snap = make_snapshot(portfolio_id="pf-1", timestamp=ts)
        repo.save(snap)
        assert repo.get_latest("pf-1") is snap

    def test_get_latest_not_found(self):
        repo = InMemoryPositionSnapshotRepository()
        assert repo.get_latest("nonexistent") is None

    def test_multiple_snapshots_latest(self):
        """多次 save，get_latest 返回时间戳最大的。"""
        repo = InMemoryPositionSnapshotRepository()
        ts1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
        ts2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=UTC)
        ts3 = datetime(2026, 1, 1, 9, 0, 0, tzinfo=UTC)  # 乱序插入

        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts1))
        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts2))
        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts3))

        latest = repo.get_latest("pf-1")
        assert latest is not None
        assert latest.as_of_timestamp == ts2  # 最晚的

    def test_get_history(self):
        repo = InMemoryPositionSnapshotRepository()
        ts1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
        ts2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=UTC)

        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts1))
        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts2))

        history = repo.get_history("pf-1")
        assert len(history) == 2
        assert history[0].as_of_timestamp == ts1  # 升序
        assert history[1].as_of_timestamp == ts2

    def test_get_history_empty(self):
        repo = InMemoryPositionSnapshotRepository()
        assert repo.get_history("nonexistent") == []

    def test_get_all_latest(self):
        """get_all 返回每个组合的最新快照。"""
        repo = InMemoryPositionSnapshotRepository()
        ts1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
        ts2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=UTC)

        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts1))
        repo.save(make_snapshot(portfolio_id="pf-1", timestamp=ts2))
        repo.save(make_snapshot(portfolio_id="pf-2", timestamp=ts1))

        all_latest = repo.get_all()
        assert len(all_latest) == 2  # 2个组合
        # pf-1 的最新是 ts2
        pf1 = [s for s in all_latest if s.portfolio_id == "pf-1"][0]
        assert pf1.as_of_timestamp == ts2

    def test_delete(self):
        repo = InMemoryPositionSnapshotRepository()
        repo.save(make_snapshot(portfolio_id="pf-1"))
        assert repo.delete("pf-1") is True
        assert repo.get_latest("pf-1") is None
        assert repo.delete("pf-1") is False

    def test_count(self):
        repo = InMemoryPositionSnapshotRepository()
        assert repo.count() == 0
        repo.save(make_snapshot(portfolio_id="pf-1"))
        repo.save(make_snapshot(portfolio_id="pf-1"))  # 同组合2个快照
        repo.save(make_snapshot(portfolio_id="pf-2"))
        assert repo.count() == 3  # 总快照数
        repo.delete("pf-1")
        assert repo.count() == 1  # 只剩 pf-2 的1个

    def test_empty_repo_queries(self):
        repo = InMemoryPositionSnapshotRepository()
        assert repo.get_all() == []
        assert repo.get_history("x") == []
        assert repo.count() == 0


# ──────────────────────────────────────────────────────────────────────────────
# 工厂函数
# ──────────────────────────────────────────────────────────────────────────────


class TestFactory:
    def test_create_order_repository_memory(self):
        repo = create_order_repository("memory")
        assert isinstance(repo, InMemoryOrderRepository)
        assert isinstance(repo, OrderRepository)

    def test_create_position_repository_memory(self):
        repo = create_position_snapshot_repository("memory")
        assert isinstance(repo, InMemoryPositionSnapshotRepository)
        assert isinstance(repo, PositionSnapshotRepository)

    def test_create_order_repository_default(self):
        repo = create_order_repository()
        assert isinstance(repo, InMemoryOrderRepository)

    def test_create_position_repository_default(self):
        repo = create_position_snapshot_repository()
        assert isinstance(repo, InMemoryPositionSnapshotRepository)

    def test_create_order_repository_unsupported(self):
        with pytest.raises(RepositoryError):
            create_order_repository("postgres")

    def test_create_position_repository_unsupported(self):
        with pytest.raises(RepositoryError):
            create_position_snapshot_repository("sqlite")


# ──────────────────────────────────────────────────────────────────────────────
# 集成场景
# ──────────────────────────────────────────────────────────────────────────────


class TestIntegration:
    def test_order_lifecycle_with_repository(self):
        """模拟订单生命周期：创建→提交→部分成交→全部成交，仓储全程跟踪。"""
        repo = InMemoryOrderRepository()

        # 创建
        order = make_order(order_id="life-1", status=OrderStatus.PENDING)
        repo.save(order)
        assert repo.count() == 1
        assert len(repo.get_open_orders()) == 1

        # 提交
        order.status = OrderStatus.SUBMITTED
        repo.save(order)
        assert len(repo.get_open_orders()) == 1

        # 部分成交
        order.status = OrderStatus.PARTIAL
        order.filled_quantity = Decimal("30")
        repo.save(order)
        assert len(repo.get_open_orders()) == 1
        assert len(repo.get_by_status(OrderStatus.PARTIAL)) == 1

        # 全部成交
        order.status = OrderStatus.FILLED
        order.filled_quantity = Decimal("100")
        repo.save(order)
        assert len(repo.get_open_orders()) == 0
        assert len(repo.get_by_status(OrderStatus.FILLED)) == 1

    def test_position_snapshot_history(self):
        """模拟持仓快照历史：3个时间点的快照，查询最新和历史。"""
        repo = InMemoryPositionSnapshotRepository()

        # 3个时间点的快照
        for hour in range(10, 13):
            ts = datetime(2026, 1, 1, hour, 0, 0, tzinfo=UTC)
            snap = make_snapshot(
                portfolio_id="pf-1",
                timestamp=ts,
                cash=Decimal(1_000_000 - hour * 1000),
            )
            repo.save(snap)

        assert repo.count() == 3
        latest = repo.get_latest("pf-1")
        assert latest is not None
        assert latest.cash == Decimal("988000")  # 12点 = 1000000-12*1000

        history = repo.get_history("pf-1")
        assert len(history) == 3
        # 升序
        assert history[0].as_of_timestamp.hour == 10
        assert history[2].as_of_timestamp.hour == 12
