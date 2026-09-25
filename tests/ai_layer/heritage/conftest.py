"""conftest — L7 heritage 测试夹具：PG 可达性探测 + 一次性临时 schema 部署/清理（ai_heritage + ai_intake 双面）。

红线：DB 用例只写 ai_heritage_test_*/ai_intake_test_* 临时 schema（session 末 DROP），禁写生产路径；
PG 不可达=skip 而非假绿；文件产物一律 tmp_path 注入。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[3]
HERITAGE_DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_heritage_ddl.py"
INTAKE_DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_intake_ddl.py"
HERITAGE_TEST_SCHEMA = "ai_heritage_test_herit"
INTAKE_TEST_SCHEMA = "ai_intake_test_herit"


def _load_ddl(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001  可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


needs_pg = pytest.mark.skipif(not pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@pytest.fixture(scope="session")
def heritage_ddl() -> ModuleType:
    return _load_ddl("ai_heritage_ddl_under_test", HERITAGE_DDL_PATH)


@pytest.fixture(scope="session")
def intake_ddl() -> ModuleType:
    return _load_ddl("ai_intake_ddl_under_test", INTAKE_DDL_PATH)


@pytest.fixture(scope="function")
def heritage_schema(heritage_ddl: ModuleType) -> str:
    """每测试部署一次性传承库临时 schema（真 DDL、真 PG），测试末 DROP——隔离登记闸查重面。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {HERITAGE_TEST_SCHEMA} CASCADE")
        heritage_ddl.deploy(schema=HERITAGE_TEST_SCHEMA)
    finally:
        conn.close()
    yield HERITAGE_TEST_SCHEMA
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {HERITAGE_TEST_SCHEMA} CASCADE")
    finally:
        conn.close()


@pytest.fixture(scope="function")
def intake_schema(intake_ddl: ModuleType) -> str:
    """每测试部署一次性 L2 临时 schema（T4 快照面测试用），测试末 DROP。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {INTAKE_TEST_SCHEMA} CASCADE")
        intake_ddl.deploy(schema=INTAKE_TEST_SCHEMA)
    finally:
        conn.close()
    yield INTAKE_TEST_SCHEMA
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {INTAKE_TEST_SCHEMA} CASCADE")
    finally:
        conn.close()
