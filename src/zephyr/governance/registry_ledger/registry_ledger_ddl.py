# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [MODULE] zephyr.governance.registry_ledger.registry_ledger_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] schemas.categories.registry_ledger.registry_* 四表 DDL 常量
# [CONSUMERS] deploy.py; scripts/governance/registry_migration/wave0_phase0_gate.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DDL 聚合唯一入口按依赖序（catalog 先于 entry）；_schema_version 台账 ON CONFLICT DO NOTHING 可重跑
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildA-20260923；2026-09-25 wave0 改名 ledger_schema（N-16 basename 唯一）；2026-10-13 st-maint5-20261013 起点自装仓根 sys.path（尾位，防 site-packages 命名空间包 schemas 遮蔽）
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

import os
import sys

# ── schemas 真源导入（仓根路径引导：src/zephyr/governance/registry_ledger/本文件 → 上溯四级=仓根）──
# pip 包 safety_schemas 在 site-packages 落的命名空间包 schemas 无 __init__.py：
# `import schemas` 假成功（__file__=None）而炸点在子模块 schemas.categories。`python <脚本路径>`
# 形态 sys.path[0]=脚本目录、仓根恒不在场 ⇒ 登记正门写腿（bct→api→本文件）必断。
# 放尾位而非头位（先例 #ARCH-104 用头位，那是 worker 入口件非被广泛 import 的库件）：
# 本件被队列/治理链在任意进程导入，头位会改写全进程包优先级。
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_REPO_SCHEMAS = os.path.join(_REPO_ROOT, "schemas")
if os.path.isdir(_REPO_SCHEMAS):
    if _REPO_ROOT not in sys.path:
        sys.path.append(_REPO_ROOT)
    # 同进程若已把那份命名空间 schemas 载入 sys.modules，其 __path__ 在装配前就算死了，
    # 只补 sys.path 不解蔽——把仓根真身直接接进它的搜索面。
    _cached_schemas = sys.modules.get("schemas")
    if _cached_schemas is not None and getattr(_cached_schemas, "__file__", None) is None:
        _search_path = getattr(_cached_schemas, "__path__", None)
        if _search_path is not None and _REPO_SCHEMAS not in list(_search_path):
            _search_path.append(_REPO_SCHEMAS)

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
