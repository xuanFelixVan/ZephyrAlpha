# [BLUEPRINT] MOD-L04-001 | schemas/categories/registry_ledger/__init__.py | §
# [MODULE] schemas.categories.registry_ledger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] schemas.categories.registry_ledger.registry_* 四表 DDL 常量
# [CONSUMERS] src/zephyr/governance/registry_ledger/schema.py（聚合入口）; deploy.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DDL-as-Code 真源子目录地图条目；单簇超 20 件拆子目录（本簇 4 表封顶型）
# [ERROR_CONTRACT] DDL 常量纯声明无运行时错误面；解析失败=部署器 fail-closed 拒跑
# [TESTS] tests/governance/test_registry_ledger.py（部署幂等/指纹稳定）
# [TTL] permanent
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""注册表 PG 行级账本 DDL 真源子目录（W-M1 车道A·波0）。

范围：registry_catalog / registry_entry / registry_event / registry_snapshot 四表，
PostgreSQL schema `registry_ledger`（实例=depgraph 同库，meta_question 先例）。
设计真源：docs/_working/registry_migration/02_ledger_design.md §2（已批 D1-D6/A1-A3）。
新表落位：registry_* 一律入本目录；DDL 变更需同步 _schema_version 并过幂等部署零漂移。
"""
