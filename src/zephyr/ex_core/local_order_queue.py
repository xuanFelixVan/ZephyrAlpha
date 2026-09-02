# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.local_order_queue
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.order
# [CONSUMERS] zephyr.ex_core.adapters.qmt_file_bridge_integration
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 逐笔间隔发送; 失败延迟10秒重试; 队列在本地(QMT永远只看到1~2笔)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LocalOrderQueueError
# [TESTS] tests/ex_core/test_local_order_queue.py
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Local Order Queue——本地订单排队器（算法单切片缓冲）

职责:
  - 算法单（TWAP/VWAP 切片）在本地排队，按时间间隔逐笔发送
  - QMT 柜台对程序化报单有同标的同向挂单上限（约 2~3 笔），
    排队在本地，QMT 通道永远不觉得挤（蓝图 §7.5）
  - 发送失败延迟重试（默认 10 秒），不丢单

约束:
  - 只负责排队与调度，下单动作委托给 OrderManager.submit_order
  - 1 秒调度循环，interval_seconds 控制相邻两笔的最小间隔

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from zephyr.shared.contracts.order import Order

_logger = logging.getLogger(__name__)


class LocalOrderQueueError(Exception):
    """本地订单队列错误"""

    error_code = "ZA-XC-LOQ"


class OrderQueueItemStatus(str, Enum):
    """队列项状态"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class OrderQueueItem:
    """队列项"""

    order: Order
    scheduled_time: float  # 计划发送时间（epoch 秒）
    status: OrderQueueItemStatus = OrderQueueItemStatus.PENDING
    attempts: int = 0
    last_error: str = ""


@dataclass
class QueueStats:
    """队列统计"""

    total: int
    pending: int
    sent: int
    failed: int


class LocalOrderQueue:
    """本地订单排队器

    Usage:
        queue = LocalOrderQueue(order_manager, broker_id="qmt_sim", default_interval=180.0)
        queue.enqueue(order)                     # 默认间隔
        queue.enqueue_batch(orders, interval_seconds=10.0)  # 批量，逐笔间隔 10 秒
        queue.start()                            # 启动调度线程
        stats = queue.get_stats()
        queue.stop()
    """

    # 调度循环间隔（秒）
    LOOP_INTERVAL = 1.0
    # 发送失败重试延迟（秒）
    RETRY_DELAY = 10.0

    def __init__(self, order_manager, broker_id: str, default_interval: float = 180.0):
        """初始化

        Args:
            order_manager: OrderManager 实例（submit_order(order_id, broker_id=...) 调用点）
            broker_id: 目标券商标识（如 "qmt_sim" / "qmt_real"）
            default_interval: 默认发送间隔（秒），算法单切片常用 180 秒（3 分钟）
        """
        self._order_manager = order_manager
        self._broker_id = broker_id
        self._default_interval = default_interval

        self._items: list[OrderQueueItem] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def broker_id(self) -> str:
        return self._broker_id

    def enqueue(self, order: Order, interval_seconds: float | None = None) -> None:
        """单笔入队

        Args:
            order: 订单（须已通过 OrderManager.create_order 创建）
            interval_seconds: 距上一笔（或现在）的发送间隔，None 用默认
        """
        interval = interval_seconds if interval_seconds is not None else self._default_interval
        with self._lock:
            scheduled = self._next_schedule_time(interval)
            self._items.append(OrderQueueItem(order=order, scheduled_time=scheduled))
        _logger.info(
            "入队 %s broker=%s scheduled=+%.1fs",
            order.order_id,
            self._broker_id,
            scheduled - time.monotonic(),
        )

    def enqueue_batch(self, orders: list[Order], interval_seconds: float | None = None) -> None:
        """批量入队（逐笔间隔）

        第 1 笔立即调度，其后每笔间隔 interval_seconds。
        """
        interval = interval_seconds if interval_seconds is not None else self._default_interval
        with self._lock:
            base = time.monotonic()
            for i, order in enumerate(orders):
                self._items.append(OrderQueueItem(order=order, scheduled_time=base + i * interval))
        _logger.info(
            "批量入队 %d 笔 broker=%s interval=%.1fs",
            len(orders),
            self._broker_id,
            interval,
        )

    def start(self) -> None:
        """启动调度线程"""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name=f"local-order-queue-{self._broker_id}",
            daemon=True,
        )
        self._thread.start()
        _logger.info("LocalOrderQueue started broker=%s", self._broker_id)

    def stop(self) -> None:
        """停止调度线程（已入队未发送的订单保留在队列中）"""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        _logger.info("LocalOrderQueue stopped broker=%s", self._broker_id)

    def get_stats(self) -> QueueStats:
        """队列统计"""
        with self._lock:
            total = len(self._items)
            pending = sum(1 for i in self._items if i.status == OrderQueueItemStatus.PENDING)
            sent = sum(1 for i in self._items if i.status == OrderQueueItemStatus.SENT)
            failed = sum(1 for i in self._items if i.status == OrderQueueItemStatus.FAILED)
        return QueueStats(total=total, pending=pending, sent=sent, failed=failed)

    def get_items(self) -> list[OrderQueueItem]:
        """队列项快照（监控用）"""
        with self._lock:
            return list(self._items)

    def health_check(self) -> dict:
        """健康检查（前端监控数据源）"""
        running = bool(self._thread and self._thread.is_alive())
        stats = self.get_stats()
        ok = running and stats.failed == 0
        if not running:
            level = "down"
        elif stats.failed > 0:
            level = "degraded"
        else:
            level = "ok"
        return {
            "component": f"queue_{self._broker_id}",
            "type": "order_queue",
            "ok": ok,
            "level": level,
            "running": running,
            "total": stats.total,
            "pending": stats.pending,
            "sent": stats.sent,
            "failed": stats.failed,
        }

    # ── 内部 ──

    def _next_schedule_time(self, interval: float) -> float:
        """计划时间 = max(现在, 最后一笔待发时间) + interval；空队列立即"""
        last_pending = max(
            (i.scheduled_time for i in self._items if i.status == OrderQueueItemStatus.PENDING),
            default=None,
        )
        base = last_pending if last_pending is not None else time.monotonic()
        if last_pending is None:
            # 空队列：首笔只等 interval 的极小偏移，尽快发出
            return base + min(interval, 0.05)
        return base + interval

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._dispatch_due()
            except Exception as e:  # 调度异常不杀线程
                _logger.warning("队列调度异常 broker=%s: %r", self._broker_id, e)
            self._stop_event.wait(self.LOOP_INTERVAL)

    def _dispatch_due(self) -> None:
        """发送所有到期的队列项"""
        now = time.monotonic()
        with self._lock:
            due = [i for i in self._items if i.status == OrderQueueItemStatus.PENDING and i.scheduled_time <= now]
        for item in due:
            self._send(item)

    def _send(self, item: OrderQueueItem) -> None:
        """发送单笔，失败延迟重试"""
        item.attempts += 1
        try:
            self._order_manager.submit_order(item.order.order_id, broker_id=self._broker_id)
            item.status = OrderQueueItemStatus.SENT
            _logger.info(
                "队列发送 %s broker=%s attempt=%d",
                item.order.order_id,
                self._broker_id,
                item.attempts,
            )
        except Exception as e:
            item.last_error = str(e)
            item.scheduled_time = time.monotonic() + self.RETRY_DELAY
            _logger.warning(
                "队列发送失败 %s broker=%s attempt=%d，%.0f 秒后重试: %r",
                item.order.order_id,
                self._broker_id,
                item.attempts,
                self.RETRY_DELAY,
                e,
            )


if __name__ == "__main__":
    # 冒烟：仅验证导入与基本入队
    from unittest.mock import MagicMock

    om = MagicMock()
    q = LocalOrderQueue(om, broker_id="qmt_sim", default_interval=1.0)
    print("LocalOrderQueue smoke ok, stats:", q.get_stats())
