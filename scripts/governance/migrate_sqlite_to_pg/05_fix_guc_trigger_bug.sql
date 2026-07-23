-- =====================================================================
-- 幂等迁移脚本：修复 GUC 触发器缺陷（#ARCH-GUC-TRIGGER-FIX-001）
-- =====================================================================
-- 裁定文档: docs/_archive/ruling_guc_trigger_cascading_sync_failure.md
-- 严重级别: P0（生产阻断——reconciler 持续失败 23+ 次）
-- 实施日期: 2026-07-19
--
-- 根因:
--   03_create_dataflow_schema.sql 和 03_create_decision_schema.sql 的触发器函数
--   使用 `SHOW app.allow_design_maturity_delete INTO v_allow`，但该 GUC 未在
--   session 中 SET（sync_dataflow_registry 不需要绕过保护，只删 production 行）。
--   SHOW 在 GUC 未注册时抛 UndefinedObject 异常，导致 sync 失败。
--
-- 修复:
--   替换为 `v_allow := current_setting('app.allow_design_maturity_delete', true)`。
--   current_setting 的 missing_ok=true 参数在 GUC 未注册时返回 NULL，不抛异常，
--   触发器正常跳过逃生通道检查，继续执行保护逻辑。
--   对齐 02_create_pg_schema.sql L665 的 protect_depgraph_design_edges 模式。
--
-- 幂等性:
--   CREATE OR REPLACE FUNCTION 可重复执行，无副作用。
--   触发器不需要重建（函数定义更新后自动生效）。
--
-- 影响范围:
--   - protect_dataflow_design_maturity() 函数定义
--   - protect_decision_design_maturity() 函数定义
--   - 6 个触发器（dataflow 3 + decision 3）自动引用新函数定义
--
-- 验证:
--   1. SELECT current_setting('app.allow_design_maturity_delete', true) → NULL
--   2. DELETE FROM dataflow_jobs WHERE design_maturity='production' AND job_name='__test__' → 成功（0 行）
--   3. DELETE FROM dataflow_jobs WHERE design_maturity='design' → 失败（ARCH-053 保护）
--   4. sync_dataflow_registry(cur) 完整执行成功
-- =====================================================================

-- ========== 1. 修复 protect_dataflow_design_maturity() ==========
CREATE OR REPLACE FUNCTION protect_dataflow_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    -- #ARCH-GUC-TRIGGER-FIX-001: 用 current_setting(..., true) 替代 SHOW
    v_allow := current_setting('app.allow_design_maturity_delete', true);
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    -- ARCH-MM-002 (2026-07-23): 两档化后保护范围仅 design（prototype 已删除）
    -- #ARCH-GUC-TRIGGER-FIX-001c: 用 OLD::text 替代 CASE/COALESCE 引用特定列
    IF TG_OP = 'DELETE' AND OLD.design_maturity = 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design 态 dataflow 行（表=%, row=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, OLD::text;
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity = 'design' AND NEW.design_maturity IS DISTINCT FROM OLD.design_maturity THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design 态 dataflow 行降级（表=%, row=%, %→%）', TG_TABLE_NAME, OLD::text, OLD.design_maturity, NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ========== 2. 修复 protect_decision_design_maturity() ==========
CREATE OR REPLACE FUNCTION protect_decision_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    -- #ARCH-GUC-TRIGGER-FIX-001: 用 current_setting(..., true) 替代 SHOW
    v_allow := current_setting('app.allow_design_maturity_delete', true);
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    -- #ARCH-GUC-TRIGGER-FIX-001c: 用 OLD::text 替代 CASE/COALESCE 引用特定列
    IF TG_OP = 'DELETE' AND OLD.design_maturity = 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design 态 decision 行（表=%, row=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, OLD::text;
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity = 'design' AND NEW.design_maturity IS DISTINCT FROM 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design 态 decision 行降级（表=%, row=%, design→%）', TG_TABLE_NAME, OLD::text, NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ========== 3. 验证修复生效 ==========
DO $$
DECLARE
    v_test TEXT;
BEGIN
    -- 验证 current_setting(..., true) 在 GUC 未注册时返回 NULL
    v_test := current_setting('app.allow_design_maturity_delete', true);
    IF v_test IS NULL THEN
        RAISE NOTICE 'ARCH-GUC-TRIGGER-FIX-001: current_setting(missing_ok=true) 返回 NULL，修复生效';
    ELSE
        RAISE NOTICE 'ARCH-GUC-TRIGGER-FIX-001: GUC 已被 SET 为 %（逃生通道开启中）', v_test;
    END IF;
END $$;

-- ========== 4. 记录迁移元数据（条件性，schema_migrations 表可能不存在）==========
-- 注意：本项目无 schema_migrations 表，迁移元数据通过 git commit log 追踪。
-- 如未来引入 schema_migrations 表，可取消下方 DO 块注释。
-- DO $$
-- BEGIN
--     IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schema_migrations') THEN
--         INSERT INTO schema_migrations (migration_id, description, applied_at)
--         VALUES (
--             '05_fix_guc_trigger_bug',
--             '#ARCH-GUC-TRIGGER-FIX-001: 修复 GUC 触发器缺陷——替换 SHOW 为 current_setting(..., true)',
--             NOW()
--         )
--         ON CONFLICT (migration_id) DO NOTHING;
--         RAISE NOTICE 'ARCH-GUC-TRIGGER-FIX-001: 迁移元数据已记录到 schema_migrations';
--     ELSE
--         RAISE NOTICE 'ARCH-GUC-TRIGGER-FIX-001: schema_migrations 表不存在，跳过元数据记录（通过 git commit 追踪）';
--     END IF;
-- END $$;

-- ========== 5. 清理遗留的 _fixed 变体函数（如有）==========
-- 前序调试可能创建了 protect_dataflow_design_maturity_fixed 等变体，需清理
DROP FUNCTION IF EXISTS protect_dataflow_design_maturity_fixed() CASCADE;
DROP FUNCTION IF EXISTS protect_decision_design_maturity_fixed() CASCADE;