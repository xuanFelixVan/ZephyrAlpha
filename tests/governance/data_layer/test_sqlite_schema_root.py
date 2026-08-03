# [A_test] module_id: MOD-GOV_sqlite_schema_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §test
# [MODULE] tests.test_sqlite_schema
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] init_db幂等;migration只向前;PRAGMA基线一致
# [MODIFY-GUARD] src/zephyr/db/sqlite_schema.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_sqlite_schema_root.py
# [TTL] task_bound

from __future__ import annotations

import sqlite3

import pytest

schema_mod = pytest.importorskip("zephyr.governance.persistence.sqlite_schema")
init_db = schema_mod.init_db
get_db_connection = schema_mod.get_db_connection
table_names = schema_mod.table_names
view_names = schema_mod.view_names
schema_version = schema_mod.schema_version
migration_dry_run = schema_mod.migration_dry_run
_MIGRATIONS = schema_mod._MIGRATIONS


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_schema.db"


@pytest.fixture
def initialized_db(db_path):
    result = init_db(db_path)
    return result


class TestInitDb:
    def test_creates_database_file(self, db_path):
        result = init_db(db_path)
        assert result.exists()

    def test_idempotent_init(self, db_path):
        first = init_db(db_path)
        second = init_db(db_path)
        assert first == second

    def test_creates_parent_directory(self, tmp_path):
        nested = tmp_path / "deep" / "nested" / "test.db"
        result = init_db(nested)
        assert result.exists()

    def test_returns_resolved_path(self, db_path):
        result = init_db(db_path)
        assert result.is_absolute()


class TestGetDbConnection:
    def test_returns_connection(self, initialized_db):
        conn = get_db_connection(initialized_db)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_connection_has_row_factory(self, initialized_db):
        conn = get_db_connection(initialized_db)
        assert conn.row_factory is not None
        conn.close()

    def test_connection_executes_pragma(self, initialized_db):
        conn = get_db_connection(initialized_db)
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode == "wal"
        conn.close()

    def test_connection_foreign_keys_on(self, initialized_db):
        conn = get_db_connection(initialized_db)
        cursor = conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1
        conn.close()


class TestTableNames:
    def test_returns_list(self, initialized_db):
        result = table_names(initialized_db)
        assert isinstance(result, list)

    def test_contains_core_tables(self, initialized_db):
        result = table_names(initialized_db)
        assert "tasks" in result
        assert "events" in result
        assert "gates" in result

    def test_contains_circuit_breaker_table(self, initialized_db):
        result = table_names(initialized_db)
        assert "circuit_breaker_state" in result

    def test_contains_schema_version_table(self, initialized_db):
        result = table_names(initialized_db)
        assert "_schema_version" in result

    def test_empty_db_returns_few_tables(self, tmp_path):
        empty_db = tmp_path / "empty.db"
        conn = sqlite3.connect(str(empty_db))
        conn.close()
        result = table_names(empty_db)
        assert isinstance(result, list)


class TestViewNames:
    def test_returns_list(self, initialized_db):
        result = view_names(initialized_db)
        assert isinstance(result, list)

    def test_contains_core_views(self, initialized_db):
        result = view_names(initialized_db)
        assert "event_log" in result
        assert "v_active_tasks" in result
        assert "v_recent_sessions" in result


class TestSchemaVersion:
    def test_returns_int(self, initialized_db):
        result = schema_version(initialized_db)
        assert isinstance(result, int)

    def test_version_is_positive(self, initialized_db):
        result = schema_version(initialized_db)
        assert result > 0

    def test_version_matches_migrations(self, initialized_db):
        result = schema_version(initialized_db)
        max_registered = max(m[0] for m in _MIGRATIONS)
        assert result <= max_registered


class TestMigrationDryRun:
    def test_returns_dict(self, initialized_db):
        result = migration_dry_run(initialized_db)
        assert isinstance(result, dict)

    def test_contains_current_version(self, initialized_db):
        result = migration_dry_run(initialized_db)
        assert "current_version" in result

    def test_contains_migrations_list(self, initialized_db):
        result = migration_dry_run(initialized_db)
        assert "migrations" in result
        assert isinstance(result["migrations"], list)

    def test_pending_only_mode(self, initialized_db):
        result = migration_dry_run(initialized_db, pending_only=True)
        assert "pending_count" in result

    def test_migration_entry_has_required_fields(self, initialized_db):
        result = migration_dry_run(initialized_db)
        if result["migrations"]:
            entry = result["migrations"][0]
            assert "version" in entry
            assert "description" in entry
            assert "status" in entry


class TestMigrationsIntegrity:
    def test_migrations_list_not_empty(self):
        assert len(_MIGRATIONS) > 0

    def test_migrations_have_increasing_versions(self):
        versions = [m[0] for m in _MIGRATIONS]
        for i in range(1, len(versions)):
            assert versions[i] > versions[i - 1], f"Migration v{versions[i]} not after v{versions[i - 1]}"

    def test_each_migration_has_description(self):
        for version, description, statements in _MIGRATIONS:
            assert len(description) > 0, f"Migration v{version} has empty description"

    def test_each_migration_has_statements_list(self):
        for version, description, statements in _MIGRATIONS:
            assert isinstance(statements, list), f"Migration v{version} statements not a list"
