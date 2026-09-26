# [BLUEPRINT] MOD-METAQ-WO009 | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md | §WO-009（质押事件版本载体回填）
# [MODULE] scripts.governance.meta_question.wo009.backfill_pledge_event_version
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection 读写);
#                zephyr.infrastructure.database_service (CH reader 只读源); zephyr.data.table_registry（表名品类真源 #ARCH-CH-024）;
#                scripts.governance.meta_question.wo009.apply_pledge_event_version_ddl（schema 白名单/三步验证复用）;
#                psycopg2.extras.execute_values
# [CONSUMERS] metaq_pledge.pledge_event_version（唯一写入者）; scripts/governance/meta_question/wo009/recheck_pq0072_violation.py（复算前置）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] B1 源=CH c3_fundamental.equity_pledge_detail 只读，写侧只碰 metaq_pledge 自己的表（无 DELETE/TRUNCATE/ALTER 能力）;
#              B2 幂等：event_uid = 源行全列 sha256 内容指纹，插入一律 ON CONFLICT DO UPDATE（重跑=自愈，不产生第二行）;
#              B3 分片=月（shard_key='YYYY-MM'），断点账本 metaq_pledge.backfill_run_log 是续跑唯一真源（源行数吻合才判 done）;
#              B4 时间：known_at 由 PG DEFAULT now() 定值（实测源列 ingest_ts=DEFAULT now() 读时求值、全表仅 2 取值
#                 且最大值随查询时刻漂移 → 不承载知识到达语义，弃用；本脚本全程禁 datetime.now()/time.time()，
#                 RULE-SCHEMA-TZ）；valid_from=announce_date；1970 哨兵业务日期一律置 NULL 并计数，不猜测真实日期;
#              B5 股东实体解析只在 name_norm 唯一命中时写 holder_entity_id，未命中必 NULL（反幻觉，禁编造实体）;
#              B6 版本链闭合按"同 (归一股东名, 代码) 对的不同公告日"计算 → 恒满足 CHECK valid_to > valid_from；
#                 闭合语句只 UPDATE 本载体表，每次全量重算（幂等，不依赖上次结果）;
#              B7 回填窗口默认严格 ≤ PIT 闭卷切点 2025-09-09（防切点后版本反向洗白窗内违规）。
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] schema 不合规/未建表->拒跑码 2; 单片写失败->该片不记账（下次自动重跑）+码 2;
#                  CH 源行数与 PG 落库行数不吻合->汇总非零退出（fail-visible）; --resume 时全部片 done->直接进闭合+统计并退出 0
# [TESTS] 演练路径：--schema metaq_pledge_test_wo009 --only-shard 2019-03 --dry-run/--only-shard 真写 → 复核行数后清理
# [A_module] module_id=MOD-METAQ-WO009-BACKFILL | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-009：质押公告事件 → ``metaq_pledge.pledge_event_version`` 回填（分片 / 断点续跑 / 幂等）。

规模：CH 源窗内（``announce_date <= 2025-09-09`` 且股东名非空）112,822 行 → 载体 112,822 版本行。

用法::

    python .../backfill_pledge_event_version.py --schema metaq_pledge_test_wo009 --only-shard 2019-03   # 演练单片
    python .../backfill_pledge_event_version.py --yes                                                # 全量（续跑同命令）
    python .../backfill_run_log 查询：SELECT * FROM metaq_pledge.backfill_run_log ORDER BY shard_key;
    python .../backfill_pledge_event_version.py --close-chain-only                                   # 只重算版本链
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

import psycopg2.extras

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_pledge_event_version_ddl import (  # noqa: E402
    VERIFICATION_RECORD,
    SafetyViolation,
    check_schema_name,
    print_verification,
)

from zephyr.data.table_registry import get_registry  # noqa: E402  （表名品类真源 #ARCH-CH-024）
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402

DEFAULT_END = "2025-09-09"  # PIT 闭卷切点（B7）
DEFAULT_START = "1990-01-01"
SQL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SENTINEL_YEAR = 1990  # 源里 1970-01-01 = 缺失哨兵（B4）

# 源列清单（真源=CH DESCRIBE 实测，顺序即指纹顺序，改动即换指纹命名空间）
SRC_COLUMNS = (
    "symbol",
    "exchange",
    "symbol_canonical",
    "announce_date",
    "shareholder_name",
    "shareholder_type",
    "pledge_shares",
    "pledge_start_date",
    "pledge_end_date",
    "is_released",
    "release_date",
    "pledgee",
    "total_holdings",
    "total_pledged",
    "pledge_ratio",
    "holding_ratio",
    "is_buyback",
    "remark",
    "data_source",
    "quality_flag",
)
# NO-BARE-SQL：SQL 集中于此（§5.160.2）。取数窗 {start}/{end} 由 fetch_source 注入
# （禁在此写死 PIT 日期）；源列清单经 _SQL_SOURCE_COLS 单次拼接，避免两级 format 占位混用；
# PG 写侧继续用 %s / VALUES %s（execute_values 批量槽），{s} 承载 schema
# —— 渲染文本与提取前逐字等值（\n 与缩进即原三引号形态）。CH 源表名经品类册派生（#ARCH-CH-024），
# SQL 常量以 f-string 注入 ⇒ 真源唯一、渲染值与旧字面量逐字相同。
_SQL_SOURCE_COLS = ", ".join(SRC_COLUMNS)
_CH_SOURCE_TABLE = get_registry().table("fund_equity_pledge_detail")  # 源表真源（品类册）
_SQL_SELECT_SOURCE = (
    "\nSELECT " + _SQL_SOURCE_COLS + "\n"
    f"FROM {_CH_SOURCE_TABLE}\n"
    "WHERE announce_date >= toDate('{start}') AND announce_date <= toDate('{end}')\n"
    "  AND shareholder_name != ''\n"
    "ORDER BY announce_date, symbol_canonical, shareholder_name, pledge_shares, pledgee\n"
)

INSERT_COLS = (
    "event_uid",
    "source_ref",
    "source_row_no",
    "backfill_run_id",
    "symbol",
    "symbol_canonical",
    "exchange",
    "company_entity_id",
    "holder_name",
    "holder_name_norm",
    "holder_entity_id",
    "holder_kind",
    "holder_type_src",
    "holder_resolution",
    "event_type",
    "event_date_basis",
    "valid_from",
    "valid_to",
    "is_current",
    "business_from",
    "business_to",
    "business_span_inverted",
    "release_date",
    "is_released",
    "pledgee",
    "pledge_shares",
    "total_holdings",
    "total_pledged",
    "pledge_ratio",
    "holding_ratio",
    "is_buyback",
    "remark",
    "src_data_source",
    "src_quality_flag",
)
# 冲突时覆写源值（自愈）；valid_to / is_current 由闭合语句独占，不在覆写清单内
_UPDATE_COLS = tuple(c for c in INSERT_COLS if c not in ("event_uid", "valid_to", "is_current"))
_SQL_INSERT_VERSION = (
    "INSERT INTO {s}.pledge_event_version ("
    + ", ".join(INSERT_COLS)
    + ") VALUES %s ON CONFLICT (event_uid) DO UPDATE SET "
    + ", ".join(f"{c} = EXCLUDED.{c}" for c in _UPDATE_COLS)
    + ", recorded_at = now()"
)

# 版本链闭合（B6）：按"同对不同公告日"取下一日 → valid_to；最后一日 = 现行版本
_SQL_CLOSE_CHAIN = """
WITH d AS (
    SELECT DISTINCT holder_name_norm, symbol, valid_from
    FROM {s}.pledge_event_version
),
dd AS (
    SELECT holder_name_norm, symbol, valid_from,
           lead(valid_from) OVER (
               PARTITION BY holder_name_norm, symbol ORDER BY valid_from
           ) AS next_from
    FROM d
)
UPDATE {s}.pledge_event_version p
SET valid_to = dd.next_from,
    is_current = (dd.next_from IS NULL)
FROM dd
WHERE p.holder_name_norm = dd.holder_name_norm
  AND p.symbol = dd.symbol
  AND p.valid_from = dd.valid_from
  AND (p.valid_to IS DISTINCT FROM dd.next_from OR p.is_current IS DISTINCT FROM (dd.next_from IS NULL))
"""

_SQL_RUN_LOG_UPSERT = """
INSERT INTO {s}.backfill_run_log (shard_key, rows_source, rows_written, status, run_id, finished_at)
VALUES %s
ON CONFLICT (shard_key) DO UPDATE SET
    rows_source = EXCLUDED.rows_source, rows_written = EXCLUDED.rows_written,
    status = EXCLUDED.status, run_id = EXCLUDED.run_id, finished_at = EXCLUDED.finished_at
"""

# 只读探针（断点账本/落库行数核对）
_SQL_TO_REGCLASS = "SELECT to_regclass('{t}')"
_SQL_SHARD_DONE = "SELECT shard_key, rows_source, status FROM {s}.backfill_run_log"
_SQL_SHARD_LOG = "SELECT shard_key, rows_source, rows_written, status FROM {s}.backfill_run_log ORDER BY 1"
_SQL_HOLDER_INDEX = "SELECT name_norm, entity_id, entity_type FROM public.node_entity"
_SQL_STATS_AGG = """
        SELECT count(*)                                   AS total_rows,
               count(DISTINCT symbol)                     AS distinct_symbols,
               count(DISTINCT (holder_name_norm, symbol)) AS distinct_pairs,
               min(valid_from)                            AS min_valid_from,
               max(valid_from)                            AS max_valid_from,
               count(DISTINCT holder_entity_id)           AS distinct_holder_entities,
               count(*) FILTER (WHERE is_current)         AS current_versions,
               count(*) FILTER (WHERE business_from IS NULL) AS business_from_null,
               count(*) FILTER (WHERE business_span_inverted) AS business_span_inverted_rows,
               min(known_at)                              AS min_known_at,
               max(known_at)                              AS max_known_at
        FROM {s}.pledge_event_version"""
_SQL_EVENT_TYPE_MIX = "SELECT event_type, count(*) FROM {s}.pledge_event_version GROUP BY 1 ORDER BY 2 DESC"
_SQL_RESOLUTION_MIX = "SELECT holder_resolution, count(*) FROM {s}.pledge_event_version GROUP BY 1"
_SQL_COMPANY_MISSING_TOP = (
    "SELECT company_entity_id, count(*) FROM {s}.pledge_event_version p "
    "WHERE NOT EXISTS (SELECT 1 FROM public.node_entity n "
    "WHERE n.entity_id = p.company_entity_id) "
    "GROUP BY 1 ORDER BY 2 DESC LIMIT 5"
)
_SQL_COMPANY_MISSING_ROWS = """SELECT count(*) FROM {s}.pledge_event_version p WHERE NOT EXISTS
        (SELECT 1 FROM public.node_entity n WHERE n.entity_id = p.company_entity_id)"""
_SQL_SOURCE_ROWS_WINDOW = (
    f"SELECT count() FROM {_CH_SOURCE_TABLE} "
    "WHERE announce_date >= toDate('{start}') AND announce_date <= toDate('{end}') "
    "AND shareholder_name != ''"
)


def norm_name(s: object) -> str:
    """股东名归一（与 PQ-0072 判据同一函数：仅去空白，不做别名合并——保持判据可比）。"""
    return re.sub(r"\s+", "", str(s or ""))


def _d(v: object) -> dt.date | None:
    """日期规范化：None / 1970 哨兵 → NULL（B4）。"""
    if v is None:
        return None
    if isinstance(v, dt.datetime):
        v = v.date()
    if isinstance(v, dt.date):
        return None if v.year < SENTINEL_YEAR else v
    s = str(v)[:10]
    try:
        got = dt.date.fromisoformat(s)
    except ValueError:
        return None
    return None if got.year < SENTINEL_YEAR else got


def event_uid(row: dict[str, object]) -> str:
    """源行全列内容指纹（源表无主键；实测窗内零全行重复 → 指纹唯一即主键安全）。"""
    parts = []
    for c in SRC_COLUMNS:
        v = row.get(c)
        if isinstance(v, dt.datetime) or isinstance(v, dt.date):
            v = v.isoformat()
        parts.append("∅" if v is None else str(v))
    return "sha256:" + hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def classify(row: dict[str, object]) -> str:
    """事件类型派生（词表与 DDL CHECK 一致；链按对不按类型分区，故派生误判不产生版本缝隙）。"""
    remark = str(row.get("remark") or "")
    rel_date = _d(row.get("release_date"))
    ad = _d(row.get("announce_date"))
    if row.get("is_released") and rel_date and ad and rel_date == ad:
        return "pledge_release"
    if "展期" in remark or "购回" in remark:
        return "pledge_extension"
    return "pledge"


def load_holder_index(cur: object) -> dict[str, tuple[str, str]]:
    """name_norm → (entity_id, entity_type)。实测 node_entity.name_norm 唯一（零同名多实体）。"""
    cur.execute(_SQL_HOLDER_INDEX)
    out: dict[str, tuple[str, str]] = {}
    for name_norm, entity_id, entity_type in cur.fetchall():
        key = str(name_norm or "")
        if key:
            out.setdefault(key, (str(entity_id), str(entity_type)))
    return out


def business_inverted(b_from: dt.date | None, b_to: dt.date | None) -> bool:
    """源缺陷申报（B4 的孪生）：业务区间倒挂照实打标，原值不改写、行不丢弃。"""
    return bool(b_from and b_to and b_to < b_from)


def transform(row: dict[str, object], holder_index: dict[str, tuple[str, str]], run_id: str) -> tuple:
    uid = event_uid(row)
    name_norm = norm_name(row.get("shareholder_name"))
    hit = holder_index.get(name_norm)
    canonical = str(row.get("symbol_canonical") or f"{row.get('symbol')}.{row.get('exchange')}")
    b_from = _d(row.get("pledge_start_date"))
    b_to = _d(row.get("pledge_end_date"))
    return (
        uid,
        f"ch:{_CH_SOURCE_TABLE}#{uid}",
        0,
        run_id,
        str(row.get("symbol")),
        canonical,
        str(row.get("exchange")),
        f"CO:{canonical}",
        str(row.get("shareholder_name")),
        name_norm,
        hit[0] if hit else None,
        hit[1] if hit else None,
        str(row.get("shareholder_type") or ""),
        "resolved" if hit else "unresolved",
        classify(row),
        "announce_date",
        _d(row.get("announce_date")),
        None,  # valid_to：闭合语句负责
        False,  # is_current：闭合语句负责
        b_from,
        b_to,
        business_inverted(b_from, b_to),
        _d(row.get("release_date")),
        row.get("is_released"),
        str(row.get("pledgee") or ""),
        row.get("pledge_shares"),
        row.get("total_holdings"),
        row.get("total_pledged"),
        row.get("pledge_ratio"),
        row.get("holding_ratio"),
        row.get("is_buyback"),
        str(row.get("remark") or ""),
        str(row.get("data_source") or ""),
        row.get("quality_flag"),
    )


def shard_key_of(row: dict[str, object]) -> str:
    ad = _d(row.get("announce_date"))
    return ad.strftime("%Y-%m") if ad else "unknown"


def fetch_source(ch: object, start: str, end: str) -> list[dict[str, object]]:
    sql = _SQL_SELECT_SOURCE.format(start=start, end=end)
    rows = ch.execute(sql)
    return [dict(zip(SRC_COLUMNS, r, strict=True)) for r in rows]


def close_chain(schema: str, conn: object) -> int:
    cur = conn.cursor()
    cur.execute(_SQL_CLOSE_CHAIN.format(s=schema))
    n = cur.rowcount
    conn.commit()
    return n


def collect_stats(schema: str, conn: object) -> dict[str, object]:
    cur = conn.cursor()
    cur.execute(_SQL_STATS_AGG.format(s=schema))
    cols = [d[0] for d in cur.description]
    stats: dict[str, object] = dict(zip(cols, cur.fetchone(), strict=True))
    cur.execute(_SQL_EVENT_TYPE_MIX.format(s=schema))
    stats["event_type_mix"] = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute(_SQL_RESOLUTION_MIX.format(s=schema))
    stats["holder_resolution"] = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute(_SQL_COMPANY_MISSING_TOP.format(s=schema))
    stats["company_entity_missing_top"] = [[r[0], r[1]] for r in cur.fetchall()]
    cur.execute(_SQL_COMPANY_MISSING_ROWS.format(s=schema))
    stats["company_entity_missing_rows"] = cur.fetchone()[0]
    cur.execute(_SQL_SHARD_LOG.format(s=schema))
    stats["shards"] = [{"shard": r[0], "src": r[1], "written": r[2], "status": r[3]} for r in cur.fetchall()]
    return stats


def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="WO-009 质押事件版本回填（分片/续跑/幂等）")
    ap.add_argument("--schema", default="metaq_pledge")
    ap.add_argument("--start", default=DEFAULT_START, help="回填窗起（含）")
    ap.add_argument("--end", default=DEFAULT_END, help="回填窗止（含），默认 PIT 闭卷切点")
    ap.add_argument("--page-size", type=int, default=2000)
    ap.add_argument("--only-shard", default="", help="只跑某一片（如 2019-03，演练/补洞用）")
    ap.add_argument("--close-chain-only", action="store_true", help="不回填，只重算版本链")
    ap.add_argument("--stats-only", action="store_true", help="不写，只出统计")
    ap.add_argument("--dry-run", action="store_true", help="只读源+转换，不写库")
    ap.add_argument("--yes", action="store_true", help="确认写库（先打印三步验证）")
    ap.add_argument("--run-id", default="", help="本次运行标识（缺省自动生成，不取时钟）")
    return ap


def _validate_window(args: argparse.Namespace) -> str | None:
    """回填窗与 schema 合法性校验；返回错误文案（None=通过）。"""
    for tag, val in (("start", args.start), ("end", args.end)):
        if not SQL_DATE_RE.match(val):
            return f"{tag} 非 ISO 日期：{val!r}"
    try:
        check_schema_name(args.schema)
    except ValueError as exc:
        return str(exc)
    return None


def _run_stats_only(args: argparse.Namespace) -> int:
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(_SQL_TO_REGCLASS.format(t=f"{args.schema}.pledge_event_version"))
    if cur.fetchone()[0] is None:
        print(f"REFUSED: {args.schema}.pledge_event_version 不存在（先跑 DDL）", file=sys.stderr)
        conn.close()
        return 2
    stats = collect_stats(args.schema, conn)
    conn.close()
    print(json.dumps(stats, ensure_ascii=False, indent=1, default=str))
    return 0


def _print_run_verification(args: argparse.Namespace, run_id: str) -> int:
    if args.dry_run or args.yes:
        print_verification(
            args.schema,
            extra={
                "action": "回填 pledge_event_version（INSERT ON CONFLICT DO UPDATE + 版本链闭合）",
                "run_id": run_id,
                "window": f"{args.start}..{args.end}",
                "delete_update_drop_on_existing_business_tables": "无（B1：只写本载体表；无 DELETE/TRUNCATE/ALTER 路径）",
            },
        )
        return 0
    print("REFUSED: 未传 --yes（且 --dry-run 亦未传），拒绝写库", file=sys.stderr)
    return 2


def _fetch_and_shard(
    ch: Any, args: argparse.Namespace
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    rows = fetch_source(ch, args.start, args.end)
    shards: dict[str, list[dict[str, object]]] = {}
    for r in rows:
        shards.setdefault(shard_key_of(r), []).append(r)
    print(f"SOURCE rows={len(rows)} shards={len(shards)} window={args.start}..{args.end}")
    return rows, shards


def _dry_run_sample(args: argparse.Namespace, rows: list[dict[str, object]], run_id: str) -> int:
    sample = rows[:2]
    print("DRY-RUN transformed sample:")
    conn_ro = get_depgraph_pg_connection(read_only=True)
    hi = load_holder_index(conn_ro.cursor())
    conn_ro.close()
    for r in sample:
        print(
            json.dumps(dict(zip(INSERT_COLS, transform(r, hi, run_id), strict=True)), ensure_ascii=False, default=str)[
                :900
            ]
        )
    return 0


def _write_one_shard(
    args: argparse.Namespace,
    conn: Any,
    key: str,
    bucket: list[dict[str, object]],
    resume_state: tuple[dict[str, tuple], Any],
    run_id: str,
) -> tuple[int, int, tuple]:
    """写单片；返回 (written, skipped, log_item)。"""
    done, holder_index = resume_state
    cur = conn.cursor()
    if args.only_shard and key != args.only_shard:
        return 0, 0, ()
    if key in done and done[key][0] == len(bucket) and not args.only_shard:
        return 0, len(bucket), (key, len(bucket), done[key][0], "done", run_id, None)
    payload = [transform(r, holder_index, run_id) for r in bucket]
    for i in range(0, len(payload), args.page_size):
        psycopg2.extras.execute_values(
            cur,
            _SQL_INSERT_VERSION.format(s=args.schema),
            payload[i : i + args.page_size],
            template="(" + ",".join(["%s"] * len(INSERT_COLS)) + ")",
            page_size=args.page_size,
        )
    conn.commit()  # 片级提交=断点粒度（B3）
    print(f"  shard {key}: src={len(bucket)} written={len(payload)}")
    return len(payload), 0, (key, len(bucket), len(payload), "done", run_id, None)


def _exec_write_phase(
    args: argparse.Namespace, shards: dict[str, list[dict[str, object]]], run_id: str
) -> tuple[dict[str, object] | None, dict[str, int], int]:
    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
        cur = conn.cursor()
        cur.execute(_SQL_TO_REGCLASS.format(t=f"{args.schema}.pledge_event_version"))
        if cur.fetchone()[0] is None:
            print(
                f"REFUSED: 目标表不存在，先跑 apply_pledge_event_version_ddl.py --schema {args.schema}", file=sys.stderr
            )
            return None, {}, 2
        cur.execute(_SQL_SHARD_DONE.format(s=args.schema))
        done = {r[0]: (r[1], r[2]) for r in cur.fetchall() if r[2] == "done"}
        holder_index = load_holder_index(cur)
        if args.close_chain_only:
            print(f"CHAIN closed rows={close_chain(args.schema, conn)}")
            return None, {}, 0
        log_items: list[tuple] = []
        written_total = skipped = 0
        for key in sorted(shards):
            written, skip, item = _write_one_shard(args, conn, key, shards[key], (done, holder_index), run_id)
            written_total += written
            skipped += skip
            if item:
                log_items.append(item)
        if log_items and not args.only_shard:
            psycopg2.extras.execute_values(
                cur,
                _SQL_RUN_LOG_UPSERT.format(s=args.schema),
                log_items,
                template="(" + ",".join(["%s"] * 6) + ")",
                page_size=200,
            )
            conn.commit()
        elif args.only_shard:
            conn.rollback()  # 演练单片不污染断点账本（重跑仍安全）
        closed = close_chain(args.schema, conn)
        stats = collect_stats(args.schema, conn)
        acc = {"written_total": written_total, "skipped": skipped, "closed": closed}
        return stats, acc, 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _finalize_stats(
    args: argparse.Namespace,
    ch: Any,
    stats: dict[str, object],
    run_id: str,
    acc: dict[str, int],
    shards: dict[str, list[dict[str, object]]],
) -> int:
    stats["run_id"] = run_id
    stats["written_this_run"] = acc["written_total"]
    stats["skipped_resumed"] = acc["skipped"]
    stats["chain_closed_rows_touched"] = acc["closed"]
    print(json.dumps({k: v for k, v in stats.items() if k != "shards"}, ensure_ascii=False, indent=1, default=str))
    out = REPO / ".runtime" / "tmp" / "st-metaq-gc-20260924" / "wo009" / "backfill_stats.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    src_n = ch.execute(_SQL_SOURCE_ROWS_WINDOW.format(start=args.start, end=args.end))[0][0]
    stats["source_rows_in_window"] = src_n
    if args.only_shard:
        print(
            f"REHEARSAL（单片 {args.only_shard}）：本片 src={len(shards.get(args.only_shard, []))} "
            f"carrier_total={stats['total_rows']}（全窗行数核对仅整窗跑时判定）"
        )
        return 0
    ok = src_n == stats["total_rows"]
    print(f"SOURCE-vs-CARRIER rows: src={src_n} carrier={stats['total_rows']} -> {'MATCH' if ok else 'MISMATCH'}")
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    err = _validate_window(args)
    if err:
        print(f"REFUSED: {err}", file=sys.stderr)
        return 2
    run_id = args.run_id or f"wo009-{uuid.uuid4().hex[:12]}"

    svc = DatabaseService()
    ch = svc.get_clickhouse_conn(role="reader")

    if args.stats_only:
        return _run_stats_only(args)

    rc = _print_run_verification(args, run_id)
    if rc:
        return rc

    rows, shards = _fetch_and_shard(ch, args)
    if args.dry_run:
        return _dry_run_sample(args, rows, run_id)

    stats, acc, rc = _exec_write_phase(args, shards, run_id)
    if stats is None:
        return rc
    return _finalize_stats(args, ch, stats, run_id, acc, shards)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SafetyViolation as exc:
        print(f"BLOCKED-BY-SAFETY: {exc}", file=sys.stderr)
        sys.exit(4)
