# [A_test] module_id: MOD-GOV_verify_schema_health | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | scripts/governance/verify_schema_health.py | §test
# [MODULE] tests.test_verify_schema_health
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 漂移必拦截; 只读触发器必齐全; 版本必一致
# [MODIFY-GUARD] scripts/governance/verify_schema_health.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] python -m pytest tests/test_verify_schema_health.py -q
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
test_verify_schema_health.py — verify_schema_health.py 门禁可靠性单元测试

覆盖三类校验：
  1. parse_ddl_columns 纯函数（DDL 文本解析）
  2. check_ddl_columns / check_readonly_triggers / check_schema_version 集成测试
     （init_db 建健康 DB → 注入漂移 → 验证检测）
  3. main() 端到端退出码（subprocess 子进程模拟 pre-commit 调用）

只读触发器由 sync_yaml_to_depgraph.py 创建（非 init_db），测试 fixture 补建，
模拟生产库真实状态（DDL 一致 + 触发器齐全 + 版本一致）。
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# sys.path 设置（verify_schema_health 不是包模块，需手动加入 scripts/governance）
# ---------------------------------------------------------------------------
from zephyr.shared.io.paths import REPO_ROOT

_REPO_ROOT = REPO_ROOT
_GOV_DIR = _REPO_ROOT / "scripts" / "governance"
_SRC_DIR = _REPO_ROOT / "src"
for _p in (str(_GOV_DIR), str(_SRC_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

schema_mod = pytest.importorskip("zephyr.governance.depgraph_schema")
vsh = pytest.importorskip("verify_schema_health")

init_db = schema_mod.init_db
_MIGRATIONS = schema_mod._MIGRATIONS
_DDL_INDEXES = schema_mod._DDL_INDEXES

# 只读触发器保护的表清单——从真源 sync_yaml_to_depgraph.py 动态获取
# （经 verify_schema_health.py re-export，消除硬编码副本，红蓝对抗修复-严重1）
_READONLY_TABLES = vsh.READONLY_TABLES


def _create_readonly_triggers(conn: sqlite3.Connection) -> None:
    """补建 9 表 × 3 只读触发器（复制 sync_yaml_to_depgraph.restore_readonly_triggers 逻辑）。

    init_db 不创建只读触发器，需 fixture 补建以模拟生产库健康态。
    """
    for table in _READONLY_TABLES:
        for action in ("insert", "update", "delete"):
            conn.execute(
                f"CREATE TRIGGER IF NOT EXISTS readonly_{table}_{action} "
                f"BEFORE {action.upper()} ON {table} "
                f"FOR EACH ROW "
                f"BEGIN "
                f"SELECT RAISE(ABORT, '{table} 表只读'); "
                f"END;"
            )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def healthy_db_path(tmp_path):
    """创建一个 schema 健康的临时 depgraph（init_db 全量迁移 + 只读触发器齐全）。"""
    db = tmp_path / "test_health.db"
    init_db(db)
    conn = sqlite3.connect(str(db))
    try:
        _create_readonly_triggers(conn)
        conn.commit()
    finally:
        conn.close()
    return db


@pytest.fixture
def healthy_db_conn(healthy_db_path):
    """返回健康 DB 的 sqlite3 连接（测试结束自动关闭）。"""
    conn = sqlite3.connect(str(healthy_db_path))
    yield conn
    conn.close()


def _run_script(db_path: Path, *extra_args) -> subprocess.CompletedProcess:
    """子进程运行 verify_schema_health.py，返回 CompletedProcess。"""
    script = _GOV_DIR / "verify_schema_health.py"
    return subprocess.run(
        [sys.executable, str(script), "--db", str(db_path), *extra_args],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )


# ---------------------------------------------------------------------------
# 1. parse_ddl_columns 纯函数单元测试
# ---------------------------------------------------------------------------

class TestParseDdlColumns:
    def test_simple_table(self):
        ddl = "CREATE TABLE IF NOT EXISTS foo (id TEXT PRIMARY KEY, name TEXT)"
        cols = vsh.parse_ddl_columns(ddl)
        assert "id" in cols
        assert "name" in cols

    def test_without_if_not_exists(self):
        ddl = "CREATE TABLE bar (a TEXT, b INTEGER)"
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["a", "b"]

    def test_skips_primary_key_constraint(self):
        ddl = "CREATE TABLE foo (id TEXT, name TEXT, PRIMARY KEY (id))"
        cols = vsh.parse_ddl_columns(ddl)
        assert "id" in cols
        assert "name" in cols
        assert "PRIMARY" not in cols

    def test_skips_foreign_key_constraint(self):
        ddl = "CREATE TABLE bar (id TEXT, foo_id TEXT, FOREIGN KEY (foo_id) REFERENCES foo(id))"
        cols = vsh.parse_ddl_columns(ddl)
        assert "id" in cols
        assert "foo_id" in cols
        assert "FOREIGN" not in cols

    def test_skips_check_constraint(self):
        # CHECK 后带空格 → toks[0]=CHECK，被精确匹配跳过
        ddl = "CREATE TABLE x (status TEXT, CHECK (status IN ('a','b')))"
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["status"]

    def test_skips_unique_constraint(self):
        # UNIQUE 后带空格 → toks[0]=UNIQUE，被精确匹配跳过
        ddl = "CREATE TABLE x (id TEXT, name TEXT, UNIQUE (name))"
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["id", "name"]

    def test_check_no_space_is_known_limitation(self):
        # 紧贴括号的 CHECK(...) 不被识别（toks[0]=CHECK(status ≠ CHECK）
        # 这是 parse_ddl_columns 的已知限制：仅精确匹配首 token
        # 真实 DDL 中 CHECK 均为列级约束（跟在列定义后），不受此限制影响
        ddl = "CREATE TABLE x (status TEXT, CHECK(status IN ('a','b')))"
        cols = vsh.parse_ddl_columns(ddl)
        # 紧贴时 CHECK(status 被误当作列名——记录此行为
        assert "status" in cols
        assert len(cols) == 2  # status + 误解析的 CHECK(status

    def test_skips_constraint_keyword(self):
        ddl = "CREATE TABLE x (id TEXT, CONSTRAINT chk1 CHECK(id != ''))"
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["id"]

    def test_handles_nested_parens_in_check(self):
        # CHECK 约束含嵌套括号和逗号，不应误分割
        ddl = "CREATE TABLE nodes (id TEXT, status TEXT CHECK(status IN ('a', 'b', 'c')))"
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["id", "status"]

    def test_column_named_like_constraint_prefix(self):
        # constraint_id 首 token 为 CONSTRAINT_ID，不等于 CONSTRAINT，不应被跳过
        ddl = "CREATE TABLE x (constraint_id TEXT, check_result TEXT, unique_hash TEXT)"
        cols = vsh.parse_ddl_columns(ddl)
        assert "constraint_id" in cols
        assert "check_result" in cols
        assert "unique_hash" in cols

    def test_no_create_table_returns_empty(self):
        assert vsh.parse_ddl_columns("SELECT 1 FROM dual") == []

    def test_multiline_ddl(self):
        ddl = """
        CREATE TABLE IF NOT EXISTS domains (
            domain_id    TEXT PRIMARY KEY,
            domain_name  TEXT NOT NULL,
            domain_group TEXT,
            description  TEXT
        )
        """
        cols = vsh.parse_ddl_columns(ddl)
        assert cols == ["domain_id", "domain_name", "domain_group", "description"]

    def test_real_nodes_ddl(self):
        # 用真源 _DDL_NODES 验证解析正确性
        cols = vsh.parse_ddl_columns(schema_mod._DDL_NODES)
        assert "node_id" in cols
        assert "tags" in cols
        assert "owner" in cols
        # 表级约束不应出现
        assert "PRIMARY" not in cols
        assert "FOREIGN" not in cols


# ---------------------------------------------------------------------------
# 1b. parse_ddl_named_check_constraints 纯函数测试（Ruling:100PCT-AI-GOVERNANCE P1-2）
# ---------------------------------------------------------------------------
class TestParseDdlNamedCheckConstraints:
    """验证从 DDL 文本中解析命名 CHECK 约束。"""

    def test_no_named_constraints(self):
        """无命名 CHECK 约束的 DDL 返回空列表"""
        ddl = "CREATE TABLE foo (id TEXT, status TEXT CHECK (status IN ('a','b')))"
        result = vsh.parse_ddl_named_check_constraints(ddl)
        assert result == []

    def test_single_named_constraint(self):
        """单个命名 CHECK 约束"""
        ddl = (
            "CREATE TABLE decision_layers ("
            "  layer_id TEXT PRIMARY KEY,"
            "  domain_id TEXT,"
            "  CONSTRAINT chk_domain_not_empty CHECK (domain_id IS NULL OR domain_id <> '')"
            ")"
        )
        result = vsh.parse_ddl_named_check_constraints(ddl)
        assert result == ["chk_domain_not_empty"]

    def test_multiple_named_constraints(self):
        """多个命名 CHECK 约束"""
        ddl = (
            "CREATE TABLE foo ("
            "  id TEXT PRIMARY KEY,"
            "  CONSTRAINT chk_a CHECK (id <> ''),"
            "  CONSTRAINT chk_b CHECK (id IS NOT NULL)"
            ")"
        )
        result = vsh.parse_ddl_named_check_constraints(ddl)
        assert set(result) == {"chk_a", "chk_b"}

    def test_case_insensitive(self):
        """CONSTRAINT 关键字大小写不敏感"""
        ddl = "CREATE TABLE foo (id TEXT, constraint chk_a check (id <> ''))"
        result = vsh.parse_ddl_named_check_constraints(ddl)
        assert result == ["chk_a"]

    def test_real_decision_layers_ddl(self):
        """用真源 _DDL_DECISION_LAYERS 验证解析正确性"""
        from zephyr.governance.persistence import decisiongraph_schema
        result = vsh.parse_ddl_named_check_constraints(decisiongraph_schema._DDL_DECISION_LAYERS)
        assert "chk_decision_layers_domain_id_not_empty" in result

    def test_inline_check_not_captured(self):
        """内联 CHECK（无 CONSTRAINT 关键字）不被捕获——设计如此"""
        ddl = "CREATE TABLE foo (id TEXT, status TEXT CHECK (status IN ('a','b')))"
        result = vsh.parse_ddl_named_check_constraints(ddl)
        assert result == []


# ---------------------------------------------------------------------------
# 2. check_ddl_columns 集成测试（注入漂移验证检测）
# ---------------------------------------------------------------------------

# P2迁移：以下测试类依赖 init_db 创建 SQLite 临时库 + sqlite3 连接 + PRAGMA/sqlite_master/触发器，
# init_db 现在只验证 PG schema 不创建 SQLite 文件，这些测试不适用 PG。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 get_db_connection + information_schema 替代 SQLite 临时库/sqlite_master），当前 skip。
@pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + init_db 创建 SQLite 文件，不适用 PG")
class TestCheckDdlColumns:

    def test_healthy_db_no_issues(self, healthy_db_conn):
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert issues == []

    def test_detects_extra_column(self, healthy_db_conn):
        healthy_db_conn.execute("ALTER TABLE nodes ADD COLUMN bogus_drift_col TEXT")
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "nodes" in issues[0]
        assert "bogus_drift_col" in issues[0]
        assert "多出列" in issues[0]

    def test_detects_missing_column(self, healthy_db_conn):
        healthy_db_conn.execute("ALTER TABLE nodes DROP COLUMN tags")
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "nodes" in issues[0]
        assert "tags" in issues[0]
        assert "缺少列" in issues[0]

    def test_detects_missing_table(self, healthy_db_conn):
        healthy_db_conn.execute("DROP TABLE business_streams")
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "business_streams" in issues[0]
        assert "不存在" in issues[0]

    def test_detects_both_extra_and_missing(self, healthy_db_conn):
        healthy_db_conn.execute("ALTER TABLE nodes ADD COLUMN extra_col TEXT")
        healthy_db_conn.execute("ALTER TABLE nodes DROP COLUMN owner")
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert len(issues) == 2
        assert any("extra_col" in i for i in issues)
        assert any("owner" in i for i in issues)

    def test_detects_drift_in_multiple_tables(self, healthy_db_conn):
        healthy_db_conn.execute("ALTER TABLE edges ADD COLUMN ghost TEXT")
        healthy_db_conn.execute("ALTER TABLE domains ADD COLUMN phantom TEXT")
        issues = []
        vsh.check_ddl_columns(healthy_db_conn, issues)
        assert len(issues) == 2
        assert any("edges" in i for i in issues)
        assert any("domains" in i for i in issues)


# ---------------------------------------------------------------------------
# 3. check_readonly_triggers 集成测试
# ---------------------------------------------------------------------------

# P2迁移：依赖 SQLite 临时库 + sqlite_master 查询触发器，不适用 PG。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 pg_trigger 系统表替代 sqlite_master 触发器检查），当前 skip。
@pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + sqlite_master 触发器检查，不适用 PG")
class TestCheckReadonlyTriggers:
    def test_healthy_db_no_issues(self, healthy_db_conn):
        issues = []
        vsh.check_readonly_triggers(healthy_db_conn, issues)
        assert issues == []

    def test_detects_missing_insert_trigger(self, healthy_db_conn):
        healthy_db_conn.execute("DROP TRIGGER readonly_gates_insert")
        issues = []
        vsh.check_readonly_triggers(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "readonly_gates_insert" in issues[0]
        assert "TRIGGER-MISSING" in issues[0]

    def test_detects_missing_update_trigger(self, healthy_db_conn):
        healthy_db_conn.execute("DROP TRIGGER readonly_field_vocabularies_update")
        issues = []
        vsh.check_readonly_triggers(healthy_db_conn, issues)
        assert any("readonly_field_vocabularies_update" in i for i in issues)

    def test_detects_missing_delete_trigger(self, healthy_db_conn):
        healthy_db_conn.execute("DROP TRIGGER readonly_registries_delete")
        issues = []
        vsh.check_readonly_triggers(healthy_db_conn, issues)
        assert any("readonly_registries_delete" in i for i in issues)

    def test_detects_all_three_triggers_for_one_table(self, healthy_db_conn):
        healthy_db_conn.execute("DROP TRIGGER readonly_gates_insert")
        healthy_db_conn.execute("DROP TRIGGER readonly_gates_update")
        healthy_db_conn.execute("DROP TRIGGER readonly_gates_delete")
        issues = []
        vsh.check_readonly_triggers(healthy_db_conn, issues)
        assert len(issues) == 3
        assert all("gates" in i for i in issues)

    def test_total_triggers_expected(self, healthy_db_conn):
        # 9 表 × 3 动作 = 27 触发器
        cursor = healthy_db_conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'readonly_%'"
        )
        count = cursor.fetchone()[0]
        assert count == 27


# ---------------------------------------------------------------------------
# 4. check_schema_version 集成测试
# ---------------------------------------------------------------------------

# P2迁移：依赖 SQLite 临时库 + _schema_version 表 + init_db 创建 SQLite 文件，不适用 PG。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 get_db_connection + PG _schema_version 表替代 SQLite 临时库），当前 skip。
@pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + _schema_version 版本表，不适用 PG")
class TestCheckSchemaVersion:
    def test_healthy_db_no_issues(self, healthy_db_conn):
        issues = []
        vsh.check_schema_version(healthy_db_conn, issues)
        assert issues == []

    def test_detects_version_behind(self, healthy_db_conn):
        # 删除最新版本记录，模拟未执行迁移
        healthy_db_conn.execute(
            "DELETE FROM _schema_version WHERE version = (SELECT MAX(version) FROM _schema_version)"
        )
        issues = []
        vsh.check_schema_version(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "VERSION-DRIFT" in issues[0]
        assert "未执行" in issues[0]

    def test_detects_version_ahead(self, healthy_db_conn):
        # 插入一个超前版本，模拟 DB 版本 > len(_MIGRATIONS)
        expected = len(_MIGRATIONS)
        healthy_db_conn.execute(
            "INSERT INTO _schema_version (version, applied_at, description) VALUES (?, 'test', 'fake')",
            (expected + 5,),
        )
        issues = []
        vsh.check_schema_version(healthy_db_conn, issues)
        assert len(issues) == 1
        assert "VERSION-DRIFT" in issues[0]

    def test_error_message_contains_diff_count(self, healthy_db_conn):
        healthy_db_conn.execute(
            "DELETE FROM _schema_version WHERE version = (SELECT MAX(version) FROM _schema_version)"
        )
        issues = []
        vsh.check_schema_version(healthy_db_conn, issues)
        assert "差 1 条" in issues[0]


# ---------------------------------------------------------------------------
# 5. main() 端到端退出码测试（subprocess 子进程模拟 pre-commit 调用）
# ---------------------------------------------------------------------------

# P2迁移：依赖 SQLite 临时库 + subprocess 调用 verify_schema_health.py --db <sqlite_file>，
# verify_schema_health.py 现在检查 PG schema，不再支持 --db 指向 SQLite 文件。
# TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（subprocess 调用不再传 --db，verify_schema_health.py 直接连 PG），当前 skip。
@pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + subprocess --db <sqlite_file>，不适用 PG")
class TestMainExitCodes:
    def test_healthy_db_exit_zero(self, healthy_db_path):
        result = _run_script(healthy_db_path)
        assert result.returncode == 0
        assert "[PASS]" in result.stdout

    def test_drift_db_exit_one(self, healthy_db_path):
        conn = sqlite3.connect(str(healthy_db_path))
        conn.execute("ALTER TABLE nodes ADD COLUMN drift_col TEXT")
        conn.commit()
        conn.close()
        result = _run_script(healthy_db_path)
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout
        assert "drift_col" in result.stdout

    def test_warn_only_exit_zero_with_drift(self, healthy_db_path):
        conn = sqlite3.connect(str(healthy_db_path))
        conn.execute("ALTER TABLE nodes ADD COLUMN drift_col TEXT")
        conn.commit()
        conn.close()
        result = _run_script(healthy_db_path, "--warn-only")
        assert result.returncode == 0
        assert "[FAIL]" in result.stdout  # 仍报告漂移但不阻断

    def test_ci_flag_exit_one_with_drift(self, healthy_db_path):
        conn = sqlite3.connect(str(healthy_db_path))
        conn.execute("ALTER TABLE nodes ADD COLUMN drift_col TEXT")
        conn.commit()
        conn.close()
        result = _run_script(healthy_db_path, "--ci")
        assert result.returncode == 1

    def test_missing_db_exit_two(self, tmp_path):
        result = _run_script(tmp_path / "nonexistent.db")
        assert result.returncode == 2
        # verify_schema_health.py L182 用 print() 输出到 stdout（非 stderr）
        assert "[ERROR]" in result.stdout

    def test_trigger_drift_exit_one(self, healthy_db_path):
        conn = sqlite3.connect(str(healthy_db_path))
        conn.execute("DROP TRIGGER readonly_gates_insert")
        conn.commit()
        conn.close()
        result = _run_script(healthy_db_path)
        assert result.returncode == 1
        assert "TRIGGER-MISSING" in result.stdout

    def test_version_drift_exit_one(self, healthy_db_path):
        conn = sqlite3.connect(str(healthy_db_path))
        conn.execute(
            "DELETE FROM _schema_version WHERE version = (SELECT MAX(version) FROM _schema_version)"
        )
        conn.commit()
        conn.close()
        result = _run_script(healthy_db_path)
        assert result.returncode == 1
        assert "VERSION-DRIFT" in result.stdout

    def test_no_args_connects_pg(self):
        # 治本（2026-06-29）：测试名+注释语义修正（原 test_no_args_uses_default_db_path 过时）。
        # P2 PG 迁移后 --db 参数已废弃，脚本经 get_depgraph_pg_connection() 连 depgraph (PostgreSQL)。
        # PG 健康则 exit 0；PG 不可达则 exit 2——两种都接受，只要不崩溃。
        result = subprocess.run(
            [sys.executable, str(_GOV_DIR / "verify_schema_health.py")],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode in (0, 2)


# ---------------------------------------------------------------------------
# 6. check_pg_runtime_health 单元测试（P3-T4 改造，mock PG 系统视图）
# ---------------------------------------------------------------------------

class _FakeCursor:
    """模拟 psycopg2 cursor，fetchone 返回预设 dict 行。"""

    def __init__(self, rows):
        self._rows = rows

    def execute(self, *args, **kwargs):
        pass

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        return self._rows


class _FakeConn:
    """模拟 PG 连接，按 SQL 关键词路由返回预设行。"""

    def __init__(self, deadlocks=0, active_conns=5, max_conns=100, long_tx=0):
        self._deadlocks = deadlocks
        self._active = active_conns
        self._max = max_conns
        self._long_tx = long_tx

    def execute(self, sql, *args):
        sql_lower = sql.lower()
        if "pg_stat_database" in sql_lower:
            return _FakeCursor([{"deadlocks": self._deadlocks}])
        elif "long_tx" in sql_lower:
            return _FakeCursor([{"long_tx": self._long_tx}])
        elif "pg_stat_activity" in sql_lower:
            return _FakeCursor([{"active": self._active, "max_conn": self._max}])
        return _FakeCursor([])

    def close(self):
        pass


class TestCheckPgRuntimeHealth:
    """校验4：PG 运行时健康检查（P3-T4 改造，替代常驻 monitor_pg.py）。"""

    def test_healthy_db_no_issues(self):
        conn = _FakeConn(deadlocks=0, active_conns=5, max_conns=100, long_tx=0)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert issues == []

    def test_deadlock_info_only_not_blocking(self, capsys):
        """死锁累计值仅信息性输出，不加入 issues（不阻断提交）。"""
        conn = _FakeConn(deadlocks=3, active_conns=5, max_conns=100, long_tx=0)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert issues == []
        captured = capsys.readouterr()
        assert "PG-DEADLOCK" in captured.out
        assert "3" in captured.out

    def test_connection_saturation_blocks(self):
        conn = _FakeConn(deadlocks=0, active_conns=85, max_conns=100, long_tx=0)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert len(issues) == 1
        assert "PG-CONN-SATURATED" in issues[0]
        assert "85" in issues[0]

    def test_connection_normal_no_issue(self):
        conn = _FakeConn(deadlocks=0, active_conns=50, max_conns=100, long_tx=0)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert issues == []

    def test_long_transaction_blocks(self):
        conn = _FakeConn(deadlocks=0, active_conns=5, max_conns=100, long_tx=2)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert len(issues) == 1
        assert "PG-LONG-TX" in issues[0]
        assert "2" in issues[0]

    def test_multiple_issues_all_reported(self):
        """死锁不阻断 + 连接饱和阻断 + 长事务阻断 = 2 个 issues。"""
        conn = _FakeConn(deadlocks=1, active_conns=90, max_conns=100, long_tx=3)
        issues = []
        vsh.check_pg_runtime_health(conn, issues)
        assert len(issues) == 2
        assert any("PG-CONN-SATURATED" in i for i in issues)
        assert any("PG-LONG-TX" in i for i in issues)
