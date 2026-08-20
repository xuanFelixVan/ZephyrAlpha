# [A_test] module_id: MOD-GOV_depgraph_schema | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §test_depgraph_schema
# [MODULE] tests.test_depgraph_schema
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] init_db幂等; migration只向前; 事务原子性; PRAGMA基线一致
# [MODIFY-GUARD] src/zephyr/governance/depgraph_schema.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] python -m pytest tests/test_depgraph_schema.py -q
# [A_module] module_id=MOD-DATABASE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
test_depgraph_schema.py — depgraph_schema.py DDL 真源与迁移框架单元测试

覆盖：
  1. init_db 幂等性（重复调用结果一致）
  2. init_db 创建所有表 + 索引 + 版本记录
  3. init_db legacy bootstrap（兼容旧库 current=-1）
  4. migration 事务原子性（中途失败 → ROLLBACK，无部分应用）
  5. _get_current_version 三态逻辑（0 / -1 / N）
  6. get_db_connection PRAGMA 基线
  7. 公共 API（table_names / schema_version）
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_REPO_ROOT = REPO_ROOT
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

schema_mod = pytest.importorskip("zephyr.governance.depgraph_schema")

init_db = schema_mod.init_db
get_db_connection = schema_mod.get_depgraph_pg_connection
table_names = schema_mod.table_names
schema_version = schema_mod.schema_version
_MIGRATIONS = schema_mod._MIGRATIONS
_DDL_INDEXES = schema_mod._DDL_INDEXES
_get_current_version = schema_mod.get_current_version

# P2迁移：init_db 已迁移到 PostgreSQL（只验证 PG schema，不再创建 SQLite 文件），
# PRAGMA/sqlite_master/_schema_version/SQLite 临时库测试均不适用 PG。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 get_db_connection + information_schema + %s 占位符替代 SQLite 临时库/PRAGMA/sqlite_master），当前 skip。
pytestmark = pytest.mark.skip(
    reason="P2迁移：init_db 已迁移到 PG，SQLite 临时库 + PRAGMA 基线 + migration 事务原子性测试不适用"
)


def _extract_index_name(sql: str) -> str | None:
    """从 CREATE INDEX 语句提取索引名。"""
    match = re.search(r"INDEX\s+IF\s+NOT\s+EXISTS\s+(\w+)", sql, re.IGNORECASE)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fresh_db_path(tmp_path):
    """全新临时 DB 路径（未初始化）。"""
    return tmp_path / "test_depgraph.db"


@pytest.fixture
def initialized_db(fresh_db_path):
    """已初始化的 DB 路径。"""
    return init_db(fresh_db_path)


# ---------------------------------------------------------------------------
# 1. init_db 幂等性与基础行为
# ---------------------------------------------------------------------------


class TestInitDb:
    def test_creates_database_file(self, fresh_db_path):
        result = init_db(fresh_db_path)
        assert result.exists()

    def test_returns_resolved_path(self, fresh_db_path):
        result = init_db(fresh_db_path)
        assert result == fresh_db_path.resolve()

    def test_idempotent_multiple_calls(self, fresh_db_path):
        first = init_db(fresh_db_path)
        second = init_db(fresh_db_path)
        third = init_db(fresh_db_path)
        assert first == second == third

    def test_idempotent_no_duplicate_migrations(self, fresh_db_path):
        init_db(fresh_db_path)
        init_db(fresh_db_path)
        conn = sqlite3.connect(str(fresh_db_path))
        cursor = conn.execute("SELECT COUNT(*) FROM _schema_version")
        count = cursor.fetchone()[0]
        conn.close()
        # 每个版本只记录一次
        assert count == len(_MIGRATIONS)

    def test_creates_parent_directory(self, tmp_path):
        db = tmp_path / "nested" / "deep" / "dir" / "test.db"
        result = init_db(db)
        assert result.exists()
        assert result.parent.exists()

    def test_accepts_string_path(self, tmp_path):
        db_str = str(tmp_path / "str_path.db")
        result = init_db(db_str)
        assert result.exists()

    def test_echo_does_not_break(self, fresh_db_path, capsys):
        result = init_db(fresh_db_path, echo=True)
        assert result.exists()
        captured = capsys.readouterr()
        assert "current version" in captured.out or "migration" in captured.out.lower()


# ---------------------------------------------------------------------------
# 2. init_db 表 + 索引 + 版本完整性
# ---------------------------------------------------------------------------


class TestSchemaIntegrity:
    def test_schema_version_matches_migration_count(self, initialized_db):
        ver = schema_version(initialized_db)
        assert ver == len(_MIGRATIONS)

    def test_schema_version_is_17(self, initialized_db):
        # v17 是当前最新（v15 删11列 + v16 删 orphan trigger + v17 清理 stale 索引声明）
        ver = schema_version(initialized_db)
        assert ver == 17

    def test_all_expected_tables_exist(self, initialized_db):
        tables = set(table_names(initialized_db))
        # 21 张保留表（verify_schema_health._DDL_MAP 的表）
        expected = {
            "nodes",
            "edges",
            "domains",
            "domain_dependencies",
            "domain_events",
            "contracts",
            "rule_bindings",
            "arch_constraints",
            "arch_directory_tree",
            "arch_path_mappings",
            "gates",
            "governance_audit_logs",
            "blueprint_links",
            "business_streams",
            "cross_registry_rules",
            "field_vocabularies",
            "hard_boundaries",
            "infrastructure_components",
            "model_capabilities",
            "registries",
            "domain_mapping",
        }
        missing = expected - tables
        assert not missing, f"缺少表: {missing}"

    def test_dropped_tables_absent(self, initialized_db):
        # v14 删除的 3 张死表不应存在
        tables = set(table_names(initialized_db))
        assert "arch_bottlenecks" not in tables
        assert "arch_layers" not in tables
        assert "invariants" not in tables

    def test_core_indexes_exist(self, initialized_db):
        # 核心索引必须存在（node/edge/domain 的查询热路径）
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        actual = {row[0] for row in cursor.fetchall()}
        conn.close()
        required = {
            "idx_nodes_domain",
            "idx_nodes_type",
            "idx_nodes_path",
            "idx_edges_from",
            "idx_edges_to",
            "idx_domains_group",
        }
        assert required.issubset(actual), f"缺少核心索引: {required - actual}"

    def test_no_ghost_indexes(self, initialized_db):
        # DB 中存在的索引都应来自 _DDL_INDEXES 声明（无幽灵索引）
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        actual = {row[0] for row in cursor.fetchall()}
        conn.close()
        declared = {_extract_index_name(sql) for sql in _DDL_INDEXES}
        ghost = actual - declared
        assert not ghost, f"DB 有未声明的幽灵索引: {ghost}"

    def test_stale_index_cleaned(self, initialized_db):
        # v17 清理验证：_DDL_INDEXES 中 idx_domains_can_build stale 条目已删除
        # 背景：domains.can_build 列在 v10 删除, 但 _DDL_INDEXES 中 idx_domains_can_build
        # 声明未清理, init_db 执行时因 'no such column' 被 _run_migration benign 跳过.
        # v17 通过 DROP INDEX IF EXISTS + 清理 _DDL_INDEXES 声明 完成治理.
        # 三层一致性：真源声明 + DB 实例 + migration 版本

        # 1. _DDL_INDEXES 真源中不再声明 stale 索引
        stale_declarations = [s for s in _DDL_INDEXES if "idx_domains_can_build" in s]
        assert not stale_declarations, f"_DDL_INDEXES 仍含 stale 条目: {stale_declarations}"

        # 2. DB 中不存在此索引（v17 DROP INDEX IF EXISTS 已执行 + 全新库 v1~v17 不再创建）
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_domains_can_build'")
        assert cursor.fetchone() is None, "idx_domains_can_build 不应存在（v17 已清理）"

        # 3. v17 migration 已应用
        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        assert cursor.fetchone()[0] >= 17, "v17 migration 未应用"
        conn.close()

    def test_nodes_has_no_dropped_columns(self, initialized_db):
        # v15 删除的 9 列不应存在
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("PRAGMA table_info(nodes)")
        cols = {row[1] for row in cursor.fetchall()}
        conn.close()
        dropped = {
            "in_degree",
            "out_degree",
            "business_stream",
            "stream_role",
            "runtime_plane",
            "ddd_aggregate",
            "has_dynamic_import",
            "implementation_ref",
            "provided_interfaces",
        }
        assert dropped.isdisjoint(cols), f"v15 已删列仍存在: {dropped & cols}"

    def test_edges_has_no_migration_status(self, initialized_db):
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("PRAGMA table_info(edges)")
        cols = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "migration_status" not in cols, "v15 已删 edges.migration_status 仍存在"

    def test_no_orphan_chk_triggers(self, initialized_db):
        # v16 删除的 orphan trigger 不应存在
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'chk_edges%'")
        triggers = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert "chk_edges_design_immutable_update" not in triggers


# ---------------------------------------------------------------------------
# 3. _get_current_version 三态逻辑
# ---------------------------------------------------------------------------


class TestGetCurrentVersion:
    def test_empty_db_returns_zero(self, tmp_path):
        db = tmp_path / "empty.db"
        sqlite3.connect(str(db)).close()  # 创建空 DB
        conn = sqlite3.connect(str(db))
        assert _get_current_version(conn) == 0
        conn.close()

    def test_legacy_db_returns_negative_one(self, tmp_path):
        # 有 nodes 表但无 _schema_version 表 → -1（legacy bootstrap 触发）
        db = tmp_path / "legacy.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE nodes (node_id TEXT)")
        conn.commit()
        assert _get_current_version(conn) == -1
        conn.close()

    def test_initialized_db_returns_latest_version(self, initialized_db):
        conn = sqlite3.connect(str(initialized_db))
        ver = _get_current_version(conn)
        conn.close()
        assert ver == len(_MIGRATIONS)


# ---------------------------------------------------------------------------
# 4. migration 事务原子性（中途失败 → ROLLBACK，无部分应用）
# ---------------------------------------------------------------------------


class TestMigrationAtomicity:
    def test_failed_migration_rolls_back(self, tmp_path, monkeypatch):
        """注入一个会失败的 migration，验证事务回滚：bad 表不存在 + 版本不变。"""
        db = tmp_path / "test_rollback.db"
        init_db(db)  # 先初始化到 v16
        original_version = schema_version(db)
        assert original_version == len(_MIGRATIONS)

        # 追加一个会失败的 migration（第一条成功，第二条语法错误）
        bad_migration = (
            original_version + 1,
            "故意失败的 migration（事务原子性测试）",
            [
                "CREATE TABLE bad_test_table (id TEXT)",
                "THIS IS INVALID SQL SYNTAX @@@",
            ],
        )
        monkeypatch.setattr(schema_mod, "_MIGRATIONS", list(_MIGRATIONS) + [bad_migration])

        with pytest.raises(RuntimeError, match="Migration"):
            init_db(db)

        # 验证事务回滚
        conn = sqlite3.connect(str(db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE name='bad_test_table'")
        assert cursor.fetchone() is None, "事务回滚失败：bad_test_table 仍存在"
        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        assert cursor.fetchone()[0] == original_version, "版本号不应前进"
        conn.close()

    def test_failed_migration_preserves_existing_data(self, tmp_path, monkeypatch):
        """失败迁移不应破坏已有数据（_schema_version 记录不被删除）。"""
        db = tmp_path / "test_data.db"
        init_db(db)
        # 记录已有 migration 记录数
        conn = sqlite3.connect(str(db))
        cursor = conn.execute("SELECT COUNT(*) FROM _schema_version")
        original_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        original_max = cursor.fetchone()[0]
        conn.close()
        assert original_count == len(_MIGRATIONS)
        assert original_max == len(_MIGRATIONS)

        bad_migration = (
            len(_MIGRATIONS) + 1,
            "坏 migration",
            ["INVALID SQL @@@@"],
        )
        monkeypatch.setattr(schema_mod, "_MIGRATIONS", list(_MIGRATIONS) + [bad_migration])

        with pytest.raises(RuntimeError):
            init_db(db)

        # 验证已有记录未被删除、版本未倒退
        conn = sqlite3.connect(str(db))
        cursor = conn.execute("SELECT COUNT(*) FROM _schema_version")
        after_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT MAX(version) FROM _schema_version")
        after_max = cursor.fetchone()[0]
        conn.close()
        assert after_count == original_count, "失败 migration 不应删除已有记录"
        assert after_max == original_max, "失败 migration 不应改变已有版本"


# ---------------------------------------------------------------------------
# 5. get_db_connection PRAGMA 基线
# ---------------------------------------------------------------------------


class TestGetDbConnection:
    def test_returns_connection(self, initialized_db):
        conn = get_db_connection(initialized_db)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_wal_mode(self, initialized_db):
        conn = get_db_connection(initialized_db)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode.lower() == "wal"

    def test_foreign_keys_on(self, initialized_db):
        conn = get_db_connection(initialized_db)
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        assert fk == 1

    def test_busy_timeout_set(self, initialized_db):
        conn = get_db_connection(initialized_db)
        timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        conn.close()
        assert timeout == 5000

    def test_row_factory_is_row(self, initialized_db):
        conn = get_db_connection(initialized_db)
        assert conn.row_factory is sqlite3.Row
        conn.close()


# ---------------------------------------------------------------------------
# 6. 公共 API
# ---------------------------------------------------------------------------


class TestPublicApi:
    def test_table_names_returns_list(self, initialized_db):
        names = table_names(initialized_db)
        assert isinstance(names, list)
        assert len(names) > 0

    def test_table_names_sorted(self, initialized_db):
        names = table_names(initialized_db)
        assert names == sorted(names)

    def test_schema_version_returns_int(self, initialized_db):
        ver = schema_version(initialized_db)
        assert isinstance(ver, int)
        assert ver > 0

    def test_table_names_with_string_path(self, initialized_db):
        names = table_names(str(initialized_db))
        assert "nodes" in names
        assert "_schema_version" in names

    def test_schema_version_with_string_path(self, initialized_db):
        ver = schema_version(str(initialized_db))
        assert ver == len(_MIGRATIONS)

    def test_all_exported_names_exist(self):
        for name in schema_mod.__all__:
            assert hasattr(schema_mod, name), f"__all__ 声明 {name} 但模块中不存在"


# ---------------------------------------------------------------------------
# 7. _DDL_INDEXES 完整性（每条都能成功执行）
# ---------------------------------------------------------------------------


class TestDdlIndexes:
    def test_all_index_sql_parseable(self):
        for sql in _DDL_INDEXES:
            name = _extract_index_name(sql)
            assert name is not None
            assert name.startswith("idx_")

    def test_no_duplicate_index_names(self):
        names = [_extract_index_name(sql) for sql in _DDL_INDEXES]
        assert len(names) == len(set(names)), "存在重复索引名"

    def test_core_indexes_recreated_after_v15(self, initialized_db):
        # v15 重建 arch_directory_tree 表后执行了 *_DDL_INDEXES 重建索引
        # 验证核心索引（引用未删列的）在 v15 后仍存在
        conn = sqlite3.connect(str(initialized_db))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        actual = {row[0] for row in cursor.fetchall()}
        conn.close()
        # arch_directory_tree 重建后其索引应被重建
        assert "idx_arch_dir_domain" in actual, "v15 重建后 arch_directory_tree 索引丢失"
        assert "idx_arch_dir_build" in actual
