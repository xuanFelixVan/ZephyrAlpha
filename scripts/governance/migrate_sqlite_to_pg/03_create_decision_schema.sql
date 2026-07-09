-- =====================================================================
-- decisiongraph Schema DDL（决策流图架构 4 张表 + 索引 + 约束）
-- =====================================================================
-- 物理位置：同一个 PostgreSQL 数据库（与 depgraph 共库，不同表前缀 decision_*）
-- 连接入口：get_decisiongraph_pg_connection()（复用 depgraph PG 连接）
-- Schema Python 真源：src/zephyr/governance/decisiongraph_schema.py
--
-- 表清单（4 张）：
--   1. decision_layers  — 决策层定义（L0-L6 + 四轨）
--   2. decision_nodes   — 决策节点（signal/portfolio_target/risk_check/order 等）
--   3. decision_edges   — 决策因果边（4类 typed edges: triggering/informing/constraining/approving）
--   4. decision_tracks  — 四轨定义（model_driven/data_driven/human_override/emergency）
--
-- 五条承重墙不变量（DB 级约束）：
--   DEC-INV-001 风控一票否决：order 节点必须有 approving 入边来自 risk_check（触发器）
--   DEC-INV-002 信号仓位分离：signal→order 边 INSERT 时阻断（触发器）
--   DEC-INV-003 DAG 无环：应用层 Tarjan SCC 检测（非 DB 约束）
--   DEC-INV-004 时间单调性：edges.valid_since >= from_node.created_at（CHECK 约束）
--   DEC-INV-005 evidence_hash 必填：nodes.evidence_hash NOT NULL
--
-- 借鉴：
--   - MARIA OS Evidence Graph：4类 typed causal edges + evidence_hash + DAG
--   - DMN DRD：节点三分类（Decision/InputData/KnowledgeSource）
--   - QuantConnect Lean：5层节点类型 + Insight/PortfolioTarget 双契约
--   - OpenLineage Facet：JSONB facets 可扩展元数据
--
-- 变更历史：
--   v1.0.0 (2026-07-05): 初版——4张表 + 5索引 + 2触发器
--   v1.1.0 (2026-07-06): decision_layers 加 module_id + source_code_ref；decision_nodes 加 source_code_ref
--   v1.2.0 (2026-07-09): decision_layers/decision_nodes 加 domain_id（ARCH-056 四图模块同步引擎核心字段对齐）
-- =====================================================================

-- ========== 1. decision_tracks（四轨定义，无外键依赖，先创建） ==========
CREATE TABLE IF NOT EXISTS decision_tracks (
    track_id               TEXT PRIMARY KEY,
    track_name             TEXT NOT NULL,
    track_name_en          TEXT NOT NULL,
    description            TEXT,
    priority               INTEGER NOT NULL,
    activation_condition   TEXT
);

-- ========== 2. decision_layers（决策层定义，FK→decision_tracks） ==========
CREATE TABLE IF NOT EXISTS decision_layers (
    layer_id               TEXT PRIMARY KEY,
    layer_name             TEXT NOT NULL,
    layer_name_en          TEXT NOT NULL,
    track                  TEXT NOT NULL REFERENCES decision_tracks(track_id),
    description            TEXT,
    decision_frequency     TEXT,
    design_maturity        TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status           TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    module_id              TEXT,
    domain_id              TEXT,
    source_code_ref        TEXT
);

-- ========== 3. decision_nodes（决策节点，FK→decision_layers） ==========
CREATE TABLE IF NOT EXISTS decision_nodes (
    node_id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    layer_id               TEXT NOT NULL REFERENCES decision_layers(layer_id),
    node_type              TEXT NOT NULL,
    path                   TEXT NOT NULL UNIQUE,
    module_id              TEXT,
    domain_id              TEXT,
    decision_name          TEXT NOT NULL,
    decision_name_en       TEXT NOT NULL,
    inputs                 JSONB,
    outputs                JSONB,
    conditions             JSONB,
    facets                 JSONB,
    evidence_hash          TEXT NOT NULL,
    design_maturity        TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status           TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    source_code_ref        TEXT,
    created_at             TIMESTAMPTZ DEFAULT NOW(),
    finalized_at           TIMESTAMPTZ
);

-- ========== 4. decision_edges（决策因果边，FK→decision_nodes） ==========
CREATE TABLE IF NOT EXISTS decision_edges (
    edge_id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_node_id           BIGINT NOT NULL REFERENCES decision_nodes(node_id) ON DELETE CASCADE,
    to_node_id             BIGINT NOT NULL REFERENCES decision_nodes(node_id) ON DELETE CASCADE,
    edge_type              TEXT NOT NULL
        CHECK (edge_type IN ('triggering', 'informing', 'constraining', 'approving')),
    edge_type_cn           TEXT,
    condition              TEXT,
    priority               INTEGER,
    track                  TEXT,
    evidence_bundle        JSONB,
    design_maturity        TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status           TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    valid_since            TIMESTAMPTZ DEFAULT NOW()
);

-- ========== 5. 索引 ==========
CREATE INDEX IF NOT EXISTS idx_decision_nodes_layer ON decision_nodes(layer_id);
CREATE INDEX IF NOT EXISTS idx_decision_nodes_module ON decision_nodes(module_id);
CREATE INDEX IF NOT EXISTS idx_decision_edges_from ON decision_edges(from_node_id);
CREATE INDEX IF NOT EXISTS idx_decision_edges_to ON decision_edges(to_node_id);
CREATE INDEX IF NOT EXISTS idx_decision_edges_type ON decision_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_decision_layers_module ON decision_layers(module_id);

-- ========== 5.1 ALTER TABLE 迁移（v1.1.0：为已存在的表添加新列，幂等） ==========
-- decision_layers 加 module_id + source_code_ref
ALTER TABLE decision_layers ADD COLUMN IF NOT EXISTS module_id TEXT;
ALTER TABLE decision_layers ADD COLUMN IF NOT EXISTS source_code_ref TEXT;
-- decision_nodes 加 source_code_ref
ALTER TABLE decision_nodes ADD COLUMN IF NOT EXISTS source_code_ref TEXT;
-- decision_edges 加 design_maturity + build_status（v1.2.0：对齐 nodes 表三态机制）
ALTER TABLE decision_edges ADD COLUMN IF NOT EXISTS design_maturity TEXT DEFAULT 'production'
    CHECK (design_maturity IN ('design', 'production', 'prototype'));
ALTER TABLE decision_edges ADD COLUMN IF NOT EXISTS build_status TEXT DEFAULT 'generated'
    CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated'));
-- v1.2.0 (ARCH-056): decision_layers/decision_nodes 加 domain_id（四图模块同步引擎核心字段对齐）
ALTER TABLE decision_layers ADD COLUMN IF NOT EXISTS domain_id TEXT;
ALTER TABLE decision_nodes ADD COLUMN IF NOT EXISTS domain_id TEXT;
CREATE INDEX IF NOT EXISTS idx_decision_layers_domain ON decision_layers(domain_id);
CREATE INDEX IF NOT EXISTS idx_decision_nodes_domain ON decision_nodes(domain_id);

-- ========== 6. 触发器：承重墙不变量 ==========
-- DEC-INV-002 信号仓位分离：signal 节点不能直接连 order 节点
CREATE OR REPLACE FUNCTION check_signal_order_separation()
RETURNS TRIGGER AS $$
DECLARE
    from_type TEXT;
    to_type TEXT;
BEGIN
    SELECT node_type INTO from_type FROM decision_nodes WHERE node_id = NEW.from_node_id;
    SELECT node_type INTO to_type FROM decision_nodes WHERE node_id = NEW.to_node_id;
    IF from_type = 'signal' AND to_type = 'order' THEN
        RAISE EXCEPTION 'DEC-INV-002 信号仓位分离: signal 节点不能直接连 order 节点，必须经 portfolio_target 中转';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_signal_order_separation ON decision_edges;
CREATE TRIGGER trg_check_signal_order_separation
    BEFORE INSERT OR UPDATE ON decision_edges
    FOR EACH ROW EXECUTE FUNCTION check_signal_order_separation();

-- DEC-INV-001 风控一票否决（延迟检查，仅在 order 节点 finalized 时触发）
-- 注：此约束需要应用层配合，因为 INSERT order 节点时 approving 边可能尚未创建
-- 应用层在 finalize order 节点时必须验证存在 risk_check→order 的 approving 边
-- DB 级仅做 signal→order 硬阻断（DEC-INV-002），风控审批由应用层校验

-- ========== 7. 初始数据（四轨定义） ==========
INSERT INTO decision_tracks (track_id, track_name, track_name_en, description, priority, activation_condition)
VALUES
    ('model_driven', '模型驱动轨', 'Model-Driven Track',
     '传统 AI 信号链：L0→L1→L2-A/B/C/D→L3→L4→L5→L6', 1, '正常运行时'),
    ('data_driven', '数据驱动轨', 'Data-Driven Track',
     '端到端 DL 信号：原始数据→自动特征→买卖信号→密度预测', 2, '模型驱动轨信号不足时补充'),
    ('human_override', '人工指令轨', 'Human Override Track',
     '人工买入/卖出/调仓指令 + 人工风控干预', 3, '人工干预时'),
    ('emergency', '应急保命轨', 'Emergency Track',
     '全系统降级到最简规则', 4, '所有模型/策略/信号失效时')
ON CONFLICT (track_id) DO NOTHING;

-- ========== 8. 初始数据（决策层定义） ==========
INSERT INTO decision_layers (layer_id, layer_name, layer_name_en, track, description, decision_frequency, design_maturity, build_status, module_id, source_code_ref)
VALUES
    ('L0', '数据接入与预处理层', 'Data Ingestion & Preprocessing', 'model_driven',
     'miniQMT + iFind + tushare + 另类数据源 → 事件总线 → 分层时序存储',
     'tick', 'production', 'stable', NULL, NULL),
    ('L1', '因子计算层', 'Factor Calculation', 'model_driven',
     '因子工厂全生命周期管理 → 盘前全量/盘中增量双模计算 → 因子池',
     'daily', 'production', 'stable', NULL, NULL),
    ('L2A', '信号层', 'Signal Generation', 'model_driven',
     '信号工厂 → 多策略投票 → 收益率条件密度预测 → Transformer/Mamba时序增强',
     'daily', 'design', 'planned', NULL, NULL),
    ('L2B', '主力行为层', 'Main Force Behavior Analysis', 'model_driven',
     '六阶段识别 + 自迭代推演 + 庄家专项 + 群体博弈模拟',
     'daily', 'design', 'planned', NULL, NULL),
    ('L2C', '市场状态与大盘预测层', 'Market State & Index Prediction', 'model_driven',
     '3×3矩阵 + 2叠加态 + 三层大盘预测 + T+1次日8态走势预测 + 体制转换检测',
     'daily', 'design', 'planned', NULL, NULL),
    ('L2D', '知识图谱与因果推演层', 'Knowledge Graph & Causal Inference', 'model_driven',
     '六类知识图谱 → 事件影响链分析 → 因果传导推演 → GNN股票关系建模 → Causal ML',
     'daily', 'design', 'planned', NULL, NULL),
    ('L3', '策略组合层', 'Strategy & Portfolio Combination', 'model_driven',
     '多策略信号合成 → 资本分配 → 元策略路由 → 组合构建',
     'daily', 'design', 'planned', NULL, NULL),
    ('L4', '风控层', 'Risk Control', 'model_driven',
     'Pre/Post-Trade 风控校验 + Kill Switch 熔断 + 止损评估',
     'realtime', 'production', 'stable', NULL, NULL),
    ('L5', '学习层', 'Learning & Optimization', 'model_driven',
     '7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环',
     'weekly', 'design', 'planned', NULL, NULL),
    ('L6', '自评估层', 'Self Evaluation', 'model_driven',
     'LLM 自评估(Judge+交叉验证) + 多模态金融推理 + VeNRA零幻觉锚定',
     'weekly', 'design', 'planned', NULL, NULL)
ON CONFLICT (layer_id) DO UPDATE SET
    module_id = EXCLUDED.module_id,
    source_code_ref = EXCLUDED.source_code_ref;

-- ========== 9. 设计态保护触发器（ARCH-053，2026-07-06） ==========
-- 防止 sync/generator 覆盖或降级设计态节点
-- 逃生通道：SET app.allow_design_maturity_delete = on（仅 apply_decisiongraph.py 设计态写入命令启用）
-- 对齐 depgraph.protect_depgraph_design_edges 模式（裁定#203 + #ARCH-053）
CREATE OR REPLACE FUNCTION protect_decision_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    SHOW app.allow_design_maturity_delete INTO v_allow;
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    IF TG_OP = 'DELETE' AND OLD.design_maturity = 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design 态 decision 行（表=%, id=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, COALESCE(OLD.layer_id, OLD.node_id::TEXT, OLD.edge_id::TEXT);
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity = 'design' AND NEW.design_maturity IS DISTINCT FROM 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design 态 decision 行降级（表=%, id=%, design→%）', TG_TABLE_NAME, COALESCE(OLD.layer_id, OLD.node_id::TEXT, OLD.edge_id::TEXT), NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_protect_decision_design_layers ON decision_layers;
CREATE TRIGGER trg_protect_decision_design_layers
    BEFORE DELETE OR UPDATE ON decision_layers
    FOR EACH ROW EXECUTE FUNCTION protect_decision_design_maturity();

DROP TRIGGER IF EXISTS trg_protect_decision_design_nodes ON decision_nodes;
CREATE TRIGGER trg_protect_decision_design_nodes
    BEFORE DELETE OR UPDATE ON decision_nodes
    FOR EACH ROW EXECUTE FUNCTION protect_decision_design_maturity();

DROP TRIGGER IF EXISTS trg_protect_decision_design_edges ON decision_edges;
CREATE TRIGGER trg_protect_decision_design_edges
    BEFORE DELETE OR UPDATE ON decision_edges
    FOR EACH ROW EXECUTE FUNCTION protect_decision_design_maturity();
