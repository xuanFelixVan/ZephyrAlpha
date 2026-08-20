# [BLUEPRINT] MOD-EX-056 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""FillHandler 测试——部分成交处理器。

覆盖: 单笔/多笔成交累积、加权均价、状态转换、幂等、佣金、查询、回调、异常。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.fill_handler import (
    DuplicateFillError,
    FillHandler,
    FillSummary,
    InvalidFillError,
    OrderNotFoundError,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

# ──────────────────────────────────────────────────────────────────────────────
# 工厂
# ──────────────────────────────────────────────────────────────────────────────


def make_order(
    order_id: str = "ord-001",
    symbol: str = "600000",
    quantity: Decimal = Decimal("100"),
    side: OrderSide = OrderSide.BUY,
    status: OrderStatus = OrderStatus.SUBMITTED,
) -> Order:
    """创建测试用 Order（CTR-004）。"""
    return Order(
        order_id=order_id,
        symbol=symbol,
        strategy_id="test-strategy",
        side=side,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("10.00"),
        status=status,
        created_at=datetime.now(UTC),
        idempotency_key="test-key",
    )


def make_fill(
    fill_id: str = "fill-001",
    order_id: str = "ord-001",
    price: Decimal = Decimal("10.00"),
    qty: Decimal = Decimal("100"),
    commission: Decimal = Decimal("5.00"),
    timestamp: datetime | None = None,
) -> Fill:
    """创建测试用 Fill（CTR-005）。"""
    return Fill(
        fill_id=fill_id,
        fill_price=price,
        fill_timestamp=timestamp or datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key="fill-key",
        order_id=order_id,
        strategy_id="test-strategy",
        symbol="600000",
        commission=commission,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 配置 / 构造
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruct:
    def test_empty_handler(self):
        handler = FillHandler()
        assert handler.order_count == 0
        assert handler.total_fill_count == 0

    def test_get_summary_none_for_unknown(self):
        handler = FillHandler()
        assert handler.get_summary("unknown") is None

    def test_get_fills_empty_for_unknown(self):
        handler = FillHandler()
        assert handler.get_fills("unknown") == []

    def test_get_remaining_none_for_unknown(self):
        handler = FillHandler()
        assert handler.get_remaining("unknown") is None


# ──────────────────────────────────────────────────────────────────────────────
# 单笔成交
# ──────────────────────────────────────────────────────────────────────────────


class TestSingleFill:
    def test_single_fill_complete(self):
        """单笔全部成交 → FILLED。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(qty=Decimal("100"), price=Decimal("10.00"))

        summary = handler.process_fill(fill, order)

        assert summary.is_complete is True
        assert summary.filled_quantity == Decimal("100")
        assert summary.remaining_quantity == Decimal("0")
        assert summary.avg_fill_price == Decimal("10.00")
        assert summary.fill_count == 1
        assert summary.total_commission == Decimal("5.00")
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == Decimal("100")
        assert order.avg_fill_price == Decimal("10.00")

    def test_single_partial_fill(self):
        """单笔部分成交 → PARTIAL。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(qty=Decimal("30"), price=Decimal("10.00"))

        summary = handler.process_fill(fill, order)

        assert summary.is_complete is False
        assert summary.filled_quantity == Decimal("30")
        assert summary.remaining_quantity == Decimal("70")
        assert summary.avg_fill_price == Decimal("10.00")
        assert summary.fill_count == 1
        assert order.status == OrderStatus.PARTIAL

    def test_fill_updates_order_in_place(self):
        """process_fill 就地修改 order 字段。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        assert order.filled_quantity == Decimal("0")
        assert order.avg_fill_price is None

        handler.process_fill(make_fill(qty=Decimal("50"), price=Decimal("10.00")), order)

        assert order.filled_quantity == Decimal("50")
        assert order.avg_fill_price == Decimal("10.00")
        assert order.updated_at is not None


# ──────────────────────────────────────────────────────────────────────────────
# 多笔成交
# ──────────────────────────────────────────────────────────────────────────────


class TestMultipleFills:
    def test_two_partial_fills_then_complete(self):
        """3笔成交: 30 + 50 + 20 = 100 → FILLED。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        # 第1笔: 30 @ 10.00
        s1 = handler.process_fill(
            make_fill(fill_id="f1", qty=Decimal("30"), price=Decimal("10.00")),
            order,
        )
        assert s1.filled_quantity == Decimal("30")
        assert s1.remaining_quantity == Decimal("70")
        assert order.status == OrderStatus.PARTIAL

        # 第2笔: 50 @ 11.00
        s2 = handler.process_fill(
            make_fill(fill_id="f2", qty=Decimal("50"), price=Decimal("11.00")),
            order,
        )
        assert s2.filled_quantity == Decimal("80")
        assert s2.remaining_quantity == Decimal("20")
        assert order.status == OrderStatus.PARTIAL

        # 第3笔: 20 @ 12.00 → 全部成交
        s3 = handler.process_fill(
            make_fill(fill_id="f3", qty=Decimal("20"), price=Decimal("12.00")),
            order,
        )
        assert s3.filled_quantity == Decimal("100")
        assert s3.remaining_quantity == Decimal("0")
        assert s3.is_complete is True
        assert order.status == OrderStatus.FILLED

    def test_weighted_average_price(self):
        """加权均价: (10×30 + 11×50 + 12×20) / 100 = 10.90。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(
            make_fill(fill_id="f1", qty=Decimal("30"), price=Decimal("10.00")),
            order,
        )
        handler.process_fill(
            make_fill(fill_id="f2", qty=Decimal("50"), price=Decimal("11.00")),
            order,
        )
        s3 = handler.process_fill(
            make_fill(fill_id="f3", qty=Decimal("20"), price=Decimal("12.00")),
            order,
        )

        # (300 + 550 + 240) / 100 = 1090 / 100 = 10.90
        assert s3.avg_fill_price == Decimal("10.90")

    def test_fill_count_accumulates(self):
        """fill_count 随成交笔数递增。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        s1 = handler.process_fill(make_fill(fill_id="f1", qty=Decimal("10")), order)
        assert s1.fill_count == 1

        s2 = handler.process_fill(make_fill(fill_id="f2", qty=Decimal("20")), order)
        assert s2.fill_count == 2

        s3 = handler.process_fill(make_fill(fill_id="f3", qty=Decimal("70")), order)
        assert s3.fill_count == 3

    def test_commission_accumulates(self):
        """total_commission = 各笔 commission 之和。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(
            make_fill(fill_id="f1", qty=Decimal("30"), commission=Decimal("3.00")),
            order,
        )
        handler.process_fill(
            make_fill(fill_id="f2", qty=Decimal("70"), commission=Decimal("7.00")),
            order,
        )
        summary = handler.get_summary(order.order_id)
        assert summary is not None
        assert summary.total_commission == Decimal("10.00")


# ──────────────────────────────────────────────────────────────────────────────
# 幂等
# ──────────────────────────────────────────────────────────────────────────────


class TestIdempotency:
    def test_duplicate_fill_id_ignored(self):
        """同一 fill_id 重复处理不重复累积。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(fill_id="dup-1", qty=Decimal("30"))

        s1 = handler.process_fill(fill, order)
        assert s1.filled_quantity == Decimal("30")

        # 重复处理同一 fill
        s2 = handler.process_fill(fill, order)
        assert s2.filled_quantity == Decimal("30")  # 未累积
        assert s2.fill_count == 1  # 未增加

    def test_duplicate_returns_cached_summary(self):
        """重复处理返回缓存的 summary（同一对象）。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(fill_id="dup-2", qty=Decimal("50"))

        s1 = handler.process_fill(fill, order)
        s2 = handler.process_fill(fill, order)
        assert s1 is s2  # 同一对象


# ──────────────────────────────────────────────────────────────────────────────
# 状态转换
# ──────────────────────────────────────────────────────────────────────────────


class TestStateTransition:
    def test_submitted_to_partial(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"), status=OrderStatus.SUBMITTED)
        handler.process_fill(make_fill(qty=Decimal("30")), order)
        assert order.status == OrderStatus.PARTIAL

    def test_submitted_to_filled(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"), status=OrderStatus.SUBMITTED)
        handler.process_fill(make_fill(qty=Decimal("100")), order)
        assert order.status == OrderStatus.FILLED

    def test_partial_to_filled(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"), status=OrderStatus.SUBMITTED)

        handler.process_fill(make_fill(fill_id="f1", qty=Decimal("30")), order)
        assert order.status == OrderStatus.PARTIAL

        handler.process_fill(make_fill(fill_id="f2", qty=Decimal("70")), order)
        assert order.status == OrderStatus.FILLED

    def test_partial_stays_partial(self):
        """PARTIAL 状态下再次部分成交，保持 PARTIAL。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"), status=OrderStatus.SUBMITTED)

        handler.process_fill(make_fill(fill_id="f1", qty=Decimal("30")), order)
        assert order.status == OrderStatus.PARTIAL

        handler.process_fill(make_fill(fill_id="f2", qty=Decimal("20")), order)
        assert order.status == OrderStatus.PARTIAL  # 仍然 PARTIAL

    def test_over_fill_still_filled(self):
        """超量成交 → 仍标记 FILLED + 日志警告。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        handler.process_fill(make_fill(qty=Decimal("110")), order)
        assert order.status == OrderStatus.FILLED
        summary = handler.get_summary(order.order_id)
        assert summary is not None
        assert summary.is_complete is True
        assert summary.remaining_quantity == Decimal("0")  # 不为负


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_fills_returns_history(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(make_fill(fill_id="f1", qty=Decimal("30")), order)
        handler.process_fill(make_fill(fill_id="f2", qty=Decimal("70")), order)

        fills = handler.get_fills(order.order_id)
        assert len(fills) == 2
        assert fills[0].fill_id == "f1"
        assert fills[1].fill_id == "f2"

    def test_get_remaining(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(make_fill(qty=Decimal("30")), order)
        assert handler.get_remaining(order.order_id) == Decimal("70")

    def test_get_summary_after_multiple_fills(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(
            make_fill(fill_id="f1", qty=Decimal("30"), price=Decimal("10.00")),
            order,
        )
        handler.process_fill(
            make_fill(fill_id="f2", qty=Decimal("70"), price=Decimal("11.00")),
            order,
        )

        summary = handler.get_summary(order.order_id)
        assert summary is not None
        assert summary.total_quantity == Decimal("100")
        assert summary.filled_quantity == Decimal("100")
        assert summary.remaining_quantity == Decimal("0")
        # (30×10 + 70×11) / 100 = (300+770)/100 = 10.70
        assert summary.avg_fill_price == Decimal("10.70")
        assert summary.fill_count == 2
        assert summary.is_complete is True

    def test_summary_is_frozen(self):
        """FillSummary 是 frozen dataclass。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        summary = handler.process_fill(make_fill(qty=Decimal("50")), order)

        with pytest.raises(AttributeError):
            summary.filled_quantity = Decimal("999")

    def test_last_fill_timestamp(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        ts1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
        ts2 = datetime(2026, 1, 1, 11, 0, 0, tzinfo=UTC)

        handler.process_fill(make_fill(fill_id="f1", qty=Decimal("30"), timestamp=ts1), order)
        s2 = handler.process_fill(make_fill(fill_id="f2", qty=Decimal("70"), timestamp=ts2), order)

        assert s2.last_fill_timestamp == ts2


# ──────────────────────────────────────────────────────────────────────────────
# 回调
# ──────────────────────────────────────────────────────────────────────────────


class TestCallback:
    def test_callback_invoked(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        received: list[tuple[Fill, FillSummary]] = []
        handler.register_callback(lambda f, s: received.append((f, s)))

        fill = make_fill(qty=Decimal("50"))
        handler.process_fill(fill, order)

        assert len(received) == 1
        assert received[0][0] is fill
        assert received[0][1].filled_quantity == Decimal("50")

    def test_callback_error_doesnt_block(self):
        """回调异常不阻断处理。"""
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        def bad_callback(f, s):
            raise RuntimeError("callback error")

        handler.register_callback(bad_callback)

        # 不应抛异常
        summary = handler.process_fill(make_fill(qty=Decimal("50")), order)
        assert summary.filled_quantity == Decimal("50")

    def test_multiple_callbacks(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        calls_a: list[FillSummary] = []
        calls_b: list[FillSummary] = []
        handler.register_callback(lambda f, s: calls_a.append(s))
        handler.register_callback(lambda f, s: calls_b.append(s))

        handler.process_fill(make_fill(qty=Decimal("50")), order)

        assert len(calls_a) == 1
        assert len(calls_b) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 异常
# ──────────────────────────────────────────────────────────────────────────────


class TestErrors:
    def test_zero_quantity_raises(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(qty=Decimal("0"))

        with pytest.raises(InvalidFillError):
            handler.process_fill(fill, order)

    def test_negative_quantity_raises(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))
        fill = make_fill(qty=Decimal("-10"))

        with pytest.raises(InvalidFillError):
            handler.process_fill(fill, order)

    def test_order_id_mismatch_raises(self):
        handler = FillHandler()
        order = make_order(order_id="ord-A")
        fill = make_fill(order_id="ord-B", fill_id="f1")

        with pytest.raises(OrderNotFoundError):
            handler.process_fill(fill, order)


# ──────────────────────────────────────────────────────────────────────────────
# 统计
# ──────────────────────────────────────────────────────────────────────────────


class TestStats:
    def test_order_count(self):
        handler = FillHandler()
        order1 = make_order(order_id="ord-1", quantity=Decimal("100"))
        order2 = make_order(order_id="ord-2", quantity=Decimal("200"))

        handler.process_fill(make_fill(fill_id="f1", order_id="ord-1", qty=Decimal("50")), order1)
        assert handler.order_count == 1

        handler.process_fill(make_fill(fill_id="f2", order_id="ord-2", qty=Decimal("100")), order2)
        assert handler.order_count == 2

    def test_total_fill_count(self):
        handler = FillHandler()
        order = make_order(quantity=Decimal("100"))

        handler.process_fill(make_fill(fill_id="f1", qty=Decimal("30")), order)
        handler.process_fill(make_fill(fill_id="f2", qty=Decimal("70")), order)

        assert handler.total_fill_count == 2
