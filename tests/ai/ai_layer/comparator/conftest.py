"""conftest — L4 测试夹具：PG 可达性探测 + 一次性临时 schema 部署/清理（真 DDL、真 PG）。

测试隔离铁律：测试禁写生产路径——PG 用例一律落 `ai_compare_test_l4cmp` 临时 schema，
session 结束 DROP；journal/文件用 tmp_path。PG 不可达时 skip（skip 而非假绿）。
"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.comparator.experiment_store import deploy as deploy_ddl

TEST_SCHEMA = "ai_compare_test_l4cmp"


def pg_reachable() -> bool:
    """PG 可达性探测（任何异常都判不可达——skip 而非假绿）。"""
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        try:
            conn.cursor().execute("SELECT 1")
        finally:
            conn.close()
        return True
    except Exception:  # noqa: BLE001——可达性探测，任何异常都判不可达
        return False


PG_OK = pg_reachable()


@pytest.fixture(scope="session")
def test_schema() -> str:
    """部署一次性临时 schema（真 DDL、真 PG、superuser 通道），session 结束 DROP。"""
    if not PG_OK:
        pytest.skip("PostgreSQL 不可达（skip 而非假绿）")
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    def _admin_exec(sql: str) -> None:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
        try:
            conn.cursor().execute(sql)
        finally:
            conn.close()

    _admin_exec(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
    deploy_ddl(TEST_SCHEMA)
    yield TEST_SCHEMA
    _admin_exec(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
