# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §depgraph
# [MODULE] zephyr.governance.depgraph_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.security.secrets (SecretsError, get_secret_from_file); psycopg2
# [CONSUMERS] generate_project_depgraph.py; diagnose_depgraph.py; extract_depgraph.py; apply_depgraph.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] depgraph is PostgreSQL (连接串由 get_depgraph_pg_connection() 从环境变量派生); init_db must be idempotent
# [MODIFY-GUARD] sqlite_schema.py; database_manager.py; depgraph generators
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on migration failure; OperationalError on DDL errors
# [TESTS] tests/test_depgraph_schema.py
# [TTL] permanent

"""
depgraph Schema DDL + 版本化迁移框架
========================================
依据：数据库合并方案（9库->3库），depgraph 作为依赖图专用数据库（PostgreSQL）

物理路径：PostgreSQL depgraph（连接串由 get_depgraph_pg_connection() 从环境变量派生；P2迁移后，原 SQLite data/databases/depgraph.db 已删除归档）
Safety  : M（DDL 定义，init_db 幂等执行）

表结构
------
 1. nodes                 — 依赖图节点（28列，v3对齐模板受控词表）
 2. edges                 — 依赖图边（19列）
 3. domains               — 域定义（15列，v10清理装饰字段后）
 4. domain_dependencies   — 域间依赖（5列）
 5. domain_events         — 域事件（6列）
 6. contracts             — 域间契约（13列，v13扩展6列契约追踪字段）
 7. rule_bindings         — 规则绑定（6列）
 8. arch_constraints      — 架构约束（9列）
 9. arch_directory_tree   — 目录树（10列，v3新增build_status）
10. arch_path_mappings    — 路径映射（7列）
11. _schema_version       — Schema 版本追踪

v6变更: arch_domain_capacity + arch_domain_layers 已合并入 domains 表
        domains 表新增6字段: layer_id/growth_pattern/target_modules/feasibility/bottleneck_description/last_capacity_check
v9变更: domains 表新增 production_nodes 字段（ARCH-CAP-001 口径修复）
v10变更: domains 表清理7个无区分度装饰字段（can_build/gate_reason/hard_boundary_ref/growth_pattern/feasibility/bottleneck_description/last_capacity_check）
v14变更: 删除3张死表/漂移表（arch_bottlenecks/arch_layers/invariants）— fix #ARCH-013~015
v15变更: domains 表 domain_id 添加 CHECK 约束（裁定#ARCH-target_layer_v1.0.0）
        CHECK (domain_id ~ '^D_[A-Z][A-Z0-9_]*$') — 格式校验（与 DOMAIN_ID_RE 语义一致，允许数字如 D_INFRA_A2A），
        阻止连字符(D-DATA)/中文(基础设施)等废弃格式
        nodes.domain_id 已有 FK REFERENCES domains(domain_id)（02_create_pg_schema.sql L53）
        保留 cross_registry_rules（健康sync缓存）与 governance_audit_logs（auto_runner活跃写入）
v16变更: domains 表 build_status DEFAULT 'unbuilt' -> 'planned'（修复预存bug：
        'unbuilt' 不在 CHECK 允许值中，INSERT 不提供 build_status 时失败）
        _DDL_DOMAINS 补齐 lifecycle/build_status/layer_id 的 CHECK 约束（与 02_create_pg_schema.sql 对齐）

PRAGMA 基线（P2迁移后已废弃）
-----------------------------------
  PostgreSQL 不需要 PRAGMA 配置（由服务器 postgresql.conf 管理）。
  SQLite 时代的 PRAGMA 配置已删除。

P2 迁移后 schema 真源（重要）
-----------------------------------
  PG schema 真源：scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql
  init_db() 仅验证核心表存在，不执行 DDL/migration。

  _DDL_* 常量：列名对比真源（verify_schema_health.py 引用做 drift 校验），
  类型定义与 02_create_pg_schema.sql 真源对齐（6 个 IDENTITY 列均为
  BIGINT GENERATED ALWAYS AS IDENTITY，FK 列为 BIGINT）。
  _DDL_*_V5 常量：v5/v11 migration 历史 SQL 记录，_MIGRATIONS 列表元组元素，
  仅供版本号元数据引用，不执行。

用法
----
    from zephyr.governance.depgraph_schema import init_db, get_depgraph_pg_connection

    init_db()              # 幂等，验证 PG schema 健康性
    conn = get_depgraph_pg_connection()   # 返回 PostgreSQL 连接（psycopg2）

P2 迁移后路径真源（2026-06-27 治本）
-----------------------------------
  物理文件 data/databases/depgraph.db 已删除归档，逻辑库迁移至 PostgreSQL (连接串由 get_depgraph_pg_connection() 从环境变量派生)。
  禁止定义 DB_PATH = .../depgraph.db 常量（路径污染源）。
  PG 连接入口唯一真源：get_depgraph_pg_connection()（本模块定义）。
  PG 连接配置真源：config/.env.postgres（_PG_ENV_PATH）。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg2

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.security.secrets import SecretsError, get_secret_from_file  # §5.34.8 修复：DB密码走SecretProvider真源


# PostgreSQL 连接配置文件路径（P2迁移真源：MOD-DB_DEPGRAPH_PG）
_PG_ENV_PATH: Path = REPO_ROOT / "config" / ".env.postgres"

# 必需字段（§5.34.8 修复：统一走 get_secret_from_file，优先级 os.environ > 指定文件）
_PG_REQUIRED_KEYS: tuple[str, ...] = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


def _load_pg_config() -> dict[str, str]:
    """从 config/.env.postgres 加载 PostgreSQL 连接参数。

    §5.34.8 修复：改用 get_secret_from_file（SecretProvider 真源），
    优先级 os.environ > 指定文件 > 抛异常。
    必需字段：POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    """
    if not _PG_ENV_PATH.exists():
        raise FileNotFoundError(
            "PG 连接配置文件不存在\n"
            "请参考 P2迁移方案 §四 创建该文件（含 5 个必需字段）"
        )
    config: dict[str, str] = {}
    missing: list[str] = []
    for key in _PG_REQUIRED_KEYS:
        try:
            config[key] = get_secret_from_file(key, _PG_ENV_PATH)
        except SecretsError as e:
            if "not found in" in str(e):
                missing.append(key)
            else:
                raise
    if missing:
        raise ValueError(f"PG 连接配置缺少必需字段: {missing} (文件: {_PG_ENV_PATH})")
    return config


def _build_pg_dsn(config: dict[str, str] | None = None, *, superuser: bool = False) -> dict[str, Any]:
    """构建 psycopg2.connect() 的关键字参数。

    :param superuser: True 时使用 postgres 超级用户（用于数据迁移 / SET session_replication_role）
    :return: psycopg2.connect() 的 kwargs
    """
    if config is None:
        config = _load_pg_config()
    kwargs: dict[str, Any] = {
        "host": config["POSTGRES_HOST"],
        "port": config["POSTGRES_PORT"],
        "dbname": config["POSTGRES_DB"],
        "password": config["POSTGRES_PASSWORD"],
    }
    kwargs["user"] = "postgres" if superuser else config["POSTGRES_USER"]
    return kwargs

# ---------------------------------------------------------------------------
# DDL — nodes 表（31列，v11删除module_lifecycle_state+添加CHECK约束）
# P2迁移后类型与 02_create_pg_schema.sql 真源对齐：node_id 为 BIGINT IDENTITY
# ---------------------------------------------------------------------------

_DDL_NODES = """
CREATE TABLE IF NOT EXISTS nodes (
    node_id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    node_type                TEXT    NOT NULL,
    path                     TEXT    NOT NULL,
    granularity              TEXT    NOT NULL DEFAULT 'file',
    domain_id                TEXT,
    subdomain_id             TEXT,
    blueprint_id             TEXT,
    belongs_to               TEXT,
    owner                    TEXT,
    change_policy            TEXT    DEFAULT 'evolving',
    impact_level             TEXT    DEFAULT 'M',
    modification_permission  TEXT    DEFAULT 'ai_modifiable',
    file_header_score        INTEGER DEFAULT 0,
    tags                     TEXT,
    architecture_layer       TEXT,
    design_maturity          TEXT    DEFAULT 'production' CHECK(design_maturity IN ('design','production','prototype')),
    deployment_lifecycle     TEXT    DEFAULT 'stable',
    trust_zone               TEXT    DEFAULT 'trusted_core',
    license                  TEXT    DEFAULT 'Internal',
    drive_direction          TEXT    DEFAULT 'bottom_up',
    type_specific_data       TEXT,
    last_verified            TEXT,
    node_name                TEXT    DEFAULT '',
    file_path                TEXT    DEFAULT '',
    build_status             TEXT    DEFAULT 'generated' CHECK(build_status IN ('planned','generated','testing','stable','deprecated')),
    can_build                INTEGER DEFAULT 1,
    gate_reason              TEXT    NOT NULL DEFAULT '',
    hard_boundary_ref        TEXT,
    consumed_interfaces      TEXT,
    blueprint_id_invalid     INTEGER DEFAULT 0,
    blueprint_path           TEXT,
    entry_point              BOOLEAN DEFAULT FALSE,
    public_api               TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — edges 表
# P2迁移后类型与 02_create_pg_schema.sql 真源对齐：edge_id 为 BIGINT IDENTITY，FK 列为 BIGINT
# ---------------------------------------------------------------------------

_DDL_EDGES = """
CREATE TABLE IF NOT EXISTS edges (
    edge_id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_node_id             BIGINT  NOT NULL,
    to_node_id               BIGINT  NOT NULL,
    dep_type                 TEXT    NOT NULL,
    architecture_direction   TEXT    DEFAULT 'downstream',
    coupling_strength        TEXT    DEFAULT 'critical',
    used_symbol              TEXT,
    invocation_method        TEXT,
    api_contract_refs        TEXT,
    event_ref                TEXT,
    ddd_integration_pattern  TEXT,
    failure_mode             TEXT,
    fallback                 TEXT,
    activation_condition     TEXT,
    data_transfer_description TEXT,
    resource_impact          TEXT,
    relationship_type        TEXT    DEFAULT 'one_to_many',
    cross_domain             INTEGER DEFAULT 0,
    verified                 INTEGER DEFAULT 0,
    dep_maturity             TEXT DEFAULT 'active',
    is_legal_cycle           INTEGER DEFAULT 0,
    valid_since              TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — nodes_metadata 表（裁定#209 Stage 2：字段角色分离）
# 迁移 PRODUCTION_PROTECTED_FIELDS(14) 出 nodes 表——path 为稳定 PK
# （node_id 是 IDENTITY，DELETE+INSERT 后变化，不可作 FK）。
# nodes_metadata 在 write_depgraph_to_db 中 UPSERT（DELETE 前）保存当前值，
# INSERT 后 UPDATE nodes 从 metadata 恢复空字段（替代 P1/P2 Python 保护机制）。
# ---------------------------------------------------------------------------

_DDL_NODES_METADATA = """
CREATE TABLE IF NOT EXISTS nodes_metadata (
    path                     TEXT    PRIMARY KEY,
    blueprint_id            TEXT,
    owner                    TEXT,
    impact_level            TEXT,
    change_policy           TEXT,
    modification_permission TEXT,
    belongs_to              TEXT,
    build_status            TEXT,
    gate_reason              TEXT    NOT NULL DEFAULT '',
    hard_boundary_ref       TEXT,
    consumed_interfaces     TEXT,
    tags                     TEXT,
    trust_zone               TEXT,
    deployment_lifecycle     TEXT,
    architecture_layer       TEXT,
    last_updated             TEXT,
    module_name_cn           TEXT,
    module_name_en           TEXT,
    description_cn           TEXT,
    description_en           TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — edges_metadata 表（裁定#209 Stage 2：字段角色分离）
# 迁移 EDGES_PROTECTED_FIELDS(9) 出 edges 表——(from_path, to_path, dep_type)
# 为稳定复合 PK（edge_id 是 IDENTITY，node_id 在 DELETE+INSERT 后变化）。
# ---------------------------------------------------------------------------

_DDL_EDGES_METADATA = """
CREATE TABLE IF NOT EXISTS edges_metadata (
    from_path                TEXT    NOT NULL,
    to_path                  TEXT    NOT NULL,
    dep_type                 TEXT    NOT NULL DEFAULT '',
    failure_mode             TEXT,
    fallback                 TEXT,
    activation_condition     TEXT,
    data_transfer_description TEXT,
    resource_impact          TEXT,
    ddd_integration_pattern  TEXT,
    event_ref                TEXT,
    api_contract_refs        TEXT,
    verified                 INTEGER,
    last_updated             TEXT,
    PRIMARY KEY (from_path, to_path, dep_type)
)
"""

# ---------------------------------------------------------------------------
# DDL — domains 表
# ---------------------------------------------------------------------------

_DDL_DOMAINS = """
CREATE TABLE IF NOT EXISTS domains (
    domain_id        TEXT    PRIMARY KEY
        CHECK (domain_id ~ '^D_[A-Z][A-Z0-9_]*$'),
    domain_name      TEXT    NOT NULL,
    domain_group     TEXT    NOT NULL,
    description      TEXT,
    ssot_path        TEXT,
    current_modules  INTEGER DEFAULT 0,
    max_modules      INTEGER,
    lifecycle        TEXT    DEFAULT 'design_only'
        CHECK (lifecycle IN ('operational', 'design_only', 'prototype', 'deprecated')),
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL,
    build_status     TEXT    DEFAULT 'planned'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    modification_permission TEXT,
    layer_id         TEXT
        -- SSoT: docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml (documentation SSoT)
        -- Runtime SSoT: 本 DB trigger（SQL 静态约束，不能动态读 YAML）
        CHECK (layer_id IS NULL OR layer_id IN ('L0_infrastructure', 'L1_foundation', 'L2_domain', 'L3_application')), target_modules   INTEGER,
    production_nodes INTEGER DEFAULT 0
)
"""

# ---------------------------------------------------------------------------
# DDL — domain_dependencies 表
# ---------------------------------------------------------------------------

_DDL_DOMAIN_DEPS = """
CREATE TABLE IF NOT EXISTS domain_dependencies (
    from_domain      TEXT    NOT NULL,
    to_domain        TEXT    NOT NULL,
    edge_count       INTEGER DEFAULT 0,
    edge_types       TEXT,
    constraint_type  TEXT,
    PRIMARY KEY (from_domain, to_domain)
)
"""

# ---------------------------------------------------------------------------
# DDL — domain_events 表
# ---------------------------------------------------------------------------

_DDL_DOMAIN_EVENTS = """
CREATE TABLE IF NOT EXISTS domain_events (
    event_id         TEXT    PRIMARY KEY,
    name             TEXT    NOT NULL,
    source_domain    TEXT    NOT NULL,
    target_domains   TEXT,
    payload_schema   TEXT,
    priority         TEXT    DEFAULT 'P1',
    event_type       TEXT    NOT NULL DEFAULT 'domain_event'
)
"""

# ---------------------------------------------------------------------------
# DDL — contracts 表
# ---------------------------------------------------------------------------

_DDL_CONTRACTS = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id        TEXT    PRIMARY KEY,
    name               TEXT    NOT NULL,
    provider_domain    TEXT    NOT NULL,
    consumer_domain    TEXT    NOT NULL,
    contract_type      TEXT    NOT NULL,
    schema_definition  TEXT,
    version            TEXT,
    promise            TEXT,
    actual_consumer    TEXT,
    fulfillment_status TEXT,
    gap                TEXT,
    target_phase       TEXT,
    last_reviewed      TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — rule_bindings 表
# ---------------------------------------------------------------------------

_DDL_RULE_BINDINGS = """
-- 5.18.2/5.18.3 治本决策（2026-07-01）：rule_id 是 TEXT（YAML 文件名 stem），
-- 由 rule_engine.py 通过 YAML 文件存在性校验，非 node 引用，故不设 FK。
CREATE TABLE IF NOT EXISTS rule_bindings (
    binding_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    function_name    TEXT    NOT NULL,
    rule_id          TEXT    NOT NULL,
    binding_type     TEXT    NOT NULL,
    trigger_type     TEXT    NOT NULL,
    trigger_id       TEXT,
    domain_id        TEXT    NOT NULL DEFAULT ''
)
"""

# ---------------------------------------------------------------------------
# DDL — arch_* 表
# ---------------------------------------------------------------------------

_DDL_ARCH_CONSTRAINTS = """
CREATE TABLE IF NOT EXISTS arch_constraints (
    constraint_id    TEXT    PRIMARY KEY,
    name             TEXT    NOT NULL,
    constraint_type  TEXT    NOT NULL,
    from_domain      TEXT,
    to_domain        TEXT,
    rule_definition  TEXT    NOT NULL,
    severity         TEXT    DEFAULT 'hard',
    enforcement      TEXT    DEFAULT 'gate',
    description      TEXT,
    details          TEXT,
    detected_at      TEXT,
    violation_status TEXT    DEFAULT 'open'
)
"""

_DDL_ARCH_DIRECTORY_TREE = """
-- 5.18.9 治本（2026-07-02）：补 FK 到 domains（683 孤儿已清理）
CREATE TABLE IF NOT EXISTS arch_directory_tree (
    path             TEXT    PRIMARY KEY,
    parent_path      TEXT,
    path_type        TEXT    NOT NULL,
    domain_id        TEXT    REFERENCES domains(domain_id),
    blueprint_id     TEXT,
    change_policy    TEXT,
    modification_permission TEXT,
    build_status     TEXT    DEFAULT 'unbuilt',
    design_maturity  TEXT    NOT NULL DEFAULT 'design',
    last_scanned     TEXT
)
"""

_DDL_ARCH_PATH_MAPPINGS = """
CREATE TABLE IF NOT EXISTS arch_path_mappings (
    mapping_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    domain_id        TEXT    NOT NULL,
    path_pattern     TEXT    NOT NULL,
    path_type        TEXT    NOT NULL,
    state            TEXT    NOT NULL DEFAULT 'design',
    covers           TEXT,
    aliases          TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — _schema_version 表
# ---------------------------------------------------------------------------

_DDL_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS _schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT    NOT NULL,
    description TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — 索引
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_nodes_domain       ON nodes(domain_id)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_type         ON nodes(node_type)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_blueprint    ON nodes(blueprint_id)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_change_policy ON nodes(change_policy)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_build_status ON nodes(build_status)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_can_build    ON nodes(can_build)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_path         ON nodes(path)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_file_path    ON nodes(file_path)",
    "CREATE INDEX IF NOT EXISTS idx_edges_from         ON edges(from_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_edges_to           ON edges(to_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_edges_type         ON edges(dep_type)",
    "CREATE INDEX IF NOT EXISTS idx_edges_cross_domain ON edges(cross_domain)",
    "CREATE INDEX IF NOT EXISTS idx_domains_group      ON domains(domain_group)",
    "CREATE INDEX IF NOT EXISTS idx_domdeps_from       ON domain_dependencies(from_domain)",
    "CREATE INDEX IF NOT EXISTS idx_domdeps_to         ON domain_dependencies(to_domain)",
    "CREATE INDEX IF NOT EXISTS idx_arch_dir_domain    ON arch_directory_tree(domain_id)",
    "CREATE INDEX IF NOT EXISTS idx_arch_dir_build     ON arch_directory_tree(build_status)",
    "CREATE INDEX IF NOT EXISTS idx_arch_path_domain   ON arch_path_mappings(domain_id)",
    # 裁定#209 Stage 2：metadata 表索引
    "CREATE INDEX IF NOT EXISTS idx_nodes_metadata_bp     ON nodes_metadata(blueprint_id)",
    "CREATE INDEX IF NOT EXISTS idx_edges_metadata_from   ON edges_metadata(from_path)",
    "CREATE INDEX IF NOT EXISTS idx_edges_metadata_to      ON edges_metadata(to_path)",
]

# ---------------------------------------------------------------------------
# PRAGMA 配置（P2迁移后已删除：PostgreSQL 不需要 PRAGMA，由服务器配置管理）
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DDL — v5 重建表（node_id INTEGER PK + edges FK + arch_directory_tree node_id）
# ---------------------------------------------------------------------------

_DDL_NODES_V5 = """
CREATE TABLE IF NOT EXISTS nodes (
    node_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    node_type                TEXT,
    path                     TEXT,
    granularity              TEXT,
    domain_id                TEXT,
    subdomain_id             TEXT,
    blueprint_id             TEXT,
    belongs_to               TEXT,
    owner                    TEXT,
    change_policy            TEXT,
    impact_level             TEXT,
    modification_permission  TEXT,
    file_header_score        INTEGER DEFAULT 0,
    tags                     TEXT,
    architecture_layer       TEXT,
    design_maturity          TEXT DEFAULT 'production' CHECK(design_maturity IN ('design','production','prototype')),
    deployment_lifecycle     TEXT DEFAULT 'stable',
    trust_zone               TEXT DEFAULT 'trusted_core',
    license                  TEXT DEFAULT 'Internal',
    drive_direction          TEXT DEFAULT 'bottom_up',
    type_specific_data       TEXT,
    last_verified            TEXT,
    node_name                TEXT DEFAULT '',
    file_path                TEXT DEFAULT '',
    build_status             TEXT DEFAULT 'generated' CHECK(build_status IN ('planned','generated','testing','stable','deprecated')),
    can_build                INTEGER DEFAULT 1,
    gate_reason               TEXT DEFAULT '',
    hard_boundary_ref        TEXT,
    consumed_interfaces      TEXT,
    implementation_ref       TEXT,
    has_dynamic_import       INTEGER DEFAULT 0,
    blueprint_id_invalid     INTEGER DEFAULT 0,
    in_degree                INTEGER DEFAULT 0,
    out_degree               INTEGER DEFAULT 0,
    blueprint_path           TEXT,
    business_stream          TEXT,
    stream_role              TEXT,
    runtime_plane            TEXT,
    ddd_aggregate            TEXT,
    provided_interfaces      TEXT
)
"""

_DDL_EDGES_V5 = """
CREATE TABLE IF NOT EXISTS edges (
    edge_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id             INTEGER NOT NULL,
    to_node_id               INTEGER NOT NULL,
    dep_type                 TEXT,
    architecture_direction   TEXT,
    coupling_strength        TEXT,
    used_symbol              TEXT,
    invocation_method        TEXT,
    api_contract_refs        TEXT,
    event_ref                TEXT,
    ddd_integration_pattern  TEXT,
    failure_mode             TEXT,
    fallback                 TEXT,
    activation_condition     TEXT,
    data_transfer_description TEXT,
    resource_impact          TEXT,
    relationship_type        TEXT,
    cross_domain             INTEGER DEFAULT 0,
    verified                 INTEGER DEFAULT 0,
    dep_maturity             TEXT DEFAULT 'active',
    valid_since              TEXT,
    migration_status         TEXT DEFAULT 'active',
    is_legal_cycle           INTEGER DEFAULT 0,
    FOREIGN KEY (from_node_id) REFERENCES nodes(node_id),
    FOREIGN KEY (to_node_id) REFERENCES nodes(node_id)
)
"""

_DDL_ARCH_DIR_TREE_V5 = """
CREATE TABLE IF NOT EXISTS arch_directory_tree (
    path                     TEXT PRIMARY KEY,
    parent_path              TEXT,
    path_type                TEXT,
    domain_id                TEXT,
    node_id                  INTEGER,
    blueprint_id             TEXT,
    change_policy            TEXT,
    modification_permission  TEXT,
    last_scanned             TEXT,
    build_status             TEXT,
    design_maturity          TEXT,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
)
"""

# ---------------------------------------------------------------------------
# DDL — v7 新增表（gates + governance_audit_logs）
# ---------------------------------------------------------------------------

_DDL_GATES = """
CREATE TABLE IF NOT EXISTS gates (
    gate_id        TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    entry          TEXT NOT NULL,
    description    TEXT,
    files_trigger  TEXT,
    always_run     INTEGER DEFAULT 0,
    category       TEXT NOT NULL,
    status         TEXT DEFAULT 'active',
    source         TEXT DEFAULT '.pre-commit-config.yaml',
    event_driven   TEXT DEFAULT '',
    auto_start     INTEGER DEFAULT 1,
    CHECK (status IN ('active', 'deprecated', 'disabled'))
)
"""

_DDL_GOVERNANCE_AUDIT_LOGS = """
CREATE TABLE IF NOT EXISTS governance_audit_logs (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    timestamp     TEXT NOT NULL,
    total_gates   INTEGER DEFAULT 0,
    passed_gates  INTEGER DEFAULT 0,
    failed_gates  INTEGER DEFAULT 0,
    skipped_gates INTEGER DEFAULT 0,
    success       INTEGER DEFAULT 0,
    errors        TEXT DEFAULT ''
)
"""

# ---------------------------------------------------------------------------
# DDL — v8 只读保护表 + domain_mapping（schema 盲区修复）
# ---------------------------------------------------------------------------

_DDL_BLUEPRINT_LINKS = """
CREATE TABLE IF NOT EXISTS blueprint_links (
    blueprint_id       TEXT PRIMARY KEY,
    blueprint_path     TEXT NOT NULL,
    alignment_verified INTEGER DEFAULT 0,
    last_verified      TEXT
)
"""

_DDL_BUSINESS_STREAMS = """
CREATE TABLE IF NOT EXISTS business_streams (
    stream_id      TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    goal           TEXT,
    input          TEXT,
    output         TEXT,
    runtime_plane  TEXT,
    CHECK (runtime_plane IN ('data_plane', 'control_plane', 'management_plane'))
)
"""

_DDL_CROSS_REGISTRY_RULES = """
CREATE TABLE IF NOT EXISTS cross_registry_rules (
    rule_id          TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    fields           TEXT,
    ssot             TEXT NOT NULL,
    consistency      TEXT,
    violation_action TEXT,
    CHECK (consistency IN ('exact', 'derived', 'independent')),
    CHECK (violation_action IN ('block', 'warn', 'log'))
)
"""

_DDL_FIELD_VOCABULARIES = """
CREATE TABLE IF NOT EXISTS field_vocabularies (
    field_name     TEXT NOT NULL,
    value          TEXT NOT NULL,
    definition     TEXT,
    ai_consumption TEXT,
    source_yaml    TEXT,
    PRIMARY KEY (field_name, value)
)
"""

_DDL_HARD_BOUNDARIES = """
CREATE TABLE IF NOT EXISTS hard_boundaries (
    boundary_id    TEXT PRIMARY KEY,
    category       TEXT NOT NULL,
    constraint_def TEXT NOT NULL,
    parameters     TEXT,
    impact         TEXT,
    CHECK (category IN ('architectural', 'domain', 'data', 'security', 'operational'))
)
"""

_DDL_INFRASTRUCTURE_COMPONENTS = """
CREATE TABLE IF NOT EXISTS infrastructure_components (
    component_id    TEXT PRIMARY KEY,
    component_type  TEXT NOT NULL,
    address         TEXT,
    health_check    TEXT,
    dependencies    TEXT,
    sla             TEXT,
    status          TEXT DEFAULT 'active',
    CHECK (component_type IN ('event_bus', 'message_queue', 'relational_db',
                               'vector_db', 'cache', 'object_storage',
                               'config_center', 'service_registry', 'ci_pipeline'))
)
"""

_DDL_MODEL_CAPABILITIES = """
CREATE TABLE IF NOT EXISTS model_capabilities (
    model_name              TEXT PRIMARY KEY,
    tier                    TEXT NOT NULL,
    max_files_per_session   INTEGER,
    allowed_paths           TEXT,
    forbidden_paths         TEXT,
    recommended_tasks       TEXT,
    forbidden_tasks         TEXT,
    CHECK (tier IN ('premium', 'standard', 'free', 'api'))
)
"""

_DDL_REGISTRIES = """
CREATE TABLE IF NOT EXISTS registries (
    registry_id    TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    title          TEXT,
    path           TEXT NOT NULL,
    version        TEXT,
    description    TEXT,
    ssot_for       TEXT
)
"""

_DDL_DOMAIN_MAPPING = """
CREATE TABLE IF NOT EXISTS domain_mapping (
    mapping_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    path_prefix  TEXT NOT NULL,
    domain_id    TEXT NOT NULL,
    subdomain_id TEXT,
    mapping_type TEXT NOT NULL,
    mapped_at    TEXT NOT NULL,
    mapped_by    TEXT NOT NULL,
    note         TEXT
)
"""

# ---------------------------------------------------------------------------
# 版本化迁移框架（P2迁移后：历史 SQLite 迁移记录，不再执行）
# PG schema 真源：scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql
# 本列表保留以支持 check_schema_version_writes.py / verify_schema_health.py 引用版本号元数据
# ---------------------------------------------------------------------------

_MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (
        1,
        "Initial schema - 15 tables",
        [
            _DDL_NODES,
            _DDL_EDGES,
            _DDL_DOMAINS,
            _DDL_DOMAIN_DEPS,
            _DDL_DOMAIN_EVENTS,
            _DDL_CONTRACTS,
            _DDL_RULE_BINDINGS,
            _DDL_ARCH_CONSTRAINTS,
            _DDL_ARCH_DIRECTORY_TREE,
            _DDL_ARCH_PATH_MAPPINGS,
            *_DDL_INDEXES,
        ],
    ),
    (
        2,
        "DM-100101: Add 7 fields to nodes table (node_name, file_path, stability, safety_level, ai_autonomy, design_state, runtime_state)",
        [
            "ALTER TABLE nodes ADD COLUMN node_name TEXT DEFAULT ''",
            "ALTER TABLE nodes ADD COLUMN file_path TEXT DEFAULT ''",
            "ALTER TABLE nodes ADD COLUMN stability TEXT DEFAULT 'evolving'",
            "ALTER TABLE nodes ADD COLUMN safety_level TEXT DEFAULT 'M'",
            "ALTER TABLE nodes ADD COLUMN ai_autonomy TEXT DEFAULT 'ai_modifiable'",
            "ALTER TABLE nodes ADD COLUMN design_state TEXT DEFAULT 'draft'",
            "ALTER TABLE nodes ADD COLUMN runtime_state TEXT DEFAULT 'inactive'",
            "CREATE INDEX IF NOT EXISTS idx_nodes_stability    ON nodes(stability)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_design_state ON nodes(design_state)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_file_path    ON nodes(file_path)",
        ],
    ),
    (
        3,
        "v3: Align nodes/domains/arch_directory_tree with TPL-DEPGRAPH-001 v6 template. Merge duplicate fields (stability->change_policy, safety_level->impact_level, ai_autonomy->modification_permission). Rename design_state->build_status, runtime_state->module_lifecycle_state. Add can_build/gate_reason/hard_boundary_ref/consumed_interfaces to nodes. Add build_status/can_build/gate_reason/hard_boundary_ref to domains. Add build_status to arch_directory_tree, rename stability->change_policy, ai_autonomy->modification_permission.",
        [
            # --- nodes: merge data from old columns to standard columns ---
            "UPDATE nodes SET change_policy = COALESCE(NULLIF(change_policy,''), NULLIF(stability,'')) WHERE stability IS NOT NULL AND stability != ''",
            "UPDATE nodes SET impact_level = COALESCE(NULLIF(impact_level,''), NULLIF(safety_level,'')) WHERE safety_level IS NOT NULL AND safety_level != ''",
            "UPDATE nodes SET modification_permission = COALESCE(NULLIF(modification_permission,''), NULLIF(ai_autonomy,'')) WHERE ai_autonomy IS NOT NULL AND ai_autonomy != ''",
            # --- nodes: rename design_state -> build_status ---
            "ALTER TABLE nodes RENAME COLUMN design_state TO build_status",
            # Migrate build_status values: draft->unbuilt, active->built, inactive->unbuilt
            "UPDATE nodes SET build_status = 'unbuilt' WHERE build_status = 'draft' OR build_status = 'inactive'",
            "UPDATE nodes SET build_status = 'built' WHERE build_status = 'active'",
            # --- nodes: rename runtime_state -> module_lifecycle_state ---
            "ALTER TABLE nodes RENAME COLUMN runtime_state TO module_lifecycle_state",
            # Migrate module_lifecycle_state values: inactive->planned, active->active, deprecated->deprecated
            "UPDATE nodes SET module_lifecycle_state = 'planned' WHERE module_lifecycle_state = 'inactive'",
            # --- nodes: add new fields ---
            "ALTER TABLE nodes ADD COLUMN can_build INTEGER DEFAULT 1",
            "ALTER TABLE nodes ADD COLUMN gate_reason TEXT",
            "ALTER TABLE nodes ADD COLUMN hard_boundary_ref TEXT",
            "ALTER TABLE nodes ADD COLUMN consumed_interfaces TEXT",
            # --- nodes: drop old indexes first (must drop before DROP COLUMN) ---
            "DROP INDEX IF EXISTS idx_nodes_stability",
            "DROP INDEX IF EXISTS idx_nodes_design_state",
            # --- nodes: drop old duplicate columns ---
            "ALTER TABLE nodes DROP COLUMN stability",
            "ALTER TABLE nodes DROP COLUMN safety_level",
            "ALTER TABLE nodes DROP COLUMN ai_autonomy",
            # --- nodes: new indexes ---
            "CREATE INDEX IF NOT EXISTS idx_nodes_change_policy ON nodes(change_policy)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_build_status ON nodes(build_status)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_can_build ON nodes(can_build)",
            # --- domains: add 4 fields ---
            "ALTER TABLE domains ADD COLUMN build_status TEXT DEFAULT 'unbuilt'",
            "ALTER TABLE domains ADD COLUMN can_build INTEGER DEFAULT 1",
            "ALTER TABLE domains ADD COLUMN gate_reason TEXT",
            "ALTER TABLE domains ADD COLUMN hard_boundary_ref TEXT",
            "CREATE INDEX IF NOT EXISTS idx_domains_can_build ON domains(can_build)",
            # --- arch_directory_tree: rename stability->change_policy, ai_autonomy->modification_permission ---
            "ALTER TABLE arch_directory_tree RENAME COLUMN stability TO change_policy",
            "ALTER TABLE arch_directory_tree RENAME COLUMN ai_autonomy TO modification_permission",
            # --- arch_directory_tree: add build_status ---
            "ALTER TABLE arch_directory_tree ADD COLUMN build_status TEXT DEFAULT 'unbuilt'",
            "CREATE INDEX IF NOT EXISTS idx_arch_dir_build ON arch_directory_tree(build_status)",
        ],
    ),
    (
        4,
        "T0-001~T0-004 schema fixes: Add event_type to domain_events, domain_id to rule_bindings, design_maturity to arch_directory_tree, UNIQUE index on nodes(path)",
        [
            "ALTER TABLE domain_events ADD COLUMN event_type TEXT NOT NULL DEFAULT 'domain_event'",
            "ALTER TABLE rule_bindings ADD COLUMN domain_id TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE arch_directory_tree ADD COLUMN design_maturity TEXT NOT NULL DEFAULT 'design'",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_path ON nodes(path)",
        ],
    ),
    (
        5,
        "v5: node_id INTEGER PK + edges from_node_id/to_node_id FK + dep_maturity + arch_directory_tree node_id + nodes 5 new fields",
        [
            # 重建 nodes 表（node_id TEXT -> INTEGER PK AUTOINCREMENT）
            "DROP TABLE IF EXISTS edges",
            "DROP TABLE IF EXISTS nodes",
            "DROP TABLE IF EXISTS arch_directory_tree",
            _DDL_NODES_V5,
            _DDL_EDGES_V5,
            _DDL_ARCH_DIR_TREE_V5,
            # 重建索引
            *_DDL_INDEXES,
        ],
    ),
    (
        6,
        "v6: domains 吸收 arch_domain_capacity + arch_domain_layers（6新字段）",
        [
            "ALTER TABLE domains ADD COLUMN layer_id TEXT",
            "ALTER TABLE domains ADD COLUMN growth_pattern TEXT DEFAULT 'linear'",
            "ALTER TABLE domains ADD COLUMN target_modules INTEGER",
            "ALTER TABLE domains ADD COLUMN feasibility TEXT DEFAULT 'feasible'",
            "ALTER TABLE domains ADD COLUMN bottleneck_description TEXT",
            "ALTER TABLE domains ADD COLUMN last_capacity_check TEXT",
            "DROP TABLE IF EXISTS arch_domain_capacity",
            "DROP TABLE IF EXISTS arch_domain_layers",
        ],
    ),
    (
        7,
        "v7: gates 表加 event_driven 和 auto_start 列 + 创建 governance_audit_logs 表",
        [
            _DDL_GATES,
            _DDL_GOVERNANCE_AUDIT_LOGS,
        ],
    ),
    (
        8,
        "v8: CREATE 9 readonly tables + domain_mapping（schema 盲区修复）",
        [
            _DDL_BLUEPRINT_LINKS,
            _DDL_BUSINESS_STREAMS,
            _DDL_CROSS_REGISTRY_RULES,
            _DDL_FIELD_VOCABULARIES,
            _DDL_HARD_BOUNDARIES,
            _DDL_INFRASTRUCTURE_COMPONENTS,
            _DDL_MODEL_CAPABILITIES,
            _DDL_REGISTRIES,
            _DDL_DOMAIN_MAPPING,
        ],
    ),
    (
        9,
        "v9: Add production_nodes column to domains（ARCH-CAP-001 口径修复）",
        [
            "ALTER TABLE domains ADD COLUMN production_nodes INTEGER DEFAULT 0",
        ],
    ),
    (
        10,
        "v10: Drop 7 decorative fields from domains（无区分度/无值字段清理）",
        [
            "DROP INDEX IF EXISTS idx_domains_can_build",
            "ALTER TABLE domains DROP COLUMN can_build",
            "ALTER TABLE domains DROP COLUMN gate_reason",
            "ALTER TABLE domains DROP COLUMN hard_boundary_ref",
            "ALTER TABLE domains DROP COLUMN growth_pattern",
            "ALTER TABLE domains DROP COLUMN feasibility",
            "ALTER TABLE domains DROP COLUMN bottleneck_description",
            "ALTER TABLE domains DROP COLUMN last_capacity_check",
        ],
    ),
    (
        11,
        "v11: Add CHECK constraints to nodes (build_status 5 values, design_maturity 3 values) + archive module_lifecycle_state column (裁定#178-183)",
        [
            # 1. 创建归档表（保存module_lifecycle_state数据）
            """CREATE TABLE IF NOT EXISTS nodes_archive_module_lifecycle (
                node_id              INTEGER,
                module_lifecycle_state TEXT,
                archived_at         TEXT    NOT NULL
            )""",
            # 2. 复制module_lifecycle_state数据到归档表
            "INSERT INTO nodes_archive_module_lifecycle (node_id, module_lifecycle_state, archived_at) SELECT node_id, module_lifecycle_state, datetime('now') FROM nodes WHERE module_lifecycle_state IS NOT NULL",
            # 3. 删除依赖nodes表的视图（重建nodes表前必须先删除视图）
            "DROP VIEW IF EXISTS dep_cycles",
            # 4. 创建新nodes表（带CHECK约束，无module_lifecycle_state列）
            _DDL_NODES_V5.replace("CREATE TABLE IF NOT EXISTS nodes", "CREATE TABLE nodes_new"),
            # 5. 从旧表复制数据到新表（排除module_lifecycle_state列）
            """INSERT INTO nodes_new (
                node_id, node_type, path, granularity, domain_id, subdomain_id, blueprint_id, belongs_to, owner,
                change_policy, impact_level, modification_permission, file_header_score, tags, architecture_layer,
                design_maturity, deployment_lifecycle, trust_zone, license, drive_direction, type_specific_data,
                last_verified, node_name, file_path, build_status, can_build, gate_reason, hard_boundary_ref,
                consumed_interfaces, implementation_ref, has_dynamic_import, blueprint_id_invalid, in_degree,
                out_degree, blueprint_path, business_stream, stream_role, runtime_plane, ddd_aggregate, provided_interfaces
            )
            SELECT
                node_id, node_type, path, granularity, domain_id, subdomain_id, blueprint_id, belongs_to, owner,
                change_policy, impact_level, modification_permission, file_header_score, tags, architecture_layer,
                design_maturity, deployment_lifecycle, trust_zone, license, drive_direction, type_specific_data,
                last_verified, node_name, file_path, build_status, can_build, gate_reason, hard_boundary_ref,
                consumed_interfaces, implementation_ref, has_dynamic_import, blueprint_id_invalid, in_degree,
                out_degree, blueprint_path, business_stream, stream_role, runtime_plane, ddd_aggregate, provided_interfaces
            FROM nodes""",
            # 6. 删除旧nodes表（FK已禁用，不会触发edges/arch_directory_tree的FK检查）
            "DROP TABLE nodes",
            # 7. 重命名新表为nodes（SQLite会自动更新edges/arch_directory_tree的FK引用）
            "ALTER TABLE nodes_new RENAME TO nodes",
            # 8. 重建索引（path使用非UNIQUE索引，v19 migration会清理重复值并升级为UNIQUE）
            *[
                stmt.replace("CREATE UNIQUE INDEX", "CREATE INDEX") if "idx_nodes_path" in stmt else stmt
                for stmt in _DDL_INDEXES
            ],
            # 9. 重建dep_cycles视图
            """CREATE VIEW IF NOT EXISTS dep_cycles AS
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
        ORDER BY n.domain_id, n.node_id""",
        ],
    ),
    (
        12,
        "v12: Add CHECK triggers to domains (lifecycle 4值, build_status 5值, layer_id 4值) + nodes DELETE cleanup trigger (裁定#203-B/#203-C, ARCH-006/007)",
        [
            # 1. nodes表DELETE触发器：删除节点时自动清理edges（防止孤儿边再产生，根因：FK无ON DELETE CASCADE）
            """CREATE TRIGGER IF NOT EXISTS trg_nodes_delete_cleanup_edges
            AFTER DELETE ON nodes
            BEGIN
                DELETE FROM edges WHERE from_node_id = OLD.node_id OR to_node_id = OLD.node_id;
            END""",
            # 2. domains lifecycle校验 (INSERT)
            """CREATE TRIGGER IF NOT EXISTS chk_domains_lifecycle_insert
            BEFORE INSERT ON domains
            WHEN NEW.lifecycle NOT IN ('operational', 'design_only', 'prototype', 'deprecated')
            BEGIN
                SELECT RAISE(ABORT, 'domains.lifecycle illegal value (legal: operational/design_only/prototype/deprecated)');
            END""",
            # 3. domains lifecycle校验 (UPDATE)
            """CREATE TRIGGER IF NOT EXISTS chk_domains_lifecycle_update
            BEFORE UPDATE OF lifecycle ON domains
            WHEN NEW.lifecycle NOT IN ('operational', 'design_only', 'prototype', 'deprecated')
            BEGIN
                SELECT RAISE(ABORT, 'domains.lifecycle illegal value (legal: operational/design_only/prototype/deprecated)');
            END""",
            # 4. domains build_status校验 (INSERT)
            """CREATE TRIGGER IF NOT EXISTS chk_domains_build_status_insert
            BEFORE INSERT ON domains
            WHEN NEW.build_status NOT IN ('planned', 'generated', 'testing', 'stable', 'deprecated')
            BEGIN
                SELECT RAISE(ABORT, 'domains.build_status illegal value (legal: planned/generated/testing/stable/deprecated)');
            END""",
            # 5. domains build_status校验 (UPDATE)
            """CREATE TRIGGER IF NOT EXISTS chk_domains_build_status_update
            BEFORE UPDATE OF build_status ON domains
            WHEN NEW.build_status NOT IN ('planned', 'generated', 'testing', 'stable', 'deprecated')
            BEGIN
                SELECT RAISE(ABORT, 'domains.build_status illegal value (legal: planned/generated/testing/stable/deprecated)');
            END""",
            # 6. domains layer_id校验 (INSERT，允许NULL)
            # SSoT: layer_vocabulary.yaml — 4值需与词表保持一致
            """CREATE TRIGGER IF NOT EXISTS chk_domains_layer_id_insert
            BEFORE INSERT ON domains
            WHEN NEW.layer_id IS NOT NULL AND NEW.layer_id NOT IN ('L0_infrastructure', 'L1_foundation', 'L2_domain', 'L3_application')
            BEGIN
                SELECT RAISE(ABORT, 'domains.layer_id illegal value (legal: L0_infrastructure/L1_foundation/L2_domain/L3_application/NULL)');
            END""",
            # 7. domains layer_id校验 (UPDATE，允许NULL)
            """CREATE TRIGGER IF NOT EXISTS chk_domains_layer_id_update
            BEFORE UPDATE OF layer_id ON domains
            WHEN NEW.layer_id IS NOT NULL AND NEW.layer_id NOT IN ('L0_infrastructure', 'L1_foundation', 'L2_domain', 'L3_application')
            BEGIN
                SELECT RAISE(ABORT, 'domains.layer_id illegal value (legal: L0_infrastructure/L1_foundation/L2_domain/L3_application/NULL)');
            END""",
        ],
    ),
    (
        13,
        "v13: Add 6 extension columns to contracts (promise/actual_consumer/fulfillment_status/gap/target_phase/last_reviewed) — fix #ARCH-008 schema drift",
        [
            "ALTER TABLE contracts ADD COLUMN promise TEXT",
            "ALTER TABLE contracts ADD COLUMN actual_consumer TEXT",
            "ALTER TABLE contracts ADD COLUMN fulfillment_status TEXT",
            "ALTER TABLE contracts ADD COLUMN gap TEXT",
            "ALTER TABLE contracts ADD COLUMN target_phase TEXT",
            "ALTER TABLE contracts ADD COLUMN last_reviewed TEXT",
        ],
    ),
    (
        14,
        "v14: Drop 3 dead/drifted tables (arch_bottlenecks/arch_layers/invariants) — fix #ARCH-013~015. "
        "KEEP cross_registry_rules (healthy sync) and governance_audit_logs (auto_runner active writer).",
        [
            "DROP TABLE IF EXISTS arch_bottlenecks",
            "DROP TABLE IF EXISTS arch_layers",
            "DROP TABLE IF EXISTS invariants",
        ],
    ),
    (
        15,
        "v15: Drop 11 dead/drifted columns + rebuild arch_directory_tree (remove node_id FK) — fix #ARCH-016 schema drift. "
        "nodes: 9 columns (in/out_degree改动态计算; business_stream/stream_role/runtime_plane/ddd_aggregate/"
        "has_dynamic_import/implementation_ref/provided_interfaces无业务读写). "
        "edges: migration_status (无业务读写). "
        "arch_directory_tree: 重建表删node_id列+FK约束 (state列已在v5删除).",
        [
            # nodes: 9 dead/latent columns (无业务读写或仅JSON key; in/out_degree改动态COUNT计算)
            "ALTER TABLE nodes DROP COLUMN in_degree",
            "ALTER TABLE nodes DROP COLUMN out_degree",
            "ALTER TABLE nodes DROP COLUMN business_stream",
            "ALTER TABLE nodes DROP COLUMN stream_role",
            "ALTER TABLE nodes DROP COLUMN runtime_plane",
            "ALTER TABLE nodes DROP COLUMN ddd_aggregate",
            "ALTER TABLE nodes DROP COLUMN has_dynamic_import",
            "ALTER TABLE nodes DROP COLUMN implementation_ref",
            "ALTER TABLE nodes DROP COLUMN provided_interfaces",
            # edges: 1 dead column (仅V5 DDL+migration复制, 无业务读写)
            # 先DROP orphan索引+触发器 (源码中不存在, 仅DB实例中有), 否则DROP COLUMN会失败或trigger变悬空
            "DROP INDEX IF EXISTS idx_edges_migration",
            "DROP TRIGGER IF EXISTS chk_edges_migration_status",
            "DROP TRIGGER IF EXISTS chk_edges_migration_status_update",
            "ALTER TABLE edges DROP COLUMN migration_status",
            # arch_directory_tree: 重建表 (删node_id列+FK约束; state列已在v5删除, 此处仅对齐v1 DDL)
            # 用重建表模式因node_id有FK约束, ALTER DROP COLUMN对有FK的列可能受限
            _DDL_ARCH_DIRECTORY_TREE.replace(
                "CREATE TABLE IF NOT EXISTS arch_directory_tree",
                "CREATE TABLE arch_directory_tree_new",
            ),
            "INSERT INTO arch_directory_tree_new "
            "(path, parent_path, path_type, domain_id, blueprint_id, change_policy, "
            "modification_permission, build_status, design_maturity, last_scanned) "
            "SELECT path, parent_path, path_type, domain_id, blueprint_id, change_policy, "
            "modification_permission, build_status, design_maturity, last_scanned "
            "FROM arch_directory_tree",
            "DROP TABLE arch_directory_tree",
            "ALTER TABLE arch_directory_tree_new RENAME TO arch_directory_tree",
            # 重建索引 (DROP TABLE已删除arch_directory_tree的索引, 需重建)
            *_DDL_INDEXES,
        ],
    ),
    (
        16,
        "v16: Drop surviving orphan trigger chk_edges_design_immutable_update — fix #ARCH-016 残留. "
        "源码中不存在(MOD-DB_DEPGRAPH_PG裁定: 3个chk_前缀orphan trigger仅DB实例中有), v15已清2个, 此为第3个. "
        "该trigger引用dep_maturity(live列,不broken)但从未触发(全代码库无UPDATE edges SET dep_maturity).",
        [
            "DROP TRIGGER IF EXISTS chk_edges_design_immutable_update",
        ],
    ),
    (
        17,
        "v17: Drop stale index idx_domains_can_build — _DDL_INDEXES cleanup (fix #ARCH-016 残留). "
        "domains.can_build 列在 v10 已删除, 但 _DDL_INDEXES 中 idx_domains_can_build 声明未清理. "
        "init_db 执行时因 'no such column' 被 _run_migration benign 跳过, DB 中实际不存在此索引. "
        "清理 _DDL_INDEXES 声明 + DROP INDEX IF EXISTS 确保生产库与声明一致.",
        [
            "DROP INDEX IF EXISTS idx_domains_can_build",
        ],
    ),
    (
        18,
        "v18: Add blueprint_id format CHECK triggers to nodes (裁定#208 双轨制+历史兼容 DB 层防护). "
        "应用层 V1(apply_depgraph L359 禁止 --update-module 改 blueprint_id) + V2(L2135 --rename-blueprint-id 格式校验) "
        "可被直接 SQL 绕过. 本 migration 在 DB 层添加 BEFORE INSERT + BEFORE UPDATE OF blueprint_id 触发器, "
        "用 GLOB 粗校验 MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER* 前缀(纯 SQL 无依赖), 应用层 is_valid_module_id() 做精细正则校验. "
        "治本 2026-07-02: 扩展 SYS- 前缀为 SYS-MASTER-001 等系统级蓝图开路. "
        "分层防御: DB 层阻断 gross violation(如 WRONG-FORMAT), app 层拦截 subtle violation(如 MOD-lowercase). "
        "特殊情况处理: NULL(无蓝图)/空串(无蓝图)/blueprint_id_invalid=1(遗留失效 ID) 均放行. "
        "未保护 arch_directory_tree/blueprint_links: 前者 sync_directory_registry UPSERT 会触发 UPDATE 校验阻断 "
        "(2 个遗留无效 ID: DOC-ROOT/CAT-IDX-001), 后者 sync_blueprint_links 做 DELETE+INSERT FROM nodes 会触发 INSERT 校验阻断 "
        "(716 个遗留无效 ID). nodes 是 blueprint_id 真源, 保护 nodes 即间接保护派生表.",
        [
            # 1. nodes BEFORE INSERT: 粗校验 blueprint_id 前缀
            # GLOB 大小写敏感(双轨制+历史兼容要求大写), 纯 SQL 无需扩展
            # 放行: NULL / 空串 / blueprint_id_invalid=1 / MOD-* / D-* / SH-* / SYS-* / PLACEHOLDER*
            # R2 治本修订(2026-07-05): D-* 保留接受——用于 submodule_id 引用 + 历史 blueprint_id 数据;
            # module_id 合法性校验由应用层 is_valid_module_id() 负责(R2 后 D-XXX-NNN 作 module_id 触发 N-06 阻断)
            """CREATE TRIGGER IF NOT EXISTS chk_nodes_blueprint_id_insert
            BEFORE INSERT ON nodes
            WHEN NEW.blueprint_id IS NOT NULL
              AND NEW.blueprint_id != ''
              AND NEW.blueprint_id_invalid = 0
              AND NEW.blueprint_id NOT GLOB 'MOD-*'
              AND NEW.blueprint_id NOT GLOB 'D-*'
              AND NEW.blueprint_id NOT GLOB 'SH-*'
              AND NEW.blueprint_id NOT GLOB 'SYS-*'
              AND NEW.blueprint_id NOT GLOB 'PLACEHOLDER*'
            BEGIN
                SELECT RAISE(ABORT, 'nodes.blueprint_id format violation (裁定#208 双轨制+历史兼容: MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*, or set blueprint_id_invalid=1 for legacy)');
            END""",
            # 2. nodes BEFORE UPDATE OF blueprint_id: 粗校验 blueprint_id 前缀
            # 仅当 blueprint_id 列出现在 SET 子句时触发, 不影响其他列的 UPDATE
            """CREATE TRIGGER IF NOT EXISTS chk_nodes_blueprint_id_update
            BEFORE UPDATE OF blueprint_id ON nodes
            WHEN NEW.blueprint_id IS NOT NULL
              AND NEW.blueprint_id != ''
              AND NEW.blueprint_id_invalid = 0
              AND NEW.blueprint_id NOT GLOB 'MOD-*'
              AND NEW.blueprint_id NOT GLOB 'D-*'
              AND NEW.blueprint_id NOT GLOB 'SH-*'
              AND NEW.blueprint_id NOT GLOB 'SYS-*'
              AND NEW.blueprint_id NOT GLOB 'PLACEHOLDER*'
            BEGIN
                SELECT RAISE(ABORT, 'nodes.blueprint_id format violation (裁定#208 双轨制+历史兼容: MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*, or set blueprint_id_invalid=1 for legacy)');
            END""",
        ],
    ),
    (
        19,
        "v19: 清理 nodes.path 重复值 + 升级 idx_nodes_path 为 UNIQUE（5.4.3 修复）",
        [
            # 1. 创建临时映射表: old_node_id -> canonical_node_id (MIN per path)
            """CREATE TEMP TABLE IF NOT EXISTS _node_dedup_map AS
            SELECT n1.node_id AS old_id, MIN(n2.node_id) AS new_id
            FROM nodes n1
            JOIN nodes n2 ON n1.path = n2.path
            WHERE n1.node_id > n2.node_id
            GROUP BY n1.node_id""",
            # 2. 更新 edges.from_node_id 指向 canonical node
            """UPDATE edges SET from_node_id = (SELECT new_id FROM _node_dedup_map WHERE old_id = edges.from_node_id)
            WHERE from_node_id IN (SELECT old_id FROM _node_dedup_map)""",
            # 3. 更新 edges.to_node_id 指向 canonical node
            """UPDATE edges SET to_node_id = (SELECT new_id FROM _node_dedup_map WHERE old_id = edges.to_node_id)
            WHERE to_node_id IN (SELECT old_id FROM _node_dedup_map)""",
            # 4. 删除重复 nodes（保留每个 path 的 MIN node_id）
            "DELETE FROM nodes WHERE node_id NOT IN (SELECT MIN(node_id) FROM nodes GROUP BY path)",
            # 5. 清理临时表
            "DROP TABLE IF EXISTS _node_dedup_map",
            # 6. 删除旧的非UNIQUE索引，创建UNIQUE索引
            "DROP INDEX IF EXISTS idx_nodes_path",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_path ON nodes(path)",
        ],
    ),
]


def _get_current_version(conn: Any) -> int:
    """获取 PG schema 版本。

    P2迁移后：PG schema 由 02_create_pg_schema.sql 创建，_schema_version 表已填充。
    返回值含义：
        -1: nodes 表存在但 _schema_version 表不存在（旧 PG，需重新建 schema）
        0: 两者都不存在
        >0: 当前 schema 版本号
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = '_schema_version'
        """)
        if cur.fetchone() is None:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'nodes'
            """)
            if cur.fetchone() is not None:
                return -1
            return 0
        cur.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
        row = cur.fetchone()
        return row[0] if row else 0


def _run_migration(
    conn: Any,
    version: int,
    description: str,
    statements: list[str],
) -> None:
    """执行单个迁移版本（PG模式：保留作为参考，init_db 中不再调用）。

    P2迁移后：PG schema 由 02_create_pg_schema.sql 一次性创建，_MIGRATIONS 不再执行。
    此函数保留以支持 check_schema_version_writes.py 引用 _MIGRATIONS 数据。
    """
    from datetime import UTC, datetime

    now = datetime.now(UTC).isoformat()
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            with conn.cursor() as cur:
                cur.execute(stmt)
        except psycopg2.Error as exc:
            msg = str(exc).lower()
            benign = (
                "already exists",
                "duplicate column",
                "no such column",
            )
            if any(p in msg for p in benign):
                continue
            raise RuntimeError(f"Migration v{version} statement #{i} failed: {exc}") from exc  # 5.99.1 修复: 移除SQL文本泄露,仅保留版本/语句编号/原始异常
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO _schema_version (version, applied_at, description) VALUES (%s, %s, %s) "
            "ON CONFLICT (version) DO NOTHING",
            (version, now, description),
        )


def init_db(
    db_path: Path | str | None = None,  # 保留参数向后兼容（PG模式下忽略）
    *,
    echo: bool = False,
) -> None:
    """验证 depgraph (PostgreSQL) schema 健康性（幂等）。

    P2迁移后：PG schema 由 scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql 创建。
    本函数不再执行 DDL/migration，仅验证核心表存在。

    若核心表不存在，请运行:
        psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql

    :return: None（PG 模式下无文件路径返回）
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'nodes'
            """)
            if cur.fetchone() is None:
                raise RuntimeError(
                    "depgraph (PostgreSQL) schema 未创建。请运行:\n"
                    "  psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql"
                )
            if echo:
                cur.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
                )
                count = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
                ver = cur.fetchone()[0]
                print(f"[depgraph_schema] PG schema healthy: {count} tables, version=v{ver}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------


def get_depgraph_pg_connection(
    db_path: Path | str | None = None,  # 保留参数向后兼容（PG模式下忽略）
    *,
    superuser: bool = False,
    autocommit: bool = True,
    replica: bool = False,
    # 以下参数保留向后兼容但 PG 模式下无效（避免调用方修改）
    check_same_thread: bool = False,  # SQLite-only，PG 忽略
    timeout: float = 30.0,  # SQLite-only，PG 忽略
    apply_foreign_keys: bool = True,  # SQLite-only，PG 忽略（FK 由 schema DDL 管理）
) -> psycopg2.extensions.connection:
    """返回 depgraph (PostgreSQL) 连接。

    所有 depgraph 连接必须经此入口（统一 PG 配置，防止散点连接绕过连接池配置）。

    :param superuser: True 使用 postgres 超级用户（用于数据迁移 / SET session_replication_role）
    :param autocommit: True 启用自动提交（默认）；False 需显式 conn.commit()
    :param replica: True 设置 session_replication_role='replica' 禁用所有触发器和 FK
        （仅超级用户可用；用于批量数据导入/迁移场景；自动设置 superuser=True）

    注意：以下 SQLite 时代参数保留向后兼容但 PG 模式下无效：
        - db_path, check_same_thread, timeout, apply_foreign_keys
    """
    if replica:
        superuser = True  # session_replication_role 需要超级用户

    conn = psycopg2.connect(**_build_pg_dsn(superuser=superuser))
    conn.autocommit = autocommit

    if replica:
        with conn.cursor() as cur:
            cur.execute("SET session_replication_role = 'replica';")
        if not autocommit:
            conn.commit()

    return conn


# DEPRECATED: get_db_connection 已改名为 get_depgraph_pg_connection（消除与 SQLite 同名冲突）。
# 保留别名向后兼容，新代码必须用 get_depgraph_pg_connection。见 AGENTS.md §11.4。
get_db_connection = get_depgraph_pg_connection


def table_names(db_path: Path | str | None = None) -> list[str]:
    """返回 depgraph (PostgreSQL) 中所有 public schema 表名。"""
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def schema_version(db_path: Path | str | None = None) -> int:
    """返回当前 depgraph (PostgreSQL) 的 schema 版本。"""
    conn = get_depgraph_pg_connection()
    try:
        return _get_current_version(conn)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 5.18.12 治本：PG 迁移框架恢复（轻量级，不依赖 alembic）
# ---------------------------------------------------------------------------

_PG_SCHEMA_SQL_PATH: Path = REPO_ROOT / "scripts" / "governance" / "migrate_sqlite_to_pg" / "02_create_pg_schema.sql"


def apply_pg_schema(*, version: int | None = None, description: str = "") -> None:
    """从 02_create_pg_schema.sql 执行 DDL（幂等，CREATE IF NOT EXISTS）。

    5.18.12 治本（2026-07-02）：恢复 PG schema 版本化迁移能力。
    PG schema 真源为 02_create_pg_schema.sql，本函数提供可重复执行的入口，
    避免手动 psql -f 操作无版本追踪的问题。

    :param version: 迁移版本号（写入 _schema_version 表）；None 时不登记
    :param description: 迁移描述（写入 _schema_version 表）
    """
    if not _PG_SCHEMA_SQL_PATH.exists():
        raise FileNotFoundError(f"PG schema 真源文件不存在: {_PG_SCHEMA_SQL_PATH}")

    sql_text = _PG_SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        if version is not None:
            from datetime import UTC, datetime
            now = datetime.now(UTC).isoformat()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO _schema_version (version, applied_at, description) "
                    "VALUES (%s, %s, %s) ON CONFLICT (version) DO NOTHING",
                    (version, now, description or f"apply_pg_schema v{version}"),
                )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 5.18.13 治本：迁移前备份（downgrade 替代方案）
# ---------------------------------------------------------------------------

def backup_before_migration(backup_path: Path | str) -> Path:
    """在应用破坏性 migration 前备份 PG depgraph（pg_dump）。

    5.18.13 治本（2026-07-02）：为 PG migration 提供 downgrade 能力。
    SQLite migration 的 downgrade 策略是"建备份表->重建->恢复"（见 v19/v31）；
    PG migration 的 downgrade 策略是"pg_dump 备份->pg_restore 恢复"。

    :param backup_path: 备份文件路径（.dump 格式）
    :return: 备份文件 Path
    """
    import subprocess

    config = _load_pg_config()
    backup_file = Path(backup_path)
    backup_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pg_dump",
        "-h", config["POSTGRES_HOST"],
        "-p", config["POSTGRES_PORT"],
        "-U", config["POSTGRES_USER"],
        "-d", config["POSTGRES_DB"],
        "-F", "c",  # custom format for pg_restore
        "-f", str(backup_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PGPASSWORD": config["POSTGRES_PASSWORD"]})
    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr}")
    return backup_file


def restore_from_backup(backup_path: Path | str) -> None:
    """从 pg_dump 备份恢复 PG depgraph（downgrade 执行入口）。

    :param backup_path: 备份文件路径（.dump 格式，由 backup_before_migration 创建）
    """
    import subprocess

    config = _load_pg_config()
    backup_file = Path(backup_path)
    if not backup_file.exists():
        raise FileNotFoundError(f"备份文件不存在: {backup_file}")

    cmd = [
        "pg_restore",
        "-h", config["POSTGRES_HOST"],
        "-p", config["POSTGRES_PORT"],
        "-U", config["POSTGRES_USER"],
        "-d", config["POSTGRES_DB"],
        "--clean",  # 先 DROP 再 CREATE
        "--if-exists",
        str(backup_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PGPASSWORD": config["POSTGRES_PASSWORD"]})
    if result.returncode != 0:
        raise RuntimeError(f"pg_restore failed: {result.stderr}")


__all__ = [
    "get_depgraph_pg_connection",
    "get_db_connection",  # DEPRECATED 别名，向后兼容
    "init_db",
    "schema_version",
    "table_names",
    "apply_pg_schema",  # 5.18.12: PG 迁移框架
    "backup_before_migration",  # 5.18.13: 迁移前备份
    "restore_from_backup",  # 5.18.13: 从备份恢复（downgrade）
]


if __name__ == "__main__":
    import sys

    init_db(echo=True)
    tables = table_names()
    ver = schema_version()
    print(f"\n  depgraph (PostgreSQL) schema verified")
    print(f"  Schema version: v{ver}")
    print(f"  Tables ({len(tables)}): {', '.join(tables)}")
    sys.exit(0)
