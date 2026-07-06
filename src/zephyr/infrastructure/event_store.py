# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.event_store
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.sqlite_factory; zephyr.shared.io.paths
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
# [A_module] module_id=MOD-INF_audit_event_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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

import logging

logger = logging.getLogger(__name__)

import json
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
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

    def to_row(self) -> tuple[Any, ...]:
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
    def from_row(cls, row: dict[str, Any]) -> StoredEvent:
        return cls(
            event_id=row["event_id"],
            timestamp=row["timestamp"],
            level=EventLevel(row["level"]),
            component=row["component"],
            event_type=row["event_type"],
            payload=json.loads(row["payload"]) if row["payload"] else {},
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )


# class-name-alias: 审计日志事件存储（RI-13），区别于 events/event_store.py 的任务领域事件存储（JSONL）
class EventStore:
    """事件存储——基于 SQLite 的不可篡改审计日志

    特性：
    - SQLite WAL 模式高并发写入
    - SHA256 checksum 防篡改
    - 按时间/组件/级别多维度查询
    - 线程安全
    """

    def __init__(self, db_path: str | Path = REPO_ROOT / "data" / "events.db", auto_init: bool = True) -> None:
        self._db_path = Path(db_path)
        # 5.142.7 修复: 移除全局 self._lock (串行化抵消WAL并发收益), 改用线程局部连接
        # 依赖 SQLite timeout=10 忙等待锁 + WAL 模式处理并发 (读不阻塞写, 写不阻塞读)
        self._local = threading.local()
        self._all_conns: dict[int, sqlite3.Connection] = {}
        self._all_conns_lock = threading.Lock()

        if auto_init:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            self._migrate()

    @property
    def _conn(self) -> sqlite3.Connection:
        """5.142.7 修复: 线程局部连接复用, 避免每次操作创建/关闭连接的开销."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = get_db_connection(str(self._db_path), timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
            tid = threading.get_ident()
            with self._all_conns_lock:
                self._all_conns[tid] = conn
        return self._local.conn

    def _init_db(self) -> None:
        conn = self._conn
        conn.executescript(EVENT_STORE_SCHEMA)
        conn.commit()

    def _migrate(self) -> None:
        pass

    def record(self, event: StoredEvent) -> str:
        conn = self._conn
        conn.execute(
            "INSERT INTO events (event_id,timestamp,level,component,event_type,payload,metadata,checksum) VALUES (?,?,?,?,?,?,?,?)",
            event.to_row(),
        )
        conn.commit()
        return event.event_id

    def record_batch(self, events: list[StoredEvent]) -> int:
        if not events:
            return 0
        conn = self._conn
        conn.executemany(
            "INSERT INTO events (event_id,timestamp,level,component,event_type,payload,metadata,checksum) VALUES (?,?,?,?,?,?,?,?)",
            [e.to_row() for e in events],
        )
        conn.commit()
        return len(events)

    def query(
        self,
        component: str | None = None,
        level: EventLevel | None = None,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredEvent]:
        conn = self._conn
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

    def count(self, component: str | None = None) -> int:
        conn = self._conn
        if component:
            row = conn.execute("SELECT COUNT(*) FROM events WHERE component = ?", (component,)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0] if row else 0

    def verify_integrity(self, event_id: str) -> bool:
        conn = self._conn
        row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
        if not row:
            return False
        stored = StoredEvent.from_row(dict(row))
        import hashlib

        payload_str = json.dumps(stored.payload, ensure_ascii=False)
        expected = hashlib.sha256(f"{stored.event_id}{stored.timestamp}{payload_str}".encode()).hexdigest()[:16]
        return expected == row["checksum"]

    def close_all(self) -> None:
        """5.142.7 修复: 关闭所有线程的连接 (线程池场景下 close() 只关闭当前线程连接不够)."""
        with self._all_conns_lock:
            for tid, conn in list(self._all_conns.items()):
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("suppressed error in event_store", exc_info=True)
            self._all_conns.clear()
        if hasattr(self._local, "conn"):
            self._local.conn = None

    def close(self) -> None:
        self.close_all()
