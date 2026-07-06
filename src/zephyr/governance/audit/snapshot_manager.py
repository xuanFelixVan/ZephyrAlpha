# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §event-sourcing
# [MODULE] zephyr.governance.audit.snapshot_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.event_store; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.governance.observability_governance.projection_engine; zephyr.governance.audit_trail.event_store
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] snapshot_json is valid JSON; last_event_timestamp tracks replay cutoff; create_snapshot is atomic
# [MODIFY-GUARD] task_snapshots schema changes MUST go through sqlite_schema migration
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SnapshotError on write failure
# [TESTS] tests/test_event_store_stress.py
# [A_module] module_id=MOD-DAT_snapshot_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SnapshotManager — Event Sourcing 快照管理（DW-0005）
=====================================================
定期将事件流折叠结果持久化到 task_snapshots 表，加速后续 replay。

功能：
- create_snapshot(task_id, state): 保存当前状态快照
- load_latest_snapshot(task_id): 加载最近快照
- get_replay_start(task_id): 返回 (snapshot_state, events_after_snapshot) 高效回放

使用 task_snapshots 表（v18 创建，v19 新增 last_event_timestamp 列）。
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from zephyr.governance.audit_trail.event_store import EventRecord, EventStore
from zephyr.governance.persistence.sqlite_schema import SchemaManager, get_db_connection
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

__all__ = [
    "SnapshotError",
    "SnapshotManager",
]


class SnapshotError(RuntimeError):
    """快照操作失败。"""
    error_code = "ZA-GV-0002"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class SnapshotManager:
    """Event Sourcing 快照管理器。

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
        self._event_store: EventStore | None = None

    def _get_event_store(self) -> EventStore:
        if self._event_store is None:
            self._event_store = EventStore(self._db_path, auto_init=False)
        return self._event_store

    def close(self) -> None:
        if self._event_store is not None:
            self._event_store.close()
            self._event_store = None
        if self._conn is not None:
            self._conn.close()

    def __enter__(self) -> SnapshotManager:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def create_snapshot(
        self,
        task_id: str,
        state: dict,
    ) -> int:
        """保存当前状态快照到 task_snapshots 表。

        参数
        ----
        task_id
            目标任务 ID。
        state
            当前折叠状态 dict。

        返回
        ----
        int
            snapshot_id（自增主键）。
        """
        snapshot_json = dumps(state, ensure_ascii=False)
        now = datetime.now(UTC).isoformat()

        last_event_timestamp = state.get("_last_event_timestamp")
        last_event_id = state.get("_last_event_id", 0)

        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                """INSERT INTO task_snapshots (task_id, snapshot_json, last_event_id, last_event_timestamp, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (task_id, snapshot_json, last_event_id, last_event_timestamp, now),
            )
            snapshot_id = self._conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

        return snapshot_id

    def load_latest_snapshot(self, task_id: str) -> dict | None:
        """加载指定 task_id 的最近快照。

        返回
        ----
        dict | None
            最近快照的状态 dict，无快照时返回 None。
        """
        cursor = self._conn.execute(
            """SELECT snapshot_json, last_event_timestamp
               FROM task_snapshots
               WHERE task_id = ?
               ORDER BY created_at DESC, snapshot_id DESC
               LIMIT 1""",
            (task_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        try:
            state = json.loads(row["snapshot_json"])
        except (json.JSONDecodeError, TypeError):
            return None
        return state

    def get_replay_start(self, task_id: str) -> tuple[dict, list[EventRecord]]:
        """返回 (snapshot_state, events_after_snapshot) 用于高效回放。

        如果存在快照，只回放快照之后的事件；否则回放全部事件。

        参数
        ----
        task_id
            目标任务 ID。

        返回
        ----
        tuple[dict, list[EventRecord]]
            (快照状态或空 dict, 需要回放的事件列表)
        """
        cursor = self._conn.execute(
            """SELECT snapshot_json, last_event_timestamp
               FROM task_snapshots
               WHERE task_id = ?
               ORDER BY created_at DESC
               LIMIT 1""",
            (task_id,),
        )
        row = cursor.fetchone()

        if row is None:
            store = self._get_event_store()
            all_events = store.replay_events(task_id)
            return {}, all_events

        try:
            snapshot_state = json.loads(row["snapshot_json"])
        except (json.JSONDecodeError, TypeError):
            snapshot_state = {}

        cutoff_timestamp = row["last_event_timestamp"]

        store = self._get_event_store()
        if cutoff_timestamp:
            all_events = store.replay_events(task_id)
            last_event_id = snapshot_state.get("_last_event_id")
            if last_event_id:
                cutoff_idx = -1
                for i, ev in enumerate(all_events):
                    if ev.event_id == last_event_id:
                        cutoff_idx = i
                        break
                events_after = all_events[cutoff_idx + 1 :] if cutoff_idx >= 0 else all_events
            else:
                cutoff_idx = -1
                for i, ev in enumerate(all_events):
                    if ev.timestamp <= cutoff_timestamp:
                        cutoff_idx = i
                events_after = all_events[cutoff_idx + 1 :] if cutoff_idx >= 0 else all_events
        else:
            events_after = store.replay_events(task_id)

        return snapshot_state, events_after
