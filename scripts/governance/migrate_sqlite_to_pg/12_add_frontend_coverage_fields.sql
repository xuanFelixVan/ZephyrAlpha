-- ============================================================
-- 12_add_frontend_coverage_fields.sql
-- ============================================================
-- 用途：depgraph nodes 表新增前端覆盖三字段（has_frontend / no_frontend_reason / frontend_ref）
-- 背景：六图对齐体系（第六全景图 frontend_map）统一对账设计——每个模块必须声明"有没有前端"，
--       没有前端必须填理由（"事出有因"）。缺口视图=机器派生查询：
--         前端有后端没有 = frontend_map.backend_ref 空/悬空
--         后端有前端没有 = nodes.has_frontend='yes'/'planned' 但 frontend_ref 空
--         对账异常     = has_frontend='no' 但 no_frontend_reason 空
-- 裁定：四件套草案 §六（Owner 2026-08-31，路线 A 一步到位——字段内化 depgraph 节点本体）
-- 执行方式：python 迁移通道（psycopg2）或 psql -U postgres -d depgraph -f 12_add_frontend_coverage_fields.sql
-- 幂等：使用 ADD COLUMN IF NOT EXISTS / CREATE INDEX IF NOT EXISTS，可重复执行
-- ============================================================

ALTER TABLE nodes ADD COLUMN IF NOT EXISTS has_frontend TEXT NOT NULL DEFAULT 'no'
    CHECK (has_frontend IN ('yes', 'no', 'planned'));
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS no_frontend_reason TEXT NOT NULL DEFAULT '';
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS frontend_ref TEXT NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_nodes_has_frontend ON nodes(has_frontend);
