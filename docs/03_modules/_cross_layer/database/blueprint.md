---
module_id: SH-DB-001
submodule_path: src/zephyr/infrastructure/db
title: "Database 集成蓝图 — 2库职责划分(SQLite治理+PG架构) + 三层冷热架构定位"
doc_type: blueprint
status: Active
version: "4.3.2"
layer: L1_foundation
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260519-001
date: "2026-07-07"
valid_from: "2026-05-19"
last_updated: "2026-07-07"
ttl: permanent
rule_form: structural
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
scope: global
stability: evolving
verifiability: automated
construction_progress: completed
actual_disk_path: "src/zephyr/governance/persistence/"
codification_level: L2
generation: 3
functional_domain: data
summary: "Database 集成蓝图——2个关系数据库职责划分：(1)governance.db(SQLite,治理运行时,15+表) (2)depgraph(PostgreSQL16,架构静态真源,28表)。market.duckdb(DuckDB业务时序)已于2026-07-05删除。三层冷热架构定位：Warm(DuckDB+Parquet)+Cold(E盘归档)为当前规范，Hot(Redis)/Feature Store/Event Store为P2未来蓝图(#ARCH-048门禁逻辑已废弃)。聚合 MOD-INF-012A(Core)和 MOD-INF-012B(PG迁移,P2已完成)。P3优化方案已归档删除(2026-06-30)。DW-045拆分完成，详细内容见子蓝图。"
tags: [database, db, sqlite, duckdb, atm, atomic-transaction, task-repo, olap, infrastructure, migration, self-healing, operational-excellence, dual-db-router, write-batcher, integration-blueprint]
priority: P1
runtime_plane: hot
child_modules:
  - {module_id: "MOD-INF-012A", title: "Database Core — SQLite+DuckDB 双引擎核心运营", status: "Active", construction_progress: "completed", path: "sub_blueprints/（012A 无独立蓝图文件，代码清单见本文档 §1.1）"}
  - {module_id: "MOD-DB_DEPGRAPH_PG", title: "P2 PostgreSQL迁移 — depgraph SQLite→PostgreSQL（Windows原生安装）", status: "Active", construction_progress: "completed", path: "sub_blueprints/mod_inf_012b_p2_postgresql_migration.md"}
depends_on:
  - {target: "MOD-TASK_SYSTEM", at: "§3.2.1", why: "task_system——TaskCard数据层真源"}
  - {target: "MOD-GATE_ENGINE", at: "§1", why: "GateEngine——门禁结果SQLite落盘消费方"}
  - {target: "architecture_model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——本蓝图真源"}
references:
  - {id: "PS-STD-001", at: "§2~§7", why: "frontmatter字段合法值"}
  - {id: "PS-STD-005", at: "§6", why: "蓝图归属与引用链——belongs_to字段定义"}
  - {id: "GOV-AI-001", at: "全篇", why: "AI自治权限注册——数据库操作权限边界"}
  - {id: "MOD-FEEDBACK_LOOP", at: "§2.1", why: "FLE 消费 olap_engine——集成关系"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计事件入库"}
  - {id: "MOD-INF-015", at: "全篇", why: "query_metrics 等遥测读写"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Database 集成蓝图 — SQLite+DuckDB 核心运营 + v3.0 PostgreSQL容量升级

> module_id: SH-DB-001 | version: 4.3.2 | status: Active | layer: cross_layer | belongs_to: MOD-MASTER_BLUEPRINT
> actual_disk_path: `src/zephyr/governance/persistence/` | generation: 3 | construction_progress: completed
> **DW-045 拆分完成**。详细内容见子蓝图。本文档为集成入口。

## 概述

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules SH-DB-001`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules SH-DB-001`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> 本蓝图为集成索引，012A 代码清单见本文档 §1.1，012B 施工方案见子蓝图 mod_inf_012b_p2_*

本蓝图是 Database 模块的集成入口——聚合两个子蓝图：
- **MOD-INF-012A Database Core**：SQLite+DuckDB 双引擎核心运营（13 个 .py 全部已实现，物理代码主位置 `src/zephyr/infrastructure/db/`）
- **MOD-INF-012B v3.0 Capacity Upgrade**：depgraph 使用 PostgreSQL（16/16 综合验证通过，5/5 红蓝测试 40并发写入验证通过，TC-PG-08/10 残留于 2026-06-29 清理完毕 4/4 验收）

核心职责：为 AI 治理框架提供结构化数据持久化与查询能力——8 张核心表、10 状态任务机、ATM 两阶段原子事务、OLAP 分析、冷热数据分层。v3.0 目标支持 40+ AI 并发写入 + PostgreSQL MVCC。

## 二库职责划分（2026-06-30 决策：原3库中 market.duckdb 已于2026-07-05删除）

> **决策依据**：单人开发+无实盘阶段。2个关系数据库各有硬需求，引擎选择需求驱动，合并代价远大于收益。统一入口 `DatabaseService` 封装引擎差异，AI只需记住一个类。
> **数据库清单真源**：[infrastructure_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)（INFRA-DB条目，含非关系库）

| # | 数据库 | 引擎 | infra_id | 职责 | 表数 | 集成度 | 引擎选择硬需求 |
|---|--------|------|----------|------|:----:|:------:|-------------|
| 1 | governance.db | SQLite | INFRA-DB-001 | **治理运行时**——TaskCard/事件/门禁/断路器/FLE指标 | 15+ | 18+处import(核心) | 嵌入式零部署、高频小事务、状态机CHECK约束 |
| 2 | depgraph | PostgreSQL 16 | INFRA-DB-003 | **架构静态真源**——nodes/edges/domains等28表，架构治理 | 28 | 架构真源 | 复杂关系查询、MVCC并发、架构图遍历 |

**不合并理由**（第一性原理）：
- SQLite→PostgreSQL：18+处import重写、TaskRepository核心类重写、SQL语法适配(?→%s, GLOB→SIMILAR TO)，代价极高
- 真源唯一：2库职责不重叠（治理运行时/架构静态），无同步需求
- 责任唯一：`DatabaseService`统一入口，引擎差异封装

### market.duckdb 已删除（见 ARCH-046 + ARCH-048 + ClickHouse 母蓝图）

> **market.duckdb（原 INFRA-DB-005）已于 2026-07-01 废弃，2026-07-05 删除**（见 ARCH-046 铁律3"删除即彻底删除"）。原 market_schema.py 同步删除（死代码）。原 8 表（tick_data/orders/positions/risk_snapshots/factor_values/backtest_results/backtest_trades/kline_3s）业务迁移至 ClickHouse c1_market，详见 [c1_market_clickhouse.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md)。
>
> **当前业务行情数据库真源**：[infrastructure_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) INFRA-DB-006（ClickHouse c1_market，status=connected）。统一入口：`DatabaseService.get_clickhouse_conn()`（readonly=1）。

## 三层冷热架构定位（当前:ClickHouse+DuckDB双引擎 | 未来蓝图:Redis/FeatureStore/CQRS——门禁逻辑不适用，见 #ARCH-048）

> ⚠️ **门禁逻辑不适用（#ARCH-048, 2026-07-05）**：本节原"需求门禁触发演进"逻辑已被母蓝图 MOD-ARCH-BIZDB §3.1 弃用，改为"硬性边界二元判定：能造现在就造"。Redis/EventStore 施工优先级降为 P2（待实盘需求触发）。ClickHouse 已于 2026-07-01 部署（INFRA-DB-006），不再受"AUM>200万"门禁约束。以下门禁表保留作为历史参考，**不作为当前施工依据**。

> **裁定依据**（不适用，见 #ARCH-048）：设计文档(数据架构.md v6.0)自身有门禁分级。当前单人+无实盘，Hot层(Redis)的<5ms推理需求(DD-11-01)不存在。降级为未来蓝图使当前规范与实现一致，AI不混淆，且不阻塞未来。

| 架构组件 | 蓝图定位 | 门禁触发条件 | 理由 |
|---------|:-------:|------------|------|
| **Warm层(DuckDB+Parquet)** | **当前规范** | — | DuckDB OLAP 内存模式（INFRA-DB-004）只读挂载 governance.db，回测/因子研究够用，DuckDB~100ms满足15秒延迟预算（原 market.duckdb 已于2026-07-01废弃，2026-07-05删除） |

> 📌 **Warm层业务行情OLAP暂缓决策（2026-07-13，用户裁定）**：业务行情数据的 DuckDB Warm 层暂不开发。理由：(1) **时间错开无冲突**——ClickHouse 写入在交易时段（9:30-15:30），回测在非交易时段，两者不重叠，不存在"互相拖累"问题；(2) **性能差距不显著**——单机同配置下 DuckDB 略快于 ClickHouse（嵌入式无网络开销），但都是列式+向量化引擎，回测场景体感差异不在数量级；(3) **存储成本**——若 DuckDB 导入副本会双倍存储，若直接读 Parquet 则依赖 Cold 层先归档（Cold 层当前亦暂缓）；(4) ClickHouse 在非交易时段跑回测完全够用。触发条件改为"**回测任务排队/ClickHouse查询明显变慢时再启动**"。
| **Cold层(E盘Parquet归档)** | **当前规范(架构预留)** | 交易≥7年合规(证监会) | 法律硬要求；当前无实盘数据但架构需预留，DuckDB直接ATTACH E盘Parquet，单引擎管理 |

> 📌 **Cold层施工暂缓决策（2026-07-13，用户裁定）**：当前 D盘 ClickHouse 存储充裕，Cold层暂不开发。触发条件改为"**D盘存储紧张时再启动**"（而非按固定时间表）。理由：(1) 数据增长速度可控，D盘容量短期内无压力；(2) ClickHouse 自带压缩，tick 数据压缩比高，实际占用远小于原始体积；(3) 合规7年要求是长期约束，当前无实盘交易数据，时间窗口充裕；(4) 届时再做归档迁移完全来得及，不阻塞业务。原"架构预留"定位保持不变，仅明确施工时机。
| **Hot层(Redis)** | **P2未来蓝图**（#ARCH-048降级） | **实盘交易触发** | 无实盘=无<5ms推理需求；Redis的<5ms需求来自盘中5000只×200因子推理(DD-11-01)，非Tick存储 |

> 📌 **Hot层(Redis)施工时机确认（2026-07-13，用户裁定）**：Redis 热层是实盘交易的命脉——盘中 tick 数据下载后需立即计算因子、汇总、做出买卖决策，<5ms 推理延迟是刚需。但当前无实盘，故暂不开发。触发条件保持"**实盘交易启动前开发**"。此为三层中相对最紧急项（因离实盘最近），但实盘未启动前不急。
| **Feature Store三件套** | **P2未来蓝图** | 因子>500触发 | 当前因子少，DuckDB表+视图替代；DD-11-01训练-推理双存储需求暂缓 |
| **Event Store CQRS** | **P2未来蓝图**（#ARCH-048降级） | 吸纳外部资金触发 | 单人阶段DuckDB INSERT ONLY表替代；DD-12-01事件溯源暂缓 |
| **ClickHouse升级** | **✅已部署（2026-07-01）** | ~~AUM>200万触发~~ 已解除 | DuckDB→ClickHouse已升级（INFRA-DB-006, c1_market数据库+daily_kline表已建），不再受门禁约束 |

**门禁触发后的升级路径**：
1. **实盘交易触发** → 启用Hot Redis层（盘中因子截面<5ms推理）
2. **因子>500触发** → 启用Feature Store（离线Parquet+在线Redis+Registry SQLite）
3. **吸纳外部资金触发** → 启用Event Store CQRS + E盘双副本（DD-07-04）
4. **AUM>200万触发** → DuckDB→ClickHouse升级（DD-07-01门禁）

## 子蓝图索引

| module_id | 标题 | 状态 | 施工进度 | 文件路径 |
|-----------|------|------|:---:|------|
| MOD-INF-012A | Database Core — SQLite+DuckDB 双引擎核心运营 | Active | completed | 012A 无独立蓝图文件，代码清单见本文档 §1.1 |
| MOD-DB_DEPGRAPH_PG | P2 PostgreSQL迁移 — depgraph SQLite→PostgreSQL（Windows原生安装） | Active | completed | [sub_blueprints/mod_inf_012b_p2_postgresql_migration.md](sub_blueprints/mod_inf_012b_p2_postgresql_migration.md) |

> **P3 PostgreSQL优化方案已归档删除**（2026-06-30）：原P3的4任务中T2/T3裁定删除（伪需求/过度工程），T1 pgvector改造待VMS自然演进，T4监控告警已实现（扩展verify_schema_health.py，实现记录见AGENTS.md §11.2）。P3历史文档已删除，避免Draft状态误导AI实现已裁定的伪需求。

> **depgraph Schema 变更门禁（DDL-as-Code 铁律执行入口，ARCH-016/017/018 治本）**：
> - **DDL 真源**：[depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py)（`_DDL_*` 声明 + `_MIGRATIONS` 版本链，DDL-as-Code 唯一真源，禁止只靠手动建表/改表）。
> - **门禁**：GATE-SCHEMA-HEALTH 已合并到 **GATE-C2**（run_gate_chain 顺序执行 check_contract_code_drift + check_contract_physical_path + verify_schema_health），`.pre-commit-config.yaml` commit 阶段自动触发（ARCH-017），--no-verify 绕不过 GitCommitGateway in-process gate。
> - **检测真源**：[verify_schema_health.py](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/verify_schema_health.py) 4 校验（DDL 列一致性/只读触发器/Schema 版本一致性/PG 运行时健康），capability=schema_health_verification。
> - **变更协议**：Schema 变更必须先改 `depgraph_schema.py` 的 `_DDL_*` / `_MIGRATIONS` → git commit 备份 → `apply_depgraph.py` 执行迁移 → verify_schema_health.py 校验通过。禁止直连 PG 手动 DDL。
> - **重定向锚点**：gate_registry.yaml 保留 GATE-SCHEMA-HEALTH 条目（status=deprecated, redirect_to=GATE-C2）供历史引用可追溯。

### 职责划分

| 子蓝图 | 覆盖内容 | 物理代码 |
|--------|---------|---------|
| MOD-INF-012A | SQLite WAL 事务引擎 / DuckDB OLAP / ATM v2.0 / TaskRepository 10状态机 / DatabaseManager 运维 / AuditSchema 审计查询 / QueryMetrics 性能监控 | `src/zephyr/infrastructure/db/` 13 个 .py（全部已实现；governance/ 根与 governance/persistence/ 存在过渡期副本） |
| MOD-DB_DEPGRAPH_PG | Windows原生安装 PostgreSQL / 数据迁移 / SQL 方言调整 / 删除文件锁 / 红蓝测试 | 见 P2 方案 §十二受影响文件索引 |

### AI 施工指引

- **读 Core 实现** → 本文档 §1.1——了解已实现的 SQLite+DuckDB 基础设施
- **施工 P2 迁移** → [mod_inf_012b_p2_postgresql_migration.md](sub_blueprints/mod_inf_012b_p2_postgresql_migration.md)——迁移设计 + 施工步骤 + 验收标准
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
| 14 | WriteBatcher | 012B | ⏸ 暂缓（待 L 级） | 批量写入缓冲——真问题但 L 级（5000+脚本）需求，当前 S 级 571 脚本无写争抢实证 |
| 15 | ScriptRegistry | 012B | ✅ 已覆盖 | 脚本注册表——已由 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py) ScriptRegistry 类覆盖（CT-DB-005 契约对齐） |
| 16 | ScriptExecutionLogger | 012B | ⏸ 暂缓（待 M-1 级） | 脚本执行日志——571 脚本已达 M-1 下限 500，纯新增低风险，待启动（CT-DB-006 契约） |

### 数据流概览

```
MOD-TASK_SYSTEM (task_system) ──→ TaskRepository ──→ events 表 ──→ OLAPEngine ──→ MOD-FEEDBACK_LOOP (FLE)
MOD-GATE_ENGINE (gate_engine) ──→ TaskRepository ──→ gates 表   ──→ AuditSchema ──→ MOD-INF-020 (audit)
v3.0: 脚本执行器 ──→ get_depgraph_pg_connection() ──→ depgraph (PostgreSQL)──→ script_executions 表（暂缓，待 M-1 级）
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
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\` | Python 源码（012A 13 个 .py 已实现；012B P2 已完成） |
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

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py SH-DB-001`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=SH-DB-001` 的 12 个 file 节点 | design | `extract_depgraph.py --modules SH-DB-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | SH-DB-001 | SH-DB-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 12 文件 | 27 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 新增 012B-P2 条目（版本 4.0.1 已于 2026-06-27 更新） | DW-045 拆分 + P2 细化 |
| 2 | DB YAML SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_db.yaml` | 同步 code 文件 + schema_version | SSoT 漂移修复 |
| 3 | 模块 ID 注册表 | `D:\ZephyrAlpha\architecture_model\module_id_registry.yaml` | 新增 MOD-INF-012A/012B-P2 | 新模块 ID 注册 |

---

## §decisiongraph 决策流图架构（TRAE-061，共库不同表）

> **本节归属**：数据库蓝图补充——decisiongraph 与 depgraph 共用同一 PostgreSQL 实例，表前缀不同（2026-07-06 新增）。
> 真源：[`decisiongraph_schema.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/decisiongraph_schema.py) + [`decision_graph_model.yaml`](file:///d:/ZephyrAlpha/architecture_model/domain/decision_graph_model.yaml)

### 共库关系

| 维度 | depgraph | decisiongraph |
|------|----------|---------------|
| PG 实例 | 同一个（localhost:5432） | 同一个 |
| 表前缀 | `nodes`/`edges`/`domains`... | `decision_tracks`/`decision_layers`/`decision_nodes`/`decision_edges` |
| 连接入口 | `get_depgraph_pg_connection()` | `get_decisiongraph_pg_connection()`（委托 depgraph，无独立配置） |
| 写锁 | `pg_advisory_lock(424242)` | `pg_advisory_lock(424244)` |
| YAML 真源 | 代码 AST 扫描 | `architecture_model/domain/decision_graph_model.yaml` |

### DDL 真源

- **文件**：`scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql`
- **Schema Python 真源**：`src/zephyr/governance/persistence/decisiongraph_schema.py`
- **变更协议**：Schema 变更先改 `decisiongraph_schema.py` + DDL 文件 → git commit → 执行 DDL → 校验。禁止直连 PG 手动 DDL。

### 初始数据

- `decision_tracks`：4 轨（model_driven/data_driven/human_override/emergency）
- `decision_layers`：10 层（L0-L6，含 L2A/B/C/D）
- `decision_nodes`/`decision_edges`：运行时由业务填充（回测适配器等）

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

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | `src/zephyr/infrastructure/db/` (13 .py) | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\` | Core 已实现源码 | 已实现 (012A) |
| 2 | `write_batcher.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\db\write_batcher.py` | v3.0 批量写入 | ⏸ 暂缓（待 L 级 5000+脚本） |
| 3 | `data/databases/governance.db` | `D:\ZephyrAlpha\data/databases/governance.db` | 012A 任务卡库（保持SQLite） | 运行时生成 |
| 4 | `depgraph (PostgreSQL)` | `localhost:5432/depgraph` | 012B 迁移结果库（SQLite→PostgreSQL，depgraph 全景图，28 表） | 运行时生成 |
| 5 | `data/backups/` | `D:\ZephyrAlpha\data\backups\` | 备份目录 | 运行时生成 |
| 6 | `data/warehouse/` | `D:\ZephyrAlpha\data\warehouse\` | 冷归档 | 运行时生成 |

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
| `src/zephyr/governance/persistence/database_service.py` | ✅ 已实现 | governance版DatabaseService（连接管理+健康检查，继承DatabaseCRUDMixin，P-PLAN-1双连接） |
| `src/zephyr/infrastructure/database_service.py` | ✅ 已实现 | infrastructure版DatabaseService（连接管理+ClickHouse+健康检查，继承DatabaseCRUDMixin，P-PLAN-2统一row_factory） |
| `src/zephyr/shared/database/database_crud_mixin.py` | ✅ 已实现 | DatabaseCRUDMixin（共享9个CRUD方法+_TASK_COLUMNS单一真源，被两个DatabaseService类继承，P-PLAN专项工程抽取消除约100行重复） |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_task_repo_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_sqlite_schema_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_atomic_transaction_manager_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_olap_engine_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_database_manager_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_audit_schema_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_query_metrics_unit.py` | ✅ 已实现 | 单元测试 |
| `tests/test_circuit_breaker_unit.py` | ✅ 已实现 | 单元测试（含 circuit_breaker_repo） |
| `tests/db/test_task_repo_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_sqlite_schema_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_atomic_transaction_manager_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_olap_engine_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_audit_schema_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_database_manager_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_query_metrics_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_circuit_breaker_repo_db.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_gate_repo.py` | ✅ 已实现 | DB 集成测试 |
| `tests/db/test_dm400_stale_task_fix.py` | ✅ 已实现 | DB 集成测试 |

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
