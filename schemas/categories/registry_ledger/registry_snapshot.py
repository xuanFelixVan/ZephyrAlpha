# [BLUEPRINT] MOD-L04-001 | schemas/categories/registry_snapshot.py | §
# [MODULE] schemas.categories.registry_ledger.registry_snapshot
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] none
# [CONSUMERS] src/zephyr/governance/registry_ledger/schema.py（DDL 聚合）; registry_projection/pg_source.py（投影只读消费端）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] registry_snapshot 表 DDL 唯一真源（PG）；发布=不可变全量+每册单调版本（触发器 RAISE+REVOKE 双保险）
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；解析失败=部署器 fail-closed 拒跑
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_snapshot 表 DDL-as-Code（发布=不可变全量+每册单调版本）。

设计真源：docs/_working/registry_migration/02_ledger_design.md §2.4（D-1/D-4 已批：
快照保留 14 天+月档）。manifest={entry_key: payload_sha256} 点查免解包；bundle 全条目
payload 打包（TOAST 自动外置）；git_commit_ref 发布时已知不回填。机械不可变与
registry_event 同款双保险（deploy.py）。
"""

REGISTRY_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS {schema}.registry_snapshot (
  snapshot_pk     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  registry_id     text NOT NULL,
  snapshot_version integer NOT NULL,
  parent_snapshot_version integer,
  manifest        jsonb NOT NULL,
  bundle          jsonb NOT NULL,
  content_sha256  char(64) NOT NULL,
  entry_count     integer NOT NULL,
  git_commit_ref  char(40),
  published_by    text NOT NULL,
  published_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_registry_snapshot UNIQUE (registry_id, snapshot_version)
)
"""

TABLE_NAME = "registry_snapshot"
SCHEMA_NAME = "registry_ledger"
