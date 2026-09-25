# [MODULE] tests.ai_layer.perceive.conftest
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""conftest — L1 perceive 测试夹具：确定性时间锚 + PG 可达性探测 + 一次性临时 schema。

测试纪律：零生产路径写入（journal/账本/产物全部 tmp_path 注入）；PG 用例按真 DDL 部署
一次性临时 schema（ai_intake_test_ 前缀，session 结束 DROP），PG 不可达=skip 非 fail。
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[3]
DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_intake_ddl.py"
TEST_SCHEMA = "ai_intake_test_perceive"

FIXED_NOW: datetime = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)


def _pg_reachable() -> bool:
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001  可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


pytestmark_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@pytest.fixture(scope="session")
def ddl() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ai_intake_ddl_perceive", DDL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def test_schema(ddl: ModuleType) -> str:
    """部署一次性临时 schema（真 DDL、真 PG），session 结束 DROP。"""
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % TEST_SCHEMA)
    rc = ddl.deploy(schema=TEST_SCHEMA) if hasattr(ddl, "deploy") else None
    if rc is None:
        code = ddl.main(["--schema", TEST_SCHEMA])
        assert code == 0, f"临时 schema 部署失败 rc={code}"
    yield TEST_SCHEMA
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % TEST_SCHEMA)
