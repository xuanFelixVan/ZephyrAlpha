# [BLUEPRINT] MOD-L04-001 | schemas/categories/registry_catalog.py | §
# [MODULE] schemas.categories.registry_ledger.registry_catalog
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] none
# [CONSUMERS] src/zephyr/governance/registry_ledger/schema.py（DDL 聚合）; deploy.py（部署器）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] registry_catalog 表 DDL 唯一真源（PG）；幂等 CREATE TABLE IF NOT EXISTS 可重跑；种子=Phase 0 机械扫描零人工填写
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；解析失败=部署器 fail-closed 拒跑
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_catalog 表 DDL-as-Code（册级登记表，小表，ROOR∪文件头机械扫描种子）。

设计真源：docs/_working/registry_migration/02_ledger_design.md §2.1（D-1/A-1 已批）。
种子=Phase 0 机械扫描，零人工填写；family_key 与 _split_registry_entries 族定义同一真源，
一册多族时主族入 family_key、次族入 extra_families。
"""

REGISTRY_CATALOG_DDL = """
CREATE TABLE IF NOT EXISTS {schema}.registry_catalog (
  registry_id        text PRIMARY KEY,
  physical_path      text NOT NULL UNIQUE,
  family_key         text,
  extra_families     jsonb,
  identity_mode      text NOT NULL,
  unique_key_fields  jsonb,
  maintenance        text NOT NULL,
  entry_schema       jsonb,
  status             text NOT NULL DEFAULT 'active',
  ledger_version     integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
)
"""

TABLE_NAME = "registry_catalog"
SCHEMA_NAME = "registry_ledger"
