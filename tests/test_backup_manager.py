# [A_test] module_id: SRC-TST-0409 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md | §test
# [MODULE] tests.test_backup_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_backup_manager.py


from zephyr.trading.orchestrator.backup_manager import (
    RETENTION_POLICY,
    BackupManager,
    BackupRecord,
)


class TestRetentionPolicy:
    def test_daily_retention(self):
        assert RETENTION_POLICY["daily"] == 30

    def test_monthly_retention(self):
        assert RETENTION_POLICY["monthly"] == 12

    def test_yearly_retention(self):
        assert RETENTION_POLICY["yearly"] == 5

    def test_has_three_tiers(self):
        assert len(RETENTION_POLICY) == 3


class TestBackupRecordModel:
    def test_create_with_required_fields(self):
        record = BackupRecord(backup_id="SQLITE-test-20260522", target="test.db")
        assert record.backup_id == "SQLITE-test-20260522"
        assert record.target == "test.db"
        assert record.size_bytes == 0
        assert record.checksum == ""
        assert record.timestamp is not None

    def test_create_with_all_fields(self):
        record = BackupRecord(
            backup_id="CHROMA-20260522",
            target="chromadb",
            size_bytes=1024,
            checksum="abc123",
        )
        assert record.size_bytes == 1024
        assert record.checksum == "abc123"

    def test_timestamp_auto_populated(self):
        record = BackupRecord(backup_id="B-1", target="test.db")
        assert record.timestamp is not None


class TestBackupManagerInstantiation:
    def test_create_instance(self):
        mgr = BackupManager()
        assert mgr is not None

    def test_has_backup_sqlite_method(self):
        mgr = BackupManager()
        assert callable(mgr.backup_sqlite)

    def test_has_backup_chromadb_method(self):
        mgr = BackupManager()
        assert callable(mgr.backup_chromadb)

    def test_has_verify_integrity_method(self):
        mgr = BackupManager()
        assert callable(mgr.verify_integrity)

    def test_has_get_retention_method(self):
        mgr = BackupManager()
        assert callable(mgr.get_retention)

    def test_initial_no_records(self):
        mgr = BackupManager()
        assert len(mgr._records) == 0


class TestBackupSqlite:
    def test_returns_backup_record(self):
        mgr = BackupManager()
        record = mgr.backup_sqlite("zalpha_metadata")
        assert isinstance(record, BackupRecord)

    def test_record_has_sqlite_prefix(self):
        mgr = BackupManager()
        record = mgr.backup_sqlite("zalpha_metadata")
        assert record.backup_id.startswith("SQLITE-")

    def test_record_has_db_target(self):
        mgr = BackupManager()
        record = mgr.backup_sqlite("zalpha_metadata")
        assert record.target == "governance.db"

    def test_record_stored(self):
        mgr = BackupManager()
        mgr.backup_sqlite("test_db")
        assert len(mgr._records) == 1

    def test_multiple_backups(self):
        mgr = BackupManager()
        mgr.backup_sqlite("db1")
        mgr.backup_sqlite("db2")
        assert len(mgr._records) == 2


class TestBackupChromadb:
    def test_returns_backup_record(self):
        mgr = BackupManager()
        record = mgr.backup_chromadb()
        assert isinstance(record, BackupRecord)

    def test_record_has_chroma_prefix(self):
        mgr = BackupManager()
        record = mgr.backup_chromadb()
        assert record.backup_id.startswith("CHROMA-")

    def test_record_has_chromadb_target(self):
        mgr = BackupManager()
        record = mgr.backup_chromadb()
        assert record.target == "chromadb"

    def test_record_stored(self):
        mgr = BackupManager()
        mgr.backup_chromadb()
        assert len(mgr._records) == 1


class TestVerifyIntegrity:
    def test_returns_true(self):
        mgr = BackupManager()
        result = mgr.verify_integrity("SQLITE-test-20260522")
        assert result is True

    def test_returns_bool(self):
        mgr = BackupManager()
        result = mgr.verify_integrity("any-id")
        assert isinstance(result, bool)

    def test_verify_nonexistent_backup(self):
        mgr = BackupManager()
        result = mgr.verify_integrity("nonexistent")
        assert result is True


class TestGetRetention:
    def test_returns_dict(self):
        mgr = BackupManager()
        result = mgr.get_retention()
        assert isinstance(result, dict)

    def test_returns_copy(self):
        mgr = BackupManager()
        result = mgr.get_retention()
        result["extra"] = 99
        assert "extra" not in mgr.get_retention()

    def test_matches_retention_policy(self):
        mgr = BackupManager()
        result = mgr.get_retention()
        assert result == dict(RETENTION_POLICY)
