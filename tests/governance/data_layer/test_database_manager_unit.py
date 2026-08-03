# [A_test] module_id: MOD-GOV_database_manager_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-623 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_database_manager
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-623 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

"""T-DB-001: test_database_manager.py — DatabaseManager 单元测试
Phase experimental, P1, 1.5h
"""


import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from zephyr.governance.persistence.database_manager import (
    DatabaseHealthStatus,
    DatabaseManager,
    DatabaseManagerError,
)


@pytest.fixture
def tmp_db_path():
    import gc
    import time

    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_dm_")
    os.close(fd)
    yield Path(path)
    gc.collect()
    for ext in ("", "-wal", "-shm"):
        p = Path(str(path) + ext)
        if p.exists():
            for _attempt in range(5):
                try:
                    p.unlink()
                    break
                except PermissionError:
                    gc.collect()
                    time.sleep(0.1)


@pytest.fixture
def dm(tmp_db_path):
    mgr = DatabaseManager(db_path=tmp_db_path, auto_init=True)
    yield mgr
    try:
        mgr.close(backup_before_close=False)
    except Exception:
        pass


class TestDatabaseManagerInit:
    def test_init_creates_db_file(self, tmp_db_path):
        dm = DatabaseManager(db_path=tmp_db_path, auto_init=True)
        assert tmp_db_path.exists()
        dm.close(backup_before_close=False)

    def test_init_without_auto_init(self, tmp_db_path):
        dm = DatabaseManager(db_path=tmp_db_path, auto_init=False)
        dm.close(backup_before_close=False)


class TestHealthCheck:
    def test_health_check_returns_status(self, dm):
        status = dm.health_check()
        assert isinstance(status, DatabaseHealthStatus)
        assert status.healthy is True
        assert status.integrity_ok is True
        assert status.schema_version > 0

    def test_health_check_caches_last_health(self, dm):
        dm.health_check()
        assert dm.last_health is not None
        assert dm.last_health.healthy is True

    def test_health_check_on_closed_raises(self, dm):
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError):
            dm.health_check()

    def test_health_status_to_dict(self, dm):
        status = dm.health_check()
        d = status.to_dict()
        assert "healthy" in d
        assert "schema_version" in d
        assert "db_size_mb" in d
        assert "integrity_ok" in d


class TestBackup:
    def test_backup_creates_file(self, dm, tmp_db_path):
        backup_dir = tmp_db_path.parent / "test_backups"
        dm2 = DatabaseManager(db_path=tmp_db_path, backup_dir=backup_dir)
        try:
            path = dm2.backup(label="test")
            assert path.exists()
            assert path.suffix == ".db"
        finally:
            dm2.close(backup_before_close=False)

    def test_backup_on_closed_raises(self, dm):
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError):
            dm.backup()


class TestMaintenance:
    def test_maintenance_runs(self, dm):
        result = dm.maintenance()
        assert "vacuum" in result
        assert "integrity" in result


class TestStats:
    def test_stats_returns_counts(self, dm):
        s = dm.stats()
        assert "task_count" in s
        assert "event_count" in s
        assert "gate_count" in s
        assert "db_size_mb" in s
        assert "wal_size_mb" in s
        assert isinstance(s["task_count"], int)


class TestConnectionPool:
    def test_get_connection_returns_connection(self, dm):
        conn = dm.get_connection()
        assert isinstance(conn, sqlite3.Connection)
        dm.return_connection(conn)

    def test_return_connection_reuses(self, dm):
        conn1 = dm.get_connection()
        dm.return_connection(conn1)
        conn2 = dm.get_connection()
        assert conn2 is conn1

    def test_get_connection_on_closed_raises(self, dm):
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError):
            dm.get_connection()


class TestClose:
    def test_close_is_idempotent(self, dm):
        dm.close(backup_before_close=False)
        dm.close(backup_before_close=False)
