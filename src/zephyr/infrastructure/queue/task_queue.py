# [BLUEPRINT] SRC-130 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.queue.task_queue
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Task Queue — 后台任务队列 + 自动 Dispatch。

依据：
    蓝图 MOD-TASK_SYSTEM §13.3 路线图 #9 + v0.6.0
    任务卡 TASK-INF-0132 (Part 2/4)

功能：
    - 后台轮询 READY 任务
    - AI 自治允许时自动 dispatch
    - 间隔可配置（默认 5 分钟）
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT


class QueueItemStatus(str, Enum):
    ENQUEUED = "enqueued"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueItem:
    item_id: str
    task_id: str
    priority: str = "P2"
    status: QueueItemStatus = QueueItemStatus.ENQUEUED
    enqueued_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    dispatched_at: str = ""


@dataclass
class QueueConfig:
    poll_interval_s: int = 300
    auto_dispatch: bool = True
    max_concurrent: int = 1
    only_p0: bool = False


class TaskQueue:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or (REPO_ROOT / "data" / "queue")
        self._items: list[QueueItem] = []
        self._config = QueueConfig()
        self._running = False
        self._thread: threading.Thread | None = None
        self._dispatch_handler: Callable[[QueueItem], bool] | None = None
        self._lifecycle_lock = threading.Lock()  # 5.142.6 修复: 保护 start_polling/stop_polling 的 check-then-act, 避免 TOCTOU

    def enqueue(self, task_id: str, priority: str = "P2") -> QueueItem:
        item = QueueItem(
            item_id=f"QITEM-{task_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            task_id=task_id,
            priority=priority,
        )
        self._items.append(item)
        return item

    def dequeue_next(self) -> QueueItem | None:
        ready = [
            i
            for i in self._items
            if i.status == QueueItemStatus.ENQUEUED and (not self._config.only_p0 or i.priority == "P0")
        ]

        ready.sort(key=lambda x: {"P0": 0, "P1": 1, "P2": 2}.get(x.priority, 3))

        if ready:
            item = ready[0]
            item.status = QueueItemStatus.DISPATCHED
            item.dispatched_at = datetime.now(UTC).isoformat()
            return item

        return None

    def set_dispatch_handler(self, handler: Callable[[QueueItem], bool]) -> None:
        self._dispatch_handler = handler

    def start_polling(self) -> None:
        # 5.142.6 修复: 加锁保护 check-then-act, 防止并发创建多个线程
        with self._lifecycle_lock:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()

    def stop_polling(self) -> None:
        # 5.142.6 修复: 加锁保护 _running 写入, 防止与 start_polling() 竞争
        with self._lifecycle_lock:
            self._running = False

    def _poll_loop(self) -> None:
        while self._running:
            if self._config.auto_dispatch:
                item = self.dequeue_next()
                if item and self._dispatch_handler:
                    item.status = QueueItemStatus.RUNNING
                    success = self._dispatch_handler(item)
                    item.status = QueueItemStatus.COMPLETED if success else QueueItemStatus.FAILED

            time.sleep(self._config.poll_interval_s)

    def get_stats(self) -> dict[str, int]:
        stats: dict[str, int] = {s.value: 0 for s in QueueItemStatus}
        for item in self._items:
            stats[item.status.value] += 1
        return stats

    def clear_completed(self) -> int:
        before = len(self._items)
        self._items = [i for i in self._items if i.status not in (QueueItemStatus.COMPLETED, QueueItemStatus.FAILED)]
        return before - len(self._items)
