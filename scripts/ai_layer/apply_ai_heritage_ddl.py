# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] scripts.ai_layer.apply_ai_heritage_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] CLI python scripts/ai_layer/apply_ai_heritage_ddl.py [--schema ai_heritage] [--verify];
#             tests/ai_layer/heritage/test_heritage_ddl.py（临时 schema 部署）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL-as-Code: ai_heritage 四表五视图 DDL 真源即本文件（设计真源=docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.3）;
#              全部幂等(CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS + CREATE OR REPLACE VIEW); 时间戳一律 TIMESTAMPTZ(RULE-SCHEMA-TZ 同义执行);
#              生熟分界再分内外：ai_intake=生食库/ai_heritage=自家经验库，schema 级隔离独立演进(DESIGN §2.2 ④);
#              零物理删除语义：本件无 DROP TABLE/DROP COLUMN，唯 DROP TEST SCHEMA 限 ai_heritage_test_ 前缀(DESIGN §2.8 删除红线);
#              CHECK 值域与 DESIGN §2.3/§2.5 一致：entry_kind 三类/source_kind 八通道/status 四态/surface 五族/
#              venue 五考场/机制族 8 族(词表锚=L2 apply_ai_intake_ddl MECHANISM_FAMILIES 同值);
#              schema 名必须匹配 ^ai_heritage(_test_[a-z0-9_]+)?$（fail-closed, 防 DDL/DROP 打偏）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.3（改表结构先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->打印错误+退出码 2; schema 名不合规->ValueError 立即拒跑(不静默改名);
#                  DDL 语句失败->回滚+非零退出; --verify 缺件->退出码 3 并列出缺失清单
# [TESTS] tests/ai_layer/heritage/test_heritage_ddl.py（幂等两次零错/CHECK 值域/临时 schema 部署清理）
# [TTL] permanent
"""AI 层 L7 传承段——传承库 DDL 部署器（PostgreSQL depgraph 同实例，schema `ai_heritage`）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.3（四表五视图，三类条目统一登记）。
照 ``scripts/ai_layer/apply_ai_intake_ddl.py`` 模式实现（幂等 + 角色分级 GRANT + 白名单 schema）。

表/视图清单::

    ai_heritage_entry        H1 条目主表（三类共用——消费统计/查重指纹/遗忘状态跨类单点）
    ai_heritage_elite        H2 精英档案扩展表（胜者+判据+差异；1:1 FK entry_id）
    ai_heritage_criteria     H3 判据档案扩展表（"当时为什么算它赢"）
    ai_heritage_defect       H4 缺陷模式扩展表（主文档 §三 3.5 三字段：根因/签名/配方）
    ai_heritage_elites_active V1 active 精英（surface×family，L2 组合素材/L5 祖先分支查询口）
    ai_heritage_defect_hot   V2 active 缺陷模式（T4 快照源+派工签名匹配源）
    ai_heritage_l1_prior     V3 domain×family 格先验（prior_factor∈[1.0,2.0]+rationale_refs）
    ai_heritage_l1_exclusion V4 active 缺陷排除词表展开（L1 keyword_groups 直接读）
    ai_heritage_kpi          V5 月度 KPI（新增/命中/降级+覆盖率/prior 冻结态）

规则参数（阈值/保留期）不落 DDL，真源=``config/heritage_policy.yaml``（规则=YAML、运行数据=DB，
DESIGN §2.2 ⑥，对标 comparison_policy.yaml 先例）。

用法::

    python scripts/ai_layer/apply_ai_heritage_ddl.py            # 部署 ai_heritage（幂等）
    python scripts/ai_layer/apply_ai_heritage_ddl.py --verify   # 只核对件数不部署
"""

from __future__ import annotations

import argparse
import functools
import logging
import re
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.depgraph_schema import (  # noqa: E402
    deploy_schema as _deploy_schema_engine,
    drop_test_schema as _drop_test_schema_engine,
    q_list as _q_list,
)

log = logging.getLogger("ai_heritage.ddl")

SCHEMA_RE: Final = re.compile(r"^ai_heritage(_test_[a-z0-9_]+)?$")
TEST_SCHEMA_PREFIX: Final = "ai_heritage_test_"


# FUNCTION-DUP 治本（2026-09-24）：deploy/drop 引擎唯一实现收敛 depgraph_schema，本模块按自身 DDL/GRANT/种子源绑定
deploy = functools.partial(
    _deploy_schema_engine,
    ddl_statements_fn=lambda schema: _ddl_statements(schema),
    grant_statements_fn=lambda schema: _grant_statements(schema),
)
drop_test_schema = functools.partial(_drop_test_schema_engine, test_schema_prefix=TEST_SCHEMA_PREFIX)
DEFAULT_SCHEMA: Final = "ai_heritage"

ENTRY_KINDS: Final[tuple[str, ...]] = ("elite", "criteria", "defect")
SOURCE_KINDS: Final[tuple[str, ...]] = (
    "l6_switch",
    "l4_experiment",
    "work_order",
    "redblue",
    "casebook",
    "checklist_seed",
    "memory_digest",
    "manual",
)
ENTRY_STATUS: Final[tuple[str, ...]] = ("active", "archived", "retired", "compressed")
SURFACES: Final[tuple[str, ...]] = ("code_module", "gate_param", "model", "tool", "rule")
VENUES: Final[tuple[str, ...]] = ("c4", "replay", "dual_run", "tool_bench", "other")
# 机制族 8 族词表（真源=L2 apply_ai_intake_ddl.MECHANISM_FAMILIES / ai_intake T2 CHECK 同值，引用锚定不另设真源）
MECHANISM_FAMILIES: Final[tuple[str, ...]] = (
    "prediction",
    "ranking",
    "optimization",
    "detection",
    "extraction",
    "orchestration",
    "pricing_risk",
    "unclassified",
)
TOTAL_CELLS: Final = 48  # 行为格 v0=6 域×8 族（config/heritage_policy.yaml anti_incest.total_cells 同值）

ENTRY_ID_RE_SQL: Final = r"^HT-[0-9]{8}-[0-9]{3}$"


_SQL_ENTRY = """
CREATE TABLE IF NOT EXISTS {s}.ai_heritage_entry (
    entry_id       TEXT PRIMARY KEY CHECK (entry_id ~ '{entry_id_re}'),
    entry_kind     TEXT NOT NULL CHECK (entry_kind IN ({kinds})),
    title          TEXT NOT NULL,
    plain_zh       TEXT NOT NULL CHECK (length(btrim(plain_zh)) >= 10),
    domain_id      TEXT NOT NULL,
    source_kind    TEXT NOT NULL CHECK (source_kind IN ({source_kinds})),
    source_ref     TEXT NOT NULL,
    text_norm      TEXT NOT NULL,
    simhash        BIT(64) NOT NULL,
    content_sha256 CHAR(64) NOT NULL UNIQUE,
    status         TEXT NOT NULL DEFAULT 'active' CHECK (status IN ({status})),
    hit_count      INT NOT NULL DEFAULT 0,
    last_hit_at    TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SQL_ELITE = """
CREATE TABLE IF NOT EXISTS {s}.ai_heritage_elite (
    entry_id         TEXT PRIMARY KEY REFERENCES {s}.ai_heritage_entry(entry_id),
    surface          TEXT NOT NULL CHECK (surface IN ({surfaces})),
    winner_ref       TEXT NOT NULL,
    loser_ref        TEXT,
    diff_summary     TEXT NOT NULL CHECK (length(btrim(diff_summary)) >= 30),
    evidence_ref     TEXT NOT NULL,
    score_summary    JSONB,
    mechanism_family TEXT NOT NULL CHECK (mechanism_family IN ({families})),
    gen              SMALLINT NOT NULL DEFAULT 1,
    parent_entry_id  TEXT REFERENCES {s}.ai_heritage_entry(entry_id)
)
"""

_SQL_CRITERIA = """
CREATE TABLE IF NOT EXISTS {s}.ai_heritage_criteria (
    entry_id         TEXT PRIMARY KEY REFERENCES {s}.ai_heritage_entry(entry_id),
    experiment_id    TEXT NOT NULL,
    criteria_hash    CHAR(64) NOT NULL,
    venue            TEXT NOT NULL CHECK (venue IN ({venues})),
    verdict          TEXT NOT NULL,
    simhash          BIT(64),
    mechanism_family TEXT CHECK (mechanism_family IN ({families})),
    why_win          TEXT NOT NULL CHECK (length(btrim(why_win)) >= 30),
    still_valid      BOOLEAN NOT NULL DEFAULT true,
    invalidated_by   TEXT
)
"""

_SQL_DEFECT = """
CREATE TABLE IF NOT EXISTS {s}.ai_heritage_defect (
    entry_id           TEXT PRIMARY KEY REFERENCES {s}.ai_heritage_entry(entry_id),
    root_cause         TEXT NOT NULL,
    signature          TEXT NOT NULL,
    recipe             TEXT NOT NULL,
    pattern_norm       TEXT NOT NULL UNIQUE,
    affected_surfaces  JSONB NOT NULL,
    tool_id            TEXT,
    scene              TEXT,
    exclusion_keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    occurrence_count   INT NOT NULL DEFAULT 1,
    first_seen         TIMESTAMPTZ NOT NULL,
    last_seen          TIMESTAMPTZ NOT NULL,
    fused_into_gate    TEXT
)
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_heritage_entry_kind ON {s}.ai_heritage_entry (entry_kind, status)",
    "CREATE INDEX IF NOT EXISTS ix_heritage_entry_domain ON {s}.ai_heritage_entry (domain_id, status)",
    "CREATE INDEX IF NOT EXISTS ix_heritage_entry_simhash ON {s}.ai_heritage_entry (simhash)",
    "CREATE INDEX IF NOT EXISTS ix_heritage_entry_last_hit ON {s}.ai_heritage_entry (last_hit_at)",
)

# V1：active 精英，按 surface×mechanism_family（L2 组合素材/L5 祖先分支查询口；格内保优 3 由
# forget.py 按月降级执行，视图只过滤 status 不重复算排名——语义=现役全体）
_SQL_VIEW_ELITES_ACTIVE = """
CREATE OR REPLACE VIEW {s}.ai_heritage_elites_active AS
SELECT e.entry_id, e.domain_id, e.status, e.hit_count, e.last_hit_at, e.created_at,
       x.surface, x.winner_ref, x.loser_ref, x.diff_summary, x.evidence_ref,
       x.score_summary, x.mechanism_family, x.gen, x.parent_entry_id
FROM {s}.ai_heritage_entry e
JOIN {s}.ai_heritage_elite x ON x.entry_id = e.entry_id
WHERE e.status = 'active'
"""

# V2：active 且未 compressed 的缺陷模式（T4 快照源+派工签名匹配源）
_SQL_VIEW_DEFECT_HOT = """
CREATE OR REPLACE VIEW {s}.ai_heritage_defect_hot AS
SELECT e.entry_id, e.domain_id, e.status, e.plain_zh, e.source_ref,
       d.root_cause, d.signature, d.recipe, d.pattern_norm, d.affected_surfaces,
       d.tool_id, d.scene, d.exclusion_keywords, d.occurrence_count,
       d.first_seen, d.last_seen, d.fused_into_gate
FROM {s}.ai_heritage_entry e
JOIN {s}.ai_heritage_defect d ON d.entry_id = e.entry_id
WHERE e.status = 'active'
"""

# V3：domain×family 格先验（active 精英数+近 90 天 hit 数→prior_factor∈[1.0,2.0] 与 rationale_refs）。
# v0 系数裁定：0.10/精英+0.01/hit，LEAST 封顶 2.0——纯加法只调排序（DESIGN §2.6 约束 1），
# 系数修订走 config/heritage_policy.yaml→OBJ_R（视图系数改动随批对齐）
_SQL_VIEW_L1_PRIOR = """
CREATE OR REPLACE VIEW {s}.ai_heritage_l1_prior AS
WITH cells AS (
    SELECT e.domain_id, x.mechanism_family,
           count(*)::int AS elite_n,
           COALESCE(sum(e.hit_count) FILTER (
               WHERE e.last_hit_at >= now() - INTERVAL '90 days'), 0)::int AS hit90_n,
           array_agg(e.entry_id ORDER BY e.entry_id) AS rationale_refs
    FROM {s}.ai_heritage_entry e
    JOIN {s}.ai_heritage_elite x ON x.entry_id = e.entry_id
    WHERE e.status = 'active'
    GROUP BY 1, 2
)
SELECT domain_id, mechanism_family, elite_n, hit90_n, rationale_refs,
       LEAST(2.0::numeric, 1.0::numeric + 0.10::numeric * elite_n + 0.01::numeric * hit90_n)
           AS prior_factor
FROM cells
"""

# V4：active 缺陷的 exclusion_keywords 展开（排除词表直接读；只滤词不灭矿脉的保底在消费侧 priors.py）
_SQL_VIEW_L1_EXCLUSION = """
CREATE OR REPLACE VIEW {s}.ai_heritage_l1_exclusion AS
SELECT e.domain_id, d.entry_id, d.pattern_norm, kw.keyword
FROM {s}.ai_heritage_entry e
JOIN {s}.ai_heritage_defect d ON d.entry_id = e.entry_id
CROSS JOIN LATERAL jsonb_array_elements_text(d.exclusion_keywords) AS kw(keyword)
WHERE e.status = 'active'
"""

# V5：月度 KPI（新增/命中/降级三数+l7_prior 占比占位列）+全局覆盖率/prior 冻结态（§2.6 约束 4）。
# v0 口径代理裁定：hits_recorded=sum(hit_count) FILTER last_hit_at 落月（hit_count 为累计值，
# 月度聚合窗回写时刷 last_hit_at——月粒度可视）；demoted=updated_at 落月且 status<>active；
# l7_prior 占比列留 NULL，L1 施工项 9 落地后由 L1 journal 侧回填（本 schema 无该数据真源）
_SQL_VIEW_KPI = """
CREATE OR REPLACE VIEW {s}.ai_heritage_kpi AS
WITH months AS (
    SELECT date_trunc('month', created_at) AS m FROM {s}.ai_heritage_entry
    UNION
    SELECT date_trunc('month', last_hit_at) FROM {s}.ai_heritage_entry WHERE last_hit_at IS NOT NULL
    UNION
    SELECT date_trunc('month', updated_at) FROM {s}.ai_heritage_entry WHERE status <> 'active'
),
cov AS (
    SELECT count(DISTINCT e.domain_id || '|' || x.mechanism_family)::int AS covered
    FROM {s}.ai_heritage_entry e
    JOIN {s}.ai_heritage_elite x ON x.entry_id = e.entry_id
    WHERE e.status = 'active'
)
SELECT to_char(m.m, 'YYYY-MM') AS month,
    (SELECT count(*) FROM {s}.ai_heritage_entry e2
      WHERE date_trunc('month', e2.created_at) = m.m) AS entries_new,
    (SELECT COALESCE(sum(e3.hit_count), 0) FROM {s}.ai_heritage_entry e3
      WHERE e3.last_hit_at IS NOT NULL AND date_trunc('month', e3.last_hit_at) = m.m) AS hits_recorded,
    (SELECT count(*) FROM {s}.ai_heritage_entry e4
      WHERE e4.status <> 'active' AND date_trunc('month', e4.updated_at) = m.m) AS demoted,
    NULL::numeric AS l7_prior_share,
    (SELECT round(100.0 * c.covered / {total_cells}.0, 2) FROM cov c) AS coverage_pct,
    ((SELECT c.covered * 100.0 FROM cov c) < 60.0 * {total_cells}) AS prior_frozen
FROM months m
"""


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_heritage 或 ai_heritage_test_<后缀>，"
            "防 DDL/DROP 打偏到他人 schema）"
        )
    return schema


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL 语句（幂等；schema 名已由 check_schema_name 白名单校验）。"""
    fmt: dict[str, Any] = {
        "s": schema,
        "kinds": _q_list(ENTRY_KINDS),
        "source_kinds": _q_list(SOURCE_KINDS),
        "status": _q_list(ENTRY_STATUS),
        "surfaces": _q_list(SURFACES),
        "venues": _q_list(VENUES),
        "families": _q_list(MECHANISM_FAMILIES),
        "entry_id_re": ENTRY_ID_RE_SQL,
        "total_cells": TOTAL_CELLS,
    }
    out = [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        _SQL_ENTRY.format(**fmt),
        _SQL_ELITE.format(**fmt),
        _SQL_CRITERIA.format(**fmt),
        _SQL_DEFECT.format(**fmt),
    ]
    out.extend(tpl.format(**fmt) for tpl in _SQL_INDEXES)
    out.extend([
        _SQL_VIEW_ELITES_ACTIVE.format(**fmt),
        _SQL_VIEW_DEFECT_HOT.format(**fmt),
        _SQL_VIEW_L1_PRIOR.format(**fmt),
        _SQL_VIEW_L1_EXCLUSION.format(**fmt),
        _SQL_VIEW_KPI.format(**fmt),
    ])
    return out


def _grant_statements(schema: str) -> list[str]:
    """角色分级授权（照 ai_intake 惯例：reader 只读 / writer 读写）。"""
    tables = (
        "ai_heritage_entry",
        "ai_heritage_elite",
        "ai_heritage_criteria",
        "ai_heritage_defect",
    )
    views = (
        "ai_heritage_elites_active",
        "ai_heritage_defect_hot",
        "ai_heritage_l1_prior",
        "ai_heritage_l1_exclusion",
        "ai_heritage_kpi",
    )
    out = [
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_reader",
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_writer",
    ]
    out.extend(f"GRANT SELECT ON {schema}.{t} TO depgraph_reader" for t in tables + views)
    out.extend(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {schema}.{t} TO depgraph_writer" for t in tables
    )
    return out


EXPECTED_TABLES: Final[tuple[str, ...]] = (
    "ai_heritage_entry",
    "ai_heritage_elite",
    "ai_heritage_criteria",
    "ai_heritage_defect",
)
EXPECTED_VIEWS: Final[tuple[str, ...]] = (
    "ai_heritage_elites_active",
    "ai_heritage_defect_hot",
    "ai_heritage_l1_prior",
    "ai_heritage_l1_exclusion",
    "ai_heritage_kpi",
)
SQL_VERIFY_RELATIONS = (
    "SELECT table_name, table_type FROM information_schema.tables "
    "WHERE table_schema = %s ORDER BY table_name"
)


def verify(schema: str = DEFAULT_SCHEMA) -> tuple[bool, list[str]]:
    """核对 schema 内表/视图是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(read_only=True)
    missing: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(SQL_VERIFY_RELATIONS, (schema,))
        found = {row[0]: row[1] for row in cur.fetchall()}
        for t in EXPECTED_TABLES:
            if t not in found:
                missing.append(f"table:{t}")
        for v in EXPECTED_VIEWS:
            if v not in found:
                missing.append(f"view:{v}")
    finally:
        conn.close()
    return (not missing), missing


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_heritage schema。"""
    parser = argparse.ArgumentParser(description="AI 层 L7 传承库 DDL 部署器（幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_heritage）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    parser.add_argument(
        "--drop-test-schema",
        action="store_true",
        help="删除测试残留 schema（仅 ai_heritage_test_ 前缀）",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.drop_test_schema:
            drop_test_schema(args.schema)
            print(f"DROPPED test schema {args.schema}")
            return 0
        if args.verify:
            ok, missing = verify(args.schema)
            print(f"VERIFY {args.schema}: {'OK' if ok else 'MISSING ' + ','.join(missing)}")
            return 0 if ok else 3
        counts = deploy(args.schema)
        ok, missing = verify(args.schema)
        print(f"DEPLOYED {args.schema} {counts} verify={'OK' if ok else missing}")
        return 0 if ok else 3
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2（PG 不可达/权限不足等）
        print(f"DDL FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: DDL 部署器属人工运维入口，非自动常驻任务
    sys.exit(main())
