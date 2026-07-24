-- =====================================================================
-- 幂等迁移脚本 Phase 2：剩余违规治本修复（#ARCH-5VIOLATIONS-FIX-002）
-- =====================================================================
-- 修复内容:
--   1. D_GOV_SCRIPTS 进一步拆分（195→<150）
--      - 17 arch_guard 节点迁移到 D_ARCH_GUARD
--      - 35 _archive 节点标记为 deprecated（归档脚本不计入 production 容量）
--   2. D_FRONTEND 层级重新分配 L1→L2（前端是展示域，非基础层）
--   3. 重新同步 domain_dependencies（域迁移后）
--   4. 重算 cross_domain 列
-- =====================================================================

-- ========== 1. D_GOV_SCRIPTS 进一步拆分 ==========

-- 1.1 迁移 arch_guard 节点（17 个）到 D_ARCH_GUARD
UPDATE nodes SET domain_id='D_ARCH_GUARD'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/arch_guard/%';

-- 1.2 标记 _archive 节点为 deprecated（归档脚本不再维护）
-- 裁定依据: _archive 目录存放已归档脚本，不再是 AI 维护的 production 模块
-- design_maturity='deprecated' 排除出 production 容量统计（ARCH-CAP-001 口径）
UPDATE nodes SET design_maturity='deprecated'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/_archive/%'
    AND design_maturity='production';

-- ========== 2. D_FRONTEND 层级重新分配 L1→L2 ==========
-- 裁定依据（#ARCH-FRONTEND-LAYER-REALLOC-001）:
--   D_FRONTEND = "前端" (12 production 节点)
--   前端是展示层，依赖 D_GOVERNANCE(task_repo/sqlite_schema) 和 D_TRADING(order)
--   前端不是基础层（foundation），是业务展示域
--   L2_domain 更符合其定位（展示域依赖业务域）
UPDATE domains SET layer_id='L2_domain'
    WHERE domain_id='D_FRONTEND' AND layer_id='L1_foundation';

-- ========== 3. 重新同步 domain_dependencies ==========
DELETE FROM domain_dependencies;
INSERT INTO domain_dependencies (from_domain, to_domain, edge_count, edge_types, constraint_type)
SELECT
    n1.domain_id AS from_domain,
    n2.domain_id AS to_domain,
    COUNT(*) AS edge_count,
    STRING_AGG(DISTINCT e.dep_type, ',' ORDER BY e.dep_type) AS edge_types,
    CASE
        WHEN COUNT(*) FILTER (WHERE e.dep_type IN ('import_depends','H')) > 0 THEN 'hard'
        WHEN COUNT(*) FILTER (WHERE e.dep_type IN ('event_depends','event','E')) > 0 THEN 'event_or_hard'
        ELSE 'soft'
    END AS constraint_type
FROM edges e
JOIN nodes n1 ON e.from_node_id = n1.node_id
JOIN nodes n2 ON e.to_node_id = n2.node_id
WHERE n1.domain_id != n2.domain_id
    AND n1.domain_id IS NOT NULL AND n1.domain_id != ''
    AND n2.domain_id IS NOT NULL AND n2.domain_id != ''
    AND e.dep_maturity = 'active'
GROUP BY n1.domain_id, n2.domain_id
ON CONFLICT (from_domain, to_domain) DO UPDATE SET
    edge_count = excluded.edge_count,
    edge_types = excluded.edge_types,
    constraint_type = excluded.constraint_type;

-- ========== 4. 重算 cross_domain 列 ==========
UPDATE edges SET cross_domain = edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
);

-- ========== 5. 验证 ==========
DO $$
DECLARE
    v_capacity_violations BIGINT;
    v_hard_limit_violations BIGINT;
    v_gov_scripts_count BIGINT;
BEGIN
    -- D_GOV_SCRIPTS production count
    SELECT COUNT(*) INTO v_gov_scripts_count FROM nodes
    WHERE domain_id='D_GOV_SCRIPTS' AND design_maturity='production';
    RAISE NOTICE 'D_GOV_SCRIPTS production nodes: %', v_gov_scripts_count;

    -- Capacity violations
    SELECT COUNT(*) INTO v_capacity_violations FROM (
        SELECT n.domain_id FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id, d.max_modules
        HAVING COUNT(*) > d.max_modules
    ) t;
    RAISE NOTICE 'Capacity violations: %', v_capacity_violations;

    -- Hard limit violations (>150)
    SELECT COUNT(*) INTO v_hard_limit_violations FROM (
        SELECT n.domain_id FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id
        HAVING COUNT(*) > 150
    ) t;
    RAISE NOTICE 'Hard limit violations: %', v_hard_limit_violations;
END $$;
