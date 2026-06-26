---
module_id: MOD-INF-012B
title: "P2 PostgreSQL迁移任务卡总览（全量重写版）— 3阶段骨架卡 + 24个TC-PG执行卡"
doc_type: task_card_index
status: Draft
version: "2.0.0"
belongs_to: "MOD-INF-012B-P2"
date: "2026-06-25"
ttl: permanent
---

# P2 PostgreSQL迁移任务卡总览（全量重写版）

> 施工方案真源：[MOD-INF-012B-P2-postgresql-migration.md](MOD-INF-012B-P2-postgresql-migration.md)
> 受影响文件索引：[MOD-INF-012B-P2-affected-files-index.md](MOD-INF-012B-P2-affected-files-index.md)
> 版本说明：v2.0.0 基于深度去噪审查（去噪率68%，120→63文件）全量重写，原8个任务卡重构为"3阶段骨架卡 + 24个TC-PG执行卡"

## 文档说明

本文档基于 [affected-files-index.md §九深度去噪审查](MOD-INF-012B-P2-affected-files-index.md#九深度去噪审查2026-06-25) 结果全量重写：

- **原8个任务卡**（P2-T1~P2-T6）重构为**3个阶段骨架卡**（保留基础设施/数据迁移/验证阶段）+ **24个TC-PG执行卡**（SQL方言调整细化）
- **去噪成果**：原始约120个需迁移文件 → 去噪后63个文件，去噪率68%
- **关键清理**：5个幽灵测试文件、9个governance.db噪音项、12个一次性脚本、3个已有PG兼容文件、18个纯噪音引用

**任务卡设计原则**：
- 每个TC-PG任务卡聚焦1个主文件（或1组同质文件），降低幻觉漂移
- 每个任务卡包含完整文件清单、施工要点、验收标准、回滚方案（自包含）
- max_length=50000约束：任务卡足够细粒度，避免超长

---

## 一、阶段总览

| 阶段 | 名称 | 任务卡 | 依赖 | 风险 |
|:---:|------|--------|------|:---:|
| 1 | Docker部署PostgreSQL + pgbouncer | **P2-T1**（骨架卡） | 无 | 中 |
| 2 | 数据迁移脚本（SQLite→PostgreSQL） | **P2-T2**（骨架卡） | 阶段1 | 高 |
| 3 | SQL方言调整（SQLite特有语法→PG标准） | **TC-PG-01~TC-PG-20**（20个执行卡） | 阶段2 | 高 |
| 4 | 删除文件锁补丁 | 合并到 **TC-PG-06**（apply_depgraph.py） | 阶段3 | 中 |
| 5 | 连接池配置 | **TC-PG-21**（执行卡） | 阶段1 | 低 |
| 6 | 红蓝测试验证并发写入 | **P2-T6**（骨架卡） | 阶段3-5 | 中 |
| 辅助 | YAML描述更新 + 视图迁移 + 归档 | **TC-PG-22~TC-PG-24**（3个执行卡） | 阶段3 | 低 |
| - | **合计** | **3骨架卡 + 24执行卡 = 27个** | - | - |

每个执行卡后面跟一个元任务卡（循环审查修复），共**27个任务卡 + 27个元任务卡 = 54个卡**。

---

## 二、任务卡清单（27个）

### 2.1 阶段骨架卡（3个，保留原结构）

| # | 任务卡ID | 名称 | 对应文档章节 | 元任务卡ID |
|---|---------|------|------------|-----------|
| 1 | P2-T1 | Docker部署PostgreSQL + pgbouncer | P2方案§四 | P2-MT1 |
| 2 | P2-T2 | 数据迁移脚本（SQLite→PostgreSQL） | P2方案§五 | P2-MT2 |
| 3 | P2-T6 | 红蓝测试验证并发写入 | P2方案§九 | P2-MT6 |

### 2.2 TC-PG执行卡（24个，SQL方言调整+辅助）

| # | 任务卡ID | 名称 | 包含文件 | 文件数 | 元任务卡ID |
|---|---------|------|---------|:---:|-----------|
| 1 | TC-PG-01 | depgraph_schema.py迁移 | depgraph_schema.py + persistence/depgraph_schema.py | 2 | MT-PG-01 |
| 2 | TC-PG-02 | database_service.py迁移 | database_service.py | 1 | MT-PG-02 |
| 3 | TC-PG-03 | depgraph_reader.py迁移 | depgraph_reader.py + dashboard.py | 2 | MT-PG-03 |
| 4 | TC-PG-04 | rule_engine.py迁移 | rule_engine.py | 1 | MT-PG-04 |
| 5 | TC-PG-05 | auto_runner.py迁移 | auto_runner.py | 1 | MT-PG-05 |
| 6 | TC-PG-06 | apply_depgraph.py迁移（含文件锁删除） | apply_depgraph.py + repair/concurrent_write_test.py | 2 | MT-PG-06 |
| 7 | TC-PG-07 | sync_yaml_to_depgraph.py迁移 | sync_yaml_to_depgraph.py | 1 | MT-PG-07 |
| 8 | TC-PG-08 | generate_project_depgraph.py迁移 | generate_project_depgraph.py | 1 | MT-PG-08 |
| 9 | TC-PG-09 | extract_depgraph.py迁移 | extract_depgraph.py | 1 | MT-PG-09 |
| 10 | TC-PG-10 | generate_target_path_tree.py迁移 | generate_target_path_tree.py | 1 | MT-PG-10 |
| 11 | TC-PG-11 | audit_domain_nodes.py迁移 | audit_domain_nodes.py | 1 | MT-PG-11 |
| 12 | TC-PG-12 | diagnose_depgraph.py迁移 | diagnose_depgraph.py | 1 | MT-PG-12 |
| 13 | TC-PG-13 | detect_causal_conflicts.py迁移 | detect_causal_conflicts.py | 1 | MT-PG-13 |
| 14 | TC-PG-14 | analyze_change_impact.py迁移 | analyze_change_impact.py | 1 | MT-PG-14 |
| 15 | TC-PG-15 | check_rule_four_way_alignment.py迁移 | check_rule_four_way_alignment.py | 1 | MT-PG-15 |
| 16 | TC-PG-16 | check_schema_version_writes.py迁移 | check_schema_version_writes.py | 1 | MT-PG-16 |
| 17 | TC-PG-17 | perf_depgraph_baseline.py迁移 | perf_depgraph_baseline.py | 1 | MT-PG-17 |
| 18 | TC-PG-18 | upgrade_headers_to_14fields.py迁移 | upgrade_headers_to_14fields.py | 1 | MT-PG-18 |
| 19 | TC-PG-19 | d5_architecture生成器批量迁移 | 18个生成器 | 18 | MT-PG-19 |
| 20 | TC-PG-20 | tests/ depgraph.db测试迁移 | 6个测试文件 | 6 | MT-PG-20 |
| 21 | TC-PG-21 | PG依赖与连接配置 | requirements.txt + pyproject.toml + .env.example + pg_connection.py | 4 | MT-PG-21 |
| 22 | TC-PG-22 | 规则/注册表YAML描述更新 | trae_056 + trae_059 + registry_of_registries.yaml | 3 | MT-PG-22 |
| 23 | TC-PG-23 | depgraph_schema.py视图迁移 | CREATE VIEW dep_cycles | 1 | MT-PG-23 |
| 24 | TC-PG-24 | 归档一次性脚本 | 12个一次性脚本移至_archive/ | 12 | MT-PG-24 |
| - | **合计** | - | - | **63** | - |

> **文件数说明**：TC-PG-23（视图迁移）与TC-PG-01（depgraph_schema.py迁移）共享同一文件`src/zephyr/governance/depgraph_schema.py`，但分属不同施工阶段（TC-PG-01为SQL方言调整，TC-PG-23为视图迁移），故文件数统计中不重复计算。实际唯一文件数为63。

---

## 三、依赖关系图

```
P2-T1（Docker部署）─┬─→ P2-T2（数据迁移）─┬─→ TC-PG-01~20（SQL方言）─┬─→ P2-T6（红蓝测试）
                   │                      │                          │
                   └─→ TC-PG-21（连接池）──┘                          │
                                          │                          │
                                          └─→ TC-PG-22~24（辅助）────┘

TC-PG-06（apply_depgraph）= 阶段3（SQL方言）+ 阶段4（删除文件锁）合并
TC-PG-23（视图迁移）依赖 TC-PG-01（depgraph_schema.py）完成
```

**关键依赖约束**：
1. TC-PG-01必须先于其他TC-PG执行（depgraph_schema.py是Schema真源）
2. TC-PG-06包含文件锁删除（原P2-T4合并进来）
3. TC-PG-21（连接池）可与TC-PG-01~20并行，但需在P2-T6前完成
4. TC-PG-23（视图迁移）依赖TC-PG-01完成
5. TC-PG-24（归档）可在任何时间执行，无依赖

---

## 四、阶段骨架卡详情

### 4.1 任务卡 P2-T1：Docker部署PostgreSQL + pgbouncer

| 字段 | 值 |
|------|-----|
| 任务卡ID | P2-T1 |
| 标题 | Docker部署PostgreSQL 16 + pgbouncer |
| 优先级 | P1 |
| 安全级别 | M |
| 执行模型 | GLM-5.2 |
| 依赖 | 无 |
| 对应文档 | P2方案§四 |
| 预计Token | 8000 |
| 超时 | 30分钟 |

**施工范围**：
- 可修改：`docker/docker-compose.postgres.yml`（新建）、`docker/postgres/init/01_create_extensions.sql`（新建）、`docker/.env.postgres`（新建）、`.gitignore`（修改）
- 禁止修改：`src/`、`scripts/`、`data/databases/depgraph.db`

**施工步骤**：见P2方案§四.4.2[动作1-8]，包含：
1. 创建Docker Compose文件（postgres:16-alpine + pgbouncer）
2. 创建PostgreSQL数据目录
3. 创建初始化脚本（pg_stat_statements + pgcrypto扩展）
4. 创建环境变量文件
5. 更新.gitignore
6. 启动容器
7. 验证PostgreSQL健康
8. 验证扩展安装

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | PostgreSQL容器运行 | `docker ps --filter name=zephyr-postgres` | Up (healthy) |
| 2 | pgbouncer容器运行 | `docker ps --filter name=zephyr-pgbouncer` | Up |
| 3 | PostgreSQL可连接 | `docker exec zephyr-postgres pg_isready` | accepting connections |
| 4 | pgbouncer可连接 | `docker exec zephyr-pgbouncer psql -c "SELECT 1"` | 返回1 |
| 5 | 扩展已安装 | `docker exec zephyr-postgres psql -c "\dx"` | pg_stat_statements + pgcrypto |
| 6 | .env.postgres已gitignore | `git check-ignore docker/.env.postgres` | 返回该文件路径 |

**回滚方案**：
```powershell
docker compose -f docker\docker-compose.postgres.yml down
Remove-Item -Recurse -Force "D:\ZephyrAlpha\data\databases\postgres"
git checkout -- .gitignore
```

---

### 4.2 任务卡 P2-T2：数据迁移脚本（SQLite→PostgreSQL）

| 字段 | 值 |
|------|-----|
| 任务卡ID | P2-T2 |
| 标题 | SQLite→PostgreSQL数据迁移 |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | P2-T1完成 |
| 对应文档 | P2方案§五 |
| 预计Token | 10000 |
| 超时 | 60分钟 |

**施工范围**：
- 可修改：`scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql`（新建）、`scripts/governance/migrate_sqlite_to_pg/01_create_pg_schema.sql`（新建）、`scripts/governance/migrate_sqlite_to_pg/migrate_data.py`（新建）、`requirements.txt`（修改）
- 禁止修改：`src/`、`data/databases/depgraph.db`（只读取）

**施工步骤**：见P2方案§五.5.2[动作1-6]，包含：
1. 备份depgraph.db（git commit）
2. 安装psycopg2-binary
3. 导出SQLite实际schema（注意：DB实际41列，非DDL的30列）
4. 创建PostgreSQL Schema DDL（翻译规则见P2方案§五.5.2[动作2]）
5. 创建数据迁移Python脚本
6. 执行迁移并验证行数对比

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | migrate_data.py存在 | `Test-Path scripts/governance/migrate_sqlite_to_pg/migrate_data.py` | True |
| 2 | nodes行数一致 | 对比SQLite与PG的`SELECT COUNT(*) FROM nodes` | 14383 |
| 3 | edges行数一致 | 对比SQLite与PG的`SELECT COUNT(*) FROM edges` | 22605 |
| 4 | domains行数一致 | 对比SQLite与PG的`SELECT COUNT(*) FROM domains` | 55 |
| 5 | psycopg2-binary已安装 | `pip show psycopg2-binary` | 已安装 |
| 6 | PG可查询 | `docker exec zephyr-postgres psql -U zephyr -d depgraph -c "SELECT 1"` | 返回1 |

**回滚方案**：
```powershell
docker exec zephyr-postgres psql -U zephyr -d depgraph -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
git checkout -- requirements.txt
```

---

### 4.3 任务卡 P2-T6：红蓝测试验证并发写入

| 字段 | 值 |
|------|-----|
| 任务卡ID | P2-T6 |
| 标题 | 红蓝测试验证40AI并发写入 |
| 优先级 | P1 |
| 安全级别 | M |
| 依赖 | TC-PG-01~20 + TC-PG-21完成 |
| 对应文档 | P2方案§九 |
| 预计Token | 10000 |
| 超时 | 90分钟 |

**施工范围**：
- 可修改：`tests/integration/test_pg_concurrency.py`（新建）

**施工步骤**：见P2方案§九.9.3[动作1-3]，包含：
1. 创建红蓝测试脚本（5个测试函数）
2. 执行红蓝测试
3. 执行40AI并发写入压力测试（4000节点，<30s）

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 并发写不同域 | `pytest test_concurrent_write_different_domains` | 40/40成功 |
| 2 | 并发写同一域 | `pytest test_concurrent_write_same_domain` | 40/40成功 |
| 3 | 读写并发 | `pytest test_concurrent_read_during_write` | 通过 |
| 4 | 无脏读 | `pytest test_no_dirty_read` | 通过 |
| 5 | 死锁检测 | `pytest test_deadlock_detection` | 通过 |
| 6 | 40AI压力测试 | 压力测试脚本 | 4000节点, <30s, >100 nodes/s |
| 7 | 无database is locked | 检查测试输出 | 0结果 |

**回滚方案**：
```powershell
Remove-Item tests/integration/test_pg_concurrency.py
docker exec zephyr-postgres psql -U zephyr -d depgraph -c "DELETE FROM nodes WHERE domain_id LIKE 'D-TEST-%' OR domain_id LIKE 'D-PERF-%';"
```

---

## 五、TC-PG执行卡详情（24个）

### 5.1 TC-PG-01：depgraph_schema.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-01 |
| 标题 | depgraph_schema.py迁移（Schema DDL真源） |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | P2-T2完成 |
| 对应文档 | P2方案§六.6.4 |
| 预计Token | 12000 |
| 超时 | 90分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/depgraph_schema.py`（主文件）
- `src/zephyr/governance/persistence/depgraph_schema.py`（纯re-export代理，随主文件迁移）

**施工要点**（基于affected-files-index.md §1.1第1项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L77 | `DB_PATH = .../depgraph.db` | 从环境变量读取`PG_DSN` | 路径常量→PG连接串 |
| L359-366 | `_PRAGMAS`（6条） | 删除全部 | PG无PRAGMA机制 |
| L369-371 | `_apply_pragmas()` | 删除函数及所有调用点（L920、L990、L1010，共3处；L963为`PRAGMA foreign_keys=ON`非_apply_pragmas调用） | - |
| L123,236,252,306,380,425,493,606 | `INTEGER PRIMARY KEY AUTOINCREMENT` | `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | 8处 |
| L862,864,999 | `sqlite_master`查询 | `information_schema.tables` | 3处 |
| L901,937 | `INSERT OR IGNORE INTO _schema_version` | `INSERT ... ON CONFLICT (version) DO NOTHING` | 2处 |
| L799 | `datetime('now')` | `NOW()` | 1处 |
| L901,937 | `VALUES (?, ?, ?)` | `VALUES (%s, %s, %s)` | 占位符 |
| L918,983,997,1008 | `sqlite3.connect()` | `psycopg2.connect()` | 4处 |
| L947,963 | `PRAGMA foreign_keys = OFF/ON` | `SET session_replication_role = 'replica'`或删除 | 2处 |
| L831-855 | `CREATE VIEW ... WITH RECURSIVE` | 保留（PG兼容） | 无需修改 |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留PRAGMA | `grep -n "PRAGMA" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 2 | 无残留AUTOINCREMENT | `grep -n "AUTOINCREMENT" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 3 | 无残留sqlite_master | `grep -n "sqlite_master" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 4 | 无残留INSERT OR IGNORE | `grep -n "INSERT OR IGNORE" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 5 | 无残留datetime('now') | `grep -n "datetime('now')" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 6 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 7 | 无残留?占位符 | `grep -n "VALUES (?)" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 8 | 模块可导入 | `python -c "from zephyr.governance.depgraph_schema import DB_PATH"` | 无报错 |

**回滚方案**：
```powershell
git checkout -- src/zephyr/governance/depgraph_schema.py src/zephyr/governance/persistence/depgraph_schema.py
```

---

### 5.2 TC-PG-02：database_service.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-02 |
| 标题 | database_service.py迁移（三库连接管理器） |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.4 |
| 预计Token | 8000 |
| 超时 | 60分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/database_service.py`

**施工要点**（基于affected-files-index.md §1.1第2项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L58 | `self.depgraph_db` | 从环境变量读取`PG_DSN` | 硬编码路径→PG连接配置 |
| L76-81 | `get_depgraph_conn()`内`sqlite3.connect()` | `psycopg2.connect()`；移除`row_factory = sqlite3.Row` | 改用`RealDictCursor` |
| L161,177,222,255,292 | `VALUES (?, ...)` | `VALUES (%s, ...)` | 5处占位符（含governance.db与market部分保持?） |
| L168,177 | `datetime('now')` | `NOW()` | governance.db部分保持 |
| L303 | `sqlite_master` | `information_schema.tables` | 1处 |
| L186,192,198,204,210 | `get_depgraph_conn()`调用链 | `sqlite3.Connection`→PG连接类型注解 | 类型注解更新（5处） |

**关键约束**：database_service.py管理三库（depgraph/market/governance），仅depgraph部分迁移，governance.db和market.duckdb保持原样。

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | depgraph连接已改PG | `grep -n "psycopg2" src/zephyr/governance/database_service.py` | 有结果 |
| 2 | governance.db保持SQLite | `grep -n "sqlite3.connect.*governance" src/zephyr/governance/database_service.py` | 有结果 |
| 3 | 无残留sqlite_master(depgraph) | `grep -n "sqlite_master" src/zephyr/governance/database_service.py` | 0结果 |
| 4 | 模块可导入 | `python -c "from zephyr.governance.database_service import DatabaseService"` | 无报错 |
| 5 | get_depgraph_conn可用 | `python -c "from zephyr.governance.database_service import DatabaseService; DatabaseService().get_depgraph_conn()"` | 无报错 |

**回滚方案**：
```powershell
git checkout -- src/zephyr/governance/database_service.py
```

---

### 5.3 TC-PG-03：depgraph_reader.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-03 |
| 标题 | depgraph_reader.py迁移（只读访问层） |
| 优先级 | P1 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.4 |
| 预计Token | 8000 |
| 超时 | 60分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/depgraph_reader.py`（主文件）
- `src/zephyr/infrastructure/asset_inventory/dashboard.py`（CLEAN：仅KnowledgeTransferGate类小段sqlite3查询合并到此卡）

**施工要点**（基于affected-files-index.md §1.1第3项 + §9.3 CLEAN第7项）：

| 文件 | 位置 | 当前 | 迁移后 |
|------|------|------|--------|
| depgraph_reader.py | L46 | `DB_PATH = .../depgraph.db` | 从环境变量读取`PG_DSN` |
| depgraph_reader.py | L58 | `sqlite3.connect()` | `psycopg2.connect()`；移除`row_factory = sqlite3.Row` |
| depgraph_reader.py | L78-245（约23处） | `?`占位符 | 全部`?`→`%s` |
| depgraph_reader.py | L112,118 | `from_node`/`to_node`列名 | 核对修复为`from_node_id`/`to_node_id`（潜在bug） |
| depgraph_reader.py | L124 | `edge_type`列名 | 核对修复为`dep_type`（潜在bug） |
| depgraph_reader.py | L210 | `arch_domains`表 | 核对修复（表不存在，潜在bug） |
| dashboard.py | L159 | `dep_path = .../depgraph.db` | 从环境变量读取`PG_DSN` |
| dashboard.py | L186 | `sqlite3.connect(timeout=10.0)` | `psycopg2.connect()` |
| dashboard.py | L187 | `SELECT node_id FROM nodes ORDER BY fan_in DESC LIMIT 5` | 修复列名`fan_in`→`in_degree`（潜在bug） |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect(depgraph) | `grep -n "sqlite3.connect" src/zephyr/governance/depgraph_reader.py` | 0结果 |
| 2 | 无残留?占位符 | `grep -n "VALUES (?)" src/zephyr/governance/depgraph_reader.py` | 0结果 |
| 3 | 列名bug已修复 | `grep -n "from_node_id\|to_node_id\|dep_type" src/zephyr/governance/depgraph_reader.py` | 有结果 |
| 4 | dashboard.py已迁移 | `grep -n "psycopg2" src/zephyr/infrastructure/asset_inventory/dashboard.py` | 有结果 |
| 5 | 模块可导入 | `python -c "from zephyr.governance.depgraph_reader import DepgraphReader"` | 无报错 |

**回滚方案**：
```powershell
git checkout -- src/zephyr/governance/depgraph_reader.py src/zephyr/infrastructure/asset_inventory/dashboard.py
```

---

### 5.4 TC-PG-04：rule_engine.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-04 |
| 标题 | rule_engine.py迁移（规则引擎） |
| 优先级 | P1 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.4 |
| 预计Token | 6000 |
| 超时 | 45分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/rule_engine.py`

**施工要点**（基于affected-files-index.md §1.1第4项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L50 | `_DB_PATH = .../depgraph.db` | 从环境变量读取`PG_DSN` | 路径常量 |
| L53-56 | `_PRAGMAS`（WAL/foreign_keys/busy_timeout） | 删除全部 | PG无PRAGMA |
| L90 | `sqlite3.connect(timeout=10.0)` | `psycopg2.connect()`；`timeout`→PG连接超时配置 | - |
| L92-93 | `for pragma in _PRAGMAS: conn.execute(pragma)` | 删除循环 | - |
| L94 | `sqlite_master` | `information_schema.tables` | - |
| L154,172,190 | `VALUES (?)`/`WHERE ... = ?` | `VALUES (%s)`/`WHERE ... = %s` | 3处占位符 |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留PRAGMA | `grep -n "PRAGMA" src/zephyr/governance/rule_engine.py` | 0结果 |
| 2 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" src/zephyr/governance/rule_engine.py` | 0结果 |
| 3 | 无残留sqlite_master | `grep -n "sqlite_master" src/zephyr/governance/rule_engine.py` | 0结果 |
| 4 | 模块可导入 | `python -c "from zephyr.governance.rule_engine import RuleEngine"` | 无报错 |

**回滚方案**：
```powershell
git checkout -- src/zephyr/governance/rule_engine.py
```

---

### 5.5 TC-PG-05：auto_runner.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-05 |
| 标题 | auto_runner.py迁移（自动运行器） |
| 优先级 | P1 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.4 |
| 预计Token | 6000 |
| 超时 | 45分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/auto_runner.py`

**施工要点**（基于affected-files-index.md §1.1第5项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L41 | `_DEPGRAPH_DB = .../depgraph.db` | 从环境变量读取`PG_DSN` | 路径常量 |
| L202,260,282 | `sqlite3.connect()` | `psycopg2.connect()` | 3处（L199为`if not _DEPGRAPH_DB.exists()`非连接点） |
| L206-215 | `CREATE TABLE IF NOT EXISTS governance_audit_logs (... AUTOINCREMENT ...)` | `AUTOINCREMENT`→`SERIAL`；建议删除兜底建表逻辑 | 兜底建表 |
| L220 | `VALUES (?, ?, ?, ?, ?, ?, ?)` | `VALUES (%s, %s, %s, %s, %s, %s, %s)` | 占位符 |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留AUTOINCREMENT | `grep -n "AUTOINCREMENT" src/zephyr/governance/auto_runner.py` | 0结果 |
| 2 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" src/zephyr/governance/auto_runner.py` | 0结果 |
| 3 | 无残留?占位符 | `grep -n "VALUES (?)" src/zephyr/governance/auto_runner.py` | 0结果 |
| 4 | 模块可导入 | `python -c "from zephyr.governance.auto_runner import AutoRunner"` | 无报错 |

**回滚方案**：
```powershell
git checkout -- src/zephyr/governance/auto_runner.py
```

---

### 5.6 TC-PG-06：apply_depgraph.py迁移（含文件锁删除）

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-06 |
| 标题 | apply_depgraph.py迁移（核心写入脚本 + 文件锁删除） |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.5 + §七（文件锁删除合并） |
| 预计Token | 15000 |
| 超时 | 120分钟 |

**可修改文件白名单**：
- `scripts/governance/apply_depgraph.py`（主文件，高复杂度）
- `scripts/governance/repair/concurrent_write_test.py`（MERGE-B：合并到此卡）

**施工要点**（基于affected-files-index.md §2.1第1项 + §9.4 MERGE-B）：

**A. SQL方言调整**：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L70 | `DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` | 路径常量 |
| L259,312,484,610,680,750,860,892,940,995,1044,1096,1158,1206,1261,1357,1407,1455,1512 | `sqlite3.connect()` | `psycopg2.connect()`/连接池 | 19处连接 |
| L647,708,806 | `cur.lastrowid` | `INSERT ... RETURNING id` | 3处（PG无lastrowid） |

**B. 文件锁删除（原P2-T4合并）**：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L191 | `import lock_files as _lf` | 删除 | PG MVCC管理并发 |
| L194 | `_db_write_lock_lock` | 删除 | threading.Lock |
| L198 | `_db_write_lock()` | 删除 | 双重锁 |
| L248 | `_optional_db_lock()` | 删除 | 可选锁包装器 |
| L148 | `_create_physical_backup()` | 改为`pg_dump`逻辑备份 | 物理备份→逻辑备份 |
| L303 | `_atomic_write()`内`_optional_db_lock`调用 | 删除调用，改用PG事务 | - |
| L76 | `_check_git_backup()` | 改为建议性检查（非阻断） | git备份门禁 |

**关键约束**：
- `scripts/lock_files.py`保留（通用文件锁，非DB锁）
- 仅删除DB相关锁调用，保留YAML文件锁（如generate_project_depgraph.py的YAML输出分支锁）

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留_db_write_lock | `grep -n "_db_write_lock" scripts/governance/apply_depgraph.py` | 0结果 |
| 2 | 无残留DB锁调用 | `grep -n "acquire_lock.*depgraph" scripts/governance/apply_depgraph.py` | 0结果 |
| 3 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" scripts/governance/apply_depgraph.py` | 0结果 |
| 4 | 无残留cur.lastrowid | `grep -n "cur.lastrowid" scripts/governance/apply_depgraph.py` | 0结果 |
| 5 | lock_files.py保留 | `Test-Path scripts/lock_files.py` | True |
| 6 | 备份方式为pg_dump | `grep -n "pg_dump" scripts/governance/apply_depgraph.py` | 有结果 |
| 7 | apply_depgraph.py diagnose可运行 | `python scripts/governance/apply_depgraph.py diagnose` | 正常输出 |
| 8 | apply_depgraph.py add-node可运行 | `python scripts/governance/apply_depgraph.py add-node --node-id TEST-PG --node-type module --domain-id D-TEST --name "PG Test"` | 成功插入 |
| 9 | 清理测试数据 | `python scripts/governance/apply_depgraph.py delete-node --node-id TEST-PG` | 成功删除 |

**回滚方案**：
```powershell
git checkout -- scripts/governance/apply_depgraph.py scripts/governance/repair/concurrent_write_test.py
```

---

### 5.7 TC-PG-07：sync_yaml_to_depgraph.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-07 |
| 标题 | sync_yaml_to_depgraph.py迁移（YAML同步脚本） |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.5 |
| 预计Token | 15000 |
| 超时 | 120分钟 |

**可修改文件白名单**：
- `scripts/governance/sync_yaml_to_depgraph.py`（高复杂度：27个触发器+12处INSERT OR REPLACE）

**施工要点**（基于affected-files-index.md §2.1第2项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L51 | `DB_PATH` | 从环境变量读取`PG_DSN` | 路径常量 |
| L864 | `sqlite3.connect()` | `psycopg2.connect()` | 连接 |
| L195,292,421,454,492,575,598,619,719,749,787,819 | `INSERT OR REPLACE` | `INSERT ... ON CONFLICT (...) DO UPDATE SET ...` | 12处 |
| L78,87 | `disable_readonly_triggers`/`restore_readonly_triggers` | `ALTER TABLE ... DISABLE TRIGGER` | 只读触发器管理 |

**关键约束**：27个只读触发器需用PL/pgSQL重写（见P2方案§六.6.5触发器翻译规则），3个chk_前缀触发器（chk_edges_design_immutable_update等）源码中不存在，仅DB实例中有，迁移时从DB导出实际触发器定义。

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留INSERT OR REPLACE | `grep -n "INSERT OR REPLACE" scripts/governance/sync_yaml_to_depgraph.py` | 0结果 |
| 2 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" scripts/governance/sync_yaml_to_depgraph.py` | 0结果 |
| 3 | 触发器已改PL/pgSQL | `grep -n "LANGUAGE plpgsql" scripts/governance/sync_yaml_to_depgraph.py` | 有结果 |
| 4 | sync_yaml可运行 | `python scripts/governance/sync_yaml_to_depgraph.py --dry-run` | 正常输出 |
| 5 | YAML同步后数据一致 | 对比同步前后`SELECT COUNT(*) FROM nodes` | 一致 |

**回滚方案**：
```powershell
git checkout -- scripts/governance/sync_yaml_to_depgraph.py
```

---

### 5.8 TC-PG-08：generate_project_depgraph.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-08 |
| 标题 | generate_project_depgraph.py迁移（项目依赖图生成） |
| 优先级 | P1 |
| 安全级别 | H |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.5 |
| 预计Token | 12000 |
| 超时 | 90分钟 |

**可修改文件白名单**：
- `scripts/governance/generate_project_depgraph.py`（高复杂度：5处连接+4处lock_files删除）

**施工要点**（基于affected-files-index.md §2.1第3项）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L223 | `DEPGRAPH_DB_PATH` | 从环境变量读取`PG_DSN` | 路径常量 |
| L491,586,2619,3120,3192 | `sqlite3.connect()` | `psycopg2.connect()` | 5处连接 |
| L2513,2516,2540,3514 | `lock_files`（subprocess调用） | 删除 | PG MVCC管理并发 |
| L2623 | `sqlite_master` | `information_schema.tables` | - |
| L3509-3566 | YAML输出分支锁 | 保留 | YAML文件锁不迁移PG |

**关键约束**：YAML输出分支锁（L3509-3566）保留，因为YAML文件不迁移到PG。

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect(depgraph) | `grep -n "sqlite3.connect" scripts/governance/generate_project_depgraph.py` | 0结果 |
| 2 | 无残留lock_files(depgraph) | `grep -n "lock_files" scripts/governance/generate_project_depgraph.py` | 仅YAML分支 |
| 3 | 无残留sqlite_master | `grep -n "sqlite_master" scripts/governance/generate_project_depgraph.py` | 0结果 |
| 4 | 脚本可运行 | `python scripts/governance/generate_project_depgraph.py --help` | 正常输出 |

**回滚方案**：
```powershell
git checkout -- scripts/governance/generate_project_depgraph.py
```

---

### 5.9 TC-PG-09：extract_depgraph.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-09 |
| 标题 | extract_depgraph.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.6 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：
- `scripts/governance/extract_depgraph.py`（中复杂度：2处连接，无`?`占位符）

**施工要点**（基于affected-files-index.md §2.1第4项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L176,414 | `sqlite3.connect(str(db_path))` | `psycopg2.connect()` |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" scripts/governance/extract_depgraph.py` | 0结果 |
| 2 | 脚本可运行 | `python scripts/governance/extract_depgraph.py --help` | 正常输出 |

**回滚方案**：
```powershell
git checkout -- scripts/governance/extract_depgraph.py
```

---

### 5.10 TC-PG-10：generate_target_path_tree.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-10 |
| 标题 | generate_target_path_tree.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.6 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：
- `scripts/governance/generate_target_path_tree.py`（中复杂度：路径常量+2处连接）

**施工要点**（基于affected-files-index.md §2.1第5项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L51 | `DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` |
| L73,94 | `sqlite3.connect()` | `psycopg2.connect()` |

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect | `grep -n "sqlite3.connect" scripts/governance/generate_target_path_tree.py` | 0结果 |
| 2 | 脚本可运行 | `python scripts/governance/generate_target_path_tree.py --help` | 正常输出 |

**回滚方案**：
```powershell
git checkout -- scripts/governance/generate_target_path_tree.py
```

---

### 5.11 TC-PG-11：audit_domain_nodes.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-11 |
| 标题 | audit_domain_nodes.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 5000 |
| 超时 | 30分钟 |

**可修改文件白名单**：`scripts/governance/audit_domain_nodes.py`（中复杂度）

**施工要点**（基于affected-files-index.md §2.1第8项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L28 | `DB_PATH` | 从环境变量读取`PG_DSN` |
| L160,184,333 | `sqlite3.connect()` | `psycopg2.connect()` |
| L153 | `datetime('now')` | `NOW()` |
| L430 | `INSERT OR REPLACE` | `ON CONFLICT DO UPDATE` |

**验收标准**：无残留sqlite3.connect/datetime('now')/INSERT OR REPLACE；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/audit_domain_nodes.py`

---

### 5.12 TC-PG-12：diagnose_depgraph.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-12 |
| 标题 | diagnose_depgraph.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 3000 |
| 超时 | 20分钟 |

**可修改文件白名单**：`scripts/governance/diagnose_depgraph.py`（低复杂度）

**施工要点**（基于affected-files-index.md §2.1第11项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L26 | `DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` |
| L53 | `sqlite3.connect()` | `psycopg2.connect()` |

**验收标准**：无残留sqlite3.connect；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/diagnose_depgraph.py`

---

### 5.13 TC-PG-13：detect_causal_conflicts.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-13 |
| 标题 | detect_causal_conflicts.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 3000 |
| 超时 | 20分钟 |

**可修改文件白名单**：`scripts/governance/detect_causal_conflicts.py`（低复杂度）

**施工要点**（基于affected-files-index.md §2.1第12项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L30 | `DEFAULT_DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` |
| L35 | `sqlite3.connect()` | `psycopg2.connect()` |

**验收标准**：无残留sqlite3.connect；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/detect_causal_conflicts.py`

---

### 5.14 TC-PG-14：analyze_change_impact.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-14 |
| 标题 | analyze_change_impact.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 3000 |
| 超时 | 20分钟 |

**可修改文件白名单**：`scripts/governance/analyze_change_impact.py`（低复杂度）

**施工要点**（基于affected-files-index.md §2.1第13项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L31 | `DEFAULT_DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` |
| L36 | `sqlite3.connect()` | `psycopg2.connect()` |

**验收标准**：无残留sqlite3.connect；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/analyze_change_impact.py`

---

### 5.15 TC-PG-15：check_rule_four_way_alignment.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-15 |
| 标题 | check_rule_four_way_alignment.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：`scripts/governance/check_rule_four_way_alignment.py`（低复杂度）

**施工要点**（基于affected-files-index.md §2.1第14项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L37 | `DB_PATH` | 从环境变量读取`PG_DSN` |
| L62 | `sqlite3.connect(timeout=10.0)` | `psycopg2.connect()`；`timeout`→`statement_timeout` |

**验收标准**：无残留sqlite3.connect；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/check_rule_four_way_alignment.py`

---

### 5.16 TC-PG-16：check_schema_version_writes.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-16 |
| 标题 | check_schema_version_writes.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：`scripts/governance/check_schema_version_writes.py`（中复杂度）

**施工要点**（基于affected-files-index.md §2.1第16项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L126 | `from zephyr.governance.depgraph_schema import _MIGRATIONS` | 确认PG迁移框架 |
| L131 | `db_path` | 从环境变量读取`PG_DSN` |
| L132 | `sqlite3.connect()` | `psycopg2.connect()` |

**验收标准**：无残留sqlite3.connect；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/check_schema_version_writes.py`

---

### 5.17 TC-PG-17：perf_depgraph_baseline.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-17 |
| 标题 | perf_depgraph_baseline.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：`scripts/governance/perf_depgraph_baseline.py`（中复杂度）

**施工要点**（基于affected-files-index.md §2.1第19项）：

| 位置 | 当前 | 迁移后 |
|------|------|--------|
| L51 | `DEPGRAPH_PATH` | 从环境变量读取`PG_DSN` |
| L60 | `sqlite3.connect(uri, uri=True)` | 标准连接+只读事务（PG无文件URI） |
| L67 | `sqlite_master` | `information_schema.tables` |

**验收标准**：无残留sqlite3.connect/sqlite_master；脚本可运行。

**回滚方案**：`git checkout -- scripts/governance/perf_depgraph_baseline.py`

---

### 5.18 TC-PG-18：upgrade_headers_to_14fields.py迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-18 |
| 标题 | upgrade_headers_to_14fields.py迁移 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：`scripts/ops/upgrade_headers_to_14fields.py`（中复杂度，有测试，CI集成）

**施工要点**：此脚本位于`scripts/ops/`而非`scripts/governance/`，但访问depgraph.db。迁移要点：
1. 路径常量→PG_DSN
2. sqlite3.connect()→psycopg2.connect()
3. 占位符?→%s
4. 确保CI集成测试通过

**验收标准**：无残留sqlite3.connect；CI测试通过。

**回滚方案**：`git checkout -- scripts/ops/upgrade_headers_to_14fields.py`

---

### 5.19 TC-PG-19：d5_architecture生成器批量迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-19 |
| 标题 | d5_architecture生成器批量迁移（18个生成器→1个任务卡） |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.6 |
| 预计Token | 12000 |
| 超时 | 90分钟 |

**可修改文件白名单**（18个生成器，基于affected-files-index.md §9.4 MERGE-A）：

| # | 文件路径 | 特殊注意点 |
|---|---------|-----------|
| 1 | `scripts/governance/d5_architecture/generators/generate_capacity_report.py` | - |
| 2 | `scripts/governance/d5_architecture/generators/generate_domain_architecture_diagram.py` | - |
| 3 | `scripts/governance/d5_architecture/generators/generate_domain_doc.py` | GROUP_CONCAT (L139,155)→STRING_AGG |
| 4 | `scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py` | - |
| 5 | `scripts/governance/d5_architecture/generators/generate_domain_index.py` | - |
| 6 | `scripts/governance/d5_architecture/generators/generate_integration_topology.py` | GROUP_CONCAT (L48)→STRING_AGG |
| 7 | `scripts/governance/d5_architecture/generators/generate_navigation_index.py` | - |
| 8 | `scripts/governance/d5_architecture/generators/generate_path_tree.py` | - |
| 9 | `scripts/governance/d5_architecture/generators/generate_runtime_plane_mapping.py` | - |
| 10 | `scripts/governance/d5_architecture/generators/generate_capability_heatmap.py` | sqlite_master (L159)→information_schema |
| 11 | `scripts/governance/d5_architecture/generators/generate_constraint_violations.py` | - |
| 12 | `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` | GROUP_CONCAT (L48)→STRING_AGG |
| 13 | `scripts/governance/d5_architecture/generators/generate_design_vs_production.py` | - |
| 14 | `scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py` | - |
| 15 | `scripts/governance/d5_architecture/validators/validate_cross_references.py` | - |
| 16 | `scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_code_sync.py` | - |
| 17 | `scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py` | - |
| 18 | `scripts/governance/d11_compliance/validate_task_decomposition_bypass.py` | -（注：d11_compliance与d5_architecture平级，同属governance子目录） |

**施工要点**（统一模式）：
1. 所有生成器统一模式：路径常量→PG_DSN、sqlite3.connect()→psycopg2.connect()、?→%s
2. 3个生成器需特殊处理：GROUP_CONCAT→STRING_AGG（2个）、sqlite_master→information_schema（1个）
3. 批量执行：可用脚本自动化处理统一模式，手动处理3个特殊点

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect | `grep -rln "sqlite3.connect" scripts/governance/d5_architecture/ scripts/governance/d11_compliance/validate_task_decomposition_bypass.py` | 0结果 |
| 2 | 无残留GROUP_CONCAT | `grep -rln "GROUP_CONCAT" scripts/governance/d5_architecture/` | 0结果 |
| 3 | 无残留sqlite_master | `grep -rln "sqlite_master" scripts/governance/d5_architecture/` | 0结果 |
| 4 | 生成器可运行 | `python scripts/governance/d5_architecture/generators/generate_domain_index.py --help` | 正常输出 |

**回滚方案**：`git checkout -- scripts/governance/d5_architecture/ scripts/governance/d11_compliance/validate_task_decomposition_bypass.py`

---

### 5.20 TC-PG-20：tests/ depgraph.db测试迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-20 |
| 标题 | tests/ depgraph.db测试迁移（6个测试文件） |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 对应文档 | P2方案§六.6.6 |
| 预计Token | 6000 |
| 超时 | 45分钟 |

**可修改文件白名单**（6个真实测试文件，基于affected-files-index.md §9.5 KEEP第1-6项）：

**注意**：tests/governance/下的5个测试文件（test_depgraph_reader.py等）是**幽灵文件**（文件不存在），已从清单删除。

| # | 文件路径 | 说明 |
|---|---------|------|
| 1-6 | tests/下6个真实depgraph.db测试文件 | 直接连接depgraph.db的测试 |

**施工要点**：
1. 获取真实测试文件清单：`grep -rln "depgraph.db\|sqlite3.connect" tests/ --include="*.py"`
2. 逐文件修改：sqlite3.connect→psycopg2.connect、?→%s、PRAGMA删除
3. 确保测试连接PG而非SQLite文件

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留sqlite3.connect(depgraph) | `grep -rln "sqlite3.connect.*depgraph" tests/` | 0结果 |
| 2 | 测试通过 | `pytest tests/ -x -k "depgraph"` | 全部通过 |

**回滚方案**：`git checkout -- tests/`

---

### 5.21 TC-PG-21：PG依赖与连接配置

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-21 |
| 标题 | PG依赖与连接配置（原P2-T5连接池配置） |
| 优先级 | P1 |
| 安全级别 | M |
| 依赖 | P2-T1完成（可与TC-PG-01~20并行） |
| 对应文档 | P2方案§八 |
| 预计Token | 8000 |
| 超时 | 60分钟 |

**可修改文件白名单**：
- `requirements.txt`（修改：添加psycopg2-binary）
- `pyproject.toml`（修改：添加psycopg2-binary）
- `.env.example`（修改：添加PG_DSN示例）
- `src/zephyr/shared/utils/pg_connection.py`（新建：PG连接池工具）

**施工要点**：
1. 在requirements.txt和pyproject.toml添加`psycopg2-binary>=2.9`
2. 在.env.example添加`PG_DSN=postgresql://zephyr:zephyr_dev_2026@localhost:6432/depgraph`
3. 创建`src/zephyr/shared/utils/pg_connection.py`（见P2方案§八.8.2[动作2]）
4. 验证pgbouncer配置：`pool_mode=transaction`、`max_client_conn=200`、`default_pool_size=30`

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | psycopg2-binary已安装 | `pip show psycopg2-binary` | 已安装 |
| 2 | requirements.txt已更新 | `grep "psycopg2" requirements.txt` | 有结果 |
| 3 | .env.example已更新 | `grep "PG_DSN" .env.example` | 有结果 |
| 4 | pg_connection.py存在 | `Test-Path src/zephyr/shared/utils/pg_connection.py` | True |
| 5 | get_depgraph_connection可用 | `python -c "from zephyr.shared.utils.pg_connection import get_depgraph_connection"` | 无报错 |
| 6 | pgbouncer配置正确 | `docker exec zephyr-pgbouncer cat /etc/pgbouncer/pgbouncer.ini` | pool_mode=transaction |
| 7 | 10线程并发查询成功 | 并发测试脚本 | 全部成功 |

**回滚方案**：
```powershell
Remove-Item src/zephyr/shared/utils/pg_connection.py
git checkout -- requirements.txt pyproject.toml .env.example
```

---

### 5.22 TC-PG-22：规则/注册表YAML描述更新

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-22 |
| 标题 | 规则/注册表YAML描述更新 |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成 |
| 预计Token | 4000 |
| 超时 | 30分钟 |

**可修改文件白名单**：
- `docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml`（修改：更新depgraph.db描述为PostgreSQL）
- `src/zephyr/governance/rule_enforcement/g_trae_059.yaml`（修改：L1,40,58,63,76,77注释引用depgraph.db）
- `docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml`（修改：更新数据库描述）

**施工要点**：
1. 更新YAML文件中所有`depgraph.db`引用为`PostgreSQL (depgraph)`
2. 更新数据库类型描述：SQLite→PostgreSQL
3. 保持YAML规则逻辑不变，仅更新描述性文本

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | g_trae_056已更新 | `grep -i "postgresql" docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml` | 有结果 |
| 2 | g_trae_059已更新 | `grep -i "postgresql" src/zephyr/governance/rule_enforcement/g_trae_059.yaml` | 有结果 |
| 3 | registry已更新 | `grep -i "postgresql" docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml` | 有结果 |
| 4 | YAML语法正确 | `python -c "import yaml; yaml.safe_load(open('docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml'))"` | 无报错 |

**回滚方案**：`git checkout -- docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml src/zephyr/governance/rule_enforcement/g_trae_059.yaml docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml`

---

### 5.23 TC-PG-23：depgraph_schema.py视图迁移

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-23 |
| 标题 | depgraph_schema.py视图迁移（CREATE VIEW dep_cycles） |
| 优先级 | P2 |
| 安全级别 | M |
| 依赖 | TC-PG-01完成（depgraph_schema.py迁移后） |
| 预计Token | 3000 |
| 超时 | 20分钟 |

**可修改文件白名单**：
- `src/zephyr/governance/depgraph_schema.py`（L831-855：CREATE VIEW dep_cycles）

**施工要点**（基于affected-files-index.md §1.1第1项最后行）：

| 位置 | 当前 | 迁移后 | 说明 |
|------|------|--------|------|
| L831-855 | `CREATE VIEW ... WITH RECURSIVE` | 保留（PG兼容） | PG支持WITH RECURSIVE |

**关键约束**：此视图PG兼容，无需修改SQL，但需验证：
1. 视图在PG中创建成功
2. 视图查询结果与SQLite一致

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 视图存在 | `docker exec zephyr-postgres psql -U zephyr -d depgraph -c "\dv dep_cycles"` | 有结果 |
| 2 | 视图可查询 | `docker exec zephyr-postgres psql -U zephyr -d depgraph -c "SELECT COUNT(*) FROM dep_cycles"` | 返回行数 |

**回滚方案**：`docker exec zephyr-postgres psql -U zephyr -d depgraph -c "DROP VIEW IF EXISTS dep_cycles;"`

---

### 5.24 TC-PG-24：归档一次性脚本

| 字段 | 值 |
|------|-----|
| 任务卡ID | TC-PG-24 |
| 标题 | 归档一次性脚本（12个脚本移至_archive/） |
| 优先级 | P3 |
| 安全级别 | L |
| 依赖 | 无（可在任何时间执行） |
| 预计Token | 2000 |
| 超时 | 15分钟 |

**可修改文件白名单**（12个一次性脚本，基于affected-files-index.md §9.4 DELETE + OBSOLETE）：

**DELETE（8个一次性脚本）**：

| # | 文件路径 | 理由 |
|---|---------|------|
| 1 | `scripts/governance/dm105_depgraph_triage.py` | DM-105一次性三策略分诊脚本 |
| 2 | `scripts/governance/dm106_p2b_verification.py` | DM-106一次性P2-B验证脚本 |
| 3 | `scripts/governance/migrate_arch_f_functions.py` | 阶段1迁移脚本，已完成 |
| 4 | `scripts/governance/migrate_clean_build_status.py` | OPS任务卡一次性脏值清洗 |
| 5 | `scripts/governance/d5_architecture/dm200912_rewrite_views.py` | docstring自述"一次性脚本" |
| 6 | `scripts/governance/d5_architecture/dm200912_query_domains.py` | docstring自述"一次性脚本" |
| 7 | `scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py` | docstring自述"一次性脚本" |
| 8 | `scripts/governance/d5_architecture/dm200916_write_direct.py` | docstring自述"一次性脚本" |

**OBSOLETE（4个已完成使命）**：

| # | 文件路径 | 理由 |
|---|---------|------|
| 9 | `scripts/governance/rename_whitelist_cleanup.py` | 代码注释"替换已执行完毕" |
| 10 | `scripts/governance/verify_final_delivery.py` | autopilot session一次性 |
| 11 | `scripts/governance/repair/audit_design_completeness.py` | autopilot session一次性 |
| 12 | `scripts/governance/repair/red_blue_test.py` | autopilot session一次性 |

**施工要点**：
1. 创建归档目录：`scripts/_archive/`
2. 将12个脚本移动到`scripts/_archive/`
3. 在归档目录创建README.md说明归档原因和日期
4. 更新相关文档引用（如有）

**验收标准**：

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 归档目录存在 | `Test-Path scripts/_archive/` | True |
| 2 | 12个脚本已移动 | `(Get-ChildItem scripts/_archive/*.py).Count` | ≥12 |
| 3 | 原位置无残留 | 检查12个原路径 | 文件不存在 |
| 4 | README存在 | `Test-Path scripts/_archive/README.md` | True |

**回滚方案**：
```powershell
Move-Item scripts/_archive/*.py scripts/governance/  # 逐个还原
Remove-Item scripts/_archive/README.md
```

---

## 六、元任务卡（循环审查修复，27个）

每个任务卡完成后，必须经过对应的元任务卡循环审查，直到连续2次0问题。

### 6.1 元任务卡清单

| # | 元任务卡ID | 对应任务卡 | 审查重点 |
|---|-----------|-----------|---------|
| 1 | P2-MT1 | P2-T1 | Docker容器健康、扩展安装、.gitignore |
| 2 | P2-MT2 | P2-T2 | 数据行数一致、schema对齐、psycopg2安装 |
| 3 | P2-MT6 | P2-T6 | 并发测试通过、无database is locked、测试数据清理 |
| 4 | MT-PG-01 | TC-PG-01 | 无残留PRAGMA/AUTOINCREMENT/sqlite_master/INSERT OR IGNORE |
| 5 | MT-PG-02 | TC-PG-02 | depgraph连接改PG、governance.db保持SQLite |
| 6 | MT-PG-03 | TC-PG-03 | 列名bug修复、dashboard.py迁移 |
| 7 | MT-PG-04 | TC-PG-04 | 无残留PRAGMA/sqlite3.connect/sqlite_master |
| 8 | MT-PG-05 | TC-PG-05 | 无残留AUTOINCREMENT/sqlite3.connect |
| 9 | MT-PG-06 | TC-PG-06 | 无残留_db_write_lock/cur.lastrowid、pg_dump备份 |
| 10 | MT-PG-07 | TC-PG-07 | 无残留INSERT OR REPLACE、触发器改PL/pgSQL |
| 11 | MT-PG-08 | TC-PG-08 | 无残留lock_files(depgraph)、YAML分支锁保留 |
| 12 | MT-PG-09 | TC-PG-09 | 无残留sqlite3.connect |
| 13 | MT-PG-10 | TC-PG-10 | 无残留sqlite3.connect |
| 14 | MT-PG-11 | TC-PG-11 | 无残留datetime('now')/INSERT OR REPLACE |
| 15 | MT-PG-12 | TC-PG-12 | 无残留sqlite3.connect |
| 16 | MT-PG-13 | TC-PG-13 | 无残留sqlite3.connect |
| 17 | MT-PG-14 | TC-PG-14 | 无残留sqlite3.connect |
| 18 | MT-PG-15 | TC-PG-15 | 无残留sqlite3.connect、statement_timeout |
| 19 | MT-PG-16 | TC-PG-16 | 无残留sqlite3.connect、_MIGRATIONS导入 |
| 20 | MT-PG-17 | TC-PG-17 | 无残留sqlite_master、URI连接改造 |
| 21 | MT-PG-18 | TC-PG-18 | CI测试通过 |
| 22 | MT-PG-19 | TC-PG-19 | 无残留GROUP_CONCAT/sqlite_master（批量18个） |
| 23 | MT-PG-20 | TC-PG-20 | 无残留sqlite3.connect(depgraph)、测试通过 |
| 24 | MT-PG-21 | TC-PG-21 | pgbouncer配置、并发查询、pg_connection可用 |
| 25 | MT-PG-22 | TC-PG-22 | YAML语法正确、描述已更新 |
| 26 | MT-PG-23 | TC-PG-23 | 视图存在、可查询 |
| 27 | MT-PG-24 | TC-PG-24 | 12个脚本已归档、README存在 |

### 6.2 元任务卡统一模板

每个元任务卡遵循统一模板：

```
### 元任务卡 MT-PG-XX：审查修复TC-PG-XX

| 字段 | 值 |
|------|-----|
| 任务卡ID | MT-PG-XX |
| 标题 | 循环审查修复TC-PG-XX |
| 优先级 | 同对应任务卡 |
| 安全级别 | 同对应任务卡 |
| 依赖 | TC-PG-XX完成 |

**审查流程**：
1. 按对应任务卡的验收标准逐项检查
2. 记录问题
3. 修复问题（直接修改对应文件）
4. 重新检查
5. 连续2次0问题 → COMPLETED

**修复授权**：同对应任务卡的可修改文件白名单
```

### 6.3 全局验收标准（所有任务卡完成后）

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | src/无残留PRAGMA(depgraph) | `grep -rn "PRAGMA" src/` | 仅governance.db相关 |
| 2 | src/无残留INSERT OR REPLACE | `grep -rn "INSERT OR REPLACE" src/` | 0结果 |
| 3 | src/无残留INSERT OR IGNORE(depgraph) | `grep -rn "INSERT OR IGNORE" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 4 | src/无残留AUTOINCREMENT | `grep -rn "AUTOINCREMENT" src/` | 0结果 |
| 5 | src/无残留sqlite3.connect(depgraph) | `grep -rn "sqlite3.connect.*depgraph" src/` | 0结果 |
| 6 | src/无残留cursor.lastrowid | `grep -rn "cursor.lastrowid" src/` | 0结果 |
| 7 | src/无残留sqlite_master(depgraph) | `grep -rn "sqlite_master" src/` | 仅governance.db相关 |
| 8 | src/无残留GROUP_CONCAT | `grep -rn "GROUP_CONCAT" src/` | 0结果 |
| 9 | src/无残留datetime('now')(depgraph) | `grep -rn "datetime('now')" src/` | 仅governance.db相关 |
| 10 | src/无残留?占位符(depgraph) | `grep -rn "VALUES (?)" src/zephyr/governance/depgraph_schema.py` | 0结果 |
| 11 | scripts/无残留_db_write_lock | `grep -rn "_db_write_lock" scripts/` | 0结果 |
| 12 | scripts/无残留sqlite3.connect(depgraph) | `grep -rn "sqlite3.connect.*depgraph" scripts/` | 0结果 |
| 13 | 全部模块可导入 | `python -c "import zephyr.governance.depgraph_schema; import zephyr.governance.database_service; import zephyr.governance.depgraph_reader"` | 无报错 |
| 14 | 红蓝测试通过 | `pytest tests/integration/test_pg_concurrency.py -v` | 全部通过 |

---

## 七、执行顺序建议

基于依赖关系和风险分析，推荐执行顺序：

### 7.1 串行关键路径（P1优先级）

```
P2-T1（Docker部署）→ P2-T2（数据迁移）→ TC-PG-01（depgraph_schema.py）
→ TC-PG-02~05（src核心文件）→ TC-PG-06~08（高复杂度脚本）
→ TC-PG-21（连接池）→ P2-T6（红蓝测试）
```

### 7.2 并行可执行任务

以下任务卡可在TC-PG-01完成后并行执行：
- TC-PG-09~18（低中复杂度独立脚本）
- TC-PG-19（d5_architecture批量迁移）
- TC-PG-20（tests迁移）
- TC-PG-22（YAML描述更新）
- TC-PG-23（视图迁移，依赖TC-PG-01）
- TC-PG-24（归档，无依赖）

### 7.3 执行建议

1. **先串行执行关键路径**：P2-T1 → P2-T2 → TC-PG-01 → TC-PG-02~05
2. **再并行执行独立任务**：TC-PG-06~18可分配给多个AI并行
3. **最后执行验证**：TC-PG-21 → P2-T6
4. **辅助任务随时可做**：TC-PG-22~24

---

## 八、文档变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-06-25 | 初版：8个任务卡 + 8个元任务卡 |
| 2.0.0 | 2026-06-25 | 全量重写：基于深度去噪审查（去噪率68%），重构为3阶段骨架卡 + 24个TC-PG执行卡 |

---

> 本文档基于 [affected-files-index.md §九深度去噪审查](MOD-INF-012B-P2-affected-files-index.md#九深度去噪审查2026-06-25) 结果编写。
> 原始约120个需迁移文件 → 去噪后63个文件，分为24个TC-PG执行卡，去噪率68%。
