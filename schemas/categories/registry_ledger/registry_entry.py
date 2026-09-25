# [BLUEPRINT] MOD-L04-001 | schemas/categories/registry_entry.py | §
# [MODULE] schemas.categories.registry_ledger.registry_entry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] none
# [CONSUMERS] src/zephyr/governance/registry_ledger/schema.py（DDL 聚合）; api.py（意图 API）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] registry_entry 表 DDL 唯一真源（PG）；UNIQUE(registry_id,family_key,entry_key) 六道保障；version CAS 基线；tombstone 永不物理删
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；解析失败=部署器 fail-closed 拒跑
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_entry 表 DDL-as-Code（条目状态表，last-writer-wins 唯一层，version CAS 基线）。

设计真源：docs/_working/registry_migration/02_ledger_design.md §2.2（D-1/A-1 已批）。
不变式：I1 并发写冲突必显式 409；I4 retire=tombstone 永不物理删（UNIQUE 不放开，
同键复活=新事件 reopen 走版本推进）。
"""

REGISTRY_ENTRY_DDL = """
CREATE TABLE IF NOT EXISTS {schema}.registry_entry (
  entry_pk        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  registry_id     text NOT NULL REFERENCES {schema}.registry_catalog(registry_id),
  family_key      text NOT NULL,
  entry_key       text NOT NULL,
  payload         jsonb NOT NULL,
  payload_sha256  char(64) NOT NULL,
  version         integer NOT NULL DEFAULT 1,
  status          text NOT NULL DEFAULT 'active',
  held_by_session text,
  held_at         timestamptz,
  lease_expires_at timestamptz,
  created_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_by text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  last_event_id  bigint,
  CONSTRAINT uq_registry_entry UNIQUE (registry_id, family_key, entry_key)
)
"""

REGISTRY_ENTRY_STATUS_INDEX_DDL = """
CREATE INDEX IF NOT EXISTS idx_registry_entry_status
  ON {schema}.registry_entry(registry_id, status)
"""

TABLE_NAME = "registry_entry"
SCHEMA_NAME = "registry_ledger"
