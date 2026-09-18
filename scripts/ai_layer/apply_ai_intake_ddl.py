# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] scripts.ai_layer.apply_ai_intake_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] CLI python scripts/ai_layer/apply_ai_intake_ddl.py [--schema ai_intake] [--verify]; ★ 测试侧消费者 test_card_store.py 未建（在册缺口，见 lanes/aibase_relay.md §6）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] DDL-as-Code: ai_intake 五表三视图 DDL 真源即本文件（设计真源=docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2）;
#              全部幂等(CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS + CREATE OR REPLACE VIEW); 时间戳一律 TIMESTAMPTZ(RULE-SCHEMA-TZ 同义执行);
#              生熟分离物理边界=schema 级隔离(ai_intake.* 是生食库, 产线代码禁读);
#              schema 名必须匹配 ^[a-z_][a-z0-9_]*$ 且以 ai_intake 开头(fail-closed, 防 DROP/CREATE 打偏);
#              DROP 仅在 --drop-test-schema 且 schema 以 ai_intake_test_ 前缀时允许(测试残留清理专用)
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2（改表结构先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->打印错误+退出码 2; schema 名不合规->ValueError 立即拒跑(不静默改名); DDL 语句失败->回滚+非零退出; --verify 缺件->退出码 3 并列出缺失清单
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：opt-in 临时 schema 部署用例 test_card_store.py 未建；本件 --verify 已实跑 rc=0，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""AI 层 L2 收集段——原材料库 DDL 部署器（PostgreSQL depgraph 同实例，schema `ai_intake`）。

设计真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §2.2（五表三视图）。
照 ``scripts/industry_graph/apply_industry_graph_ddl.py`` 模式实现（admin 通道 + 幂等 + 角色分级 GRANT）。

表清单::

    ai_intake_domain          T1 域字典（域可生长，停用不删=墓碑制）
    ai_intake_card            T2 卡主表（全域共用——查重/KPI/行为格必须跨域单点）
    ai_intake_ext_governance  T3 治理学域扩展
    ai_intake_ext_trading_algo T3 交易算法域扩展
    ai_intake_ext_ai_eng      T3 AI 工程域扩展
    ai_intake_ext_data_eng    T3 数据工程域扩展
    ai_intake_ext_cost_eng    T3 成本工程域扩展
    ai_intake_ref_snapshot    T4 比对面快照（生成器产出，禁手工维护）
    ai_intake_source_quota    T5 源配额（过渡件，L1 源注册表落地后降级为只读缓存）
    ai_intake_elites          V1 每行为格 elite_score 前 3
    ai_intake_negative        V2 阴性库（funnel_stage='rejected'）
    ai_intake_kpi_weekly      V3 周×域 入考率 KPI

用法::

    python scripts/ai_layer/apply_ai_intake_ddl.py            # 部署 ai_intake（幂等）
    python scripts/ai_layer/apply_ai_intake_ddl.py --verify   # 只核对件数不部署
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

log = logging.getLogger("ai_intake.ddl")

SCHEMA_RE: Final = re.compile(r"^ai_intake(_test_[a-z0-9_]+)?$")
TEST_SCHEMA_PREFIX: Final = "ai_intake_test_"
DEFAULT_SCHEMA: Final = "ai_intake"
V0_DOMAINS: Final[tuple[tuple[str, str, str], ...]] = (
    ("governance", "治理学", "gate/registry/sop/宪法邻接件"),
    ("trading_algo", "交易算法", "alpha 机制与信号"),
    ("ai_eng", "AI 工程", "模型/评测/token 成本"),
    ("data_eng", "数据工程", "数据集与字段质量"),
    ("cost_eng", "成本工程", "计费线与省钱机制"),
    ("tooling", "工具域", "工具坑集与脚手架"),
)
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
FUNNEL_STAGES: Final[tuple[str, ...]] = ("L0", "L1", "L2", "E2", "intake", "e2_pending", "rejected")
SOURCE_KINDS: Final[tuple[str, ...]] = ("paper", "repo", "mechanism", "benchmark")
FOUR_GATES_KEYS: Final[tuple[str, ...]] = (
    "provenance",
    "cross_validation",
    "ashare_adaptation",
    "backtestable",
)


def _q_list(values: tuple[str, ...]) -> str:
    """把常量元组渲染成 SQL 单引号列表（值来源全是本模块常量，非外部输入）。"""
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


_SQL_DOMAIN = """
CREATE TABLE IF NOT EXISTS {s}.ai_intake_domain (
    domain_id  TEXT PRIMARY KEY,
    name_zh    TEXT NOT NULL,
    note       TEXT,
    enabled    BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SQL_CARD = """
CREATE TABLE IF NOT EXISTS {s}.ai_intake_card (
    card_id           TEXT PRIMARY KEY,
    domain_id         TEXT NOT NULL REFERENCES {s}.ai_intake_domain(domain_id),
    title             TEXT,
    novelty           TEXT,
    mechanism         TEXT,
    source_name       TEXT,
    source_url        TEXT NOT NULL CHECK (length(btrim(source_url)) > 0),
    source_publisher  TEXT,
    source_year       SMALLINT,
    source_kind       TEXT CHECK (source_kind IN ({kinds})),
    license           TEXT,
    content_sha256    CHAR(64) NOT NULL UNIQUE,
    simhash           BIT(64) NOT NULL,
    mechanism_family  TEXT NOT NULL CHECK (mechanism_family IN ({families})),
    elite_cell        TEXT GENERATED ALWAYS AS (domain_id || '|' || mechanism_family) STORED,
    elite_score       REAL,
    elite_rank        SMALLINT,
    elite_status      TEXT NOT NULL DEFAULT 'active' CHECK (elite_status IN ('active','benched')),
    funnel_stage      TEXT NOT NULL DEFAULT 'L0' CHECK (funnel_stage IN ({stages})),
    stage_changed_at  TIMESTAMPTZ,
    rejection_reason  TEXT,
    labor_killed      TEXT NOT NULL CHECK (length(btrim(labor_killed)) >= 20),
    four_gates        JSONB NOT NULL CHECK (four_gates ?& array[{gate_keys}]),
    injection_probe   TEXT NOT NULL CHECK (length(btrim(injection_probe)) > 0),
    risk_flags        JSONB NOT NULL DEFAULT '[]'::jsonb,
    dedup_compared_vs JSONB NOT NULL DEFAULT '[]'::jsonb,
    duplicate_of      TEXT REFERENCES {s}.ai_intake_card(card_id),
    raw_ref           TEXT,
    spec_ref          TEXT,
    handoff_ref       TEXT,
    evidence_ref      TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SQL_EXT_TABLES: Final[tuple[str, ...]] = (
    """
    CREATE TABLE IF NOT EXISTS {s}.ai_intake_ext_governance (
        card_id           TEXT PRIMARY KEY REFERENCES {s}.ai_intake_card(card_id) ON DELETE CASCADE,
        rule_target       TEXT,
        enforcement_level TEXT,
        replay_testable   BOOLEAN NOT NULL DEFAULT false,
        updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS {s}.ai_intake_ext_trading_algo (
        card_id          TEXT PRIMARY KEY REFERENCES {s}.ai_intake_card(card_id) ON DELETE CASCADE,
        alpha_horizon    TEXT,
        data_requirements JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        baseline_cmp     TEXT,
        updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS {s}.ai_intake_ext_ai_eng (
        card_id         TEXT PRIMARY KEY REFERENCES {s}.ai_intake_card(card_id) ON DELETE CASCADE,
        model_tier      TEXT,
        eval_task_ref   TEXT,
        token_cost_class TEXT,
        updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS {s}.ai_intake_ext_data_eng (
        card_id      TEXT PRIMARY KEY REFERENCES {s}.ai_intake_card(card_id) ON DELETE CASCADE,
        dataset_ref  TEXT,
        field_list   JSONB NOT NULL DEFAULT '[]'::jsonb,
        quality_gaps JSONB NOT NULL DEFAULT '[]'::jsonb,
        updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS {s}.ai_intake_ext_cost_eng (
        card_id          TEXT PRIMARY KEY REFERENCES {s}.ai_intake_card(card_id) ON DELETE CASCADE,
        cost_category    TEXT,
        savings_estimate NUMERIC(18, 4),
        billing_line_ref TEXT,
        updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
)

_SQL_REF_SNAPSHOT = """
CREATE TABLE IF NOT EXISTS {s}.ai_intake_ref_snapshot (
    snapshot_id  BIGSERIAL PRIMARY KEY,
    ref_family   TEXT NOT NULL CHECK (ref_family IN ('chart','indicator','algo_flow','L7')),
    ref_key      TEXT NOT NULL,
    text_norm    TEXT NOT NULL,
    simhash      BIT(64) NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (ref_family, ref_key)
)
"""

_SQL_SOURCE_QUOTA = """
CREATE TABLE IF NOT EXISTS {s}.ai_intake_source_quota (
    source_slug TEXT PRIMARY KEY,
    track       TEXT,
    daily_quota INTEGER NOT NULL DEFAULT 10 CHECK (daily_quota >= 1),
    note        TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_intake_card_stage ON {s}.ai_intake_card (domain_id, funnel_stage)",
    "CREATE INDEX IF NOT EXISTS ix_intake_card_cell ON {s}.ai_intake_card (elite_cell)",
    "CREATE INDEX IF NOT EXISTS ix_intake_card_source ON {s}.ai_intake_card (source_name, created_at)",
    "CREATE INDEX IF NOT EXISTS ix_intake_card_simhash ON {s}.ai_intake_card (simhash)",
    "CREATE INDEX IF NOT EXISTS ix_intake_ref_family ON {s}.ai_intake_ref_snapshot (ref_family)",
)

_SQL_VIEW_ELITES = """
CREATE OR REPLACE VIEW {s}.ai_intake_elites AS
SELECT card_id, domain_id, mechanism_family, elite_cell, elite_score, elite_rank, elite_status, funnel_stage
FROM (
    SELECT c.card_id, c.domain_id, c.mechanism_family, c.elite_cell, c.elite_score,
           c.elite_rank, c.elite_status, c.funnel_stage,
           row_number() OVER (
               PARTITION BY c.elite_cell ORDER BY c.elite_score DESC NULLS LAST, c.created_at
           ) AS rn
    FROM {s}.ai_intake_card c
    WHERE c.elite_status = 'active'
) ranked
WHERE ranked.rn <= 3
"""

_SQL_VIEW_NEGATIVE = """
CREATE OR REPLACE VIEW {s}.ai_intake_negative AS
SELECT card_id, domain_id, mechanism_family, elite_cell, funnel_stage, rejection_reason,
       duplicate_of, source_name, source_url, content_sha256, simhash, stage_changed_at
FROM {s}.ai_intake_card
WHERE funnel_stage = 'rejected'
"""

_SQL_VIEW_KPI = """
CREATE OR REPLACE VIEW {s}.ai_intake_kpi_weekly AS
SELECT date_trunc('week', created_at)                       AS week_start,
       domain_id,
       count(*)                                             AS cards_total,
       count(*) FILTER (WHERE funnel_stage IN ('E2','intake','e2_pending')) AS cards_to_exam,
       count(*) FILTER (WHERE funnel_stage = 'rejected')    AS cards_rejected,
       CASE WHEN count(*) = 0 THEN NULL
            ELSE round(100.0 * count(*) FILTER (WHERE funnel_stage IN ('E2','intake','e2_pending')) / count(*), 2)
       END                                                  AS exam_pass_rate_pct
FROM {s}.ai_intake_card
GROUP BY 1, 2
"""

# 域字典 v0 种子（T1 数据；{s} 由 check_schema_name 白名单校验后渲染）
SQL_SEED_DOMAIN = (
    "INSERT INTO {s}.ai_intake_domain (domain_id, name_zh, note) "
    "VALUES (%s, %s, %s) ON CONFLICT (domain_id) DO NOTHING"
)


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL 语句（幂等；schema 名已由 check_schema_name 白名单校验）。"""
    fmt: dict[str, Any] = {
        "s": schema,
        "kinds": _q_list(SOURCE_KINDS),
        "families": _q_list(MECHANISM_FAMILIES),
        "stages": _q_list(FUNNEL_STAGES),
        "gate_keys": _q_list(FOUR_GATES_KEYS),
    }
    out = [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        _SQL_DOMAIN.format(**fmt),
        _SQL_CARD.format(**fmt),
    ]
    out.extend(tpl.format(**fmt) for tpl in _SQL_EXT_TABLES)
    out.append(_SQL_REF_SNAPSHOT.format(**fmt))
    out.append(_SQL_SOURCE_QUOTA.format(**fmt))
    out.extend(tpl.format(**fmt) for tpl in _SQL_INDEXES)
    out.extend([
        _SQL_VIEW_ELITES.format(**fmt),
        _SQL_VIEW_NEGATIVE.format(**fmt),
        _SQL_VIEW_KPI.format(**fmt),
    ])
    return out


def _seed_statements(schema: str) -> list[tuple[str, tuple[Any, ...]]]:
    """域字典 v0 六域种子（幂等 upsert；域名=T1 数据，Owner 可改，DESIGN §5.3）。"""
    sql = SQL_SEED_DOMAIN.format(s=schema)
    return [(sql, row) for row in V0_DOMAINS]


def _grant_statements(schema: str) -> list[str]:
    """角色分级授权（照 industry_graph 惯例：reader 只读 / writer 读写）。"""
    tables = (
        "ai_intake_domain",
        "ai_intake_card",
        "ai_intake_ext_governance",
        "ai_intake_ext_trading_algo",
        "ai_intake_ext_ai_eng",
        "ai_intake_ext_data_eng",
        "ai_intake_ext_cost_eng",
        "ai_intake_ref_snapshot",
        "ai_intake_source_quota",
    )
    views = ("ai_intake_elites", "ai_intake_negative", "ai_intake_kpi_weekly")
    out = [
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_reader",
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_writer",
        f"GRANT USAGE, SELECT ON SEQUENCE {schema}.ai_intake_ref_snapshot_snapshot_id_seq TO depgraph_writer",
    ]
    out.extend(f"GRANT SELECT ON {schema}.{t} TO depgraph_reader" for t in tables + views)
    out.extend(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {schema}.{t} TO depgraph_writer" for t in tables
    )
    return out


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_intake 或 ai_intake_test_<后缀>，"
            "防 DDL/DROP 打偏到他人 schema）"
        )
    return schema


def deploy(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> dict[str, int]:
    """部署/刷新 schema（幂等）。返回各阶段执行计数。

    :param schema: 目标 schema（白名单校验）
    :param conn: 可选已存在连接（测试注入用）；缺省自建 admin 连接并负责关闭
    """
    check_schema_name(schema)
    own_conn = conn is None
    if own_conn:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    counts = {"ddl": 0, "seed": 0, "grant": 0}
    try:
        cur = conn.cursor()
        for stmt in _ddl_statements(schema):
            cur.execute(stmt)
            counts["ddl"] += 1
        for sql, params in _seed_statements(schema):
            cur.execute(sql, params)
            counts["seed"] += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        for stmt in _grant_statements(schema):
            # SAVEPOINT 包裹：角色不存在（本地精简实例）时只回滚该条 GRANT，
            # 不能整事务回滚（PG 的 DDL 是事务性的，rollback 会把表一起撤掉）。
            cur.execute("SAVEPOINT sp_grant")
            try:
                cur.execute(stmt)
                counts["grant"] += 1
                cur.execute("RELEASE SAVEPOINT sp_grant")
            except Exception as exc:  # noqa: BLE001——授权失败不阻断 DDL 主体，warning 留痕
                log.warning("GRANT 跳过：%s", exc)
                cur.execute("ROLLBACK TO SAVEPOINT sp_grant")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()
    return counts


EXPECTED_TABLES: Final[tuple[str, ...]] = (
    "ai_intake_domain",
    "ai_intake_card",
    "ai_intake_ext_governance",
    "ai_intake_ext_trading_algo",
    "ai_intake_ext_ai_eng",
    "ai_intake_ext_data_eng",
    "ai_intake_ext_cost_eng",
    "ai_intake_ref_snapshot",
    "ai_intake_source_quota",
)
EXPECTED_VIEWS: Final[tuple[str, ...]] = (
    "ai_intake_elites",
    "ai_intake_negative",
    "ai_intake_kpi_weekly",
)
SQL_VERIFY_RELATIONS = (
    "SELECT table_name, table_type FROM information_schema.tables "
    "WHERE table_schema = %s ORDER BY table_name"
)
SQL_VERIFY_GENERATED_COL = (
    "SELECT column_name, is_generated FROM information_schema.columns "
    "WHERE table_schema = %s AND table_name = 'ai_intake_card' AND is_generated = 'ALWAYS'"
)


def verify(schema: str = DEFAULT_SCHEMA) -> tuple[bool, list[str]]:
    """核对 schema 内表/视图/生成列是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
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
        cur.execute(SQL_VERIFY_GENERATED_COL, (schema,))
        if not cur.fetchall():
            missing.append("generated_column:ai_intake_card.elite_cell")
    finally:
        conn.close()
    return (not missing), missing


def drop_test_schema(schema: str) -> None:
    """删除测试残留 schema（仅 ai_intake_test_ 前缀允许；生产 schema 永不删）。"""
    if not schema.startswith(TEST_SCHEMA_PREFIX):
        raise ValueError(f"拒删非测试 schema：{schema!r}")
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_intake schema。"""
    parser = argparse.ArgumentParser(description="AI 层 L2 原材料库 DDL 部署器（幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_intake）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    parser.add_argument(
        "--drop-test-schema",
        action="store_true",
        help="删除测试残留 schema（仅 ai_intake_test_ 前缀）",
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
