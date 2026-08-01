# [BLUEPRINT] SH-DB-003 | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] zephyr.governance.persistence.battlemap_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); psycopg2
# [CONSUMERS] apply_battle_map.py; battle_map_reader.py; align_battle_map.py; generate_trading_flow_diagram.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] battlemap shares PostgreSQL connection with depgraph (same DB, different tables); init_db must be idempotent; BM-INV-001~004
# [MODIFY-GUARD] depgraph_schema.py; battlemap generators
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on connection failure; OperationalError on DDL errors
# [TESTS] tests/test_battlemap_schema.py
# [TTL] permanent

"""
battlemap Schema DDL + 不变量声明
==================================
依据：battle_map_positioning.md V0.2（第四全景图 battlemap），作战地图与 depgraph 共享
PostgreSQL 实例（同一 DB，不同表）。PG 连接由 depgraph_schema.get_depgraph_pg_connection()
派生，本模块通过 get_battle_map_pg_connection() 委托，保证 PG 配置 SSoT。

物理路径：PostgreSQL（与 depgraph/decisiongraph 共享实例，连接串由 get_depgraph_pg_connection() 派生）
Safety  : M（DDL 定义，init_battle_map_db 幂等验证）

表结构（3 张表）
------
1. battle_map_steps    — 作战环节表（11列，环节定义+indicators JSONB 6件套）
2. battle_map_anchors  — 双向对齐关系表（7列，环节↔各图模块/候选/蓝图锚点）
3. battle_map_edges    — 环节流转表（6列，环节间 data_flow/trigger/degradation 边）

与 depgraph / decisiongraph 的关系
---------------------------------
- 复用同一个 PostgreSQL 实例（同一 DB，不同表前缀 battle_map_*）
- PG 连接配置 SSoT：config/.env.postgres（_PG_ENV_PATH 在 depgraph_schema 中定义）
- get_battle_map_pg_connection() 委托 get_depgraph_pg_connection()，无独立配置

design_maturity 受控词表（与 depgraph/decisiongraph 节点表对齐）
-------------------------------------------------------------
- design_maturity 2态：design / production [ARCH-MM-002 两档化]

四条承重墙不变量（BM-INV-001~004）
---------------------------------
- BM-INV-001: 每个作战环节至少有一个锚点（环节无锚点=悬空决策，君子协定告警）
- BM-INV-002: 锚点 target_id 必须能在 target_graph 对应图/仓库找到（防幽灵锚点）
- BM-INV-003: 环节叙事必须来自翻译真源 battle_map_steps 段，禁止生成器硬编码
- BM-INV-004: 全景图模块的 battle_map_step_ids 是派生只读缓存，禁止直接写入

PG schema 真源
--------------
  PG schema 真源：scripts/governance/migrate_sqlite_to_pg/08_create_battlemap_schema.sql
  init_battle_map_db() 仅验证 3 张核心表存在（SELECT 1 FROM each LIMIT 1），不执行 DDL/migration。

  _DDL_BATTLE_MAP_* 常量：列名对比真源（verify 脚本引用做 drift 校验），
  类型定义与 PG schema 真源对齐。本模块不执行 DDL，仅作为 Python 侧列名/类型对比真源。

pg_advisory_lock key
--------------------
  depgraph       = 424242
  dataflowgraph  = 424243
  decisiongraph  = 424244
  battlemap      = 424245  ← 本图使用

用法
----
    from zephyr.governance.persistence.battlemap_schema import (
        init_battle_map_db,
        get_battle_map_pg_connection,
    )

    init_battle_map_db()                          # 幂等，验证 3 张核心表存在
    conn = get_battle_map_pg_connection()         # 返回 PG 连接（与 depgraph 共享）
"""

from __future__ import annotations

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ---------------------------------------------------------------------------
# 受控词表（V0.2 先内联 CHECK，后续抽 battle_map_model.yaml 动态加载——VOCAB-HARDCODE 治本渐进路径）
# ---------------------------------------------------------------------------

# flow_stage 6值（与 decision_nodes.flow_stage 对齐）
_FLOW_STAGES = (
    "stock_selection",
    "buy_flow",
    "sell_flow",
    "position_management",
    "execution",
    "reconciliation",
)

# target_graph 5值（锚点指向的图/仓库）
_TARGET_GRAPHS = (
    "depgraph",
    "dataflowgraph",
    "decisiongraph",
    "candidate",
    "blueprint",
)

# target_role 3值（锚点在环节中的角色）
_TARGET_ROLES = ("primary", "supplement", "degradation")

# edge_type 3值（环节流转边类型）
_EDGE_TYPES = ("data_flow", "trigger", "degradation")

# design_maturity 2态（与 depgraph/decisiongraph 对齐）
_DESIGN_MATURITIES = ("design", "production")


# ---------------------------------------------------------------------------
# 公共 API — PG 连接（复用 depgraph 的 PG 实例）
# ---------------------------------------------------------------------------


def get_battle_map_pg_connection(*args, **kwargs):
    """返回 battlemap (PostgreSQL) 连接。

    battlemap 与 depgraph/decisiongraph 共享同一个 PostgreSQL 实例（同一 DB，不同表），
    本函数直接委托 get_depgraph_pg_connection()，保证 PG 配置 SSoT
    （config/.env.postgres）。

    所有位置参数透传给 get_depgraph_pg_connection()，详见其文档。

    :return: psycopg2 连接对象（autocommit=True 默认）
    """
    return get_depgraph_pg_connection(*args, **kwargs)


# ---------------------------------------------------------------------------
# DDL — battle_map_steps 表（作战环节，11列）
# step_id TEXT PK（格式 BM-<阶段缩写>-<序号>，如 BM-BUY-03）
# indicators JSONB — 6件套结构化数据（trigger/consumes/params/data_flow/code_mapping/degradation）
# narrative_ref TEXT — 指向翻译真源 battle_map_steps 段的 step_id（叙事真源在 YAML）
# ---------------------------------------------------------------------------

_DDL_BATTLE_MAP_STEPS = f"""
CREATE TABLE IF NOT EXISTS battle_map_steps (
    step_id          TEXT    PRIMARY KEY,
    step_name        TEXT    NOT NULL,
    flow_stage       TEXT    NOT NULL
        CHECK (flow_stage IN ({', '.join(f"'{s}'" for s in _FLOW_STAGES)})),
    layer            TEXT,
    sort_order       INTEGER NOT NULL DEFAULT 0,
    narrative_ref    TEXT,
    indicators       JSONB,
    source_ref       TEXT,
    design_maturity  TEXT    DEFAULT 'production'
        CHECK (design_maturity IN ({', '.join(f"'{m}'" for m in _DESIGN_MATURITIES)})),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
)
"""

# ---------------------------------------------------------------------------
# DDL — battle_map_anchors 表（双向对齐关系，7列）
# 双向查找真源：step_id ↔ target_graph + target_id
# BM-INV-001: 环节无锚点=悬空决策（君子协定，align_battle_map.py 告警）
# BM-INV-002: target_id 必须能在 target_graph 找到（应用层校验，防幽灵锚点）
# ---------------------------------------------------------------------------

_DDL_BATTLE_MAP_ANCHORS = f"""
CREATE TABLE IF NOT EXISTS battle_map_anchors (
    anchor_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    step_id          TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    target_graph     TEXT    NOT NULL
        CHECK (target_graph IN ({', '.join(f"'{g}'" for g in _TARGET_GRAPHS)})),
    target_id        TEXT    NOT NULL,
    target_role      TEXT    NOT NULL DEFAULT 'primary'
        CHECK (target_role IN ({', '.join(f"'{r}'" for r in _TARGET_ROLES)})),
    status_snapshot  TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (step_id, target_graph, target_id)
)
"""

# ---------------------------------------------------------------------------
# DDL — battle_map_edges 表（环节流转，6列）
# edge_type 3值：data_flow / trigger / degradation
# FK: from_step_id/to_step_id REFERENCES battle_map_steps(step_id)
# ---------------------------------------------------------------------------

_DDL_BATTLE_MAP_EDGES = f"""
CREATE TABLE IF NOT EXISTS battle_map_edges (
    edge_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_step_id     TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    to_step_id       TEXT    NOT NULL REFERENCES battle_map_steps(step_id) ON DELETE CASCADE,
    edge_type        TEXT    NOT NULL
        CHECK (edge_type IN ({', '.join(f"'{t}'" for t in _EDGE_TYPES)})),
    label            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    CHECK (from_step_id <> to_step_id)
)
"""

# ---------------------------------------------------------------------------
# DDL — 索引（6个，对齐 depgraph/decisiongraph 索引命名风格）
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_battle_map_steps_flow_stage ON battle_map_steps(flow_stage)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_steps_sort ON battle_map_steps(flow_stage, sort_order)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_step ON battle_map_anchors(step_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_target ON battle_map_anchors(target_graph, target_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_edges_from ON battle_map_edges(from_step_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_edges_to ON battle_map_edges(to_step_id)",
]


# ---------------------------------------------------------------------------
# 四条承重墙不变量（BM-INV-001~004）DB 约束说明
# 实际约束在 SQL 真源文件实现（_DDL_BATTLE_MAP_* 常量作为 Python 侧对比真源）
# ---------------------------------------------------------------------------
#
# BM-INV-001: 每个作战环节至少有一个锚点
#   约束位置: 应用层（align_battle_map.py 君子协定告警，非 DB 约束）
#   约束类型: 应用层校验（君子协定，跑顺后升级硬阻断）
#   说明: 环节无锚点=悬空决策=幻觉风险。align_battle_map.py 查询无锚点的 steps 并告警。
#
# BM-INV-002: 锚点 target_id 必须能在 target_graph 找到
#   约束位置: 应用层（apply_battle_map.py 写入时校验 + align_battle_map.py 批量校验）
#   约束类型: 应用层校验（跨表/跨 YAML 校验，DB 无法用 FK 表达）
#   说明: 防幽灵锚点——target_id 指向 depgraph/candidate/decisiongraph 等不存在的节点。
#         apply_battle_map.py 写入时查 target_graph 验证 target_id 存在。
#
# BM-INV-003: 环节叙事必须来自翻译真源 battle_map_steps 段
#   约束位置: 应用层（generate_trading_flow_diagram.py 只读翻译真源，禁止硬编码）
#   约束类型: 应用层规约（君子协定）
#   说明: 叙事真源是 module_translation_registry.yaml 的 battle_map_steps 段，
#         生成器禁止在代码里硬编码环节叙事。
#
# BM-INV-004: 全景图模块的 battle_map_step_ids 是派生只读缓存
#   约束位置: 应用层（apply_battle_map.py 单向 sync：anchors→各图字段，禁止反向写入）
#   约束类型: 应用层规约（君子协定）
#   说明: 全景图模块节点的 battle_map_step_ids 字段由 anchors 表派生，
#         真源在 anchors，禁止直接写入模块节点该字段（防漂移）。
# ---------------------------------------------------------------------------


def init_battle_map_db(*, echo: bool = False) -> None:
    """验证 battlemap (PostgreSQL) schema 健康性（幂等）。

    battlemap 与 depgraph/decisiongraph 共享 PG 实例，本函数仅验证 3 张核心表存在
    （battle_map_steps/battle_map_anchors/battle_map_edges），不执行 DDL/migration。

    若核心表不存在，请运行 battlemap 的 DDL 创建脚本：
        scripts/governance/migrate_sqlite_to_pg/08_create_battlemap_schema.sql

    :param echo: True 时打印验证结果
    :return: None
    """
    conn = get_battle_map_pg_connection()
    try:
        with conn.cursor() as cur:
            for table_name in (
                "battle_map_steps",
                "battle_map_anchors",
                "battle_map_edges",
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
                        f"battlemap (PostgreSQL) 表 {table_name} 未创建。"
                        "请运行 battlemap 的 DDL 创建脚本："
                        "scripts/governance/migrate_sqlite_to_pg/08_create_battlemap_schema.sql"
                    )
            if echo:
                # 幂等验证：SELECT 1 FROM each table LIMIT 1（不加载全表数据）
                for table_name in (
                    "battle_map_steps",
                    "battle_map_anchors",
                    "battle_map_edges",
                ):
                    cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1")  # noqa: S608
                    cur.fetchone()
                print("[battlemap_schema] PG schema healthy: 3 tables verified")
    finally:
        conn.close()


if __name__ == "__main__":
    # CLI 入口：python -m zephyr.governance.persistence.battlemap_schema
    # 幂等验证 battlemap 3 张核心表存在
    init_battle_map_db(echo=True)
