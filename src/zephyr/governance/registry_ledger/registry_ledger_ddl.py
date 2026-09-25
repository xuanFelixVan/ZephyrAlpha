# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [MODULE] zephyr.governance.registry_ledger.registry_ledger_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] schemas.categories.registry_ledger.registry_* 四表 DDL 常量
# [CONSUMERS] deploy.py; scripts/governance/registry_migration/wave0_phase0_gate.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DDL 聚合唯一入口按依赖序（catalog 先于 entry）；_schema_version 台账 ON CONFLICT DO NOTHING 可重跑
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildA-20260923；2026-09-25 wave0 改名 ledger_schema（N-16 basename 唯一）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；模板 format 缺键 raise（编程错误）
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_ledger DDL 聚合与 _schema_version 台账（真源=schemas/categories/registry_ledger/）。
# [ALGO_FLOW]

_schema_version 惯例与 depgraph_schema 同款：INTEGER PRIMARY KEY + applied_at +
description，INSERT ON CONFLICT (version) DO NOTHING，可重跑。
"""

from schemas.categories.registry_ledger.registry_catalog import REGISTRY_CATALOG_DDL
from schemas.categories.registry_ledger.registry_entry import (
    REGISTRY_ENTRY_DDL,
    REGISTRY_ENTRY_STATUS_INDEX_DDL,
)
from schemas.categories.registry_ledger.registry_event import (
    REGISTRY_EVENT_DDL,
    REGISTRY_EVENT_ENTRY_INDEX_DDL,
)
from schemas.categories.registry_ledger.registry_snapshot import REGISTRY_SNAPSHOT_DDL

SCHEMA_NAME = "registry_ledger"

SCHEMA_VERSION = 1
SCHEMA_VERSION_DESCRIPTION = (
    "W-M1 wave0 lane A: registry_catalog/registry_entry/registry_event/registry_snapshot "
    "+ append-only triggers (docs/_working/registry_migration/02_ledger_design.md §2)"
)

SCHEMA_VERSION_DDL = """
CREATE TABLE IF NOT EXISTS {schema}._schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    description TEXT
)
"""

APPEND_ONLY_GUARD_FUNCTION_DDL = """
CREATE OR REPLACE FUNCTION {schema}.fn_forbid_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'registry_ledger: % on % is forbidden (append-only ledger, 02_ledger_design.md I2/I3)', TG_OP, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql
"""

APPEND_ONLY_TRIGGER_DDL = """
DROP TRIGGER IF EXISTS trg_{table}_no_mutation ON {schema}.{table};
CREATE TRIGGER trg_{table}_no_mutation
BEFORE UPDATE OR DELETE ON {schema}.{table}
FOR EACH ROW EXECUTE FUNCTION {schema}.fn_forbid_mutation()
"""

REVOKE_MUTATION_DDL = """
REVOKE UPDATE, DELETE ON {schema}.{table} FROM PUBLIC
"""

GRANT_READER_DDL = """
GRANT USAGE ON SCHEMA {schema} TO {role};
GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {role}
"""

GRANT_WRITER_DDL = """
GRANT USAGE ON SCHEMA {schema} TO {role};
GRANT SELECT, INSERT ON {schema}.registry_event TO {role};
GRANT SELECT, INSERT, UPDATE ON {schema}.registry_entry TO {role};
GRANT SELECT, INSERT, UPDATE ON {schema}.registry_catalog TO {role};
GRANT SELECT, INSERT ON {schema}.registry_snapshot TO {role};
GRANT USAGE ON SEQUENCE {schema}.registry_entry_entry_pk_seq TO {role};
GRANT USAGE ON SEQUENCE {schema}.registry_event_event_id_seq TO {role};
GRANT USAGE ON SEQUENCE {schema}.registry_snapshot_snapshot_pk_seq TO {role}
"""


def table_ddls(schema: str = SCHEMA_NAME) -> list[str]:
    """按依赖序返回全部表/索引 DDL（catalog 先于 entry，FK 依赖）。"""
    return [
        REGISTRY_CATALOG_DDL.format(schema=schema),
        REGISTRY_ENTRY_DDL.format(schema=schema),
        REGISTRY_ENTRY_STATUS_INDEX_DDL.format(schema=schema),
        REGISTRY_EVENT_DDL.format(schema=schema),
        REGISTRY_EVENT_ENTRY_INDEX_DDL.format(schema=schema),
        REGISTRY_SNAPSHOT_DDL.format(schema=schema),
    ]
