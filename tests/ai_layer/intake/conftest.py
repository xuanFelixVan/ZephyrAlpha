"""conftest — L2 测试夹具：PG 可达性探测 + 一次性临时 schema 部署/清理。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[3]
DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_intake_ddl.py"
TEST_SCHEMA = "ai_intake_test_aibase"


def _load_ddl() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ai_intake_ddl_under_test", DDL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def pg_reachable() -> bool:
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001——可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


pytestmark_pg = pytest.mark.skipif(not pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@pytest.fixture(scope="session")
def ddl() -> ModuleType:
    return _load_ddl()


@pytest.fixture(scope="session")
def test_schema(ddl: ModuleType) -> str:
    """部署一次性临时 schema（真 DDL、真 PG），session 结束 DROP。"""
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % TEST_SCHEMA)
    deploy = getattr(ddl, "deploy", None) or getattr(ddl, "apply_ddl", None) or getattr(ddl, "main")
    rc = deploy(schema=TEST_SCHEMA) if callable(deploy) and getattr(deploy, "__name__", "") != "main" else None
    if rc is None:
        # 走 CLI 幂等部署（deploy 签名不匹配时的兜底路径）
        code = deploy(["--schema", TEST_SCHEMA])
        assert code == 0, f"临时 schema 部署失败 rc={code}"
    yield TEST_SCHEMA
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % TEST_SCHEMA)
