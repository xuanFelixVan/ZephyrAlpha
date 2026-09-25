# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_scheduling_ddl
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_scheduling_ddl — C2 验收：schema 名白名单/DDL 渲染（七态 CHECK/TIMESTAMPTZ/审计守卫）/
verify 与 deploy（fake conn 注入，零 PG 依赖）；与 policy order_states 同表驱动护栏。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Final

import pytest

REPO: Final = Path(__file__).resolve().parents[3]
DDL_PATH = REPO / "scripts" / "ai_layer" / "apply_ai_layer_scheduling_ddl.py"


def _load_ddl() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ai_scheduling_ddl_under_test", DDL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ddl() -> ModuleType:
    return _load_ddl()


# ---------------------------------------------------------------------------
# schema 名白名单（fail-closed）
# ---------------------------------------------------------------------------

def test_schema_name_whitelist(ddl: ModuleType) -> None:
    assert ddl.check_schema_name("ai_scheduling") == "ai_scheduling"
    assert ddl.check_schema_name("ai_scheduling_test_x1") == "ai_scheduling_test_x1"
    for bad in ("ai_intake", "ai_compare", "public", "ai_scheduling; DROP TABLE x", ""):
        with pytest.raises(ValueError, match="schema 名不合规"):
            ddl.check_schema_name(bad)


def test_drop_refuses_non_test_schema(ddl: ModuleType) -> None:
    with pytest.raises(ValueError, match="拒删非测试 schema"):
        ddl.drop_test_schema("ai_scheduling")


# ---------------------------------------------------------------------------
# DDL 渲染（幂等标志/七态 CHECK/审计守卫）
# ---------------------------------------------------------------------------

def test_ddl_statements_content(ddl: ModuleType, policy: dict[str, Any]) -> None:
    stmts = ddl._ddl_statements("ai_scheduling")
    joined = "\n".join(stmts)
    assert stmts[0] == "CREATE SCHEMA IF NOT EXISTS ai_scheduling"
    assert joined.count("IF NOT EXISTS") >= 4  # 幂等标志（schema+表+3 索引）
    assert "ai_scheduling.ai_work_order" in joined
    assert "TIMESTAMPTZ" in joined  # RULE-SCHEMA-TZ
    for st in ddl.ORDER_STATES:  # 七态 CHECK 全在册
        assert f"'{st}'" in joined
    assert "append-only violation" in joined  # 审计守卫触发器在册
    assert "TRIGGER trg_ai_work_order_audit" in joined
    # 同表驱动护栏：policy 与 DDL 状态枚举一致（改一处必改两处）
    assert tuple(policy["order_states"]) == ddl.ORDER_STATES


def test_state_machine_seven_states(ddl: ModuleType) -> None:
    """§2.7 红蓝 R1-B10：七态齐（含 deferred 补态）。"""
    assert ddl.ORDER_STATES == (
        "pending", "held_maturity", "held_incomplete",
        "dispatched", "deferred", "done", "dead",
    )


def test_grant_statements(ddl: ModuleType) -> None:
    grants = ddl._grant_statements("ai_scheduling")
    joined = "\n".join(grants)
    assert "GRANT USAGE ON SCHEMA ai_scheduling TO depgraph_reader" in joined
    assert "GRANT SELECT ON ai_scheduling.ai_work_order TO depgraph_reader" in joined
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in joined


# ---------------------------------------------------------------------------
# deploy / verify（fake conn 注入，零 PG 依赖）
# ---------------------------------------------------------------------------

class FakeCursor:
    """按查询标记（information_schema/pg_constraint/pg_trigger）回放预制行集。"""

    def __init__(self, rows_by_marker: dict[str, list[tuple[Any, ...]]]) -> None:
        self._rows = rows_by_marker
        self.last_sql = ""

    def execute(self, sql: str, _params: Any = None) -> None:
        self.last_sql = sql

    def fetchall(self) -> list[tuple[Any, ...]]:
        for marker, rows in self._rows.items():
            if marker in self.last_sql:
                return rows
        return []


class FakeConn:
    def __init__(self, rows_by_marker: dict[str, list[tuple[Any, ...]]]) -> None:
        self._cur = FakeCursor(rows_by_marker)
        self.committed = False
        self.rolled_back = False

    def cursor(self) -> FakeCursor:
        return self._cur

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        pass


def _all_states_check(ddl: ModuleType) -> list[tuple[Any, ...]]:
    check = "CHECK (state IN (" + ", ".join(f"'{s}'" for s in ddl.ORDER_STATES) + "))"
    return [(check,)]


def test_verify_ok_with_full_schema(ddl: ModuleType) -> None:
    conn = FakeConn({
        "information_schema": [("ai_work_order", "BASE TABLE")],
        "pg_constraint": _all_states_check(ddl),
        "pg_trigger": [("trg_ai_work_order_audit",)],
    })
    ok, missing = ddl.verify("ai_scheduling", conn=conn)
    assert ok and missing == []


def test_verify_lists_missing(ddl: ModuleType) -> None:
    conn = FakeConn({})  # 全查询空回放=库内缺件
    ok, missing = ddl.verify("ai_scheduling", conn=conn)
    assert not ok
    assert "table:ai_work_order" in missing
    assert any(m.startswith("check_state:pending") for m in missing)
    assert "trigger:trg_ai_work_order_audit" in missing


def test_deploy_runs_ddl_and_grants(ddl: ModuleType) -> None:
    conn = FakeConn({})
    counts = ddl.deploy("ai_scheduling", conn=conn)
    assert counts["ddl"] == len(ddl._ddl_statements("ai_scheduling"))
    assert counts["grant"] == len(ddl._grant_statements("ai_scheduling"))
    assert conn.committed and not conn.rolled_back
