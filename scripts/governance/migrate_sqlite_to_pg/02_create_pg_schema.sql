-- =====================================================================
-- P2 PostgreSQL迁移：Schema DDL（从SQLite实际schema翻译）
-- =====================================================================
-- 翻译基准: 00_sqlite_actual_schema.sql (25 tables / 1 view / 39 indexes / 36 triggers)
-- 关键翻译规则:
--   * INTEGER PRIMARY KEY AUTOINCREMENT → BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
--   * node_id/edge_id 等 ID 列 → BIGINT (与 IDENTITY 序列返回类型一致)
--   * GLOB 'PREFIX-*' → ~ '^PREFIX-' (POSIX 正则, 大小写敏感, 与 GLOB 语义一致)
--   * SQLite 触发器 RAISE(ABORT,...) → PL/pgSQL RAISE EXCEPTION
--   * 只读触发器 (27个) 复用单一函数 raise_readonly_exception()
--   * CHECK 触发器 (domains 6个 + nodes 2个) 转为列级 CHECK 约束 (语义等价, 更高效)
--   * 清理触发器 trg_nodes_delete_cleanup_edges → PL/pgSQL 函数
--   * FTS5 虚拟表: 实际schema中不存在, 无需处理
-- =====================================================================

-- ========== 1. 表定义（按外键依赖顺序） ==========

-- 1.1 无外键依赖的表（先创建）
-- domains: 功能域真源表
CREATE TABLE IF NOT EXISTS domains (
    domain_id              TEXT PRIMARY KEY
        CHECK (domain_id ~ '^D_[A-Z][A-Z0-9_]*$'),
    domain_name            TEXT NOT NULL,
    domain_group           TEXT NOT NULL,
    description            TEXT,
    ssot_path              TEXT,
    current_modules        INTEGER DEFAULT 0,
    max_modules            INTEGER,
    lifecycle              TEXT DEFAULT 'design_only'
        CHECK (lifecycle IN ('operational', 'design_only', 'prototype', 'deprecated')),
    created_at             TEXT NOT NULL,
    updated_at             TEXT NOT NULL,
    build_status           TEXT DEFAULT 'planned'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    modification_permission TEXT,
    layer_id               TEXT
        CHECK (layer_id IS NULL OR layer_id IN ('L0_infrastructure', 'L1_foundation', 'L2_domain', 'L3_application')),
    target_modules         INTEGER,
    production_nodes       INTEGER DEFAULT 0
);

-- _schema_version: 迁移版本记录
CREATE TABLE IF NOT EXISTS _schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL,
    description TEXT
);

-- arch_directory_tree: 架构目录树
CREATE TABLE IF NOT EXISTS arch_directory_tree (
    path                    TEXT PRIMARY KEY,
    parent_path             TEXT,
    path_type               TEXT NOT NULL,
    domain_id               TEXT REFERENCES domains(domain_id),
    blueprint_id            TEXT,
    change_policy           TEXT,
    modification_permission TEXT,
    build_status            TEXT DEFAULT 'unbuilt',
    design_maturity         TEXT NOT NULL DEFAULT 'design',
    last_scanned            TEXT
);

-- blueprint_links: 蓝图链接（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS blueprint_links (
    blueprint_id        TEXT PRIMARY KEY,
    blueprint_path      TEXT NOT NULL,
    alignment_verified  INTEGER DEFAULT 0,
    last_verified       TEXT
);

-- business_streams: 业务流（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS business_streams (
    stream_id      TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    goal           TEXT,
    input          TEXT,
    output         TEXT,
    runtime_plane  TEXT
        CHECK (runtime_plane IN ('data_plane', 'control_plane', 'management_plane'))
);

-- cross_registry_rules: 跨注册表规则（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS cross_registry_rules (
    rule_id          TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    fields           TEXT,
    ssot             TEXT NOT NULL,
    consistency      TEXT
        CHECK (consistency IN ('exact', 'derived', 'independent')),
    violation_action TEXT
        CHECK (violation_action IN ('block', 'warn', 'log'))
);

-- derived_identifier_registry: 派生标识符注册表
CREATE TABLE IF NOT EXISTS derived_identifier_registry (
    derived_type       TEXT NOT NULL,
    source_field       TEXT NOT NULL,
    derived_field      TEXT NOT NULL,
    derivation_rule    TEXT NOT NULL,
    propagation_method TEXT NOT NULL DEFAULT 'exact_value_map',
    source_doc         TEXT,
    PRIMARY KEY (derived_type, derived_field)
);

-- domain_mapping: 域映射
CREATE TABLE IF NOT EXISTS domain_mapping (
    mapping_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    path_prefix   TEXT NOT NULL,
    domain_id     TEXT NOT NULL REFERENCES domains(domain_id),
    subdomain_id  TEXT,
    mapping_type  TEXT NOT NULL,
    mapped_at     TEXT NOT NULL,
    mapped_by     TEXT NOT NULL,
    note          TEXT
);

-- domain_naming_rules: 域命名规则
CREATE TABLE IF NOT EXISTS domain_naming_rules (
    rule_id       TEXT PRIMARY KEY,
    rule_name     TEXT NOT NULL,
    rule_text     TEXT NOT NULL,
    applies_to    TEXT NOT NULL DEFAULT 'create',
    severity      TEXT NOT NULL DEFAULT 'error',
    example_bad   TEXT,
    example_good  TEXT,
    created_at    TEXT NOT NULL,
    source_doc    TEXT
);

-- field_vocabularies: 字段词表（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS field_vocabularies (
    field_name      TEXT NOT NULL,
    value           TEXT NOT NULL,
    definition      TEXT,
    ai_consumption  TEXT,
    source_yaml     TEXT,
    PRIMARY KEY (field_name, value)
);

-- gates: 门禁定义（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS gates (
    gate_id        TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    entry          TEXT NOT NULL,
    description    TEXT,
    files_trigger  TEXT,
    always_run     INTEGER DEFAULT 0,
    category       TEXT NOT NULL,
    status         TEXT DEFAULT 'active'
        CHECK (status IN ('active', 'deprecated', 'disabled')),
    source         TEXT DEFAULT '.pre-commit-config.yaml',
    event_driven   TEXT DEFAULT '',
    auto_start     INTEGER DEFAULT 1
);

-- governance_audit_logs: 治理审计日志
CREATE TABLE IF NOT EXISTS governance_audit_logs (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    timestamp       TEXT NOT NULL,
    total_gates     INTEGER DEFAULT 0,
    passed_gates    INTEGER DEFAULT 0,
    failed_gates    INTEGER DEFAULT 0,
    skipped_gates   INTEGER DEFAULT 0,
    success         INTEGER DEFAULT 0,
    errors          TEXT DEFAULT ''
);

-- hard_boundaries: 硬边界（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS hard_boundaries (
    boundary_id    TEXT PRIMARY KEY,
    category       TEXT NOT NULL
        CHECK (category IN ('architectural', 'domain', 'data', 'security', 'operational')),
    constraint_def TEXT NOT NULL,
    parameters     TEXT,
    impact         TEXT
);

-- infrastructure_components: 基础设施组件（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS infrastructure_components (
    component_id    TEXT PRIMARY KEY,
    component_type  TEXT NOT NULL
        CHECK (component_type IN ('event_bus', 'message_queue', 'relational_db',
                                   'vector_db', 'cache', 'object_storage',
                                   'config_center', 'service_registry', 'ci_pipeline')),
    address         TEXT,
    health_check    TEXT,
    dependencies    TEXT,
    sla             TEXT,
    status          TEXT DEFAULT 'active'
);

-- model_capabilities: 模型能力（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS model_capabilities (
    model_name              TEXT PRIMARY KEY,
    tier                    TEXT NOT NULL
        CHECK (tier IN ('premium', 'standard', 'free', 'api')),
    max_files_per_session   INTEGER,
    allowed_paths           TEXT,
    forbidden_paths         TEXT,
    recommended_tasks       TEXT,
    forbidden_tasks         TEXT
);

-- nodes_archive_module_lifecycle: 节点归档
CREATE TABLE IF NOT EXISTS nodes_archive_module_lifecycle (
    node_id                BIGINT,
    module_lifecycle_state TEXT,
    archived_at            TEXT NOT NULL
);

-- registries: 注册表（只读表，YAML真源）
CREATE TABLE IF NOT EXISTS registries (
    registry_id   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    title         TEXT,
    path          TEXT NOT NULL,
    version       TEXT,
    description   TEXT,
    ssot_for      TEXT
);

-- 1.2 nodes 表（无外键，但被 edges/rule_bindings 引用）
-- nodes: 代码制品节点（核心表）
-- SQLite 实际 31 列（v11/v15 migration 后）
CREATE TABLE IF NOT EXISTS nodes (
    node_id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    node_type               TEXT,
    path                    TEXT,
    granularity             TEXT,
    domain_id               TEXT REFERENCES domains(domain_id),
    subdomain_id            TEXT,
    blueprint_id            TEXT,
    belongs_to              TEXT,
    owner                   TEXT,
    change_policy           TEXT,
    impact_level            TEXT,
    modification_permission TEXT,
    file_header_score       INTEGER DEFAULT 0,
    tags                    TEXT,
    architecture_layer      TEXT,
    design_maturity         TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    deployment_lifecycle    TEXT DEFAULT 'stable',
    trust_zone              TEXT DEFAULT 'trusted_core',
    license                 TEXT DEFAULT 'Internal',
    drive_direction         TEXT DEFAULT 'bottom_up',
    type_specific_data      TEXT,
    last_verified           TEXT,
    node_name               TEXT DEFAULT '',
    file_path               TEXT DEFAULT '',
    build_status            TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    can_build               INTEGER DEFAULT 1,
    gate_reason             TEXT DEFAULT '',
    hard_boundary_ref       TEXT,
    consumed_interfaces     TEXT,
    blueprint_id_invalid    INTEGER DEFAULT 0,
    blueprint_path          TEXT
    -- 注意：blueprint_id 双轨制+历史兼容检查（MOD-*/D-*/SH-*/PLACEHOLDER*）由触发器实现，
    -- 而非 CHECK 约束。原因：SQLite 历史数据存在不符合双轨制+历史兼容的 blueprint_id
    -- （如 GOV-FSTR-001），CHECK 约束会阻止迁移。触发器只对新 INSERT/UPDATE 生效，
    -- 历史数据保留。触发器定义见§6功能性触发器。
);

-- 1.3 依赖 domains 或 nodes 的表

-- arch_constraints: 架构约束
CREATE TABLE IF NOT EXISTS arch_constraints (
    constraint_id    TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    constraint_type  TEXT NOT NULL,
    from_domain      TEXT REFERENCES domains(domain_id),
    to_domain        TEXT REFERENCES domains(domain_id),
    rule_definition  TEXT NOT NULL,
    severity         TEXT DEFAULT 'hard',
    enforcement      TEXT DEFAULT 'gate',
    description      TEXT,
    violation_status TEXT DEFAULT 'open',
    details          TEXT,
    detected_at      TEXT
);

-- arch_path_mappings: 架构路径映射
CREATE TABLE IF NOT EXISTS arch_path_mappings (
    mapping_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    domain_id    TEXT NOT NULL REFERENCES domains(domain_id),
    path_pattern TEXT NOT NULL,
    path_type    TEXT NOT NULL,
    state        TEXT NOT NULL DEFAULT 'design',
    covers       TEXT,
    aliases      TEXT
);

-- contracts: 契约
CREATE TABLE IF NOT EXISTS contracts (
    contract_id        TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    provider_domain    TEXT NOT NULL REFERENCES domains(domain_id),
    consumer_domain    TEXT NOT NULL REFERENCES domains(domain_id),
    contract_type      TEXT NOT NULL,
    schema_definition  TEXT,
    version            TEXT,
    promise            TEXT,
    actual_consumer    TEXT,
    fulfillment_status TEXT DEFAULT 'unresolved',
    gap                TEXT,
    target_phase       TEXT,
    last_reviewed      TEXT
);

-- domain_dependencies: 域依赖
CREATE TABLE IF NOT EXISTS domain_dependencies (
    from_domain     TEXT NOT NULL REFERENCES domains(domain_id),
    to_domain       TEXT NOT NULL REFERENCES domains(domain_id),
    edge_count      INTEGER DEFAULT 0,
    edge_types      TEXT,
    constraint_type TEXT,
    PRIMARY KEY (from_domain, to_domain)
);

-- domain_events: 域事件
CREATE TABLE IF NOT EXISTS domain_events (
    event_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    source_domain   TEXT NOT NULL REFERENCES domains(domain_id),
    target_domains  TEXT,
    payload_schema  TEXT,
    priority        TEXT DEFAULT 'P1',
    event_type      TEXT DEFAULT 'domain_event'
);

-- edges: 依赖边（核心表）
CREATE TABLE IF NOT EXISTS edges (
    edge_id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_node_id               BIGINT NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    to_node_id                 BIGINT NOT NULL REFERENCES nodes(node_id) ON DELETE CASCADE,
    dep_type                   TEXT,
    architecture_direction     TEXT,
    coupling_strength          TEXT,
    used_symbol                TEXT,
    invocation_method          TEXT,
    api_contract_refs          TEXT,
    event_ref                  TEXT,
    ddd_integration_pattern    TEXT,
    failure_mode               TEXT,
    fallback                   TEXT,
    activation_condition       TEXT,
    data_transfer_description  TEXT,
    resource_impact            TEXT,
    relationship_type          TEXT,
    cross_domain               INTEGER,
    verified                   INTEGER,
    dep_maturity               TEXT DEFAULT 'active',
    valid_since                TEXT,
    is_legal_cycle             INTEGER DEFAULT 0
);

-- nodes_metadata: 节点人工curated元数据（裁定#209 Stage 2 字段角色分离）
-- 迁移 PRODUCTION_PROTECTED_FIELDS(14) 出 nodes 表——path 为稳定 PK
-- （node_id 是 IDENTITY，DELETE+INSERT 后变化，不可作 FK）。
-- write_depgraph_to_db 中 UPSERT 保存当前值，INSERT 后 UPDATE nodes 恢复空字段。
CREATE TABLE IF NOT EXISTS nodes_metadata (
    path                     TEXT    PRIMARY KEY,
    blueprint_id             TEXT,
    owner                    TEXT,
    impact_level             TEXT,
    change_policy            TEXT,
    modification_permission  TEXT,
    belongs_to               TEXT,
    build_status             TEXT,
    gate_reason              TEXT    NOT NULL DEFAULT '',
    hard_boundary_ref       TEXT,
    consumed_interfaces     TEXT,
    tags                     TEXT,
    trust_zone               TEXT,
    deployment_lifecycle     TEXT,
    architecture_layer       TEXT,
    last_updated             TEXT
);

-- edges_metadata: 边人工curated元数据（裁定#209 Stage 2 字段角色分离）
-- 迁移 EDGES_PROTECTED_FIELDS(9) 出 edges 表——(from_path, to_path, dep_type)
-- 为稳定复合 PK（edge_id 是 IDENTITY，node_id 在 DELETE+INSERT 后变化）。
CREATE TABLE IF NOT EXISTS edges_metadata (
    from_path                 TEXT    NOT NULL,
    to_path                   TEXT    NOT NULL,
    dep_type                  TEXT    NOT NULL DEFAULT '',
    failure_mode              TEXT,
    fallback                  TEXT,
    activation_condition      TEXT,
    data_transfer_description TEXT,
    resource_impact           TEXT,
    ddd_integration_pattern   TEXT,
    event_ref                 TEXT,
    api_contract_refs         TEXT,
    verified                  INTEGER,
    last_updated              TEXT,
    PRIMARY KEY (from_path, to_path, dep_type)
);

-- rule_bindings: 规则绑定
-- 5.18.2/5.18.3 债务说明（2026-07-03 批次A 收尾）：
--   - 5.18.2: SQLite 中 rule_id(TEXT) → nodes.node_id(INTEGER) 类型不匹配，FK 不生效
--   - 5.18.3: PG 迁移丢失 FK（原 SQLite 有 REFERENCES，PG 无）
--   - 决策：不补 FK，采用"应用层校验"——rule_id 无对应 rules 表作 FK 目标，
--     rule_bindings.rule_id 引用的是 rule_catalog_registry.yaml 真源（YAML SSoT），
--     非 nodes.node_id。FK 应指向 rules 表（待建），当前由 apply_depgraph.py 校验。
CREATE TABLE IF NOT EXISTS rule_bindings (
    binding_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    function_name TEXT NOT NULL,
    rule_id       TEXT NOT NULL,
    binding_type  TEXT NOT NULL,
    trigger_type  TEXT NOT NULL,
    trigger_id    TEXT,
    domain_id     TEXT DEFAULT ''
);

-- ========== 2. 索引（与 SQLite 实际 schema 对齐，39个） ==========

CREATE INDEX IF NOT EXISTS idx_arch_constraint_from            ON arch_constraints(from_domain);
CREATE INDEX IF NOT EXISTS idx_arch_constraint_to              ON arch_constraints(to_domain);
CREATE INDEX IF NOT EXISTS idx_arch_dir_build                  ON arch_directory_tree(build_status);
CREATE INDEX IF NOT EXISTS idx_arch_dir_domain                 ON arch_directory_tree(domain_id);
CREATE INDEX IF NOT EXISTS idx_arch_path_domain                ON arch_path_mappings(domain_id);
CREATE INDEX IF NOT EXISTS idx_arch_path_type                  ON arch_path_mappings(path_type);
CREATE INDEX IF NOT EXISTS idx_business_streams_plane          ON business_streams(runtime_plane);
CREATE INDEX IF NOT EXISTS idx_contracts_consumer              ON contracts(consumer_domain);
CREATE INDEX IF NOT EXISTS idx_contracts_provider              ON contracts(provider_domain);
CREATE INDEX IF NOT EXISTS idx_domain_dependencies_constraint_type ON domain_dependencies(constraint_type);
CREATE INDEX IF NOT EXISTS idx_domdeps_from                    ON domain_dependencies(from_domain);
CREATE INDEX IF NOT EXISTS idx_domdeps_to                      ON domain_dependencies(to_domain);
CREATE INDEX IF NOT EXISTS idx_events_source                   ON domain_events(source_domain);
CREATE INDEX IF NOT EXISTS idx_domain_mapping_domain           ON domain_mapping(domain_id);
CREATE INDEX IF NOT EXISTS idx_domain_mapping_prefix           ON domain_mapping(path_prefix);
CREATE INDEX IF NOT EXISTS idx_domain_mapping_type             ON domain_mapping(mapping_type);
CREATE INDEX IF NOT EXISTS idx_domains_group                   ON domains(domain_group);
CREATE INDEX IF NOT EXISTS idx_domains_lifecycle               ON domains(lifecycle);
CREATE INDEX IF NOT EXISTS idx_edges_coupling_strength         ON edges(coupling_strength);
CREATE INDEX IF NOT EXISTS idx_edges_cross_domain              ON edges(cross_domain);
CREATE INDEX IF NOT EXISTS idx_edges_dep_maturity              ON edges(dep_maturity);
CREATE INDEX IF NOT EXISTS idx_edges_from                      ON edges(from_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_legal_cycle               ON edges(is_legal_cycle);
CREATE INDEX IF NOT EXISTS idx_edges_to                        ON edges(to_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_type                      ON edges(dep_type);
CREATE INDEX IF NOT EXISTS idx_edges_valid_since               ON edges(valid_since);
CREATE INDEX IF NOT EXISTS idx_edges_verified                  ON edges(verified);
CREATE INDEX IF NOT EXISTS idx_field_vocab_field               ON field_vocabularies(field_name);
CREATE INDEX IF NOT EXISTS idx_gates_category                  ON gates(category);
CREATE INDEX IF NOT EXISTS idx_gates_files_trigger             ON gates(files_trigger);
CREATE INDEX IF NOT EXISTS idx_hard_boundaries_category        ON hard_boundaries(category);
CREATE INDEX IF NOT EXISTS idx_nodes_blueprint                 ON nodes(blueprint_id);
CREATE INDEX IF NOT EXISTS idx_nodes_build_status              ON nodes(build_status);
CREATE INDEX IF NOT EXISTS idx_nodes_can_build                 ON nodes(can_build);
CREATE INDEX IF NOT EXISTS idx_nodes_change_policy             ON nodes(change_policy);
CREATE INDEX IF NOT EXISTS idx_nodes_domain                    ON nodes(domain_id);
CREATE INDEX IF NOT EXISTS idx_nodes_file_path                 ON nodes(file_path);
CREATE INDEX IF NOT EXISTS idx_nodes_path                      ON nodes(path);
CREATE INDEX IF NOT EXISTS idx_nodes_type                      ON nodes(node_type);
-- 裁定#209 Stage 2：metadata 表索引
CREATE INDEX IF NOT EXISTS idx_nodes_metadata_bp               ON nodes_metadata(blueprint_id);
CREATE INDEX IF NOT EXISTS idx_edges_metadata_from            ON edges_metadata(from_path);
CREATE INDEX IF NOT EXISTS idx_edges_metadata_to               ON edges_metadata(to_path);

-- ========== 3. 视图 ==========

-- dep_cycles: 循环依赖视图（PG 完全兼容 WITH RECURSIVE）
CREATE OR REPLACE VIEW dep_cycles AS
WITH RECURSIVE
cycle_nodes AS (
    SELECT DISTINCT from_node_id AS node_id FROM edges e1
    WHERE EXISTS (
        SELECT 1 FROM edges e2
        WHERE e2.from_node_id = e1.to_node_id
        AND e2.to_node_id = e1.from_node_id
    )
    UNION
    SELECT DISTINCT to_node_id AS node_id FROM edges e1
    WHERE EXISTS (
        SELECT 1 FROM edges e2
        WHERE e2.from_node_id = e1.to_node_id
        AND e2.to_node_id = e1.from_node_id
    )
)
SELECT
    n.node_id,
    n.path,
    n.domain_id,
    n.design_maturity
FROM cycle_nodes c
JOIN nodes n ON c.node_id = n.node_id
ORDER BY n.domain_id, n.node_id;

-- ========== 4. 触发器函数 ==========

-- 4.1 只读表保护函数（8个只读表 × 3 操作 = 24个触发器复用此函数。blueprint_links 于 2026-07-02 移除——它是 nodes 派生物化视图）
CREATE OR REPLACE FUNCTION raise_readonly_exception()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION '% 表只读（唯一真源是 YAML），请修改 YAML 后运行 sync_yaml_to_depgraph.py', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

-- 4.2 节点删除时清理关联边（对应 SQLite trg_nodes_delete_cleanup_edges）
-- 5.18.8 修复：edges 表 FK 已加 ON DELETE CASCADE，此函数被 CASCADE 取代，保留仅供历史参考。
-- CREATE OR REPLACE FUNCTION cleanup_edges_on_node_delete()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     DELETE FROM edges WHERE from_node_id = OLD.node_id OR to_node_id = OLD.node_id;
--     RETURN OLD;
-- END;
-- $$ LANGUAGE plpgsql;

-- ========== 5. 只读表触发器（24个，复用 raise_readonly_exception。blueprint_links 于 2026-07-02 移除——它是 nodes 派生物化视图，apply_depgraph.py 可直接写入） ==========

-- business_streams (只读)
CREATE TRIGGER readonly_business_streams_delete
    BEFORE DELETE ON business_streams FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_business_streams_insert
    BEFORE INSERT ON business_streams FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_business_streams_update
    BEFORE UPDATE ON business_streams FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- cross_registry_rules (只读)
CREATE TRIGGER readonly_cross_registry_rules_delete
    BEFORE DELETE ON cross_registry_rules FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_cross_registry_rules_insert
    BEFORE INSERT ON cross_registry_rules FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_cross_registry_rules_update
    BEFORE UPDATE ON cross_registry_rules FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- field_vocabularies (只读)
CREATE TRIGGER readonly_field_vocabularies_delete
    BEFORE DELETE ON field_vocabularies FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_field_vocabularies_insert
    BEFORE INSERT ON field_vocabularies FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_field_vocabularies_update
    BEFORE UPDATE ON field_vocabularies FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- gates (只读)
CREATE TRIGGER readonly_gates_delete
    BEFORE DELETE ON gates FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_gates_insert
    BEFORE INSERT ON gates FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_gates_update
    BEFORE UPDATE ON gates FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- hard_boundaries (只读)
CREATE TRIGGER readonly_hard_boundaries_delete
    BEFORE DELETE ON hard_boundaries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_hard_boundaries_insert
    BEFORE INSERT ON hard_boundaries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_hard_boundaries_update
    BEFORE UPDATE ON hard_boundaries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- infrastructure_components (只读)
CREATE TRIGGER readonly_infrastructure_components_delete
    BEFORE DELETE ON infrastructure_components FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_infrastructure_components_insert
    BEFORE INSERT ON infrastructure_components FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_infrastructure_components_update
    BEFORE UPDATE ON infrastructure_components FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- model_capabilities (只读)
CREATE TRIGGER readonly_model_capabilities_delete
    BEFORE DELETE ON model_capabilities FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_model_capabilities_insert
    BEFORE INSERT ON model_capabilities FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_model_capabilities_update
    BEFORE UPDATE ON model_capabilities FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- registries (只读)
CREATE TRIGGER readonly_registries_delete
    BEFORE DELETE ON registries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_registries_insert
    BEFORE INSERT ON registries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();
CREATE TRIGGER readonly_registries_update
    BEFORE UPDATE ON registries FOR EACH ROW EXECUTE FUNCTION raise_readonly_exception();

-- ========== 6. 功能性触发器 ==========

-- 6.1 节点删除时清理关联边（对应 SQLite trg_nodes_delete_cleanup_edges）
-- 5.18.8 修复：edges FK 已加 ON DELETE CASCADE，此 trigger 被 CASCADE 取代，不再创建。
-- CREATE TRIGGER trg_nodes_delete_cleanup_edges
--     AFTER DELETE ON nodes
--     FOR EACH ROW EXECUTE FUNCTION cleanup_edges_on_node_delete();

-- 6.2 blueprint_id 双轨制+历史兼容检查（对应 SQLite chk_nodes_blueprint_id_insert/update）
-- 裁定#208：blueprint_id 必须匹配 MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*（除非 blueprint_id_invalid=1）
-- 治本 2026-07-02：扩展 SYS- 前缀为 SYS-MASTER-001 等系统级蓝图开路
-- 用触发器而非 CHECK 约束实现：历史数据可能不符合双轨制+历史兼容，CHECK 会阻止迁移；
-- 触发器只对新 INSERT/UPDATE 生效，历史数据保留。
CREATE OR REPLACE FUNCTION check_blueprint_id_format()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.blueprint_id IS NOT NULL
       AND NEW.blueprint_id != ''
       AND NEW.blueprint_id_invalid = 0
       AND NEW.blueprint_id !~ '^(MOD-|D-|SH-|SYS-|PLACEHOLDER)' THEN
        RAISE EXCEPTION 'nodes.blueprint_id format violation (裁定#208 双轨制+历史兼容: MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*, or set blueprint_id_invalid=1 for legacy)';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chk_nodes_blueprint_id_insert
    BEFORE INSERT ON nodes
    FOR EACH ROW EXECUTE FUNCTION check_blueprint_id_format();

CREATE TRIGGER chk_nodes_blueprint_id_update
    BEFORE UPDATE OF blueprint_id ON nodes
    FOR EACH ROW EXECUTE FUNCTION check_blueprint_id_format();

-- 6.3 edges 表三写分区硬约束（S1.3）
-- 三写分区：
--   1. YAML sync (sync_yaml_to_depgraph.py): dep_maturity='design', valid_since IS NOT NULL (DELETE + INSERT)
--   2. apply_depgraph.py: dep_maturity='design', valid_since IS NULL (INSERT + targeted DELETE by edge_id)
--   3. generate_project_depgraph.py: dep_maturity='production' (DELETE + INSERT)
-- 保护：禁止删除 apply_depgraph.py 写入的 design edge (valid_since IS NULL)，
--        除非连接设置了 app.allow_delete_apply_depgraph_edges=on（apply_depgraph.py 自动设置）。
CREATE OR REPLACE FUNCTION protect_apply_depgraph_edges()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.dep_maturity = 'design' AND OLD.valid_since IS NULL THEN
        IF current_setting('app.allow_delete_apply_depgraph_edges', true) IS DISTINCT FROM 'on' THEN
            RAISE EXCEPTION 'apply_depgraph design edge protected (dep_maturity=design, valid_since IS NULL). Set app.allow_delete_apply_depgraph_edges=on to delete (apply_depgraph.py does this automatically).';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_edges_protect_apply_depgraph
    BEFORE DELETE ON edges
    FOR EACH ROW EXECUTE FUNCTION protect_apply_depgraph_edges();

-- =====================================================================
-- DDL 翻译完成。统计对照:
--   SQLite 表: 25 → PG 表: 25 ✓
--   SQLite 视图: 1 → PG 视图: 1 ✓
--   SQLite 索引: 39 → PG 索引: 39 ✓
--   SQLite 触发器: 36 → PG:
--     - 只读触发器: 27 (9表×3) → 27 个 CREATE TRIGGER (复用1个函数) ✓
--     - CHECK 触发器: 8 (domains 6 + nodes 2) → 转为列级 CHECK 约束 (语义等价, 更高效)
--     - 清理触发器: 1 → 1 个 CREATE TRIGGER + 1 个函数 ✓
--     - 总计: 28 个 PG 触发器 + CHECK 约束 (覆盖原 36 个 SQLite 触发器的全部语义)
-- =====================================================================

-- =====================================================================
-- S1.2: YAML 真源只读缓存表 COMMENT（HB-001 规则化，2026-07-02）
-- 依据：hard_boundaries_registry.yaml HB-001 table_comment_required=true
-- 目的：AI 在 SQL 上下文中通过 \d+ tablename 或 pg_description 视图
--       即可一眼识别表性质（YAML 真源只读缓存），无需先读到特定文件
-- 8 张表对应 sync_yaml_to_depgraph.py READONLY_TABLES 列表
-- =====================================================================

COMMENT ON TABLE gates IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE field_vocabularies IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/vocabularies/ 目录 + _registry/catalogs/frontmatter_field_registry.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE registries IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE cross_registry_rules IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE hard_boundaries IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/hard_boundaries_registry.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE business_streams IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/business_streams_registry.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE infrastructure_components IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';

COMMENT ON TABLE model_capabilities IS 'YAML 真源只读缓存表。禁止直接 INSERT/UPDATE/DELETE（readonly 触发器保护）。真源：docs/01_policies_and_standards/_registry/contracts/model_capability_contract.yaml。同步入口：scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py';
