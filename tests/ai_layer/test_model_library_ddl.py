# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_library
# [MODULE] tests.ai_layer.test_model_library_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/ai_layer/apply_model_library_ddl.py（importlib 直载）; zephyr.governance.depgraph_schema（PG 可达性自探测）
# [CONSUMERS] pytest tests/ai_layer/test_model_library_ddl.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] schema 名白名单纯校验零 PG 全枚举（合规/打偏双路）；DDL 幂等标志逐句断言（IF NOT EXISTS）；
#              PG 用例只写 ai_layer_model_test_ 前缀临时 schema，用后必 DROP（finally 兜底）；
#              生产 schema ai_layer_model 只 --verify 只读核对，测试永不部署/永不删；
#              PG 不可达=skip 而非假绿（可达性探测任何异常都判不可达）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §3.2
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；schema 名不合规→ValueError 落用例；drop 非测试前缀→ValueError 落用例
# [TESTS] tests/ai_layer/test_model_library_ddl.py
# [TTL] permanent
"""test_model_library_ddl — C3 验收：schema 白名单 fail-closed + DDL 幂等 + 临时 schema 部署/verify/DROP 闭环。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Final

import pytest

REPO: Final = Path(__file__).resolve().parents[2]
DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_model_library_ddl.py"
TEST_SCHEMA = "ai_layer_model_test_p1c3"


def _load_ddl() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ai_layer_model_ddl_under_test", DDL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        try:
            conn.cursor().execute("SELECT 1")
            return True
        finally:
            conn.close()
    except Exception:  # noqa: BLE001——可达性探测，任何异常都判不可达（skip 而非假绿）
        return False


PG_MARK = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@pytest.fixture(scope="module")
def ddl() -> ModuleType:
    return _load_ddl()


def test_schema_whitelist_accepts(ddl: ModuleType) -> None:
    """合规名原样放行：生产名+测试前缀名。"""
    assert ddl.check_schema_name("ai_layer_model") == "ai_layer_model"
    assert ddl.check_schema_name("ai_layer_model_test_p1c3") == "ai_layer_model_test_p1c3"


def test_schema_whitelist_rejects(ddl: ModuleType) -> None:
    """打偏名一律 ValueError（fail-closed，绝不静默改名）：邻居 schema/前缀仿冒/大写/注入串。"""
    for bad in (
        "ai_intake",
        "model_library",
        "ai_layer_models",
        "ai_layer_model_test_",
        "AI_LAYER_MODEL",
        "ai_layer_model; DROP SCHEMA x",
        "ai_layer_model_test_P1",
        "",
    ):
        with pytest.raises(ValueError, match="schema 名不合规"):
            ddl.check_schema_name(bad)


def test_ddl_statements_idempotent(ddl: ModuleType) -> None:
    """全部语句 IF NOT EXISTS 幂等；三表两索引齐备。"""
    stmts = ddl._ddl_statements("ai_layer_model")  # noqa: SLF001——白盒幂等断言
    assert len(stmts) == 6  # schema + 3 tables + 2 indexes
    assert all("IF NOT EXISTS" in s for s in stmts)
    joined = "\n".join(stmts)
    for table in ("model_registry", "model_price_history", "model_promo_history"):
        assert f"CREATE TABLE IF NOT EXISTS ai_layer_model.{table}" in joined
    assert "TIMESTAMPTZ" in joined  # RULE-SCHEMA-TZ
    assert "DATETIME" not in joined.upper().replace("TIMESTAMPTZ", "")


def test_grant_role_tiers(ddl: ModuleType) -> None:
    """角色分级：reader 只 SELECT，writer 全权；两序列授 writer。"""
    grants = ddl._grant_statements("ai_layer_model")  # noqa: SLF001
    reader = [g for g in grants if "depgraph_reader" in g and "GRANT SELECT ON" in g]
    writer = [g for g in grants if "GRANT SELECT, INSERT, UPDATE, DELETE ON" in g]
    assert len(reader) == 3
    assert len(writer) == 3
    assert sum("model_price_history_id_seq" in g for g in grants) == 1
    assert sum("model_promo_history_id_seq" in g for g in grants) == 1


def test_drop_refuses_non_test_schema(ddl: ModuleType) -> None:
    """生产 schema 永不删：非 ai_layer_model_test_ 前缀一律 ValueError（不触 PG）。"""
    with pytest.raises(ValueError, match="拒删非测试 schema"):
        ddl.drop_test_schema("ai_layer_model")


@PG_MARK
def test_deploy_verify_drop_roundtrip(ddl: ModuleType) -> None:
    """临时 schema 真 DDL 部署→verify OK→CLI verify rc=0→DROP 清场（finally 兜底）。"""
    try:
        counts = ddl.deploy(TEST_SCHEMA)
        assert counts["ddl"] == 6
        ok, missing = ddl.verify(TEST_SCHEMA)
        assert ok, f"临时 schema 缺件：{missing}"
        assert ddl.main(["--verify", "--schema", TEST_SCHEMA]) == 0
    finally:
        ddl.drop_test_schema(TEST_SCHEMA)
    ok_after, _missing = ddl.verify(TEST_SCHEMA)
    assert not ok_after  # 清场后核对应报缺件而非假绿
