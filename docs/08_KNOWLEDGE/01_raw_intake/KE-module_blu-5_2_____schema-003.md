---
module_id: KE-module_blu-5_2_____schema-003
title: 5.2 数据库 Schema
category: module_blueprint
---

# 5.2 数据库 Schema

5.2 数据库 Schema

```sql
-- ai_provenance（Immutable Core，只追加 + hash 链）
CREATE TABLE ai_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL, field TEXT NOT NULL,
    old_value TEXT, new_value TEXT,
    author_agent TEXT NOT NULL, timestamp TEXT NOT NULL,
    audit_result TEXT NOT NULL, prev_hash TEXT, curr_hash TEXT NOT NULL
);

-- capacity_metrics（AI-Modifiable，7 天 TTL）
CREATE TABLE capacity_metrics (
    ts TEXT NOT NULL, sli_id TEXT NOT NULL,
    value REAL NOT NULL, governance_layer TEXT, runtime_plane TEXT
);
CREATE INDEX idx_metrics_ts ON capacity_metrics(ts);

-- error_budget（v2.0.0 新增，Human-Gated 阈值 + AI-Modifiable 消耗）
CREATE TABLE error_budget (
    slo_id TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    budget_total REAL NOT NULL,
    budget_consumed REAL NOT NULL,
    budget_remaining REAL NOT NULL,
    response_tier TEXT NOT NULL,
    last_updated TEXT NOT NULL
);
CREATE INDEX idx_eb_slo ON error_budget(slo_id);

-- token_budget_usage（v2.0.0 新增，AI-Modifiable，7 天 TTL）
CREATE TABLE token_budget_usage (
    ts TEXT NOT NULL,
    budget_level TEXT NOT NULL,
    level_id TEXT NOT NULL,
    tokens_consumed INTEGER NOT NULL,
    tokens_remaining INTEGER NOT NULL,
    model_name TEXT,
    cost_usd REAL
);
CREATE INDEX idx_tbu_ts ON token_budget_usage(ts);
```
