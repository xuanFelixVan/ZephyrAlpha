# [A_test] module_id: MOD-GOV_database_service | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DATABASE_SERVICE | src/zephyr/governance/persistence/database_service.py | §22
# [MODULE] tests.governance.test_database_service
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_DATABASE_SERVICE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
R2-1: DatabaseService 测试 — governance/depgraph 连接与健康检查

覆盖项：
1. get_governance_conn() 返回有效的 SQLite 连接
2. get_depgraph_conn() 返回有效的 PostgreSQL 连接
3. health_check() 对 governance.db / depgraph 执行 SELECT 1 并返回 True
"""

import sys

import pytest

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT  # alias 真源
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def db_service():
    """DatabaseService 实例 fixture（每个测试独立实例）"""
    from zephyr.governance.persistence.database_service import DatabaseService

    ds = DatabaseService()
    yield ds
    ds.close_all()


class TestDatabaseServiceConnection:
    """DatabaseService 连接测试"""

    def test_get_governance_conn_returns_sqlite(self, db_service):
        """验证 governance.db 连接"""
        import sqlite3

        conn = db_service.get_governance_conn()
        assert isinstance(conn, sqlite3.Connection)
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1

    def test_get_depgraph_conn_returns_pg(self, db_service):
        """验证 depgraph (PostgreSQL) 连接（P2迁移后：psycopg2）"""
        import psycopg2

        conn = db_service.get_depgraph_conn()
        assert isinstance(conn, psycopg2.extensions.connection)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        # RealDictCursor 返回 RealDictRow，用 values() 兼容数字索引访问
        assert list(result.values())[0] == 1


class TestHealthCheck:
    """健康检查测试 — SELECT 1 + WAL检查 + schema版本检查"""

    def test_health_check_governance_returns_true(self, db_service):
        """验证 governance.db 健康检查通过"""
        result = db_service.health_check()
        assert result["governance"] is True

    def test_health_check_depgraph_returns_true(self, db_service):
        """验证 depgraph 健康检查通过"""
        result = db_service.health_check()
        assert result["depgraph"] is True

    def test_health_check_all_pass(self, db_service):
        """验证本模块声明覆盖范围内的数据库健康检查通过（governance + depgraph）。

        clickhouse/redis 为环境可选依赖（config/.env.clickhouse 不存在、redis 未运行
        均为合法环境态），不在本模块覆盖项（docstring 1-3：governance/depgraph）内，
        仅断言键存在不断言 True。
        """
        result = db_service.health_check()
        assert result["governance"] is True and result["depgraph"] is True, f"核心数据库健康检查失败: {result}"
        assert "clickhouse" in result and "redis" in result
