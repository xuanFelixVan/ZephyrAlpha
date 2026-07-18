---
module_id: MOD-INF-012B
title: SQLite → PostgreSQL 数据迁移工具集
version: "1.0.0"
layer: cross_layer
depends_on: [MOD-INF-002]
tags: [migration, sqlite, postgresql, depgraph, disaster-recovery]
ttl: task_bound
doc_type: index
---

# SQLite → PostgreSQL 数据迁移工具集

depgraph 从 SQLite（`data/databases/depgraph.db`）迁移到 PostgreSQL（localhost:5432/depgraph）
的一次性运维工具集。真源分类遵循 trae_062：规则数据（YAML 真源）走 `seed_from_yaml.py`，
架构/运营数据（DB 真源）走 `migrate_data.py`。

## 文件清单

| 文件 | 职责 |
|------|------|
| `00_sqlite_actual_schema.sql` | SQLite 实际 schema 快照（翻译基准，只读参考） |
| `01_create_extensions.sql` | PG 扩展初始化（pg_stat_statements / pgcrypto） |
| `02_create_pg_schema.sql` | PG Schema DDL（30 表 / 42 索引 / 2 视图 / 36 触发器 / 3 函数） |
| `02_create_pg_schema_down.sql` | 02 的降级脚本（反依赖顺序 DROP 全部对象，幂等） |
| `seed_from_yaml.py` | 从 YAML 真源灌种子表（委托 `sync_yaml_to_depgraph.sync_all()`） |
| `migrate_data.py` | 运营数据迁移（每表独立事务 + migration_log 幂等） |

## 执行顺序（严格按序）

```bash
# 0. 前置条件检查（见下节），然后：
psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql
psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql

# 1. 先灌种子表（nodes.domain_id 等 FK 引用 domains，种子必须先就位）
PYTHONPATH=src python scripts/governance/migrate_sqlite_to_pg/seed_from_yaml.py

# 2. 再迁移运营数据（nodes/edges/governance_audit_logs 等 9 表）
PYTHONPATH=src python scripts/governance/migrate_sqlite_to_pg/migrate_data.py
```

## 前置条件

1. PostgreSQL 16 已启动（Windows 服务运行中），`config/.env.postgres` 存在且凭据有效。
2. `data/databases/depgraph.db` 已备份（破坏性操作三步验证：必要性/真实性/可逆性，
   规则真源 `trae_063_data_ops_discipline.yaml`）。
3. PG 目标库 `depgraph` 已创建（`CREATE DATABASE depgraph;`）。
4. 连接使用 `postgres` 超级用户——`SET session_replication_role` 需要超级用户权限。

## 幂等与重跑

- `migrate_data.py` 首次成功后在 `migration_log` 表写入 `status='completed'` 记录；
  重跑时检测到已完成则跳过并提示。强制重跑用 `--force`。
- 每表独立事务（DELETE+INSERT+VERIFY+COMMIT）：单表失败仅回滚该表，已提交表数据
  不受损；修复后重跑只需 `migrate_data.py`（partial 状态不阻断重跑）。
- 部分失败时 `migration_log` 记录 `status='partial'`，不会误判为已完成。

## 回滚步骤

1. **迁移中途失败**：进程退出后 PG 触发器已在 finally 中恢复；直接修复问题重跑即可
   （每表事务保证无半成品状态）。SQLite 源库全程只读，不受迁移影响。
2. **迁移完成后回滚到 SQLite**：depgraph 连接切回 SQLite 入口（`db_utils.get_db_connection`），
   PG 侧如需清场执行：
   ```bash
   psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema_down.sql
   ```
   该脚本按反依赖顺序 DROP 02 创建的全部对象（视图→表→函数，索引/触发器随表自动 DROP），
   可重复执行。
3. **种子表回滚**：种子表是 YAML 真源的只读缓存，清场后由 `seed_from_yaml.py` 可随时重建。

## 相关文档

- 迁移背景与组件裁定：`docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md`
- 真源分类铁律（规则数据 YAML / 架构数据 DB）：`docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml`
- 数据操作纪律（破坏性操作三步验证）：`docs/01_policies_and_standards/rules/trae_063_data_ops_discipline.yaml`
- 种子同步能力真源：`scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py`
