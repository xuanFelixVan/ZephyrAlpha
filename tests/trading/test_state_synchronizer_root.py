# [A_test] module_id: SRC-TST-1687 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_state_synchronizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_state_synchronizer_root.py
# [TTL] task_bound

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.orchestrator.lifecycle.state_synchronizer import (
    GhostTask,
    OrphanFile,
    StateSynchronizer,
    SyncResult,
)


class TestSyncResult:
    def test_create(self):
        result = SyncResult(
            task_id="T-1",
            file_path="test.md",
            action="STALE_TASK_WARNING",
            old_status="PENDING",
            new_status="VERIFIED",
            reason="File accepted but task still PENDING",
        )
        assert result.task_id == "T-1"
        assert result.action == "STALE_TASK_WARNING"
        assert result.old_status == "PENDING"
        assert result.new_status == "VERIFIED"


class TestOrphanFile:
    def test_create(self):
        orphan = OrphanFile(file_path="orphan.md", suggested_task_id="OPS-1")
        assert orphan.file_path == "orphan.md"
        assert orphan.suggested_task_id == "OPS-1"


class TestGhostTask:
    def test_create(self):
        ghost = GhostTask(task_id="T-1", file_path="missing.md", task_status="COMPLETED")
        assert ghost.task_id == "T-1"
        assert ghost.file_path == "missing.md"
        assert ghost.task_status == "COMPLETED"


class TestStateSynchronizerInstantiation:
    def test_create_with_default_db(self):
        sync = StateSynchronizer()
        assert sync is not None

    def test_create_with_custom_db(self):
        sync = StateSynchronizer(db_path=Path("/tmp/test.db"))
        assert sync is not None

    def test_has_sync_all(self):
        sync = StateSynchronizer()
        assert callable(sync.sync_all)

    def test_has_sync_task(self):
        sync = StateSynchronizer()
        assert callable(sync.sync_task)

    def test_has_detect_orphans(self):
        sync = StateSynchronizer()
        assert callable(sync.detect_orphans)

    def test_has_detect_ghosts(self):
        sync = StateSynchronizer()
        assert callable(sync.detect_ghosts)


class TestSyncAll:
    def test_sync_all_no_tasks(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        with patch("zephyr.orchestrator.state_synchronizer.get_db_connection", return_value=mock_conn):
            sync = StateSynchronizer()
            result = sync.sync_all()
            assert result == []

    def test_sync_all_with_consistent_task(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            {"task_id": "T-1", "files_in_scope": '["nonexistent.md"]', "status": "PENDING"},
        ]
        with (
            patch("zephyr.orchestrator.state_synchronizer.get_db_connection", return_value=mock_conn),
            patch("zephyr.orchestrator.state_synchronizer.REPO_ROOT", Path("/nonexistent")),
        ):
            sync = StateSynchronizer()
            result = sync.sync_all(auto_fix=False)
            assert isinstance(result, list)


class TestSyncTask:
    def test_sync_task_not_found(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        with patch("zephyr.orchestrator.state_synchronizer.get_db_connection", return_value=mock_conn):
            sync = StateSynchronizer()
            result = sync.sync_task("NONEXISTENT-1")
            assert result is None


class TestDetectGhosts:
    def test_detect_ghosts_no_tasks(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        with patch("zephyr.orchestrator.state_synchronizer.get_db_connection", return_value=mock_conn):
            sync = StateSynchronizer()
            result = sync.detect_ghosts()
            assert result == []

    def test_detect_ghosts_with_missing_file(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            {"task_id": "T-1", "files_in_scope": '["nonexistent_file.md"]', "status": "COMPLETED"},
        ]
        with (
            patch("zephyr.orchestrator.state_synchronizer.get_db_connection", return_value=mock_conn),
            patch("zephyr.orchestrator.state_synchronizer.REPO_ROOT", Path("/nonexistent")),
        ):
            sync = StateSynchronizer()
            result = sync.detect_ghosts()
            assert len(result) == 1
            assert result[0].task_id == "T-1"
            assert result[0].task_status == "COMPLETED"
