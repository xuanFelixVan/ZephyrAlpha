---
module_id: MOD-DB_DEPGRAPH_PG_OPT
submodule_path: src/zephyr/infrastructure/db
title: "P3 PostgreSQL优化任务卡总览 — 4个任务卡 + 4个元任务卡"
doc_type: index
status: Draft
version: "1.0.0"
layer: cross_layer
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260625-P3
date: "2026-06-25"
valid_from: "2026-06-25"
ttl: permanent
rule_form: structural
belongs_to: "MOD-DB_DEPGRAPH_PG_OPT"
parent_module: "SH-DB-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: planned
actual_disk_path: ''
codification_level: L2
generation: 3
functional_domain: data
summary: "P3 PostgreSQL优化任务卡总览——4个任务卡（P3-T1 pgvector / P3-T2 LISTEN-NOTIFY / P3-T3 分区表 / P3-T4 监控告警）+ 4个元任务卡。前置条件：P2迁移完成。"
tags: [postgresql, pgvector, listen-notify, partitioning, monitoring, task-cards, p3, database-upgrade]
priority: P2
runtime_plane: hot
depends_on:
  - {target: "MOD-DB_DEPGRAPH_PG", at: "全篇", why: "P2迁移完成是P3优化的前置条件"}
  - {target: "SH-DB-001", at: "全篇", why: "父蓝图——Database集成蓝图"}
references:
  - {id: "MOD-DB_DEPGRAPH_PG_OPT", at: "全篇", why: "P3方案真源——施工方案详细步骤"}
  - {id: "MOD-DB_DEPGRAPH_PG", at: "全篇", why: "P2方案——前置条件与PG连接配置来源"}
---
# P3 PostgreSQL优化任务卡总览

> 施工方案真源：[mod_inf_012b_p3_postgresql_optimization.md](mod_inf_012b_p3_postgresql_optimization.md)
> 前置条件：P2迁移完成（PostgreSQL运行中，红蓝测试通过）

## 任务卡清单

| # | 任务卡ID | 名称 | 对应文档章节 | 元任务卡ID |
|---|---------|------|------------|-----------|
| 1 | P3-T1 | pgvector扩展（代码embedding语义检索） | §四 | P3-MT1 |
| 2 | P3-T2 | LISTEN/NOTIFY（AI间事件通知） | §五 | P3-MT2 |
| 3 | P3-T3 | 按domain_id分区表（大表优化） | §六 | P3-MT3 |
| 4 | P3-T4 | 监控告警（pg_stat_activity） | §七 | P3-MT4 |

## 推荐执行顺序

```
P3-T4（监控告警）→ P3-T1（pgvector）→ P3-T2（LISTEN/NOTIFY）→ P3-T3（分区表）
```

**理由**：见P3方案§三.3.1

---

## 任务卡 P3-T1：pgvector扩展（代码embedding语义检索）

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-T1 |
| 标题 | pgvector扩展 — 代码embedding语义检索 |
| 优先级 | P2 |
| 安全级别 | M |
| 执行模型 | GLM-5.2 |
| 依赖 | P2完成 |
| 对应文档 | P3方案§四 |
| 预计Token | 10000 |
| 超时 | 90分钟 |

### 施工范围

**可修改文件白名单**：
- `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql`（修改，取消vector注释）
- `src/zephyr/shared/utils/code_embedding.py`（新建）
- `scripts/governance/update_embeddings.py`（新建）
- `requirements.txt`（修改）

**禁止修改文件**：
- `src/zephyr/governance/depgraph_schema.py`（分区表在P3-T3处理）
- `scripts/governance/apply_depgraph.py`

### 施工步骤

#### 步骤1：安装pgvector扩展

```powershell
psql -U zephyr -d depgraph -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U zephyr -d depgraph -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

#### 步骤2：更新PostgreSQL初始化脚本

**文件路径**：`scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql`

**注意**：此文件在P2阶段1[动作3]中创建，此处为修改（取消pgvector的注释）。

**操作**：见P3方案§四.4.3[动作2]

#### 步骤3：在nodes表添加embedding列

```powershell
psql -U zephyr -d depgraph -c "
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding vector(384);
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT '';
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP;
"
```

#### 步骤4：创建HNSW索引

```powershell
psql -U zephyr -d depgraph -c "
CREATE INDEX IF NOT EXISTS idx_nodes_embedding
ON nodes USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
"
```

#### 步骤5：创建Python embedding工具

**操作**：创建 `src/zephyr/shared/utils/code_embedding.py`

**文件内容**：见P3方案§四.4.3[动作5]

**关键**：复用P2中定义的PG连接配置（`from zephyr.shared.utils.pg_connection import PG_CONFIG`）

#### 步骤6：安装Python依赖

```powershell
pip install sentence-transformers
```

#### 步骤7：更新requirements.txt

追加：`sentence-transformers>=2.7.0`

#### 步骤8：创建embedding批量更新脚本

**操作**：创建 `scripts/governance/update_embeddings.py`

**文件内容**：见P3方案§四.4.3[动作8]

#### 步骤9：执行embedding批量更新

```powershell
# 先更新一个小域测试
python scripts\governance\update_embeddings.py --domain D-GOVERNANCE

# 验证embedding已生成
psql -U zephyr -d depgraph -c "
SELECT COUNT(*) as total, COUNT(embedding) as has_embedding
FROM nodes WHERE domain_id = 'D-GOVERNANCE';
"

# 测试语义搜索
python -c "
import sys; sys.path.insert(0, 'src')
from zephyr.shared.utils.code_embedding import semantic_search
results = semantic_search('任务管理', top_k=5)
for r in results:
    print(f'{r[\"similarity\"]:.3f} | {r[\"node_id\"]} | {r[\"name\"]} | {r[\"domain_id\"]}')
"
```

### 验收标准

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | pgvector扩展安装 | `SELECT extname FROM pg_extension WHERE extname='vector'` | vector |
| 2 | embedding列存在 | `\d nodes` | 显示embedding列 |
| 3 | HNSW索引存在 | `SELECT indexname FROM pg_indexes WHERE indexname='idx_nodes_embedding'` | idx_nodes_embedding |
| 4 | embedding已生成 | `SELECT COUNT(embedding) FROM nodes WHERE domain_id='D-GOVERNANCE'` | >0 |
| 5 | 语义搜索可用 | `semantic_search('任务管理')` | 返回相关模块 |
| 6 | 搜索延迟 | 语义搜索计时 | < 50ms |

### 回滚方案

```powershell
# 1. 删除embedding列
psql -U zephyr -d depgraph -c "
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding;
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding_model;
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding_updated_at;
"
# 2. 删除HNSW索引
psql -U zephyr -d depgraph -c "DROP INDEX IF EXISTS idx_nodes_embedding;"
# 3. 删除vector扩展
psql -U zephyr -d depgraph -c "DROP EXTENSION IF EXISTS vector;"
# 4. 删除Python文件
Remove-Item src/zephyr/shared/utils/code_embedding.py
Remove-Item scripts/governance/update_embeddings.py
```

---

## 元任务卡 P3-MT1：审查修复P3-T1

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-MT1 |
| 标题 | 循环审查修复P3-T1（pgvector扩展） |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | P3-T1完成 |

### 审查清单

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | vector扩展已安装 | `SELECT extname FROM pg_extension WHERE extname='vector'` | vector |
| 2 | embedding列存在 | `SELECT column_name FROM information_schema.columns WHERE table_name='nodes' AND column_name='embedding'` | embedding |
| 3 | embedding_model列存在 | 同上，column_name='embedding_model' | embedding_model |
| 4 | embedding_updated_at列存在 | 同上，column_name='embedding_updated_at' | embedding_updated_at |
| 5 | HNSW索引存在 | `SELECT indexname FROM pg_indexes WHERE indexname='idx_nodes_embedding'` | idx_nodes_embedding |
| 6 | code_embedding.py存在 | `Test-Path src/zephyr/shared/utils/code_embedding.py` | True |
| 7 | update_embeddings.py存在 | `Test-Path scripts/governance/update_embeddings.py` | True |
| 8 | sentence-transformers已安装 | `pip show sentence-transformers` | 已安装 |
| 9 | requirements.txt已更新 | `grep "sentence-transformers" requirements.txt` | 有结果 |
| 10 | D-GOVERNANCE域有embedding | `SELECT COUNT(embedding) FROM nodes WHERE domain_id='D-GOVERNANCE'` | >0 |
| 11 | 语义搜索返回结果 | `semantic_search('任务管理', top_k=5)` | 返回≥1个结果 |
| 12 | 语义搜索延迟 | 计时 | < 50ms |
| 13 | PostgreSQL初始化脚本已更新 | `grep "vector" scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql` | CREATE EXTENSION IF NOT EXISTS vector |

### 审查流程

1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → COMPLETED

### 修复授权

- `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql`
- `src/zephyr/shared/utils/code_embedding.py`
- `scripts/governance/update_embeddings.py`
- `requirements.txt`
- PostgreSQL数据库（ALTER TABLE / CREATE INDEX / CREATE EXTENSION）

---

## 任务卡 P3-T2：LISTEN/NOTIFY（AI间事件通知）

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-T2 |
| 标题 | LISTEN/NOTIFY — AI间事件通知 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | P2完成 |
| 对应文档 | P3方案§五 |
| 预计Token | 8000 |
| 超时 | 60分钟 |

### 施工范围

**可修改文件白名单**：
- `src/zephyr/shared/utils/pg_notify.py`（新建）
- `src/zephyr/shared/utils/depgraph_events.py`（新建）

**禁止修改文件**：
- `scripts/governance/apply_depgraph.py`
- `src/zephyr/governance/depgraph_schema.py`

### 施工步骤

#### 步骤1：创建触发器函数（自动发送NOTIFY）

**操作**：在PostgreSQL中创建触发器函数和触发器

见P3方案§五.5.3[动作1]

#### 步骤2：创建Python LISTEN/NOTIFY工具

**操作**：创建 `src/zephyr/shared/utils/pg_notify.py`

**文件内容**：见P3方案§五.5.3[动作2]

**关键**：
- 复用P2中定义的PG连接配置（`from zephyr.shared.utils.pg_connection import PG_CONFIG`）
- LISTEN使用直连PostgreSQL端口5432

#### 步骤3：创建事件通知集成工具

**操作**：创建 `src/zephyr/shared/utils/depgraph_events.py`

**文件内容**：见P3方案§五.5.3[动作3]

#### 步骤4：验证LISTEN/NOTIFY功能

见P3方案§五.5.3[动作4]

#### 步骤5：验证触发器自动通知

见P3方案§五.5.3[动作5]

### 验收标准

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 触发器函数存在 | `SELECT proname FROM pg_proc WHERE proname='notify_node_change'` | notify_node_change |
| 2 | 触发器已绑定 | `SELECT tgname FROM pg_trigger WHERE tgname LIKE 'tr_notify_%'` | 3个触发器 |
| 3 | 手动NOTIFY可用 | `SELECT pg_notify('test', '{}')` | 成功 |
| 4 | EventListener可用 | Python测试脚本 | 收到事件 |
| 5 | 触发器自动通知 | 插入节点测试 | 自动收到事件 |
| 6 | 事件延迟 | 计时 | < 100ms |

### 回滚方案

```powershell
# 1. 删除触发器
psql -U zephyr -d depgraph -c "
DROP TRIGGER IF EXISTS tr_notify_node_insert ON nodes;
DROP TRIGGER IF EXISTS tr_notify_node_update ON nodes;
DROP TRIGGER IF EXISTS tr_notify_node_delete ON nodes;
DROP FUNCTION IF EXISTS notify_node_change();
"
# 2. 删除Python文件
Remove-Item src/zephyr/shared/utils/pg_notify.py
Remove-Item src/zephyr/shared/utils/depgraph_events.py
```

---

## 元任务卡 P3-MT2：审查修复P3-T2

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-MT2 |
| 标题 | 循环审查修复P3-T2（LISTEN/NOTIFY） |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | P3-T2完成 |

### 审查清单

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | 触发器函数存在 | `SELECT proname FROM pg_proc WHERE proname='notify_node_change'` | notify_node_change |
| 2 | INSERT触发器存在 | `SELECT tgname FROM pg_trigger WHERE tgname='tr_notify_node_insert'` | tr_notify_node_insert |
| 3 | UPDATE触发器存在 | `SELECT tgname FROM pg_trigger WHERE tgname='tr_notify_node_update'` | tr_notify_node_update |
| 4 | DELETE触发器存在 | `SELECT tgname FROM pg_trigger WHERE tgname='tr_notify_node_delete'` | tr_notify_node_delete |
| 5 | pg_notify.py存在 | `Test-Path src/zephyr/shared/utils/pg_notify.py` | True |
| 6 | depgraph_events.py存在 | `Test-Path src/zephyr/shared/utils/depgraph_events.py` | True |
| 7 | EventListener可导入 | `python -c "from zephyr.shared.utils.pg_notify import EventListener"` | 无报错 |
| 8 | notify_change可调用 | `python -c "from zephyr.shared.utils.pg_notify import notify_change"` | 无报错 |
| 9 | 手动NOTIFY测试 | `SELECT pg_notify('depgraph_changed', '{"test":true}')` | 成功 |
| 10 | 触发器自动通知测试 | 插入测试节点，监听收到事件 | 收到事件 |
| 11 | 事件延迟 | 计时 | < 100ms |
| 12 | LISTEN使用直连PG(5432) | `grep "port.*5432" src/zephyr/shared/utils/pg_notify.py` | 有结果 |
| 13 | 复用PG_CONFIG | `grep "from zephyr.shared.utils.pg_connection import PG_CONFIG" src/zephyr/shared/utils/pg_notify.py` | 有结果 |

### 审查流程

1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → COMPLETED

### 修复授权

- `src/zephyr/shared/utils/pg_notify.py`
- `src/zephyr/shared/utils/depgraph_events.py`
- PostgreSQL数据库（CREATE TRIGGER / CREATE FUNCTION）

---

## 任务卡 P3-T3：按domain_id分区表（大表优化）

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-T3 |
| 标题 | 按domain_id HASH分区nodes和edges表 |
| 优先级 | P2 |
| 安全级别 | H |
| 依赖 | P2完成 + P3-T1完成（embedding列已添加）+ P3-T2完成（触发器已创建） |
| 对应文档 | P3方案§六 |
| 预计Token | 12000 |
| 超时 | 120分钟 |

### 施工范围

**可修改文件白名单**：
- `scripts/governance/migrate_sqlite_to_pg/02_partition_tables.sql`（新建）
- `scripts/governance/migrate_sqlite_to_pg/performance_baseline.txt`（新建）
- `scripts/governance/migrate_sqlite_to_pg/performance_after_partition.txt`（新建）
- `src/zephyr/governance/depgraph_schema.py`（修改，DDL改为分区表）

**禁止修改文件**：
- `scripts/governance/apply_depgraph.py`（SQL方言已在P2-T3-B处理）

### 前置条件

- [ ] P3-T1完成（embedding列已在nodes表中）
- [ ] P3-T2完成（触发器已在nodes表上创建）
- [ ] 当前查询性能基线已记录

### 风险提示

**高风险操作**：
1. 分区表主键必须包含分区键(domain_id)，原主键仅node_id需改为(node_id, domain_id)
2. edges表外键引用nodes.node_id，分区后需处理外键
3. 迁移期间数据不可用，需在维护窗口执行
4. 必须先pg_dump备份

### 施工步骤

#### 步骤1：记录性能基线

```powershell
cd D:\ZephyrAlpha
psql -U zephyr -d depgraph -c "
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM edges WHERE source_id IN (SELECT node_id FROM nodes WHERE domain_id = 'D-GOVERNANCE');
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM nodes;
" > scripts\governance\migrate_sqlite_to_pg\performance_baseline.txt
```

#### 步骤2：备份PostgreSQL数据库

```powershell
pg_dump -U zephyr -d depgraph > data\databases\backups\depgraph_pre_partition.sql
```

#### 步骤3：获取完整列定义

```powershell
psql -U zephyr -d depgraph -c "\d nodes"
psql -U zephyr -d depgraph -c "\d edges"
```

将输出中的列定义填入分区表DDL（替换 `-- ...` 注释部分）

#### 步骤4：创建分区表迁移脚本

**操作**：创建 `scripts/governance/migrate_sqlite_to_pg/02_partition_tables.sql`

**文件内容**：见P3方案§六.6.4[动作2]

**关键决策**：
- edges外键处理：选择方案A（删除外键，改用应用层校验）
- 分区数：8（HASH分区）
- 主键：nodes(node_id, domain_id)，edges(edge_id, domain_id)

#### 步骤5：执行分区迁移

```powershell
# 执行分区迁移
psql -U zephyr -d depgraph -f scripts\governance\migrate_sqlite_to_pg\02_partition_tables.sql

# 验证数据一致性
psql -U zephyr -d depgraph -c "
SELECT 'nodes_old' as tbl, COUNT(*) FROM nodes_old
UNION ALL
SELECT 'nodes_new', COUNT(*) FROM nodes
UNION ALL
SELECT 'edges_old', COUNT(*) FROM edges_old
UNION ALL
SELECT 'edges_new', COUNT(*) FROM edges;
"
```

#### 步骤6：验证分区裁剪

```powershell
psql -U zephyr -d depgraph -c "
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';
"
```

#### 步骤7：对比性能

```powershell
psql -U zephyr -d depgraph -c "
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM edges WHERE domain_id = 'D-GOVERNANCE';
EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM nodes;
" > scripts\governance\migrate_sqlite_to_pg\performance_after_partition.txt
```

#### 步骤8：删除旧表

```powershell
psql -U zephyr -d depgraph -c "
DROP TABLE nodes_old;
DROP TABLE edges_old;
"
```

#### 步骤9：更新depgraph_schema.py

**操作**：修改Schema DDL，将nodes和edges表定义改为分区表定义

#### 步骤10：重建触发器（分区后触发器需重建）

```powershell
# 分区表迁移后，P3-T2的触发器需在分区表上重建
# 重新执行P3-T2步骤1的触发器创建SQL
```

### 验收标准

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | nodes已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='nodes'` | 9（8分区+默认） |
| 2 | edges已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='edges'` | 9 |
| 3 | 数据一致 | nodes_old vs nodes_new行数 | 一致 |
| 4 | 分区裁剪生效 | EXPLAIN显示单分区扫描 | 只扫描1个分区 |
| 5 | 按域查询性能提升 | 对比基线 | 5-10x提升 |
| 6 | 索引已创建 | `\di` | 显示所有索引 |
| 7 | 旧表已删除 | `\dt` | 无nodes_old/edges_old |
| 8 | 触发器已重建 | `SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'tr_notify_%'` | 3 |
| 9 | embedding列在分区表中 | `SELECT column_name FROM information_schema.columns WHERE table_name='nodes_p0' AND column_name='embedding'` | embedding |
| 10 | apply_depgraph.py可运行 | `python scripts/governance/apply_depgraph.py diagnose` | 正常输出 |

### 回滚方案

```powershell
# 1. 恢复旧表（如果尚未删除）
psql -U zephyr -d depgraph -c "
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS edges;
ALTER TABLE nodes_old RENAME TO nodes;
ALTER TABLE edges_old RENAME TO edges;
"
# 2. 如果旧表已删除，从备份恢复
psql -U zephyr -d depgraph -f data\databases\backups\depgraph_pre_partition.sql
# 3. 恢复depgraph_schema.py
git checkout -- src/zephyr/governance/depgraph_schema.py
```

---

## 元任务卡 P3-MT3：审查修复P3-T3

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-MT3 |
| 标题 | 循环审查修复P3-T3（分区表） |
| 优先级 | P2 |
| 安全级别 | H |
| 依赖 | P3-T3完成 |

### 审查清单

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | nodes已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='nodes'` | 9 |
| 2 | edges已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='edges'` | 9 |
| 3 | nodes_p0~p7存在 | `SELECT tablename FROM pg_tables WHERE tablename LIKE 'nodes_p%' ORDER BY tablename` | 8个分区 |
| 4 | nodes_default存在 | `SELECT tablename FROM pg_tables WHERE tablename='nodes_default'` | nodes_default |
| 5 | edges_p0~p7存在 | `SELECT tablename FROM pg_tables WHERE tablename LIKE 'edges_p%' ORDER BY tablename` | 8个分区 |
| 6 | edges_default存在 | `SELECT tablename FROM pg_tables WHERE tablename='edges_default'` | edges_default |
| 7 | nodes行数一致 | `SELECT count(*) FROM nodes` | 14383（与迁移前一致） |
| 8 | edges行数一致 | `SELECT count(*) FROM edges` | 22605（与迁移前一致） |
| 9 | 分区裁剪生效 | `EXPLAIN SELECT * FROM nodes WHERE domain_id='D-GOVERNANCE'` | 只扫描1个分区 |
| 10 | 旧表已删除 | `SELECT tablename FROM pg_tables WHERE tablename IN ('nodes_old','edges_old')` | 0结果 |
| 11 | 触发器已重建 | `SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'tr_notify_%'` | 3 |
| 12 | embedding列在分区中 | `SELECT column_name FROM information_schema.columns WHERE table_name='nodes_p0' AND column_name='embedding'` | embedding |
| 13 | HNSW索引在分区中 | `SELECT indexname FROM pg_indexes WHERE tablename='nodes_p0' AND indexname LIKE '%embedding%'` | 有结果 |
| 14 | apply_depgraph.py diagnose可运行 | `python scripts/governance/apply_depgraph.py diagnose` | 正常输出 |
| 15 | 性能基线文件存在 | `Test-Path scripts/governance/migrate_sqlite_to_pg/performance_baseline.txt` | True |
| 16 | 分区后性能文件存在 | `Test-Path scripts/governance/migrate_sqlite_to_pg/performance_after_partition.txt` | True |
| 17 | 按域查询性能提升 | 对比基线和分区后 | 5-10x提升 |
| 18 | depgraph_schema.py已更新 | `grep "PARTITION BY" src/zephyr/governance/depgraph_schema.py` | 有结果 |

### 审查流程

1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → COMPLETED

### 修复授权

- `scripts/governance/migrate_sqlite_to_pg/02_partition_tables.sql`
- `src/zephyr/governance/depgraph_schema.py`
- PostgreSQL数据库（DROP/CREATE/TRUNCATE）

---

## 任务卡 P3-T4：监控告警（pg_stat_activity）

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-T4 |
| 标题 | pg_stat_activity监控告警 |
| 优先级 | P3 |
| 安全级别 | L |
| 依赖 | P2完成 |
| 对应文档 | P3方案§七 |
| 预计Token | 6000 |
| 超时 | 45分钟 |

### 施工范围

**可修改文件白名单**：
- `scripts/governance/monitor_pg.py`（新建）
- `config/pg_monitor.yaml`（新建）

**禁止修改文件**：
- `src/zephyr/governance/depgraph_schema.py`（分区表在P3-T3处理）
- `scripts/governance/apply_depgraph.py`
- `src/zephyr/shared/utils/pg_connection.py`（P2 已定义，仅复用）
- `src/zephyr/shared/utils/code_embedding.py`（P3-T1 处理）
- `src/zephyr/shared/utils/pg_notify.py`（P3-T2 处理）

### 施工步骤

#### 步骤1：创建监控脚本

**操作**：创建 `scripts/governance/monitor_pg.py`

**文件内容**：见P3方案§七.7.3[动作1]

**关键**：复用P2中定义的PG连接配置（`from zephyr.shared.utils.pg_connection import PG_CONFIG`）

#### 步骤2：执行单次监控检查

```powershell
cd D:\ZephyrAlpha
python scripts\governance\monitor_pg.py
```

#### 步骤3：验证慢查询检测

```powershell
# 在一个终端启动慢查询
psql -U zephyr -d depgraph -c "SELECT pg_sleep(10);"

# 在另一个终端运行监控
python scripts\governance\monitor_pg.py
```

#### 步骤4：创建监控配置文件

**操作**：创建 `config/pg_monitor.yaml`

**文件内容**：见P3方案§七.7.3[动作4]

### 验收标准

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 监控脚本可运行 | `python monitor_pg.py` | 无报错 |
| 2 | 慢查询检测 | pg_sleep(10) + 监控 | 检测到慢查询 |
| 3 | 连接数检测 | 并发连接 + 监控 | 显示当前连接数 |
| 4 | 告警日志写入 | 检查alerts.log | 有告警记录 |
| 5 | 持续监控 | `--watch --interval 5` | 每5s检查一次 |

### 回滚方案

```powershell
Remove-Item scripts/governance/monitor_pg.py
Remove-Item config/pg_monitor.yaml
```

---

## 元任务卡 P3-MT4：审查修复P3-T4

### 基本信息

| 字段 | 值 |
|------|-----|
| 任务卡ID | P3-MT4 |
| 标题 | 循环审查修复P3-T4（监控告警） |
| 优先级 | P3 |
| 安全级别 | L |
| 依赖 | P3-T4完成 |

### 审查清单

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | monitor_pg.py存在 | `Test-Path scripts/governance/monitor_pg.py` | True |
| 2 | pg_monitor.yaml存在 | `Test-Path config/pg_monitor.yaml` | True |
| 3 | 监控脚本可运行 | `python scripts/governance/monitor_pg.py` | 无报错 |
| 4 | 慢查询检测功能 | pg_sleep(10) + 监控 | 检测到慢查询 |
| 5 | 连接数检测功能 | `python scripts/governance/monitor_pg.py` | 显示连接数 |
| 6 | 空闲事务检测功能 | 开启事务不提交 + 监控 | 检测到空闲事务 |
| 7 | 死锁检测功能 | `SELECT deadlocks FROM pg_stat_database WHERE datname='depgraph'` | 可查询 |
| 8 | 告警日志路径存在 | `Test-Path data/databases/postgres/alerts.log` | True（有告警时） |
| 9 | 持续监控模式 | `python scripts/governance/monitor_pg.py --watch --interval 5` | 每5s检查 |
| 10 | 复用PG_CONFIG | `grep "from zephyr.shared.utils.pg_connection import PG_CONFIG" scripts/governance/monitor_pg.py` | 有结果 |
| 11 | 告警阈值合理 | `grep "slow_query_seconds\|max_connections" config/pg_monitor.yaml` | 5s, 150 |
| 12 | pg_stat_statements可用 | `SELECT query, calls, mean_exec_time FROM pg_stat_statements LIMIT 1` | 有结果 |

### 审查流程

1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → COMPLETED

### 修复授权

- `scripts/governance/monitor_pg.py`
- `config/pg_monitor.yaml`
