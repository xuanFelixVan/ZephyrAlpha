# [A_test] module_id: SRC-TST-1339 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_rollback_manager
# [INVARIANTS] RollbackManager uses real SQLite via db_utils; tests use in-memory DB with schema
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_rollback_manager.py
# [TTL] task_bound

from __future__ import annotations

import json
import sqlite3

import pytest

from zephyr.orchestrator.rollback_manager import Checkpoint, RollbackManager


def _create_test_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'PENDING',
            phase INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL DEFAULT '',
            execution_model TEXT NOT NULL DEFAULT 'deepseek',
            safety_level TEXT NOT NULL DEFAULT 'L',
            directive TEXT NOT NULL DEFAULT '',
            depends_on TEXT NOT NULL DEFAULT '[]',
            files_in_scope TEXT NOT NULL DEFAULT '[]',
            session_id TEXT,
            waiting_for TEXT,
            ready_at TEXT,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL DEFAULT '{}',
            task_id TEXT,
            session_id TEXT,
            created_at TEXT NOT NULL,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


def _insert_task(db_path, task_id, status="PENDING", title="Test Task", phase=0):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(
        "INSERT OR REPLACE INTO tasks (task_id, status, phase, title, execution_model, safety_level, directive, depends_on, files_in_scope, created_at, updated_at) VALUES (?, ?, ?, ?, 'deepseek', 'L', '', '[]', '[]', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')",
        (task_id, status, phase, title),
    )
    conn.commit()
    conn.close()


def _get_task_status(db_path, task_id):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    conn.close()
    return row["status"] if row else None


@pytest.fixture
def test_db(tmp_path):
    db_path = _create_test_db(tmp_path)
    return db_path


@pytest.fixture
def manager(test_db):
    return RollbackManager(db_path=test_db)


class TestCheckpoint:
    def test_creation(self):
        cp = Checkpoint(checkpoint_id="CP-1", created_at="2026-01-01", description="test", task_count=5)
        assert cp.checkpoint_id == "CP-1"
        assert cp.task_count == 5


class TestRollbackManagerCheckpoint:
    def test_checkpoint_returns_id(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        cp_id = manager.checkpoint("initial state")
        assert cp_id.startswith("CP-")

    def test_checkpoint_stores_snapshot(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        _insert_task(test_db, "T-2", "IN_PROGRESS")
        cp_id = manager.checkpoint("two tasks")
        conn = sqlite3.connect(str(test_db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT payload FROM events WHERE event_id = ?", (cp_id,)).fetchone()
        conn.close()
        snapshot = json.loads(row["payload"])
        assert len(snapshot) == 2

    def test_checkpoint_empty_db(self, manager):
        cp_id = manager.checkpoint("empty")
        assert cp_id.startswith("CP-")


class TestRollbackManagerRollbackTo:
    def test_rollback_restores_status(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        cp_id = manager.checkpoint("before change")
        conn = sqlite3.connect(str(test_db))
        conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = 'T-1'")
        conn.commit()
        conn.close()
        assert _get_task_status(test_db, "T-1") == "COMPLETED"
        count = manager.rollback_to(cp_id)
        assert count == 1
        assert _get_task_status(test_db, "T-1") == "PENDING"

    def test_rollback_nonexistent_checkpoint_raises(self, manager):
        with pytest.raises(ValueError, match="Checkpoint not found"):
            manager.rollback_to("CP-NONEXISTENT")

    def test_rollback_returns_task_count(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        _insert_task(test_db, "T-2", "IN_PROGRESS")
        cp_id = manager.checkpoint("two tasks")
        count = manager.rollback_to(cp_id)
        assert count == 2


class TestRollbackManagerListCheckpoints:
    def test_list_checkpoints_empty(self, manager):
        cps = manager.list_checkpoints()
        assert cps == []

    def test_list_checkpoints_returns_checkpoints(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        manager.checkpoint("first")
        cps = manager.list_checkpoints()
        assert len(cps) == 1
        assert isinstance(cps[0], Checkpoint)
        assert cps[0].task_count == 1

    def test_list_checkpoints_multiple(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        manager.checkpoint("first")
        _insert_task(test_db, "T-2", "IN_PROGRESS")
        manager.checkpoint("second")
        cps = manager.list_checkpoints()
        assert len(cps) == 2


class TestRollbackManagerUndoLast:
    def test_undo_last_returns_checkpoint_id(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        manager.checkpoint("first")
        result = manager.undo_last()
        assert result is not None
        assert result.startswith("CP-")

    def test_undo_last_none_when_no_checkpoints(self, manager):
        result = manager.undo_last()
        assert result is None

    def test_undo_last_restores_state(self, manager, test_db):
        _insert_task(test_db, "T-1", "PENDING")
        manager.checkpoint("before")
        conn = sqlite3.connect(str(test_db))
        conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = 'T-1'")
        conn.commit()
        conn.close()
        manager.undo_last()
        assert _get_task_status(test_db, "T-1") == "PENDING"
