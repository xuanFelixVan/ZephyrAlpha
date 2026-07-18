-- =====================================================================
-- P2 PostgreSQL迁移：Schema 降级脚本（DROP 02_create_pg_schema.sql 创建的全部对象）
-- =====================================================================
-- 5.32.7 治本：02 只有 CREATE 无 DROP，无法回滚。本脚本按反依赖顺序 DROP：
--   1. 视图（依赖 edges/nodes 表，先 DROP）
--   2. 表（含 FK 的表先于被引用表；索引/触发器随表自动 DROP）
--   3. 触发器函数（表 DROP 后函数不再被引用）
-- 全部使用 IF EXISTS + CASCADE，可重复执行（幂等）。
-- 对照清单（02 创建物）：
--   表 30 / 索引 42 / 视图 2 / 触发器 36（33 只读 + 2 blueprint_id 检查 + 1 edges 保护）
--   函数 3（raise_readonly_exception / check_blueprint_id_format / protect_apply_depgraph_edges）
-- 注意：本脚本只回滚 02 的对象。01 的扩展（pg_stat_statements/pgcrypto 为系统级，
--       多库共享，不在此 DROP）、03/03b/04 的 dataflow/decision/roles 不在本脚本范围。
-- =====================================================================

-- ========== 1. 视图（依赖 edges/nodes，先 DROP） ==========
DROP VIEW IF EXISTS dep_import_cycles;
DROP VIEW IF EXISTS dep_cycles;

-- ========== 2. 表（反依赖顺序；索引 42 个与触发器 36 个随表自动 DROP） ==========

-- 2.1 含 FK 引用其他表的表（先 DROP）
DROP TABLE IF EXISTS data_source_apis CASCADE;        -- FK → data_source_assets
DROP TABLE IF EXISTS edges CASCADE;                   -- FK → nodes（含 trg_edges_protect_apply_depgraph 触发器）
DROP TABLE IF EXISTS rule_bindings CASCADE;           -- 无 PG FK（应用层校验，见 02 §rule_bindings 注释）
DROP TABLE IF EXISTS contracts CASCADE;               -- FK → domains
DROP TABLE IF EXISTS domain_dependencies CASCADE;     -- FK → domains
DROP TABLE IF EXISTS domain_events CASCADE;           -- FK → domains
DROP TABLE IF EXISTS arch_constraints CASCADE;        -- FK → domains
DROP TABLE IF EXISTS arch_path_mappings CASCADE;      -- FK → domains
DROP TABLE IF EXISTS domain_mapping CASCADE;          -- FK → domains
DROP TABLE IF EXISTS arch_directory_tree CASCADE;     -- FK → domains
DROP TABLE IF EXISTS nodes CASCADE;                   -- FK → domains（含 chk_nodes_blueprint_id_insert/update 触发器）

-- 2.2 独立表（无 FK 依赖，顺序无关）
DROP TABLE IF EXISTS edges_metadata CASCADE;
DROP TABLE IF EXISTS nodes_metadata CASCADE;
DROP TABLE IF EXISTS nodes_archive_module_lifecycle CASCADE;
DROP TABLE IF EXISTS governance_audit_logs CASCADE;
DROP TABLE IF EXISTS data_source_assets CASCADE;      -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS service_assets CASCADE;          -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS config_assets CASCADE;
DROP TABLE IF EXISTS registries CASCADE;              -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS model_capabilities CASCADE;      -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS infrastructure_components CASCADE; -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS hard_boundaries CASCADE;         -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS gates CASCADE;                   -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS field_vocabularies CASCADE;      -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS domain_naming_rules CASCADE;
DROP TABLE IF EXISTS derived_identifier_registry CASCADE;
DROP TABLE IF EXISTS cross_registry_rules CASCADE;    -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS business_streams CASCADE;        -- 只读触发器 ×3 随表 DROP
DROP TABLE IF EXISTS blueprint_links CASCADE;
DROP TABLE IF EXISTS _schema_version CASCADE;

-- 2.3 被引用根表（最后 DROP）
DROP TABLE IF EXISTS domains CASCADE;

-- ========== 3. 触发器函数（表已 DROP，函数不再被引用） ==========
DROP FUNCTION IF EXISTS protect_apply_depgraph_edges();
DROP FUNCTION IF EXISTS check_blueprint_id_format();
DROP FUNCTION IF EXISTS raise_readonly_exception();

-- =====================================================================
-- 降级完成。验证：\dt 应仅剩 migration_log（migrate_data.py 幂等标记表，
-- 非 02 创建物；如需彻底清除请手动 DROP TABLE IF EXISTS migration_log）。
-- =====================================================================
