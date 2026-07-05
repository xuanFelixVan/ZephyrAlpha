# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.outbox
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.contracts.core.base_event
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_outbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
outbox.py —— 事务性 Outbox 模式（Phase 10 新增 | 盲点 B24 修复）

痛点修复：事件发布不在事务内 → "写数据库成功但事件丢失" 或 "事件发出但数据库回滚"——
  1. 当前 Observer.emit() 是 fire-and-forget——没有事务性保证
  2. dlq.py 只能捕获 handler 异常——不能解决 "事件根本没发出" 的问题
  3. 在数据库写入和事件发布之间存在根本性的原子性缺口

设计对标：
  - Debezium CDC（Change Data Capture + outbox table）
  - PostgreSQL LISTEN/NOTIFY（事务内通知）
  - Transactional Outbox（Microservices Patterns / Chris Richardson）

设计原则：
  - Outbox pub/sub——先写 outbox 表（在事务内），后台 worker 异步轮询发送
  - 至少一次语义——worker 保证最终一致性（可能重复发送，但从不丢失）
  - 可配置轮询间隔 + 批处理大小

AI 施工约定：
  - 任何需要事务性事件发布的模块 MUST 使用 Outbox——禁止裸 Observer.emit()
  - outbox 消息 MUST 带 idempotency_key（防止重复消费）

SSoT: MOD-INF-016 §2.21 shared-outbox
Version: 0.1.0
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, Protocol

# 5.119.3 修复: 导入 trace_id_var 用于每轮轮询重置 trace_id
from zephyr.shared.utils.logging import trace_id_var

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "MemoryOutboxStore",
    "OutboxEntry",
    "OutboxError",
    "OutboxPublisher",
    "OutboxStatus",
    "OutboxStore",
]

logger = logging.getLogger(__name__)


class OutboxError(ZephyrBaseError):
    """Outbox 操作失败——存储后端不可达、消息格式无效。"""


@unique
class OutboxStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


@dataclass
class OutboxEntry:
    id: str
    event_type: str
    payload: dict[str, Any]
    status: OutboxStatus = OutboxStatus.PENDING
    created_at: float = field(default_factory=time.monotonic)
    published_at: float = 0.0
    retry_count: int = 0
    idempotency_key: str = ""


class OutboxStore(Protocol):
    """Outbox 存储后端接口。"""

    # 5.56.5 修复：原注解 -> Self 但 Self 未导入且语义错误（方法返回 OutboxEntry 不是 Self）。
    # 改为 -> OutboxEntry。
    async def append(self, event_type: str, payload: dict[str, Any], *, idempotency_key: str = "") -> OutboxEntry: ...
    async def fetch_pending(self, limit: int = 100) -> list[OutboxEntry]: ...
    async def mark_published(self, entry_id: str) -> None: ...
    async def mark_failed(self, entry_id: str) -> None: ...
    async def count_pending(self) -> int: ...


class MemoryOutboxStore:
    """内存中的 Outbox 存储——开发/测试用。

    Production 应替换为基于 SQLite/PostgreSQL 的实现。
    """

    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: dict[str, OutboxEntry] = {}
        self._max_entries = max_entries
        self._lock = asyncio.Lock()

    async def append(self, event_type: str, payload: dict[str, Any], *, idempotency_key: str = "") -> OutboxEntry:
        async with self._lock:
            if len(self._entries) >= self._max_entries:
                stale = sorted(
                    [e for e in self._entries.values() if e.status != OutboxStatus.PENDING],
                    key=lambda e: e.published_at,
                )
                for entry in stale[: len(self._entries) // 4]:
                    del self._entries[entry.id]

            entry_id = str(uuid.uuid4())[:12]
            entry = OutboxEntry(
                id=entry_id,
                event_type=event_type,
                payload=payload,
                idempotency_key=idempotency_key or entry_id,
            )
            self._entries[entry_id] = entry
            logger.debug("outbox: appended %s (%s)", entry_id, event_type)
            return entry

    async def fetch_pending(self, limit: int = 100) -> list[OutboxEntry]:
        # 5.57.7 修复：原 fetch_pending 无锁，与 append 并发时 "RuntimeError: dictionary changed size during iteration"。
        # mark_published/mark_failed/count_pending 同样无锁。所有读写 self._entries 的方法都加锁。
        async with self._lock:
            pending = [e for e in self._entries.values() if e.status == OutboxStatus.PENDING]
            pending.sort(key=lambda e: e.created_at)
            return pending[:limit]

    async def mark_published(self, entry_id: str) -> None:
        async with self._lock:
            entry = self._entries.get(entry_id)
            if entry is not None:
                entry.status = OutboxStatus.PUBLISHED
                entry.published_at = time.monotonic()

    async def mark_failed(self, entry_id: str) -> None:
        async with self._lock:
            entry = self._entries.get(entry_id)
            if entry is not None:
                entry.status = OutboxStatus.FAILED
                entry.retry_count += 1

    async def count_pending(self) -> int:
        async with self._lock:
            return sum(1 for e in self._entries.values() if e.status == OutboxStatus.PENDING)


class OutboxPublisher:
    """后台轮询型 Outbox 发布器——从 outbox 表取 PENDING 消息 → 调用 handler 发布。

    对标 Debezium 的轮询模式（非 CDC，简单可靠）。

    Usage::

        store = MemoryOutboxStore()
        publisher = OutboxPublisher(
            store=store,
            handler=lambda e: observer.emit(e.event_type, **e.payload),
            poll_interval_seconds=1.0,
        )
        await publisher.start()
        ...
        await publisher.stop()
    """

    def __init__(
        self,
        store: OutboxStore,
        handler: Callable[[OutboxEntry], Any],
        *,
        poll_interval_seconds: float = 1.0,
        batch_size: int = 20,
        max_retries: int = 5,
    ) -> None:
        self._store = store
        self._handler = handler
        self._poll_interval = poll_interval_seconds
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._running = False
        self._task: asyncio.Task[Any] | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("outbox publisher started (interval=%.1fs, batch=%d)", self._poll_interval, self._batch_size)

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("outbox publisher stopped")

    async def _poll_loop(self) -> None:
        while self._running:
            # 5.119.3 修复: 每轮轮询重置 trace_id,避免冻结为 start() 时刻的快照
            # 原 create_task 时 trace_id 被冻结,后续每轮日志携带相同 trace_id 无法区分轮次
            trace_id_var.set(f"outbox-poll-{uuid.uuid4().hex[:8]}")
            try:
                pending = await self._store.fetch_pending(limit=self._batch_size)
                for entry in pending:
                    if entry.retry_count >= self._max_retries:
                        await self._store.mark_failed(entry.id)
                        logger.warning("outbox: %s exhausted retries (%d)", entry.id, entry.retry_count)
                        continue

                    try:
                        result = self._handler(entry)
                        if asyncio.iscoroutine(result):
                            await result
                        await self._store.mark_published(entry.id)
                        logger.debug("outbox: %s published → %s", entry.id, entry.event_type)
                    except Exception as exc:
                        await self._store.mark_failed(entry.id)
                        logger.error("outbox: %s publish failed: %s", entry.id, exc)
            except Exception as exc:
                logger.error("outbox poll failed: %s", exc)

            await asyncio.sleep(self._poll_interval)
