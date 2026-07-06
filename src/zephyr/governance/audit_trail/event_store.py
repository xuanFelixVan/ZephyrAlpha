# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §event-sourcing
# [MODULE] zephyr.governance.audit_trail.event_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.governance.observability_governance.projection_engine; zephyr.governance.audit.snapshot_manager; zephyr.governance.persistence.task_repo
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] event_id is UUID4; timestamp is UTC ISO 8601; append_event is atomic within BEGIN IMMEDIATE
# [MODIFY-GUARD] task_events schema changes MUST go through sqlite_schema migration
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventStoreError on write failure; IntegrityError on verify_integrity failure
# [TESTS] tests/test_event_store_stress.py
# [A_module] module_id=MOD-DAT_event_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EventStore — Event Sourcing 事件追加与回放（DW-0002）
=====================================================
append-only 事件存储，支持：
- append_event: 原子追加事件（UUID event_id + UTC timestamp）
- replay_events: 按 task_id 时间顺序回放全部事件
- verify_integrity: 校验事件链完整性（时间戳单调递增 + event_id 唯一性）

线程安全：通过 SQLite BEGIN IMMEDIATE 事务保证写串行化。
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from zephyr.governance.persistence.sqlite_schema import SchemaManager, get_db_connection
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

__all__ = [
    "EventRecord",
    "EventStore",
    "EventStoreError",
    "IntegrityError",
]


class EventStoreError(RuntimeError):
    """EventStore 基础异常。"""

    error_code = "ZA-GV-0010"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class IntegrityError(EventStoreError):
    """事件链完整性校验失败。"""


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    task_id: str
    event_type: str
    payload: str
    timestamp: str
    session_id: str | None
    # 5.57.2: seq 单调序列号（消费者可检测乱序）；5.57.6: prev_hash 完整性链
    seq: int = 0
    prev_hash: str = ""


class EventStore:
    """Event Sourcing 事件存储——append-only 写入 + 时间顺序回放 + 完整性校验。

    参数
    ----
    db_path
        SQLite 数据库路径；默认 DB_PATH。
    auto_init
        为 True 时在构造时调用 SchemaManager.ensure_task_events_table()。
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        auto_init: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        if auto_init:
            SchemaManager.ensure_task_events_table(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()

    def __enter__(self) -> EventStore:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def append_event(
        self,
        task_id: str,
        event_type: str,
        payload: dict | str | None = None,
        session_id: str | None = None,
    ) -> str:
        """原子追加一条事件，返回 event_id。

        参数
        ----
        task_id
            关联的任务 ID。
        event_type
            事件类型（如 CREATED / STATUS_CHANGED / PRIORITY_CHANGED / FIELD_UPDATED）。
        payload
            事件载荷，dict 或 JSON 字符串。None 视为空 dict。
        session_id
            可选的 session 标识。

        返回
        ----
        str
            自动生成的 UUID4 event_id。
        """
        event_id = str(uuid.uuid4())
        timestamp = self._now_iso()
        if payload is None:
            payload_str = "{}"
        elif isinstance(payload, dict):
            payload_str = json.dumps(payload, ensure_ascii=False)
        else:
            payload_str = payload

        # 5.57.2: 获取 per-task 单调递增 seq；5.57.6: 计算前一条事件 prev_hash
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                """SELECT event_id, task_id, event_type, payload, timestamp, session_id,
                          COALESCE(seq, 0) AS seq, COALESCE(prev_hash, '') AS prev_hash
                   FROM task_events
                   WHERE task_id = ?
                   ORDER BY seq DESC, timestamp DESC, rowid DESC
                   LIMIT 1""",
                (task_id,),
            ).fetchone()
            if row is not None:
                prev_seq = int(row["seq"])
                # 5.57.6: prev_hash = SHA256(前一条事件规范化串)
                canonical = f"{row['event_id']}|{row['task_id']}|{row['event_type']}|{row['payload']}|{row['timestamp']}|{row['session_id'] or ''}"
                prev_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            else:
                prev_seq = 0
                prev_hash = ""
            next_seq = prev_seq + 1

            self._conn.execute(
                """INSERT INTO task_events (event_id, task_id, event_type, payload, timestamp, session_id, seq, prev_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (event_id, task_id, event_type, payload_str, timestamp, session_id, next_seq, prev_hash),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

        return event_id

    def replay_events(self, task_id: str) -> list[EventRecord]:
        """按时间顺序回放指定 task_id 的全部事件。

        返回
        ----
        list[EventRecord]
            按 seq ASC 排序的事件记录列表（5.57.2: 单调序列号保证因果顺序）。
        """
        cursor = self._conn.execute(
            """SELECT event_id, task_id, event_type, payload, timestamp, session_id,
                      COALESCE(seq, 0) AS seq, COALESCE(prev_hash, '') AS prev_hash
               FROM task_events
               WHERE task_id = ?
               ORDER BY seq ASC, timestamp ASC, rowid ASC""",
            (task_id,),
        )
        return [
            EventRecord(
                event_id=row["event_id"],
                task_id=row["task_id"],
                event_type=row["event_type"],
                payload=row["payload"],
                timestamp=row["timestamp"],
                session_id=row["session_id"],
                seq=int(row["seq"]),
                prev_hash=row["prev_hash"],
            )
            for row in cursor.fetchall()
        ]

    def verify_integrity(self, task_id: str) -> dict:
        """校验指定 task_id 的事件链完整性。

        检查项：
        1. event_id 唯一性（PRIMARY KEY 保证）
        2. seq 单调递增（5.57.2）
        3. payload 为合法 JSON
        4. checksum 链连续性（每条事件的 prev_hash = SHA256(前一条事件序列化)）
           5.57.6 治本：比较数据库存储的 prev_hash 与重计算的 expected_prev_hash，
           不一致=数据库 at-rest 篡改/payload 被改/事件被删

        返回
        ----
        dict
            {valid: bool, errors: list[str], event_count: int, last_timestamp: str | None}
        """
        events = self.replay_events(task_id)
        errors: list[str] = []
        prev_hash = ""
        seen_ids: set[str] = set()

        for i, ev in enumerate(events):
            if ev.event_id in seen_ids:
                errors.append(f"Duplicate event_id: {ev.event_id} at position {i}")
            seen_ids.add(ev.event_id)

            # 5.57.2: seq 单调递增校验
            if i > 0:
                prev_ev = events[i - 1]
                if ev.seq <= prev_ev.seq:
                    errors.append(f"Seq regression at position {i}: seq={ev.seq} <= prev_seq={prev_ev.seq}")

            try:
                json.loads(ev.payload)
            except (json.JSONDecodeError, TypeError) as exc:
                errors.append(f"Invalid JSON payload at position {i}: {exc}")

            # 5.57.6 治本：比较存储的 prev_hash 与重计算的 expected_prev_hash
            if i > 0:
                expected_prev_hash = prev_hash
                # 容忍空值（migration 前历史数据 seq/prev_hash 为空/0）
                if ev.prev_hash and expected_prev_hash and ev.prev_hash != expected_prev_hash:
                    errors.append(
                        f"Hash chain broken at position {i}: stored prev_hash={ev.prev_hash[:12]}... "
                        f"!= expected={expected_prev_hash[:12]}... (at-rest tampering detected)"
                    )

            canonical = f"{ev.event_id}|{ev.task_id}|{ev.event_type}|{ev.payload}|{ev.timestamp}|{ev.session_id or ''}"
            prev_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "event_count": len(events),
            "last_timestamp": events[-1].timestamp if events else None,
        }
