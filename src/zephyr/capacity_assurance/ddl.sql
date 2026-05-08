-- ============================================================================
-- ZephyrAlpha 容量保障体系 — 数据库 DDL
-- 真源：蓝图 MOD-INF-001 §5.2 数据库 Schema
-- 版本：v2.6.0 | 创建：2026-05-07
-- ============================================================================

-- ----------------------------------------------------------------------------
-- ai_provenance（Immutable Core，只追加 + hash 链）
-- 特性：不可修改、不可删除、hash 链完整性校验
-- ----------------------------------------------------------------------------
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
CREATE INDEX IF NOT EXISTS idx_prov_timestamp ON ai_provenance(timestamp);

-- ----------------------------------------------------------------------------
-- capacity_metrics（AI-Modifiable，7 天 TTL）
-- 特性：高频写入、TTL 过期清理、compensated 字段标记补偿值（盲点 #30）
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- error_budget（v2.0.0 新增，Human-Gated 阈值 + AI-Modifiable 消耗）
-- 特性：五级响应追踪、Burn Rate 多窗口监控
-- ----------------------------------------------------------------------------
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
CREATE INDEX IF NOT EXISTS idx_eb_window ON error_budget(window_start, window_end);

-- ----------------------------------------------------------------------------
-- token_budget_usage（v2.0.0 新增，AI-Modifiable，7 天 TTL）
-- 特性：多级 Token 消耗追踪、模型级成本核算
-- ----------------------------------------------------------------------------
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
CREATE INDEX IF NOT EXISTS idx_tbu_level ON token_budget_usage(budget_level, level_id);

-- ----------------------------------------------------------------------------
-- capacity_metrics_hourly（v2.3.0 新增，压缩聚合表）
-- 特性：从 capacity_metrics 按小时聚合，降低存储压力（盲点 #21）
-- ----------------------------------------------------------------------------
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
