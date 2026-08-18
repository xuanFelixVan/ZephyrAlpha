"""红队测试：OrderManager._on_fill 防御校验 + CancelRateGuard 并发/reset 防护。

覆盖修复：
- P1: OrderManager._on_fill 无 fill 数值校验 / 无 fill_id 幂等去重 / 读-改-写无锁
- P1: CancelRateGuard._daily_count 竞态丢计数 + reset() 盘中清零无防护
"""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_manager import OrderManager
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill


def _make_fill(
    order_id: str,
    fill_id: str = "fill-1",
    qty: Decimal = Decimal("10"),
    price: Decimal | None = Decimal("10.00"),
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


class TestOnFillGuard:
    """OrderManager._on_fill 红队防御：非法 fill 拒收 + fill_id 幂等去重 + 并发不丢更新。"""

    def _setup(self) -> tuple[OrderManager, str]:
        om = OrderManager()
        order = om.create_order(
            symbol="600000.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10.00"),
        )
        return om, order.order_id

    def test_fill_qty_zero_rejected(self):
        om, order_id = self._setup()
        om._on_fill(_make_fill(order_id, qty=Decimal("0")))
        assert om.get_fills_for_order(order_id) == []
        order = om.orders[order_id]
        assert not order.filled_quantity or order.filled_quantity == 0

    def test_fill_qty_negative_rejected(self):
        om, order_id = self._setup()
        om._on_fill(_make_fill(order_id, qty=Decimal("-5")))
        assert om.get_fills_for_order(order_id) == []
        order = om.orders[order_id]
        assert not order.filled_quantity or order.filled_quantity == 0

    def test_fill_price_nan_rejected(self):
        om, order_id = self._setup()
        om._on_fill(_make_fill(order_id, price=Decimal("NaN")))
        assert om.get_fills_for_order(order_id) == []
        order = om.orders[order_id]
        assert not order.filled_quantity or order.filled_quantity == 0

    def test_fill_duplicate_id_skipped(self):
        om, order_id = self._setup()
        fill = _make_fill(order_id, fill_id="dup-1", qty=Decimal("10"))
        om._on_fill(fill)
        om._on_fill(fill)  # 同一 fill_id 重复推送
        fills = om.get_fills_for_order(order_id)
        assert len(fills) == 1
        assert om.orders[order_id].filled_quantity == Decimal("10")

    def test_fill_concurrent_no_lost_update(self):
        """多线程并发 _on_fill：无锁时读-改-写丢更新，加锁后累计精确。"""
        om, order_id = self._setup()
        n_threads, fills_per_thread = 8, 25
        barrier = threading.Barrier(n_threads)

        def worker(tid: int) -> None:
            barrier.wait()
            for i in range(fills_per_thread):
                om._on_fill(_make_fill(order_id, fill_id=f"t{tid}-f{i}", qty=Decimal("1")))

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total = n_threads * fills_per_thread
        assert om.orders[order_id].filled_quantity == Decimal(str(total))
        assert len(om.get_fills_for_order(order_id)) == total


class TestCancelRateGuardConcurrency:
    """CancelRateGuard 并发计数 + reset 盘中防护。"""

    def test_concurrent_record_submit_no_lost_count(self):
        guard = CancelRateGuard()
        n_threads, submits_per_thread = 8, 50
        barrier = threading.Barrier(n_threads)

        def worker() -> None:
            barrier.wait()
            for _ in range(submits_per_thread):
                guard.record_submit()

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert guard.daily_declaration_count == n_threads * submits_per_thread

    def test_reset_with_count_logs_critical(self, caplog: pytest.LogCaptureFixture):
        guard = CancelRateGuard()
        guard.record_submit()
        with caplog.at_level(logging.CRITICAL):
            guard.reset()
        assert guard.daily_declaration_count == 0
        assert any(
            r.levelno == logging.CRITICAL and "reset" in r.getMessage()
            for r in caplog.records
        )

    def test_reset_clean_no_critical(self, caplog: pytest.LogCaptureFixture):
        """计数为 0 的盘前 reset 不触发 critical。"""
        guard = CancelRateGuard()
        with caplog.at_level(logging.CRITICAL):
            guard.reset()
        assert not any(r.levelno == logging.CRITICAL for r in caplog.records)
