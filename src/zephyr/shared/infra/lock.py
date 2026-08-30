# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.lock
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
lock.py —— 分布式锁抽象（Phase 10 新增 | 盲点 B23 修复）

痛点修复：多 Agent 并发操作时需要协调——防止重复处理同一资源——
  1. 两个 AI agent 同时修改同一个 Task -> 数据竞争
  2. 没有 Lock 接口 -> 无法在 Redis / etcd / SQL 之间切换后端
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: counter_path 参数
#   fields: 参数 counter_path，类型注解 Path | str
#   code: lock.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① next_fencing_token
#   name_en: next_fencing_token
#   intro: 读取并递增持久化 fencing 计数器，返回新的单调递增 token（5.58.2）。
#   desc: 读取并递增持久化 fencing 计数器，返回新的单调递增 token（5.58.2）。 调用方 MUST 已持有对应互斥锁——递增操作在锁保护下串行化，保证单调性。 计数器文件…；源码 L130-L151
#   inputs: counter_path
#   outputs: int
# - id: A2
#   name_zh: ② SyncLockRenewer
#   name_en: SyncLockRenewer
#   intro: TTL 锁自动续期 watchdog（5.58.3）——守护线程定期调用 refresh_fn 刷新锁时间戳。
#   desc: TTL 锁自动续期 watchdog（5.58.3）——守护线程定期调用 refresh_fn 刷新锁时间戳。 refresh_fn() 续约前 MUST 验证持有者身份（own…；公共方法（定义序）: start,…
#   inputs: refresh_fn interval_s name
#   outputs: 返回值
# - id: A3
#   name_zh: ③ DistributedLock
#   name_en: DistributedLock
#   intro: 分布式锁接口——acquire / release / stats。
#   desc: 分布式锁接口——acquire / release / stats。；公共方法（定义序）: acquire, release, is_locked；源码 L205-L218
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ MemoryLock
#   name_en: MemoryLock
#   intro: 单进程异步锁——开发/测试用，不用于跨进程。
#   desc: 单进程异步锁——开发/测试用，不用于跨进程。 对标 asyncio.Lock + context manager 语法糖。 Usage:: lock = MemoryLock()…；公共方法（定义序）: acquire…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write

__all__ = [
    "DistributedLock",
    "LockError",
    "LockHandle",
    "MemoryLock",
    "SyncLockRenewer",
    "next_fencing_token",
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 5.58 同步文件锁共享助手（fencing token + TTL 自动续期）
# ---------------------------------------------------------------------------


def next_fencing_token(counter_path: Path | str) -> int:
    """读取并递增持久化 fencing 计数器，返回新的单调递增 token（5.58.2）。

    调用方 MUST 已持有对应互斥锁——递增操作在锁保护下串行化，保证单调性。
    计数器文件缺失/损坏时从 1 重新开始：旧锁内容中的 token 随锁文件一起失效，
    不会有两个活跃持有者共享同一 token（释放验证同时比对 owner + token）。
    """
    path = Path(counter_path)
    token = 0
    try:
        raw = path.read_text(encoding="utf-8").strip()
        token = int(raw) if raw else 0
    except (OSError, ValueError):
        token = 0
    token += 1
    try:
        # AI-15 审计治本（2026-08-17）：委托唯一真源 file_utils.atomic_write，
        # 消除本地 tmp+os.replace 重复实现（AtomicWriteError 是 OSError 子类，静默语义不变）。
        atomic_write(path, str(token))
    except OSError:
        pass
    return token


class SyncLockRenewer:
    """TTL 锁自动续期 watchdog（5.58.3）——守护线程定期调用 refresh_fn 刷新锁时间戳。

    refresh_fn() 续约前 MUST 验证持有者身份（owner + fencing token），
    返回 False（锁已释放/已被取代）时 watchdog 自动停止。
    线程为 daemon——进程退出不阻塞；stop() 通过 Event 立即唤醒退出。
    """

    def __init__(self, refresh_fn: Callable[[], bool], interval_s: float, name: str = "sync-lock-renewer") -> None:
        self._refresh_fn = refresh_fn
        self._interval_s = max(1.0, interval_s)
        self._name = name
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name=self._name, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.wait(self._interval_s):
            try:
                if not self._refresh_fn():
                    return
            except Exception:  # noqa: BLE001 — watchdog 异常静默退出，续约失效后锁按 TTL 自然过期
                logger.warning("SyncLockRenewer '%s' refresh failed, stopping", self._name, exc_info=True)
                return

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        self._thread = None


class LockError(ZephyrBaseError):
    """分布式锁操作失败——锁已被占用、后端不可达、超时。"""

    error_code = "ZA-SH-0041"


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
