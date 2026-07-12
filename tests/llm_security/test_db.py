# [A_test] module_id: SRC-TST-0703 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §test
# [MODULE] zephyr.governance.persistence
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_db.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

dm_mod = pytest.importorskip("zephyr.governance.database_manager")
DatabaseManager = dm_mod.DatabaseManager
DatabaseManagerError = dm_mod.DatabaseManagerError
DatabaseHealthStatus = dm_mod.DatabaseHealthStatus

task_repo_mod = pytest.importorskip("zephyr.governance.persistence.task_repo")
TaskRepository = task_repo_mod.TaskRepository
TaskNotFoundError = task_repo_mod.TaskNotFoundError
InvalidTransitionError = task_repo_mod.InvalidTransitionError

atm_mod = pytest.importorskip("zephyr.governance.financial_governance.atomic_transaction_manager")
AtomicTransactionManager = atm_mod.AtomicTransactionManager
TransactionError = atm_mod.TransactionError
TransactionTimeoutError = atm_mod.TransactionTimeoutError

transition_mod = pytest.importorskip("zephyr.governance.lifecycle_governance.transition")

try:
    from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
    from zephyr.integration.shared.schema.base_config import Classification, EvolutionPolicy
    from zephyr.integration.shared.schema.execution_model import ExecutionModel
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
    from zephyr.shared.foundation.models import TaskCard

    HAS_TASK_TYPES = True
except Exception:
    HAS_TASK_TYPES = False

_NOW = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)


def _make_task(task_id="OPS-1", seq=1, title="Test task", priority=Priority.P2):
    return TaskCard(
        task_id=task_id,
        namespace=TaskNamespace.OPS,
        seq=seq,
        title=title,
        status=TaskStatus.PENDING,
        priority=priority,
        phase=1,
        execution_model=ExecutionModel.qwen,
        safety_level=SafetyLevel.L,
        directive="test",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        source_blueprint="MOD-TEST",
        source_section="§1",
        description="A test task for unit testing purposes that meets the minimum length requirement",
        files_in_scope=["test.py"],
        deliverables=["result.txt"],
        acceptance=["passes"],
        depends_on=[],
        tags=["test"],
        applicable_rules=[{"module_id": "RULE-TEST", "section": "§1", "reason": "test"}],
        allowed_touch=["test.py"],
        rollback_instructions="git checkout",
        post_sync_standard=["echo ok"],
        created_at=_NOW,
        updated_at=_NOW,
    )


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_metadata.db"


@pytest.fixture
def dm(db_path):
    manager = DatabaseManager(db_path=db_path, auto_init=True, pool_size=2)
    yield manager
    manager.close(backup_before_close=False)


@pytest.fixture
def repo(db_path):
    r = TaskRepository(db_path=db_path, auto_init=True, enable_gate=False)
    yield r
    r.close()


class TestDatabaseHealthStatus:
    def test_create_healthy(self):
        status = DatabaseHealthStatus(
            healthy=True,
            schema_version=1,
            db_size_bytes=1024,
            wal_size_bytes=0,
            table_count=5,
            integrity_ok=True,
            checked_at="2026-01-01T00:00:00",
        )
        assert status.healthy is True
        assert status.error is None

    def test_create_unhealthy(self):
        status = DatabaseHealthStatus(
            healthy=False,
            schema_version=1,
            db_size_bytes=1024,
            wal_size_bytes=0,
            table_count=5,
            integrity_ok=False,
            checked_at="2026-01-01T00:00:00",
            error="corruption detected",
        )
        assert status.healthy is False
        assert status.error == "corruption detected"

    def test_to_dict(self):
        status = DatabaseHealthStatus(
            healthy=True,
            schema_version=1,
            db_size_bytes=1048576,
            wal_size_bytes=0,
            table_count=5,
            integrity_ok=True,
            checked_at="2026-01-01T00:00:00",
        )
        d = status.to_dict()
        assert d["healthy"] is True
        assert "db_size_mb" in d
        assert d["db_size_mb"] == 1.0

    def test_repr(self):
        status = DatabaseHealthStatus(
            healthy=True,
            schema_version=1,
            db_size_bytes=0,
            wal_size_bytes=0,
            table_count=0,
            integrity_ok=True,
            checked_at="now",
        )
        assert "HEALTHY" in repr(status)

        status2 = DatabaseHealthStatus(
            healthy=False,
            schema_version=1,
            db_size_bytes=0,
            wal_size_bytes=0,
            table_count=0,
            integrity_ok=False,
            checked_at="now",
            error="fail",
        )
        assert "UNHEALTHY" in repr(status2)


class TestDatabaseManager:
    def test_init_creates_db(self, db_path):
        dm = DatabaseManager(db_path=db_path, auto_init=True)
        assert db_path.exists()
        dm.close(backup_before_close=False)

    def test_get_connection(self, dm):
        conn = dm.get_connection()
        assert conn is not None
        cursor = conn.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
        dm.return_connection(conn)

    def test_get_connection_after_close_raises(self, db_path):
        dm = DatabaseManager(db_path=db_path, auto_init=True)
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError):
            dm.get_connection()

    def test_health_check(self, dm):
        status = dm.health_check()
        assert isinstance(status, DatabaseHealthStatus)
        assert status.healthy is True

    def test_health_check_caches(self, dm):
        s1 = dm.health_check()
        s2 = dm.last_health
        assert s1 is s2

    def test_close_idempotent(self, dm):
        dm.close(backup_before_close=False)
        dm.close(backup_before_close=False)

    def test_context_manager(self, db_path):
        with DatabaseManager(db_path=db_path, auto_init=True) as dm_inner:
            conn = dm_inner.get_connection()
            assert conn is not None
            dm_inner.return_connection(conn)

    def test_backup(self, dm, tmp_path):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        dm._backup_dir = backup_dir
        backup_path = dm.backup(label="test")
        assert backup_path.exists()

    def test_backup_after_close_raises(self, db_path):
        dm = DatabaseManager(db_path=db_path, auto_init=True)
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError):
            dm.backup()

    def test_prometheus_export(self, dm):
        output = dm.prometheus_export()
        assert "zalpha_db_task_count" in output
        assert "zalpha_db_schema_version" in output

    def test_connection_leak_detector(self, dm):
        result = dm.connection_leak_detector()
        assert "leaked_count" in result
        assert "pool_size" in result


class TestTaskRepository:
    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_create_and_get(self, repo):
        task = _make_task(task_id="OPS-1", seq=1, title="Test task")
        result = repo.create(task, allow_direct_create=True)
        assert result.task_id == "OPS-1"

        fetched = repo.get("OPS-1")
        assert fetched is not None
        assert fetched.title == "Test task"

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_get_nonexistent_returns_none(self, repo):
        assert repo.get("NONEXISTENT") is None

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_get_or_raises(self, repo):
        with pytest.raises(TaskNotFoundError):
            repo.get_or_raise("NONEXISTENT")

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_delete_soft(self, repo):
        task = _make_task(task_id="OPS-2", seq=2, title="Delete me")
        repo.create(task, allow_direct_create=True)
        assert repo.delete("OPS-2") is True
        assert repo.get("OPS-2") is None

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_delete_nonexistent(self, repo):
        assert repo.delete("NONEXISTENT") is False

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_list_by_status(self, repo):
        task = _make_task(task_id="OPS-3", seq=3, title="List me")
        repo.create(task, allow_direct_create=True)
        results = repo.list_by_status(TaskStatus.PENDING)
        assert any(t.task_id == "OPS-3" for t in results)

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_count_by_status(self, repo):
        result = repo.count_by_status()
        assert isinstance(result, dict)

    @pytest.mark.skipif(not HAS_TASK_TYPES, reason="Task types not importable")
    def test_next_seq(self, repo):
        seq = repo.next_seq()
        assert isinstance(seq, int)
        assert seq >= 1


class TestAtomicTransactionManager:
    def _make_atm(self, tmp_path):
        from unittest.mock import MagicMock

        from zephyr.security.llm_defense.llm_security.input_sanitizer import InputSanitizer

        db = tmp_path / "atm_test.db"
        mock_sanitizer = MagicMock(spec=InputSanitizer)
        mock_sanitizer.validate_path = lambda path, mode="write": (
            Path(path) if Path(path).is_absolute() else tmp_path / path
        )
        atm = AtomicTransactionManager(
            db_path=str(db),
            root=str(tmp_path),
            sanitizer=mock_sanitizer,
        )
        return atm

    def test_init_creates_db(self, tmp_path):
        atm = self._make_atm(tmp_path)
        assert atm.db_path.exists()
        atm.close()

    def test_simple_sql_transaction(self, tmp_path):
        atm = self._make_atm(tmp_path)
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE IF NOT EXISTS test_items (id INTEGER PRIMARY KEY, name TEXT)")
            tx.execute("INSERT INTO test_items (id, name) VALUES (?, ?)", (1, "alpha"))
        row = atm._conn.execute("SELECT name FROM test_items WHERE id=1").fetchone()
        assert row[0] == "alpha"
        atm.close()

    def test_rollback_on_exception(self, tmp_path):
        atm = self._make_atm(tmp_path)
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE IF NOT EXISTS test_items (id INTEGER PRIMARY KEY, name TEXT)")
            tx.execute("INSERT INTO test_items (id, name) VALUES (?, ?)", (1, "alpha"))

        with pytest.raises(RuntimeError), atm.transaction() as tx:
            tx.execute("INSERT INTO test_items (id, name) VALUES (?, ?)", (2, "beta"))
            raise RuntimeError("force rollback")

        rows = atm._conn.execute("SELECT COUNT(*) FROM test_items").fetchone()
        assert rows[0] == 1
        atm.close()

    def test_write_file(self, tmp_path):
        atm = self._make_atm(tmp_path)
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE IF NOT EXISTS dummy (id INTEGER)")
            target = tx.write_file("output/test_file.txt", "hello world")
        assert target.exists()
        assert target.read_text(encoding="utf-8") == "hello world"
        atm.close()

    def test_nested_transaction_raises(self, tmp_path):
        atm = self._make_atm(tmp_path)
        with pytest.raises(TransactionError, match="nested"), atm.transaction() as tx1:
            with atm.transaction() as tx2:
                pass
        atm.close()

    def test_validate_write_path(self, tmp_path):
        atm = self._make_atm(tmp_path)
        result = atm.validate_write_path("output/safe.txt")
        assert isinstance(result, Path)
        atm.close()

    def test_context_manager(self, tmp_path):
        atm = self._make_atm(tmp_path)
        assert atm.db_path.exists()
        atm.close()


class TestTransitionHelpers:
    def test_allowed_transitions_pending(self):
        result = transition_mod._ALLOWED_TRANSITIONS.get(TaskStatus.PENDING, frozenset())
        assert TaskStatus.IN_PROGRESS in result
        assert TaskStatus.BLOCKED in result
        assert TaskStatus.CANCELLED in result

    def test_terminal_states(self):
        assert len(transition_mod._ALLOWED_TRANSITIONS.get(TaskStatus.VERIFIED, frozenset())) == 0
        assert len(transition_mod._ALLOWED_TRANSITIONS.get(TaskStatus.CANCELLED, frozenset())) == 0

    def test_is_valid_transition(self):
        assert transition_mod._is_valid_transition(TaskStatus.PENDING, TaskStatus.IN_PROGRESS) is True
        assert transition_mod._is_valid_transition(TaskStatus.PENDING, TaskStatus.COMPLETED) is False
