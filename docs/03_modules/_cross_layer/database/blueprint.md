---
module_id: "MOD-INF-012"
title: "Database 蓝图 — 数据库系统·双库路由与持久化"
doc_type: blueprint
status: Active
version: "3.7.1"
layer: cross_layer
blueprint_level: module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-06"
ttl: permanent
rule_form: structural
belongs_to: "MOD-MASTER-001"
parent_module: ""
scope: global
stability: evolving
verifiability: automated
construction_progress: partially_implemented
actual_disk_path: 'D:\ZephyrAlpha\src\zephyr\db\'
codification_level: L2
codification_at: "2026-05-14"
last_verified: "2026-05-14"
last_updated: "2026-05-14"
generation: 2
functional_domain: data
summary: "双引擎元数据层（SQLite+DuckDB），13个.py已实现；v3.0 PostgreSQL双库路由+WriteBatcher+6张新表待施工；蓝图模板v3.5合规"
tags: [database, db, sqlite, duckdb, atm, atomic-transaction, task-repo, olap, infrastructure, migration, self-healing, operational-excellence, dual-db-router, write-batcher]
priority: P1
depends_on:
  - {target: "MOD-INF-006", at: "§3.2.1", why: "task_repo.py——TaskCard数据层真源"}
  - {target: "MOD-INF-007", at: "§1", why: "GateEngine——门禁结果SQLite落盘消费方"}
  - {target: "architecture-model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——本蓝图真源"}
references:
  - {id: "PS-STD-001", at: "§2~§7", why: "frontmatter字段合法值"}
  - {id: "PS-STD-002", at: "§3.1~§3.2", why: "标准文档模板——蓝图层级章节集"}
  - {id: "PS-STD-005", at: "§6", why: "蓝图归属与引用链——belongs_to字段定义"}
  - {id: "GOV-AI-001", at: "全篇", why: "AI自治权限注册——数据库操作权限边界"}
  - {id: "MOD-INF-010", at: "§2.1", why: "FLE 消费 olap_engine——集成关系"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计事件入库"}
  - {id: "MOD-INF-015", at: "全篇", why: "query_metrics 等遥测读写"}
---

<!-- COMPLIANCE_CHECKLIST
blueprint_template_version: "3.5"
checks:
  - id: CC-01, desc: "§7 备选方案已删除", status: PASS
  - id: CC-02, desc: "§15 正面后果已删除，负面后果合并到§14", status: PASS
  - id: CC-03, desc: "§14 增加'类型'列（风险/负面后果）", status: PASS
  - id: CC-04, desc: "§18 增加时态属性标注（永久时态）", status: PASS
  - id: CC-05, desc: "§5.1 技术约束去掉'原因'列", status: PASS
  - id: CC-06, desc: "§5.3 迁移方案标注临时时态", status: PASS
  - id: CC-07, desc: "§10 拆为4个子节", status: PASS
  - id: CC-08, desc: "铁律新增 #13~#15", status: PASS
  - id: CC-09, desc: "蓝图拆分判定标准段落已添加", status: PASS
  - id: CC-10, desc: "§0.1 '存在性'列+阻塞原因列（受控词表）", status: PASS
  - id: CC-11, desc: "COMPLIANCE_CHECKLIST 已添加", status: PASS
  - id: CC-12, desc: "§0 前移至概述之后", status: PASS
  - id: CC-13, desc: "§10.2 依赖图对齐声明含多对齐项+验证命令", status: PASS
  - id: CC-14, desc: "§10.3 内部依赖图含执行顺序依赖+数据流依赖子节", status: PASS
  - id: CC-15, desc: "§10.4 自动化规格含是否需要/如何实现/触发方式三子节", status: PASS
  - id: CC-16, desc: "施工声明（铁律/安全删除/必备链接）标注时态属性", status: PASS
-->

# Database 蓝图 — 数据库系统·双库路由与持久化

> module_id: MOD-INF-012 | version: 3.7.1 | status: active | layer: cross_layer | belongs_to: MOD-MASTER-001
> actual_disk_path: `D:\ZephyrAlpha\src\zephyr\db\` | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图描述 Database 模块——它解决了 AI 治理框架中结构化数据持久化与查询的核心问题。核心职责包括：SQLite WAL 事务引擎、DuckDB OLAP 分析引擎、ATM 两阶段原子事务、WriteBatcher 批量写入、TaskRepository 10状态任务机。当前规模 8 张核心表 / ~10GB 数据，13 个 .py 已实现；v3.0 目标 PostgreSQL 双库路由 + 6 张新表 + 100 AI 并发写入。上游依赖 Pipeline Orchestrator（任务创建），下游被审计溯源、知识库、门禁引擎消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[compression-workflow-standard.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/compression-workflow-standard.md)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:---:|-------------------|
| 1 | `atomic_transaction_manager.py` | §3 ATM v2.0 | 跨 SQLite/文件系统两阶段提交 + 幂等去重 + 补偿 | 已实现 | — |
| 2 | `olap_engine.py` | §3 OLAP | DuckDB OLAP 分析引擎 + Parquet 冷热分层归档 | 已实现 | — |
| 3 | `sqlite_schema.py` | §3 Schema | SQLite 表结构定义 + 版本化迁移框架 v1–v8 | 已实现 | — |
| 4 | `task_repo.py` | §3 TaskRepo | 任务 CRUD + 10 状态机 + N:N task_files + 软删除 | 已实现 | — |
| 5 | `database_manager.py` | §3 DBManager | 连接池/健康检查/自动备份/WAL checkpoint | 已实现 | — |
| 6 | `audit_schema.py` | §3 AuditSchema | 审计视图与查询入口 | 已实现 | — |
| 7 | `query_metrics.py` | §3 QueryMetrics | SQL 查询性能监控 P50/P95/P99 | 已实现 | — |
| 8 | `base_repo.py` | §3 基类 | 仓库基类 | 已实现 | — |
| 9 | `gate_repo.py` | §3 门禁 | 门禁记录仓库 | 已实现 | — |
| 10 | `circuit_breaker_repo.py` | §3 熔断 | 熔断器状态仓库 | 已实现 | — |
| 11 | `query.py` | §3 查询 | 通用查询工具 | 已实现 | — |
| 12 | `transition.py` | §3 状态转换 | 状态转换逻辑 | 已实现 | — |
| 13 | `__init__.py` | — | 包初始化 | 已实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls D:\ZephyrAlpha\src\zephyr\db\` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| v3.0 新增 6 张表 DDL 待施工（蓝图特有：Schema DDL） | 检查 sqlite_schema.py _MIGRATIONS | ☐ |
| v3.0 新增 DualDBRouter/WriteBatcher/ScriptScheduler 待施工 | 检查 src/zephyr/db/ 目录 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v2.x (基线) | 13 个 .py 文件：ATM/task_repo/olap_engine/sqlite_schema/database_manager/audit_schema/query_metrics + 辅助文件 | — | — |
| v3.0 (容量升级) | §17 新增 DDL/接口设计 | modules/scripts/module_scripts/script_dependencies/file_script_map/script_executions 6 张新表 DDL; DualDBRouter/WriteBatcher/ScriptScheduler 3 个新组件 | 待施工 Phase 3A–3F |

---

## §1 设计背景与目标

### 1.1 背景

| 维度 | 设计决策 |
|------|---------|
| 元数据存储 | SQLite 3.x WAL 模式 |
| OLAP 分析 | DuckDB（嵌入式） |
| 原子事务 | ATM v2.0 两阶段提交 |
| 版本化迁移 | 内嵌 _MIGRATIONS 注册表 |
| 备份策略 | SQLite backup API |

> 选择理由见 §18 决策记录 D-INF012-06~10

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 所有 TaskCard CRUD < 50ms（含状态转换 + events 写入） | 4 份测试覆盖 + query_metrics P95 < 50ms |
| 2 | 跨 SQLite/文件系统原子事务零不一致 | ATM execute 全部路径有测试覆盖 + 补偿事件链路完整 |
| 3 | DB 单点故障 5 分钟内自动恢复 | 健康检查自动检测 + 最新备份自动恢复 |
| 4 | events 表永不超过 30 天热数据（冷热分层） | archive_events 每次执行后 events 表行数 ≤ 阈值 |
| 5 | AI Agent 可零上下文消费 DB 诊断信息 | ai_diagnostic_report() 返回结构化 dict |
| 6 | init_db() 幂等——任意环境可重复执行 | 多次执行不报错、不丢数据 |

### 1.3 不包含的目标

| # | 明确排除 |
|---|---------|
| 1 | 分布式事务（跨多机器） |
| 2 | 实时 CDC 变更流（Kafka/Redpanda） |
| 3 | ORM 层（SQLAlchemy） |
| 4 | 数据库集群/主从复制 |
| 5 | 在线备份（Litestream S3 流式复制） |
| 6 | 全文搜索引擎集成（Elasticsearch） |
| 7 | 时序数据库（InfluxDB/TimescaleDB） |

**负向责任**：本蓝图不涉及任务调度逻辑（→ MOD-INF-006）、门禁规则评估（→ MOD-INF-007）、向量检索（→ MOD-INF-011）、LLM 安全审计（→ MOD-INF-014）。

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 单机本地部署（i7-12700KF / 64GB RAM / 1TB NVMe SSD） | 无分布式需求，PostgreSQL 本地单实例足够 |
| 1 人 + AI 维护，零 DBA | 所有运维必须自动化 |
| Windows 开发环境 | subprocess 内存隔离需 Windows Job Object；Docker Desktop 运行 PostgreSQL |
| SQLite WAL 单 Writer 限制 | v2.x 写入串行化；v3.0 通过 PostgreSQL MVCC 解决 |
| 100 AI Agent 并发峰值 | 连接池 max 50 + PostgreSQL max_connections 120 + WriteBatcher 批量合并 |
| 数据库文件 < 1GB（v2.x）/ < 10GB（v3.0 稳态） | 停机备份 < 30s |

---

## §2 模块边界

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

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 任务调度与分派 | MOD-INF-006 (task-system) + MOD-INF-009 (pipeline) |
| 2 | 门禁规则定义与评估 | MOD-INF-007 (gate-engine) |
| 3 | FLE 时序指标定义 | MOD-INF-010 (feedback-loop) |
| 4 | 向量化检索 | MOD-INF-011 (vector-memory / ChromaDB) |
| 5 | 上下文构建注入 | MOD-INF-008 (context-engine) |
| 6 | 审计事件语义解析 | MOD-INF-020 (audit-trail) |
| 7 | 监控 Dashboard 渲染 | MOD-INF-015 (system-telemetry) |
| 8 | LLM Prompt/响应管理 | MOD-INF-014 (llm-security) |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | TaskRepository | 任务 CRUD + 10 状态机 + 事件写入 | sqlite_schema, GateEngine | 同步调用 |
| 2 | AtomicTransactionManager | 跨 SQLite/文件系统两阶段提交 | sqlite3, os.replace | 同步调用 |
| 3 | OLAPEngine | DuckDB OLAP 分析 + Parquet 归档 | duckdb, pyarrow | 同步调用 |
| 4 | DatabaseManager | 连接池/健康检查/备份/WAL checkpoint | sqlite3 | 同步调用 |
| 5 | AuditSchema | 审计视图 + 补偿事件查询 + Schema 漂移检测 | sqlite3 | 同步调用 |
| 6 | QueryMetrics | P50/P95/P99 + slow_queries | sqlite3 | 装饰器 + 同步调用 |
| 7 | SQLiteSchema | DDL + _MIGRATIONS 迁移框架 | sqlite3 | init_db() 同步调用 |
| 8 | DualDBRouter | PostgreSQL（在线）+ SQLite（离线缓存）路由 | asyncpg, sqlite3 | 异步调用（v3.0） |
| 9 | WriteBatcher | 批量写入缓冲 + PG COPY | DualDBRouter | 异步调用（v3.0） |
| 10 | ScriptScheduler | Worker Pool + Semaphore + PriorityQueue | WriteBatcher | 异步调用（v3.0） |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | MOD-INF-006 (task-system) | TaskRepository.create() → SQLite INSERT | events 表 | TaskCard (Pydantic V2) |
| 2 | MOD-INF-007 (gate-engine) | TaskRepository.transition() → G1 门禁 + 状态写入 + events | events + gates 表 | GateResult |
| 3 | MOD-INF-010 (feedback-loop) | OLAPEngine.task_progress_trend() → DuckDB 聚合 | TrendRow list | TrendRow |
| 4 | ATM 调用方 | ATM.execute() → PREPARE → COMMIT/ROLLBACK | tx_idempotency 表 | TransactionResult |
| 5 | v3.0: 脚本执行器 | WriteBatcher.enqueue() → 缓冲 → PG COPY | script_executions 表 | ExecutionRow |
| 6 | v3.0: AI Agent | DualDBRouter.read() → SQLite 优先 → PG fallback | 调用方 | dict list |

### 3.3 状态生命周期

TaskCard 10 状态机（`task_repo.py` transition()）：

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| draft | create | pending | 必填字段完整 |
| pending | approve | in_progress | G1 门禁通过 |
| in_progress | complete | review | 完成标准满足 |
| review | accept | completed | 审核通过 |
| review | reject | in_progress | 审核不通过 |
| completed | verify | verified | 验证通过 |
| verified | close | closed | 无阻塞项 |
| 任意 | block | blocked | 有阻塞依赖 |
| blocked | unblock | in_progress | 阻塞解除 |
| 任意 | cancel | cancelled | 取消条件满足 |

---

## §4 接口契约

### 4.1 公共 API

#### TaskRepository

```python
class TaskRepo:
    def create(task: TaskCard) -> TaskCard
    def get(task_id: str) -> Optional[TaskCard]
    def update(task_id: str, updates: dict) -> TaskCard
    def upsert(task: TaskCard) -> TaskCard
    def delete(task_id: str) -> bool
    def hard_delete(task_id: str) -> bool
    def transition(task_id: str, to_status: Status) -> TaskCard
    def list_by_status(status: Status) -> list[TaskCard]
    def list_by_phase(phase: int) -> list[TaskCard]
    def list_by_session(session_id: str) -> list[TaskCard]
    def list_by_namespace(namespace) -> list[TaskCard]
    def list_active() -> list[TaskCard]
    def list_by_dependency(dependency_task_id: str) -> list[TaskCard]
    def list_by_tag(tag: str) -> list[TaskCard]
    def list_by_blocked_by(blocker_task_id: str) -> list[TaskCard]
```

#### AtomicTransactionManager

```python
class AtomicTransactionManager:
    def __init__(db_path: Path, timeout: float = 30.0)
    def execute(operations: list[Callable]) -> Any
    def write_file(target_path: Path, content: str) -> None
    def commit() -> None
    def rollback() -> None
```

#### OLAPEngine

```python
class OLAPEngine:
    def task_progress_trend(period: str, limit: int, phase: Optional[int]) -> list[TrendRow]
    def compliance_rate_trend(period: str, limit: int, gate_id: Optional[str]) -> list[TrendRow]
    def knowledge_activation_trend(period: str, limit: int, category: Optional[str]) -> list[TrendRow]
    def archive_events(days: int, archive_dir: Optional[Path]) -> dict
    def query_unified_events(limit: int) -> list[TrendRow]
```

#### DatabaseManager

```python
class DatabaseManager:
    def health_check() -> HealthStatus
    def backup(label: Optional[str]) -> Path
    def maintenance() -> dict
    def stats() -> dict
```

#### DualDBRouter（v3.0）

```python
class DualDBRouter:
    def __init__(pg_dsn: str, sqlite_path: Path)
    async def read(query: str, params: tuple) -> list[dict]
    async def write(query: str, params: tuple) -> None
    async def write_batch(query: str, rows: list[tuple]) -> int
    async def enable_offline_mode() -> None
    async def disable_offline_mode() -> None
    async def health_check() -> dict
```

#### WriteBatcher（v3.0）

```python
class WriteBatcher:
    def __init__(router: DualDBRouter, config: WriteBatcherConfig)
    async def enqueue(row: tuple) -> None
    async def start() -> None
    async def stop() -> None
    def stats() -> dict
```

### 4.2 数据模型

> 数据模型定义见 `D:\ZephyrAlpha\src\zephyr\db\` 对应源码（铁律#13：已实现代码不在蓝图中重复）。枚举值：TaskStatus(9)、TriggerType(4)、ExecutionStatus(6)。Pydantic 模型：HealthStatus(6 字段)、WriteBatcherConfig(5 字段)。

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `task_repo.create()` | `task: TaskCard` | ✅ | task_id UNIQUE |
| `task_repo.transition()` | `task_id + to_status + session_id?` | ✅ | 必须符合 10 状态机转换表 |
| `task_repo.upsert()` | `task: TaskCard` | ✅ | ON CONFLICT DO UPDATE |
| `olap_engine.task_progress_trend()` | `period + limit + phase?` | ✅ | period ∈ {day,week,month}; limit 1-10000 |
| `olap_engine.archive_events()` | `days + archive_dir?` | ✅ | days > 0 |
| `atm.execute()` | `operations: list[Callable]` | ✅ | 禁止嵌套事务 |
| `atm.write_file()` | `target_path + content` | ✅ | InputSanitizer.validate_path 禁止 `../` |
| `dual_db_router.read()` | `query + params` | ✅ | 参数化查询 |
| `write_batcher.enqueue()` | `row: tuple` | ✅ | 非阻塞 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `task_repo.create()` | `TaskCard` | `P0InflationFrozenError` / `IntegrityError` |
| `task_repo.transition()` | `TaskCard` | `TaskNotFoundError` / `InvalidTransitionError` / `GateViolationError` |
| `task_repo.get()` | `TaskCard \| None` | — |
| `olap_engine.task_progress_trend()` | `list[TrendRow]` | `ValueError`（参数校验失败） |
| `atm.execute()` | `Any` | `TransactionError` / `TransactionTimeoutError` |
| `database_manager.health_check()` | `HealthStatus` | — |
| `dual_db_router.health_check()` | `{pg_healthy, sqlite_healthy, mode, pg_pool_size}` | — |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| CT-DB-001~004 接口签名变更 | ❌ 破坏性 | 需 Owner 审批 + 通知所有消费者 |
| CT-DB-005~007 新增契约 | ✅ 向后兼容 | v3.0 新增，不影响 v2.x |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|------|
| 1 | SQLite WAL 单 Writer | v3.0 通过 PG MVCC 解决 |
| 2 | DuckDB sqlite_scanner 可选 | fallback_to_sqlite 降级 |
| 3 | Windows subprocess 内存隔离 | 需 pywin32 Job Object |
| 4 | asyncpg 仅在线模式 | 离线模式回退 SQLite |
| 5 | PG Advisory Lock 非持久化 | 锁在 session 断开时自动释放 |
| 6 | FTS5 仅 SQLite 侧 | PostgreSQL 侧用 pg_trgm GIN 索引 |

### 5.2 容量估算

#### v2.x 基线

| 维度 | 当前规模 | 1年后估算 | 3年后估算 | 上限 |
|------|:---:|:---:|:---:|------|
| tasks 表行数 | ~200 | ~2,000 | ~10,000 | 无硬上限 |
| events 表行数 | ~500 | ~5,000 | ~50,000 | 冷热分层（30天热 + Parquet永久） |
| script_executions 表行数 | 0 | ~100,000 | ~1,200,000 | 冷热分层（30天热 + Parquet归档） |
| DB 文件大小 | ~5 MB | ~50 MB | ~200 MB | SQLite 单文件 ~281 TB |
| WAL 文件大小 | ~2 MB | ~10 MB | ~20 MB | wal_autocheckpoint=4096 自动截断 |
| Parquet 归档 | 0 | ~50 MB | ~500 MB | 磁盘容量限制 |
| 备份文件 | ~35 MB (7天) | ~350 MB | ~1.4 GB | 自动轮转清理 |

#### v3.0 重算

| 表名 | v3.0 稳态行数 | 月增量 | 表稳态大小 |
|---|---|---|---|
| tasks | ~5,000 | ~2,000 | ~10 MB |
| events | ~50,000（30天热） | ~100,000 | ~25 MB（热） |
| gates | ~10,000 | ~20,000 | ~5 MB |
| knowledge | ~2,000 | ~500 | ~2 MB |
| modules | **1,500** | — | <1 MB |
| scripts | **10,000** | — | ~3 MB |
| module_scripts | **50,000** | — | ~5 MB |
| script_dependencies | **5,000** | — | ~1 MB |
| file_script_map | **30,000** | — | ~6 MB |
| script_executions | **500,000（30天热）** | **~500,000** | **~150 MB（热）** |

| 汇总 | v3.0 重算 |
|---|---|
| SQLite 热数据大小 | **~200 MB** |
| PostgreSQL 主库大小 | **~250 MB**（含所有表 + 索引开销 ×1.5） |
| Parquet 冷归档（30天+） | **~2 GB/年** |
| 备份总大小 | **PostgreSQL: ~250 MB × 7天 = 1.75 GB** |

#### 并发容量

| 维度 | v2.x | v3.0 重算 |
|---|---|---|
| 并发写连接 | 1（单Writer） | **50+（PostgreSQL MVCC）** |
| 并发读连接 | 10+ | **100+（SQLite WAL + PG 读无锁）** |
| 脚本并发执行 | 1（串行） | **40–100（Worker Pool + Semaphore）** |
| 峰值脚本排队 | — | **1,500（100 AI 同时触发）** |
| WriteBatcher 吞吐 | — | **2,000 rows/s（COPY 批量）** |

#### 性能基线

| 操作 | v2.x 目标 | v3.0 目标 |
|---|---|---|
| task_repo.get() | < 5ms | **< 2ms**（SQLite 缓存命中） |
| task_repo.create() | < 20ms | **< 20ms**（PG 写 + async SQLite sync） |
| task_repo.transition() | < 50ms | **< 50ms**（含门禁评估 + events） |
| script_executions 单条写入 | N/A | **< 1ms**（enqueue 非阻塞） |
| script_executions 批量 flush | N/A | **< 100ms**（50 条/批） |
| resolve_scripts_by_files() | N/A | **< 50ms**（三路匹配 SQL） |
| OLAP 趋势查询 | < 500ms | **< 500ms**（DuckDB + Parquet） |
| health_check（双库） | < 100ms | **< 200ms**（PG ping + SQLite integrity） |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。

#### v3.0 迁移策略（待施工）

| Phase | 操作 | 校验 |
|:---:|------|------|
| 1 | SQLite → JSONL 导出（按表分别导出） | 行数 = 源表行数 |
| 2 | JSONL → PostgreSQL 导入（pg COPY） | PG 行数 = 导出文件行数 |
| 3 | 双写过渡期（1 周）：DualDBRouter.write() → PG（主）+ 异步回写 SQLite | PG 稳定后停 SQLite 写入 |
| 4 | SQLite 降级为只读缓存 | DualDBRouter 停止 SQLite 写入 |

**回滚方案**：双写期间，若 PG 异常 → `DualDBRouter.enable_offline_mode()` → 全部读写回 SQLite（零数据丢失）。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | SQLite WAL 写锁冲突（SQLITE_BUSY） | busy_timeout 5s + 重试 | ATM 锁串行化 + 5s 重试 | task_repo 写操作 |
| 2 | ATM rename 失败致不一致 | tx_idempotency 状态检查 | compensating_transaction + .bak 回滚 | 跨 DB/文件事务 |
| 3 | 数据库文件损坏 | PRAGMA integrity_check（health_check 每 60s） | 自动从最新备份恢复 | 全部模块 |
| 4 | 事务超时后持有写锁 | ATM tx_timeout 30s | 自动 ROLLBACK + 释放写锁 | task_repo 写操作 |
| 5 | DuckDB sqlite_scanner 不可用 | olap_engine 初始化检测 | fallback_to_sqlite 降级模式 | OLAP 查询 |
| 6 | WriteBatcher flush 失败 | 重试 3 次 + 死信队列 | retry_queue → DLQ → 人工介入 | script_executions 写入 |
| 7 | PostgreSQL 不可达 | DualDBRouter health_check | enable_offline_mode() → SQLite 降级 | 全部写操作 |
| 8 | 连接泄漏 | connection_leak_detector | 自动关闭超时连接（>300s） | 连接池 |
| 9 | 磁盘空间不足 | disk_monitor | 自动清理过期备份 + WAL TRUNCATE | 全部操作 |
| 10 | Schema 版本落后 | schema_version() vs _MIGRATIONS | init_db() 自动补齐迁移 | 数据库初始化 |

---

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 路径穿越攻击（ATM write_file） | 高 | InputSanitizer.validate_path——禁止 `../` 和绝对路径越界 | test_atomic_transaction_manager 路径校验用例 |
| 2 | SQL 注入（OLAP 查询） | 中 | 参数化查询 + period 白名单 + limit 范围校验 | test_olap_engine 参数校验用例 |
| 3 | 数据库文件未授权访问 | 中 | 文件系统权限控制；PostgreSQL pg_hba.conf 限制本地连接 | 检查 data/ 目录权限 |
| 4 | 备份文件泄露敏感数据 | 低 | 备份目录不在项目根目录；.gitignore 排除 | 检查 .gitignore 规则 |
| 5 | AI Agent 越权写操作 | 中 | GOV-AI-001 权限注册表 + task_repo 接口级权限 | 审计日志检查越权操作 |
| 6 | PostgreSQL 连接凭据泄露 | 高 | 环境变量注入（ZALPHA_PG_PASSWORD）；不硬编码 | Grep 检查源码无明文密码 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | task_repo CRUD + 状态机 + 事件 + 查询 | ~40+ 用例 | 7/7 模块全覆盖 |
| 2 | 单元测试 | ATM 两阶段提交 + 幂等 + 补偿 | ~18+ 用例 | 全部通过 |
| 3 | 单元测试 | sqlite_schema 迁移幂等 | ~20+ 用例 | 全部通过 |
| 4 | 单元测试 | olap_engine 趋势查询 + 降级 | ~15+ 用例 | 全部通过 |
| 5 | 单元测试 | database_manager 运维 | 14 用例 | 全部通过 |
| 6 | 单元测试 | audit_schema 审计查询 | 8 用例 | 全部通过 |
| 7 | 单元测试 | query_metrics 性能监控 | 12 用例 | 全部通过 |
| 8 | 集成测试 | v3.0 DualDBRouter + WriteBatcher | 在线/离线切换/批量写入/背压 | Phase 3B+3C |
| 9 | 压力测试 | 100 AI 并发写入 | 模拟 100 AI 同时增量扫描 | Phase 3F |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-006 | 必须 | task_repo.py——TaskCard 数据层真源 | v0.3+ | `D:\ZephyrAlpha\docs\03_modules\_l01_infrastructure\task-system\blueprint.md` |
| MOD-INF-007 | 必须 | GateEngine——门禁结果 SQLite 落盘消费方 | — | `D:\ZephyrAlpha\docs\03_modules\_l01_infrastructure\gate-engine\blueprint.md` |
| b_db.yaml | 必须 | DB YAML SSoT——本蓝图真源 | v2.2+ | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` |
| MOD-INF-010 | 可选 | FLE 消费 olap_engine——集成关系 | — | `D:\ZephyrAlpha\docs\03_modules\_l01_infrastructure\feedback-loop\blueprint.md` |
| MOD-INF-020 | 可选 | 审计事件入库 | — | `D:\ZephyrAlpha\docs\03_modules\_l01_infrastructure\audit-trail\blueprint.md` |
| MOD-INF-015 | 可选 | query_metrics 等遥测读写 | — | `D:\ZephyrAlpha\docs\03_modules\_l01_infrastructure\system-telemetry\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | ☐ 待验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-012` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | ☐ 待验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-012` |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | ☐ 待验证 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `sqlite_schema.py` init_db() | `task_repo.py` | Schema 必须先初始化才能 CRUD | 检查 tasks 表是否存在 |
| `sqlite_schema.py` init_db() | `olap_engine.py` | Schema 必须先初始化才能 OLAP 查询 | 检查 events 表是否存在 |
| `sqlite_schema.py` init_db() | `audit_schema.py` | Schema 必须先初始化才能审计查询 | 检查 audit 视图是否存在 |
| `dual_db_router.py`（v3.0） | `write_batcher.py`（v3.0） | WriteBatcher 依赖 DualDBRouter.write_batch() | 检查 DualDBRouter 实例 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `task_repo.py` | `olap_engine.py` | TaskCard 状态变更事件 | 共享数据库 events 表 |
| `task_repo.py` | `audit_schema.py` | 审计事件记录 | 共享数据库 events 表 |
| `database_manager.py` | `query_metrics.py` | 查询执行耗时 | 装饰器注入 |
| `atomic_transaction_manager.py` | `audit_schema.py` | 补偿事件 | 共享数据库 tx_idempotency 表 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 6 个外部依赖 + 13 个内部文件，手动维护易漂移 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖（MOD-INF-006/007/010/020/015），需 CI 门禁 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 迁移方案执行后需从蓝图删除 |
| 4 | 施工步骤完成度自动检测 | 是 | v3.0 待施工，需跟踪 Phase 3A–3F 进度 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | `scripts/governance/check_blueprint_deps.py` | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | `scripts/governance/d5_architecture/validators/validate_path_alignment.py` | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 蓝图文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\db\` | Python 源码（13 个 .py） |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\db\` | 单元测试 |
| 数据文件 | `D:\ZephyrAlpha\data\zalpha_metadata.db` | SQLite 主数据库 |
| 备份目录 | `D:\ZephyrAlpha\data\backups\` | 自动备份文件（7天日备份 + 4周末备份） |
| 冷数据归档 | `D:\ZephyrAlpha\data\warehouse\` | Parquet 冷数据（events_YYYYMMDD.parquet） |

---

## §12 集成目标

| # | 项目 | 深度 | 集成点 | 验证方法 |
|---|------|:---:|------|---------|
| 1 | task-system | P1 | task_repo.py → 状态机 + 审计互锁 | transition() 事务原子性测试 |
| 2 | pipeline | P1 | task_repo.py → status 驱动的决策 | list_by_status() 查询正确性 |
| 3 | mcp-servers | P1 | task_repo.py + ATM session handoff | create/upsert 幂等性测试 |
| 4 | feedback-loop | P1 | olap_engine.py → 趋势分析 + report 产出 | trend API 返回格式验证 |
| 5 | system-telemetry | P1 | database_manager.py → stats 面板 | stats() 字段完整性验证 |
| 6 | audit-trail | P1 | audit_schema.py→AuditQuery + 补偿事件 | 补偿事件查询正确性 |
| 7 | gate-engine | P1 | gates 表 + events 表共享写入 | transition() 中门禁原子落盘 |
| 8 | capacity-assurance | P1 | database_manager.health_check() | health_status 结构验证 |

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号 3.6.0 + 完整度 100% + status active | v3.6 模板升级 + 压缩 |
| 2 | DB YAML SSoT | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | 补全 6 个缺失 .py + 更新 schema_version | SSoT 漂移修复 |
| 3 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | DB 模块状态 active | 代码施工完成 |
| 4 | AI 自治权限注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | 注册 MOD-INF-012 的 AI 操作权限边界 | blueprint 新增 belongs_to + references |

---

## §14 风险与负面后果

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|------|:---:|:---:|------|------|
| R01 | SQLite 单点故障 | 高 | P1 | 自动备份（7天+4周）+ health_check 自动 failover | 风险 |
| R02 | WAL 无限增长 | 中 | P2 | wal_autocheckpoint=4096 + 维护时 wal_truncate | 风险 |
| R03 | Schema 迁移手动高风险 | 中 | P2 | _MIGRATIONS 表 + init_db() 自动按序执行 | 风险 |
| R04 | 软删除数据残留 | 中 | P2 | is_deleted=1 过滤 + 物理清理工具 | 风险 |
| R05 | DuckDB sqlite_scanner 依赖 | 中 | P2 | olap_engine.fallback_to_sqlite 降级模式 | 风险 |
| R06 | 备份从未验证能恢复 | 中 | P2 | T-DB-005 verify_backup() 已实现 | 风险 |
| R07 | 无死信队列 | 中 | P2 | T-DB-006 dead_letter_queue 已实现 | 风险 |
| R08 | 无连接泄漏检测 | 中 | P2 | T-DB-011 connection_leak_detector 已实现 | 风险 |
| R09 | 磁盘空间无监控 | 中 | P2 | disk_monitor() 待实现 | 风险 |
| R10 | PostgreSQL 迁移导致短暂不可用 | 高 | P1 | 双写过渡期——PostgreSQL + SQLite 并行写 1 周 | 风险 |
| R11 | WriteBatcher 内存缓冲区溢出 | 中 | P2 | 背压机制——缓冲区>500条时降速 | 风险 |
| R12 | PG Advisory Lock 死锁 | 中 | P2 | 超时释放 + lock 获取顺序排序（按 hash） | 风险 |
| R13 | Worker Pool 中脚本子进程泄漏 | 中 | P2 | 定期扫描 + 孤儿进程 reaper（每分钟） | 风险 |
| R14 | PostgreSQL Docker 数据目录权限问题（Windows） | 高 | P1 | 使用 named volume 而非 bind mount + 预检脚本 | 风险 |
| C01 | SQLite 单文件限制 | — | — | 上限约 281TB（实际远不会达到） | 负面后果 |
| C02 | 事务管理复杂度 | — | — | ATM v2.0 四状态（PREPARED/COMMITTED/ROLLED_BACK/COMPENSATED） | 负面后果 |
| C03 | v3.0 迁移成本 | — | — | SQLite → PostgreSQL 需全量迁移 + 双写过渡期 | 负面后果 |
| C04 | v3.0 新增运维 | — | — | PostgreSQL Docker 实例需要监控和维护 | 负面后果 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| Phase 划分 | scaffold（已完成）+ v2.0 升级（已完成）+ v3.0 容量升级（待施工） |
| 施工模式 | 既有模块增强——不新建文件，只补测试和增量功能 |
| 核心风险 | v3.0 PostgreSQL 迁移期间双写一致性 |
| 目标 generation | 2 — 本次施工将蓝图从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 13 个 .py 源文件已在 `D:\ZephyrAlpha\src\zephyr\db\` 就绪 | hard | ✅ | ✅ |
| 2 | b_db.yaml SSoT 已同步至 v2.2.0 | hard | ✅ | ✅ |
| 3 | 蓝图 §4 接口契约 CT-DB-001~007 已定义 | hard | ✅ | ✅ |
| 4 | Owner 确认 v3.0 Decision 1–5（§17.3 架构决策） | hard | ☐ | ☐ |
| 5 | PostgreSQL Docker 镜像已拉取至本地 | hard | ☐ | ☐ |

### 16.3 实施步骤

#### 步骤 1：Schema Foundation（Phase 3A）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 CT-DB-005 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py`（扩展） |
| 验收标准 | 6 张新表 DDL + _MIGRATIONS v17–v20 + init_db() 幂等 |
| 验证命令 | `python -m pytest tests/unit/db/test_sqlite_schema.py -v` |
| G7 检查项 | 上游：sqlite_schema.py 现有迁移链；下游：modules/scripts/module_scripts 等 6 张表 |

#### 步骤 2：PostgreSQL 迁移（Phase 3B）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 CT-DB-007 DualDBRouter |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\db\dual_db_router.py`（新建） |
| 验收标准 | DualDBRouter 在线/离线切换 + task_repo 适配 + 双模式测试通过 |
| 验证命令 | `python -m pytest tests/unit/db/test_dual_db_router.py -v` |
| G7 检查项 | 上游：asyncpg pool 配置；下游：所有 task_repo/events/gates 写入路径 |

#### 步骤 3：并发与调度（Phase 3C）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 CT-DB-006 WriteBatcher |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\db\write_batcher.py`（新建） |
| 验收标准 | WriteBatcher 批量写入 + PG Advisory Lock + 连接池扩容 + Session 隔离 |
| 验证命令 | `python -m pytest tests/unit/db/test_write_batcher.py -v` |
| G7 检查项 | 上游：DualDBRouter.write_batch()；下游：script_executions 写入 |

#### 步骤 4：增量扫描集成（Phase 3D）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 CT-DB-005 resolve_scripts_by_files() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py`（扩展 file_script_map） |
| 验收标准 | file_script_map 填充 + git diff 解析 + 拓扑排序 + Worker Pool |
| 验证命令 | `python -m pytest tests/unit/db/test_incremental_scan.py -v` |
| G7 检查项 | 上游：file_script_map DDL；下游：ScriptScheduler 调度 |

#### 步骤 5：生产加固（Phase 3E+3F）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 CT-DB-007 health_check() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\db\script_scheduler.py`（新建） |
| 验收标准 | Worker Pool + 系统级背压 + FTS5 + PG Docker + 数据迁移 + 备份 + 压测 |
| 验证命令 | `python -m pytest tests/unit/db/ -v --timeout=300` |
| G7 检查项 | 上游：WriteBatcher + DualDBRouter；下游：全系统增量扫描 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 3A | 新增 DDL 迁移失败 | init_db() 自动回滚未完成迁移；_MIGRATIONS 表不记录 = 幂等 |
| Phase 3B | PG 连接失败 | DualDBRouter.enable_offline_mode() → SQLite 降级 |
| Phase 3C | WriteBatcher 缓冲区溢出 | 背压机制降速 + DLQ 死信队列 |
| Phase 3D | file_script_map 数据填充遗漏 | 渐进填充——先核心模块（~5%），再全量 |
| Phase 3E+3F | 压测不通过 | 缩回 v2.x 模式——DualDBRouter 全部走 SQLite |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | dual_db_router.py | `D:\ZephyrAlpha\src\zephyr\db\dual_db_router.py` | ☐ | ☐ | ☐ |
| 2 | write_batcher.py | `D:\ZephyrAlpha\src\zephyr\db\write_batcher.py` | ☐ | ☐ | ☐ |
| 3 | script_scheduler.py | `D:\ZephyrAlpha\src\zephyr\db\script_scheduler.py` | ☐ | ☐ | ☐ |
| 4 | pg_lock.py | `D:\ZephyrAlpha\src\zephyr\db\pg_lock.py` | ☐ | ☐ | ☐ |
| 5 | test_dual_db_router.py | `D:\ZephyrAlpha\tests\unit\db\test_dual_db_router.py` | ☐ | ☐ | ☐ |
| 6 | test_write_batcher.py | `D:\ZephyrAlpha\tests\unit\db\test_write_batcher.py` | ☐ | ☐ | ☐ |
| 7 | docker-compose.yml | `D:\ZephyrAlpha\docker-compose.yml` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 (v2.0 完成，v3.0 待施工) |
| verification_status | passed——7/7 测试通过 | 蓝图审计 |
| code_alignment_verified | yes | 审计者 |

---

## §17 容量升级附录

> generation=2 蓝图必须填写。v3.0 容量升级方案是蓝图正文的一部分。

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 治理脚本数 | ~268（未入库） | `scripts/script_manifest.yaml` 条目数 |
| 模块数 | 51（隐式） | `module-id-registry.yaml` 条目数 |
| 并发 AI Agent | 1-2 | 运行时观察 |
| 数据库写入并发 | 1 Writer | SQLite WAL 单写锁 |
| 脚本并发执行 | 1（TaskQueue 串行） | TaskQueue 队列深度 |
| SQLite 热数据大小 | ~5 MB | `data/zalpha_metadata.db` 文件大小 |
| 连接池大小 | 2 | `database_manager.py` pool_size |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | SQLite 单 Writer 无法支撑 100 AI 并发写入 | PostgreSQL MVCC 双库分层 | 并发写 > 5 |
| GAP-002 | 无脚本注册表——增量扫描无法实现 | 6 张新表 DDL | 脚本数 > 500 |
| GAP-003 | 无批量写入路径——逐行 INSERT 吞吐不足 | WriteBatcher + PG COPY | 写入 QPS > 20/s |
| GAP-004 | 无分布式锁——跨 AI 模块级互斥缺失 | PostgreSQL Advisory Lock | AI Agent > 10 |
| GAP-005 | 无脚本调度——串行执行无法利用多核 | Worker Pool + Semaphore(40-100) | 脚本并发需求 > 5 |
| GAP-006 | 无系统级背压——100 AI 同时触发增量扫描可打满 CPU/内存 | Token Bucket + Scan Dedup + Queue 背压 | AI Agent > 20 |
| GAP-007 | 无全文搜索——10,000 脚本无法快速检索 | FTS5 + pg_trgm | 脚本数 > 1,000 |

### §17.3 架构决策

→ 见 **§18 决策记录**（D-INF012-01~10 完整决策表）

### §17.4 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v2.x | 1 | 基线 | SQLite + DuckDB 双引擎 + ATM + 13 个 .py | ✅ |
| v3.0 | 2 | 容量升级 | PostgreSQL 双库分层 + 6 张新表 + WriteBatcher + Worker Pool + 增量扫描 | ⚠️ 待施工 |

### 缺口清单

→ 见 **§17.2 缺口分析**（GAP-001~007 完整缺口表）

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| DualDBRouter | GAP-001 | `dual_db_router.py`（新建） | Phase 3B | 待施工 |
| WriteBatcher | GAP-003 | `write_batcher.py`（新建） | Phase 3C | 待施工 |
| ScriptScheduler | GAP-005 | `script_scheduler.py`（新建） | Phase 3F | 待施工 |
| 6 张新表 DDL | GAP-002 | `sqlite_schema.py`（扩展） | Phase 3A | 待施工 |
| PG Advisory Lock | GAP-004 | `pg_lock.py`（新建） | Phase 3C | 待施工 |
| FTS5 索引 | GAP-007 | `sqlite_schema.py`（扩展） | Phase 3F | 待施工 |

### §17.5 施工 Phase 路径图

| Phase | 名称 | 步骤 | 预计 |
|:---:|------|------|------|
| 3A | Schema Foundation | S-3A-01~05: modules/scripts/module_scripts/script_deps/file_script_map/script_executions DDL + CRUD + 迁移 v17–v20 | 3–5 天 |
| 3B | PostgreSQL 迁移 | S-3B-01~06: PG Docker + DDL + DualDBRouter + task_repo 适配 + events/gates 迁移 + 双模式测试 | 5–7 天 |
| 3C | 并发与调度 | S-3C-01~05: WriteBatcher + PG Advisory Lock + 连接池扩容 + Session 隔离 + 压力测试 | 3–5 天 |
| 3D | 增量扫描集成 | S-3D-01~04: file_script_map 填充 + git diff 解析 + 拓扑排序 + Worker Pool + 全量扫描 CLI | 3–4 天 |
| 3E | 生产加固 | S-3E-01~04: 容量重算 + 风险更新 + E2E 测试 + 文档补齐 | 2–3 天 |
| 3F | 容量加固 | S-3F-01~08: Worker Pool + 系统级背压 + FTS5 + PG Docker 配置 + 数据迁移 + 脚本超时 + PG 备份 + 压测 | 5–7 天 |

总施工周期: 23–31 天

### §17.6 施工进入条件

| # | 条件 | 确认方 | 状态 |
|---|------|------|------|
| 1 | Owner 确认 Decision 1–5（§17.3 5 项架构决策） | Owner | ☐ |
| 2 | Owner 批准 23–31 天施工周期 | Owner | ☐ |
| 3 | v2.x 现有 7 份测试全部绿（回归基线） | CI | ☐ |
| 4 | `data/zalpha_metadata.db` 最新备份已归档 | 施工者 | ☐ |
| 5 | PostgreSQL Docker 镜像已拉取至本地 | 施工者 | ☐ |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF012-01 | 双库分层——PostgreSQL（在线）+ SQLite（离线缓存） | A:PG单库 / B:纯SQLite+WriteBatcher / C:PG+SQLite双库 | C | PG 解决并发写；SQLite 保留零运维 fallback | 2026-05-10 |
| 2 | D-INF012-02 | WriteBatcher 批量写入——100ms/50条触发 PG COPY | A:逐行INSERT / B:WriteBatcher缓冲 | B | 逐行 INSERT ~20 writes/s → COPY 批量 ~2,000 rows/s | 2026-05-10 |
| 3 | D-INF012-03 | 增量扫描 = git diff → file_script_map → 脚本调度 | A:全量扫描 / B:增量扫描默认+全量可选 | B | 全量扫描 10,000 脚本耗时过长 | 2026-05-10 |
| 4 | D-INF012-04 | 分布式锁 = PostgreSQL Advisory Lock | A:Redis / B:MemoryLock / C:PG Advisory Lock | C | 零额外依赖；锁不需持久化但需跨进程 | 2026-05-10 |
| 5 | D-INF012-05 | Full Scan 周检可选，Incremental 为默认 | A:增量默认 / B:全量默认 | A | 日常增量 < 1min | 2026-05-10 |
| 6 | D-INF012-06 | 元数据存储选 SQLite（v2.x 基线） | A:PostgreSQL / B:SQLite / C:MongoDB | B | 零运维、单文件备份、WAL 读写并发 | 2026-05-03 |
| 7 | D-INF012-07 | OLAP 分析选 DuckDB 嵌入式 | A:ClickHouse / B:DuckDB | B | 零配置、嵌入式、Parquet 原生支持 | 2026-05-05 |
| 8 | D-INF012-08 | 原子事务选 ATM v2.0 两阶段提交 | A:2PC 经典 / B:ATM 自研 | B | 跨 SQLite/文件系统保证原子性 | 2026-05-05 |
| 9 | D-INF012-09 | 版本化迁移选内嵌 _MIGRATIONS 注册表 | A:Alembic / B:SQL 内联 | B | 项目规模用 SQL 内联即可 | 2026-05-05 |
| 10 | D-INF012-10 | 备份策略选 SQLite backup API | A:cp 命令 / B:SQLite backup API / C:Litestream | B | 内置 API 保证备份一致性 | 2026-05-05 |

---

## 蓝图特有：ATM v2.0 原子事务管理器

```yaml
atm_contract: P0-DB-ATM-v2
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

## 蓝图特有：DualDBRouter 路由规则

| 操作 | 在线模式（PostgreSQL 健康） | 离线模式（PG 不可达） |
|---|---|---|
| task_repo.get() | SQLite → miss? → PG | SQLite |
| task_repo.create() | PG → async sync to SQLite | SQLite |
| task_repo.transition() | PG（写事务内）→ sync SQLite | SQLite |
| events 写入 | PG → async sync to SQLite | SQLite |
| script_executions 写入 | PG via WriteBatcher | SQLite |
| modules/scripts CRUD | PG（管理操作）→ sync SQLite | SQLite |
| olap_engine 查询 | SQLite + DuckDB | SQLite + DuckDB |
| audit_schema 查询 | SQLite + PG UNION | SQLite only |

---

## 蓝图特有：WriteBatcher 批量写入

| 参数 | 值 |
|---|---|
| flush_interval_ms | 100 |
| batch_size | 50 |
| max_buffer_size | 500 |
| retry_attempts | 3 |
| retry_backoff_ms | 200 |

| 场景 | 逐行 INSERT | WriteBatcher (50条/批) | 提升 |
|---|---|---|---|
| 100 脚本结果写入 | ~5s（串行排队） | ~50ms（1 批 COPY） | **100x** |
| 1,500 脚本结果写入（极端峰值） | ~75s | ~1.5s（30 批） | **50x** |

---

## 蓝图特有：v3.0 Schema DDL

### 新增 6 张表

| # | 表名 | 用途 | 预估行数 | 索引数量 |
|---|---|---|---|---|
| 1 | `modules` | 1,500 模块的元信息注册表 | 1,500 | 3 |
| 2 | `scripts` | 10,000 治理脚本的注册表 | 10,000 | 4 |
| 3 | `module_scripts` | 模块→脚本多对多映射 | ~50,000 | 3 |
| 4 | `script_dependencies` | 脚本间 DAG 依赖关系 | ~5,000 | 2 |
| 5 | `file_script_map` | 文件→脚本增量触发表 | ~30,000 | 3 |
| 6 | `script_executions` | 脚本执行记录（运行日志） | ~500,000/月 | 5 |

### modules 表 DDL

```sql
CREATE TABLE IF NOT EXISTS modules (
    module_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    layer           TEXT NOT NULL CHECK(layer IN ('infrastructure', 'domain', 'application', 'cross_layer')),
    status          TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'deprecated', 'archived')),
    owner           TEXT,
    scripts_count   INTEGER DEFAULT 0,
    files_count     INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_modules_layer  ON modules(layer);
CREATE INDEX IF NOT EXISTS idx_modules_status ON modules(status);
CREATE INDEX IF NOT EXISTS idx_modules_owner  ON modules(owner);
```

### scripts 表 DDL

```sql
CREATE TABLE IF NOT EXISTS scripts (
    script_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    file_path       TEXT NOT NULL UNIQUE,
    language        TEXT NOT NULL CHECK(language IN ('python','sql','shell','yaml','json','other')),
    category        TEXT NOT NULL CHECK(category IN ('lint','audit','gate','security','performance','compliance','custom')),
    avg_duration_ms INTEGER DEFAULT 0,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_scripts_category ON scripts(category);
CREATE INDEX IF NOT EXISTS idx_scripts_language  ON scripts(language);
CREATE INDEX IF NOT EXISTS idx_scripts_active    ON scripts(is_active);
CREATE INDEX IF NOT EXISTS idx_scripts_name      ON scripts(name);
```

### module_scripts 表 DDL

```sql
CREATE TABLE IF NOT EXISTS module_scripts (
    module_id       TEXT NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    script_id       TEXT NOT NULL REFERENCES scripts(script_id) ON DELETE CASCADE,
    priority        INTEGER DEFAULT 0,
    is_incremental  INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (module_id, script_id)
);
CREATE INDEX IF NOT EXISTS idx_ms_module   ON module_scripts(module_id);
CREATE INDEX IF NOT EXISTS idx_ms_script   ON module_scripts(script_id);
CREATE INDEX IF NOT EXISTS idx_ms_priority ON module_scripts(module_id, priority);
```

### script_dependencies 表 DDL

```sql
CREATE TABLE IF NOT EXISTS script_dependencies (
    script_id           TEXT NOT NULL REFERENCES scripts(script_id) ON DELETE CASCADE,
    depends_on_script_id TEXT NOT NULL REFERENCES scripts(script_id) ON DELETE CASCADE,
    dependency_type     TEXT NOT NULL DEFAULT 'hard' CHECK(dependency_type IN ('hard', 'soft')),
    PRIMARY KEY (script_id, depends_on_script_id)
);
CREATE INDEX IF NOT EXISTS idx_script_deps_on ON script_dependencies(depends_on_script_id);
```

### file_script_map 表 DDL

```sql
CREATE TABLE IF NOT EXISTS file_script_map (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file_pattern    TEXT NOT NULL,
    match_type      TEXT NOT NULL CHECK(match_type IN ('exact', 'glob', 'module')),
    script_id       TEXT NOT NULL REFERENCES scripts(script_id) ON DELETE CASCADE,
    module_id       TEXT REFERENCES modules(module_id) ON DELETE SET NULL,
    priority        INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(file_pattern, script_id)
);
CREATE INDEX IF NOT EXISTS idx_fsm_script  ON file_script_map(script_id);
CREATE INDEX IF NOT EXISTS idx_fsm_module  ON file_script_map(module_id);
CREATE INDEX IF NOT EXISTS idx_fsm_pattern ON file_script_map(file_pattern);
```

### script_executions 表 DDL

```sql
CREATE TABLE IF NOT EXISTS script_executions (
    execution_id    TEXT PRIMARY KEY,
    script_id       TEXT NOT NULL REFERENCES scripts(script_id) ON DELETE CASCADE,
    session_id      TEXT,
    trigger_type    TEXT NOT NULL CHECK(trigger_type IN ('incremental','full_scan','manual','pre_commit')),
    status          TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','running','passed','failed','timeout','cancelled')),
    started_at      TEXT,
    completed_at    TEXT,
    duration_ms     INTEGER,
    exit_code       INTEGER,
    stdout_summary  TEXT,
    stderr_summary  TEXT,
    findings_count  INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_se_script   ON script_executions(script_id);
CREATE INDEX IF NOT EXISTS idx_se_session  ON script_executions(session_id);
CREATE INDEX IF NOT EXISTS idx_se_status   ON script_executions(status);
CREATE INDEX IF NOT EXISTS idx_se_created  ON script_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_se_trigger  ON script_executions(trigger_type);
```

### PostgreSQL DDL 适配

| SQLite 类型 | PostgreSQL 类型 | 说明 |
|---|---|---|
| `TEXT` | `VARCHAR(255)` | 所有业务 ID / name 字段 |
| `TEXT` (长文本) | `TEXT` | stdout/stderr summary |
| `INTEGER` | `INTEGER` | 计数器/标志位 |
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` | 自增 ID |
| `TEXT PRIMARY KEY` | `VARCHAR(255) PRIMARY KEY` | 字符串主键 |
| `datetime('now')` | `NOW()` | 时间函数 |

---

## 蓝图特有：file_script_map 增量扫描

```sql
WITH matched AS (
    SELECT DISTINCT fsm.script_id, fsm.priority
    FROM file_script_map fsm
    WHERE fsm.match_type = 'exact'
      AND fsm.file_pattern IN ({placeholders})
    UNION
    SELECT DISTINCT fsm.script_id, fsm.priority
    FROM file_script_map fsm
    WHERE fsm.match_type = 'glob'
      AND ({glob_conditions})
    UNION
    SELECT DISTINCT ms.script_id, ms.priority
    FROM module_scripts ms
    WHERE ms.module_id IN ({module_placeholders})
      AND ms.is_incremental = 1
)
SELECT s.script_id, s.name, s.file_path, s.category, s.avg_duration_ms,
       COALESCE(m.priority, 999) AS final_priority
FROM matched m
JOIN scripts s ON s.script_id = m.script_id
WHERE s.is_active = 1
ORDER BY final_priority ASC, s.avg_duration_ms ASC;
```

---

## 蓝图特有：ScriptScheduler Worker Pool

| 参数 | 值 | 推导依据 |
|---|---|---|
| `pool_size`（常态） | **40** | i7-12700KF 12核20线程——预留 8 线程给 AI Agent + PG + OS |
| `pool_size`（弹性峰值） | **100** | 100 AI 同时触发时的极端情况 |
| `per_script_timeout` | **300s**（5 分钟） | P95 < 60s，5 分钟覆盖 99.9% |
| `per_script_max_memory` | **512 MB** | subprocess 级别 |
| `queue_max_size` | **1,500** | 100 AI × 15 脚本 |

五层保护链路：Admission Control（Token Bucket rate=10/s）→ Scan Deduplication（TTL 5s）→ PriorityQueue（max_size=1,500）→ Worker Pool（Semaphore 40-100）→ WriteBatcher（DB 写入背压）

---

## 蓝图特有：PostgreSQL 部署配置

| 参数 | 值 | 推导 |
|---|---|---|
| `shared_buffers` | **4 GB** | 64GB RAM × 25% |
| `effective_cache_size` | **12 GB** | 64GB × 50% |
| `max_connections` | **120** | 100 AI + 10 管理连接 + 10 余量 |
| `work_mem` | **64 MB** | 40 并发 × 64MB = 2.5GB 峰值 |
| `statement_timeout` | **30s** | 防止慢查询占用连接 |
| `idle_in_transaction_session_timeout` | **60s** | 防止 AI 持有事务不释放 |

asyncpg 连接池：`min_size=10, max_size=50, max_queries=50000, max_inactive_connection_lifetime=300`

---

## 蓝图特有：FTS5 全文搜索

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS scripts_fts USING fts5(
    script_id UNINDEXED, name, file_path, category, language, description,
    content='scripts', content_rowid='rowid', tokenize='porter unicode61'
);
```

| 模式 | FTS5 索引位置 |
|---|---|
| 在线模式（PostgreSQL） | SQLite 本地缓存 + PostgreSQL `pg_trgm` GIN 索引 |
| 离线模式 | SQLite FTS5 |

---

## 蓝图特有：Session 管理表

```sql
CREATE TABLE IF NOT EXISTS sessions (
    session_id      TEXT PRIMARY KEY,
    agent_id        TEXT,
    status          TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'idle', 'disconnected', 'closed')),
    connection_type TEXT NOT NULL DEFAULT 'pg' CHECK(connection_type IN ('pg', 'sqlite', 'offline')),
    last_active_at  TEXT NOT NULL DEFAULT (datetime('now')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    closed_at       TEXT
);
```

---

## 蓝图特有：运营卓越性

### 自愈设计

| 场景 | 自动检测 | 自动修复 | 人工介入条件 |
|------|:---:|:---:|------|
| WAL 文件无限增长 | wal_autocheckpoint=4096 | 自动 checkpoint | WAL > 100MB 触发告警 |
| 数据库文件损坏 | PRAGMA integrity_check（每60s） | 自动从最新备份恢复 | 恢复失败 → escalation:owner |
| 连接泄漏 | connection_leak_detector | 自动关闭超时连接 | 泄漏 > 10个 → escalation:owner |
| 慢查询积累 | query_metrics >500ms | 写入 slow_queries 表 | 单日 > 20条 → escalation:owner |
| 磁盘空间不足 | disk_monitor | 自动清理过期备份 + WAL TRUNCATE | 剩余 < 0.5GB → escalation:owner |
| 事务死锁/超时 | ATM tx_timeout 30s | 自动 ROLLBACK | 连续超时 3 次 → escalation:owner |
| Schema 版本落后 | schema_version() < MIGRATIONS max | init_db() 自动补齐迁移 | 迁移失败 → escalation:owner |

### AI 可消费的 DB 诊断输出

> 已实现。接口签名：`ai_diagnostic_report() -> dict`，返回 `{summary, health, stats, schema_drift, query_performance, findings}`。源码见 `D:\ZephyrAlpha\src\zephyr\db\database_manager.py`。

### Database-as-Code 原则

| # | 原则 |
|---|------|
| 1 | DDL 在 sqlite_schema.py 中定义为 Python 字符串常量——不是外置 .sql 文件 |
| 2 | Schema 版本化：_MIGRATIONS 注册表 = single source of truth |
| 3 | init_db() 幂等——可在 CI/CD/本地任意环境重复执行 |
| 4 | PRAGMA 基线：所有连接通过 get_db_connection() 统一配置——不允许手动调 PRAGMA |

### 备份恢复演练

| 项目 | 内容 |
|------|------|
| 频率 | 每月 1 次自动恢复演练 |
| 步骤 | 从最新备份恢复到临时路径 → integrity_check → 对比表数量/行数 → 删除临时 DB → 记录结果 |
| 通过标准 | 恢复 DB 的 table_count == 生产 DB && integrity_check == 'ok' |
| 失败处理 | escalation:owner + 标记备份策略为 UNTRUSTED |

### PostgreSQL 备份策略

| 备份类型 | 工具 | 频率 | 保留策略 |
|---|---|---|---|
| 逻辑备份 | `pg_dump -Fc` | 每日凌晨 3:00 | 保留 7 天 |
| 物理备份（可选） | `pg_basebackup` | 每周日凌晨 2:00 | 保留 4 周 |
| WAL 归档（可选） | `archive_command` | 持续 | 保留 7 天（支持 PITR） |

### 演进方向

| # | 能力 | 当前状态 | 何时需要 |
|---|------|:---:|------|
| 1 | SQLCipher 透明加密 | ❌ | L04+ 金融敏感数据落库 |
| 2 | 只读副本（Read Replica） | ❌ | 项目 > 1000 模块、多 IDE 同时读 |
| 3 | 在线备份（Litestream） | ❌ | DB > 100MB 且备份耗时长 |
| 4 | 数据脱敏 | ❌ | 引入外部协作者 |
| 5 | 自适应 VACUUM | ❌ | DB > 500MB |
| 6 | 行级安全（RLS via Triggers） | ❌ | 多 Agent 多租户写入 |
| 7 | 查询缓存（Prepared Statement Cache） | ❌ | 高频查询场景 |
| 8 | CDC 变更流 | ✅ | events 表即天然 CDC |
| 9 | SQLite → PostgreSQL 零停机迁移 | ❌ | 团队 > 3 人或生产环境要求 |
| 10 | 自适应慢查询阈值 | ❌ | 负载波动大时 |

---

## 蓝图特有：SSoT 漂移与一致性

b_db.yaml（v2.2.0）与磁盘实际代码一致。蓝图 v3.7 是 canonical 真源，无漂移。

漂移防护：每次修改 db/ 目录下文件后，MUST 同步更新 b_db.yaml。CI 门禁：启动时对比 b_db.yaml.files 与 `D:\ZephyrAlpha\src\zephyr\db\*.py` glob 结果。不一致 → 阻断启动。

---

## 蓝图特有：接口契约（CT-DB-001~007）

### CT-DB-001：task_repo CRUD 契约

```yaml
contract_id: CT-DB-001
provider: MOD-INF-012 (TaskRepository)
consumers: [MOD-INF-006, MOD-INF-009, MOD-INF-013]
operations:
  create: {input: "Task (Pydantic V2, 62 fields)", output: "TaskCard", idempotency: "task_id UNIQUE"}
  get: {input: "task_id: str", output: "TaskCard | None", filter: "is_deleted = 0"}
  transition: {input: "task_id + to_status + session_id?", output: "TaskCard", atomicity: "G1门禁+状态写入+events同一写事务"}
  upsert: {input: "Task + files?", output: "TaskCard", semantics: "ON CONFLICT DO UPDATE"}
  delete: {input: "task_id: str", output: "bool", semantics: "软删除 is_deleted=1"}
  list_by_*: {input: "filter params", output: "list[TaskCard]", filter: "is_deleted = 0"}
```

### CT-DB-002：ATM 事务契约

```yaml
contract_id: CT-DB-002
provider: MOD-INF-012 (AtomicTransactionManager)
consumers: [MOD-INF-006, MOD-INF-010]
operations:
  transaction: {isolation: "BEGIN IMMEDIATE", timeout: "30s", idempotency: "tx_idempotency 去重", compensation: "SQLite COMMIT成功但文件rename失败→compensation event"}
  write_file: {safety: "InputSanitizer.validate_path", atomicity: "tmp→fsync→os.replace", rollback: ".bak 文件恢复"}
```

### CT-DB-003：OLAP 查询契约

```yaml
contract_id: CT-DB-003
provider: MOD-INF-012 (OLAPEngine)
consumers: [MOD-INF-010, MOD-INF-015]
operations:
  task_progress_trend: {input: "period+limit+phase?", output: "list[TrendRow]", protection: "参数化+period白名单+limit范围校验"}
  archive_events: {input: "days+archive_dir?", output: "{archived_count, archive_files, deleted_count}", guarantee: "DuckDB读取→Parquet写入→SQLite DELETE"}
  query_unified_events: {input: "limit", output: "list[TrendRow]", semantics: "UNION ALL (SQLite热+Parquet冷)"}
```

### CT-DB-004：运维管理契约

```yaml
contract_id: CT-DB-004
provider: MOD-INF-012 (DatabaseManager)
consumers: [MOD-INF-015, MOD-INF-001]
operations:
  health_check: {output: "HealthStatus {healthy, schema_version, db_size_bytes, wal_size_bytes, table_count, integrity_ok}"}
  backup: {input: "label?", output: "Path", consistency: "SQLite backup API", retention: "7天日备份+4周末备份"}
  maintenance: {output: "{vacuum, integrity, wal_truncated, pre_health, post_health}"}
  stats: {output: "{task_count, active_task_count, event_count, gate_count, ke_count, slow_query_count, db_size_mb, wal_size_mb, schema_version}"}
```

### CT-DB-005：脚本注册与查询契约

```yaml
contract_id: CT-DB-005
provider: MOD-INF-012 (ScriptRegistry)
consumers: [MOD-INF-006, MOD-INF-009, MOD-INF-010]
status: v3.0 设计阶段
operations:
  register_module: {input: "ModuleRegistration", output: "bool", idempotency: "module_id UNIQUE"}
  register_script: {input: "ScriptRegistration", output: "bool", idempotency: "script_id UNIQUE"}
  link_module_script: {input: "module_id, script_id, priority?, is_incremental?", output: "bool", semantics: "INSERT OR IGNORE"}
  link_file_script: {input: "file_pattern, match_type, script_id, module_id?", output: "bool", semantics: "INSERT OR IGNORE"}
  resolve_scripts_by_files: {input: "changed_files, changed_modules", output: "list[ScriptToRun]", semantics: "三路匹配"}
  resolve_scripts_by_module: {input: "module_id, incremental_only", output: "list[ScriptToRun]"}
  get_execution_dag: {input: "script_ids", output: "{edges, topological_order}", semantics: "Kahn's algorithm"}
```

### CT-DB-006：脚本执行记录契约

```yaml
contract_id: CT-DB-006
provider: MOD-INF-012 (ScriptExecutionLogger + WriteBatcher)
consumers: [MOD-INF-006, MOD-INF-020, MOD-INF-010]
status: v3.0 设计阶段
operations:
  log_execution_start: {input: "execution_id, script_id, session_id, trigger_type", output: "bool"}
  log_execution_result: {input: "execution_id, status, duration_ms, exit_code, ...", output: "bool", semantics: "UPDATE via WriteBatcher"}
  batch_log_results: {input: "list[ExecutionResultRow]", output: "int", semantics: "WriteBatcher.enqueue 100ms/50条"}
  query_execution_trend: {input: "script_id?, days, trigger_type?", output: "list[ExecutionTrendRow]"}
  query_session_audit: {input: "session_id", output: "list[ExecutionAuditRow]"}
```

### CT-DB-007：DualDBRouter 契约

```yaml
contract_id: CT-DB-007
provider: MOD-INF-012 (DualDBRouter)
consumers: [MOD-INF-006, MOD-INF-009, MOD-INF-007, ALL modules that consume task_repo/events/gates]
status: v3.0 设计阶段
operations:
  read: {input: "query, params", output: "list[dict]", semantics: "SQLite优先→PG fallback"}
  write: {input: "query, params", output: "None", semantics: "在线→PG；离线→SQLite"}
  write_batch: {input: "query, rows", output: "int", semantics: "在线→PG COPY；离线→SQLite executemany"}
  enable_offline_mode / disable_offline_mode: {semantics: "零停机降级/恢复"}
  health_check: {output: "{pg_healthy, sqlite_healthy, mode, pg_pool_size}"}
guarantees:
  - "在线模式下所有写操作走 PostgreSQL——无数据丢失风险"
  - "离线模式下写 SQLite——恢复后需手动或自动同步"
  - "读操作在 99.9% 情况下走 SQLite 缓存（<1ms）"
```

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

### 蓝图拆分判定标准

| 判定条件 | 动作 | 示例 |
|---------|------|------|
| 单章 > 3000 token | 拆为子节 | §10 拆为 §10.1~§10.4 |
| 单章涉及 > 3 个独立主题 | 按主题拆子节 | §17 容量升级按基线/缺口/决策/版本拆 |
| 子节仍 > 3000 token | 提取为蓝图特有独立段 | Schema DDL 提取为"蓝图特有：v3.0 Schema DDL" |
| 表格行 > 20 行 | 考虑按分类拆为多表 | §14 风险按 v2.x/v3.0 分类 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

本蓝图不涉及文件废弃/迁移/删除。v3.0 为纯新增设计，所有变更均为新建表/新增接口/新增模块。

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
| 1 | 元数据注册表 | PS-STD-001 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | latest | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射 |
| 3 | 蓝图体系架构标准 | PS-STD-005 | 1.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\blueprint-architecture-standard.md` | 三级金字塔 + belongs_to |
| 4 | 模块ID注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 编号注册 |
| 5 | ADR-0030 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0030-sqlite-task-metadata-store.md` | SQLite元数据层决策 |
| 6 | ADR-0041 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0041-session-handoff-protocol.md` | Session Handoff协议 |
| 7 | AI自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | AI操作权限 |
| 8 | DB YAML SSoT | — | 2.2.0 | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | DB YAML真源 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | ChromaDB (VMS) | `D:\ZephyrAlpha\src\zephyr\vector_memory\` | 向量数据持久化 | ChromaDB 管语义向量检索，SQLite 管结构化元数据——互补 |
| 2 | 脚本系统 run_all.py | `D:\ZephyrAlpha\scripts\run_all.py` | DB 完整性检查 | run_all.py 检查项目级一致性，database_manager.health_check() 检查 DB 物理完整性——互补 |
| 3 | MOD-INF-020 audit-trail | `D:\ZephyrAlpha\src\zephyr\audit_trail\` | 审计事件存储 | Audit Trail 消费 events 表做不可变日志链，本模块是 events 的生产者——上下游关系 |

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
| 8 | `base_repo.py` | `D:\ZephyrAlpha\src\zephyr\db\base_repo.py` | 辅助源码 | 已实现 |
| 9 | `gate_repo.py` | `D:\ZephyrAlpha\src\zephyr\db\gate_repo.py` | 辅助源码 | 已实现 |
| 10 | `circuit_breaker_repo.py` | `D:\ZephyrAlpha\src\zephyr\db\circuit_breaker_repo.py` | 辅助源码 | 已实现 |
| 11 | `query.py` | `D:\ZephyrAlpha\src\zephyr\db\query.py` | 辅助源码 | 已实现 |
| 12 | `transition.py` | `D:\ZephyrAlpha\src\zephyr\db\transition.py` | 辅助源码 | 已实现 |
| 13 | `zalpha_metadata.db` | `D:\ZephyrAlpha\data\zalpha_metadata.db` | 数据文件 | 运行时生成 |
| 14 | `data/backups/` | `D:\ZephyrAlpha\data\backups\` | 备份目录 | 运行时生成 |
| 15 | `data/warehouse/` | `D:\ZephyrAlpha\data\warehouse\` | 冷数据归档 | 运行时生成 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 数据库——task_repo+sqlite_schema+ATM已实现，olap_engine待施工

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/db/atomic_transaction_manager.py` | ✅ 已实现 | |
| `src/zephyr/db/audit_schema.py` | ✅ 已实现 | |
| `src/zephyr/db/base_repo.py` | ✅ 已实现 | |
| `src/zephyr/db/circuit_breaker_repo.py` | ✅ 已实现 | |
| `src/zephyr/db/database_manager.py` | ✅ 已实现 | |
| `src/zephyr/db/gate_repo.py` | ✅ 已实现 | |
| `src/zephyr/db/olap_engine.py` | ✅ 已实现 | |
| `src/zephyr/db/query.py` | ✅ 已实现 | |
| `src/zephyr/db/query_metrics.py` | ✅ 已实现 | |
| `src/zephyr/db/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/db/task_repo.py` | ✅ 已实现 | |
| `src/zephyr/db/transition.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_task_repo.py` | ✅ 已实现 | |
| `tests/unit/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/unit/test_atomic_transaction_manager.py` | ✅ 已实现 | |
| `tests/unit/test_olap_engine.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本模块的核心架构设计 | **本蓝图 §1-§10** | — |
| 本模块的接口契约 | **本蓝图 §4 + 蓝图特有：CT-DB-001~007** | b_db.yaml（次要副本） |
| 本模块的数据结构定义 | **本蓝图 §4.2 + sqlite_schema.py 磁盘代码** | — |
| 本模块的施工步骤 | **本蓝图 §16** | — |
| 本模块的测试覆盖要求 | **本蓝图 §9** | — |
| 磁盘文件清单 | **`D:\ZephyrAlpha\src\zephyr\db\*.py`（13 文件）** | b_db.yaml（次要副本） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 触发条件

| 触发场景 | 关键词 | 操作 |
|---------|--------|------|
| 修改 `src/zephyr/db/` 下任何文件 | database, db, sqlite, duckdb, atm, task_repo, olap | 读本蓝图 §4 接口契约 + §0 代码对齐 |
| 新增数据库表/索引/视图 | DDL, schema, migration, table | 读 §5 约束条件 + 蓝图特有：Schema DDL |
| 修改 TaskCard 模型或状态机 | task, status, transition, state_machine | 读 §4 TaskRepository + §3.3 状态生命周期 |
| v3.0 容量升级施工 | postgresql, write_batcher, dual_db, worker_pool | 读 §17 容量升级附录 + §16 施工指引 |
| 数据库运维/故障排查 | health_check, backup, wal, integrity | 读蓝图特有：运营卓越性 |

### 导航路径

新 AI 找到本文件：`registry-of-registries.yaml` → `REG-BLUEPRINT-001` → `blueprint-registry.yaml` → `MOD-INF-012` → 本文件

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-006 (task-system) | §4 TaskRepository 接口、CT-DB-001 |
| Tier 1 | MOD-INF-010 (feedback-loop) | CT-DB-003 OLAP 查询契约、CT-DB-002 ATM 事务 |
| Tier 1 | MOD-INF-020 (audit-trail) | CT-DB-001 审计互锁、events 表不可变日志 |
| Tier 2 | MOD-INF-009 (pipeline) | task_repo list_by_* 查询 |
| Tier 2 | MOD-INF-013 (mcp-servers) | task_repo create/upsert |
| Tier 2 | MOD-INF-007 (gate-engine) | gates 表 + events 表共享写入 |
| Tier 2 | MOD-INF-015 (system-telemetry) | CT-DB-004 DatabaseManager stats + health |
| Tier 3 | MOD-INF-001 (capacity-assurance) | CT-DB-004 health_check() |
| Tier 3 | MOD-INF-016 (shared+core) | TaskCard 模型定义（Pydantic V2） |

### 变更同步规则

| 变更类型 | Tier 1（核心消费者） | Tier 2（集成系统） | Tier 3（监控/工具） |
|---------|------------------|------------------|------------------|
| task_repo 接口签名变更 | 下游检查兼容性 | pipeline 检查查询字段 | shared+core 更新 TaskCard |
| events 表结构变更 | audit-trail 检查审计链完整性 | gate-engine 检查写入兼容 | — |
| OLAP 查询 schema 变更 | feedback-loop 检查 Dashboard | — | system-telemetry 检查监控 |
| DatabaseManager stats 字段变更 | — | system-telemetry 检查面板 | capacity-assurance 检查告警 |
| 新增表/索引 | 通知所有 Tier 1 | — | — |
| ATM 契约变更 | 通知 task-system + feedback-loop | — | — |

### 修改条件

| 变更类型 | 审批要求 | AI 权限 |
|---------|---------|:---:|
| 接口契约新增/修改（CT-DB-*） | Owner 审批 + 通知所有消费者 | ❌ AI 不可自主 |
| 数据模型重命名/删除字段 | Owner 审批 + 迁移方案 | ❌ AI 不可自主 |
| 新增表/索引/视图 | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 施工步骤微调（测试用例、路径修正） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 风险矩阵补充（§14 新增 R15+） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
| 容量估算更新（§5.2） | AI 可自主——蓝图 patch +1 | ✅ AI 可自主 |
