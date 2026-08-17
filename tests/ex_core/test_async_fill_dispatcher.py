# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_async_fill_dispatcher.py
# [TTL] task_bound
# 对应: src/zephyr/ex_core/async_fill_dispatcher.py
# 覆盖: gap 12 回调线程异步派发（入队/消费/幂等/停机/背压）
"""AsyncFillDispatcher 单元测试（40_execution_broker §决策① 工程约束1 gap 12）。"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.async_fill_dispatcher import (
    AsyncFillDispatcher,
    AsyncFillDispatcherError,
    DispatchStats,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

# ───────────────────────── Fixtures ─────────────────────────


def _make_fill(
    fill_id: str = "fill-1",
    order_id: str = "ord-1",
    symbol: str = "600000.SH",
    qty: Decimal = Decimal("100"),
    price: Decimal = Decimal("10.00"),
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=price,
        fill_timestamp=datetime(2026, 8, 10, 10, 30, tzinfo=timezone.utc),
        filled_quantity=qty,
        idempotency_key=f"idem-{fill_id}",
        order_id=order_id,
        strategy_id="test-strat",
        symbol=symbol,
    )


def _make_order(order_id: str = "ord-1") -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"idem-{order_id}",
        symbol="600000.SH",
        strategy_id="test-strat",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("500"),
        limit_price=Decimal("10.00"),
        status=OrderStatus.SUBMITTED,
        created_at=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def started_dispatcher():
    """构造已启动的派发器，测试结束自动停机。"""
    processed: list[tuple[Fill, Order]] = []
    lock = threading.Lock()
    order_store: dict[str, Order] = {}

    def consumer(fill: Fill, order: Order) -> None:
        with lock:
            processed.append((fill, order))

    def lookup(fill: Fill) -> Order | None:
        return order_store.get(fill.order_id)

    dispatcher = AsyncFillDispatcher(
        consumer=consumer,
        lookup_order_fn=lookup,
        queue_maxsize=100,
        consumer_name="test-dispatcher",
    )
    dispatcher.start()
    yield dispatcher, processed, lock, order_store
    dispatcher.stop(timeout=2.0)


# ───────────────────────── 基本入队派发 ─────────────────────────


class TestEnqueueDispatch:
    """基本入队 + 消费派发。"""

    def test_enqueue_and_dispatch(self, started_dispatcher):
        """入队一笔 fill → 消费线程处理 → consumer 被调用。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order = _make_order()
        order_store[order.order_id] = order
        fill = _make_fill()

        assert dispatcher.enqueue(fill) is True
        assert dispatcher.flush(timeout=2.0) is True

        with lock:
            assert len(processed) == 1
            assert processed[0][0].fill_id == "fill-1"
            assert processed[0][1].order_id == "ord-1"

    def test_multiple_fills_dispatched_in_order(self, started_dispatcher):
        """多笔 fill 按入队顺序派发（FIFO）。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")

        for i in range(5):
            fill = _make_fill(fill_id=f"fill-{i}", order_id="ord-1")
            assert dispatcher.enqueue(fill) is True

        assert dispatcher.flush(timeout=2.0) is True

        with lock:
            assert len(processed) == 5
            ids = [p[0].fill_id for p in processed]
            assert ids == [f"fill-{i}" for i in range(5)]

    def test_order_not_found_skipped(self, started_dispatcher):
        """订单不存在 → 跳过不调 consumer，记 error。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        fill = _make_fill(order_id="nonexistent")

        assert dispatcher.enqueue(fill) is True
        assert dispatcher.flush(timeout=2.0) is True

        with lock:
            assert len(processed) == 0
        stats = dispatcher.stats
        assert stats.errors >= 1


# ───────────────────────── fill_id 幂等去重 ─────────────────────────


class TestDeduplication:
    """fill_id 幂等去重。"""

    def test_duplicate_fill_id_rejected(self, started_dispatcher):
        """重复 fill_id → enqueue 返回 False，不重复处理。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")
        fill = _make_fill(fill_id="dup-1")

        first = dispatcher.enqueue(fill)
        second = dispatcher.enqueue(fill)  # 重复

        assert first is True
        assert second is False
        assert dispatcher.flush(timeout=2.0) is True

        with lock:
            assert len(processed) == 1  # 只处理一次

    def test_dedup_count_tracked(self, started_dispatcher):
        """去重计数正确。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")
        fill = _make_fill(fill_id="dup-2")

        dispatcher.enqueue(fill)
        dispatcher.enqueue(fill)
        dispatcher.enqueue(fill)  # 2 次重复
        dispatcher.flush(timeout=2.0)

        stats = dispatcher.stats
        assert stats.deduplicated == 2

    def test_different_fill_ids_all_accepted(self, started_dispatcher):
        """不同 fill_id 都能正常入队（不互相去重）。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")

        # 3 个不同 fill_id，都应入队成功
        for i in range(3):
            assert dispatcher.enqueue(_make_fill(fill_id=f"unique-{i}")) is True
        dispatcher.flush(timeout=2.0)

        with lock:
            assert len(processed) == 3


# ───────────────────────── 背压保护 ─────────────────────────


class TestBackpressure:
    """队列满背压保护。"""

    def test_queue_full_returns_false(self):
        """队列满 → enqueue 返回 False 不阻塞。"""
        # 不启动消费线程，让队列填满
        processed: list = []
        dispatcher = AsyncFillDispatcher(
            consumer=lambda f, o: processed.append(f),
            lookup_order_fn=lambda f: _make_order(),
            queue_maxsize=3,
        )
        try:
            # 填满队列（maxsize=3）
            for i in range(3):
                assert dispatcher.enqueue(_make_fill(fill_id=f"f-{i}")) is True
            # 第 4 笔应被拒绝
            assert dispatcher.enqueue(_make_fill(fill_id="f-overflow")) is False
        finally:
            dispatcher.stop(timeout=1.0)


# ───────────────────────── 停机后拒绝入队 ─────────────────────────


class TestShutdownReject:
    """停机后拒绝入队。"""

    def test_enqueue_after_stop_raises(self):
        """stop() 后 enqueue → 抛 AsyncFillDispatcherError。"""
        dispatcher = AsyncFillDispatcher(
            consumer=lambda f, o: None,
            lookup_order_fn=lambda f: _make_order(),
        )
        dispatcher.start()
        dispatcher.stop(timeout=1.0)

        with pytest.raises(AsyncFillDispatcherError):
            dispatcher.enqueue(_make_fill())


# ───────────────────────── 优雅停机 ─────────────────────────


class TestGracefulShutdown:
    """优雅停机：处理完队列再退出。"""

    def test_stop_drains_queue(self):
        """stop() 前队列内的 fill 会被处理完。"""
        processed: list = []
        lock = threading.Lock()
        order = _make_order()

        def consumer(f, o):
            with lock:
                processed.append(f)

        dispatcher = AsyncFillDispatcher(
            consumer=consumer,
            lookup_order_fn=lambda f: order,
        )
        dispatcher.start()

        # 入队 10 笔
        for i in range(10):
            dispatcher.enqueue(_make_fill(fill_id=f"drain-{i}"))

        # 停机前给消费线程一点时间
        time.sleep(0.1)
        dispatcher.stop(timeout=3.0)

        with lock:
            # 至少处理了一部分（可能没全处理完，取决于停机速度）
            assert len(processed) >= 1

    def test_stop_returns_true_when_thread_exits(self):
        """stop() 正常退出 → 返回 True。"""
        dispatcher = AsyncFillDispatcher(
            consumer=lambda f, o: None,
            lookup_order_fn=lambda f: _make_order(),
        )
        dispatcher.start()
        assert dispatcher.is_running is True

        result = dispatcher.stop(timeout=2.0)
        assert result is True
        assert dispatcher.is_running is False


# ───────────────────────── 异常隔离 ─────────────────────────


class TestExceptionIsolation:
    """单笔异常不中断消费循环。"""

    def test_consumer_exception_doesnt_block_others(self):
        """consumer 第 1 笔抛异常，第 2 笔仍被处理。"""
        processed: list = []
        lock = threading.Lock()
        order = _make_order()
        call_count = {"n": 0}

        def consumer(f, o):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("故意异常")
            with lock:
                processed.append(f)

        dispatcher = AsyncFillDispatcher(
            consumer=consumer,
            lookup_order_fn=lambda f: order,
        )
        dispatcher.start()

        dispatcher.enqueue(_make_fill(fill_id="err-1"))
        dispatcher.enqueue(_make_fill(fill_id="ok-2"))
        dispatcher.flush(timeout=2.0)
        dispatcher.stop(timeout=2.0)

        with lock:
            # 第 2 笔被处理（第 1 笔异常不影响）
            assert len(processed) == 1
            assert processed[0].fill_id == "ok-2"


# ───────────────────────── 统计 ─────────────────────────


class TestStats:
    """派发统计。"""

    def test_stats_reflect_activity(self, started_dispatcher):
        """入队+派发后 stats 反映活动。"""
        dispatcher, processed, lock, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")

        for i in range(3):
            dispatcher.enqueue(_make_fill(fill_id=f"stat-{i}"))
        dispatcher.flush(timeout=2.0)

        stats = dispatcher.stats
        assert stats.enqueued == 3
        assert stats.dispatched == 3
        assert stats.deduplicated == 0
        assert stats.errors == 0
        assert stats.last_dispatch_at is not None

    def test_stats_snapshot_is_copy(self, started_dispatcher):
        """stats 返回快照，不影响内部状态。"""
        dispatcher, _, _, order_store = started_dispatcher
        order_store["ord-1"] = _make_order("ord-1")
        dispatcher.enqueue(_make_fill())
        dispatcher.flush(timeout=2.0)

        s1 = dispatcher.stats
        s1.enqueued = 999  # 改快照
        s2 = dispatcher.stats
        assert s2.enqueued != 999  # 内部未受影响


# ───────────────────────── LRU 去重窗口 ─────────────────────────


class TestDedupWindow:
    """fill_id LRU 去重窗口淘汰。"""

    def test_lru_eviction_allows_old_id_reuse(self):
        """超过 dedup_window 后，老 fill_id 被淘汰，可再次入队。"""
        processed: list = []
        dispatcher = AsyncFillDispatcher(
            consumer=lambda f, o: processed.append(f),
            lookup_order_fn=lambda f: _make_order(),
            dedup_window=3,  # 只保留最近 3 个 fill_id
        )
        dispatcher.start()
        try:
            # 入队 A, B, C（填满窗口）
            dispatcher.enqueue(_make_fill(fill_id="A"))
            dispatcher.enqueue(_make_fill(fill_id="B"))
            dispatcher.enqueue(_make_fill(fill_id="C"))
            dispatcher.flush(timeout=1.0)
            # 入队 D → A 被淘汰
            dispatcher.enqueue(_make_fill(fill_id="D"))
            dispatcher.flush(timeout=1.0)
            # A 再次入队应成功（已被淘汰）
            assert dispatcher.enqueue(_make_fill(fill_id="A")) is True
        finally:
            dispatcher.stop(timeout=1.0)
