# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.orchestrator.core.task_queue
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol
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
# [A_module] module_id=MOD-ORC_task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-TASK_SYSTEM 盲点#9
依赖: TaskRepository + Protocol:PipelineDispatcher + EventHook

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

AUDIT-08 H6 修复：不再直接导入 PipelineOrchestrator，改用 Protocol 解耦，
打破 pipeline ↔ orchestrator 双向循环依赖。

Usage:
    from zephyr.orchestrator.core.task_queue import ActiveTaskQueue

    queue = ActiveTaskQueue(repo, orchestrator)
    queue.start()
    # ...
    queue.stop()
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol

logger = logging.getLogger("zephyr.task_queue")

_POLL_INTERVAL = 4.0
_MAX_PER_CYCLE = 3


@runtime_checkable
class PipelineDispatcher(Protocol):
    """AUDIT-08 H6: 打破 pipeline↔orchestrator 循环依赖的协议接口。

    任何实现了 ``dispatch(task_card)`` 方法的对象均可注入 ActiveTaskQueue，
    无需直接依赖 PipelineOrchestrator 类型。
    """

    def dispatch(self, task_card: object) -> object: ...


class ActiveTaskQueue:
    """后台任务队列——从 READY 池拉取任务并自动分发。

    内部使用 threading.Event 管理启停。
    可注册 EventHook 回调实现 push 式调度（减少轮询延迟）。
    """

    def __init__(
        self,
        repo: TaskRepositoryProtocol,
        orchestrator: PipelineDispatcher | None = None,
        *,
        poll_interval: float = _POLL_INTERVAL,
        max_per_cycle: int = _MAX_PER_CYCLE,
    ) -> None:
        self._repo = repo
        self._orchestrator = orchestrator
        self._poll_interval = poll_interval
        self._max_per_cycle = max_per_cycle

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._stats: dict[str, int] = {"dispatched": 0, "errors": 0, "cycles": 0}
        # 5.142.8 修复: _stats 后台线程写 + 属性读无锁, 用 _stats_lock 保护读写避免半更新值
        self._stats_lock = threading.Lock()

    # ── public API ──────────────────────────────────────────────────

    def start(self, *, daemon: bool = True) -> None:
        """启动后台轮询线程。"""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=daemon, name="zephyr-task-queue")
        self._thread.start()
        logger.info("ActiveTaskQueue started (interval=%.1fs, max/cycle=%d)", self._poll_interval, self._max_per_cycle)

    def stop(self, *, timeout: float = 5.0) -> None:
        """停止后台轮询线程并等待退出。"""
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        # 5.142.8 修复: 读取 _stats 加锁, 与后台 _loop/_tick 写入互斥
        with self._stats_lock:
            errors = self._stats["errors"]
            dispatched = self._stats["dispatched"]
        # 5.53.3 修复：原无条件 INFO，累计大量 errors 时信息被埋在 INFO 中。errors>0 时用 WARNING。
        if errors > 0:
            logger.warning("ActiveTaskQueue stopped (dispatched=%d, errors=%d)", dispatched, errors)
        else:
            logger.info("ActiveTaskQueue stopped (dispatched=%d, errors=%d)", dispatched, errors)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict[str, int]:
        # 5.142.8 修复: dict(self._stats) 迭代拷贝加锁, 避免读到半更新值
        with self._stats_lock:
            return dict(self._stats)

    # ── internal ────────────────────────────────────────────────────

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                n = self._tick()
            except Exception:
                logger.exception("ActiveTaskQueue tick failed", exc_info=True)
                # 5.142.8 修复: _stats 写入加锁
                with self._stats_lock:
                    self._stats["errors"] += 1
                n = 0
            # 5.142.8 修复: _stats 写入加锁
            with self._stats_lock:
                self._stats["cycles"] += 1
            wait = self._poll_interval if n == 0 else min(1.0, self._poll_interval / 2)
            self._stop_event.wait(timeout=wait)

    def _tick(self) -> int:
        ready = self._repo.list_by_status("READY")
        dispatched = 0
        for task_card in ready[: self._max_per_cycle]:
            try:
                self._repo.transition(task_card.task_id, "IN_PROGRESS")
                if self._orchestrator is not None:
                    self._orchestrator.dispatch(task_card)
                dispatched += 1
                # 5.142.8 修复: _stats 写入加锁
                with self._stats_lock:
                    self._stats["dispatched"] += 1
                logger.info("Queue dispatched %s", task_card.task_id)
            except Exception:
                logger.exception("Queue failed to dispatch %s", task_card.task_id, exc_info=True)
                # 5.142.8 修复: _stats 写入加锁
                with self._stats_lock:
                    self._stats["errors"] += 1
        return dispatched


_queue: ActiveTaskQueue | None = None
_queue_lock = threading.Lock()


def get_queue(
    repo: TaskRepository,
    orchestrator: PipelineDispatcher | None = None,
) -> ActiveTaskQueue:
    global _queue
    if _queue is None:
        with _queue_lock:
            if _queue is None:
                _queue = ActiveTaskQueue(repo, orchestrator)
    return _queue


# 5.137.1 修复：魔数提取为命名常量
_DEFAULT_MAX_SIZE = 1000
_DEFAULT_PRIORITY_LEVELS = 3
_DEFAULT_TIMEOUT_SEC = 300
_DEFAULT_RETRY_LIMIT = 3


class QueueConfig:
    def __init__(
        self,
        max_size: int = _DEFAULT_MAX_SIZE,
        priority_levels: int = _DEFAULT_PRIORITY_LEVELS,
        timeout: int = _DEFAULT_TIMEOUT_SEC,
        retry_limit: int = _DEFAULT_RETRY_LIMIT,
    ):
        self.max_size = max_size
        self.priority_levels = priority_levels
        self.timeout = timeout
        self.retry_limit = retry_limit


class QueueItem:
    def __init__(self, item_id="", task=None, priority=0, created_at=None, status="pending"):
        self.item_id = item_id
        self.task = task
        self.priority = priority
        self.created_at = created_at
        self.status = status


class QueueItemStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# TaskQueue 别名已移除（Q9 修复 2026-07-05）：core 不应提供兼容别名，
# compat shim 在 orchestrator/task_queue.py 提供 TaskQueue = ActiveTaskQueue。
# 旧 import 应走 compat shim 或直接使用 ActiveTaskQueue。