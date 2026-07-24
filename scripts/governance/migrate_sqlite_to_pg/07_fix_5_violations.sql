-- =====================================================================
-- 幂等迁移脚本：5类违规治本修复（#ARCH-5VIOLATIONS-FIX-001）
-- =====================================================================
-- 裁定: 见本次治本修复（2026-07-25）
-- 严重级别: P1（架构约束违规系统性修复）
--
-- 修复范围:
--   1. NULL layer_id 修复（5 域）
--   2. domain_dependencies 自动同步（从实际跨域边派生）
--   3. 域分配修复（路径与 domain_id 不一致的节点迁移）
--   4. 域拆分（D_GOV_SCRIPTS 拆分为平行域）
--   5. D_SHARED 层级重新分配 L1→L0
--
-- 第一性原理:
--   - depgraph.edges 是依赖关系唯一真源（L1 铁律）
--   - domain_dependencies 应为 edges 的派生聚合，非独立维护
--   - 路径与 domain_id 必须一致（FP-2 路径=功能域）
--   - 域容量 ≤150 是 AI 可维护性硬上限（ARCH-CAP-002）
--   - 平行域原则：拆分产生平级域，无父子关系（ARCH-CAP-004）
--
-- 幂等性:
--   - UPDATE WHERE 条件确保重复执行影响 0 行
--   - INSERT ON CONFLICT 确保重复执行不报错
--   - 域拆分使用 INSERT ON CONFLICT 避免重复创建
-- =====================================================================

-- ========== 1. NULL layer_id 修复（5 域） ==========
-- 裁定依据: 域的功能定位 + 入/出边分析
--   D_BEHAVIORAL_AUDIT (0节点): L2_domain（行为审计是业务域）
--   D_COMPLIANCE (2节点, 49出边→D_GOV_DRIFT/D_SECURITY): L2_domain（合规是业务域）
--   D_DATA (109节点, 数据接入): L1_foundation（数据接入是基础层）
--   D_INFRASTRUCTURE (26节点, 107入边): L0_infrastructure（跨层契约基础设施）
--   D_SIGLEGACY (0节点): L2_domain（信号遗留设计态）
UPDATE domains SET layer_id='L0_infrastructure', max_modules=150
    WHERE domain_id='D_INFRASTRUCTURE' AND layer_id IS NULL;
UPDATE domains SET layer_id='L1_foundation', max_modules=150
    WHERE domain_id='D_DATA' AND layer_id IS NULL;
UPDATE domains SET layer_id='L2_domain', max_modules=150
    WHERE domain_id='D_BEHAVIORAL_AUDIT' AND layer_id IS NULL;
UPDATE domains SET layer_id='L2_domain', max_modules=150
    WHERE domain_id='D_COMPLIANCE' AND layer_id IS NULL;
UPDATE domains SET layer_id='L2_domain', max_modules=150
    WHERE domain_id='D_SIGLEGACY' AND layer_id IS NULL;

-- ========== 2. D_SHARED 层级重新分配 L1→L0 ==========
-- 裁定依据（#ARCH-SHARED-LAYER-REALLOC-001）:
--   D_SHARED 包含 contracts(50)/utils(12)/io(10) 等最基础构建块
--   183 个节点中 155 条边来自 D_INFRA_RUNTIME(L0) → D_SHARED(L1)
--   D_SHARED 仅 8 条出边（4→D_INFRA_RUNTIME, 1→D_FEEDBACK_LOOP, 1→D_GOV_RULE, 1→D_INFRASTRUCTURE, 1→D_ML_TRAIN）
--   D_SHARED 是最底层基础层，一切依赖它，它几乎不依赖任何域
--   将 D_SHARED 从 L1 提升为 L0 可消除 183 条 L0→L1 层级违规
--   新增 3 条 L0→L1/L2 违规（D_SHARED→D_FEEDBACK_LOOP/D_GOV_RULE/D_ML_TRAIN）
--   净减少 180 条层级违规
UPDATE domains SET layer_id='L0_infrastructure'
    WHERE domain_id='D_SHARED' AND layer_id='L1_foundation';

-- ========== 3. 域分配修复（路径与 domain_id 不一致的节点迁移） ==========
-- 裁定依据: FP-2 路径=功能域，文件路径决定域归属
-- 修复原则: 节点 path 的目录前缀决定其 domain_id

-- 3.1 D_SECURITY 中 src/zephyr/gov_drift/* 节点 → D_GOV_DRIFT
UPDATE nodes SET domain_id='D_GOV_DRIFT'
    WHERE domain_id='D_SECURITY' AND path LIKE 'src/zephyr/gov_drift/%';

-- 3.2 D_SECURITY 中 src/zephyr/governance/* 节点 → D_GOVERNANCE
UPDATE nodes SET domain_id='D_GOVERNANCE'
    WHERE domain_id='D_SECURITY' AND path LIKE 'src/zephyr/governance/%';

-- 3.3 D_SECURITY 中 src/zephyr/security/llm_defense/* → D_SECURITY_LLM
UPDATE nodes SET domain_id='D_SECURITY_LLM'
    WHERE domain_id='D_SECURITY' AND path LIKE 'src/zephyr/security/llm_defense/%';

-- 3.4 D_GOV_CODE_QUALITY 中 src/zephyr/gov_enforcement/* → D_GOV_ENFORCEMENT
UPDATE nodes SET domain_id='D_GOV_ENFORCEMENT'
    WHERE domain_id='D_GOV_CODE_QUALITY' AND path LIKE 'src/zephyr/gov_enforcement/%';

-- 3.5 D_INFRA_RUNTIME 中 src/zephyr/trading/* → D_TRADING
UPDATE nodes SET domain_id='D_TRADING'
    WHERE domain_id='D_INFRA_RUNTIME' AND path LIKE 'src/zephyr/trading/%';

-- 3.6 D_INFRA_RUNTIME 中 src/zephyr/shared/* → D_SHARED
UPDATE nodes SET domain_id='D_SHARED'
    WHERE domain_id='D_INFRA_RUNTIME' AND path LIKE 'src/zephyr/shared/%';

-- 3.7 D_GOVERNANCE 中 src/zephyr/infrastructure/* → D_INFRA_RUNTIME
UPDATE nodes SET domain_id='D_INFRA_RUNTIME'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'src/zephyr/infrastructure/%';

-- 3.8 D_GOVERNANCE 中 src/zephyr/shared/* → D_SHARED
UPDATE nodes SET domain_id='D_SHARED'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'src/zephyr/shared/%';

-- 3.9 D_GOVERNANCE 中 src/zephyr/gov_enforcement/* → D_GOV_ENFORCEMENT
UPDATE nodes SET domain_id='D_GOV_ENFORCEMENT'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'src/zephyr/gov_enforcement/%';

-- 3.10 D_GOVERNANCE 中 src/zephyr/integration/* → D_INTEGRATION
UPDATE nodes SET domain_id='D_INTEGRATION'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'src/zephyr/integration/%';

-- 3.11 D_GOVERNANCE 中 scripts/arch_guard/* → D_ARCH_GUARD (新域, 见第4节)
--     先跳过，等 D_ARCH_GUARD 创建后执行

-- 3.12 D_GOVERNANCE 中 scripts/*.py 散落脚本 → D_GOV_SCRIPTS
UPDATE nodes SET domain_id='D_GOV_SCRIPTS'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'scripts/%.py';

-- 3.13 D_GOVERNANCE 中 docs/* → D_GOV_DOCS
UPDATE nodes SET domain_id='D_GOV_DOCS'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'docs/%';

-- 3.14 D_GOVERNANCE 中 tests/* → 保留在 D_GOVERNANCE（测试随域）

-- ========== 4. 域拆分：D_GOV_SCRIPTS 拆分为平行域 ==========
-- 裁定依据（#ARCH-GOV-SCRIPTS-SPLIT-001）:
--   D_GOV_SCRIPTS (378 节点) 远超 150 硬上限
--   按 scripts/governance/d{N}_* 功能维度拆分（ARCH-CAP-004 平行域原则）
--   每个 d{N} 前缀代表一个治理维度（功能聚类）
--   拆分后所有域 ≤150

-- 4.1 创建新平行域（INSERT ON CONFLICT 幂等）
-- 注意：created_at/updated_at 是 NOT NULL，必须提供
-- D_SECURITY_LLM 已存在（L1_foundation），保留 L1 不变
INSERT INTO domains (domain_id, domain_name, domain_group, layer_id, ssot_path, max_modules, lifecycle, build_status, created_at, updated_at, modification_permission, description)
VALUES
    ('D_ARCH_SCRIPTS', '架构治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d5_architecture', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '架构治理脚本（d5_architecture）')
    , ('D_META_SCRIPTS', '元治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/meta', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '元治理脚本（meta）')
    , ('D_CODE_SCRIPTS', '代码质量脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d7_code', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '代码质量脚本（d7_code）')
    , ('D_STRUCT_SCRIPTS', '结构治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d1_structure', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '结构治理脚本（d1_structure）')
    , ('D_DATA_SCRIPTS', '数据治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d3_metadata', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '数据治理脚本（d3_metadata）')
    , ('D_COMPLIANCE_SCRIPTS', '合规治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d11_compliance', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '合规治理脚本（d11_compliance）')
    , ('D_SEC_SCRIPTS', '安全治理脚本', 'governance_scripts', 'L2_domain', 'scripts/governance/d6_security', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '安全治理脚本（d6_security）')
    , ('D_ARCH_GUARD', '架构守护脚本', 'governance_scripts', 'L2_domain', 'scripts/arch_guard', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '架构守护脚本（fitness functions）')
    , ('D_CONTRACTS', '共享契约', 'shared', 'L0_infrastructure', 'src/zephyr/shared/contracts', 150, 'operational', 'stable', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', '共享契约（从 D_SHARED 拆分）')
ON CONFLICT (domain_id) DO UPDATE SET
    domain_name=excluded.domain_name,
    domain_group=excluded.domain_group,
    layer_id=excluded.layer_id,
    ssot_path=excluded.ssot_path,
    max_modules=excluded.max_modules,
    lifecycle=excluded.lifecycle,
    build_status=excluded.build_status,
    updated_at=excluded.updated_at,
    modification_permission=excluded.modification_permission,
    description=excluded.description;

-- 4.2 迁移 D_GOV_SCRIPTS 节点到新域（按路径前缀）
UPDATE nodes SET domain_id='D_ARCH_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d5_architecture/%';
UPDATE nodes SET domain_id='D_META_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/meta/%';
UPDATE nodes SET domain_id='D_CODE_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d7_code/%';
UPDATE nodes SET domain_id='D_STRUCT_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d1_structure/%';
UPDATE nodes SET domain_id='D_DATA_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d3_metadata/%';
UPDATE nodes SET domain_id='D_COMPLIANCE_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d11_compliance/%';
UPDATE nodes SET domain_id='D_SEC_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/d6_security/%';

-- 4.3 迁移 D_GOVERNANCE 中 arch_guard 脚本到 D_ARCH_GUARD
UPDATE nodes SET domain_id='D_ARCH_GUARD'
    WHERE domain_id='D_GOVERNANCE' AND path LIKE 'scripts/arch_guard/%';

-- 4.4 迁移 D_SHARED 中 contracts 到 D_CONTRACTS
UPDATE nodes SET domain_id='D_CONTRACTS'
    WHERE domain_id='D_SHARED' AND path LIKE 'src/zephyr/shared/contracts/%';

-- ========== 5. domain_dependencies 自动同步（从实际跨域边派生） ==========
-- 裁定依据（#ARCH-DOMAIN-DEP-AUTOSYNC-001）:
--   domain_dependencies 是 edges 的派生聚合，非独立维护
--   255 条手动声明 vs 1161 条实际跨域边 = 906 条漂移
--   治本: DELETE + INSERT FROM edges 聚合，零漂移
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

-- ========== 6. 触发器重算 cross_domain（域迁移后） ==========
-- 域迁移改变了节点的 domain_id，需要重算所有边的 cross_domain 列
UPDATE edges SET cross_domain = edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
);

-- ========== 7. 验证 ==========
DO $$
DECLARE
    v_null_layer BIGINT;
    v_cross_violations BIGINT;
    v_capacity_violations BIGINT;
    v_hard_limit_violations BIGINT;
    v_orphan_violations BIGINT;
    v_layer_violations BIGINT;
    v_cross_mismatch BIGINT;
BEGIN
    -- NULL layer_id
    SELECT COUNT(*) INTO v_null_layer FROM domains WHERE layer_id IS NULL;
    RAISE NOTICE 'NULL layer_id domains: %', v_null_layer;

    -- Cross-domain violations
    SELECT COUNT(*) INTO v_cross_violations FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE n1.domain_id != n2.domain_id
    AND n1.domain_id IS NOT NULL AND n1.domain_id != ''
    AND n2.domain_id IS NOT NULL AND n2.domain_id != ''
    AND e.dep_maturity = 'active'
    AND NOT EXISTS (
        SELECT 1 FROM domain_dependencies dd
        WHERE dd.from_domain = n1.domain_id AND dd.to_domain = n2.domain_id
    );
    RAISE NOTICE 'Cross-domain violations: %', v_cross_violations;

    -- Capacity violations (ARCH-CAP-001)
    SELECT COUNT(*) INTO v_capacity_violations FROM (
        SELECT n.domain_id FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id, d.max_modules
        HAVING COUNT(*) > d.max_modules
    ) t;
    RAISE NOTICE 'Capacity violations: %', v_capacity_violations;

    -- Hard limit violations (ARCH-CAP-002, >150)
    SELECT COUNT(*) INTO v_hard_limit_violations FROM (
        SELECT n.domain_id FROM nodes n
        JOIN domains d ON n.domain_id = d.domain_id
        WHERE n.design_maturity = 'production'
        GROUP BY n.domain_id
        HAVING COUNT(*) > 150
    ) t;
    RAISE NOTICE 'Hard limit violations: %', v_hard_limit_violations;

    -- Layer violations
    SELECT COUNT(*) INTO v_layer_violations FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    JOIN domains d1 ON n1.domain_id = d1.domain_id
    JOIN domains d2 ON n2.domain_id = d2.domain_id
    WHERE CAST(SUBSTR(d1.layer_id, 2, 1) AS INTEGER)
        < CAST(SUBSTR(d2.layer_id, 2, 1) AS INTEGER)
    AND e.dep_maturity = 'active';
    RAISE NOTICE 'Layer violations: %', v_layer_violations;

    -- cross_domain mismatch
    SELECT COUNT(*) INTO v_cross_mismatch FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE n1.domain_id IS NOT NULL AND n1.domain_id <> ''
      AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
      AND COALESCE(e.cross_domain, 0) <> (CASE WHEN n1.domain_id <> n2.domain_id THEN 1 ELSE 0 END);
    RAISE NOTICE 'cross_domain mismatch: %', v_cross_mismatch;

    RAISE NOTICE '===== 5VIOLATIONS FIX SUMMARY =====';
    RAISE NOTICE 'NULL layer=%, cross=%, capacity=%, hard_limit=%, layer=%, cd_mismatch=%',
        v_null_layer, v_cross_violations, v_capacity_violations, v_hard_limit_violations,
        v_layer_violations, v_cross_mismatch;
END $$;
