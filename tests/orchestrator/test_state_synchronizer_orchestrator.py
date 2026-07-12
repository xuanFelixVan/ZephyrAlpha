# [A_test] module_id: SRC-TST-1920 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-539 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_state_synchronizer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for state_synchronizer.py (T-2-04)
"""

import json as _json
from pathlib import Path

import pytest

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.orchestrator.lifecycle.state_synchronizer import StateSynchronizer


@pytest.fixture
def syncer(tmp_db: Path) -> StateSynchronizer:
    return StateSynchronizer(db_path=tmp_db)


def _insert_task(conn, task_id: str, file_path: str, status: str = "PENDING") -> None:
    now = "2026-04-24T00:00:00+00:00"
    files_json = _json.dumps([file_path])
    conn.execute("BEGIN")
    conn.execute(
        """INSERT OR REPLACE INTO tasks
           (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, files_in_scope, depends_on, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 'P2', 2, 'glm', 'M', ?, '[]', ?, ?)""",
        (task_id, task_id.split("-")[0], int(task_id.split("-")[-1]), task_id, status, files_json, now, now),
    )
    conn.execute("COMMIT")


class TestStateSynchronizerSync:
    def test_sync_all_empty_db(self, syncer: StateSynchronizer) -> None:
        results = syncer.sync_all()
        assert results == []

    def test_sync_pending_no_file_is_ok(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "docs/nonexistent.md", "PENDING")
        conn.close()
        results = syncer.sync_all()
        assert len(results) == 0

    def test_sync_missing_artifact_detected(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "docs/missing.md", "COMPLETED")
        conn.close()
        results = syncer.sync_all()
        assert len(results) == 1
        assert results[0].action == "MISSING_ARTIFACT_ERROR"

    def test_sync_auto_fix(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "docs/missing.md", "COMPLETED")
        conn.close()
        results = syncer.sync_all(auto_fix=True)
        assert len(results) == 1
        conn2 = get_db_connection(tmp_db)
        row = conn2.execute("SELECT status FROM tasks WHERE task_id = 'ADR-001'").fetchone()
        conn2.close()
        assert row["status"] == "PENDING"

    def test_sync_single_task(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "docs/missing.md", "COMPLETED")
        conn.close()
        result = syncer.sync_task("ADR-001")
        assert result is not None
        assert result.action == "MISSING_ARTIFACT_ERROR"

    def test_sync_nonexistent_task(self, syncer: StateSynchronizer) -> None:
        result = syncer.sync_task("ADR-999")
        assert result is None


class TestDetectGhosts:
    def test_detect_ghosts(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "docs/ghost.md", "PENDING")
        conn.close()
        ghosts = syncer.detect_ghosts()
        assert len(ghosts) >= 1
        assert any(g.task_id == "ADR-001" for g in ghosts)

    def test_no_ghosts_for_existing_files(self, syncer: StateSynchronizer, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", "pyproject.toml", "PENDING")
        conn.close()
        ghosts = syncer.detect_ghosts()
        ghost_ids = [g.task_id for g in ghosts]
        assert "ADR-001" not in ghost_ids
