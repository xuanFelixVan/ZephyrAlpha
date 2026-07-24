-- 创建 D_ARCHIVE_SCRIPTS 域并迁移归档脚本
INSERT INTO domains (domain_id, domain_name, domain_group, layer_id, ssot_path, max_modules, lifecycle, build_status, created_at, updated_at, modification_permission, description)
VALUES ('D_ARCHIVE_SCRIPTS', 'Archived Scripts', 'governance_scripts', 'L2_domain', 'scripts/governance/_archive', 150, 'deprecated', 'deprecated', '2026-07-25T00:00:00+00:00', '2026-07-25T00:00:00+00:00', 'ai_modifiable', 'Archived scripts (no longer maintained)')
ON CONFLICT (domain_id) DO UPDATE SET
    domain_name=excluded.domain_name,
    domain_group=excluded.domain_group,
    layer_id=excluded.layer_id,
    ssot_path=excluded.ssot_path,
    max_modules=excluded.max_modules,
    lifecycle=excluded.lifecycle,
    build_status=excluded.build_status,
    updated_at=excluded.updated_at;

-- 迁移 _archive 节点到 D_ARCHIVE_SCRIPTS
UPDATE nodes SET domain_id='D_ARCHIVE_SCRIPTS'
    WHERE domain_id='D_GOV_SCRIPTS' AND path LIKE 'scripts/governance/_archive/%';

-- 重新同步 domain_dependencies
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

-- 重算 cross_domain
UPDATE edges SET cross_domain = edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
);

-- 验证
SELECT 'D_GOV_SCRIPTS' AS dom, COUNT(*) AS cnt FROM nodes WHERE domain_id='D_GOV_SCRIPTS' AND design_maturity='production'
UNION ALL
SELECT 'D_ARCHIVE_SCRIPTS', COUNT(*) FROM nodes WHERE domain_id='D_ARCHIVE_SCRIPTS';
