# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.lock
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
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
# [A_module] module_id=MOD-SHR_lock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修复）

痛点修复：多 Agent 并发操作时需要协调——防止重复处理同一资源——
  1. 两个 AI agent 同时修改同一个 Task → 数据竞争
  2. 没有 Lock 接口 → 无法在 Redis / etcd / SQL 之间切换后端
  3. 本地 asyncio.Lock 无法跨进程/跨容器

设计对标：
  - Redis Redlock（多节点分布式锁，Redisson 实现）
  - etcd Lock（Raft 共识 + Lease 续期）
  - Python asyncio.Lock（单进程锁——低配但零依赖）

设计原则：
  - 统一 Lock 接口——后端可替换（Memory / Redis / etcd）
  - TTL + 自动续期——防止死锁（持有者崩溃后锁不释放）
  - async context manager——Pythonic 的 with/asyncio 语法

AI 施工约定：
  - 任何并发写操作 MUST 加分布式锁——禁止裸并发写
  - 锁的 TTL MUST 设置为操作预估时间 × 2（留余量）

SSoT: MOD-INF-016 §2.20 shared-lock
Version: 0.1.0
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Protocol

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DistributedLock",
    "LockError",
    "LockHandle",
    "MemoryLock",
]

logger = logging.getLogger(__name__)


class LockError(ZephyrBaseError):
    """分布式锁操作失败——锁已被占用、后端不可达、超时。"""


@dataclass
class LockHandle:
    lock_name: str
    owner_id: str
    acquired_at: float = field(default_factory=time.monotonic)


class DistributedLock(Protocol):
    """分布式锁接口——acquire / release / stats。"""

    async def acquire(
        self,
        lock_name: str,
        *,
        ttl_seconds: float = 30.0,
        wait_timeout_seconds: float = 0.0,
    ) -> LockHandle | None: ...

    async def release(self, handle: LockHandle) -> bool: ...

    def is_locked(self, lock_name: str) -> bool: ...


class MemoryLock:
    """单进程异步锁——开发/测试用，不用于跨进程。

    对标 asyncio.Lock + context manager 语法糖。

    Usage::

        lock = MemoryLock()
        async with lock.lock("task-123") as handle:
            await process_task("task-123")
    """

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._owners: dict[str, str] = {}
        # 5.68.4 修复：跟踪 in-flight acquire 数，用于超时取消后判定是否可安全清理 _locks
        self._waiters: dict[str, int] = {}

    async def acquire(
        self,
        lock_name: str,
        *,
        ttl_seconds: float = 30.0,
        wait_timeout_seconds: float = 0.0,
    ) -> LockHandle | None:
        if lock_name not in self._locks:
            self._locks[lock_name] = asyncio.Lock()
        lock = self._locks[lock_name]
        self._waiters[lock_name] = self._waiters.get(lock_name, 0) + 1

        acquired = False
        try:
            if wait_timeout_seconds <= 0:
                if lock.locked():
                    logger.debug("lock '%s' already held by '%s'", lock_name, self._owners.get(lock_name, "unknown"))
                    return None
                await lock.acquire()
                acquired = True
            else:
                try:
                    await asyncio.wait_for(
                        lock.acquire(),
                        timeout=wait_timeout_seconds,
                    )
                    acquired = True
                except TimeoutError:
                    logger.debug("lock '%s' acquisition timed out after %.1fs", lock_name, wait_timeout_seconds)
                    return None
        finally:
            # 5.68.4 修复：超时/取消路径清理 _locks，防止每个唯一锁名永久驻留。
            # 仅当本协程未获取锁（acquired=False）且无其他等待者（waiters 归零）
            # 且锁未被持有时才删除——避免破坏其他在途 acquire 的互斥语义。
            self._waiters[lock_name] -= 1
            if self._waiters[lock_name] <= 0:
                del self._waiters[lock_name]
                if not acquired and not lock.locked() and lock_name in self._locks:
                    del self._locks[lock_name]

        owner = str(uuid.uuid4())[:8]
        self._owners[lock_name] = owner
        handle = LockHandle(lock_name=lock_name, owner_id=owner)
        logger.debug("lock '%s' acquired by '%s'", lock_name, owner)
        return handle

    async def release(self, handle: LockHandle) -> bool:
        lock = self._locks.get(handle.lock_name)
        if lock is None:
            return False
        if not lock.locked():
            return False
        # 5.58.10 修复：原 release 不验证 owner_id，任何拿到 LockHandle 引用的代码都能释放他人的锁。
        # 增加持有者一致性校验。
        if self._owners.get(handle.lock_name) != handle.owner_id:
            logger.warning(
                "lock '%s' release denied: owner mismatch (expected=%s, got=%s)",
                handle.lock_name,
                self._owners.get(handle.lock_name),
                handle.owner_id,
            )
            return False

        lock.release()
        if handle.lock_name in self._owners:
            del self._owners[handle.lock_name]
        # 5.65.4 修复：原 release 只删 _owners，不删 _locks。每个唯一锁名留下一个永久 asyncio.Lock 对象。
        # release时若_owners为空则删除_locks中的条目。
        if handle.lock_name not in self._owners and handle.lock_name in self._locks:
            del self._locks[handle.lock_name]
        logger.debug("lock '%s' released by '%s'", handle.lock_name, handle.owner_id)
        return True

    def is_locked(self, lock_name: str) -> bool:
        lock = self._locks.get(lock_name)
        return lock is not None and lock.locked()

    @asynccontextmanager
    async def lock(
        self,
        lock_name: str,
        *,
        ttl_seconds: float = 30.0,
        wait_timeout_seconds: float = 5.0,
    ) -> AsyncIterator[LockHandle]:
        handle = await self.acquire(
            lock_name,
            ttl_seconds=ttl_seconds,
            wait_timeout_seconds=wait_timeout_seconds,
        )
        if handle is None:
            raise LockError(
                f"failed to acquire lock '{lock_name}': already held or timed out",
                details={"lock_name": lock_name, "wait_timeout_seconds": wait_timeout_seconds},
            )
        try:
            yield handle
        finally:
            await self.release(handle)
