# [A_test] module_id: MOD-GOV_migrate_sqlite_to_pg | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-migrate_sqlite_to_pg | docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md | §migrate_data
# [MODULE] tests.governance.test_migrate_sqlite_to_pg
# [DOMAIN] D_GOVERNANCE
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-migrate_sqlite_to_pg | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_migrate_sqlite_to_pg.py — SQLite→PG 迁移脚本测试（5.32.3 治本：零测试）

覆盖 5.32.2（每表独立事务）/ 5.32.4（migration_log 幂等）/ 5.32.10（种子表拆分）：
- tmp_path 造小型 SQLite fixture（2 表 × 3 行），验证迁移后行数一致
- 幂等：二次运行检测到 migration_log completed 记录则跳过
- 单表失败隔离：一表失败 ROLLBACK 仅影响该表，已提交表数据保留
- 触发器恢复在 finally 中保证执行（失败后 replication_role 仍为 origin）
- 种子表与迁移表拆分一致性（SEED_TABLES 与 MIGRATION_ORDER 无交集）

不连真实 PG：用 FakePGConnection 内存假连接 + monkeypatch execute_values。
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MIGRATE_DIR = _REPO_ROOT / "scripts" / "governance" / "migrate_sqlite_to_pg"
if str(_MIGRATE_DIR) not in sys.path:
    sys.path.insert(0, str(_MIGRATE_DIR))

import migrate_data  # noqa: E402
import seed_from_yaml  # noqa: E402

# ── Fake PG 连接（内存模拟，不连真实 PostgreSQL） ─────────────────────────

class _FakeCursor:
    """模拟 psycopg2 cursor：按 SQL 文本路由到内存状态。"""

    def __init__(self, conn: "_FakePGConnection") -> None:
        self._conn = conn
        self._result: list = []

    def __enter__(self) -> "_FakeCursor":
        return self

    def __exit__(self, *args) -> bool:
        return False

    def execute(self, sql: str, params: tuple | None = None) -> None:
        normalized = " ".join(sql.split())
        upper = normalized.upper()
        self._result = []

        if upper.startswith("CREATE TABLE IF NOT EXISTS MIGRATION_LOG"):
            return
        if upper.startswith("SELECT STATUS FROM MIGRATION_LOG"):
            mid = params[0]
            self._result = [
                (r["status"],) for r in self._conn.migration_log if r["migration_id"] == mid
            ][:1]
            return
        if upper.startswith("INSERT INTO MIGRATION_LOG"):
            record = {
                "migration_id": params[0],
                "applied_at": params[1],
                "status": params[2],
                "tables_total": params[3],
                "rows_total": params[4],
                "details": params[5],
            }
            self._conn.migration_log = [
                r for r in self._conn.migration_log if r["migration_id"] != params[0]
            ]
            self._conn.migration_log.append(record)
            return
        if "INFORMATION_SCHEMA.COLUMNS" in upper:
            self._result = []  # 测试无 IDENTITY 列
            return
        if upper.startswith("SET SESSION_REPLICATION_ROLE"):
            self._conn.replication_role = normalized.split("'")[1]
            return
        delete_match = re.match(r'DELETE FROM "(\w+)"', normalized)
        if delete_match:
            tbl = delete_match.group(1)
            self._conn.delete_count[tbl] = self._conn.delete_count.get(tbl, 0) + 1
            self._conn.tables[tbl] = []
            return
        count_match = re.match(r'SELECT COUNT\(\*\) FROM "(\w+)"', normalized)
        if count_match:
            tbl = count_match.group(1)
            self._result = [(len(self._conn.tables.get(tbl, [])),)]
            return
        if upper.startswith("SELECT SETVAL"):
            self._result = [(None,)]
            return
        raise AssertionError(f"FakePG 未预期的 SQL: {normalized}")

    def fetchone(self):
        return self._result[0] if self._result else None

    def fetchall(self):
        return list(self._result)

    def __iter__(self):
        return iter(self._result)


class _FakePGConnection:
    """模拟 psycopg2 连接：内存表 + migration_log + 提交计数。"""

    def __init__(self) -> None:
        self.tables: dict[str, list] = {}
        self.migration_log: list[dict] = []
        self.replication_role = "origin"
        self.commit_count = 0
        self.rollback_count = 0
        self.delete_count: dict[str, int] = {}
        self.autocommit = False

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self)

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1

    def close(self) -> None:
        pass


def _fake_execute_values_factory(fail_tables: set[str]):
    """生成替代 psycopg2.extras.execute_values 的假实现，支持按表注入失败。"""

    def _fake_execute_values(cur, sql, data, page_size=500):
        match = re.search(r'INSERT INTO "(\w+)"', sql)
        tbl = match.group(1)
        if tbl in fail_tables:
            raise RuntimeError(f"注入失败: {tbl}")
        cur._conn.tables.setdefault(tbl, []).extend(data)

    return _fake_execute_values


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def sqlite_conn(tmp_path):
    """小型 SQLite fixture：2 表（nodes/edges）× 3 行。"""
    db_path = tmp_path / "depgraph.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE nodes (node_id INTEGER PRIMARY KEY, path TEXT)")
    conn.execute(
        "CREATE TABLE edges (edge_id INTEGER PRIMARY KEY, from_node_id INTEGER, to_node_id INTEGER)"
    )
    conn.executemany("INSERT INTO nodes VALUES (?, ?)", [(1, "a.py"), (2, "b.py"), (3, "c.py")])
    conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", [(10, 1, 2), (11, 2, 3), (12, 3, 1)])
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def pg():
    return _FakePGConnection()


@pytest.fixture
def no_fail(monkeypatch):
    """默认 execute_values 不注入失败。返回 fail_tables 集合供测试修改。"""
    fail_tables: set[str] = set()
    monkeypatch.setattr(migrate_data, "execute_values", _fake_execute_values_factory(fail_tables))
    return fail_tables


TABLES = ["nodes", "edges"]


# ── 5.32.2 每表独立事务 ─────────────────────────────────────────────────

def test_per_table_transaction_commits_each_table(sqlite_conn, pg, no_fail):
    """迁移后每表行数与 SQLite 一致，且每表独立 COMMIT（非单大事务）。"""
    rc = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t1")

    assert rc == 0
    assert len(pg.tables["nodes"]) == 3
    assert len(pg.tables["edges"]) == 3
    # 两表各有独立 DELETE（独立事务边界标志），且提交数不少于表数
    assert pg.delete_count == {"nodes": 1, "edges": 1}
    assert pg.commit_count >= len(TABLES)
    assert pg.migration_log[0]["status"] == "completed"
    assert pg.migration_log[0]["rows_total"] == 6


def test_table_failure_isolation(sqlite_conn, pg, no_fail):
    """一表失败 ROLLBACK 仅影响该表；已提交表保留；状态记为 partial 允许重跑。"""
    no_fail.add("edges")
    rc = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t2")

    assert rc == 1
    assert len(pg.tables["nodes"]) == 3  # 已提交表不受损
    assert pg.tables["edges"] == []  # 失败表已回滚（DELETE 后未插入）
    assert pg.rollback_count >= 1
    assert pg.migration_log[0]["status"] == "partial"

    # partial 不阻断重跑：修复后重跑成功并记录 completed
    no_fail.discard("edges")
    rc2 = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t2")
    assert rc2 == 0
    assert len(pg.tables["edges"]) == 3
    assert pg.migration_log[0]["status"] == "completed"


def test_triggers_restored_in_finally_on_failure(sqlite_conn, pg, no_fail):
    """迁移失败时触发器恢复在 finally 中保证执行（replication_role 回 origin）。"""
    no_fail.add("edges")
    migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t3")
    assert pg.replication_role == "origin"


# ── 5.32.4 migration_log 幂等 ───────────────────────────────────────────

def test_second_run_skips_when_completed(sqlite_conn, pg, no_fail):
    """二次运行检测到 completed 记录则跳过（不再 DELETE/INSERT）。"""
    rc1 = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t4")
    assert rc1 == 0
    first_deletes = dict(pg.delete_count)
    first_rows = {t: list(rows) for t, rows in pg.tables.items()}

    rc2 = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t4")
    assert rc2 == 0
    assert pg.delete_count == first_deletes  # 无新增 DELETE
    assert pg.tables == first_rows  # 数据未被触碰


def test_force_reruns_even_when_completed(sqlite_conn, pg, no_fail):
    """--force 语义：已完成也强制重跑（每表事务保证幂等不翻倍）。"""
    migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t5")
    rc = migrate_data.run_migration(sqlite_conn, pg, tables=TABLES, migration_id="t5", force=True)
    assert rc == 0
    assert pg.delete_count == {"nodes": 2, "edges": 2}
    assert len(pg.tables["nodes"]) == 3  # 重跑不翻倍


# ── 5.32.10 种子表拆分一致性 ────────────────────────────────────────────

def test_seed_tables_split_consistency():
    """种子表（YAML 真源）与迁移表（运营数据）无交集，且两脚本清单一致。"""
    assert migrate_data.SEED_TABLES.isdisjoint(migrate_data.MIGRATION_ORDER)
    assert set(seed_from_yaml.SEED_TABLES) == set(migrate_data.SEED_TABLES)
    # 运营数据核心表必须在迁移清单（防拆分时丢表）
    for core in ("nodes", "edges", "rule_bindings", "governance_audit_logs"):
        assert core in migrate_data.MIGRATION_ORDER
