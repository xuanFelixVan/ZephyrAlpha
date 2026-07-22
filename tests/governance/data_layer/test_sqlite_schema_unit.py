# [A_test] module_id: MOD-GOV_sqlite_schema_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-686 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_sqlite_schema
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/db/sqlite_schema.py（T-1-02）
====================================================
覆盖矩阵：
  init_db:
    - 幂等初始化 × 2（首次、重复调用）
    - 表创建完整性 × 1（6 表 + 3 视图）
    - 索引创建 × 1
  get_db_connection:
    - PRAGMA 配置验证 × 4（WAL、foreign_keys、busy_timeout、temp_store）
    - row_factory 设置 × 1
  table_names / view_names:
    - 返回正确列表 × 2
  DDL 约束验证：
    - tasks.status CHECK × 2（合法值、非法值）
    - tasks.namespace CHECK × 2（合法值、非法值）
    - tasks.priority CHECK × 2（合法值、非法值）
    - circuit_breaker_state.state CHECK × 2
    - task_files 外键 × 1
  迁移幂等性：
    - _migrate_namespace_and_seq × 1
    - _migrate_v2_fields × 1
    - _migrate_knowledge_status × 1
    - _migrate_circuit_breaker_state × 1

Task: T-1-02 | Safety: M | experimental
"""

from __future__ import annotations

import sqlite3

import pytest

from zephyr.governance.persistence.sqlite_schema import (
    get_db_connection,
    init_db,
    table_names,
    view_names,
)


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test_schema.db"
    init_db(db_path)
    return db_path


class TestInitDb:
    def test_creates_database_file(self, tmp_path):
        db_path = tmp_path / "new.db"
        result = init_db(db_path)
        assert result.exists()

    def test_idempotent_double_init(self, db):
        init_db(db)
        tables = table_names(db)
        assert "tasks" in tables

    def test_all_tables_created(self, db):
        tables = table_names(db)
        expected = {"tasks", "task_files", "events", "knowledge", "gates", "circuit_breaker_state"}
        assert expected.issubset(set(tables))

    def test_all_views_created(self, db):
        views = view_names(db)
        expected = {"event_log", "v_active_tasks", "v_recent_sessions"}
        assert expected.issubset(set(views))

    def test_indexes_created(self, db):
        conn = sqlite3.connect(str(db))
        indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        conn.close()
        assert "idx_tasks_status" in indexes
        assert "idx_events_type" in indexes
        assert "idx_gates_gate_id" in indexes
        assert "idx_tf_task" in indexes
        assert "idx_cb_state" in indexes


class TestGetDbConnection:
    def test_pragma_wal(self, db):
        conn = get_db_connection(db)
        result = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert result == "wal"

    def test_pragma_foreign_keys(self, db):
        conn = get_db_connection(db)
        result = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        assert result == 1

    def test_pragma_busy_timeout(self, db):
        conn = get_db_connection(db)
        result = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        conn.close()
        assert result == 5000

    def test_pragma_temp_store(self, db):
        conn = get_db_connection(db)
        result = conn.execute("PRAGMA temp_store").fetchone()[0]
        conn.close()
        assert result == 2

    def test_row_factory(self, db):
        conn = get_db_connection(db)
        conn.execute("CREATE TABLE rf_test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO rf_test VALUES (1, 'test')")
        row = conn.execute("SELECT * FROM rf_test").fetchone()
        conn.close()
        assert row["id"] == 1
        assert row["name"] == "test"


class TestTableNames:
    def test_returns_list(self, db):
        result = table_names(db)
        assert isinstance(result, list)
        assert len(result) >= 6

    def test_sorted_alphabetically(self, db):
        result = table_names(db)
        assert result == sorted(result)


class TestViewNames:
    def test_returns_list(self, db):
        result = view_names(db)
        assert isinstance(result, list)
        assert len(result) >= 3


class TestTasksConstraints:
    def test_valid_status(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
            "VALUES ('ADR-1', 'ADR', 1, 'Test', 'IN_PROGRESS', 'P1', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        conn.close()

    def test_invalid_status(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
                "VALUES ('ADR-2', 'ADR', 2, 'Test', 'INVALID', 'P1', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
            )
        conn.close()

    def test_valid_namespace(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
            "VALUES ('CPP-1', 'CP', 1, 'Test', 'PENDING', 'P2', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        conn.close()

    def test_invalid_namespace(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
                "VALUES ('XXX-1', 'XX', 1, 'Test', 'PENDING', 'P2', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
            )
        conn.close()

    def test_valid_priority(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
            "VALUES ('STD-1', 'STD', 1, 'Test', 'PENDING', 'P0', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        conn.close()

    def test_invalid_priority(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO tasks (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at) "
                "VALUES ('STD-2', 'STD', 2, 'Test', 'PENDING', 'PX', 1, 'deepseek', 'M', '2026-01-01', '2026-01-01')"
            )
        conn.close()


class TestCircuitBreakerConstraints:
    def test_valid_state(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute(
            "INSERT INTO circuit_breaker_state (caller_module, target_module, state, failure_count, created_at, updated_at) "
            "VALUES ('mod_a', 'mod_b', 'CLOSED', 0, '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        conn.close()

    def test_invalid_state(self, db):
        conn = sqlite3.connect(str(db))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO circuit_breaker_state (caller_module, target_module, state, failure_count, created_at, updated_at) "
                "VALUES ('mod_a2', 'mod_b2', 'BROKEN', 0, '2026-01-01', '2026-01-01')"
            )
        conn.close()


class TestTaskFilesForeignKey:
    def test_foreign_key_enforcement(self, db):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO task_files (task_id, file_path, role) VALUES ('NONEXISTENT-999', 'test.py', 'in_scope')"
            )
        conn.close()


class TestMigrationIdempotency:
    def test_migrate_namespace_and_seq_idempotent(self, db):
        init_db(db)
        init_db(db)
        conn = sqlite3.connect(str(db))
        columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()}
        conn.close()
        assert "namespace" in columns
        assert "seq" in columns

    def test_migrate_v2_fields_idempotent(self, db):
        init_db(db)
        init_db(db)
        conn = sqlite3.connect(str(db))
        columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()}
        conn.close()
        assert "title" in columns
        assert "priority" in columns

    def test_migrate_knowledge_status_idempotent(self, db):
        init_db(db)
        init_db(db)
        conn = sqlite3.connect(str(db))
        columns = {row[1] for row in conn.execute("PRAGMA table_info(knowledge)").fetchall()}
        conn.close()
        assert "status" in columns

    def test_migrate_circuit_breaker_state_idempotent(self, db):
        init_db(db)
        init_db(db)
        tables = table_names(db)
        assert "circuit_breaker_state" in tables
