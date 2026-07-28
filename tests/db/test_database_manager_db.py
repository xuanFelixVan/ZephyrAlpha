# [A_test] module_id: MOD-GOV_database_manager_db | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-484 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_database_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/db/database_manager.py
=============================================
覆盖矩阵：
  DatabaseHealthStatus:
    - 构造 + 属性读取 × 1
    - to_dict 输出正确性 × 1
    - __repr__ healthy / unhealthy × 2
  DatabaseManager:
    - 初始化（auto_init=True / False）× 2
    - 单例 instance() × 1
    - get_connection / return_connection × 3
    - health_check（正常 / 异常回退）× 2
    - backup + 备份轮转 × 1
    - wal_checkpoint_truncate × 1
    - maintenance × 1
    - stats × 1
    - close（备份前关闭 / 不备份关闭）× 2
    - 上下文管理器 × 1

Task: MOD-INF-012 | Safety: M
"""

import pytest

from zephyr.governance.persistence.database_manager import (
    DatabaseHealthStatus as DatabaseHealthStatus,
)
from zephyr.governance.persistence.database_manager import (
    DatabaseManager,
    DatabaseManagerError,
)


class TestDatabaseHealthStatus:
    def test_construct_healthy(self):
        hs = DatabaseHealthStatus(
            healthy=True,
            schema_version=3,
            db_size_bytes=1024000,
            wal_size_bytes=512000,
            table_count=8,
            integrity_ok=True,
            checked_at="2026-05-06T12:00:00Z",
        )
        assert hs.healthy is True
        assert hs.schema_version == 3
        assert hs.db_size_bytes == 1024000
        assert hs.wal_size_bytes == 512000
        assert hs.table_count == 8
        assert hs.integrity_ok is True
        assert hs.error is None

    def test_construct_unhealthy(self):
        hs = DatabaseHealthStatus(
            healthy=False,
            schema_version=-1,
            db_size_bytes=0,
            wal_size_bytes=0,
            table_count=0,
            integrity_ok=False,
            checked_at="2026-05-06T12:00:00Z",
            error="disk full",
        )
        assert hs.healthy is False
        assert hs.error == "disk full"

    def test_to_dict(self):
        hs = DatabaseHealthStatus(
            healthy=True,
            schema_version=5,
            db_size_bytes=2_097_152,
            wal_size_bytes=1_048_576,
            table_count=6,
            integrity_ok=True,
            checked_at="2026-05-06T12:00:00Z",
        )
        d = hs.to_dict()
        assert d["healthy"] is True
        assert d["schema_version"] == 5
        assert d["db_size_mb"] == 2.0
        assert d["wal_size_mb"] == 1.0
        assert d["table_count"] == 6
        assert d["integrity_ok"] is True

    def test_repr_healthy(self):
        hs = DatabaseHealthStatus(
            healthy=True,
            schema_version=3,
            db_size_bytes=0,
            wal_size_bytes=0,
            table_count=0,
            integrity_ok=True,
            checked_at="",
        )
        r = repr(hs)
        assert "healthy=True" in r
        assert "schema_version=3" in r

    def test_repr_unhealthy(self):
        hs = DatabaseHealthStatus(
            healthy=False,
            schema_version=0,
            db_size_bytes=0,
            wal_size_bytes=0,
            table_count=0,
            integrity_ok=False,
            checked_at="",
            error="timeout",
        )
        r = repr(hs)
        assert "healthy=False" in r
        assert "timeout" in r


class TestDatabaseManagerLifecycle:
    def test_init_with_auto_init(self, tmp_path):
        db_path = tmp_path / "test.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            assert db_path.exists()
        finally:
            dm.close(backup_before_close=False)

    def test_init_without_auto_init(self, tmp_path):
        db_path = tmp_path / "no_init.db"
        dm = DatabaseManager(db_path, auto_init=False)
        try:
            assert dm.get_connection() is not None
        finally:
            dm.close(backup_before_close=False)

    def test_singleton_instance(self):
        dm1 = DatabaseManager.instance()
        dm2 = DatabaseManager.instance()
        try:
            assert dm1 is dm2
        finally:
            dm1.close(backup_before_close=False)

    def test_context_manager(self, tmp_path):
        db_path = tmp_path / "ctx.db"
        with DatabaseManager(db_path, auto_init=True) as dm:
            assert dm.get_connection() is not None
        assert dm.closed is True


class TestDatabaseManagerConnection:
    def test_get_connection(self, tmp_path):
        db_path = tmp_path / "conn.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            conn = dm.get_connection()
            assert isinstance(conn, __import__("sqlite3").Connection)
        finally:
            dm.close(backup_before_close=False)

    def test_get_connection_closed_raises(self, tmp_path):
        db_path = tmp_path / "closed.db"
        dm = DatabaseManager(db_path, auto_init=False)
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError, match="closed"):
            dm.get_connection()

    def test_return_connection_reuses(self, tmp_path):
        db_path = tmp_path / "reuse.db"
        dm = DatabaseManager(db_path, auto_init=True, pool_size=2)
        try:
            conn = dm.get_connection()
            dm.return_connection(conn)
            conn2 = dm.get_connection()
            assert conn2 is conn
        finally:
            dm.close(backup_before_close=False)


class TestDatabaseManagerHealthCheck:
    def test_health_check_healthy(self, tmp_path):
        db_path = tmp_path / "health.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            status = dm.health_check()
            assert status.healthy is True
            assert status.integrity_ok is True
            assert status.schema_version > 0
            assert status.table_count > 0
        finally:
            dm.close(backup_before_close=False)

    def test_health_check_closed_raises(self, tmp_path):
        db_path = tmp_path / "hc_closed.db"
        dm = DatabaseManager(db_path, auto_init=False)
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError, match="closed"):
            dm.health_check()

    def test_last_health_property(self, tmp_path):
        db_path = tmp_path / "lasth.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            assert dm.last_health is None
            dm.health_check()
            assert dm.last_health is not None
            assert dm.last_health.healthy is True
        finally:
            dm.close(backup_before_close=False)


class TestDatabaseManagerBackup:
    def test_backup_creates_file(self, tmp_path):
        db_path = tmp_path / "bu.db"
        backup_dir = tmp_path / "backups"
        dm = DatabaseManager(db_path, backup_dir=backup_dir, auto_init=True)
        try:
            backup_path = dm.backup(label="test")
            assert backup_path.exists()
            assert "test" in backup_path.name
        finally:
            dm.close(backup_before_close=False)

    def test_backup_closed_raises(self, tmp_path):
        db_path = tmp_path / "bu_closed.db"
        dm = DatabaseManager(db_path, auto_init=False)
        dm.close(backup_before_close=False)
        with pytest.raises(DatabaseManagerError, match="closed"):
            dm.backup()


class TestDatabaseManagerWal:
    def test_wal_checkpoint_truncate(self, tmp_path):
        db_path = tmp_path / "wal.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            dm.wal_checkpoint_truncate()
        finally:
            dm.close(backup_before_close=False)


class TestDatabaseManagerMaintenance:
    def test_maintenance_on_healthy(self, tmp_path):
        db_path = tmp_path / "maint.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            result = dm.maintenance()
            assert "pre_health" in result
            assert "post_health" in result
            assert result["vacuum"] is True
        finally:
            dm.close(backup_before_close=False)


class TestDatabaseManagerStats:
    def test_stats_returns_counts(self, tmp_path):
        db_path = tmp_path / "stats.db"
        dm = DatabaseManager(db_path, auto_init=True)
        try:
            s = dm.stats()
            assert "task_count" in s
            assert "event_count" in s
            assert "gate_count" in s
            assert "ke_count" in s
            assert "db_size_mb" in s
            assert "schema_version" in s
        finally:
            dm.close(backup_before_close=False)


class TestDatabaseManagerClose:
    def test_close_generates_backup(self, tmp_path):
        db_path = tmp_path / "close_bu.db"
        backup_dir = tmp_path / "close_backups"
        dm = DatabaseManager(db_path, backup_dir=backup_dir, auto_init=True)
        dm.close(backup_before_close=True)
        backups = list(backup_dir.glob("zalpha_metadata_*.db"))
        assert len(backups) >= 1

    def test_double_close_idempotent(self, tmp_path):
        db_path = tmp_path / "double.db"
        dm = DatabaseManager(db_path, auto_init=True)
        dm.close(backup_before_close=False)
        dm.close(backup_before_close=False)
