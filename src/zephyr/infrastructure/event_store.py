# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.event_store
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_event_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
RI-13 EventStore — 事件存储
===========================
职责：持久化审计日志与事件溯源——所有关键操作必须留下不可篡改的记录。
使用方式：
    store = EventStore()  # 默认使用 REPO_ROOT / "data" / "events.db"
    store.record(event)
    events = store.query(component="gate_engine", limit=100)
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

__all__ = [
    "EVENT_STORE_SCHEMA",
    "EventLevel",
    "EventStore",
    "StoredEvent",
]


class EventLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


EVENT_STORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'info',
    component TEXT NOT NULL DEFAULT '',
    event_type TEXT NOT NULL DEFAULT '',
    payload TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}',
    checksum TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_component ON events(component);
CREATE INDEX IF NOT EXISTS idx_events_level ON events(level);
CREATE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id);
"""


@dataclass
class StoredEvent:
    event_id: str
    level: EventLevel = EventLevel.INFO
    component: str = ""
    event_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_row(self) -> tuple:
        import hashlib

        payload_str = json.dumps(self.payload, ensure_ascii=False)
        meta_str = json.dumps(self.metadata, ensure_ascii=False)
        checksum = hashlib.sha256(f"{self.event_id}{self.timestamp}{payload_str}".encode()).hexdigest()[:16]
        return (
            self.event_id,
            self.timestamp,
            self.level.value,
            self.component,
            self.event_type,
            payload_str,
            meta_str,
            checksum,
        )

    @classmethod
    def from_row(cls, row: dict) -> StoredEvent:
        return cls(
            event_id=row["event_id"],
            timestamp=row["timestamp"],
            level=EventLevel(row["level"]),
            component=row["component"],
            event_type=row["event_type"],
            payload=json.loads(row["payload"]) if row["payload"] else {},
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )


class EventStore:
    """事件存储——基于 SQLite 的不可篡改审计日志

    特性：
    - SQLite WAL 模式高并发写入
    - SHA256 checksum 防篡改
    - 按时间/组件/级别多维度查询
    - 线程安全
    """

    def __init__(self, db_path: str | Path = REPO_ROOT / "data" / "events.db", auto_init: bool = True):
        self._db_path = Path(db_path)
        self._lock = threading.Lock()

        if auto_init:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            self._migrate()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            try:
                conn.executescript(EVENT_STORE_SCHEMA)
                conn.commit()
            finally:
                conn.close()

    def _migrate(self) -> None:
        pass

    def record(self, event: StoredEvent) -> str:
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    "INSERT INTO events (event_id,timestamp,level,component,event_type,payload,metadata,checksum) VALUES (?,?,?,?,?,?,?,?)",
                    event.to_row(),
                )
                conn.commit()
                return event.event_id
            finally:
                conn.close()

    def record_batch(self, events: list[StoredEvent]) -> int:
        if not events:
            return 0
        with self._lock:
            conn = self._get_conn()
            try:
                conn.executemany(
                    "INSERT INTO events (event_id,timestamp,level,component,event_type,payload,metadata,checksum) VALUES (?,?,?,?,?,?,?,?)",
                    [e.to_row() for e in events],
                )
                conn.commit()
                return len(events)
            finally:
                conn.close()

    def query(
        self,
        component: str | None = None,
        level: EventLevel | None = None,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEvent]:
        with self._lock:
            conn = self._get_conn()
            try:
                conditions: list[str] = []
                params: list[Any] = []

                if component:
                    conditions.append("component = ?")
                    params.append(component)
                if level:
                    conditions.append("level = ?")
                    params.append(level.value)
                if event_type:
                    conditions.append("event_type = ?")
                    params.append(event_type)

                where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                sql = f"SELECT * FROM events {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                rows = conn.execute(sql, params).fetchall()
                return [StoredEvent.from_row(dict(r)) for r in rows]
            finally:
                conn.close()

    def count(self, component: str | None = None) -> int:
        with self._lock:
            conn = self._get_conn()
            try:
                if component:
                    row = conn.execute("SELECT COUNT(*) FROM events WHERE component = ?", (component,)).fetchone()
                else:
                    row = conn.execute("SELECT COUNT(*) FROM events").fetchone()
                return row[0] if row else 0
            finally:
                conn.close()

    def verify_integrity(self, event_id: str) -> bool:
        with self._lock:
            conn = self._get_conn()
            try:
                row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
                if not row:
                    return False
                stored = StoredEvent.from_row(dict(row))
                import hashlib

                payload_str = json.dumps(stored.payload, ensure_ascii=False)
                expected = hashlib.sha256(f"{stored.event_id}{stored.timestamp}{payload_str}".encode()).hexdigest()[:16]
                return expected == row["checksum"]
            finally:
                conn.close()

    def close(self) -> None:
        pass
