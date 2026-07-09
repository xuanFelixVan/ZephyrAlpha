# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.deferred_queue
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.infra.observer
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
# [A_module] module_id=MOD-ORC_deferred_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""DeferredQueue: WAITING -> READY task scheduler.

Manages deferred task execution with event-driven state transitions.
Uses Observer as the messaging layer and SQLite for task persistence.

Task: T-1-09 | experimental | GLM-5.1
Depends: observer.py (T-1-08), task_repo.py (T-1-04)
"""

from __future__ import annotations

from typing import Final
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import time
from enum import Enum, unique
from threading import RLock
from typing import Any

from zephyr.shared.infra.observer import EventType, Observer


@unique
class DeferredTaskStatus(str, Enum):
    """DeferredQueue 内部任务状态（非全局 TaskStatus，仅 WAITING->READY->RUNNING->DONE/FAILED）。"""

    WAITING = "WAITING"
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


DEFAULT_DB_PATH: Final[str] = ":memory:"


class DeferredQueue:
    """Thread-safe deferred task queue with event-driven wake-up.

    Tasks enter as WAITING and transition to READY when their
    ``waiting_for`` condition is satisfied via an Observer event.

    Usage::

        bus = Observer()
        dq = DeferredQueue(bus, db_path="data/databases/governance.db")
        dq.enqueue("task-1", waiting_for="file_event", payload={"path": "a.md"})
        bus.emit(EventType.FILE_EVENT, {"path": "a.md"})
        ready = dq.pop_ready()
    """

    def __init__(
        self,
        observer: Observer,
        db_path: str = DEFAULT_DB_PATH,
    ) -> None:
        self._observer = observer
        self._db_path = db_path
        self._lock = RLock()
        self._conn: sqlite3.Connection | None = None
        # 5.16.7 修复：_init_db 在锁内调用，确保 _get_conn 的 check-then-act 受锁保护
        with self._lock:
            self._init_db()

        for et in EventType:
            self._observer.subscribe(et, self._on_event)

    def _get_conn(self) -> sqlite3.Connection:
        # 5.16.7 修复：强制调用方持锁，防止新增方法忘记 with self._lock 导致竞态
        assert self._lock._is_owned(), "_get_conn must be called with self._lock held"
        if self._conn is None:
            self._conn = get_db_connection(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deferred_tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'WAITING',
                waiting_for TEXT NOT NULL,
                payload TEXT,
                created_at REAL NOT NULL,
                ready_at REAL,
                error_msg TEXT
            )
            """
        )
        conn.commit()

    def enqueue(
        self,
        task_id: str,
        waiting_for: str,
        payload: str | None = None,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO deferred_tasks (task_id, status, waiting_for, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (task_id, DeferredTaskStatus.WAITING.value, waiting_for, payload, time.time()),
            )
            conn.commit()

    def _on_event(self, event_type: EventType, payload: dict[str, Any]) -> None:
        event_name = event_type.value
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "SELECT task_id, waiting_for, payload FROM deferred_tasks WHERE status = ?",
                (DeferredTaskStatus.WAITING.value,),
            )
            rows = cursor.fetchall()

            for row in rows:
                wf = row["waiting_for"]
                if wf == event_name or self._condition_met(wf, event_name, payload):
                    conn.execute(
                        "UPDATE deferred_tasks SET status = ?, ready_at = ? WHERE task_id = ?",
                        (DeferredTaskStatus.READY.value, time.time(), row["task_id"]),
                    )
            conn.commit()

    def _condition_met(
        self,
        waiting_for: str,
        event_name: str,
        payload: dict[str, Any],
    ) -> bool:
        if ":" in waiting_for:
            parts = waiting_for.split(":", 1)
            if parts[0] != event_name:
                return False
            if len(parts) > 1 and parts[1] in payload:
                return True
            return False
        return waiting_for == event_name

    def pop_ready(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "SELECT task_id, waiting_for, payload, created_at, ready_at FROM deferred_tasks WHERE status = ? ORDER BY ready_at ASC LIMIT ?",
                (DeferredTaskStatus.READY.value, limit),
            )
            rows = cursor.fetchall()
            result = [dict(r) for r in rows]
            if result:
                ids = [r["task_id"] for r in result]
                placeholders = ",".join("?" * len(ids))
                conn.execute(
                    f"UPDATE deferred_tasks SET status = ? WHERE task_id IN ({placeholders})",
                    [DeferredTaskStatus.RUNNING.value] + ids,
                )
                conn.commit()
            return result

    def mark_done(self, task_id: str) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "UPDATE deferred_tasks SET status = ? WHERE task_id = ?",
                (DeferredTaskStatus.DONE.value, task_id),
            )
            conn.commit()

    def mark_failed(self, task_id: str, error_msg: str = "") -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "UPDATE deferred_tasks SET status = ?, error_msg = ? WHERE task_id = ?",
                (DeferredTaskStatus.FAILED.value, error_msg, task_id),
            )
            conn.commit()

    def count_by_status(self) -> dict[str, int]:
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute("SELECT status, COUNT(*) as cnt FROM deferred_tasks GROUP BY status")
            return {row["status"]: row["cnt"] for row in cursor.fetchall()}

    def bulk_wake(self, event_type: EventType, payload: dict[str, Any] | None = None) -> int:
        with self._lock:
            conn = self._get_conn()
            event_name = event_type.value
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt FROM deferred_tasks WHERE status = ? AND waiting_for = ?",
                (DeferredTaskStatus.WAITING.value, event_name),
            )
            count = cursor.fetchone()["cnt"]
            if count > 0:
                conn.execute(
                    "UPDATE deferred_tasks SET status = ?, ready_at = ? WHERE status = ? AND waiting_for = ?",
                    (DeferredTaskStatus.READY.value, time.time(), DeferredTaskStatus.WAITING.value, event_name),
                )
                conn.commit()
            return count

    def close(self) -> None:
        for et in EventType:
            self._observer.unsubscribe(et, self._on_event)
        if self._conn is not None:
            self._conn.close()
            self._conn = None
