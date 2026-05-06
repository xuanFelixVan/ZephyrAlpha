---
module_id: "MOD-INF-012"
title: "Database 蓝图 — SQLite + DuckDB 双引擎元数据层 v2.2"
doc_type: blueprint
status: Draft
version: "2.2.0"
layer: cross_layer
blueprint_level: module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
rule_form: structural
belongs_to: "MOD-MASTER-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: phase_1_complete
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha Database 蓝图 v2.2——SQLite + DuckDB 双引擎元数据持久化。ATM v2.0：跨SQLite/文件系统的两阶段提交 + tx_idempotency幂等去重 + compensating_transaction补偿 + 事务超时控制。task_repo v2.0：ON CONFLICT upsert + 软删除 + JSON1查询。database_manager：连接池 + 健康检查 + 自动备份 + WAL checkpoint。olap_engine：Parquet冷热分层归档 + 统一查询。audit_schema + query_metrics：审计面板 + 慢查询监控。共7个.py文件，全部已实现。v2.2：蓝图模板全对齐——补全 §1.2 目标/§1.3 不包含/§2.1 职责范围/§2.2 不包含职责/§16 AI施工检查清单+回滚+完成标准/治理信息章（SSoT声明+Tiered消费者+变更同步+修改条件）/frontmatter 4 字段。"
tags: [database, db, sqlite, duckdb, atm, atomic-transaction, task-repo, olap, infrastructure, migration, self-healing, operational-excellence]
priority: P1
# DOC-009 / Phase7-DAG：depends_on 仅「设计先验」上游；SQLite 运行时消费者见 references。
depends_on:
  - {target: "MOD-INF-006", at: "§3.2.1", why: "task_repo.py——TaskCard数据层真源"}
  - {target: "MOD-INF-007", at: "§1", why: "GateEngine——门禁结果SQLite落盘消费方"}
  - {target: "architecture-model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——本蓝图真源"}
references:
  - {id: "PS-STD-001", at: "§2~§7", why: "frontmatter字段合法值"}
  - {id: "PS-STD-002", at: "§3.1~§3.2", why: "标准文档模板——蓝图层级章节集"}
  - {id: "PS-STD-005", at: "§6", why: "蓝图归属与引用链——belongs_to字段定义"}
  - {id: "GOV-AI-001", at: "全篇", why: "AI自治权限注册——数据库操作权限边界"}
  - {id: "MOD-INF-010", at: "§2.1", why: "FLE 消费 olap_engine——集成关系，下同"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计事件入库"}
  - {id: "MOD-INF-015", at: "全篇", why: "query_metrics 等遥测读写"}
---

# Database 蓝图 v2.2

> **module_id**: MOD-INF-012 | **version**: 2.2.0 | **status**: draft | **layer**: cross_layer | **belongs_to**: MOD-MASTER-001

> **真源声明**：本蓝图的 canonical SSoT 为 [b_db.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_db.yaml)。
> 代码落位：`src/zephyr/db/`（7 个 .py 文件）。v2.2 全部已实现。

> **对标**：SQLite WAL 模式 + ITIL SACM CMDB + 分布式事务两阶段提交模式 + DuckDB OLAP 冷热分层 + Google SRE 运维卓越 + Vibe Coding 自愈设计。

---

## ⚠️ 蓝图编写铁律自检

| # | 铁律 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 所有路径必须是绝对路径 | ✅ | §6 完整路径索引 |
| 2 | 必备链接不可省略 | ✅ | §0 必备链接 |
| 3 | 蓝图是最终设计结果 | ✅ | 不记录决策过程 |
| 4 | 产出物路径与 GOV-DOC-002 一致 | ✅ | 已对齐 |
| 5 | 涉及文件范围必须明确列出 | ✅ | §6 完整文件清单 |
| 6 | 容量估算必须写 | ✅ | §13 容量估算 |
| 7 | 迁移/废弃方案必须写 | ✅ | §11 迁移指南 |
| 8 | 禁止模糊词 | ✅ | 无"待定""建议"等 |
| 9 | 蓝图必须自包含 | ✅ | CT-DB-* 合同内嵌 |
| 10 | 安全删除协议 | ✅ | 无删除型变更 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射 |
| 3 | 蓝图体系架构标准 | PS-STD-005 | 1.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\blueprint-architecture-standard.md` | 三级金字塔 + belongs_to |
| 4 | 模块ID注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 编号注册 |
| 5 | ADR-0030 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0030-sqlite-task-metadata-store.md` | SQLite元数据层决策 |
| 6 | ADR-0041 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0041-session-handoff-protocol.md` | Session Handoff协议 |
| 7 | AI自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | AI操作权限 |
| 8 | DB YAML SSoT | — | 1.1.0 | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | DB YAML真源 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | ChromaDB (VMS) | `D:\ZephyrAlpha\src\zephyr\vector_memory\` | 向量数据持久化 | ChromaDB 管语义向量检索，SQLite 管结构化元数据——两者互补不重叠 |
| 2 | 脚本系统 run_all.py | `D:\ZephyrAlpha\scripts\run_all.py` | DB 完整性检查 | run_all.py 检查项目级一致性，database_manager.health_check() 检查 DB 物理完整性——互补 |
| 3 | MOD-INF-020 audit-trail | `D:\ZephyrAlpha\src\zephyr\audit_trail\` | 审计事件存储 | Audit Trail 消费 events 表做不可变日志链，本模块是 events 的生产者——上下游关系 |

> 无直接功能重叠，所有模块均为互补。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | `atomic_transaction_manager.py` | `D:\ZephyrAlpha\src\zephyr\db\atomic_transaction_manager.py` | 核心源码 | 已实现 |
| 2 | `olap_engine.py` | `D:\ZephyrAlpha\src\zephyr\db\olap_engine.py` | 核心源码 | 已实现 |
| 3 | `sqlite_schema.py` | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | 核心源码 | 已实现 |
| 4 | `task_repo.py` | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 核心源码 | 已实现 |
| 5 | `database_manager.py` | `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | 核心源码 | 已实现 |
| 6 | `audit_schema.py` | `D:\ZephyrAlpha\src\zephyr\db\audit_schema.py` | 核心源码 | 已实现 |
| 7 | `query_metrics.py` | `D:\ZephyrAlpha\src\zephyr\db\query_metrics.py` | 核心源码 | 已实现 |
| 8 | `zalpha_metadata.db` | `D:\ZephyrAlpha\docs\09_audit\state\zalpha_metadata.db` | 数据文件 | 运行时生成 |
| 9 | `data/backups/` | `D:\ZephyrAlpha\data\backups\` | 备份目录 | 运行时生成 |
| 10 | `data/warehouse/` | `D:\ZephyrAlpha\data\warehouse\` | 冷数据归档 | 运行时生成 |

---

## 1. 概述

### 1.1 设计背景

> **根因**：ZephyrAlpha 是一个基于状态机驱动、任务流编排的 AI 施工系统。TaskCard 模型是整个系统的核心数据结构（需求→任务→实现→交付）。没有可靠的持久化层，所有状态机、门禁、审计都是空中楼阁。SQLite 零运维、WAL 并发、DuckDB OLAP 冷热分层形成双引擎架构。

| 维度 | 设计决策 | 替代方案 | 选择理由 |
|------|---------|---------|---------|
| 元数据存储 | SQLite 3.x WAL 模式 | PostgreSQL → 有运维负担，不适合 1 人项目 | 零运维、单文件备份、WAL 读写并发 |
| OLAP 分析 | DuckDB（嵌入式） | ClickHouse → 需要独立部署 | DuckDB 零配置、嵌入式、Parquet 原生支持 |
| 原子事务 | ATM v2.0 两阶段提交 | 2PC 经典模式 | 跨 SQLite/文件系统保证原子性——既写 DB 又写文件时不能半成功 |
| 版本化迁移 | 内嵌 _MIGRATIONS 注册表 | Alembic → 过度工程 | 项目规模用 SQL 内联即可，无需引入 ORM 迁移工具链 |
| 备份策略 | SQLite backup API（非 cp） | pg_dump / S3 | 使用 SQLite 内置 API 保证备份一致性 |

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 所有 TaskCard CRUD < 50ms（含状态转换 + events 写入） | 4 份测试覆盖 + query_metrics P95 < 50ms |
| 2 | 跨 SQLite/文件系统原子事务零不一致 | ATM execute 全部路径有测试覆盖 + 补偿事件链路完整 |
| 3 | DB 单点故障 5 分钟内自动恢复 | 健康检查自动检测 + 最新备份自动恢复（待 T-DB-005） |
| 4 | events 表永不超过 30 天热数据（冷热分层） | archive_events 每次执行后 events 表行数 ≤ 阈值 |
| 5 | AI Agent 可零上下文消费 DB 诊断信息 | ai_diagnostic_report() 返回结构化 dict，含 verdict + action |
| 6 | init_db() 幂等——任意环境可重复执行 | 多次执行不报错、不丢数据、迁移按序执行未运行的 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 分布式事务（跨多机器） | 1 人单机本地部署，不需要 3PC 或 Paxos |
| 2 | 实时 CDC 变更流（Kafka/Redpanda） | events 表即天然 CDC——需要 event-driven 消费时直接查 events 表 |
| 3 | ORM 层（SQLAlchemy） | 增加依赖链和故障面——原生 sqlite3 + DuckDB 即可 |
| 4 | 数据库集群/主从复制 | 1 人项目，SQLite 单文件 + 自动备份足够 |
| 5 | 在线备份（Litestream S3 流式复制） | 当前 DB < 10MB，停机备份 < 5s——待 DB > 100MB 再引入（见 §19 #3） |
| 6 | 全文搜索引擎集成（Elasticsearch） | 任务量级不匹配——SQLite FTS5 就够用（见 T-DB-010） |
| 7 | 时序数据库（InfluxDB/TimescaleDB） | OLAP engine 的 DuckDB + Parquet 已满足时序分析需求 |

---

## 2. 模块边界

### 2.1 职责范围

| # | 职责 | 说明 | 落位 |
|---|------|------|------|
| 1 | TaskCard 元数据 CRUD | 任务的创建/读取/更新/删除/软删除/状态转换 | `task_repo.py` |
| 2 | 状态机引擎 | 10 状态转换 + G1 门禁在写事务内执行 | `task_repo.py` transition() |
| 3 | 原子事务保证 | 跨 SQLite/文件系统两阶段提交 + 幂等去重 + 补偿 | `atomic_transaction_manager.py` |
| 4 | 版本化 Schema 管理 | DDL 定义 + _MIGRATIONS 注册表 + init_db() 幂等迁移 | `sqlite_schema.py` |
| 5 | OLAP 时序分析 | 趋势查询 + 聚合计算 + 摘要统计 | `olap_engine.py` |
| 6 | 冷热数据分层 | events 表定期归档到 Parquet + 统一查询 UNION ALL | `olap_engine.py` archive_events() |
| 7 | 连接与运维管理 | 连接池 + 健康检查 + 自动备份 + WAL checkpoint + 统计 | `database_manager.py` |
| 8 | 审计查询面板 | AuditQuery 视图 + 补偿事件查询 + Schema 漂移检测 | `audit_schema.py` |
| 9 | 查询性能监控 | P50/P95/P99 延迟统计 + slow_queries 记录 | `query_metrics.py` |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 | 为什么 |
|---|--------|---------|------|
| 1 | 任务调度与分派 | MOD-INF-006 (task-system) + MOD-INF-009 (pipeline) | 数据库只管"存和查"，不管"什么时候跑" |
| 2 | 门禁规则定义与评估 | MOD-INF-007 (gate-engine) | task_repo.transition() 调用 GateEngine.evaluate()，门禁逻辑在 gate-engine |
| 3 | FLE 时序指标定义 | MOD-INF-010 (feedback-loop) | FLE 产出数据落库，指标语义由 FLE 定义 |
| 4 | 向量化检索 | MOD-INF-011 (vector-memory / ChromaDB) | 语义检索用 ChromaDB，SQLite 管结构化元数据 |
| 5 | 上下文构建注入 | MOD-INF-008 (context-engine) | CE 构建 prompt 上下文，需要查 DB 时走 task_repo |
| 6 | 审计事件语义解析 | MOD-INF-020 (audit-trail) | 审计链不可变存储由 audit-trail 管，本模块是 events 的生产方 |
| 7 | 监控 Dashboard 渲染 | MOD-INF-015 (system-telemetry) | query_metrics 产出指标数据，可视化由 telemetry 负责 |
| 8 | LLM Prompt/响应管理 | MOD-INF-014 (llm-security) | LLM 安全审计独立于元数据层 |

### 2.3 文件组成

| 文件 | 职责 |
|------|------|
| `task_repo.py` | 任务 CRUD + 10状态机 + N:N task_files + ON CONFLICT upsert + 软删除 + JSON1查询 |
| `atomic_transaction_manager.py` | ATM v2.0——跨 SQLite/文件系统两阶段提交 + tx_idempotency + compensating_transaction |
| `sqlite_schema.py` | SQLite 表结构定义（DDL）+ 版本化迁移框架（v1–v8） |
| `olap_engine.py` | DuckDB OLAP 分析引擎 + Parquet 冷热分层归档 + 统一查询 |
| `database_manager.py` | 连接池/健康检查/自动备份/WAL checkpoint |
| `audit_schema.py` | 审计视图与查询入口（CLI 审计面板 / compliance 报告） |
| `query_metrics.py` | SQL 查询性能监控（P50/P95/P99 + slow_queries 表） |

---

## 3. ATM v2.0 原子事务管理器

```yaml
atm_contract: P0-DB-ATM-v2
description: "跨 SQLite / 文件系统的两阶段提交（v2.0 增强）"

version: "2.0.0"

phase_1_prepare:
  - 所有参与者（SQLite + 文件系统操作）进入 PREPARE 状态
  - 在 tx_idempotency 表登记为 PREPARED（防止重复提交）
  - 任何参与者 PREPARE 失败 → 全部 ROLLBACK + 标记 ROLLED_BACK

phase_2_commit:
  - 预验证所有 tmp 文件存在且可读
  - SQLite COMMIT
  - 对所有 staged 文件执行 os.replace(tmp, target)
  - 更新 tx_idempotency 为 COMMITTED
  - 文件 rename 失败但 SQLite 已 COMMIT → 写 compensation event + 标记 COMPENSATED

timeout: 30s（事务级，超时自动 ROLLBACK）
idempotency: tx_idempotency 表去重，同一 tx_id 重复调用 commit() 会报 TransactionError
fallback: WAL 模式自动回退 → 不丢数据
```

---

## 4. task_repo.py v2.0 核心接口

```python
class TaskRepo:
    # CRUD
    def create(task: TaskCard) -> TaskCard
    def get(task_id: str) -> Optional[TaskCard]
    def update(task_id: str, updates: dict) -> TaskCard
    def upsert(task: TaskCard) -> TaskCard  # ON CONFLICT DO UPDATE（保留 created_at）
    def delete(task_id: str) -> bool  # 软删除（is_deleted=1）
    def hard_delete(task_id: str) -> bool  # 物理删除（仅限数据清理脚本）

    # 状态转换
    def transition(task_id: str, to_status: Status) -> TaskCard  # G1 门禁在写事务内执行

    # 查询
    def list_by_status(status: Status) -> list[TaskCard]   # 过滤 is_deleted=0
    def list_by_phase(phase: int) -> list[TaskCard]
    def list_by_session(session_id: str) -> list[TaskCard]
    def list_by_namespace(namespace) -> list[TaskCard]
    def list_active() -> list[TaskCard]

    # JSON1 查询
    def list_by_dependency(dependency_task_id: str) -> list[TaskCard]
    def list_by_tag(tag: str) -> list[TaskCard]
    def list_by_blocked_by(blocker_task_id: str) -> list[TaskCard]
```

状态转换时自动写入 events 表（不可变审计日志）。GateEngine 的 evaluate() 接受外部 conn 参数，门禁结果与状态转换在同一事务中原子落盘。

---

## 5. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | task_repo.py + sqlite_schema.py + ATM | ✅ implemented |
| v2.0 | database_manager + audit_schema + query_metrics + 软删除 + JSON1 + Parquet归档 | ✅ implemented |

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/db/atomic_transaction_manager.py` | ✅ v2.0 | ATM + tx_idempotency + compensation |
| `src/zephyr/db/olap_engine.py` | ✅ v2.0 | duckdb + Parquet 归档 + 统一查询 |
| `src/zephyr/db/sqlite_schema.py` | ✅ v2.0 | v1–v8 版本化迁移框架 |
| `src/zephyr/db/task_repo.py` | ✅ v2.0 | 软删除 + ON CONFLICT + JSON1 |
| `src/zephyr/db/database_manager.py` | ✅ 新增 | 连接池 + 备份 + WAL checkpoint |
| `src/zephyr/db/audit_schema.py` | ✅ 新增 | 审计视图 + 查询入口 |
| `src/zephyr/db/query_metrics.py` | ✅ 新增 | 性能监控 + slow_queries |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_task_repo.py` | ✅ 已实现 | |
| `tests/unit/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/unit/test_atomic_transaction_manager.py` | ✅ 已实现 | |
| `tests/unit/test_olap_engine.py` | ✅ 已实现 | |

### 6.3 数据目录

| 路径 | 用途 |
|------|------|
| `docs/09_audit/state/zalpha_metadata.db` | SQLite 主数据库 |
| `data/backups/` | 自动备份文件（保留最近 7 天 + 4 周末） |
| `data/warehouse/` | Parquet 冷数据归档（events_YYYYMMDD.parquet） |

---

## 7. 集成目标（v2.1 补全）

| # | 项目 | 深度 | 落位 |
|---|------|:---:|------|
| 1 | task-system | P1 | task_repo.py → 状态机 + 审计互锁 |
| 2 | pipeline | P1 | task_repo.py → status 驱动的决策 |
| 3 | mcp-servers | P1 | task_repo.py + ATM session handoff |
| 4 | feedback-loop | P1 | olap_engine.py → 趋势分析 + report 产出 |
| 5 | system-telemetry | P1 | database_manager.py → stats 面板 |
| 6 | audit-trail | P1 | audit_schema.py→AuditQuery + 补偿事件 |
| 7 | gate-engine | P1 | gates 表 + events 表共享写入 |
| 8 | capacity-assurance | P1 | database_manager.health_check() |

---

## 8. 需要更新的相关内容（v2.1 补全）

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号 2.1.0 + 完整度 95% + status phase_1_complete | v2.1 盲点补全 |
| 2 | DB YAML SSoT | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | 补全 3 个缺失 .py + 更新 schema_version + 修正 db_file_path | SSoT 漂移修复（§17） |
| 3 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | DB 模块状态 active | 代码施工完成 |
| 4 | ADR-0030 | ADR-0030 | 更新连接管理/备份策略引用 | v2.0 新增 database_manager |
| 5 | AI 自治权限注册表 | GOV-AI-001 | 注册 MOD-INF-012 的 AI 操作权限边界 | blueprint 新增 belongs_to + references 链 |

---

## 9. 已知风险与缓解

> ⚠️ **已迁至 §20**——风险矩阵在 §20 完整重建（13 条），本条保留仅作审计历史。

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| R1 | SQLite WAL mode 并发写入冲突 | 中 | 高 | WAL mode + 5s 重试 + 写入队列 → 详见 §20.R01 |
| R2 | 数据库文件损坏 | 低 | 高 | 定期 checkpoint + integrity_check + 备份 → 详见 §20.R01 |
| R3 | ATM rename 失败致不一致 | 低 | 中 | compensating_transaction + bak 回滚 → 详见 §20.R01 |
| R4 | 大量任务列表查询变慢 | 中 | 中 | 索引 + 分页 + query_metrics → 详见 §20.R05 |
| R5 | WAL 无限增长 | 中 | 高 | wal_autocheckpoint + TRUNCATE + VACUUM → 详见 §20.R02 |
| R6 | events 表行数线性恶化 | 高 | 中 | Parquet 冷热分层 → 详见 §20.R01/§13.1 |
| R7 | 事务超时后持有写锁 | 低 | 高 | 30s timeout + BEGIN IMMEDIATE → 详见 §20.R07 |

---

## 10. 后果（Consequences）

**正面后果**：
- **统一数据持久化**——所有模块通过 task_repo/olap_engine/audit_schema 访问数据
- **ATM v2.0 原子事务**——跨 SQLite+文件系统操作的一致性保证 + 幂等去重 + 补偿
- **可丢弃数据库**——自动备份 + WAL checkpoint，30 秒恢复全量
- **自诊断能力**——health_check + query_metrics 让 AI agent 可自行检测数据库健康状态
- **冷热分层**——SQLite 30 天热数据 + Parquet 永久归档，不受单表行数限制

**负面后果**：
- SQLite 单文件限制——数据库文件上限约 281TB（实际远不会达到）
- 引入事务管理复杂度——ATM v2.0 增加到 4 个状态（PREPARED/COMMITTED/ROLLED_BACK/COMPENSATED）
- 数据库迁移成本——未来如需切换到 PostgreSQL 需全量迁移

---

## 11. v2.0 迁移指南

### 11.1 已有数据库升级

从 v1.x（旧 schema）升级到 v2.0 的数据库只需调用 `init_db()` 即可自动检测并补齐缺失的迁移版本。

```python
from zephyr.db.sqlite_schema import init_db, schema_version

init_db()  # 幂等——自动检测 legacy DB 并运行 v7、v8 迁移
print(schema_version())  # 应输出 8
```

### 11.2 新增依赖

| 包 | 用途 | 是否必需 |
|----|------|:---:|
| `pyarrow` | events Parquet 归档 | 可选（仅 archive_events 调用时） |
| `duckdb` | OLAP 引擎 | 已有依赖 |

---

## 12. 接口契约（Interface Contracts）

> 对标 PS-STD-005 §5.2 禁止行为——CT-* 合同定义在模块蓝图中（1 人项目简化版），beta+ 迁移到域蓝图。

### CT-DB-001：task_repo CRUD 契约

```yaml
contract_id: CT-DB-001
provider: MOD-INF-012 (TaskRepository)
consumers:
  - MOD-INF-006 (task-system)
  - MOD-INF-009 (pipeline)
  - MOD-INF-013 (mcp-servers)

operations:
  create:
    input: "Task (Pydantic V2, 52 fields)"
    output: "TaskCard"
    errors: [P0InflationFrozenError, P0InflationWarning, sqlite3.IntegrityError]
    idempotency: "task_id UNIQUE 约束——重复创建抛 IntegrityError"

  get:
    input: "task_id: str"
    output: "TaskCard | None"
    filter: "is_deleted = 0（自动过滤软删除行）"
    
  transition:
    input: "task_id + to_status: TaskStatus + session_id?"
    output: "TaskCard"
    errors: [TaskNotFoundError, InvalidTransitionError, GateViolationError]
    atomicity: "G1门禁 + 状态写入 + events 写入在同一写事务内"
    state_machine: "10状态机——§4 转换表"

  upsert:
    input: "Task + files?"
    output: "TaskCard"
    semantics: "ON CONFLICT DO UPDATE——保留 created_at，覆盖其他字段"

  delete:
    input: "task_id: str"
    output: "bool"
    semantics: "软删除——设置 is_deleted=1 + deleted_at"

  list_by_*:
    input: "filter params"
    output: "list[TaskCard]"
    filter: "is_deleted = 0（自动排除软删除行）"
    supported_filters: [status, phase, session_id, namespace, dependency, tag, blocked_by]
```

### CT-DB-002：ATM 事务契约

```yaml
contract_id: CT-DB-002
provider: MOD-INF-012 (AtomicTransactionManager)
consumers:
  - MOD-INF-006 (task-system)
  - MOD-INF-010 (feedback-loop)

operations:
  transaction:
    isolation: "BEGIN IMMEDIATE（防写锁饥饿）"
    timeout: "30s 事务级超时——超时自动 ROLLBACK"
    idempotency: "tx_idempotency 表去重——重复 tx_id → TransactionError"
    compensation: "SQLite COMMIT 成功但文件 rename 失败 → compensation event + COMPENSATED 状态"

  write_file:
    safety: "InputSanitizer.validate_path（路径穿越防护）"
    atomicity: "tmp → fsync → os.replace（崩溃安全）"
    rollback: ".bak 文件恢复"
```

### CT-DB-003：OLAP 查询契约

```yaml
contract_id: CT-DB-003
provider: MOD-INF-012 (OLAPEngine)
consumers:
  - MOD-INF-010 (feedback-loop)
  - MOD-INF-015 (system-telemetry)

operations:
  task_progress_trend:
    input: "period: day|week|month, limit: 1-10000, phase?: int"
    output: "list[TrendRow]"
    sql_injection_protection: "参数化查询 + period白名单 + limit范围校验"

  compliance_rate_trend:
    input: "period, limit, gate_id?: str"
    output: "list[TrendRow]"
    
  knowledge_activation_trend:
    input: "period, limit, category?: str"
    output: "list[TrendRow]"

  archive_events:
    input: "days: int (默认30), archive_dir?: Path"
    output: "{archived_count, archive_files, deleted_count}"
    guarantee: "DuckDB 读取 → Parquet 写入 → SQLite DELETE 三步"

  query_unified_events:
    input: "limit: int"
    output: "list[TrendRow]"
    semantics: "UNION ALL (SQLite热数据 + Parquet冷数据)"
```

### CT-DB-004：运维管理契约

```yaml
contract_id: CT-DB-004
provider: MOD-INF-012 (DatabaseManager)
consumers:
  - MOD-INF-015 (system-telemetry)
  - MOD-INF-001 (capacity-assurance)

operations:
  health_check:
    output: "HealthStatus {healthy, schema_version, db_size_bytes, wal_size_bytes, table_count, integrity_ok}"
    checks: [integrity_check, quick_check, 文件大小, schema版本, 表数量]

  backup:
    input: "label?: str"
    output: "Path (备份文件路径)"
    consistency: "SQLite backup API（非 cp）"
    retention: "7天日备份 + 4周末备份"

  maintenance:
    output: "{vacuum, integrity, wal_truncated, pre_health, post_health}"
    schedule: "cron 每周触发"

  stats:
    output: "{task_count, active_task_count, event_count, gate_count, ke_count, slow_query_count, db_size_mb, wal_size_mb, schema_version}"
```

---

## 13. 容量估算

> ⚠️ 蓝图铁律#6：容量估算必须写。

### 13.1 存储容量

| 维度 | 当前规模 | 1年后估算 | 3年后估算 | 上限 |
|------|:---:|:---:|:---:|------|
| tasks 表行数 | ~200 | ~2,000 | ~10,000 | 无硬上限（SQLite 单表 ~2B 行理论值） |
| events 表行数 | ~500 | ~5,000 | ~50,000 | 冷热分层（30天热 + Parquet永久） |
| knowledge 表行数 | ~50 | ~500 | ~2,000 | 无硬上限 |
| DB 文件大小 | ~5 MB | ~50 MB | ~200 MB | SQLite 单文件 ~281 TB（实际远不会达到） |
| WAL 文件大小 | ~2 MB | ~10 MB | ~20 MB | wal_autocheckpoint=4096 自动截断 |
| Parquet 归档 | 0 | ~50 MB | ~500 MB | 磁盘容量限制 |
| 备份文件 | ~35 MB (7天) | ~350 MB | ~1.4 GB | 自动轮转清理 |

### 13.2 并发容量

| 维度 | 设计值 | 瓶颈 | 缓解 |
|------|:---:|------|------|
| 并发写连接 | 1（单Writer假设） | SQLite WAL 写锁 | ATM 锁串行化 + 5s busy_timeout 重试 |
| 并发读连接 | 10+ | 无（WAL 读不阻塞） | 当前 1 人+AI 远未触及 |
| 连接池大小 | 2 | 池耗尽时创建临时连接 | 临时连接用后即关 |
| 事务超时 | 30s | 超时自动 ROLLBACK | tx_timeout 可配置 |
| 慢查询阈值 | 500ms | 超过写入 slow_queries 告警 | query_metrics 监控 |

### 13.3 性能基线

| 操作 | 目标延迟 | 降级阈值 | 说明 |
|------|:---:|:---:|------|
| task_repo.get() | < 5ms | > 100ms | 主键查询 |
| task_repo.create() | < 20ms | > 500ms | 含写事务 + events 写入 |
| task_repo.transition() | < 50ms | > 500ms | 含门禁评估 + events |
| ATM transaction (无文件) | < 50ms | > 1s | SQL-only |
| ATM transaction (+3文件) | < 200ms | > 2s | 含文件 fsync |
| OLAP 趋势查询 | < 500ms | > 5s | 聚合查询 |
| health_check | < 100ms | > 1s | 完整性扫描 |
| backup | < 5s | > 30s | 取决于 DB 大小 |
| VACUUM | < 10s | > 60s | 全表重写 |

---

## 14. 消费者注册表

> 谁依赖本模块的哪些接口？改了本模块要通知谁？

| # | 消费者模块 | module_id | 消费接口 | 消费方式 | 变更影响 |
|---|-----------|-----------|---------|---------|---------|
| 1 | 任务系统 | MOD-INF-006 | TaskRepository (CRUD + 状态机) | `task_repo.py` 直接调用 | 接口签名变更 → TaskCard 读写断裂 |
| 2 | Pipeline 路由器 | MOD-INF-009 | TaskRepository (list_by_*) | 通过 MOD-INF-006 间接消费 | 查询字段变更 → 路由匹配失败 |
| 3 | MCP Servers | MOD-INF-013 | TaskRepository (decompose→create) | MCP Tool 内部调用 | create 参数变更 → MCP Tool 报错 |
| 4 | Feedback Loop | MOD-INF-010 | OLAPEngine (3 trend APIs) + ATM (write_file) | `olap_engine.py` + `atomic_transaction_manager.py` | 趋势查询 schema 变更 → Dashboard 断裂 |
| 5 | Audit Trail | MOD-INF-020 | events 表 (只读) + AuditQuery | `audit_schema.py` 直接查询 | events 表结构变更 → 审计链断裂 |
| 6 | System Telemetry | MOD-INF-015 | DatabaseManager.stats() + QueryMetrics | `database_manager.py` stats | stats 字段变更 → 监控面板断裂 |
| 7 | Capacity Assurance | MOD-INF-001 | DatabaseManager.health_check() | 健康检查 API | health status 结构变更 → 容量告警误判 |
| 8 | Gate Engine | MOD-INF-007 | gates 表 + events 表 (写入) | `gate_engine.py` 直接写 SQLite | DDL 变更 → 门禁记录丢失 |
| 9 | Shared + Core | MOD-INF-016 | TaskCard 模型定义 | `shared/schemas.py` 定义 Task 基座 | Task 模型变更 → 全系统 cascade |

---

## 15. 测试覆盖矩阵

| 被测模块 | 测试文件 | 测试数量 | 覆盖维度 | 缺口 |
|---------|---------|:---:|------|------|
| `task_repo.py` | `tests/unit/test_task_repo.py` | ~40+ | CRUD + 状态机 + 事件 + 查询 + task_files + upsert + 并发读 | ✅ 覆盖充分 |
| `sqlite_schema.py` | `tests/unit/test_sqlite_schema.py` | ~20+ | init_db 幂等 + 表/视图/索引 + PRAGMA + CHECK约束 + 外键 + 迁移幂等 | ✅ 覆盖充分 |
| `atomic_transaction_manager.py` | `tests/unit/test_atomic_transaction_manager.py` | ~18+ | 构造 + execute + write_file + commit + rollback + 嵌套禁止 + 关闭 + 路径校验 | ✅ 覆盖充分 |
| `olap_engine.py` | `tests/unit/test_olap_engine.py` | ~15+ | 初始化 + 参数校验 + 趋势查询 + 摘要 + 降级模式 | ✅ 覆盖充分 |
| `database_manager.py` | ❌ 缺失 | 0 | 连接池 + 健康检查 + 备份 + WAL checkpoint + 维护 + 统计 + 单例 + 关闭 | ❌ **P1缺口——运维核心零测试** |
| `audit_schema.py` | ❌ 缺失 | 0 | AuditQuery + 补偿事件 + Schema漂移 + 任务状态历史 + Session审计 | ❌ **P1缺口——审计查询零测试** |
| `query_metrics.py` | ❌ 缺失 | 0 | PercentileTracker + QueryMetrics.track + execute + stats + slow_query + 单例 | ❌ **P2缺口——性能监控零测试** |

> **施工优先级**：先补 `test_database_manager.py`（P1——备份/恢复是运维命脉），再补 `test_audit_schema.py`（P1——审计合规底线），最后补 `test_query_metrics.py`（P2——监控增强）。

---

## 16. 施工指引

### 16.1 AI 施工前检查清单

> ⚠️ AI 施工者**必须**在开始施工前逐项确认。任何一项为 ❌ 都**不得**开始施工。

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（§1-§19 架构 + §20 风险） | 逐节确认 | ☐ |
| 2 | 已读取 b_db.yaml SSoT（版本 v2.1.0、7 文件清单） | 打开 `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | ☐ |
| 3 | 已读取 ADR-0030（SQLite 元数据层决策） | 打开 ADR-0030 | ☐ |
| 4 | 已读取 PS-STD-005 §6（belongs_to: MOD-MASTER-001） | 确认蓝图归属 | ☐ |
| 5 | 每个施工步骤都对应蓝图 §12 接口契约 CT-DB-001~004 | 逐步骤追溯 | ☐ |
| 6 | 已确认磁盘实际有 7 个 .py 文件（`src/zephyr/db/*.py`） | glob 验证 | ☐ |

### 16.2 施工策略

| 项目 | 内容 |
|------|------|
| Phase 划分 | 1 个 scaffold（已完成）+ 1 个 v2.0 升级（已完成）+ experimental 待施工（T-DB-001~011） |
| 施工模式 | 既有模块增强——不新建文件，只补测试和增量功能 |
| 核心风险 | 补测试时可能发现既有代码的 bug——需要回滚方案 |

### 16.3 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 7 个 .py 源文件已在 `src/zephyr/db/` 就绪 | hard | ✅ | ✅ |
| 2 | b_db.yaml SSoT 已同步至 v2.1.0 | hard | ✅ | ✅ |
| 3 | 蓝图注册表已更新至 v2.1.0/95%/phase_1_complete | soft | ✅ | ✅ |
| 4 | 蓝图 §12 接口契约 CT-DB-001~004 已定义 | hard | ✅ | ✅ |

### 16.4 待施工任务

| # | 任务 | 优先级 | 预估工时 | 依赖 |
|---|------|:---:|:---:|------|
| T-DB-001 | 补全 `test_database_manager.py`——连接池/健康检查/备份/恢复/WAL checkpoint | P1 | 2h | 无 |
| T-DB-002 | 补全 `test_audit_schema.py`——AuditQuery/补偿事件/Schema漂移检测 | P1 | 1.5h | 无 |
| T-DB-003 | 补全 `test_query_metrics.py`——PercentileTracker/track装饰器/slow_query/单例 | P2 | 1h | 无 |
| T-DB-004 | 修复 b_db.yaml SSoT 漂移——增补3个缺失文件(database_manager/audit_schema/query_metrics) | P1 | 0.5h | 无 |
| T-DB-005 | `database_manager` 增加 `verify_backup()`——定期测试恢复能力 | P2 | 1h | T-DB-001 |
| T-DB-006 | `database_manager` 增加 `dead_letter_queue`——失败的写入入队重试 | P2 | 2h | 无 |
| T-DB-007 | `query_metrics` 增加 `EXPLAIN QUERY PLAN` 记录——用于慢查询优化 | P2 | 1h | 无 |
| T-DB-008 | `sqlite_schema` 增加 `migration_dry_run`——迁移预览模式（不实际执行） | P2 | 1h | 无 |
| T-DB-009 | `database_manager` 增加 Prometheus/OpenTelemetry metrics 导出 | P2 | 2h | MOD-INF-015 |
| T-DB-010 | `task_repo` 增加 FTS5 全文搜索——任务描述/标题搜索 | P3 | 3h | 无 |
| T-DB-011 | `database_manager` 增加 `connection_leak_detector`——检测未归还的连接 | P2 | 1.5h | 无 |

### 16.5 施工顺序

```
Phase scaffold (当前: ✅ 已完成)
  └── 7 个 .py 文件全部实现 + 4 份测试

Phase experimental (待施工: T-DB-001~004)
  ├── T-DB-004: SSoT 修复（已修复——v2.1 蓝图审计）
  ├── T-DB-001: database_manager 测试（运维底线）
  └── T-DB-002: audit_schema 测试（审计底线）

Phase beta (增强: T-DB-005~011)
  ├── T-DB-005: 备份验证
  ├── T-DB-006: 死信队列
  ├── T-DB-007: 查询计划分析
  ├── T-DB-008: 迁移预览
  ├── T-DB-009: Metrics 导出
  ├── T-DB-011: 连接泄漏检测
  └── T-DB-010: FTS5 搜索

Phase stable (生产就绪)
  └── 全量测试 + 备份恢复演练 + 故障注入测试
```

### 16.6 回滚方案

> ⚠️ 每个步骤如果出问题，**必须**有明确的回滚操作。

| 任务 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| T-DB-001 (database_manager 测试) | 测试发现健康检查 bug | 不修复、不回滚源文件——将 bug 登记到 §20 风险矩阵，新增 R14 条目 |
| T-DB-002 (audit_schema 测试) | AuditQuery 返回空结果 | 检查 events 表数据完整性——若缺数据，补充 test fixture；若代码问题，登记 bug |
| T-DB-003 (query_metrics 测试) | PercentileTracker 计算结果错误 | 审查算法正确性——对比手工计算与 tracker 输出 |
| T-DB-004 (SSoT 修复) | ✅ 已修复——无需回滚 | v2.1 蓝图审计时已完成 b_db.yaml + registry 同步 |
| T-DB-005 (备份验证) | 恢复后的 DB 与生产不一致 | 保留原始 DB 文件不动——恢复演练在临时路径进行，不影响生产 |
| T-DB-006~011 | 施工中途失败 | 新增代码限于新方法/新文件——不影响既有 7 文件功能。删除新文件即可回滚 |

### 16.7 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 |
|---|--------|---------------|:---:|:---:|
| 1 | test_database_manager.py | `D:\ZephyrAlpha\tests\unit\test_database_manager.py` | ❌ | ❌ |
| 2 | test_audit_schema.py | `D:\ZephyrAlpha\tests\unit\test_audit_schema.py` | ❌ | ❌ |
| 3 | test_query_metrics.py | `D:\ZephyrAlpha\tests\unit\test_query_metrics.py` | ❌ | ❌ |
| 4 | b_db.yaml SSoT | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | ✅ | ✅ |
| 5 | blueprint-registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | ✅ | ✅ |
| 6 | backup_verify() in database_manager | `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | ❌ | ❌ |
| 7 | dead_letter_queue() in database_manager | `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | ❌ | ❌ |
| 8 | connection_leak_detector in database_manager | `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | ❌ | ❌ |
| 9 | EXPLAIN 记录 in query_metrics | `D:\ZephyrAlpha\src\zephyr\db\query_metrics.py` | ❌ | ❌ |
| 10 | migration_dry_run in sqlite_schema | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | ❌ | ❌ |

### 16.8 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | phase_1_complete | 施工者 (v2.0 施工完成) |
| verification_status | partial——4/7 测试通过、3/7 待补 | 蓝图审计 (v2.1) |

---

## 17. SSoT 漂移与一致性

> ⚠️ 当前 b_db.yaml（v1.1.0）与磁盘实际代码存在漂移。蓝图 v2.1 是 canonical 真源。

### 17.1 已知漂移项

| # | 漂移内容 | b_db.yaml (旧) | 磁盘实际 (新) | 严重性 | 修复 |
|---|---------|:---|:---|:---:|------|
| D1 | 文件清单 | 4个.py | 7个.py（缺 database_manager/audit_schema/query_metrics） | 🟠 P1 | T-DB-004 |
| D2 | schema_version | 1.1.0 | 蓝图 2.1.0 | 🟡 P2 | T-DB-004 |
| D3 | db_file_path | `data/zalpha_metadata.db` | `docs/09_audit/state/zalpha_metadata.db` | 🟠 P1 | T-DB-004 |
| D4 | interfaces.contracts | CT-FLE-DB-001 + EXT-DB-ATM-001 | 蓝图 §12 定义了 4 个 CT-DB-* | 🟡 P2 | T-DB-004 |
| D5 | blueprint-registry.yaml | 版本 0.1.0 / 完整度 72% / partial_80 | 蓝图 2.1.0 / 完整度 ~95% / phase_1_complete | 🟠 P1 | 需同步更新注册表 |

### 17.2 一致性自愈策略

```yaml
drift_prevention:
  - 每次修改 db/ 目录下文件后，必须同步更新 b_db.yaml
  - CI 门禁：启动时对比 b_db.yaml.files 与 src/zephyr/db/*.py glob 结果
  - 不一致 → 阻断启动 + 提示修复 SSoT

self_healing:
  - database_manager.health_check() 自动检测 schema_version 与 _MIGRATIONS 注册表一致性
  - 不一致 → HealthStatus.unhealthy + 建议运行 init_db()
```

---

## 18. 氛围编程运营卓越性（Vibe Coding Operational Excellence）

> 本章回答：「1 人 + AI 维护的语境下，数据库怎么做到不出事、出了事能自动恢复？」

### 18.1 自愈设计（Self-Healing）

| 场景 | 自动检测 | 自动修复 | 人工介入条件 |
|------|:---:|:---:|------|
| WAL 文件无限增长 | wal_autocheckpoint=4096 | PostgreSQL式自动checkpoint | WAL > 100MB 触发告警 |
| 数据库文件损坏 | PRAGMA integrity_check（health_check 每60s） | 自动从最新备份恢复 | 恢复失败 → escalation:owner |
| 连接泄漏 | ❌ 待实现（T-DB-011） | 自动关闭超时连接 | 泄漏 > 10个 → escalation:owner |
| 慢查询积累 | query_metrics 自动检测 >500ms | 写入 slow_queries 表供 AI 分析 | 单日 > 20条 → escalation:owner |
| 磁盘空间不足 | ❌ 待实现——DatabaseManager 监控 | 自动清理过期备份 + 触发 Parquet 归档 | 剩余 < 1GB → escalation:owner |
| 事务死锁/超时 | ATM tx_timeout 30s 自动 ROLLBACK | 自动释放写锁 | 连续超时 3 次 → escalation:owner |
| Schema 版本落后 | schema_version() < MIGRATIONS max | init_db() 自动补齐迁移 | 迁移失败 → escalation:owner |

### 18.2 AI 可消费的 DB 诊断输出（AI-Consumable Diagnostics）

```python
# AI agent 调用此方法获取结构化诊断报告
def ai_diagnostic_report() -> dict:
    """
    返回一个 AI agent 可直接解析的数据库全维度诊断报告。
    
    使用方法：AI 遇到任何"感觉数据库可能有问题"的情况时，
    先调用此方法获取诊断报告，再根据 findings 决定下一步。
    """
    dm = DatabaseManager.instance()
    qm = QueryMetrics.instance()
    aq = AuditQuery()
    
    health = dm.health_check()
    stats = dm.stats()
    drift = aq.query_schema_drift()
    
    report = {
        "summary": {
            "verdict": "HEALTHY" if health.healthy else "UNHEALTHY",
            "action_required": not health.healthy,
            "recommended_action": _recommend_action(health, drift),
        },
        "health": health.to_dict(),
        "stats": stats,
        "schema_drift": drift,
        "query_performance": qm.stats_all(),
        "findings": _collect_findings(health, stats, drift),
    }
    return report
```

### 18.3 数据库作为代码（Database-as-Code）

```yaml
principles:
  - "DDL 在 sqlite_schema.py 中定义为 Python 字符串常量——不是外置 .sql 文件"
  - "Schema 版本化：_MIGRATIONS 注册表 = single source of truth"
  - "init_db() 幂等——可在 CI/CD/本地任意环境重复执行"
  - "PRAGMA 基线：所有连接通过 get_db_connection() 统一配置——不允许手动调 PRAGMA"

anti_patterns_to_avoid:
  - "❌ 手动执行 SQL 文件初始化数据库"
  - "❌ 不同环境使用不同的 PRAGMA 配置"
  - "❌ 绕过 init_db() 直接 sqlite3.connect()"
  - "❌ 在业务代码中写 DDL"
```

### 18.4 备份恢复演练（Backup Restore Drill）

```yaml
schedule: "每月 1 次自动恢复演练"
procedure:
  step_1: "从最新备份恢复到一个临时路径"
  step_2: "对恢复的 DB 执行 integrity_check"
  step_3: "对比恢复 DB 的表数量、行数与生产 DB"
  step_4: "删除临时恢复 DB"
  step_5: "记录演练结果到 events 表"

acceptance: "恢复 DB 的 table_count == 生产 DB && integrity_check == 'ok'"
failure_action: "escalation:owner + 标记备份策略为 UNTRUSTED"

implementation_status: "❌ 待实现（T-DB-005）"
```

### 18.5 故障注入测试（Chaos Engineering for SQLite）

| 故障场景 | 注入方式 | 期望行为 | 测试状态 |
|---------|---------|---------|:---:|
| WAL 文件被删除 | 手动删除 -wal 文件 | WAL 自动重建，不丢数据 | ❌ 待测试 |
| 数据库文件被截断 | 写入空文件覆盖 .db | health_check 检测 corruption → escalation | ❌ 待测试 |
| 磁盘写满 | 填满 tmp 目录 | write_file 失败 → ROLLBACK + 不丢已提交数据 | ❌ 待测试 |
| 事务中途进程崩溃 | kill -9 模拟 | WAL 恢复 → 未提交事务自动回滚 | ❌ 待测试 |
| 并发写入冲突 | 两个进程同时 BEGIN IMMEDIATE | 第二个等待 busy_timeout 5s → SQLITE_BUSY | ❌ 待测试 |
| DuckDB sqlite_scanner 不可用 | 删除 duckdb sqlite_scanner 插件 | OLAPEngine fallback 模式 + 告警 | ✅ olap_engine 已测试 |

---

## 19. 顶尖设计还应包含的演进方向

> 以下为 v2.1 之后的长线演进——1 人+AI 维护暂不需要全部实现，但必须知道天花板在哪。

| # | 能力 | 当前状态 | 顶尖做法 | 何时需要 |
|---|------|:---:|------|------|
| 1 | SQLCipher 透明加密 | ❌ 无 | Goldman SecDB 级全库加密 | L04+ 金融敏感数据落库 |
| 2 | 只读副本（Read Replica） | ❌ 无 | SQLite WAL + litestream S3 实时复制 | 项目 > 1000 模块、多 IDE 同时读 |
| 3 | 在线备份（Litestream） | ❌ 无（当前停机备份） | Fly.io Litestream——WAL 增量 S3 备份 | DB > 100MB 且备份耗时长 |
| 4 | 数据脱敏（Pseudonymization） | ❌ 无 | 测试环境自动脱敏 tasks 敏感字段 | 引入外部协作者 |
| 5 | 自适应 VACUUM（Auto-VACUUM） | ❌ 手动 cron | SQLite auto_vacuum=INCREMENTAL + 碎片率触发 | DB > 500MB |
| 6 | 行级安全（RLS via Triggers） | ❌ 无 | SQLite INSTEAD OF trigger + namespace 隔离 | 多 Agent 多租户写入 |
| 7 | 查询缓存（Prepared Statement Cache） | ❌ 无 | LRU cache 最近 100 条 parameterized SQL | 高频查询场景 |
| 8 | CDC 变更流（Change Data Capture） | ❌ 无 | events 表即天然 CDC——无需额外组件 | ✅ 已满足 |
| 9 | SQLite → PostgreSQL 零停机迁移 | ❌ 无方案 | pgloader + WAL 双写过渡期 | 团队 > 3 人或生产环境要求 |
| 10 | 自适应慢查询阈值 | ❌ 固定 500ms | P95 动态阈值——>2x P95 = slow | 负载波动大时 |

---

## 20. 已知风险与缓解（v2.1 补全）

| # | 风险 | 等级 | 描述 | 缓解 | 状态 |
|---|------|:---:|------|------|:---:|
| R01 | SQLite 单点故障 | 🟠 P1 | 单文件坏→状态/审计全部丢失 | 自动备份（7天+4周）+ health_check自动failover | ✅ 缓解 |
| R02 | WAL 无限增长 | 🟡 P2 | WAL不清导致磁盘耗尽 | wal_autocheckpoint=4096 + 维护时 wal_truncate | ✅ 缓解 |
| R03 | Schema 迁移手动高风险 | 🟡 P2 | 忘记迁移→sqlite3.OperationalError | _MIGRATIONS 表 + init_db() 自动按序执行未运行的迁移 | ✅ 缓解 |
| R04 | 软删除数据残留 | 🟡 P2 | 软删除 = 写新行，原行仍存在 | is_deleted=1 过滤 + 物理清理工具 | ✅ 缓解 |
| R05 | DuckDB sqlite_scanner 依赖 | 🟡 P2 | DuckDB WASM 可能无该模块 | olap_engine.fallback_to_sqlite 降级模式 | ✅ 缓解 |
| R06 | **3 个模块零测试** | 🟠 **P1** | database_manager/audit_schema/query_metrics 无测试覆盖 | Phase experimental 补全（T-DB-001~003） | ❌ 待处理 |
| R07 | **b_db.yaml SSoT 漂移** | 🟠 **P1** | YAML 声明的 4 个.py 与磁盘实际的 7 个.py 不一致 | T-DB-004 修复 + CI 门禁 | ❌ 待处理 |
| R08 | **蓝图注册表过期** | 🟠 **P1** | blueprint-registry.yaml 标记 database 为 v0.1.0 / 72% / partial_80，实际已是 v2.1.0 / ~95% / phase_1_complete | 同步更新注册表 | ❌ 待处理 |
| R09 | **备份从未验证能恢复** | 🟡 **P2** | 备份文件存在但实际可能损坏 | T-DB-005 每月自动恢复演练 | ❌ 待处理 |
| R10 | **无死信队列** | 🟡 **P2** | 写入失败直接丢弃（仅 log error） | T-DB-006 失败写入入队 + 定时重试 | ❌ 待处理 |
| R11 | **无连接泄漏检测** | 🟡 **P2** | 长期运行后连接耗尽 | T-DB-011 连接超时跟踪 + 自动回收 | ❌ 待处理 |
| R12 | **磁盘空间无监控** | 🟡 **P2** | DB 涨到 100GB 才发现 | §18.1 磁盘监控（待实现） | ❌ 待处理 |
| R13 | **固定慢查询阈值不适应负载变化** | 🟢 P3 | 500ms 阈值在当前规模合适 | §19 #10 自适应阈值 → P3 长线 | ⚠️ 注意 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本模块的核心架构设计（双引擎/ATM/冷热分层/迁移框架） | **本蓝图 §1-§10** | — |
| 本模块的接口契约（CT-DB-001~004） | **本蓝图 §12** | b_db.yaml（次要副本——冲突以本蓝图为准） |
| 本模块的数据结构定义（TaskCard/表/Schema/迁移） | **本蓝图 §1 概述 + sqlite_schema.py 磁盘代码** | — |
| 本模块的施工范围与步骤 | **本蓝图 §16** | — |
| 本模块的测试覆盖要求 | **本蓝图 §15 测试覆盖矩阵** | — |
| 磁盘文件清单 | **`src/zephyr/db/*.py`（7 文件）** | b_db.yaml（次要副本） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表（Tiered）

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-006 (task-system) | §4 task_repo.py 接口、§12 CT-DB-001 |
| Tier 1 | MOD-INF-010 (feedback-loop) | §12 CT-DB-003 OLAP 查询契约、CT-DB-002 ATM 事务 |
| Tier 1 | MOD-INF-020 (audit-trail) | §12 CT-DB-001 审计互锁、events 表不可变日志 |
| Tier 2 | MOD-INF-009 (pipeline) | §14 #2 task_repo list_by_* 查询 |
| Tier 2 | MOD-INF-013 (mcp-servers) | §14 #3 task_repo create/upsert |
| Tier 2 | MOD-INF-007 (gate-engine) | gates 表 + events 表共享写入 |
| Tier 2 | MOD-INF-015 (system-telemetry) | §12 CT-DB-004 DatabaseManager stats + health |
| Tier 3 | MOD-INF-001 (capacity-assurance) | §12 CT-DB-004 health_check() |
| Tier 3 | MOD-INF-016 (shared+core) | TaskCard 模型定义（Pydantic V2） |

### 变更同步规则

| 变更类型 | Tier 1（核心消费者） | Tier 2（集成系统） | Tier 3（监控/工具） |
|---------|------------------|------------------|------------------|
| task_repo 接口签名变更 | 下游 task-system 检查兼容性 | pipeline 检查查询字段 | shared+core 更新 TaskCard 模型 |
| events 表结构变更 | audit-trail 检查审计链完整性 | gate-engine 检查写入兼容 | — |
| OLAP 查询 schema 变更 | feedback-loop 检查 Dashboard 断裂 | — | system-telemetry 检查监控 |
| DatabaseManager stats 字段变更 | — | system-telemetry 检查面板 | capacity-assurance 检查告警 |
| 新增表/索引 | 通知所有 Tier 1 消费者（可能影响查询性能） | — | — |
| ATM 契约变更 | 通知 task-system + feedback-loop（两消费者） | — | — |

### 修改条件

| 变更类型 | 审批要求 | AI 权限 |
|---------|---------|:---:|
| 接口契约新增/修改（§12 CT-DB-\*） | Owner 审批 + 通知所有消费者 | ❌ AI 不可自主 |
| 数据模型重命名/删除字段 | Owner 审批 + 迁移方案 | ❌ AI 不可自主 |
| 新增表/索引/视图 | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 施工步骤微调（测试用例、路径修正） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 风险矩阵补充（§20 新增 R14+） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 容量估算更新（§13） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 施工完成标准更新（§16.7） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |

---

## Schema 版本历史

| 版本 | 描述 |
|:---:|------|
| v1 | Initial schema: tasks + events + knowledge + gates + indexes + views |
| v2 | task_files N:N mapping + namespace + seq columns (#21) |
| v3 | v2 fields: priority + model_rationale + actual_hours + files_in_scope + tags + completed_at + name→title (#12) |
| v4 | knowledge status column (T-2-11-A) |
| v5 | circuit_breaker_state table (T-V2-005) |
| v6 | TaskCard 24 extension columns (MOD-INF-006 v0.3.0) |
| v7 | _schema_version + slow_queries + tx_idempotency + wal_autocheckpoint (MOD-INF-012 v2.0) |
| v8 | soft delete columns: is_deleted + deleted_at (MOD-INF-012 v2.0) |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-06 | 2.2.0 | **蓝图模板全对齐**：(1) frontmatter 补 4 字段（rule_form/scope/stability/verifiability）；(2) §1 重构为 1.1 背景 + 1.2 目标（6 项可衡量）+ 1.3 不包含目标（7 项排除）；(3) §2 重构为 2.1 职责范围（9 项）+ 2.2 不包含职责（8 项→谁负责）+ 2.3 文件组成；(4) §16.1 新增 AI施工前检查清单（6 项）；(5) §16.6 新增 回滚方案（6 条）；(6) §16.7 新增 施工完成标准（10 项产出物）；(7) §16.8 新增 施工状态记录；(8) 新增 治理信息章（SSoT声明 6 行 + Tier 1/2/3 消费者 9 个 + 变更同步规则 6 行 + 修改条件 7 行 AI 权限矩阵） |
| 2026-05-06 | 2.1.0 | **盲点补全**：新增 必备链接 / 已有类似功能 / 涉及文件范围 模板章；新增 §12 接口契约（CT-DB-001~004 四大合同）；新增 §13 容量估算（存储+并发+性能基线）；新增 §14 消费者注册表（9 个消费者全量登记）；新增 §15 测试覆盖矩阵（4/7 已测、3/7 零测试缺口）；新增 §16 施工指引（T-DB-001~011 待施工清单 + Phase 顺序）；新增 §17 SSoT漂移与一致性（D1~D5 5 项漂移 + 自愈策略）；新增 §18 氛围编程运营卓越性（自愈设计矩阵 + AI诊断输出 + Database-as-Code + 备份恢复演练 + Chaos Engineering）；新增 §19 顶尖设计演进方向（10 项长线能力）；风险矩阵从 5 条扩至 13 条（含 3 条 P1 待处理）；frontmatter 增补 belongs_to / references / blueprint_level / 3 个缺失的 depends_on；集成目标从 4 个扩至 8 个 |
| 2026-05-05 | 2.0.0 | MOD-INF-012 v2.0 全面升级：ATM 增加 tx_idempotency + compensating_transaction + 事务超时；task_repo 增加 ON CONFLICT upsert + 软删除 + JSON1 查询；新增 database_manager（连接池/备份/WAL checkpoint）+ audit_schema（审计视图）+ query_metrics（性能监控）；olap_engine 增加 Parquet 冷热分层归档 + 统一查询；sqlite_schema 版本化迁移框架 v1–v8 |
| 2026-05-05 | 0.2.0 | 补全标准模板六项 |
| 2026-05-03 | 0.1.0 | 初始创建——从 b_db.yaml SSoT 派生 |
