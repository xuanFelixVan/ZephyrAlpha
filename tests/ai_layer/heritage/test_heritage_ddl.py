# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest (heritage_ddl/heritage_schema 夹具)
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_ddl.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL 语句面纯断言（四表五视图/TIMESTAMPTZ 全覆盖/CHECK 值域与 DESIGN §2.3 一致）;
#              schema 白名单 fail-closed；DB 用例在临时 schema 复跑 deploy 验幂等
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError 拒非法 schema 名；断言失败即红
# [TESTS] tests/ai_layer/heritage/test_heritage_ddl.py
# [TTL] permanent
"""test_heritage_ddl - DDL 登记器验收（DESIGN 施工项 1）。"""

from __future__ import annotations

import pytest

REQUIRED_TABLES = ("ai_heritage_entry", "ai_heritage_elite", "ai_heritage_criteria", "ai_heritage_defect")
REQUIRED_VIEWS = (
    "ai_heritage_elites_active",
    "ai_heritage_defect_hot",
    "ai_heritage_l1_prior",
    "ai_heritage_l1_exclusion",
    "ai_heritage_kpi",
)


def test_schema_name_whitelist(heritage_ddl) -> None:
    assert heritage_ddl.check_schema_name("ai_heritage") == "ai_heritage"
    assert heritage_ddl.check_schema_name("ai_heritage_test_x1") == "ai_heritage_test_x1"
    with pytest.raises(ValueError, match="schema 名不合规"):
        heritage_ddl.check_schema_name("pg_catalog")
    with pytest.raises(ValueError, match="schema 名不合规"):
        heritage_ddl.check_schema_name("ai_intake")
    with pytest.raises(ValueError, match="拒删非测试 schema"):
        heritage_ddl.drop_test_schema("ai_heritage")


def test_ddl_statements_shape(heritage_ddl) -> None:
    stmts = heritage_ddl._ddl_statements("ai_heritage")
    joined = "\n".join(stmts)
    assert "CREATE SCHEMA IF NOT EXISTS ai_heritage" in joined
    for table in REQUIRED_TABLES:
        assert f"CREATE TABLE IF NOT EXISTS ai_heritage.{table}" in joined, table
    for view in REQUIRED_VIEWS:
        assert f"CREATE OR REPLACE VIEW ai_heritage.{view}" in joined, view
    # TIMESTAMPTZ 全覆盖（RULE-SCHEMA-TZ）：H1 三处（last_hit_at/created_at/updated_at）+H4 两处
    # （first_seen/last_seen）；H2/H3 按 DESIGN §2.3 字段表本无时间列
    assert joined.count("TIMESTAMPTZ") == 5
    assert "entry_kind IN ('elite', 'criteria', 'defect')" in joined
    assert "status IN ('active', 'archived', 'retired', 'compressed')" in joined
    assert "source_kind IN ('l6_switch', 'l4_experiment', 'work_order', 'redblue', 'casebook', " in joined
    assert "venue IN ('c4', 'replay', 'dual_run', 'tool_bench', 'other')" in joined
    assert "surface IN ('code_module', 'gate_param', 'model', 'tool', 'rule')" in joined
    assert "^HT-[0-9]{8}-[0-9]{3}$" in joined, "entry_id 形态机检（CHECK regex）"
    assert "length(btrim(plain_zh)) >= 10" in joined
    assert "length(btrim(diff_summary)) >= 30" in joined and "length(btrim(why_win)) >= 30" in joined
    import re as _re

    assert _re.search(r"pattern_norm\s+TEXT NOT NULL UNIQUE", joined), "pattern_norm 受控词表唯一"
    assert "DELETE" not in joined, "DDL 零物理删除语义"


def test_ddl_idempotent_deploy_twice(heritage_ddl, heritage_schema: str) -> None:
    """幂等执行两次零错（验收标准原文；conftest 已部署第 1 次，此处第 2 次）。"""
    counts = heritage_ddl.deploy(schema=heritage_schema)
    assert counts["ddl"] > 0
    ok, missing = heritage_ddl.verify(heritage_schema)
    assert ok and missing == []
