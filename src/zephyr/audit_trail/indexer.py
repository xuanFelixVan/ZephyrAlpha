"""
audit_trail.indexer — MOD-INF-020 · JSONL→SQLite 派生索引器
==============================================================
蓝图 §3.2 · JSONL SSoT → SQLite 派生索引——查询加速 + BatchOrchestrator 消费

架构
----
  JSONL (SSoT) → 全量扫描 → SQLite (derived_index)
  - 索引表: audit_entries (按 entry_id 主键)
  - 聚合表: audit_summary (按 session/agent/event_type 预聚合)
  - 哈希链验证表: integrity_records (每次重建记录哈希链快照)

对标: MOD-INF-012 Database——SQLite 派生查询索引的存储
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from zephyr.shared.schema.schemas import BASE_CONFIG

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/audit_trail/audit_index.db")
DEFAULT_EVENTS_PATH = Path("data/audit_trail/events.jsonl")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_entries (
    entry_id      TEXT PRIMARY KEY,
    event_type    TEXT NOT NULL,
    timestamp     TEXT NOT NULL,
    lamport       INTEGER NOT NULL DEFAULT 0,
    agent_id      TEXT NOT NULL DEFAULT '',
    session_id    TEXT NOT NULL DEFAULT '',
    target_path   TEXT NOT NULL DEFAULT '',
    operation     TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT '',
    provenance    TEXT NOT NULL DEFAULT 'direct_agent',
    entry_hash    TEXT NOT NULL DEFAULT '',
    prev_entry_hash TEXT NOT NULL DEFAULT '',
    merkle_batch_id TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_agent
    ON audit_entries(agent_id);
CREATE INDEX IF NOT EXISTS idx_audit_session
    ON audit_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type
    ON audit_entries(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp
    ON audit_entries(timestamp);

CREATE TABLE IF NOT EXISTS audit_summary (
    summary_id   TEXT PRIMARY KEY,
    agent_id     TEXT NOT NULL DEFAULT '',
    session_id   TEXT NOT NULL DEFAULT '',
    event_type   TEXT NOT NULL DEFAULT '',
    event_count  INTEGER NOT NULL DEFAULT 0,
    first_event  TEXT NOT NULL DEFAULT '',
    last_event   TEXT NOT NULL DEFAULT '',
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS integrity_records (
    record_id   TEXT PRIMARY KEY,
    chain_hash  TEXT NOT NULL DEFAULT '',
    prev_hash   TEXT NOT NULL DEFAULT '',
    event_count INTEGER NOT NULL DEFAULT 0,
    merkle_root TEXT NOT NULL DEFAULT '',
    timestamp   TEXT NOT NULL DEFAULT '',
    verified    INTEGER NOT NULL DEFAULT 0,
    issues      TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_integrity_ts
    ON integrity_records(timestamp);
"""


class IndexResult(BaseModel):
    model_config = BASE_CONFIG

    status: str = ""
    events_scanned: int = 0
    events_indexed: int = 0
    new_entries: int = 0
    errors: list[str] = []


class AuditIndexer:
    """JSONL → SQLite 派生索引器。

    使用方式:
        indexer = AuditIndexer()
        result = indexer.rebuild()
    """

    def __init__(
        self,
        db_path: Path | str = DEFAULT_DB_PATH,
        events_path: Path | str = DEFAULT_EVENTS_PATH,
    ) -> None:
        self._db_path = Path(db_path)
        self._events_path = Path(events_path)

    def rebuild(self) -> IndexResult:
        self._ensure_schema()

        events = self._load_events()
        if not events:
            return IndexResult(status="no_data", events_scanned=0, events_indexed=0)

        errors: list[str] = []
        indexed = 0
        new_entries = 0

        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                existing = self._existing_entry_ids(conn)

                for event in events:
                    eid = event.get("entry_id", "")
                    if not eid:
                        errors.append(f"missing entry_id in event: {event.get('timestamp', '?')}")
                        continue

                    should_insert = eid not in existing

                    self._upsert_entry(conn, event, should_insert)
                    self._update_summary(conn, event)
                    indexed += 1
                    if should_insert:
                        new_entries += 1

                self._record_integrity_snapshot(conn, events)

                conn.commit()
        except Exception as exc:
            logger.exception("Index rebuild failed")
            errors.append(str(exc))
            return IndexResult(
                status="error",
                events_scanned=len(events),
                events_indexed=indexed,
                new_entries=new_entries,
                errors=errors,
            )

        return IndexResult(
            status="ok",
            events_scanned=len(events),
            events_indexed=indexed,
            new_entries=new_entries,
            errors=errors,
        )

    def query_stats(self) -> dict[str, Any]:
        if not self._db_path.exists():
            return {"total": 0, "by_event_type": {}, "by_agent": {}}

        with sqlite3.connect(str(self._db_path)) as conn:
            conn.row_factory = sqlite3.Row

            total = conn.execute("SELECT COUNT(*) as cnt FROM audit_entries").fetchone()
            by_type = {
                row["event_type"]: row["cnt"]
                for row in conn.execute(
                    "SELECT event_type, COUNT(*) as cnt FROM audit_entries GROUP BY event_type ORDER BY cnt DESC"
                ).fetchall()
            }
            by_agent = {
                row["agent_id"]: row["cnt"]
                for row in conn.execute(
                    "SELECT agent_id, COUNT(*) as cnt FROM audit_entries GROUP BY agent_id ORDER BY cnt DESC"
                ).fetchall()
            }

            return {
                "total": total["cnt"] if total else 0,
                "by_event_type": by_type,
                "by_agent": by_agent,
            }

    def _ensure_schema(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    def _load_events(self) -> list[dict[str, Any]]:
        if not self._events_path.exists():
            return []

        events: list[dict[str, Any]] = []
        with open(self._events_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    @staticmethod
    def _existing_entry_ids(conn: sqlite3.Connection) -> set[str]:
        rows = conn.execute("SELECT entry_id FROM audit_entries").fetchall()
        return {r[0] for r in rows}

    @staticmethod
    def _upsert_entry(conn: sqlite3.Connection, event: dict[str, Any], should_insert: bool) -> None:
        if should_insert:
            conn.execute(
                """INSERT OR REPLACE INTO audit_entries
                   (entry_id, event_type, timestamp, lamport, agent_id, session_id,
                    target_path, operation, status, provenance, entry_hash,
                    prev_entry_hash, merkle_batch_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.get("entry_id", ""),
                    event.get("event_type", "unknown"),
                    event.get("timestamp", ""),
                    event.get("lamport", 0),
                    event.get("agent_id", ""),
                    event.get("session_id", ""),
                    event.get("target_path", ""),
                    event.get("operation", ""),
                    event.get("status", ""),
                    event.get("provenance", "direct_agent"),
                    event.get("entry_hash", ""),
                    event.get("prev_entry_hash", ""),
                    event.get("merkle_batch_id", ""),
                ),
            )
        else:
            conn.execute(
                """UPDATE audit_entries SET
                   event_type=?, timestamp=?, lamport=?, status=?, entry_hash=?,
                   prev_entry_hash=?
                   WHERE entry_id=?""",
                (
                    event.get("event_type", "unknown"),
                    event.get("timestamp", ""),
                    event.get("lamport", 0),
                    event.get("status", ""),
                    event.get("entry_hash", ""),
                    event.get("prev_entry_hash", ""),
                    event.get("entry_id", ""),
                ),
            )

    @staticmethod
    def _update_summary(conn: sqlite3.Connection, event: dict[str, Any]) -> None:
        agent_id = event.get("agent_id", "")
        session_id = event.get("session_id", "")
        event_type = event.get("event_type", "")
        summary_id = f"{agent_id}|{session_id}|{event_type}"

        conn.execute(
            """INSERT INTO audit_summary (summary_id, agent_id, session_id, event_type)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(summary_id) DO UPDATE SET
                   event_count = event_count + 1,
                   last_event = excluded.last_event || '',
                   updated_at = datetime('now')""",
            (summary_id, agent_id, session_id, event_type),
        )

    @staticmethod
    def _record_integrity_snapshot(
        conn: sqlite3.Connection,
        events: list[dict[str, Any]],
    ) -> None:
        import hashlib

        if not events:
            return

        last = events[-1]
        entry_hashes = [e.get("entry_hash", "") for e in events if e.get("entry_hash")]

        merkle_root = ""
        if entry_hashes:
            from zephyr.audit_trail.integrity import MerkleAggregator
            merkle_root = MerkleAggregator.build(entry_hashes)

        snapshot_hash = hashlib.sha256(
            json.dumps(
                {"count": len(events), "last_entry": last.get("entry_id", "")},
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()

        conn.execute(
            """INSERT INTO integrity_records
               (record_id, chain_hash, prev_hash, event_count, merkle_root, timestamp, verified, issues)
               VALUES (?, ?, ?, ?, ?, datetime('now'), 1, '[]')""",
            (snapshot_hash[:16], snapshot_hash, last.get("entry_hash", ""), len(events), merkle_root),
        )
