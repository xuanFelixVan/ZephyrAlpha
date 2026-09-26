# [BLUEPRINT] MOD-METAQ-WO009 | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md | §WO-009（PQ-0072 判据复算）
# [MODULE] scripts.governance.meta_question.wo009.recheck_pq0072_violation
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection 只读);
#                zephyr.data.table_registry（表名品类真源 #ARCH-CH-024）; zephyr.infrastructure.database_service (CH reader); scripts.governance.meta_question.wo009.backfill_pledge_event_version（同源归一/指纹函数）
# [CONSUMERS] docs/_working/meta_question_answers/build/WO-009.yaml（案卷数字真源）; PQ-0072 复考
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] R1 判据零放宽：事件侧集合、归一函数、版本"最新生效日"取法、比较算子全部照抄考试探针
#                （.runtime/tmp/st-metaq-20260923/probes/l2_q0072.py + results/b2/PQ-0072.yaml 的 three_check.caliber），
#                只把版本集从 {edge_holding} 扩到 {edge_holding ∪ 载体}——事件集与违规算子一字不动；
#              R2 必带回归自证：先复现考试基线 5,238/110,690=4.73%，复现不出即判"判据漂移"直接非零退出（防换了把尺子量）；
#              R3 载体侧行必须 valid_from <= 切点 2025-09-09，否则拒绝参与比较（防切点后版本洗白窗内违规）；
#              R4 除违规数外另跑 7 项载体完整性断言（行数吻合/指纹可重算/链无重叠无缝/因果/命中率/解析诚实/可回溯）；
#              R5 只读脚本：不开写连接（read_only=True），任何写操作在本文件里不可能发生。
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 基线不复现->退出码 5（判据漂移，禁直接采信"归零"）; 载体缺表/空表->退出码 3;
#                  完整性断言任一失败->汇总打印后退出码 4; PG/CH 不可达->退出码 2
# [TESTS] 本单内自证：基线复现=5,238（与 results/b2/PQ-0072.yaml 记录逐位相符）；输出 JSON 落 .runtime/tmp/…/wo009/
# [A_module] module_id=MOD-METAQ-WO009-RECHECK | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-009：PQ-0072 时序违规判据复算（回填后验收尺子，只读）。

判据精确复述（照考试登记，未做任何放宽）：
  事件侧  CH c3_fundamental.equity_pledge_detail，``announce_date <= 2025-09-09`` 且 ``shareholder_name != ''``
  版本侧  R2 起为 (股东名去空白归一, 6 位代码) → ``max(valid_from)``；
          基线版本集 = public.edge_holding（``to_entity ~ '^CO:[0-9]{6}\\.(SH|SZ|BJ)$'``）；
          复算版本集 = 上集 ∪ metaq_pledge.pledge_event_version（同键，valid_from <= 切点）
  匹配    事件归一股东名 == 版本归一股东名 且 同代码（考试用 6 位代码 join：edge_holding.to_entity 去后缀）
  违规    ``str(announce_date) > str(max_valid_from)``
  阈值    违规样本 = 0

用法::

    python .../recheck_pq0072_violation.py                 # 全量复算 + 完整性断言
    python .../recheck_pq0072_violation.py --schema metaq_pledge_test_wo009   # 演练载体（只比命中率，不判验收）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_pledge_event_version_ddl import check_schema_name  # noqa: E402
from backfill_pledge_event_version import (  # noqa: E402  与回填共用同一归一/指纹实现，杜绝两套尺子
    SRC_COLUMNS,
    _d,
    event_uid,
    norm_name,
)

from zephyr.data.table_registry import get_registry  # noqa: E402  （表名品类真源 #ARCH-CH-024）
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402

CUT = "2025-09-09"
BASELINE_EXPECT = {"matched": 110690, "violations": 5238}  # results/b2/PQ-0072.yaml 登记值
EDGE_RE = re.compile(r"^CO:[0-9]{6}\.(SH|SZ|BJ)$")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{s} 承载 schema、{cols} 承载列清单、{cut} 承载
# 闭卷切点（由调用点注入，禁在此写死日期）；PG 参数继续走 %s 绑定。判据文本与提取前逐字等值。
# CH 源表名经品类册派生（#ARCH-CH-024），SQL 常量以 f-string 注入并把 {s}/{cols} 双写转义 ⇒
# 渲染值与旧字面量逐字相同、真源唯一。
_CH_SOURCE_TABLE = get_registry().table("fund_equity_pledge_detail")  # 源表真源（品类册）
_SQL_EDGE_VERSIONS = r"""
SELECT from_entity, to_entity, valid_from
FROM public.edge_holding WHERE to_entity ~ '^CO:[0-9]{6}\.(SH|SZ|BJ)$'
"""
_SQL_NODE_ENTITY_NAMES = "SELECT entity_id, name FROM public.node_entity"
_SQL_CARRIER_VERSIONS = (
    "SELECT holder_name_norm, symbol, valid_from FROM {s}.pledge_event_version WHERE valid_from <= %s"
)
_SQL_CARRIER_TRIPLES = "SELECT holder_name_norm, symbol, valid_from FROM {s}.pledge_event_version"
_SQL_CARRIER_KEYS = "SELECT DISTINCT holder_name_norm, symbol, valid_from FROM {s}.pledge_event_version"
_SQL_CARRIER_COUNT = "SELECT count(*) FROM {s}.pledge_event_version"
_SQL_CARRIER_UIDS = "SELECT event_uid FROM {s}.pledge_event_version"
_SQL_CARRIER_SAMPLE = "SELECT event_uid, {cols} FROM {s}.pledge_event_version WHERE event_uid = ANY(%s)"
_SQL_TO_REGCLASS = "SELECT to_regclass('{t}')"
_SQL_SOURCE_ROWS_WINDOW = (
    f"SELECT {{cols}} FROM {_CH_SOURCE_TABLE} WHERE announce_date <= toDate('{{cut}}') AND shareholder_name != ''"
)
_SQL_EVENTS_WINDOW = (
    f"SELECT symbol, announce_date, shareholder_name FROM {_CH_SOURCE_TABLE} "
    "WHERE announce_date <= toDate('{cut}') AND shareholder_name != '' "
    "ORDER BY announce_date, symbol, shareholder_name"
)
_SQL_SRC_EVENT_COUNT = (
    f"SELECT count() FROM {_CH_SOURCE_TABLE} WHERE announce_date <= toDate('{{cut}}') AND shareholder_name != ''"
)
_SQL_I3_CHAIN = """
        WITH x AS (
            SELECT holder_name_norm, symbol, valid_from, valid_to, is_current,
                   lag(valid_to)  OVER (PARTITION BY holder_name_norm, symbol ORDER BY valid_from) prev_to,
                   max(valid_from) OVER (PARTITION BY holder_name_norm, symbol) mx
            FROM (SELECT DISTINCT holder_name_norm, symbol, valid_from, valid_to, is_current
                  FROM {s}.pledge_event_version) d
        )
        SELECT count(*) FILTER (WHERE valid_to IS NOT NULL AND valid_to <= valid_from),
               count(*) FILTER (WHERE prev_to IS NOT NULL AND valid_from < prev_to),
               count(*) FILTER (WHERE prev_to IS NOT NULL AND valid_from > prev_to),
               count(*) FILTER (WHERE is_current <> (valid_from = mx))
        FROM x"""
_SQL_I4_CAUSALITY = """
        SELECT count(*) FILTER (WHERE known_at < (valid_from::timestamp AT TIME ZONE 'Asia/Shanghai')),
               count(*) FILTER (WHERE valid_from > %s)
        FROM {s}.pledge_event_version"""
_SQL_I5_RESOLUTION = """
        SELECT count(*) FILTER (WHERE holder_resolution='resolved' AND holder_entity_id IS NULL)
             + count(*) FILTER (WHERE holder_resolution='resolved' AND NOT EXISTS
                   (SELECT 1 FROM public.node_entity n WHERE n.entity_id = p.holder_entity_id)),
               count(*) FILTER (WHERE holder_resolution='unresolved' AND holder_entity_id IS NOT NULL)
        FROM {s}.pledge_event_version p"""
_SQL_I6_TRACEABILITY = f"""
        SELECT count(*) - count(DISTINCT source_ref),
               count(*) FILTER (WHERE source_ref NOT LIKE 'ch:{_CH_SOURCE_TABLE}#sha256:%')
        FROM {{s}}.pledge_event_version"""
_SQL_SMOKE_FUNCTION = "SELECT count(*) FROM {s}.holder_versions_as_of(%s, %s)"
_SQL_SMOKE_VIEW = "SELECT count(*) FROM {s}.v_holder_edge_version_timeline WHERE symbol = '000033'"


def carrier_versions(schema: str) -> list[tuple[str, str, object]]:
    """载体版本流（R3：只取 valid_from <= 切点）。"""
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(_SQL_CARRIER_VERSIONS.format(s=schema), (dt.date.fromisoformat(CUT),))
    rows = cur.fetchall()
    conn.close()
    return rows


def judge(events: list[tuple], index: dict[tuple[str, str], str]) -> dict[str, object]:
    """考试判据本体：匹配集 + 违规集（比较算子与探针一致，字符串 ISO 比较）。"""
    matched = viol = 0
    samples = []
    for sym, ad, shname in events:
        key = (norm_name(shname), str(sym).split(".")[0])
        vf = index.get(key)
        if vf is None:
            continue
        matched += 1
        if ad and str(ad) > vf:
            viol += 1
            if len(samples) < 5:
                samples.append([key[1], key[0][:18], str(ad), vf])
    return {
        "events": len(events),
        "matched": matched,
        "violations": viol,
        "violation_rate": round(viol / matched, 6) if matched else None,
        "samples": samples,
    }


def build_edge_index(cur: object) -> dict[tuple[str, str], str]:
    """考试版本侧原样：(归一股东名, 6 位代码) → max(valid_from)。"""
    cur.execute(_SQL_NODE_ENTITY_NAMES)
    ent = {r[0]: (r[1] or "") for r in cur.fetchall()}
    cur.execute(_SQL_EDGE_VERSIONS)
    idx: dict[tuple[str, str], str] = {}
    for fe, te, vf in cur.fetchall():
        fname = ent.get(fe, "")
        if not fname or vf is None:
            continue
        key = (norm_name(fname), te[3:].split(".")[0])
        s = str(vf)
        if key not in idx or s > idx[key]:
            idx[key] = s
    return idx


def _carrier_index(schema: str) -> dict[tuple[str, str], str]:
    """载体版本集最新生效日索引：(归一股东名, 6 位代码) → max(valid_from)（取法与 build_edge_index 同一折叠）。"""
    idx: dict[tuple[str, str], str] = {}
    for nn, sym, vf in carrier_versions(schema):
        key = (str(nn), str(sym).split(".")[0])
        s = str(vf)
        if key not in idx or s > idx[key]:
            idx[key] = s
    return idx


def _merge_max_index(base: dict[tuple[str, str], str], extra: dict[tuple[str, str], str]) -> dict[tuple[str, str], str]:
    """两版本集同键取 max(valid_from) 的并集（比较算子照抄考试探针，R1 零放宽）。"""
    union_idx = dict(base)
    for k, v in extra.items():
        if k not in union_idx or v > union_idx[k]:
            union_idx[k] = v
    return union_idx


def _aware(v: object) -> dt.datetime:
    """时刻归一到带时区的 datetime（无时区者按 UTC 解释——CH DateTime64(3,'UTC') 语义）。"""
    if isinstance(v, dt.datetime):
        return v if v.tzinfo else v.replace(tzinfo=dt.timezone.utc)
    if isinstance(v, dt.date):
        return dt.datetime(v.year, v.month, v.day, tzinfo=dt.timezone.utc)
    return dt.datetime.fromisoformat(str(v)).replace(tzinfo=dt.timezone.utc)


def _same_val(pg: object, src: object) -> bool:
    """值级对照（I2b 用）：数值走 Decimal 归一、日期/时刻按瞬时、源 1970 哨兵按既定口径视作 NULL。"""
    if pg is None and src is None:
        return True
    if pg is None or src is None:
        if pg is None and isinstance(src, (dt.date, dt.datetime)):
            return _d(src) is None  # 载体把 1970 哨兵置 NULL（B4），源有值而载体空是设计而非缺陷
        return False
    if isinstance(pg, (int, float, Decimal)) or isinstance(src, (int, float, Decimal)):
        try:
            return Decimal(str(pg)) == Decimal(str(src))
        except InvalidOperation:
            return str(pg) == str(src)
    if isinstance(pg, dt.datetime) or isinstance(src, dt.datetime):
        return _aware(pg) == _aware(src)
    if isinstance(pg, dt.date) or isinstance(src, dt.date):
        return _d(pg) == _d(src)
    return str(pg) == str(src)


def integrity_checks(schema: str, events_src: list[tuple], ch: object) -> dict[str, object]:
    """R4 七项载体完整性断言（与"违规归零"独立的另一把尺子，防自证式归零）。"""
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    res: dict[str, object] = {}

    # I1 行数吻合（源 vs 载体，逐方向）
    src_n = ch.execute(_SQL_SRC_EVENT_COUNT.format(cut=CUT))[0][0]
    cur.execute(_SQL_CARRIER_COUNT.format(s=schema))
    car_n = cur.fetchone()[0]
    res["I1_row_equality"] = {"source": src_n, "carrier": car_n, "ok": src_n == car_n}

    # I2 指纹可重算 + 值级对照：CH 源逐行重算 uid → 与库内 uid 集合双向差须为空；
    #    再按 event_uid 定序抽 3,000 行做逐字段值级对照（Numeric 用 Decimal 归一，timestamptz 比瞬时）
    src_rows = ch.execute(_SQL_SOURCE_ROWS_WINDOW.format(cols=", ".join(SRC_COLUMNS), cut=CUT))
    src_map: dict[str, dict[str, object]] = {}
    dup_uid = 0
    for r in src_rows:
        row = dict(zip(SRC_COLUMNS, r, strict=True))
        uid = event_uid(row)
        if uid in src_map:
            dup_uid += 1
        src_map[uid] = row
    cur.execute(_SQL_CARRIER_UIDS.format(s=schema))
    car_uids = {r[0] for r in cur.fetchall()}
    res["I2_fingerprint_recomputable"] = {
        "source_rows": len(src_rows),
        "distinct_uids": len(src_map),
        "carrier_rows": len(car_uids),
        "source_dup_uids": dup_uid,
        "carrier_only": len(car_uids - set(src_map)),
        "source_only": len(set(src_map) - car_uids),
        "ok": car_uids == set(src_map) and dup_uid == 0,
    }
    cmp_cols = (
        "valid_from",
        "business_from",
        "business_to",
        "release_date",
        "pledge_shares",
        "total_holdings",
        "total_pledged",
        "pledge_ratio",
        "holding_ratio",
        "is_released",
        "is_buyback",
        "src_quality_flag",
    )
    sampled = sorted(car_uids)[:3000]
    mismatches: dict[str, int] = {}
    if sampled:
        cur.execute(
            _SQL_CARRIER_SAMPLE.format(cols=", ".join(cmp_cols), s=schema),
            (sampled,),
        )
        for uid, *vals in cur.fetchall():
            srcrow = src_map.get(uid) or {}
            src_map_names = {
                "valid_from": "announce_date",
                "business_from": "pledge_start_date",
                "business_to": "pledge_end_date",
                "release_date": "release_date",
                "pledge_shares": "pledge_shares",
                "total_holdings": "total_holdings",
                "total_pledged": "total_pledged",
                "pledge_ratio": "pledge_ratio",
                "holding_ratio": "holding_ratio",
                "is_released": "is_released",
                "is_buyback": "is_buyback",
                "src_quality_flag": "quality_flag",
            }
            for col, val in zip(cmp_cols, vals, strict=True):
                sv = srcrow.get(src_map_names[col])
                if not _same_val(val, sv):
                    mismatches[col] = mismatches.get(col, 0) + 1
    res["I2b_value_level_sample"] = {
        "rows_checked": len(sampled),
        "fields": len(cmp_cols),
        "mismatch_by_field": mismatches,
        "ok": not mismatches,
    }

    # I3 版本链良构：区间不倒挂、同对不重叠、不留缝、现行版本恰为最晚公告日集
    # （链按"同对不同公告日"闭合 → 同日多事件共享同一 valid_to，故缝/重叠判定在"日"粒度上做）
    cur.execute(_SQL_I3_CHAIN.format(s=schema))
    b, o, g, m = cur.fetchone()
    res["I3_chain"] = {
        "bad_span": b,
        "overlap": o,
        "gap": g,
        "is_current_mislabel": m,
        "ok": b == 0 and o == 0 and g == 0 and m == 0,
    }

    # I4 因果（transaction_time 不得早于 valid_time）+ R3 切点洁净
    cur.execute(_SQL_I4_CAUSALITY.format(s=schema), (dt.date.fromisoformat(CUT),))
    b, fut = cur.fetchone()
    res["I4_causality_and_purity"] = {"known_before_valid": b, "rows_after_cutoff": fut, "ok": b == 0 and fut == 0}

    # I5 解析诚实：unresolved 必 NULL；resolved 必能在 node_entity 找到
    cur.execute(_SQL_I5_RESOLUTION.format(s=schema))
    bad_res, null_ok = cur.fetchone()
    res["I5_resolution_honesty"] = {
        "resolved_unbacked": bad_res,
        "unresolved_filled": null_ok,
        "ok": bad_res == 0 and null_ok == 0,
    }

    # I6 可回溯：source_ref 前缀 + 唯一
    cur.execute(_SQL_I6_TRACEABILITY.format(s=schema))
    dup, badref = cur.fetchone()
    res["I6_traceability"] = {"dup_source_ref": dup, "bad_source_ref": badref, "ok": dup == 0 and badref == 0}

    # I7 无虚构：载体 (归一名, 代码, 公告日) 三元组集 == 源三元组集
    cur.execute(_SQL_CARRIER_KEYS.format(s=schema))
    car_keys = set(cur.fetchall())
    src_keys = {(norm_name(r[2]), str(r[0]).split(".")[0], str(r[1])) for r in events_src}
    car_keys_str = {(a, b, str(c)) for a, b, c in car_keys}
    res["I7_no_fabrication"] = {
        "carrier_only": len(car_keys_str - src_keys),
        "source_only": len(src_keys - car_keys_str),
        "ok": car_keys_str == src_keys,
    }
    conn.close()
    return res


def hit_rate_comparison(events: list[tuple], schema: str) -> dict[str, object]:
    """同公告日版本命中率（考试登记"仅 1.2%"用的同一把尺子）：回填前 vs 回填后。

    定义：事件公告日恰好等于该 (归一股东名, 代码) 对某一版本的 valid_from → 命中。
    这一指标比"违规归零"更不易自证：它要求版本链在事件当天**真的有一个落点**。
    """
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(_SQL_NODE_ENTITY_NAMES)
    ent = {r[0]: (r[1] or "") for r in cur.fetchall()}
    days_edge: dict[tuple[str, str], set[str]] = defaultdict(set)
    cur.execute(_SQL_EDGE_VERSIONS)
    for fe, te, vf in cur.fetchall():
        fname = ent.get(fe, "")
        if not fname or vf is None:
            continue
        days_edge[(norm_name(fname), te[3:].split(".")[0])].add(str(vf))
    days_union: dict[tuple[str, str], set[str]] = defaultdict(set, {k: set(v) for k, v in days_edge.items()})
    cur.execute(_SQL_CARRIER_TRIPLES.format(s=schema))
    for nn, sym, vf in cur.fetchall():
        days_union[(str(nn), str(sym).split(".")[0])].add(str(vf))
    conn.close()
    tot = hit_edge = hit_union = 0
    for sym, ad, shname in events:
        key = (norm_name(shname), str(sym).split(".")[0])
        tot += 1
        s = str(ad)
        if s in days_edge.get(key, ()):
            hit_edge += 1
        if s in days_union.get(key, ()):
            hit_union += 1
    return {
        "events": tot,
        "same_day_hits_edge_only": hit_edge,
        "hit_rate_before": round(hit_edge / tot, 6) if tot else None,
        "same_day_hits_after": hit_union,
        "hit_rate_after": round(hit_union / tot, 6) if tot else None,
        "baseline_registered_in_exam": 0.012,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PQ-0072 判据复算（只读，零放宽）")
    ap.add_argument("--schema", default="metaq_pledge")
    ap.add_argument("--out", default=str(REPO / ".runtime/tmp/st-metaq-gc-20260924/wo009/recheck_pq0072.json"))
    args = ap.parse_args(argv)
    try:
        check_schema_name(args.schema)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    svc = DatabaseService()
    ch = svc.get_clickhouse_conn(role="reader")
    # 事件侧：与考试探针一字不差的过滤（切点 + 股东名非空）
    raw = ch.execute(_SQL_EVENTS_WINDOW.format(cut=CUT))
    events = [(r[0], str(r[1]), r[2]) for r in raw]

    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    edge_idx = build_edge_index(cur)
    cur.execute(_SQL_TO_REGCLASS.format(t=f"{args.schema}.pledge_event_version"))
    n_carrier = cur.fetchone()[0]
    if n_carrier is None:
        print(f"REFUSED: {args.schema}.pledge_event_version 不存在（先跑 DDL+回填）", file=sys.stderr)
        conn.close()
        return 3
    carrier_idx = _carrier_index(args.schema)
    conn.close()

    union_idx = _merge_max_index(edge_idx, carrier_idx)

    baseline = judge(events, edge_idx)
    after = judge(events, union_idx)
    carrier_only = judge(events, carrier_idx)

    out: dict[str, object] = {
        "cut": CUT,
        "criterion_restated": (
            "事件（质押公告 announce_date<=2025-09-09 且股东名非空）匹配到同 (股东名去空白归一, 6 位代码) 的"
            "版本集 max(valid_from)；违规 = str(announce_date) > str(max valid_from)；阈值 违规样本=0"
        ),
        "baseline_edge_only": baseline,
        "after_edge_union_carrier": after,
        "carrier_only": carrier_only,
        "baseline_regression_ok": (
            baseline["matched"] == BASELINE_EXPECT["matched"]
            and baseline["violations"] == BASELINE_EXPECT["violations"]
        ),
        "version_keys_edge": len(edge_idx),
        "version_keys_carrier": len(carrier_idx),
    }
    if args.schema == "metaq_pledge":
        out["integrity"] = integrity_checks(args.schema, events, ch)
        out["hit_rate"] = hit_rate_comparison(events, args.schema)
        # 载体可消费性烟测：PIT 函数 + 统一版本流视图真跑一条
        conn2 = get_depgraph_pg_connection(read_only=True)
        cur2 = conn2.cursor()
        cur2.execute(_SQL_SMOKE_FUNCTION.format(s=args.schema), ("000033", dt.date(2020, 6, 30)))
        n_fn = cur2.fetchone()[0]
        cur2.execute(_SQL_SMOKE_VIEW.format(s=args.schema))
        n_view = cur2.fetchone()[0]
        conn2.close()
        out["consumer_smoke"] = {
            "holder_versions_as_of_000033_2020-06-30": n_fn,
            "timeline_view_rows_000033": n_view,
        }
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    if not out["baseline_regression_ok"]:
        print(
            f"JUDGE DRIFT: 基线未复现（期望 {BASELINE_EXPECT}，实得 matched={baseline['matched']} "
            f"viol={baseline['violations']}）→ 拒绝采信归零",
            file=sys.stderr,
        )
        return 5
    integ = out.get("integrity") or {}
    if integ and not all(v.get("ok", True) for v in integ.values() if isinstance(v, dict)):
        print("INTEGRITY FAILED: 见 integrity 分组", file=sys.stderr)
        return 4
    verdict = "PASS" if after["violations"] == 0 else "FAIL"
    print(
        f"VERDICT {verdict}: 复算违规 {after['violations']}/{after['matched']}（基线 {baseline['violations']}/{baseline['matched']}）"
    )
    return 0 if after["violations"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
