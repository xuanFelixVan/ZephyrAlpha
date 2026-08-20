# [BLUEPRINT] SH-DB-003 | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] zephyr.governance.persistence.battlemap_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); psycopg2
# [CONSUMERS] apply_battle_map.py; battle_map_reader.py; align_battle_map.py; generate_battle_map_diagram.py
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
1. battle_map_steps    — 作战环节表（13列，V0.4.0 新增 parent_step_id + depth 支持父子嵌套）
2. battle_map_anchors  — 双向对齐关系表（7列，环节↔各图模块/候选/蓝图锚点）
3. battle_map_edges    — 环节流转表（6列，环节间 data_flow/trigger/degradation 边）

与 depgraph / decisiongraph 的关系
---------------------------------
- 复用同一个 PostgreSQL 实例（同一 DB，不同表前缀 battle_map_*）
- PG 连接配置 SSoT：config/.env.postgres（_PG_ENV_PATH 在 depgraph_schema 中定义）
- get_battle_map_pg_connection() 委托 get_depgraph_pg_connection()，无独立配置

design_maturity 受控词表（与 depgraph/decisiongraph 节点表对齐）
-------------------------------------------------------------
- design_maturity 3态：design / production / deprecated [ARCH-MM-002 两档化]
  - design/production 与 depgraph/decisiongraph 对齐
  - deprecated（2026-08-11 新增，#ARCH-OE-007~009 治本）：环节 wontfix/裁剪裁定态。
    由 architecture_issue_registry.yaml 的 #ARCH-OE-007~009 decided 裁定驱动，生成器
    _compute_step_status 优先识别 step.design_maturity='deprecated' 直接生效（治理
    裁定权威，覆盖 depgraph 锚点推导），渲染红色 🟥 弃用态。

四条承重墙不变量（BM-INV-001~004）
---------------------------------
- BM-INV-001: 每个作战环节至少有一个锚点（环节无锚点=悬空决策，君子协定告警）
- BM-INV-002: 锚点 target_id 必须能在 target_graph 对应图/仓库找到（防幽灵锚点）
- BM-INV-003: 环节叙事必须来自翻译真源 battle_map_steps 段，禁止生成器硬编码
- BM-INV-005（未落地/规划中）: 全景图模块的 battle_map_step_ids 派生只读缓存——机制未建设，当前通过 anchors 反查（详见 §8.4）

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: PG 连接配置 环境配置
#   fields: config/.env.postgres 连接串（SSoT 在 depgraph_schema）
#   code: get_depgraph_pg_connection L83
# - id: I2
#   name: 受控词表常量 内置定义
#   fields: flow_stage 11值 + target_graph 5值 + target_role 3值 + edge_type 3值 + design_maturity 3态
#   code: _FLOW_STAGES L92 / _TARGET_GRAPHS L107 / _TARGET_ROLES L116 / _EDGE_TYPES L119 / _DESIGN_MATURITIES L123
# - id: I3
#   name: information_schema 元数据 PG系统表
#   fields: information_schema.tables 表存在性查询结果
#   code: information_schema.tables L292
# 层: 算法
# - id: A1
#   name_zh: ① PG 连接委托
#   name_en: get_battle_map_pg_connection
#   intro: battlemap 不自己管连接配置，直接委托 depgraph 的连接函数保证 SSoT
#   desc: 透传所有参数给 get_depgraph_pg_connection()，与 depgraph/decisiongraph 共享同一 PG 实例（同 DB 不同表）
#   inputs: I1
#   outputs: psycopg2 连接对象（autocommit=True）
#   invariant: PG 配置 SSoT，无独立配置
# - id: A2
#   name_zh: ② 三表 DDL 对比真源定义
#   name_en: _DDL_BATTLE_MAP_STEPS/ANCHORS/EDGES
#   intro: 用 DDL 常量声明作战环节/锚点/流转边三张表的列名与 CHECK 约束，只做 drift 对比不执行
#   desc: steps 13列（step_id PK + 父子嵌套 parent_step_id/depth）+ anchors 7列（UNIQUE step_id+target_graph+target_id）+ edges 6列（禁自环 CHECK）+ 7索引；CHECK 内联受控词表；真源 DDL 在 08_create_battlemap_schema.sql
#   inputs: I2
#   outputs: Python 侧列名/类型对比真源常量
#   invariant: 本模块不执行 DDL/migration
# - id: A3
#   name_zh: ③ schema 健康幂等验证
#   name_en: init_battle_map_db
#   intro: 启动时查三张核心表在不在，缺表就报错提示去跑 DDL 脚本
#   desc: information_schema.tables 逐表查存在性→缺表 raise RuntimeError（带 DDL 脚本路径）；echo=True 时每表 SELECT 1 LIMIT 1 轻量验证
#   inputs: A1 I3
#   outputs: 验证通过/RuntimeError
#   invariant: init_db 幂等
# 层: 输出
# - id: O1
#   name_zh: battlemap PG 连接
#   name_en: psycopg2 connection
#   intro: 给 battlemap 读写脚本用的共享 PG 连接
#   downstream: apply_battle_map.py; battle_map_reader.py; align_battle_map.py; generate_battle_map_diagram.py（[CONSUMERS]）
# - id: O2
#   name_zh: schema 验证结论与 DDL 对比真源
#   name_en: init_battle_map_db 结果 + _DDL 常量
#   intro: 三表健康验证结论，以及供 verify 脚本做 drift 校验的列名真源
#   invariant: BM-INV-001~006 承重墙不变量（应用层校验为主）
#   downstream: verify drift 校验脚本; tests/test_battlemap_schema.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# I3 --> A3
# A1 --> O1
# A2 --> O2
# A3 --> O2
"""

from __future__ import annotations

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ---------------------------------------------------------------------------
# 受控词表（V0.2 先内联 CHECK，后续抽 battle_map_model.yaml 动态加载——VOCAB-HARDCODE 治本渐进路径）
# ---------------------------------------------------------------------------

# flow_stage 11值（与 decision_nodes.flow_stage 对齐）
# 2026-08-03 全生命周期扩展：+5 新阶段（研究孵化/模型训练/回测验证/仿真验证/风控管控）
# 生命周期序：研究孵化→模型训练→回测验证→仿真验证→选股→买入→卖出→仓位→风控管控→执行→对账
_FLOW_STAGES = (
    "research_incubation",  # 研究孵化（D-RESEARCH）
    "model_training",  # 模型训练（D-ML-TRAIN）
    "backtest_validation",  # 回测验证（D-BACKTEST）
    "simulation_validation",  # 仿真验证（D-SIMULATION）
    "stock_selection",  # 选股
    "buy_flow",  # 买入
    "sell_flow",  # 卖出
    "position_management",  # 仓位
    "risk_control",  # 风控管控（D-RISK）
    "execution",  # 执行
    "reconciliation",  # 对账
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

# design_maturity 3态（与 depgraph/decisiongraph 对齐 + deprecated 治理裁定态）
# deprecated（2026-08-11，#ARCH-OE-007~009）：环节 wontfix/裁剪，生成器渲染红🟥弃用态
_DESIGN_MATURITIES = ("design", "production", "deprecated")  # noqa: gate-vocab  design_maturity 3态受控词表(含deprecated治理态),depgraph对齐


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
# DDL — battle_map_steps 表（作战环节，13列，V0.4.0 新增 parent_step_id + depth）
# step_id TEXT PK（格式 BM-<阶段缩写>-<序号>，如 BM-BUY-03）
# indicators JSONB — 6件套结构化数据（trigger/consumes/params/data_flow/code_mapping/degradation）
# narrative_ref TEXT — 指向翻译真源 battle_map_steps 段的 step_id（叙事真源在 YAML）
# parent_step_id TEXT — V0.4.0 父子嵌套：自引用 FK 指向父环节（NULL=顶层）
# depth INTEGER — V0.4.0 层级深度（0=顶层,1=子,2=孙，最大2，BM-INV-006）
# ---------------------------------------------------------------------------

_DDL_BATTLE_MAP_STEPS = f"""
CREATE TABLE IF NOT EXISTS battle_map_steps (
    step_id          TEXT    PRIMARY KEY,
    step_name        TEXT    NOT NULL,
    flow_stage       TEXT    NOT NULL
        CHECK (flow_stage IN ({", ".join(f"'{s}'" for s in _FLOW_STAGES)})),
    layer            TEXT,
    sort_order       INTEGER NOT NULL DEFAULT 0,
    narrative_ref    TEXT,
    indicators       JSONB,
    source_ref       TEXT,
    design_maturity  TEXT    DEFAULT 'production'
        CHECK (design_maturity IN ({", ".join(f"'{m}'" for m in _DESIGN_MATURITIES)})),
    parent_step_id   TEXT    REFERENCES battle_map_steps(step_id) ON DELETE SET NULL,
    depth            INTEGER NOT NULL DEFAULT 0,
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
        CHECK (target_graph IN ({", ".join(f"'{g}'" for g in _TARGET_GRAPHS)})),
    target_id        TEXT    NOT NULL,
    target_role      TEXT    NOT NULL DEFAULT 'primary'
        CHECK (target_role IN ({", ".join(f"'{r}'" for r in _TARGET_ROLES)})),
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
        CHECK (edge_type IN ({", ".join(f"'{t}'" for t in _EDGE_TYPES)})),
    label            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    CHECK (from_step_id <> to_step_id)
)
"""

# ---------------------------------------------------------------------------
# DDL — 索引（7个，V0.4.0 新增 parent_step_id 索引，对齐 depgraph/decisiongraph 命名风格）
# ---------------------------------------------------------------------------

_DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_battle_map_steps_flow_stage ON battle_map_steps(flow_stage)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_steps_sort ON battle_map_steps(flow_stage, sort_order)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_steps_parent ON battle_map_steps(parent_step_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_step ON battle_map_anchors(step_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_anchors_target ON battle_map_anchors(target_graph, target_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_edges_from ON battle_map_edges(from_step_id)",
    "CREATE INDEX IF NOT EXISTS idx_battle_map_edges_to ON battle_map_edges(to_step_id)",
]


# ---------------------------------------------------------------------------
# 四条承重墙不变量（BM-INV-001~006）DB 约束说明
# 实际约束在 SQL 真源文件实现（_DDL_BATTLE_MAP_* 常量作为 Python 侧对比真源）
# ---------------------------------------------------------------------------
#
# BM-INV-001: 每个作战环节至少有一个锚点
#   约束位置: 应用层（align_battle_map.py 君子协定告警，非 DB 约束）
#   约束类型: 应用层校验（君子协定，跑顺后升级硬阻断）
#   说明: 环节无锚点=悬空决策=幻觉风险。align_battle_map.py 查询无锚点的 steps 并告警。
#         子环节孤儿豁免：子环节可通过父环节间接获得锚点覆盖。
#
# BM-INV-002: 锚点 target_id 必须能在 target_graph 找到
#   约束位置: 应用层（apply_battle_map.py 写入时校验 + align_battle_map.py 批量校验）
#   约束类型: 应用层校验（跨表/跨 YAML 校验，DB 无法用 FK 表达）
#   说明: 防幽灵锚点——target_id 指向 depgraph/candidate/decisiongraph 等不存在的节点。
#         apply_battle_map.py 写入时查 target_graph 验证 target_id 存在。
#
# BM-INV-003: 环节叙事必须来自翻译真源 battle_map_steps 段
#   约束位置: 应用层（generate_battle_map_diagram.py 只读翻译真源，禁止硬编码）
#   约束类型: 应用层规约（君子协定）
#   说明: 叙事真源是 module_translation_registry.yaml 的 battle_map_steps 段，
#         生成器禁止在代码里硬编码环节叙事。
#
# BM-INV-005（未落地/规划中，2026-08-03 核实）: 全景图模块的 battle_map_step_ids 派生只读缓存
#   现状: 机制未建设——depgraph.nodes 无 battle_map_step_ids 列（information_schema 核实 0 列）、
#         apply_battle_map.py 无 sync 逻辑、align_battle_map.py 不检测、无 trigger。
#         原注释"apply_battle_map.py 单向 sync：anchors→各图字段"为虚假描述，已删除（方案B 降级）。
#   当前方案: 通过 battle_map_anchors 反查（target_graph=depgraph, target_id=blueprint_id），
#             idx_battle_map_anchors_target 索引支撑，无需派生缓存。详见 battle_map_positioning.md §8.4。
#   未来规划: 若出现高频 nodes→battle_map 环节查询性能需求，再评估建缓存+sync+检测。
#
# BM-INV-006: 作战地图父子嵌套一致性（V0.4.0）
#   约束位置: 应用层（align_battle_map.py _check_parent_child_consistency 君子协定告警）
#   约束类型: 应用层校验（君子协定，5 类检查：悬空父引用/跨阶段嵌套/成环/depth超限/depth不符）
#   说明: parent_step_id 自引用 FK + depth 字段支持环节父子嵌套（最大深度2）。
#         子环节 flow_stage 必须与父一致；父环节必须有子环节或自身有锚点；
#         depth 不能成环。生成器用 Mermaid subgraph 渲染父子关系。
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
