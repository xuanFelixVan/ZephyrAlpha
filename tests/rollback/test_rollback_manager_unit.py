# [A_test] module_id: SRC-TST-2060 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-677 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_rollback_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for rollback_manager.py (T-2-05)
"""


from pathlib import Path

import pytest

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.orchestrator.rollback_manager import RollbackManager


@pytest.fixture
def manager(tmp_db: Path) -> RollbackManager:
    return RollbackManager(db_path=tmp_db)


def _insert_task(conn, task_id: str, status: str = "PENDING") -> None:
    now = "2026-04-24T00:00:00+00:00"
    conn.execute("BEGIN")
    conn.execute(
        """INSERT OR REPLACE INTO tasks
           (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, depends_on, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 'P2', 2, 'glm', 'M', '[]', ?, ?)""",
        (task_id, task_id.split("-")[0], int(task_id.split("-")[-1]), task_id, status, now, now),
    )
    conn.execute("COMMIT")


class TestRollbackManagerCheckpoint:
    def test_checkpoint_returns_id(self, manager: RollbackManager, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        conn.close()
        cp_id = manager.checkpoint("initial")
        assert cp_id.startswith("CP-")

    def test_checkpoint_stores_snapshot(self, manager: RollbackManager, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "PENDING")
        conn.close()
        manager.checkpoint("initial")
        cps = manager.list_checkpoints()
        assert len(cps) == 1
        assert cps[0].task_count == 1

    def test_list_checkpoints_empty(self, manager: RollbackManager) -> None:
        cps = manager.list_checkpoints()
        assert cps == []


class TestRollbackManagerRollback:
    def test_rollback_restores_status(self, manager: RollbackManager, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "PENDING")
        conn.close()

        cp_id = manager.checkpoint("before change")

        conn = get_db_connection(tmp_db)
        conn.execute("BEGIN")
        conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = 'ADR-001'")
        conn.execute("COMMIT")
        conn.close()

        count = manager.rollback_to(cp_id)
        assert count == 1

        conn = get_db_connection(tmp_db)
        row = conn.execute("SELECT status FROM tasks WHERE task_id = 'ADR-001'").fetchone()
        conn.close()
        assert row["status"] == "PENDING"

    def test_rollback_nonexistent_checkpoint_raises(self, manager: RollbackManager) -> None:
        with pytest.raises(ValueError, match="Checkpoint not found"):
            manager.rollback_to("CP-nonexistent")


class TestRollbackManagerUndo:
    def test_undo_last(self, manager: RollbackManager, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "PENDING")
        conn.close()

        manager.checkpoint("cp1")

        conn = get_db_connection(tmp_db)
        conn.execute("BEGIN")
        conn.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE task_id = 'ADR-001'")
        conn.execute("COMMIT")
        conn.close()

        manager.checkpoint("cp2")

        conn = get_db_connection(tmp_db)
        conn.execute("BEGIN")
        conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = 'ADR-001'")
        conn.execute("COMMIT")
        conn.close()

        result = manager.undo_last()
        assert result is not None

        conn = get_db_connection(tmp_db)
        row = conn.execute("SELECT status FROM tasks WHERE task_id = 'ADR-001'").fetchone()
        conn.close()
        assert row["status"] == "IN_PROGRESS"

    def test_undo_last_no_enough_checkpoints(self, manager: RollbackManager) -> None:
        result = manager.undo_last()
        assert result is None
