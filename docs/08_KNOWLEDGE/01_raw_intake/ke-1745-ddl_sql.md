---
module_id: KE-1655----ddl-sql-003
status: active
title: 2.1 创建 DDL SQL 文件
category: module_blueprint
ttl: permanent
---

# 2.1 创建 DDL SQL 文件

2.1 创建 DDL SQL 文件

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
