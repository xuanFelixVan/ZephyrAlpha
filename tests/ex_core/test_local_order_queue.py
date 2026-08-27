# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.test_local_order_queue
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.local_order_queue
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Local Order Queue 单元测试"""

from __future__ import annotations

import time
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.local_order_queue import LocalOrderQueue, OrderQueueItemStatus
from zephyr.shared.contracts.order import Order, OrderSide, OrderType


class TestLocalOrderQueue:
    """LocalOrderQueue 测试"""

    @pytest.fixture
    def mock_order_manager(self):
        """Mock OrderManager"""
        om = MagicMock()
        om.submit_order.return_value = "broker-001"
        return om

    @pytest.fixture
    def queue(self, mock_order_manager):
        """测试用队列"""
        q = LocalOrderQueue(mock_order_manager, broker_id="qmt_sim", default_interval=0.1)
        yield q
        q.stop()

    def test_enqueue(self, queue):
        """入队"""
        order = Order(
            order_id="test-001",
            idempotency_key="test-001",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

        queue.enqueue(order, interval_seconds=0.05)

        stats = queue.get_stats()
        assert stats.total == 1
        assert stats.pending == 1

    def test_enqueue_batch(self, queue):
        """批量入队"""
        orders = [
            Order(
                order_id=f"test-{i:03d}",
                idempotency_key=f"test-{i:03d}",
                symbol="510300.SH",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.50"),
                strategy_id="test",
            )
            for i in range(3)
        ]

        queue.enqueue_batch(orders, interval_seconds=0.05)

        stats = queue.get_stats()
        assert stats.total == 3
        assert stats.pending == 3

    def test_send_loop(self, queue, mock_order_manager):
        """发送循环"""
        order = Order(
            order_id="test-001",
            idempotency_key="test-001",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

        queue.enqueue(order, interval_seconds=0.05)
        queue.start()

        # 等待发送（队列循环 1 秒间隔，等 1.5 秒确保执行）
        time.sleep(1.5)

        stats = queue.get_stats()
        assert stats.sent == 1
        mock_order_manager.submit_order.assert_called_once_with("test-001", broker_id="qmt_sim")

    def test_send_retry(self, queue, mock_order_manager):
        """发送重试"""
        mock_order_manager.submit_order.side_effect = [Exception("fail"), "broker-001"]

        order = Order(
            order_id="test-001",
            idempotency_key="test-001",
            symbol="510300.SH",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("4.50"),
            strategy_id="test",
        )

        queue.enqueue(order, interval_seconds=0.05)
        queue.start()

        # 等待重试（队列循环 1 秒 + 重试延迟 10 秒，但测试等 2 秒第一次失败即可）
        time.sleep(2.0)

        stats = queue.get_stats()
        # 第一次失败， scheduled_time 推迟 10 秒，还没重试
        assert stats.sent == 0
        assert mock_order_manager.submit_order.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
