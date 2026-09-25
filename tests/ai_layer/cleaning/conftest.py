"""conftest — L3 清洗段测试夹具：PG 可达性探测 + 临时 schema 部署（卡表借 L2 DDL，规格表用 ensure_table）。

纪律：只写 ai_intake_test_* 临时 schema（session 末 DROP），禁触生产 ai_intake；
PG 不可达=skip 而非假绿（自带探测，不 import 在途 conftest 符号）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[3]
L2_DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_intake_ddl.py"
TEST_SCHEMA = "ai_intake_test_cleaning"


def _load_l2_ddl() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ai_intake_ddl_for_cleaning_tests", L2_DDL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import (
            get_depgraph_pg_connection,
            release_depgraph_pg_connection,
        )

        conn = get_depgraph_pg_connection(read_only=True)
        try:
            conn.cursor().execute("SELECT 1")
            return True
        finally:
            release_depgraph_pg_connection(conn)
    except Exception:  # noqa: BLE001  可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


needs_pg = pytest.mark.skipif(not pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@pytest.fixture(scope="session")
def l2_ddl() -> ModuleType:
    return _load_l2_ddl()


@pytest.fixture(scope="session")
def test_schema(l2_ddl: ModuleType) -> str:
    """一次性临时 schema：L2 五表（卡 FK 需要）+ L3 规格表，session 末 DROP。"""
    from zephyr.governance.depgraph_schema import (
        get_depgraph_pg_connection,
        release_depgraph_pg_connection,
    )

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
        l2_ddl.deploy(schema=TEST_SCHEMA)
        from zephyr.ai_layer.cleaning.spec_store import ensure_table

        ensure_table(TEST_SCHEMA)
        yield TEST_SCHEMA
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
    finally:
        release_depgraph_pg_connection(conn)
