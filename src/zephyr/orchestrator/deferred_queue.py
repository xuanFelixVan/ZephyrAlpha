"""DeferredQueue: WAITING -> READY task scheduler.

Manages deferred task execution with event-driven state transitions.
Uses Observer as the messaging layer and SQLite for task persistence.

Task: T-1-09 | Phase 1 | GLM-5.1
ADR ref: ADR-0036 (pending Opus authoring)
Depends: observer.py (T-1-08), task_repo.py (T-1-04)
"""
from __future__ import annotations

import sqlite3
from threading import RLock
import time
from enum import Enum, unique
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from zephyr.shared.observer import EventType, Observer


@unique
class DeferredTaskStatus(str, Enum):
    """DeferredQueue 内部任务状态（非全局 TaskStatus，仅 WAITING→READY→RUNNING→DONE/FAILED）。"""

    WAITING = "WAITING"
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


DEFAULT_DB_PATH = ":memory:"


class DeferredQueue:
    """Thread-safe deferred task queue with event-driven wake-up.

    Tasks enter as WAITING and transition to READY when their
    ``waiting_for`` condition is satisfied via an Observer event.

    Usage::

        bus = Observer()
        dq = DeferredQueue(bus, db_path="tasks.db")
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
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

        for et in EventType:
            self._observer.subscribe(et, self._on_event)

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
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
        payload: Optional[str] = None,
    ) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO deferred_tasks (task_id, status, waiting_for, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (task_id, DeferredTaskStatus.WAITING.value, waiting_for, payload, time.time()),
            )
            conn.commit()

    def _on_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
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
        payload: Dict[str, Any],
    ) -> bool:
        if ":" in waiting_for:
            parts = waiting_for.split(":", 1)
            if parts[0] != event_name:
                return False
            if len(parts) > 1 and parts[1] in payload:
                return True
            return False
        return waiting_for == event_name

    def pop_ready(self, limit: int = 100) -> List[Dict[str, Any]]:
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

    def count_by_status(self) -> Dict[str, int]:
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM deferred_tasks GROUP BY status"
            )
            return {row["status"]: row["cnt"] for row in cursor.fetchall()}

    def bulk_wake(self, event_type: EventType, payload: Optional[Dict[str, Any]] = None) -> int:
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
