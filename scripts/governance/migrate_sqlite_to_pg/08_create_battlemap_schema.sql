-- ============================================================================
-- 08_create_battlemap_schema.sql
-- ============================================================================
-- [BLUEPRINT] SH-DB-003 | battle_map_positioning.md | §battlemap
-- [MODULE] battlemap PG schema 真源（DDL 执行文件）
-- [DOMAIN] D_GOVERNANCE
-- [INVARIANTS] BM-INV-001~004（见 battlemap_schema.py 注释）
-- [SAFETY] M（DDL 创建，幂等 CREATE TABLE IF NOT EXISTS）
--
-- 作用：创建 battlemap 第四全景图的 3 张核心表 + 6 个索引。
--       与 depgraph/decisiongraph 共享同一 PostgreSQL 实例（不同表前缀 battle_map_*）。
--
-- 真源关系：
--   - 本文件是 PG schema 真源（执行 DDL）
--   - battlemap_schema.py 的 _DDL_BATTLE_MAP_* 常量是 Python 侧列名对比真源（drift 校验）
--   - init_battle_map_db() 仅验证表存在，不执行 DDL
--
-- 幂等：所有 CREATE 均带 IF NOT EXISTS，可重复执行。
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. battle_map_steps — 作战环节表（13列，V0.4.0 新增 parent_step_id + depth）
--    step_id TEXT PK（格式 BM-<阶段缩写>-<序号>，如 BM-BUY-03）
--    indicators JSONB — 6件套结构化数据（trigger/consumes/params/data_flow/code_mapping/degradation）
--    narrative_ref TEXT — 指向翻译真源 battle_map_steps 段的 step_id（叙事真源在 YAML）
--    parent_step_id TEXT — V0.4.0 父子嵌套：自引用 FK 指向父环节 step_id（NULL=顶层）
--    depth INTEGER — V0.4.0 层级深度（0=顶层, 1=子, 2=孙，最大2）
-- ============================================================================
CREATE TABLE IF NOT EXISTS battle_map_steps (
    step_id          TEXT    PRIMARY KEY,
    step_name        TEXT    NOT NULL,
    flow_stage       TEXT    NOT NULL
        -- 2026-08-03 全生命周期扩展：11 阶段（研究孵化→模型训练→回测验证→仿真验证→选股→买入→卖出→仓位→风控管控→执行→对账）
        CHECK (flow_stage IN ('research_incubation', 'model_training', 'backtest_validation',
                              'simulation_validation', 'stock_selection', 'buy_flow', 'sell_flow',
                              'position_management', 'risk_control', 'execution', 'reconciliation')),
    layer            TEXT,
    sort_order       INTEGER NOT NULL DEFAULT 0,
    narrative_ref    TEXT,
    indicators       JSONB,
    source_ref       TEXT,
    design_maturity  TEXT    DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production')),
    parent_step_id   TEXT    REFERENCES battle_map_steps(step_id) ON DELETE SET NULL,
    depth            INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- V0.4.0 增量迁移：已存在的库补列（幂等，CREATE TABLE IF NOT EXISTS 不会补列）
ALTER TABLE battle_map_steps ADD COLUMN IF NOT EXISTS parent_step_id TEXT
    REFERENCES battle_map_steps(step_id) ON DELETE SET NULL;
ALTER TABLE battle_map_steps ADD COLUMN IF NOT EXISTS depth INTEGER NOT NULL DEFAULT 0;

-- 2026-08-03 全生命周期扩展：flow_stage CHECK 约束从 6 值升级到 11 值（幂等）
-- 已存在的库需 DROP 旧约束 + ADD 新约束；新库由 CREATE TABLE 直接建对
ALTER TABLE battle_map_steps DROP CONSTRAINT IF EXISTS battle_map_steps_flow_stage_check;
ALTER TABLE battle_map_steps DROP CONSTRAINT IF EXISTS battle_map_steps_flow_stage_check1;
ALTER TABLE battle_map_steps
    ADD CONSTRAINT battle_map_steps_flow_stage_check
    CHECK (flow_stage IN ('research_incubation', 'model_training', 'backtest_validation',
                          'simulation_validation', 'stock_selection', 'buy_flow', 'sell_flow',
                          'position_management', 'risk_control', 'execution', 'reconciliation'));

COMMENT ON TABLE battle_map_steps IS '作战地图环节表——第四全景图 battlemap 真源。每行一个作战环节（如四轨融合/流动性过滤），indicators 存6件套结构化数据。';

-- ============================================================================
-- 2. battle_map_anchors — 双向对齐关系表（7列）
--    双向查找真源：step_id ↔ target_graph + target_id
--    BM-INV-001: 环节无锚点=悬空决策（应用层君子协定告警）
--    BM-INV-002: target_id 必须能在 target_graph 找到（应用层校验，防幽灵锚点）
-- ============================================================================
CREATE TABLE IF NOT EXISTS battle_map_anchors (
    anchor_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    step_id          TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    target_graph     TEXT    NOT NULL
        CHECK (target_graph IN ('depgraph', 'dataflowgraph', 'decisiongraph', 'candidate', 'blueprint')),
    target_id        TEXT    NOT NULL,
    target_role      TEXT    NOT NULL DEFAULT 'primary'
        CHECK (target_role IN ('primary', 'supplement', 'degradation')),
    status_snapshot  TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (step_id, target_graph, target_id)
);

COMMENT ON TABLE battle_map_anchors IS '作战地图双向锚点表——环节↔各图模块/候选/蓝点的对齐关系真源。方向A(step→modules)和方向B(module→step)都从此表查询。';

-- ============================================================================
-- 3. battle_map_edges — 环节流转表（6列）
--    edge_type 3值：data_flow / trigger / degradation
--    FK: from_step_id/to_step_id REFERENCES battle_map_steps(step_id) ON DELETE CASCADE
-- ============================================================================
CREATE TABLE IF NOT EXISTS battle_map_edges (
    edge_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_step_id     TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    to_step_id       TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    edge_type        TEXT    NOT NULL
        CHECK (edge_type IN ('data_flow', 'trigger', 'degradation')),
    label            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    CHECK (from_step_id <> to_step_id)
);

COMMENT ON TABLE battle_map_edges IS '作战地图环节流转表——环节间的 data_flow/trigger/degradation 边。';

-- ============================================================================
-- 4. 索引（7个，V0.4.0 新增 parent_step_id 索引）
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_battle_map_steps_flow_stage ON battle_map_steps(flow_stage);
CREATE INDEX IF NOT EXISTS idx_battle_map_steps_sort ON battle_map_steps(flow_stage, sort_order);
CREATE INDEX IF NOT EXISTS idx_battle_map_steps_parent ON battle_map_steps(parent_step_id);
CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_step ON battle_map_anchors(step_id);
CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_target ON battle_map_anchors(target_graph, target_id);
CREATE INDEX IF NOT EXISTS idx_battle_map_edges_from ON battle_map_edges(from_step_id);
CREATE INDEX IF NOT EXISTS idx_battle_map_edges_to ON battle_map_edges(to_step_id);

-- ============================================================================
-- 5. updated_at 触发器（自动维护 updated_at）
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_battle_map_steps_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS battle_map_steps_updated_at ON battle_map_steps;
CREATE TRIGGER battle_map_steps_updated_at
    BEFORE UPDATE ON battle_map_steps
    FOR EACH ROW
    EXECUTE FUNCTION trg_battle_map_steps_updated_at();

COMMIT;

-- ============================================================================
-- 验证（可选，执行后手动跑）
-- ============================================================================
-- SELECT 'battle_map_steps' AS t, COUNT(*) FROM battle_map_steps
-- UNION ALL SELECT 'battle_map_anchors', COUNT(*) FROM battle_map_anchors
-- UNION ALL SELECT 'battle_map_edges', COUNT(*) FROM battle_map_edges;
