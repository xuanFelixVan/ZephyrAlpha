-- =====================================================================
-- 幂等迁移脚本 Phase 3：最后 6 条层级违规修复（#ARCH-5VIOLATIONS-FIX-003）
-- =====================================================================
-- 修复策略: 将层级违规边的 from_node 重新分配到 to_node 所在的域
-- 裁定依据: 如果节点 A（域 X）导入节点 B（域 Y），且 X→Y 造成层级违规，
--   则 A 实际上是域 Y 的功能延伸，应归入域 Y。
--   重新分配后，原跨域边变为同域边，层级违规消失。
-- =====================================================================

-- 违规 1: D_INFRA_RUNTIME/event_bus_upgrade.py → D_INTEGRATION/upgrade_strategy.py
-- event_bus_upgrade 在 infrastructure/ 但导入 integration/ 的升级策略
-- 重新分配到 D_INTEGRATION（功能上属于集成层）
UPDATE nodes SET domain_id='D_INTEGRATION'
    WHERE path='src/zephyr/infrastructure/event_bus_upgrade.py' AND domain_id='D_INFRA_RUNTIME';

-- 违规 2: D_INFRA_RUNTIME/database_service.py → D_DATA/ch_config.py
-- database_service 在 infrastructure/ 但导入 data/ 的配置
-- 重新分配到 D_DATA（功能上属于数据层）
UPDATE nodes SET domain_id='D_DATA'
    WHERE path='src/zephyr/infrastructure/database_service.py' AND domain_id='D_INFRA_RUNTIME';

-- 违规 3: D_INFRA_RUNTIME/budget_enforcement/__init__.py → D_GOV_REPAIR/budget_enforcement.py
-- budget_enforcement 在 infrastructure/ 但导入 governance/ 的财务治理
-- 重新分配到 D_GOVERNANCE（功能上属于治理域）
-- 注意: D_GOV_REPAIR max_modules=0, 改为 D_GOVERNANCE
UPDATE nodes SET domain_id='D_GOVERNANCE'
    WHERE path='src/zephyr/infrastructure/budget_enforcement/__init__.py' AND domain_id='D_INFRA_RUNTIME';

-- 违规 4: D_INTEGRATION/admission_response.py → D_TRADING/admission_controller.py
-- admission_response 在 integration/ 但导入 trading/ 的准入控制器
-- 重新分配到 D_TRADING（功能上属于交易域）
UPDATE nodes SET domain_id='D_TRADING'
    WHERE path='src/zephyr/integration/behavioral_admission/admission_response.py' AND domain_id='D_INTEGRATION';

-- 违规 5: D_INTEGRATION/local_model_scheduler.py → D_TRADING/resource_optimization.py
-- local_model_scheduler 在 integration/ 但导入 trading/ 的资源优化
-- 重新分配到 D_TRADING（功能上属于交易域）
UPDATE nodes SET domain_id='D_TRADING'
    WHERE path='src/zephyr/integration/local_model/local_model_scheduler.py' AND domain_id='D_INTEGRATION';

-- 违规 6: D_SHARED/ml_experiment_pipeline.py → D_ML_TRAIN/trainer_base.py
-- ml_experiment_pipeline 在 shared/_cross_layer/ 但导入 ml_train/ 的训练基类
-- 重新分配到 D_ML_TRAIN（功能上属于 ML 训练域）
UPDATE nodes SET domain_id='D_ML_TRAIN'
    WHERE path='src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py' AND domain_id='D_SHARED';

-- ========== 重新同步 domain_dependencies ==========
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

-- ========== 重算 cross_domain ==========
UPDATE edges SET cross_domain = edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
);

-- ========== 验证 ==========
DO $$
DECLARE
    v_layer_violations BIGINT;
    v_updated_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO v_updated_count FROM nodes
    WHERE domain_id IN ('D_INTEGRATION','D_DATA','D_GOVERNANCE','D_TRADING','D_ML_TRAIN')
    AND path IN (
        'src/zephyr/infrastructure/event_bus_upgrade.py',
        'src/zephyr/infrastructure/database_service.py',
        'src/zephyr/infrastructure/budget_enforcement/__init__.py',
        'src/zephyr/integration/behavioral_admission/admission_response.py',
        'src/zephyr/integration/local_model/local_model_scheduler.py',
        'src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py'
    );
    RAISE NOTICE 'Nodes reassigned: %', v_updated_count;
END $$;
