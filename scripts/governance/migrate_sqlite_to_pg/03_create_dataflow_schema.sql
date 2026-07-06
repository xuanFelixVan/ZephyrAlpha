-- =====================================================================
-- dataflowgraph PostgreSQL Schema DDL（数据流图，ARCH-051）
-- =====================================================================
-- 物理位置: PostgreSQL depgraph 数据库（与 depgraph 25张表同库不同表）
-- 表名前缀: dataflow_*（与 depgraph 的 nodes/edges/domains 等表物理隔离）
-- 连接配置: config/.env.postgres（与 depgraph 共享）
-- 写入互斥锁 key: 424243（pg_advisory_lock，depgraph 用 424242，避免互锁）
-- 设计依据: ARCH-051 裁定（2026-07-06）+ dataflow_graph_registry.yaml v1.0.0
-- 业界对标: OpenLineage/Marquez（Dataset/Job/Run 三实体模型）
-- 双态模式: design_maturity(design/production/prototype) + build_status(planned/generated/testing/stable/deprecated)
-- 字段角色分离: dataflow_datasets_metadata / dataflow_jobs_metadata 保护人工 curated 字段
--   （对齐 depgraph 裁定#209 Stage 2 nodes_metadata/edges_metadata 模式）
-- =====================================================================

-- ========== 1. 表定义（按外键依赖顺序） ==========

-- 1.1 无外键依赖的表（先创建）

-- dataflow_datasets: Dataset 节点（数据集，如 market_data.tick / backtest.tick_event）
-- scope=production: 生产数据流（引用 CTR 契约）
-- scope=backtest_internal: 回测内部数据流（physical_type 指向具体类，contract_ref=NULL）
CREATE TABLE IF NOT EXISTS dataflow_datasets (
    dataset_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_name      TEXT NOT NULL UNIQUE,
    entity_type      TEXT NOT NULL DEFAULT 'dataset',
    scope            TEXT NOT NULL DEFAULT 'production'
        CHECK (scope IN ('production', 'backtest_internal')),
    contract_ref     TEXT,
    physical_type    TEXT,
    produced_by_job  TEXT,
    domain_id        TEXT,
    design_maturity  TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status     TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    pit_policy       TEXT DEFAULT 'strict'
        CHECK (pit_policy IN ('strict', 'loose', 'none')),
    format_summary   TEXT,
    valid_since      TEXT,
    last_updated     TEXT
);

-- dataflow_jobs: Job 节点（数据变换作业，如 ingest_ifind_kline / compute_value_factor）
-- source_code_ref 引用 depgraph 模块 path（跨图关联，不设 FK 避免耦合）
CREATE TABLE IF NOT EXISTS dataflow_jobs (
    job_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_name         TEXT NOT NULL UNIQUE,
    entity_type      TEXT NOT NULL DEFAULT 'job',
    scope            TEXT NOT NULL DEFAULT 'production'
        CHECK (scope IN ('production', 'backtest_internal')),
    source_code_ref  TEXT,
    trigger_type     TEXT
        CHECK (trigger_type IS NULL OR trigger_type IN ('event_driven', 'scheduled', 'manual', 'stream')),
    run_context      TEXT,
    pit_relevance    TEXT DEFAULT 'strict'
        CHECK (pit_relevance IN ('strict', 'loose', 'none')),
    description      TEXT,
    design_maturity  TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status     TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    last_updated     TEXT
);

-- 1.2 依赖 dataflow_jobs 的表

-- dataflow_runs: Run 实例（Job 的运行实例，Phase 2 运行时 instrumentation 产出）
-- run_type 支持多回测类型（日线/分钟/Tick/生产）
CREATE TABLE IF NOT EXISTS dataflow_runs (
    run_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id           BIGINT NOT NULL,
    run_type         TEXT NOT NULL
        CHECK (run_type IN ('daily_backtest', 'minute_backtest', 'tick_backtest', 'production_run')),
    run_status       TEXT DEFAULT 'pending'
        CHECK (run_status IN ('pending', 'running', 'completed', 'failed', 'aborted')),
    started_at       TIMESTAMP,
    finished_at      TIMESTAMP,
    parameters       TEXT,
    result_summary   TEXT,
    last_updated     TEXT,
    FOREIGN KEY (job_id) REFERENCES dataflow_jobs(job_id) ON DELETE CASCADE
);

-- 1.3 dataflow_edges: 数据流边
-- from_entity_type/to_entity_type: dataset/job（支持 Dataset→Job 消费 / Job→Dataset 产出）
-- edge_type: push(Job→Dataset 产出) / pull(Dataset→Job 消费) / sync/async/event_driven(Phase 3)
-- 不设 FK 到 dataflow_datasets/dataflow_jobs（from/to 可能是 dataset 或 job，多态引用）
CREATE TABLE IF NOT EXISTS dataflow_edges (
    edge_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_entity_id    BIGINT NOT NULL,
    to_entity_id      BIGINT NOT NULL,
    from_entity_type  TEXT NOT NULL
        CHECK (from_entity_type IN ('dataset', 'job')),
    to_entity_type    TEXT NOT NULL
        CHECK (to_entity_type IN ('dataset', 'job')),
    edge_type         TEXT NOT NULL
        CHECK (edge_type IN ('push', 'pull', 'sync', 'async', 'event_driven')),
    design_maturity   TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    last_updated      TEXT
);

-- 1.4 字段角色分离表（人工 curated 字段保护，对齐 depgraph 裁定#209 Stage 2）
-- entity_name/job_name 为稳定 PK（dataset_id/job_id 是 IDENTITY，DELETE+INSERT 后变化）

-- dataflow_datasets_metadata: 保护人工 curated 字段
CREATE TABLE IF NOT EXISTS dataflow_datasets_metadata (
    entity_name      TEXT PRIMARY KEY,
    contract_ref     TEXT,
    physical_type    TEXT,
    domain_id        TEXT,
    pit_policy       TEXT,
    format_summary   TEXT,
    valid_since      TEXT,
    last_updated     TEXT
);

-- dataflow_jobs_metadata: 保护人工 curated 字段
CREATE TABLE IF NOT EXISTS dataflow_jobs_metadata (
    job_name         TEXT PRIMARY KEY,
    source_code_ref  TEXT,
    trigger_type     TEXT,
    run_context      TEXT,
    pit_relevance    TEXT,
    description      TEXT,
    last_updated     TEXT
);

-- ========== 2. 索引（查询性能优化） ==========

-- dataflow_datasets 索引
CREATE INDEX IF NOT EXISTS idx_dataflow_datasets_scope          ON dataflow_datasets(scope);
CREATE INDEX IF NOT EXISTS idx_dataflow_datasets_domain_id     ON dataflow_datasets(domain_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_datasets_contract_ref  ON dataflow_datasets(contract_ref);
CREATE INDEX IF NOT EXISTS idx_dataflow_datasets_design_maturity ON dataflow_datasets(design_maturity);

-- dataflow_jobs 索引
CREATE INDEX IF NOT EXISTS idx_dataflow_jobs_scope             ON dataflow_jobs(scope);
CREATE INDEX IF NOT EXISTS idx_dataflow_jobs_source_code_ref  ON dataflow_jobs(source_code_ref);
CREATE INDEX IF NOT EXISTS idx_dataflow_jobs_design_maturity   ON dataflow_jobs(design_maturity);

-- dataflow_runs 索引
CREATE INDEX IF NOT EXISTS idx_dataflow_runs_job_id    ON dataflow_runs(job_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_runs_run_type ON dataflow_runs(run_type);
CREATE INDEX IF NOT EXISTS idx_dataflow_runs_run_status ON dataflow_runs(run_status);

-- dataflow_edges 索引
CREATE INDEX IF NOT EXISTS idx_dataflow_edges_from_entity ON dataflow_edges(from_entity_id, from_entity_type);
CREATE INDEX IF NOT EXISTS idx_dataflow_edges_to_entity   ON dataflow_edges(to_entity_id, to_entity_type);
CREATE INDEX IF NOT EXISTS idx_dataflow_edges_edge_type   ON dataflow_edges(edge_type);

-- ========== 3. 触发器：updated_at 自动更新（可选，Phase 2 补充） ==========
-- 当前 last_updated 由 Python 层（apply_dataflowgraph.py / sync_dataflow_registry）管理
-- Phase 2 可考虑添加 PL/pgSQL 触发器自动更新 last_updated

-- ========== 4. Schema 健康检查视图（可选，Phase 2 补充） ==========
-- 当前由 verify_schema_health.py 扩展校验（Phase 2 TODO）

-- ========== 5. 设计态保护触发器（ARCH-053，2026-07-06） ==========
-- 防止 sync_dataflow_registry 等批量同步工具覆盖/删除设计态节点
-- 逃生通道：SET app.allow_design_maturity_delete = on（仅 apply_dataflowgraph.py 设计态写入命令启用）
-- 对齐 depgraph.protect_depgraph_design_edges 模式（裁定#203 + #ARCH-053）
CREATE OR REPLACE FUNCTION protect_dataflow_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    SHOW app.allow_design_maturity_delete INTO v_allow;
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    -- DELETE: OLD.design_maturity / UPDATE: OLD.design_maturity（before 状态）
    IF TG_OP = 'DELETE' AND OLD.design_maturity = 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design 态 dataflow 行（表=%, entity=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, COALESCE(OLD.entity_name, OLD.job_name);
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity = 'design' AND NEW.design_maturity IS DISTINCT FROM 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design 态 dataflow 行降级（表=%, entity=%, design→%）', TG_TABLE_NAME, COALESCE(OLD.entity_name, OLD.job_name), NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_protect_dataflow_design_datasets ON dataflow_datasets;
CREATE TRIGGER trg_protect_dataflow_design_datasets
    BEFORE DELETE OR UPDATE ON dataflow_datasets
    FOR EACH ROW EXECUTE FUNCTION protect_dataflow_design_maturity();

DROP TRIGGER IF EXISTS trg_protect_dataflow_design_jobs ON dataflow_jobs;
CREATE TRIGGER trg_protect_dataflow_design_jobs
    BEFORE DELETE OR UPDATE ON dataflow_jobs
    FOR EACH ROW EXECUTE FUNCTION protect_dataflow_design_maturity();

DROP TRIGGER IF EXISTS trg_protect_dataflow_design_edges ON dataflow_edges;
CREATE TRIGGER trg_protect_dataflow_design_edges
    BEFORE DELETE OR UPDATE ON dataflow_edges
    FOR EACH ROW EXECUTE FUNCTION protect_dataflow_design_maturity();
