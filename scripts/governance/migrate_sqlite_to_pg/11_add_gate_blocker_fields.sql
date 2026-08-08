-- ============================================================
-- 11_add_gate_blocker_fields.sql
-- ============================================================
-- 用途：全景（depgraph/dataflowgraph/decisiongraph）新增 gate_reason + blocker_status 字段
-- 背景：232 个设计态模块需要记录"为什么没施工"（gate_reason）和"受限是否仍存在"（blocker_status）
-- blocker_status 取值：active(受限仍存在) / resolved(受限已解除但未施工) / none(无受限)
--
-- 执行方式：psql -U postgres -d depgraph -f 11_add_gate_blocker_fields.sql
-- 幂等：使用 ADD COLUMN IF NOT EXISTS，可重复执行
-- ============================================================

-- ============================================================
-- 1. depgraph（nodes / nodes_metadata / edges）
-- ============================================================

-- nodes: 已有 gate_reason，新增 blocker_status
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- nodes_metadata: 已有 gate_reason，新增 blocker_status
ALTER TABLE nodes_metadata ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none';

-- edges: 新增 gate_reason + blocker_status
ALTER TABLE edges ADD COLUMN IF NOT EXISTS gate_reason TEXT NOT NULL DEFAULT '';
ALTER TABLE edges ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- ============================================================
-- 2. dataflowgraph（dataflow_datasets / dataflow_jobs / dataflow_edges）
-- ============================================================

-- dataflow_datasets: 新增 gate_reason + blocker_status
ALTER TABLE dataflow_datasets ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE dataflow_datasets ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- dataflow_jobs: 新增 gate_reason + blocker_status
ALTER TABLE dataflow_jobs ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE dataflow_jobs ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- dataflow_edges: 新增 gate_reason + blocker_status
ALTER TABLE dataflow_edges ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE dataflow_edges ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- ============================================================
-- 3. decisiongraph（decision_nodes / decision_edges / decision_layers）
-- ============================================================

-- decision_nodes: 新增 gate_reason + blocker_status
ALTER TABLE decision_nodes ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE decision_nodes ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- decision_edges: 新增 gate_reason + blocker_status
ALTER TABLE decision_edges ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE decision_edges ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));

-- decision_layers: 新增 gate_reason + blocker_status
ALTER TABLE decision_layers ADD COLUMN IF NOT EXISTS gate_reason TEXT DEFAULT '';
ALTER TABLE decision_layers ADD COLUMN IF NOT EXISTS blocker_status TEXT DEFAULT 'none'
    CHECK (blocker_status IN ('active', 'resolved', 'none'));
