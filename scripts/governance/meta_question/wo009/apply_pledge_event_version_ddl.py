# [BLUEPRINT] MOD-METAQ-WO009 | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md | §WO-009（质押事件版本载体 DDL）
# [MODULE] scripts.governance.meta_question.wo009.apply_pledge_event_version_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); psycopg2
# [CONSUMERS] scripts/governance/meta_question/wo009/backfill_pledge_event_version.py（写入本 schema 两表）; scripts/governance/meta_question/wo009/recheck_pq0072_violation.py（判据复算读视图/表）; 信号侧穿透链消费者经 metaq_pledge.v_holder_edge_version_timeline / holder_versions_as_of() 取"持股+质押"双时态版本流
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 结构安全（fail-closed，代码级强断言，不靠人肉纪律）: I1 零触碰既有业务表——本部署器执行的每条语句必须先过 _assert_statement_safe()： (a) 所有被引用关系必须 schema 限定且 schema == 目标 schema；(b) 禁 DELETE/TRUNCATE/ALTER TABLE/DROP TABLE/DROP COLUMN； (c) DROP SCHEMA 仅当目标 schema 以 metaq_pledge_test_ 前缀时允许 → public.edge_holding / public.node_entity 永不被写； I2 schema 名白名单 ^metaq_pledge(_test_[a-z0-9_]+)?$，不合规 ValueError 立即拒跑（防 DDL 打偏），绝不静默改名； I3 全部 DDL 幂等：CREATE SCHEMA/TABLE/INDEX/VIEW IF NOT EXISTS + CREATE OR REPLACE FUNCTION → 可重放； I4 时间戳一律带显式时区（RULE-SCHEMA-TZ）：known_at/recorded_at/finished_at 全 TIMESTAMPTZ， known_at 缺省不取本机时钟（DEFAULT 只允许 now()），生成/回填侧禁 datetime.now()； I5 双时态语义固定：valid_from=公告生效时点（知识到达日）；business_from/business_to=业务真实区间； known_at=transaction_time（源入库时点）；同对版本链按"不同公告日"闭合 → CHECK valid_to > valid_from 恒成立； I6 一行 = 一条质押公告事件的一个版本，event_uid = 源行全列 sha256 内容指纹（源表无主键，实测窗内零全行重复） → UNIQUE(event_uid) 天然幂等，重复回填不产生第二行； I7 载体只增不改：edge_holding 的 valid_from 语义（报告期快照）不被覆写，质押版本走旁挂层。
# [MODIFY-GUARD] docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-009（改表结构先改本文件并在案卷留痕）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] schema 名不合规->ValueError 拒跑(码 2); 语句触及非目标 schema->SafetyViolation 拒跑(码 2); PG 不可达->打印错误+码 2; --verify 缺件->码 3 并列缺失清单; 拒删非测试 schema->ValueError
# [TESTS] 本单内自证：--schema metaq_pledge_test_wo009 演练 → --verify → --drop-test-schema 清理； 生产 metaq_pledge 部署后由 recheck_pq0072_violation.py 的 I 组完整性断言复核（非 pytest，运维脚本族先例）
# [A_module] module_id=MOD-METAQ-WO009-DDL | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""WO-009：质押「事件版本载体」DDL 部署器（PostgreSQL 新 schema ``metaq_pledge``，幂等可重放）。

选型结论（详见 docs/_working/meta_question_answers/build/WO-009.yaml）：
**旁挂双时态 event_version 表**（valid_time=公告生效时点，transaction_time=入库时点），
不改 ``public.edge_holding`` 原表结构、不写其行——理由三条：
  1) 实测 4,678/5,238 条违规对应的股东-公司对在事件日之后**根本不存在任何持股版本行**（不是时戳写错，
     是版本链没推进）→ 改 valid_from 口径等于伪造事实，换口径无效已被实证；
  2) 方案 B 需向 1,500,341 行业务表灌入 112,822 行（+7.52%）并引入 role 词表外的新值，
     穿透链/牛散信号全部下游连坐；
  3) edge_holding 单时态（valid_from/valid_to）无处安放"何时知道"这一轴，双时态是本题的硬需求。

对象清单::

    metaq_pledge.pledge_event_version   事件版本载体主表（双时态，112,822 行回填目标）
    metaq_pledge.backfill_run_log       分片断点账本（回填可续跑/幂等的真源）
    metaq_pledge.v_pledge_event_current 现行质押版本视图
    metaq_pledge.v_holder_edge_version_timeline  持股版本 ∪ 质押版本 的统一版本流视图（消费者入口）
    metaq_pledge.holder_versions_as_of(text, date, date)  PIT 函数：给定日可见的版本集合

用法::

    python scripts/governance/meta_question/wo009/apply_pledge_event_version_ddl.py --schema metaq_pledge_test_wo009 -- rehearse
    python scripts/governance/meta_question/wo009/apply_pledge_event_version_ddl.py            # 部署（幂等）
    python scripts/governance/meta_question/wo009/apply_pledge_event_version_ddl.py --verify    # 只核对
    python scripts/governance/meta_question/wo009/apply_pledge_event_version_ddl.py --schema metaq_pledge_test_wo009 --drop-test-schema
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(
    0, str(Path(__file__).resolve().parents[4] / "src")
)  # 本文件深 4 层：scripts/governance/meta_question/wo009/

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

log = logging.getLogger("metaq_pledge.ddl")

SCHEMA_RE: Final = re.compile(r"^metaq_pledge(_test_[a-z0-9_]+)?$")
TEST_SCHEMA_PREFIX: Final = "metaq_pledge_test_"
DEFAULT_SCHEMA: Final = "metaq_pledge"

# 业务时区：A 股公告日按北京时间记账（显式写进 CHECK，不靠会话 TimeZone）
BUSINESS_TZ: Final = "Asia/Shanghai"


class SafetyViolation(RuntimeError):
    """结构安全断言失败——语句触犯了"零触碰既有业务表"红线。"""


# 禁止的写操作关键字（对既有表的一切破坏性/结构性动作；UPDATE 亦禁——部署器只做新建）
_FORBIDDEN_RE: Final = re.compile(
    r"\b(DELETE\s+FROM|TRUNCATE\b|ALTER\s+TABLE|DROP\s+TABLE|DROP\s+COLUMN|UPDATE\b)", re.IGNORECASE
)
# 视图/函数体内允许"只读引用"的既有 schema（配合上条：本部署器无 DML 能力，故 public.* 恒为读）
_READONLY_REF_SCHEMAS: Final[frozenset[str]] = frozenset({"public"})
# 新建对象语句：必须以 "<目标 schema>." 限定对象名（防 search_path 打偏）
_OBJECT_STMT_RE: Final = re.compile(
    r"^\s*(?:CREATE|DROP)\s+(?:(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW|FUNCTION|INDEX|SEQUENCE)|SCHEMA)",
    re.IGNORECASE,
)


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。对象名与本文件既有 DDL 常量同法写死在语句内，
# schema 一律 {s} 占位由调用点注入（PG 侧参数继续走 %s 绑定，禁在此落任何日期/字面量）。
_SQL_CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS {s}"
_SQL_DROP_SCHEMA = "DROP SCHEMA IF EXISTS {s} CASCADE"
_SQL_DROP_OWN = "DROP {kind} IF EXISTS {s}.{rel}{tail} CASCADE"
_SQL_SAVEPOINT_GRANT = "SAVEPOINT sp_grant"
_SQL_RELEASE_GRANT = "RELEASE SAVEPOINT sp_grant"
_SQL_ROLLBACK_GRANT = "ROLLBACK TO SAVEPOINT sp_grant"
# 授权位顺序=原 grant_statements 字面顺序，逐条执行序不得改动
_SQL_GRANTS: Final[tuple[str, ...]] = (
    "GRANT USAGE ON SCHEMA {s} TO depgraph_reader",
    "GRANT USAGE ON SCHEMA {s} TO depgraph_writer",
    "GRANT SELECT ON {s}.pledge_event_version TO depgraph_reader",
    "GRANT SELECT ON {s}.backfill_run_log TO depgraph_reader",
    "GRANT SELECT ON {s}.v_pledge_event_current TO depgraph_reader",
    "GRANT SELECT ON {s}.v_holder_edge_version_timeline TO depgraph_reader",
    "GRANT EXECUTE ON FUNCTION {s}.holder_versions_as_of(TEXT, DATE, TIMESTAMPTZ) TO depgraph_reader",
    "GRANT SELECT, INSERT, UPDATE ON {s}.pledge_event_version TO depgraph_writer",
    "GRANT SELECT, INSERT, UPDATE ON {s}.backfill_run_log TO depgraph_writer",
)
# 完整性核对只读探针（verify/--verify 分支）
_SQL_PG_SCHEMAS = "SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg\\_%' AND nspname <> 'information_schema'"
_SQL_PG_TABLES = "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"
_SQL_PG_INDEXES = "SELECT indexname FROM pg_indexes WHERE schemaname=%s"
_SQL_PG_VIEWS = (
    "SELECT table_name FROM information_schema.views WHERE table_catalog=current_database() AND table_schema=%s"
)
_SQL_PG_PROCS = "SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname=%s"
_SQL_PG_TZ_COLUMNS = (
    "SELECT column_name, data_type FROM information_schema.columns "
    "WHERE table_schema=%s AND table_name=%s AND column_name IN ('known_at','recorded_at')"
)


def _strip_sql_comments(sql: str) -> str:
    """去掉 ``--`` 行注释与单引号字面量（注释/字面量里的表名是文档文字，不是被触及的关系）。"""
    no_comment = "\n".join(line.split("--", 1)[0] for line in sql.splitlines())
    return re.sub(r"'(?:[^']|'')*'", "''", no_comment)


def assert_statement_safe(sql: str, schema: str, known_schemas: tuple[str, ...] = ()) -> None:
    """每条语句执行前的结构安全断言（I1 的代码级实现）。

    1. 全局禁 DML/破坏性 DDL：DELETE / UPDATE / TRUNCATE / ALTER TABLE / DROP TABLE / DROP COLUMN；
    2. 语句中出现的每个"已知 schema 限定引用"必须落在目标 schema，或落在只读引用白名单 schema
       （配合第 1 条，public.edge_holding 之类只可能被读，不可能被写）；
    3. 新建对象语句（CREATE TABLE/VIEW/FUNCTION/INDEX/SCHEMA、DROP SCHEMA）的对象名必须显式
       schema 限定且等于目标 schema —— 裸名一律拒跑（防 search_path 漂移打偏）。
    """
    body = _strip_sql_comments(sql)
    m = _FORBIDDEN_RE.search(body)
    if m:
        raise SafetyViolation(f"拒执行：语句含禁用写操作 {m.group(0)!r}（本部署器只做新建，不删不改既有对象）")
    for sch in known_schemas:
        if sch in (schema, *_READONLY_REF_SCHEMAS):
            continue
        if re.search(rf"\b{re.escape(sch)}\s*\.", body, re.IGNORECASE):
            raise SafetyViolation(
                f"拒执行：语句引用了非目标 schema {sch}.*（目标 schema={schema}；只读白名单={sorted(_READONLY_REF_SCHEMAS)}）"
            )
    if _OBJECT_STMT_RE.match(body):
        for q in re.finditer(
            r"\b(?:TABLE|VIEW|FUNCTION|SEQUENCE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:OR\s+REPLACE\s+)?"
            r"(?P<obj>[A-Za-z_][\w.]*)",
            body,
            re.IGNORECASE,
        ):
            obj = q.group("obj")
            target = obj.split(".")[-2] if "." in obj else ""
            if target.lower() != schema.lower():
                raise SafetyViolation(f"拒执行：新建对象 {obj} 未限定在目标 schema {schema}（防打偏）")
            if "." not in obj:
                raise SafetyViolation(f"拒执行：新建对象 {obj} 为裸名（防 search_path 漂移）")
        for q in re.finditer(
            r"\bINDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>[\w]+)\s+ON\s+(?P<obj>[\w.]+)", body, re.IGNORECASE
        ):
            if q.group("obj").split(".")[-2].lower() != schema.lower():
                raise SafetyViolation(f"拒执行：索引 {q.group('name')} 建在非目标关系 {q.group('obj')} 上")
        for q in re.finditer(r"\bDROP\s+SCHEMA\s+(?:IF\s+EXISTS\s+)?(?P<obj>[\w.]+)", body, re.IGNORECASE):
            if q.group("obj").lower() != schema.lower():
                raise SafetyViolation(f"拒执行：DROP SCHEMA 目标 {q.group('obj')} 非已校验 schema {schema}")


# ===================== DDL 真源（大白话注释逐条写在 SQL 里） =====================
_TABLE_MAIN = "pledge_event_version"
_TABLE_RUNLOG = "backfill_run_log"
_VIEWS: Final[tuple[str, ...]] = ("v_pledge_event_current", "v_holder_edge_version_timeline")
_FUNCTION: Final = "holder_versions_as_of"

# 载体主表：一行 = 一条质押公告事件产生的一个版本（双时态）
_SQL_MAIN = """
CREATE TABLE IF NOT EXISTS {s}.pledge_event_version (
    -- 身份：源表无主键 → 用全列内容指纹当主键（实测窗内零全行重复，见探针 probe02/03）
    event_uid           TEXT        NOT NULL,
    source_ref          TEXT        NOT NULL,
    source_row_no       INTEGER     NOT NULL DEFAULT 0,
    backfill_run_id     TEXT        NOT NULL DEFAULT '',
    -- 主体：公司侧 = symbol(裸码)/symbol_canonical(带交易所后缀)/entity_id；股东侧 = 原名+归一名+entity_id
    symbol              TEXT        NOT NULL,
    symbol_canonical    TEXT        NOT NULL,
    exchange            TEXT        NOT NULL,
    company_entity_id   TEXT        NOT NULL,
    holder_name         TEXT        NOT NULL,
    holder_name_norm    TEXT        NOT NULL,
    holder_entity_id    TEXT,
    holder_kind         TEXT,
    holder_type_src     TEXT        NOT NULL DEFAULT '',
    holder_resolution   TEXT        NOT NULL,
    -- 事件语义：event_type 词表含 judicial_freeze（冻结源表未建，先留槽，见案卷待裁项 T2）
    event_type          TEXT        NOT NULL,
    event_date_basis    TEXT        NOT NULL,
    -- 双时态第一轴 valid_time：公告生效时点（市场从这天起"知道"这件事）→ 版本从这天起生效
    valid_from          DATE        NOT NULL,
    valid_to            DATE,
    is_current            BOOLEAN     NOT NULL DEFAULT FALSE,
    -- 双时态第二轴 transaction_time：入库时点（数据平台从哪天起持有这条事实）。
    -- 实测源列 CH ingest_ts 不可用作本轴：DEFAULT now() 读时求值，全表仅 2 个取值且最大值随查询时刻漂移
    -- → 它记录的是"这次查询的时间"，不是"我们知道这件事的时间"。故本轴由 PG 服务器时钟在落库时定值。
    known_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- 业务真实区间（与知识到达时点分离——这正是"换口径无效"的根因所在）
    business_from       DATE,
    business_to         DATE,
    -- 源缺陷申报位：实测窗内恰 1 行业务区间倒挂（pledge_end_date < pledge_start_date，
    -- 600237 铜峰集团 2018-11-29 公告），系源数据缺陷而非本载体可为；照源值保留 + 强制申报，
    -- 不静默改写也不静默丢弃（申报由 ck_business_span_declared 硬约束，声明与实际不符即写入失败）
    business_span_inverted BOOLEAN NOT NULL DEFAULT FALSE,
    release_date        DATE,
    is_released         SMALLINT,
    -- 事实载荷（源列原样携带，派生列一律不覆写源义）
    pledgee             TEXT        NOT NULL DEFAULT '',
    pledge_shares       NUMERIC,
    total_holdings      NUMERIC,
    total_pledged       NUMERIC,
    pledge_ratio        NUMERIC,
    holding_ratio       NUMERIC,
    is_buyback          SMALLINT,
    remark              TEXT        NOT NULL DEFAULT '',
    src_data_source     TEXT        NOT NULL,
    src_quality_flag    SMALLINT,
    -- ===== 不变量（每条一个 CHECK，违反即写入失败，不靠事后人检）=====
    CONSTRAINT pk_pledge_event_version PRIMARY KEY (event_uid),
    CONSTRAINT uq_pledge_event_source UNIQUE (source_ref),
    CONSTRAINT ck_symbol CHECK (symbol ~ '^[0-9]{{6}}$'),
    CONSTRAINT ck_symbol_canonical CHECK (symbol_canonical ~ '^[0-9]{{6}}\\.(SH|SZ|BJ)$'),
    CONSTRAINT ck_exchange CHECK (exchange IN ('SH','SZ','BJ')),
    CONSTRAINT ck_company_entity CHECK (company_entity_id = 'CO:' || symbol_canonical),
    CONSTRAINT ck_holder_norm CHECK (holder_name_norm !~ '\\s'),
    CONSTRAINT ck_event_type CHECK (event_type IN ('pledge','pledge_release','pledge_extension','judicial_freeze')),
    CONSTRAINT ck_resolution CHECK (holder_resolution IN ('resolved','unresolved')),
    CONSTRAINT ck_basis CHECK (event_date_basis = 'announce_date'),
    -- 链闭合：同对下一版本按"不同公告日"闭合 → valid_to 必晚于 valid_from（零长区间被硬拦）
    CONSTRAINT ck_valid_span CHECK (valid_to IS NULL OR valid_to > valid_from),
    -- 因果：入库时点不得早于该版本的公告生效时点（不许"未卜先知"）
    CONSTRAINT ck_known_not_before_valid
        CHECK (known_at >= (valid_from::timestamp AT TIME ZONE '{tz}')),
    -- 业务区间自洽（业务起止与公告日无强制先后：质押可追溯办理，故只约束两端互相）
    CONSTRAINT ck_business_span CHECK (business_to IS NULL OR business_from IS NULL
                                       OR business_to >= business_from OR business_span_inverted),
    -- 申报必须与数据吻合：倒挂标志为真 ⟺ 两端齐全且 end < start（禁"随手打标"，也禁"藏着不报"）
    CONSTRAINT ck_business_span_declared CHECK (
        business_span_inverted IS NOT DISTINCT FROM
        (business_from IS NOT NULL AND business_to IS NOT NULL AND business_to < business_from)
    )
)
"""

# 断点账本：分片续跑的真源（一行一片，重跑只补缺，不靠本地文件）
_SQL_RUNLOG = """
CREATE TABLE IF NOT EXISTS {s}.backfill_run_log (
    shard_key     TEXT        NOT NULL,
    rows_source   INTEGER     NOT NULL DEFAULT 0,
    rows_written  INTEGER     NOT NULL DEFAULT 0,
    status        TEXT        NOT NULL DEFAULT 'pending',
    run_id        TEXT        NOT NULL DEFAULT '',
    finished_at   TIMESTAMPTZ,
    CONSTRAINT pk_backfill_run_log PRIMARY KEY (shard_key),
    CONSTRAINT ck_status CHECK (status IN ('pending','done'))
)
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    # 判据复算与 PIT 主查询：某股东在某票上的版本流（按归一名+代码+生效日）
    "CREATE INDEX IF NOT EXISTS ix_pev_pair_valid ON {s}.pledge_event_version (holder_name_norm, symbol, valid_from)",
    # 按公司取质押版本流（穿透链附标用）
    "CREATE INDEX IF NOT EXISTS ix_pev_company_valid ON {s}.pledge_event_version (symbol_canonical, valid_from)",
    # 公告日历扫描（事件线增量/对账）
    "CREATE INDEX IF NOT EXISTS ix_pev_valid_from ON {s}.pledge_event_version (valid_from)",
    # 现行版本稀疏索引（is_current 只有少数行为真）
    "CREATE INDEX IF NOT EXISTS ix_pev_current ON {s}.pledge_event_version (symbol_canonical) WHERE is_current",
    # 实体解析后的按节点查询（股东 entity_id 维度）
    "CREATE INDEX IF NOT EXISTS ix_pev_holder_entity ON {s}.pledge_event_version (holder_entity_id) WHERE holder_entity_id IS NOT NULL",
)

# 现行质押版本（消费者最常用切片）
_SQL_VIEW_CURRENT = """
CREATE OR REPLACE VIEW {s}.v_pledge_event_current AS
SELECT symbol, symbol_canonical, exchange, company_entity_id,
       holder_name, holder_name_norm, holder_entity_id, holder_kind,
       event_type, valid_from, known_at, pledge_shares, pledgee,
       is_released, release_date, business_from, business_to, source_ref
FROM {s}.pledge_event_version
WHERE is_current
"""

# 统一版本流：持股快照版本（既有业务表，只读引用）∪ 质押事件版本（新载体）
# —— 消费者不必再二选一，PIT 比较一律走这条视图；version_kind 标明版本来源与语义。
_SQL_VIEW_TIMELINE = """
CREATE OR REPLACE VIEW {s}.v_holder_edge_version_timeline AS
SELECT 'holding_snapshot'::text            AS version_kind,
       e.from_entity                       AS holder_entity_id,
       n.name_norm::text                   AS holder_name_norm,
       e.to_entity                         AS company_entity_id,
       split_part(e.to_entity, '.', 1)     AS symbol,
       e.valid_from                        AS valid_from,
       e.valid_to                          AS valid_to,
       e.announce_date                     AS known_from_date,
       e.ingested_at                       AS known_at,
       e.role                              AS payload_role,
       e.stake_pct                         AS stake_pct,
       NULL::numeric                       AS pledge_shares,
       e.source || ':' || coalesce(e.source_ref, '') AS source_ref
FROM public.edge_holding e
JOIN public.node_entity n ON n.entity_id = e.from_entity
WHERE e.to_entity ~ '^CO:[0-9]{{6}}\\.(SH|SZ|BJ)$'
UNION ALL
SELECT 'pledge_event'::text                AS version_kind,
       p.holder_entity_id                  AS holder_entity_id,
       p.holder_name_norm                  AS holder_name_norm,
       p.company_entity_id                 AS company_entity_id,
       p.symbol                            AS symbol,
       p.valid_from                        AS valid_from,
       p.valid_to                          AS valid_to,
       p.valid_from                        AS known_from_date,
       p.known_at                          AS known_at,
       p.event_type                        AS payload_role,
       NULL::numeric                       AS stake_pct,
       p.pledge_shares                     AS pledge_shares,
       p.source_ref                        AS source_ref
FROM {s}.pledge_event_version p
"""

# PIT 函数：给定 (裸码或带后缀代码, 观察日) → 该日"已发生且已入库"的全部版本
# p_as_of = 业务观察日；p_knowledge_cutoff（可空）= 只承认可在此刻之前入库的知识（真 PIT 回放用）
_SQL_FUNCTION = """
CREATE OR REPLACE FUNCTION {s}.holder_versions_as_of(
    p_symbol TEXT, p_as_of DATE, p_knowledge_cutoff TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
    version_kind     TEXT,
    holder_name_norm TEXT,
    holder_entity_id TEXT,
    company_entity_id TEXT,
    valid_from       DATE,
    valid_to         DATE,
    known_at         TIMESTAMPTZ,
    payload_role     TEXT,
    stake_pct        NUMERIC,
    pledge_shares    NUMERIC,
    source_ref       TEXT
)
LANGUAGE sql STABLE
AS $$
    SELECT t.version_kind, t.holder_name_norm, t.holder_entity_id, t.company_entity_id,
           t.valid_from, t.valid_to, t.known_at, t.payload_role, t.stake_pct, t.pledge_shares, t.source_ref
    FROM {s}.v_holder_edge_version_timeline t
    WHERE (t.symbol = p_symbol OR t.company_entity_id = 'CO:' || p_symbol)
      AND t.valid_from <= p_as_of
      AND (t.valid_to IS NULL OR t.valid_to > p_as_of)
      AND (p_knowledge_cutoff IS NULL OR t.known_at <= p_knowledge_cutoff)
    ORDER BY t.valid_from DESC, t.version_kind
$$
"""

# 逐列大白话注释（COMMENT ON 天然幂等，重放无害）
_COMMENTS: Final[tuple[str, ...]] = (
    "COMMENT ON TABLE {s}.pledge_event_version IS "
    "'质押等股权事件的版本载体（双时态）：一行=一条公告事件的一个版本；"
    "valid_from=公告生效时点，known_at=入库时点。建表目的=PQ-0072 时序违规归零（事件驱动版本推进）；"
    "只旁挂不覆写 public.edge_holding。'",
    "COMMENT ON COLUMN {s}.pledge_event_version.event_uid IS "
    "'主键=源行全列 sha256 内容指纹（源 CH 表无主键，实测窗内零全行重复）→ 重放回填天然幂等'",
    "COMMENT ON COLUMN {s}.pledge_event_version.valid_from IS "
    "'valid_time 轴起点：公告日（市场知道这件事的时点），PQ-0072 判据用的就是这根轴'",
    "COMMENT ON COLUMN {s}.pledge_event_version.valid_to IS "
    "'同 (归一股东名, 代码) 对的下一版本公告日；NULL=现行版本。按不同日闭合，故恒 > valid_from'",
    "COMMENT ON COLUMN {s}.pledge_event_version.known_at IS "
    "'transaction_time 轴=本载体落库时点（PG 服务器时钟）。源列 ingest_ts 实测为 DEFAULT now() 读时求值"
    "（全表仅 2 取值、最大值随查询时刻漂移），不承载知识到达语义，故不采用；"
    "因此历史某日能否看到某行由 valid_from 轴回答，本记录入仓前的一切历史回放不受本表影响'",
    "COMMENT ON COLUMN {s}.pledge_event_version.business_from IS "
    "'业务真实起点 pledge_start_date（可与公告日不同）；与 valid_from 分列即是为了说明「换口径无效」："
    "判据要的是知识时点，不是业务时点'",
    "COMMENT ON COLUMN {s}.pledge_event_version.holder_resolution IS "
    "'股东名→node_entity 解析结论：resolved 时 holder_entity_id 可信；unresolved 时 holder_entity_id 必为 NULL（禁编造实体）'",
    "COMMENT ON COLUMN {s}.pledge_event_version.business_span_inverted IS "
    "'源缺陷申报位：业务区间倒挂（pledge_end_date < pledge_start_date）时置 TRUE 且原值照留——"
    "既不静默改写也不静默丢弃；CHECK ck_business_span_declared 保证声明与数据逐行吻合'",
    "COMMENT ON COLUMN {s}.pledge_event_version.event_type IS "
    "'事件词表：pledge/pledge_release/pledge_extension/judicial_freeze。judicial_freeze 目前零行——冻结独立源表未建（案卷待裁项 T2）'",
)


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（I2：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 metaq_pledge 或 metaq_pledge_test_<后缀>，防 DDL 打偏到他人 schema）"
        )
    return schema


def ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL（I3：全幂等，可重放）。"""
    fmt = {"s": schema, "tz": BUSINESS_TZ}
    out: list[str] = [_SQL_CREATE_SCHEMA.format(s=schema)]
    out.append(_SQL_MAIN.format(**fmt))
    out.append(_SQL_RUNLOG.format(**fmt))
    out.extend(tpl.format(**fmt) for tpl in _SQL_INDEXES)
    out.append(_SQL_VIEW_CURRENT.format(**fmt))
    out.append(_SQL_VIEW_TIMELINE.format(**fmt))
    out.append(_SQL_FUNCTION.format(**fmt))
    out.extend(tpl.format(**fmt) for tpl in _COMMENTS)
    return out


def grant_statements(schema: str) -> list[str]:
    """角色分级授权（照 apply_meta_question_ddl / ai_intake 惯例）。"""
    return [tpl.format(s=schema) for tpl in _SQL_GRANTS]


# ---------- RULE-DATA-OPS 三步验证（破坏性/写操作前必打印，留痕进案卷） ----------
VERIFICATION_RECORD: Final[dict[str, str]] = {
    "necessity": (
        "PQ-0072 实测：事件 vs edge_holding 最新版本生效日时序违规 5,238/110,690=4.73%（判据阈值要求 0）；"
        "违规条目中 4,678 条在事件日之后该 (股东,公司) 对不存在任何持股版本行——版本链未随事件推进，"
        "改日期口径（pledge_start_date）后仍违规 2,775/110,690=2.51%≠0 → 只有「事件→版本」载体能落地该不变量。"
    ),
    "authenticity": (
        "源=CH c3_fundamental.equity_pledge_detail（实测 120,628 行，窗内 announce_date<=2025-09-09 且股东名非空 "
        "112,822 行/3,508 只/公告窗 2003-06-10~2025-09-09，全行零重复）；"
        "版本侧=PG public.edge_holding 1,500,341 行（其中 to_entity 为上市公司的 1,500,171 行）、"
        "public.node_entity 140,725 节点（name_norm 唯一，实测零同名多实体）——均为本轮探针实查，非引用二手结论。"
    ),
    "reversibility": (
        "只新建 schema metaq_pledge 下对象，零 DELETE/UPDATE/DROP/ALTER 既有业务表（代码级 assert_statement_safe 强断言）；"
        "回滚单条：DROP SCHEMA metaq_pledge CASCADE（仅本载体，删后 edge_holding/CH 源毫发无损）；"
        "行级回滚：TRUNCATE metaq_pledge.pledge_event_version（人工执行，脚本不自动跑）。"
    ),
}


def print_verification(target_schema: str, *, extra: dict[str, Any] | None = None) -> None:
    """写操作前的"必要性/真实性/可逆性"三验证打印（RULE-DATA-OPS）。"""
    print("=" * 72)
    print(f"RULE-DATA-OPS 三步验证（目标 schema={target_schema}）")
    for key in ("necessity", "authenticity", "reversibility"):
        print(f"  [{key}] {VERIFICATION_RECORD[key]}")
    for k, v in (extra or {}).items():
        print(f"  [{k}] {v}")
    print("=" * 72)


def _known_schemas(cur: Any) -> tuple[str, ...]:
    """取库内全部 schema 名（安全断言用：只有真实存在的 schema 才可能被误写）。"""
    cur.execute(_SQL_PG_SCHEMAS)
    return tuple(r[0] for r in cur.fetchall())


def deploy(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> dict[str, int]:
    """部署/刷新载体 schema（幂等）。返回各阶段执行计数。"""
    check_schema_name(schema)
    own_conn = conn is None
    if own_conn:
        # 新建 schema 需库级 CREATE 权限 → 走 superuser（与 apply_meta_question_ddl 同法），显式事务
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    counts = {"ddl": 0, "grant": 0}
    try:
        cur = conn.cursor()
        known = _known_schemas(cur)
        for stmt in ddl_statements(schema):
            assert_statement_safe(stmt, schema, known)
            cur.execute(stmt)
            counts["ddl"] += 1
        for stmt in grant_statements(schema):
            # GRANT 只能指向本载体对象（授权位不是写数据，但同样防打偏）
            for m in re.finditer(r"\b(?:ON|TO)\s+([a-z_][\w.]*)", stmt, re.IGNORECASE):
                obj = m.group(1)
                if "." not in obj:  # 角色名（depgraph_reader/writer）
                    continue
                if obj.split(".")[-2].lower() != schema.lower():
                    raise SafetyViolation(f"拒执行：GRANT 指向非目标 schema 对象 {obj}")
            # GRANT 失败（本地精简实例缺角色）只回滚该条，不撤销已建表
            cur.execute(_SQL_SAVEPOINT_GRANT)
            try:
                cur.execute(stmt)
                counts["grant"] += 1
                cur.execute(_SQL_RELEASE_GRANT)
            except Exception as exc:  # noqa: BLE001 ——授权缺失不阻断 DDL 主体，warning 留痕
                log.warning("GRANT 跳过：%s", exc)
                cur.execute(_SQL_ROLLBACK_GRANT)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()
    return counts


EXPECTED_TABLES: Final[tuple[str, ...]] = (_TABLE_MAIN, _TABLE_RUNLOG)
EXPECTED_INDEXES: Final[tuple[str, ...]] = tuple(
    re.search(r"EXISTS ([a-z0-9_]+) ON", tpl).group(1)
    for tpl in _SQL_INDEXES  # type: ignore[union-attr]
)
EXPECTED_VIEWS: Final[tuple[str, ...]] = _VIEWS
EXPECTED_FUNCTION: Final[str] = _FUNCTION


def verify(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> tuple[bool, list[str]]:
    """核对表/索引/视图/函数是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    check_schema_name(schema)
    own_conn = conn is None
    if own_conn:
        conn = get_depgraph_pg_connection(read_only=True)
    missing: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(_SQL_PG_TABLES, (schema,))
        found = {r[0] for r in cur.fetchall()}
        missing += [f"table:{t}" for t in EXPECTED_TABLES if t not in found]
        cur.execute(_SQL_PG_INDEXES, (schema,))
        found = {r[0] for r in cur.fetchall()}
        missing += [f"index:{i}" for i in EXPECTED_INDEXES if i not in found]
        cur.execute(_SQL_PG_VIEWS, (schema,))
        found = {r[0] for r in cur.fetchall()}
        missing += [f"view:{v}" for v in EXPECTED_VIEWS if v not in found]
        cur.execute(_SQL_PG_PROCS, (schema,))
        found = {r[0] for r in cur.fetchall()}
        if EXPECTED_FUNCTION not in found:
            missing.append(f"function:{EXPECTED_FUNCTION}")
        # 列级时区不变量实核：TIMESTAMPTZ 才算过（RULE-SCHEMA-TZ）
        cur.execute(_SQL_PG_TZ_COLUMNS, (schema, _TABLE_MAIN))
        for col, dtype in cur.fetchall():
            if "timestamp with time zone" not in dtype:
                missing.append(f"tz:{col}={dtype}")
    finally:
        if own_conn:
            conn.close()
    return (not missing), missing


def drop_test_schema(schema: str) -> None:
    """删除演练残留 schema（仅 metaq_pledge_test_ 前缀；生产 schema 永不删）。"""
    if not schema.startswith(TEST_SCHEMA_PREFIX):
        raise ValueError(f"拒删非测试 schema：{schema!r}")
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        cur = conn.cursor()
        stmt = _SQL_DROP_SCHEMA.format(s=schema)
        m = re.search(r"DROP SCHEMA IF EXISTS (\w+)", stmt)
        assert m is not None
        if m.group(1) != schema:  # 双保险：DROP 目标必须逐字等于校验过的 schema 名
            raise SafetyViolation(f"DROP 目标 {m.group(1)} 与已校验 schema {schema} 不一致")
        cur.execute(stmt)
    finally:
        conn.close()


# 本部署器自有的关系（唯一允许被 rebuild 复建的对象；均为本单新建，非既有业务表）
_OWN_RELATIONS: Final[tuple[str, ...]] = (_TABLE_MAIN, _TABLE_RUNLOG, *_VIEWS, _FUNCTION)


def rebuild_carrier(schema: str) -> list[str]:
    """维护通道：复建本单自有载体对象（结构换版时用，如新增 business_span_inverted 列）。

    与 ``assert_statement_safe`` 的关系说明：该断言守的是"零触碰**既有业务表**"红线；
    这里 DROP 的是本部署器自己新建、且内容 100% 可由 CH 源重放的两张表——
    自我约束三重：①schema 必须过白名单；②DROP 目标名必须逐字属于 ``_OWN_RELATIONS``；
    ③必须 --yes 显式确认并先打印三步验证。public.* 在此路径下同样不可能被触及。
    """
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    done: list[str] = []
    try:
        cur = conn.cursor()
        for rel in reversed(_OWN_RELATIONS):
            if rel == _FUNCTION:
                kind, tail = "FUNCTION", "(text, date, timestamptz)"  # 带签名：PG 要求重载消歧
            elif rel.startswith("v_"):
                kind, tail = "VIEW", ""
            else:
                kind, tail = "TABLE", ""
            stmt = _SQL_DROP_OWN.format(kind=kind, s=schema, rel=rel, tail=tail)
            m = re.search(r"IF EXISTS ([\w.]+)", stmt)
            assert m is not None
            obj_schema, _, obj_name = m.group(1).partition(".")
            if obj_schema != schema or obj_name not in _OWN_RELATIONS:
                raise SafetyViolation(f"拒执行：rebuild 目标 {m.group(1)} 不属本单自有对象清单")
            cur.execute(stmt)
            done.append(m.group(1))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return done


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署 / 核对 / 清理演练 schema。"""
    parser = argparse.ArgumentParser(description="WO-009 质押事件版本载体 DDL 部署器（幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 metaq_pledge）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    parser.add_argument("--drop-test-schema", action="store_true", help="删除演练 schema（仅 _test_ 前缀）")
    parser.add_argument(
        "--rebuild-carrier",
        action="store_true",
        help="结构换版：先 DROP 本单自有对象（不含任何既有业务表）再按新结构重建",
    )
    parser.add_argument("--yes", action="store_true", help="确认执行写操作（先打印三步验证）")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        check_schema_name(args.schema)
        if args.drop_test_schema:
            print_verification(args.schema, extra={"action": "drop_test_schema（仅演练 schema）"})
            if not args.yes:
                print("REFUSED: 未传 --yes，拒绝执行")
                return 2
            drop_test_schema(args.schema)
            print(f"DROPPED test schema {args.schema}")
            return 0
        if args.verify:
            ok, missing = verify(args.schema)
            print(f"VERIFY {args.schema}: {'OK' if ok else 'MISSING ' + ','.join(missing)}")
            return 0 if ok else 3
        print_verification(args.schema, extra={"action": "deploy DDL（新建 schema 下对象，幂等）"})
        if not args.yes:
            print("REFUSED: 未传 --yes，拒绝执行")
            return 2
        if args.rebuild_carrier:
            print(f"REBUILD dropped own objects: {rebuild_carrier(args.schema)}")
        counts = deploy(args.schema)
        ok, missing = verify(args.schema)
        print(f"DEPLOYED {args.schema} {counts} verify={'OK' if ok else missing}")
        return 0 if ok else 3
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except SafetyViolation as exc:
        print(f"BLOCKED-BY-SAFETY: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:  # noqa: BLE001 ——CLI 边界统一转退出码 2
        print(f"DDL FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
