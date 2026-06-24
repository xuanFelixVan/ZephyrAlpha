# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infra_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.core.task_queue
# [DOMAIN] D-GOV_AUDIT
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
# [A_module] module_id=MOD-GOV_task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-INF-006 盲点#9
依赖: TaskRepository + Protocol:PipelineDispatcher + EventHook

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

AUDIT-08 H6 修复：不再直接导入 PipelineOrchestrator，改用 Protocol 解耦，
打破 pipeline ↔ orchestrator 双向循环依赖。

Usage:
    from zephyr.governance.audit_orchestration.core.task_queue import TaskQueue

    queue = TaskQueue(repo, orchestrator)
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

    任何实现了 ``dispatch(task_card)`` 方法的对象均可注入 TaskQueue，
    无需直接依赖 PipelineOrchestrator 类型。
    """

    def dispatch(self, task_card: object) -> object: ...


class TaskQueue:
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

    # ── public API ──────────────────────────────────────────────────

    def start(self, *, daemon: bool = True) -> None:
        """启动后台轮询线程。"""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=daemon, name="zephyr-task-queue")
        self._thread.start()
        logger.info("TaskQueue started (interval=%.1fs, max/cycle=%d)", self._poll_interval, self._max_per_cycle)

    def stop(self, *, timeout: float = 5.0) -> None:
        """停止后台轮询线程并等待退出。"""
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        logger.info("TaskQueue stopped (dispatched=%d, errors=%d)", self._stats["dispatched"], self._stats["errors"])

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    # ── internal ────────────────────────────────────────────────────

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                n = self._tick()
            except Exception:
                logger.exception("TaskQueue tick failed")
                self._stats["errors"] += 1
                n = 0
            self._stats["cycles"] += 1
            wait = self._poll_interval if n == 0 else min(1.0, self._poll_interval / 2)
            self._stop_event.wait(timeout=wait)

    def _tick(self) -> int:
        ready = self._repo.list_by_status("ready")
        dispatched = 0
        for task_card in ready[: self._max_per_cycle]:
            try:
                self._repo.transition(task_card.task_id, "IN_PROGRESS")
                if self._orchestrator is not None:
                    self._orchestrator.dispatch(task_card)
                dispatched += 1
                self._stats["dispatched"] += 1
                logger.info("Queue dispatched %s", task_card.task_id)
            except Exception:
                logger.exception("Queue failed to dispatch %s", task_card.task_id)
                self._stats["errors"] += 1
        return dispatched


_queue: TaskQueue | None = None


def get_queue(
    repo: TaskRepositoryProtocol,
    orchestrator: PipelineDispatcher | None = None,
) -> TaskQueue:
    global _queue
    if _queue is None:
        _queue = TaskQueue(repo, orchestrator)
    return _queue
