---
module_id: SH-DB-001
submodule_path: src/zephyr/infrastructure/db
title: "Database 集成蓝图 — SQLite+DuckDB 核心运营 + v3.0 PostgreSQL容量升级"
doc_type: blueprint
status: Active
version: "4.0.1"
layer: cross_layer
blueprint_level: module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260519-001
date: "2026-06-27"
valid_from: "2026-05-19"
ttl: permanent
rule_form: structural
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
scope: global
stability: evolving
verifiability: automated
construction_progress: partially_implemented
actual_disk_path: 'D:\ZephyrAlpha\src\zephyr\infrastructure\db\'
codification_level: L2
generation: 3
functional_domain: data
summary: "Database 集成蓝图——聚合 MOD-INF-012A（Core: SQLite+DuckDB已实现）和 MOD-INF-012B（v3.0: depgraph.db 从 SQLite 迁移到 PostgreSQL，P2迁移主体已完成2026-06-28，TC-PG-08/10残留于2026-06-29清理完毕4/4验收通过，整体待24任务卡全面验证故 partially_implemented，P3优化待施工）。DW-045拆分完成，详细内容见子蓝图。"
tags: [database, db, sqlite, duckdb, atm, atomic-transaction, task-repo, olap, infrastructure, migration, self-healing, operational-excellence, dual-db-router, write-batcher, integration-blueprint]
priority: P1
runtime_plane: hot
child_modules:
  - {module_id: "MOD-INF-012A", title: "Database Core — SQLite+DuckDB 双引擎核心运营", status: "Active", construction_progress: "completed", path: "sub_blueprints/（012A 无独立蓝图文件，代码清单见本文档 §1.1）"}
  - {module_id: "MOD-DB_DEPGRAPH_PG", title: "P2 PostgreSQL迁移 — depgraph.db SQLite→PostgreSQL（Windows原生安装）", status: "Active", construction_progress: "partially_implemented", path: "sub_blueprints/mod_inf_012b_p2_postgresql_migration.md"}
  - {module_id: "MOD-DB_DEPGRAPH_OPT", title: "P3 PostgreSQL优化 — pgvector+LISTEN/NOTIFY+分区表+监控", status: "Draft", construction_progress: "partially_implemented", path: "sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md"}
depends_on:
  - {target: "MOD-TASK_SYSTEM", at: "§3.2.1", why: "task-system——TaskCard数据层真源"}
  - {target: "MOD-GATE_ENGINE", at: "§1", why: "GateEngine——门禁结果SQLite落盘消费方"}
  - {target: "architecture_model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——本蓝图真源"}
references:
  - {id: "PS-STD-001", at: "§2~§7", why: "frontmatter字段合法值"}
  - {id: "PS-STD-005", at: "§6", why: "蓝图归属与引用链——belongs_to字段定义"}
  - {id: "GOV-AI-001", at: "全篇", why: "AI自治权限注册——数据库操作权限边界"}
  - {id: "MOD-FEEDBACK_LOOP", at: "§2.1", why: "FLE 消费 olap_engine——集成关系"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计事件入库"}
  - {id: "MOD-INF-015", at: "全篇", why: "query_metrics 等遥测读写"}
---

# Database 集成蓝图 — SQLite+DuckDB 核心运营 + v3.0 PostgreSQL容量升级

> module_id: SH-DB-001 | version: 4.0.1 | status: Active | layer: cross_layer | belongs_to: MOD-MASTER_BLUEPRINT
> actual_disk_path: `D:\ZephyrAlpha\src\zephyr\infrastructure\db\` | generation: 3 | construction_progress: partially_implemented
> **DW-045 拆分完成**。详细内容见子蓝图。本文档为集成入口。

## 概述

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules SH-DB-001`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

### §0.1 代码文件清单

> 本蓝图为集成索引，012A 代码清单见本文档 §1.1，012B 施工方案见子蓝图 mod_inf_012b_p2/p3_*

本蓝图是 Database 模块的集成入口——聚合两个子蓝图：
- **MOD-INF-012A Database Core**：SQLite+DuckDB 双引擎核心运营（13 个 .py 全部已实现，物理代码主位置 `src/zephyr/infrastructure/db/`）
- **MOD-INF-012B v3.0 Capacity Upgrade**：depgraph.db 从 SQLite 迁移到 PostgreSQL（P2 迁移主体已完成 2026-06-28，TC-PG-08/10 残留于 2026-06-29 清理完毕 4/4 验收通过，整体待 24 任务卡全面验证故 partially_implemented + P3 优化待施工）

核心职责：为 AI 治理框架提供结构化数据持久化与查询能力——8 张核心表、10 状态任务机、ATM 两阶段原子事务、OLAP 分析、冷热数据分层。v3.0 目标支持 40+ AI 并发写入 + PostgreSQL MVCC。

## 子蓝图索引

| module_id | 标题 | 状态 | 施工进度 | 文件路径 |
|-----------|------|------|:---:|------|
| MOD-INF-012A | Database Core — SQLite+DuckDB 双引擎核心运营 | Active | completed | 012A 无独立蓝图文件，代码清单见本文档 §1.1 |
| MOD-DB_DEPGRAPH_PG | P2 PostgreSQL迁移 — depgraph.db SQLite→PostgreSQL（Windows原生安装） | Active | partially_implemented | [sub_blueprints/mod_inf_012b_p2_postgresql_migration.md](sub_blueprints/mod_inf_012b_p2_postgresql_migration.md) |
| MOD-DB_DEPGRAPH_OPT | P3 PostgreSQL优化 — pgvector+LISTEN/NOTIFY+分区表+监控 | Draft | partially_implemented | [sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md](sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md) |

### 职责划分

| 子蓝图 | 覆盖内容 | 物理代码 |
|--------|---------|---------|
| MOD-INF-012A | SQLite WAL 事务引擎 / DuckDB OLAP / ATM v2.0 / TaskRepository 10状态机 / DatabaseManager 运维 / AuditSchema 审计查询 / QueryMetrics 性能监控 | `src/zephyr/infrastructure/db/` 13 个 .py（全部已实现；governance/ 根与 governance/persistence/ 存在过渡期副本） |
| MOD-DB_DEPGRAPH_PG | Windows原生安装 PostgreSQL / 数据迁移 / SQL 方言调整 / 删除文件锁 / 红蓝测试 | 见 P2 方案 §十二受影响文件索引 |
| MOD-DB_DEPGRAPH_OPT | pgvector 语义检索 / LISTEN/NOTIFY 事件通知 / 按 domain_id 分区表 / pg_stat_activity 监控告警 | 见 P3 方案 §十受影响文件索引 |

### AI 施工指引

- **读 Core 实现** → 本文档 §1.1——了解已实现的 SQLite+DuckDB 基础设施
- **施工 P2 迁移** → [mod_inf_012b_p2_postgresql_migration.md](sub_blueprints/mod_inf_012b_p2_postgresql_migration.md)——迁移设计 + 施工步骤 + 验收标准
- **施工 P3 优化** → [mod_inf_012b_p3_postgresql_optimization.md](sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md)——4 大优化方向
- **查看代码** → `D:\ZephyrAlpha\src\zephyr\infrastructure\db\`
- **查看测试** → `D:\ZephyrAlpha\tests\unit\`（unit 单元测试）与 `D:\ZephyrAlpha\tests\unit\db\`（db 集成测试）

## 集成架构概览

### 组件全景

| # | 组件 | 所属子蓝图 | 状态 | 职责 |
|---|------|:---:|:---:|------|
| 1 | TaskRepository | 012A | ✅ 已实现 | 任务 CRUD + 10 状态机 + 事件写入 + 任务卡永久保留（DB触发器 prevent_hard_delete 阻止删除） |
| 2 | AtomicTransactionManager | 012A | ✅ 已实现 | 跨 SQLite/文件系统两阶段提交 |
| 3 | OLAPEngine | 012A | ✅ 已实现 | DuckDB OLAP 分析 + Parquet 归档 |
| 4 | DatabaseManager | 012A | ✅ 已实现 | 连接池/健康检查/备份/WAL checkpoint |
| 5 | AuditSchema | 012A | ✅ 已实现 | 审计视图 + 补偿事件查询 |
| 6 | QueryMetrics | 012A | ✅ 已实现 | P50/P95/P99 + slow_queries |
| 7 | SQLiteSchema | 012A | ✅ 已实现 | DDL + _MIGRATIONS 迁移框架 |
| 8 | BaseRepo | 012A | ✅ 已实现 | 仓储基类（CRUD 公共逻辑） |
| 9 | GateRepo | 012A | ✅ 已实现 | 门禁结果持久化 |
| 10 | CircuitBreakerRepo | 012A | ✅ 已实现 | 熔断器状态仓储 |
| 11 | CircuitBreakerTypes | 012A | ✅ 已实现 | 熔断器类型定义 |
| 12 | Query | 012A | ✅ 已实现 | 查询构造器 |
| 13 | Transition | 012A | ✅ 已实现 | 状态迁移定义 |
| 14 | DualDBRouter | 012B | ❌ 已裁定删除 | ~~PostgreSQL（在线）+ SQLite（离线）路由~~——P2 迁移完成，过渡期前提消失；由 [`get_depgraph_pg_connection()`](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py)（PG）+ [`get_db_connection()`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py)（SQLite）双入口覆盖 |
| 15 | WriteBatcher | 012B | ⏸ 暂缓（待 L 级） | 批量写入缓冲——真问题但 L 级（5000+脚本）需求，当前 S 级 571 脚本无写争抢实证 |
| 16 | ScriptScheduler | 012B | ❌ 已裁定删除 | ~~Worker Pool + Semaphore + PriorityQueue~~——由 [BulkheadExecutorV2](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py)（四池+熔断）+ MOD-INF-005 覆盖 |
| 17 | ScriptRegistry | 012B | ✅ 已覆盖 | 脚本注册表——已由 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py) ScriptRegistry 类覆盖（CT-DB-005 契约对齐） |
| 18 | ScriptExecutionLogger | 012B | ⏸ 暂缓（待 M-1 级） | 脚本执行日志——571 脚本已达 M-1 下限 500，纯新增低风险，待启动（CT-DB-006 契约） |

### 数据流概览

```
MOD-TASK_SYSTEM (task-system) ──→ TaskRepository ──→ events 表 ──→ OLAPEngine ──→ MOD-FEEDBACK_LOOP (FLE)
MOD-GATE_ENGINE (gate-engine) ──→ TaskRepository ──→ gates 表   ──→ AuditSchema ──→ MOD-INF-020 (audit)
v3.0: 脚本执行器 ──→ get_depgraph_pg_connection() ──→ PG（depgraph）──→ script_executions 表（暂缓，待 M-1 级）
                            └─→ get_db_connection() ──→ SQLite（governance.db，治理/任务卡）
注: DualDBRouter 已裁定删除（P2 迁移完成，过渡期前提消失）；WriteBatcher 暂缓（待 L 级 5000+脚本）
注: 无路由器——PG 入口 get_depgraph_pg_connection() 与 SQLite 入口 get_db_connection() 是不同函数，调用方按需选择（见 AGENTS.md §11.4 真源冲突治本）
```

## 核心接口契约一览

| 契约 ID | 提供方 | 消费方 | 状态 |
|---------|--------|--------|:---:|
| CT-DB-001 | 012A TaskRepository | MOD-TASK_SYSTEM/009/013 | ✅ 已实现 |
| CT-DB-002 | 012A ATM | MOD-TASK_SYSTEM/010 | ✅ 已实现 |
| CT-DB-003 | 012A OLAPEngine | MOD-FEEDBACK_LOOP/015 | ✅ 已实现 |
| CT-DB-004 | 012A DatabaseManager | MOD-INF-015/001 | ✅ 已实现 |
| CT-DB-005 | 012B ScriptRegistry | MOD-TASK_SYSTEM/009/010 | ✅ 已由 _concurrency.ScriptRegistry 覆盖 |
| CT-DB-006 | 012B ScriptExecutionLogger | MOD-TASK_SYSTEM/020/010 | ⏸ 暂缓（待 M-1 级 500+脚本，当前 571 已达） |
| CT-DB-007 | 012B DualDBRouter | ALL modules | ❌ 已裁定删除（由 get_depgraph_pg_connection() PG + get_db_connection() SQLite 双入口覆盖） |

## 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 |
|---------|---------|---------|---------|
| MOD-TASK_SYSTEM | 必须 | task_repo.py——TaskCard 数据层真源 | v0.3+ |
| MOD-GATE_ENGINE | 必须 | GateEngine——门禁结果 SQLite 落盘消费方 | — |
| b_db.yaml | 必须 | DB YAML SSoT——本蓝图真源 | v2.2+ |
| MOD-FEEDBACK_LOOP | 可选 | FLE 消费 olap_engine | — |
| MOD-INF-020 | 可选 | 审计事件入库 | — |
| MOD-INF-015 | 可选 | query_metrics 等遥测读写 | — |

## 测试策略概览

| # | 测试覆盖 | 所属子蓝图 | 状态 |
|---|---------|:---:|:---:|
| 1 | task_repo CRUD + 状态机 | 012A | ✅ ~40+ 用例 |
| 2 | ATM 两阶段提交 + 幂等 | 012A | ✅ ~18+ 用例 |
| 3 | sqlite_schema 迁移幂等 | 012A | ✅ ~20+ 用例 |
| 4 | olap_engine 趋势查询 + 降级 | 012A | ✅ ~15+ 用例 |
| 5 | database_manager 运维 | 012A | ✅ 14 用例 |
| 6 | audit_schema 审计查询 | 012A | ✅ 8 用例 |
| 7 | query_metrics 性能监控 | 012A | ✅ 12 用例 |
| 8 | v3.0 DualDBRouter + WriteBatcher | 012B | ☐ 阶段3 SQL方言 + 阶段5 连接池 |
| 9 | 100 AI 并发压测 | 012B | ☐ 阶段6 红蓝测试 |

## 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 集成蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` | 本文件 |
| 子蓝图 P2 迁移 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\mod_inf_012b_p2_postgresql_migration.md` | P2 迁移方案 |
| 子蓝图 P3 优化 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\mod_inf_012b_p3_postgresql_optimization.md` | P3 优化方案 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\` | Python 源码（012A 13 个 .py 已实现；012B 待施工） |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\db\` | 单元测试 |
| 数据文件 | `D:\ZephyrAlpha\data/databases/governance.db` | 012A SQLite 主数据库（任务卡库，保持 SQLite 不迁移） |
| 数据文件 | `localhost:5432/depgraph`（PostgreSQL 16，连接配置 `config/.env.postgres`） | 012B 迁移目标库（SQLite→PostgreSQL，depgraph 全景图，28 表） |
| 备份目录 | `D:\ZephyrAlpha\data\backups\` | 自动备份文件（7天日备份 + 4周末备份） |
| 冷数据归档 | `D:\ZephyrAlpha\data\warehouse\` | Parquet 冷数据（events_YYYYMMDD.parquet） |

## 风险一览

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 所属子蓝图 |
|---|------|:---:|:---:|------|:---:|
| R01 | SQLite 单点故障 | 高 | P1 | 自动备份 + health_check 自动 failover | 012A |
| R10 | PostgreSQL 迁移短暂不可用 | 高 | P1 | 双写过渡期——PG + SQLite 并行写 1 周 | 012B |
| R14 | PG Windows 服务安装问题 | 中 | P1 | 图形化安装向导 + 预检脚本 | 012B |
| C03 | v3.0 迁移成本 | — | — | SQLite→PG 全量迁移 + 双写过渡期 | 012B |
| C04 | v3.0 新增运维 | — | — | PG Windows 服务监控和维护 | 012B |

> 完整风险矩阵见各子蓝图 §14。

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 新增 012B-P2/P3 条目（版本 4.0.1 已于 2026-06-27 更新） | DW-045 拆分 + P2/P3 细化 |
| 2 | DB YAML SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_db.yaml` | 同步 code 文件 + schema_version | SSoT 漂移修复 |
| 3 | 模块 ID 注册表 | `D:\ZephyrAlpha\architecture_model\module_id_registry.yaml` | 新增 MOD-INF-012A/012B-P2/P3 | 新模块 ID 注册 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链——旧引用找不到文件 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定 |
| 9 | **蓝图必须自包含** | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复** | 蓝图过厚，代码与蓝图不一致时以代码为准 |
| 14 | **临时时态内容执行完毕后从蓝图删除** | 历史残留误导 AI 执行已完成的迁移 |
| 15 | **蓝图内容拆分判定**——单章 > 3000 token 或涉及 > 3 个独立主题 → 拆分子节 | 信息过载，AI 无法精确定位 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

| # | 铁律 |
|---|------|
| 1 | 禁止蓝图阶段物理删除任何文件 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 |
| 3 | 物理删除只能在 stable 搬入阶段执行 |
| 4 | 物理删除必须人类确认 |
| 5 | "宁可慢，不可漏" |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 蓝图体系架构标准 | PS-STD-005 | 1.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_042_meta_rule_standard.yaml` | 三级金字塔 + belongs_to |
| 4 | 模块ID注册表 | — | — | `D:\ZephyrAlpha\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | DB YAML SSoT | — | 2.2.0 | `D:\ZephyrAlpha\architecture_model\layers\b_db.yaml` | DB YAML真源 |
| 6 | 子蓝图 P2 迁移 | MOD-DB_DEPGRAPH_PG | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\mod_inf_012b_p2_postgresql_migration.md` | P2 迁移方案真源 |
| 7 | 子蓝图 P3 优化 | MOD-DB_DEPGRAPH_OPT | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\mod_inf_012b_p3_postgresql_optimization.md` | P3 优化方案真源 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | `src/zephyr/infrastructure/db/` (13 .py) | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\` | Core 已实现源码 | 已实现 (012A) |
| 2 | `dual_db_router.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\dual_db_router.py` | ~~v3.0 双库路由~~ | ❌ 不新建（P2 完成，由 get_depgraph_pg_connection() + get_db_connection() 双入口覆盖） |
| 3 | `write_batcher.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\write_batcher.py` | v3.0 批量写入 | ⏸ 暂缓（待 L 级 5000+脚本） |
| 4 | `script_scheduler.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\script_scheduler.py` | ~~v3.0 Worker Pool~~ | ❌ 不新建（由 BulkheadExecutorV2 覆盖） |
| 5 | `pg_lock.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\pg_lock.py` | v3.0 PG Advisory Lock | 待施工 (012B 阶段3 SQL方言) |
| 6 | `fts5_index.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\fts5_index.py` | v3.0 FTS5 | 待施工 (012B 阶段3 SQL方言) |
| 7 | `data/databases/governance.db` | `D:\ZephyrAlpha\data/databases/governance.db` | 012A 任务卡库（保持SQLite） | 运行时生成 |
| 8 | `data/databases/depgraph.db` | `D:\ZephyrAlpha\data/databases/depgraph.db` | 012B 迁移目标库（SQLite→PostgreSQL） | 运行时生成 |
| 9 | `data/backups/` | `D:\ZephyrAlpha\data\backups\` | 备份目录 | 运行时生成 |
| 10 | `data/warehouse/` | `D:\ZephyrAlpha\data\warehouse\` | 冷归档 | 运行时生成 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 数据库——task_repo+sqlite_schema+ATM+olap_engine 均已实现（012A 完整）

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/infrastructure/db/atomic_transaction_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/audit_schema.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/base_repo.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/circuit_breaker_repo.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/circuit_breaker_types.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/database_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/gate_repo.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/olap_engine.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/query.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/query_metrics.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/task_repo.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/db/transition.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_task_repo_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_sqlite_schema_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_atomic_transaction_manager_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_olap_engine_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_database_manager_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_audit_schema_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_query_metrics_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/unit/test_circuit_breaker_unit.py` | ✅ 已实现 | 单元测试（含 circuit_breaker_repo） |
| `tests/unit/db/test_task_repo_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_sqlite_schema_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_atomic_transaction_manager_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_olap_engine_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_audit_schema_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_database_manager_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_query_metrics_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_circuit_breaker_repo_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_gate_repo.py` | ✅ 已实现 | DB 集成测试 |
| `tests/unit/db/test_dm400_stale_task_fix.py` | ✅ 已实现 | DB 集成测试 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
