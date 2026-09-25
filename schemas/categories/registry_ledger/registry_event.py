# [BLUEPRINT] MOD-L04-001 | schemas/categories/registry_event.py | §
# [MODULE] schemas.categories.registry_ledger.registry_event
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] none
# [CONSUMERS] src/zephyr/governance/registry_ledger/schema.py（DDL 聚合）; api.py（意图 API 事件写入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] registry_event 表 DDL 唯一真源（PG）；只增不改（触发器 RAISE+REVOKE 双保险）；before 走 before_sha256 指纹链式引用
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；解析失败=部署器 fail-closed 拒跑
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_event 表 DDL-as-Code（事件表，只增不改，who/when/what/how 四元组）。

设计真源：docs/_working/registry_migration/02_ledger_design.md §2.3（D-1/D-6 已批）。
不变式：I2 每条状态变化有且仅有一行事件；并发败者的 409 拒绝本身也记一行
（detail.conflict=true）。机械不可变=REVOKE UPDATE/DELETE FROM PUBLIC + BEFORE
UPDATE OR DELETE 触发器 RAISE EXCEPTION 双保险（部署器落，见 deploy.py）。
before 走 before_sha256 指纹链式引用，不存双份全文。
"""

REGISTRY_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS {schema}.registry_event (
  event_id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  registry_id   text NOT NULL,
  family_key    text NOT NULL,
  entry_key     text NOT NULL,
  action        text NOT NULL,
  actor_session text NOT NULL,
  actor_kind    text NOT NULL,
  base_version  integer,
  after_version integer NOT NULL,
  payload_after jsonb NOT NULL,
  before_sha256 char(64),
  reason        text,
  authority_ref text,
  detail        jsonb,
  created_at    timestamptz NOT NULL DEFAULT now()
)
"""

REGISTRY_EVENT_ENTRY_INDEX_DDL = """
CREATE INDEX IF NOT EXISTS idx_registry_event_entry
  ON {schema}.registry_event(registry_id, family_key, entry_key, event_id)
"""

TABLE_NAME = "registry_event"
SCHEMA_NAME = "registry_ledger"
