---


task_id: TASK-MOD-INF-001-0003
module_id: MOD-INF-001
title: "数据库 Schema 实现：5 张核心表 DDL"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:57:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\ddl.sql"
acceptance_criteria:
  - "ddl.sql 包含全部 5 张表的完整 CREATE TABLE 语句：ai_provenance / capacity_metrics / error_budget / token_budget_usage / capacity_metrics_hourly"
  - "schema.py 提供 SchemaManager 类，含 init_db() / migrate() / verify() 方法"
  - "ai_provenance 表有 prev_hash + curr_hash 字段，支持 hash 链完整性校验"
  - "capacity_metrics 表 TTL 7 天，在 schema.py 中通过 ttl_cleanup() 实现"
rollback_instructions:
  - "删除 src/zephyr/capacity_assurance/schema.py"
  - "删除 src/zephyr/capacity_assurance/ddl.sql"
  - "删除 .audit_cache/ 下的测试数据库文件"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§5.2 数据库 Schema", "§21.1 #20 MetricsWriteBuffer", "§21.2 #21 capacity_metrics_hourly"]
    purpose: "提取全部 5 张表的 DDL 定义和扩展 Schema"
  - source: "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
tags:
  - capacity-assurance
  - database-schema
  - sqlite
phase: phase_1_scaffold
estimated_effort_minutes: 45
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §3 数据库设计 5表DDL"
description: "数据库 Schema 实现：5 张核心表 DDL"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\ddl.sql"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 13500
timeout_minutes: 45
depends_on:
  - TASK-MOD-INF-001-0001
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# 数据库 Schema 实现：5 张核心表 DDL

## 1. 任务来源

从蓝图 §5.2 数据库 Schema 提取 5 张核心表的 DDL 定义：

| 表名 | 治理层级 | 特性 |
|------|---------|------|
| `ai_provenance` | Immutable Core | 只追加 + hash 链，不可删除 |
| `capacity_metrics` | AI-Modifiable | 7 天 TTL，含 ts 索引 |
| `error_budget` | Human-Gated/AI-Modifiable | 五级响应 tracking |
| `token_budget_usage` | AI-Modifiable | 7 天 TTL，含 model_name / cost_usd |
| `capacity_metrics_hourly` | AI-Modifiable | v2.3.0 新增，压缩聚合表 |

另需关注 §21.2 盲点 #20（MetricsWriteBuffer）+ #21（Telemetry 存储生命周期）。

## 2. 施工内容

### 2.1 创建 DDL SQL 文件

创建 `D:\ZephyrAlpha\src\\zephyr\\shared\\ddl.sql`，包含：

```sql
-- ai_provenance（Immutable Core）
CREATE TABLE IF NOT EXISTS ai_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    field TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    author_agent TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    audit_result TEXT NOT NULL,
    prev_hash TEXT,
    curr_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prov_module ON ai_provenance(module);
CREATE INDEX IF NOT EXISTS idx_prov_agent ON ai_provenance(author_agent);

-- capacity_metrics（AI-Modifiable，7d TTL）
CREATE TABLE IF NOT EXISTS capacity_metrics (
    ts TEXT NOT NULL,
    sli_id TEXT NOT NULL,
    value REAL NOT NULL,
    governance_layer TEXT,
    runtime_plane TEXT,
    compensated INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_metrics_ts ON capacity_metrics(ts);
CREATE INDEX IF NOT EXISTS idx_metrics_sli ON capacity_metrics(sli_id);

-- error_budget（v2.0.0）
CREATE TABLE IF NOT EXISTS error_budget (
    slo_id TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    budget_total REAL NOT NULL,
    budget_consumed REAL NOT NULL,
    budget_remaining REAL NOT NULL,
    response_tier TEXT NOT NULL,
    last_updated TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_eb_slo ON error_budget(slo_id);

-- token_budget_usage（v2.0.0）
CREATE TABLE IF NOT EXISTS token_budget_usage (
    ts TEXT NOT NULL,
    budget_level TEXT NOT NULL,
    level_id TEXT NOT NULL,
    tokens_consumed INTEGER NOT NULL,
    tokens_remaining INTEGER NOT NULL,
    model_name TEXT,
    cost_usd REAL
);
CREATE INDEX IF NOT EXISTS idx_tbu_ts ON token_budget_usage(ts);

-- capacity_metrics_hourly（v2.3.0）
CREATE TABLE IF NOT EXISTS capacity_metrics_hourly (
    slo_id TEXT NOT NULL,
    hour_bucket TEXT NOT NULL,
    avg_value REAL,
    p99_value REAL,
    max_value REAL,
    sample_count INTEGER,
    governance_layer TEXT,
    runtime_plane TEXT
);
CREATE INDEX IF NOT EXISTS idx_cmh_slo_hour ON capacity_metrics_hourly(slo_id, hour_bucket);
```

### 2.2 创建 `schema.py`

创建 `D:\ZephyrAlpha\src\\zephyr\\shared\\schema.py`，实现：
- `SchemaManager.init_db(db_path: str)`: 执行 DDL，创建全部表
- `SchemaManager.migrate()`: 从旧 Schema 版本迁移
- `SchemaManager.verify()`: 校验表结构完整性
- `SchemaManager.ttl_cleanup()`: 清理超过 TTL 的 capacity_metrics 行
- `get_db_path()`: 从环境变量 `CAPACITY_METRICS_DB_PATH` / `AI_AUDIT_PROVENANCE_DB_PATH` 读取路径

### 2.3 集成 MetricsWriteBuffer（盲点 #20）

在 `schema.py` 中实现 `MetricsWriteBuffer` 的 SQLite 写入接口：
- `executemany()` 批量写入
- 事务包裹

## 3. 验收标准

1. `ddl.sql` 包含全部 5 张表的 CREATE TABLE 语句
2. `schema.py` 中 `init_db()` 可创建内存 SQLite DB 并含全部索引
3. `ai_provenance` 表在 verify() 中校验 hash 链完整性
4. `ttl_cleanup()` 正确清理 capacity_metrics 和 token_budget_usage 超期数据
5. `compensated` 字段（盲点 #30）在 capacity_metrics 中存在