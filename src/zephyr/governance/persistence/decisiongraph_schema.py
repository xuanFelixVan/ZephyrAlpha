# [BLUEPRINT] SH-DB-002 | docs/03_modules/_cross_layer/database/blueprint.md | §decisiongraph
# [MODULE] zephyr.governance.persistence.decisiongraph_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.security.secrets (SecretsError, get_secret_from_file); psycopg2; zephyr.governance.depgraph_schema (复用 PG 连接)
# [CONSUMERS] apply_decisiongraph.py; extract_decisiongraph.py; generate_decision_graph.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] decisiongraph shares PostgreSQL connection with depgraph (same DB, different tables); init_db must be idempotent
# [MODIFY-GUARD] depgraph_schema.py; decisiongraph generators
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on connection failure; OperationalError on DDL errors
# [TESTS] tests/test_decisiongraph_schema.py
# [TTL] permanent

"""
decisiongraph Schema DDL + 不变量声明
========================================
依据：decisiongraph Phase 1 施工（裁定 TRAE-061），决策流图与 depgraph 共享 PostgreSQL
实例（同一 DB，不同表）。PG 连接由 depgraph_schema.get_depgraph_pg_connection() 派生，
本模块通过 get_decisiongraph_pg_connection() 委托，保证 PG 配置 SSoT（config/.env.postgres）。

物理路径：PostgreSQL（与 depgraph 共享实例，连接串由 get_depgraph_pg_connection() 派生）
Safety  : M（DDL 定义，init_decision_db 幂等验证）

表结构（4 张表）
------
1. decision_layers   — 决策层表（10列，层定义+生命周期）
2. decision_nodes     — 决策节点表（16列，决策定义+JSONB inputs/outputs/conditions/facets）
3. decision_edges     — 决策边表（9列，4种边类型 triggering/informing/constraining/approving）
4. decision_tracks    — 四轨表（6列，战略/战役/战术/操作四轨定义）

与 depgraph 的关系
-----------------
- 复用同一个 PostgreSQL 实例（同一 DB，不同表前缀 decision_*）
- PG 连接配置 SSoT：config/.env.postgres（_PG_ENV_PATH 在 depgraph_schema 中定义）
- get_decisiongraph_pg_connection() 委托 get_depgraph_pg_connection()，无独立配置

build_status / design_maturity 受控词表（与 depgraph 节点表对齐）
-------------------------------------------------------------
- build_status 5态：planned / generated / testing / stable / deprecated（单调推进）
- design_maturity 3态：design / production / prototype

五条承重墙不变量（DEC-INV-001~005）
---------------------------------
- DEC-INV-001: 决策节点必须有归属层（FK decision_layers.layer_id）
- DEC-INV-002: 决策边两端节点必须存在（FK decision_nodes.node_id）
- DEC-INV-003: 决策边类型受控（CHECK edge_type IN 4种合法值）
- DEC-INV-004: build_status 单调推进（CHECK + 应用层状态迁移校验）
- DEC-INV-005: design_maturity 3态受控（CHECK 3种合法值）

P2 迁移后 schema 真源（重要）
-----------------------------------
  PG schema 真源：scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql
  init_decision_db() 仅验证 4 张核心表存在（SELECT 1 FROM each LIMIT 1），不执行 DDL/migration。

  _DDL_DECISION_* 常量：列名对比真源（verify 脚本引用做 drift 校验），
  类型定义与 PG schema 真源对齐。本模块不执行 DDL，仅作为 Python 侧列名/类型对比真源。

用法
----
    from zephyr.governance.persistence.decisiongraph_schema import (
        init_decision_db,
        get_decisiongraph_pg_connection,
    )

    init_decision_db()                          # 幂等，验证 4 张核心表存在
    conn = get_decisiongraph_pg_connection()    # 返回 PG 连接（与 depgraph 共享）
"""

from __future__ import annotations

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


# ---------------------------------------------------------------------------
# 公共 API — PG 连接（复用 depgraph 的 PG 实例）
# ---------------------------------------------------------------------------


def get_decisiongraph_pg_connection(*args, **kwargs):
    """返回 decisiongraph (PostgreSQL) 连接。

    decisiongraph 与 depgraph 共享同一个 PostgreSQL 实例（同一 DB，不同表），
    本函数直接委托 get_depgraph_pg_connection()，保证 PG 配置 SSoT
    （config/.env.postgres）。

    所有参数透传给 get_depgraph_pg_connection()，详见其文档。

    :return: psycopg2 连接对象（autocommit=True 默认）
    """
    return get_depgraph_pg_connection(*args, **kwargs)


# ---------------------------------------------------------------------------
# DDL — decision_layers 表（决策层，10列）
# 列名对比真源：与 PG schema 真源对齐
# ---------------------------------------------------------------------------

_DDL_DECISION_LAYERS = """
CREATE TABLE IF NOT EXISTS decision_layers (
    layer_id            TEXT    PRIMARY KEY,
    layer_name          TEXT    NOT NULL,
    layer_name_en       TEXT    NOT NULL,
    track               TEXT    NOT NULL,
    description         TEXT,
    decision_frequency  TEXT,
    design_maturity     TEXT    DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status        TEXT    DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated'))
)
"""

# ---------------------------------------------------------------------------
# DDL — decision_nodes 表（决策节点，16列）
# JSONB 字段：inputs/outputs/conditions/facets
# FK: layer_id REFERENCES decision_layers(layer_id) — DEC-INV-001
# UNIQUE: path — 节点路径唯一
# ---------------------------------------------------------------------------

_DDL_DECISION_NODES = """
CREATE TABLE IF NOT EXISTS decision_nodes (
    node_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    layer_id         TEXT    NOT NULL REFERENCES decision_layers(layer_id),
    node_type        TEXT    NOT NULL,
    path             TEXT    NOT NULL UNIQUE,
    module_id        TEXT,
    decision_name    TEXT    NOT NULL,
    decision_name_en TEXT    NOT NULL,
    inputs           JSONB,
    outputs          JSONB,
    conditions       JSONB,
    facets           JSONB,
    evidence_hash    TEXT    NOT NULL,
    design_maturity  TEXT    DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status     TEXT    DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    finalized_at     TIMESTAMPTZ
)
"""

# ---------------------------------------------------------------------------
# DDL — decision_edges 表（决策边，9列）
# edge_type 4种合法值 — DEC-INV-003
# FK: from_node_id/to_node_id REFERENCES decision_nodes(node_id) — DEC-INV-002
# ---------------------------------------------------------------------------

_DDL_DECISION_EDGES = """
CREATE TABLE IF NOT EXISTS decision_edges (
    edge_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_node_id     BIGINT  NOT NULL REFERENCES decision_nodes(node_id),
    to_node_id       BIGINT  NOT NULL REFERENCES decision_nodes(node_id),
    edge_type        TEXT    NOT NULL
        CHECK (edge_type IN ('triggering', 'informing', 'constraining', 'approving')),
    edge_type_cn     TEXT,
    condition        TEXT,
    priority         INTEGER,
    track            TEXT,
    evidence_bundle  JSONB,
    valid_since      TIMESTAMPTZ DEFAULT NOW()
)
"""

# ---------------------------------------------------------------------------
# DDL — decision_tracks 表（四轨定义，6列）
# 四轨：战略 / 战役 / 战术 / 操作
# ---------------------------------------------------------------------------

_DDL_DECISION_TRACKS = """
CREATE TABLE IF NOT EXISTS decision_tracks (
    track_id              TEXT    PRIMARY KEY,
    track_name            TEXT    NOT NULL,
    track_name_en         TEXT    NOT NULL,
    description           TEXT,
    priority              INTEGER NOT NULL,
    activation_condition  TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — 索引（5个，对齐 depgraph 索引命名风格）
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_decision_nodes_layer ON decision_nodes(layer_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_decision_nodes_path ON decision_nodes(path)",
    "CREATE INDEX IF NOT EXISTS idx_decision_edges_from   ON decision_edges(from_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_decision_edges_to     ON decision_edges(to_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_decision_edges_type   ON decision_edges(edge_type)",
]


# ---------------------------------------------------------------------------
# 五条承重墙不变量（DEC-INV-001~005）DB 约束说明
# 实际约束在 SQL 真源文件实现（_DDL_DECISION_* 常量作为 Python 侧对比真源）
# ---------------------------------------------------------------------------
#
# DEC-INV-001: 决策节点必须有归属层
#   约束位置: decision_nodes.layer_id REFERENCES decision_layers(layer_id)
#   约束类型: DB FK
#   说明: 无孤儿决策节点，每个决策必须归属于某个决策层
#
# DEC-INV-002: 决策边两端节点必须存在
#   约束位置: decision_edges.from_node_id/to_node_id REFERENCES decision_nodes(node_id)
#   约束类型: DB FK
#   说明: 无悬空边，每个决策边的发起节点和目标节点都必须存在
#
# DEC-INV-003: 决策边类型受控
#   约束位置: decision_edges.edge_type CHECK IN ('triggering','informing','constraining','approving')
#   约束类型: DB CHECK
#   说明: 决策边只允许 4 种合法值，INSERT 非法值会被 psycopg2.IntegrityError 拒绝
#
# DEC-INV-004: build_status 单调推进
#   约束位置: decision_nodes.build_status CHECK IN ('planned','generated','testing','stable','deprecated')
#   约束类型: DB CHECK + 应用层状态迁移校验（apply_decisiongraph.py）
#   说明: 状态机为单调推进 planned→generated→testing→stable→deprecated，
#         禁止跳态（如 generated 直接跃迁到 stable 必须经过 testing）。
#         DB CHECK 保证值合法，状态迁移顺序由 apply_decisiongraph.py 应用层校验。
#
# DEC-INV-005: design_maturity 3态受控
#   约束位置: decision_nodes.design_maturity CHECK IN ('design','production','prototype')
#   约束类型: DB CHECK
#   说明: design_maturity 只允许 3 种合法值，与 depgraph 节点表语义对齐
# ---------------------------------------------------------------------------


def init_decision_db(*, echo: bool = False) -> None:
    """验证 decisiongraph (PostgreSQL) schema 健康性（幂等）。

    decisiongraph 与 depgraph 共享 PG 实例，本函数仅验证 4 张核心表存在
    （decision_layers/decision_nodes/decision_edges/decision_tracks），不执行 DDL/migration。

    若核心表不存在，请运行 decisiongraph 的 DDL 创建脚本：
        scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql

    :param echo: True 时打印验证结果
    :return: None
    """
    conn = get_decisiongraph_pg_connection()
    try:
        with conn.cursor() as cur:
            for table_name in (
                "decision_layers",
                "decision_nodes",
                "decision_edges",
                "decision_tracks",
            ):
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                    """,
                    (table_name,),
                )
                if cur.fetchone() is None:
                    raise RuntimeError(
                        f"decisiongraph (PostgreSQL) 表 {table_name} 未创建。"
                        "请运行 decisiongraph 的 DDL 创建脚本："
                        "scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql"
                    )
            if echo:
                # 幂等验证：SELECT 1 FROM each table LIMIT 1（不加载全表数据）
                for table_name in (
                    "decision_layers",
                    "decision_nodes",
                    "decision_edges",
                    "decision_tracks",
                ):
                    cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1")  # noqa: S608
                    cur.fetchone()
                print("[decisiongraph_schema] PG schema healthy: 4 tables verified")
    finally:
        conn.close()


if __name__ == "__main__":
    # CLI 入口：python -m zephyr.governance.persistence.decisiongraph_schema
    # 幂等验证 decisiongraph 4 张核心表存在
    init_decision_db(echo=True)
