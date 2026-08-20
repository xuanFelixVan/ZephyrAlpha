# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.async_fill_dispatcher
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; zephyr.ex_core.fill_handler; zephyr.shared.contracts.fill; zephyr.shared.contracts.order
# [CONSUMERS] ex_core.adapters.miniqmt_broker ; ex_core.trading_session
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 回调内只入队不处理;独立线程消费;fill_id幂等;线程安全(queue+lock);优雅停机(join+sentinel)
# [MODIFY-GUARD] 40_execution_broker.md §决策①工程约束1
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AsyncFillDispatcherError
# [TESTS] tests/ex_core/test_async_fill_dispatcher.py
# [TTL] permanent

"""

成交回报异步派发器（40_execution_broker §决策① 工程约束1 gap 12 施工）。

XtQuant 实盘头号踩坑点：on_stock_order/on_stock_trade 回调在底层 C++ 线程执行，
回调内绝对不能执行耗时操作（如数据库写入、复杂计算），否则会导致成交回报延迟
（实盘案例：回调中复杂计算导致延迟 3 秒）。

正确做法：回调内只入队（Queue.put(trade)），独立线程消费（process_trades() 循环
Queue.get()）。本模块实现这一模式，作为 FillHandler 的异步包装层。

架构:
    C++ 线程回调 on_stock_trade(fill)
        ↓ Queue.put(fill)  ← 非阻塞 O(1)，回调内立即返回
    ┌─────────────────────────┐
    │  消费线程（daemon）       │
    │  while True:             │
    │      fill = queue.get()  │ ← 阻塞等待
    │      fill_handler.process_fill(fill, order)  ← 耗时操作在此线程
    │      callbacks(fill, summary)
    └─────────────────────────┘

为何不直接在回调内处理：
  1. C++ 底层线程阻塞 → 后续回报延迟（实测 3 秒延迟案例）
  2. 回调内调同步查询接口（query_stock_trades）会死锁
  3. 回调内异常会污染 C++ 线程，可能导致 XtQuantTrader 崩溃

为何用 Queue 而非 asyncio：
  1. Queue.put/get 是线程安全的标准库，无需事件循环
  2. XtQuant 回调是同步的（C++ 调 Python），无法直接 await
  3. daemon 线程简单可靠，进程退出自动结束

为何 fill_id 幂等：网络抖动可能重复推送同一笔成交，必须去重避免双重计数。

依据：40_execution_broker.md v2.4.0 §决策① 工程约束1
      2026 miniQMT 实盘避坑指南
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill
#   fields: fill_id/order_id/成交价格数量（XtQuant C++线程回调推送）
#   code: Fill (zephyr.shared.contracts.fill)
# - id: I2
#   name: 消费回调 consumer
#   fields: (fill, order)->None，耗时处理逻辑（DB写/复杂计算在此执行）
#   code: DispatchConsumer (async_fill_dispatcher.py L97)
# - id: I3
#   name: 订单查找函数 lookup_order_fn
#   fields: fill → Order|None，解析成交对应订单
#   code: OrderLookupFn (async_fill_dispatcher.py L100)
# - id: I4
#   name: 队列与去重配置
#   fields: queue_maxsize=10000（背压上限）/dedup_window=10000（LRU去重窗口）
#   code: __init__ (async_fill_dispatcher.py L142-177)
# 层: 算法
# - id: A1
#   name_zh: ① 回调内非阻塞入队
#   name_en: AsyncFillDispatcher.enqueue
#   intro: C++回调线程内只做去重+put_nowait，O(1)立即返回，零耗时防回报延迟
#   desc: 停机后入队raise；重复fill_id去重返False；队列满丢弃并error（背压保护）；成功enqueued+1（L227-267）
#   inputs: I1 I4
#   outputs: bool（入队成功/去重/背压丢弃）
#   invariant: 回调内只入队不处理
# - id: A2
#   name_zh: ② fill_id LRU 幂等去重
#   name_en: _is_new_fill
#   intro: set查询O(1)判重，超窗口淘汰最老fill_id防内存无限增长
#   desc: fill_id=None视为新；加锁查_seen_fill_ids，命中→False；否则入集合并按LRU淘汰超出dedup_window的最老id（L321-343）
#   inputs: I1 I4
#   outputs: True=新/False=重复
#   invariant: fill_id幂等（重复推送不双重计数）
# - id: A3
#   name_zh: ③ 消费线程主循环
#   name_en: _consume_loop
#   intro: daemon独立线程阻塞Queue.get逐笔处理，收到停机哨兵退出，单笔异常不中断循环
#   desc: while running或队列非空→get(timeout=1.0)；哨兵→break；_dispatch_one异常→errors+1继续；finally task_done（L271-297）
#   inputs: I4
#   outputs: 消费循环（线程）
#   invariant: 独立线程消费；线程安全（queue+lock）
# - id: A4
#   name_zh: ④ 单笔派发
#   name_en: _dispatch_one
#   intro: 查订单后调consumer回调，耗时操作在此线程不阻塞C++回调
#   desc: lookup_order_fn(fill)→None则warning+errors+1跳过；否则consumer(fill, order)，成功后dispatched+1并刷新last_dispatch_at/queue_size（L299-317）
#   inputs: I2 I3
#   outputs: consumer(fill, order) 调用
# - id: A5
#   name_zh: ⑤ 优雅停机
#   name_en: stop
#   intro: 清running标志投哨兵，join等待消费线程排空退出
#   desc: _running.clear→put_nowait(哨兵)（满则warning）→join(timeout)，返回是否已退出（L195-223）
#   inputs: I4
#   outputs: bool（线程已退出/超时）
#   invariant: 优雅停机（join+sentinel）
# 层: 输出
# - id: O1
#   name_zh: 派发的成交处理回调 (fill, order)
#   name_en: DispatchConsumer 调用
#   intro: 在独立线程执行FillHandler耗时成交处理，与XtQuant回调线程解耦
#   invariant: 回调内只入队不处理；fill_id幂等；异常隔离不中断消费
#   downstream: ex_core.adapters.miniqmt_broker / ex_core.trading_session
# - id: O2
#   name_zh: 派发统计 DispatchStats
#   name_en: DispatchStats
#   intro: enqueued/dispatched/deduplicated/errors/queue_size/last_dispatch_at快照供监控告警
#   downstream: 无下游/内部使用（监控）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I4 --> A1
# I1 --> A2
# I4 --> A2
# A2 --> A1
# A1 --> A3
# I4 --> A3
# A3 --> A4
# I2 --> A4
# I3 --> A4
# A5 --> A3
# I4 --> A5
# A4 --> O1
# A3 --> O2
# A1 --> O2
"""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Final

from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

__all__: Final = [
    "AsyncFillDispatcherError",
    "DispatchStats",
    "AsyncFillDispatcher",
]

_logger = logging.getLogger(__name__)


class AsyncFillDispatcherError(Exception):
    """成交回报异步派发错误。"""

    error_code = "ZA-XC-0012"


@dataclass
class DispatchStats:
    """派发统计（线程安全快照，可能略有竞态但足够监控）。"""

    enqueued: int = 0  # 入队总数
    dispatched: int = 0  # 已派发（处理成功）
    deduplicated: int = 0  # 重复 fill_id 去重数
    errors: int = 0  # 处理异常数
    queue_size: int = 0  # 当前队列长度
    last_dispatch_at: datetime | None = None  # 最后派发时间


# 消费者回调签名：(fill, order) -> None
#   fill: 成交回报
#   order: 对应订单（由 lookup_order_fn 解析）
DispatchConsumer = Callable[[Fill, Order], None]

# 订单查找函数签名：fill_id 或 order_id -> Order | None
OrderLookupFn = Callable[[Fill], Order | None]

# 哨兵值，用于优雅停机
_SHUTDOWN_SENTINEL: Final[object] = object()


class AsyncFillDispatcher:
    """成交回报异步派发器（回调线程模型）。

    包装 FillHandler，将同步处理改为"回调内入队 + 独立线程消费"模式。
    解决 XtQuant C++ 回调线程内耗时操作导致回报延迟/死锁的问题。

    用法:
        # 1. 创建派发器（注入 FillHandler 和订单查找函数）
        dispatcher = AsyncFillDispatcher(
            consumer=my_fill_consumer,           # (fill, order) -> None
            lookup_order_fn=lambda f: om.orders.get(f.order_id),
            queue_maxsize=10000,
        )

        # 2. 启动消费线程
        dispatcher.start()

        # 3. 注册为 XtQuant 回调（回调内只调 enqueue，不处理）
        def on_stock_trade(trade_data):
            fill = convert_to_fill(trade_data)
            dispatcher.enqueue(fill)  # 非阻塞入队，立即返回

        xttrader.register_callback(on_stock_trade=on_stock_trade)

        # 4. 停机时优雅关闭
        dispatcher.stop(timeout=5.0)

    设计要点:
      - **回调内零耗时**：enqueue 只做 Queue.put，O(1) 非阻塞
      - **fill_id 幂等**：维护已处理 fill_id 集合，重复推送去重
      - **线程安全**：Queue 自带线程安全，stats 用 lock 保护
      - **优雅停机**：stop() 投递哨兵，消费线程处理后退出，join 等待
      - **异常隔离**：单笔 fill 处理异常不中断消费线程
      - **背压保护**：队列满时 enqueue 可选阻塞或丢弃（默认阻塞带超时）
    """

    def __init__(
        self,
        consumer: DispatchConsumer,
        lookup_order_fn: OrderLookupFn,
        queue_maxsize: int = 10000,
        dedup_window: int = 10000,
        consumer_name: str = "fill-dispatcher",
    ) -> None:
        """初始化异步派发器。

        Args:
            consumer: 消费回调 (fill, order) -> None。order 为 None 时跳过。
            lookup_order_fn: 订单查找函数 fill -> Order|None。
            queue_maxsize: 队列上限（背压保护），默认 10000。
            dedup_window: fill_id 去重窗口大小（LRU），默认 10000。
            consumer_name: 消费线程名（便于调试）。
        """
        self._consumer = consumer
        self._lookup_order_fn = lookup_order_fn
        self._queue: queue.Queue = queue.Queue(maxsize=queue_maxsize)
        self._consumer_name = consumer_name

        # 线程控制
        self._thread: threading.Thread | None = None
        self._running = threading.Event()
        self._running.set()  # 初始为 True，stop() 时 clear

        # fill_id 去重（LRU 窗口）
        self._seen_fill_ids: set[str] = set()
        self._fill_id_order: list[str] = []  # 维护 LRU 顺序
        self._dedup_window = dedup_window
        self._dedup_lock = threading.Lock()

        # 统计
        self._stats_lock = threading.Lock()
        self._stats = DispatchStats()

    # ── 生命周期 ──

    def start(self) -> None:
        """启动消费线程（daemon，进程退出自动结束）。"""
        if self._thread is not None and self._thread.is_alive():
            _logger.warning("AsyncFillDispatcher 已在运行")
            return
        self._running.set()
        self._thread = threading.Thread(
            target=self._consume_loop,
            name=self._consumer_name,
            daemon=True,
        )
        self._thread.start()
        _logger.info("AsyncFillDispatcher 启动: %s", self._consumer_name)

    def stop(self, timeout: float = 5.0) -> bool:
        """优雅停机：投递哨兵 + 等待消费线程退出。

        Args:
            timeout: join 超时秒数

        Returns:
            True=线程已退出，False=超时未退出
        """
        if self._thread is None:
            return True
        self._running.clear()
        try:
            self._queue.put_nowait(_SHUTDOWN_SENTINEL)
        except queue.Full:
            _logger.warning("停机哨兵入队失败（队列满），强制等待线程退出")
        self._thread.join(timeout=timeout)
        exited = not self._thread.is_alive()
        if exited:
            _logger.info(
                "AsyncFillDispatcher 停机完成: %s (dispatched=%d)",
                self._consumer_name,
                self._stats.dispatched,
            )
        else:
            _logger.error(
                "AsyncFillDispatcher 停机超时: %s (queue_size=%d)",
                self._consumer_name,
                self._queue.qsize(),
            )
        return exited

    # ── 回调入口（C++ 线程调用） ──

    def enqueue(self, fill: Fill) -> bool:
        """入队成交回报（回调内调用，必须非阻塞/极快）。

        此方法设计为在 XtQuant C++ 回调线程内调用，**只做 Queue.put**，
        不做任何耗时操作（无 DB 写、无复杂计算、无同步查询）。

        Args:
            fill: 成交回报

        Returns:
            True=入队成功，False=队列满（背压）或重复 fill_id 去重

        Raises:
            AsyncFillDispatcherError: 停机后入队
        """
        if not self._running.is_set():
            raise AsyncFillDispatcherError(f"派发器已停机，拒绝入队 fill_id={fill.fill_id}")

        # fill_id 幂等去重（回调内快速判断，set 查询 O(1)）
        if not self._is_new_fill(fill.fill_id):
            with self._stats_lock:
                self._stats.deduplicated += 1
            _logger.debug("重复 fill_id 去重: %s", fill.fill_id)
            return False

        # 非阻塞入队（队列满时返回 False，不阻塞 C++ 回调线程）
        try:
            self._queue.put_nowait(fill)
        except queue.Full:
            _logger.error(
                "成交队列满（backpressure），丢弃 fill_id=%s (queue_maxsize=%d)——这是严重错误，需检查消费速度",
                fill.fill_id,
                self._queue.maxsize,
            )
            return False

        with self._stats_lock:
            self._stats.enqueued += 1
        return True

    # ── 消费循环（独立线程） ──

    def _consume_loop(self) -> None:
        """消费线程主循环：Queue.get → process → callback。"""
        _logger.info("消费线程启动: %s", self._consumer_name)
        while self._running.is_set() or not self._queue.empty():
            try:
                item = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if item is _SHUTDOWN_SENTINEL:
                _logger.info("收到停机哨兵，消费线程退出")
                break

            fill: Fill = item  # type: ignore[assignment]
            try:
                self._dispatch_one(fill)
            except Exception as exc:  # noqa: BLE001 — 单笔异常不中断循环
                with self._stats_lock:
                    self._stats.errors += 1
                _logger.error(
                    "派发 fill 异常 fill_id=%s: %s",
                    getattr(fill, "fill_id", "?"),
                    exc,
                    exc_info=True,
                )
            finally:
                self._queue.task_done()

        _logger.info("消费线程退出: %s", self._consumer_name)

    def _dispatch_one(self, fill: Fill) -> None:
        """派发单笔 fill：查找订单 → 调用 consumer。"""
        order = self._lookup_order_fn(fill)
        if order is None:
            _logger.warning(
                "成交回报对应订单不存在，跳过 fill_id=%s order_id=%s",
                fill.fill_id,
                getattr(fill, "order_id", "?"),
            )
            with self._stats_lock:
                self._stats.errors += 1
            return

        # 调用消费者回调（耗时操作在此线程，不阻塞 C++ 回调线程）
        self._consumer(fill, order)

        with self._stats_lock:
            self._stats.dispatched += 1
            self._stats.last_dispatch_at = datetime.now(timezone.utc)
            self._stats.queue_size = self._queue.qsize()

    # ── fill_id 去重 ──

    def _is_new_fill(self, fill_id: str | None) -> bool:
        """判断 fill_id 是否为新（未处理过），并加入去重窗口。

        使用 LRU 窗口避免内存无限增长：超过 dedup_window 时淘汰最老的 fill_id。

        Args:
            fill_id: 成交 ID（None 视为新，不去重）

        Returns:
            True=新 fill_id，False=重复
        """
        if fill_id is None:
            return True
        with self._dedup_lock:
            if fill_id in self._seen_fill_ids:
                return False
            self._seen_fill_ids.add(fill_id)
            self._fill_id_order.append(fill_id)
            # LRU 淘汰
            if len(self._fill_id_order) > self._dedup_window:
                old = self._fill_id_order.pop(0)
                self._seen_fill_ids.discard(old)
            return True

    # ── 状态查询 ──

    @property
    def stats(self) -> DispatchStats:
        """当前派发统计快照。"""
        with self._stats_lock:
            return DispatchStats(
                enqueued=self._stats.enqueued,
                dispatched=self._stats.dispatched,
                deduplicated=self._stats.deduplicated,
                errors=self._stats.errors,
                queue_size=self._queue.qsize(),
                last_dispatch_at=self._stats.last_dispatch_at,
            )

    @property
    def is_running(self) -> bool:
        """消费线程是否在运行。"""
        return self._thread is not None and self._thread.is_alive()

    def queue_size(self) -> int:
        """当前队列长度。"""
        return self._queue.qsize()

    def flush(self, timeout: float = 5.0) -> bool:
        """等待队列消费完毕（用于测试或停机前确保处理完）。

        Args:
            timeout: 最大等待秒数

        Returns:
            True=队列已空，False=超时
        """
        deadline = datetime.now(timezone.utc).timestamp() + timeout
        while not self._queue.empty():
            if datetime.now(timezone.utc).timestamp() > deadline:
                return False
            threading.Event().wait(0.01)
        return True
