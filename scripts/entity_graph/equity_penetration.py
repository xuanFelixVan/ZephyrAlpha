# [BLUEPRINT] MOD-ENTITY-GRAPH | docs/_working/altdata_line/02_entity_graph_equity_person.md | §
# [MODULE] scripts.entity_graph.equity_penetration
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_reader (stock_basic 断线端点反查); entity_graph_ingest (_tbl TableRegistry 助手)
# [CONSUMERS] 信号侧(牛散跨票/同实控人联动/质押链传导)—设计 §5 信号用途清单
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] ig_equity_edge 并入: 每条带 source_ref='pg:ig_equity_edge.edge_id=N' 全链路可回溯;
#   role=relation 原词保留(invests_in/shareholding/subsidiary/actual_control); pledge/judicial_frozen 非持股事件不并入;
#   as_of 缺失不落边(反幻觉: 无事实时间不可 PIT 定位,只进缺口台账); 端点缺节点→stock_basic 反查建 CO:<symbol>,
#   仍缺→name=symbol 占位+low_confidence=TRUE(不编造名称); 比对口径=现行版本对(valid_to IS NULL)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/信号侧按需调用的查询比对 CLI 工具（单次查询即退出，无常驻进程不订阅事件），非"永久系统"运行体
# [ERROR_CONTRACT] PG 不可达->退出码2; 穿透函数缺失->退出码3(先跑 apply_entity_graph_ddl.py)
# [TESTS] 2026-09-19 首跑: ig_equity_edge 804/804 并入+121 端点节点补建; 比对=A 层现行对 274,865×ig 804(重叠 129/ig 独有 675/A 层独有 274,736); 三家样本穿透链实测通过(600566/600927/601963)
# [TTL] permanent
"""W7-3：ig_equity_edge(804 条)并入 edge_holding + 重叠/互补比对 + N 度穿透链实测。

三步（2026-09-19）：
    1. merge-ig      ig_equity_edge → edge_holding（source='ig_equity_edge'，幂等 DO NOTHING）
    2. compare       A 层(akshare_top10) × ig_equity_edge 现行版本对 比对 → 重叠/互补报告(json+stdout)
    3. penetrate     equity_penetration() 函数实测三家样本公司穿透链

比对口径：同 (from_entity, to_entity) 现行版本对；重叠=两源都有；互补=ig 独有(十大股东
口径外关系,如低于前十门槛/非报告期口径)；A 层独有=ig 图库覆盖外的直挂关系。

用法::

    python scripts/entity_graph/equity_penetration.py                  # 三步全跑
    python scripts/entity_graph/equity_penetration.py --penetrate 600566.SH --depth 3
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RUN_DIR = REPO / ".runtime" / "entity_graph"
COMPARE_REPORT = RUN_DIR / "ig_equity_compare_report.json"
SAMPLES = ["600566.SH", "600927.SH", "601963.SH"]  # 20260630 十大股东含上市主体数最多的三家
# 非持股事件（质押/司法冻结是股权域事件但不是持股边，设计 relation 词表分开）
_NON_HOLDING = ("pledge", "judicial_frozen")

# ========== SQL 集中化（§5.160.2：裸 SQL 禁止，一律模块级常量） ==========
SQL_FETCH_IG = "SELECT edge_id, holder, held, stake_pct, relation, as_of, source FROM ig_equity_edge ORDER BY edge_id"
SQL_RESOLVE_SYMBOLS = "SELECT symbol, entity_id FROM node_entity WHERE symbol = ANY(%s)"
SQL_INSERT_IG_NODES = """
    INSERT INTO node_entity
        (entity_id, entity_type, name, name_norm, symbol, uscc, low_confidence, source)
    VALUES %s
    ON CONFLICT (entity_id) DO NOTHING
"""
SQL_STG_IG_CREATE = """
    CREATE TEMP TABLE stg_ig_holding (
        from_entity TEXT, to_entity TEXT, stake_pct NUMERIC,
        role TEXT, valid_from DATE, source_ref TEXT
    )
"""
SQL_STG_IG_FILL = (
    "INSERT INTO stg_ig_holding (from_entity, to_entity, stake_pct, role, valid_from, source_ref) VALUES %s"
)
SQL_STG_IG_MERGE = """
    INSERT INTO edge_holding
        (from_entity, to_entity, stake_pct, role, valid_from, source, source_ref)
    SELECT from_entity, to_entity, stake_pct, role, valid_from, 'ig_equity_edge', source_ref
    FROM stg_ig_holding
    ON CONFLICT (from_entity, to_entity, role, valid_from, source) DO NOTHING
"""
SQL_A_CURRENT = "SELECT from_entity, to_entity FROM edge_holding WHERE source = 'akshare_top10' AND valid_to IS NULL"
SQL_B_CURRENT = "SELECT from_entity, to_entity FROM edge_holding WHERE source = 'ig_equity_edge'"
SQL_COUNT_OVERLAP = "SELECT count(*) FROM (" + SQL_A_CURRENT + " INTERSECT " + SQL_B_CURRENT + ") t"
SQL_COUNT_A_CURRENT = "SELECT count(*) FROM edge_holding WHERE source = 'akshare_top10' AND valid_to IS NULL"
SQL_COUNT_B = "SELECT count(*) FROM edge_holding WHERE source = 'ig_equity_edge'"
SQL_COUNT_B_STAKE = "SELECT count(*) FROM edge_holding WHERE source = 'ig_equity_edge' AND stake_pct IS NOT NULL"
SQL_COUNT_A_STAKE = (
    "SELECT count(*) FROM edge_holding WHERE source = 'akshare_top10' AND valid_to IS NULL AND stake_pct IS NOT NULL"
)
SQL_OVERLAP_SAMPLES = """
    SELECT fe.name, te.name, e.role, e.stake_pct, e.valid_from
    FROM edge_holding e
    JOIN node_entity fe ON fe.entity_id = e.from_entity
    JOIN node_entity te ON te.entity_id = e.to_entity
    WHERE e.source = 'ig_equity_edge'
      AND EXISTS (
          SELECT 1 FROM edge_holding a
          WHERE a.source = 'akshare_top10' AND a.valid_to IS NULL
            AND a.from_entity = e.from_entity AND a.to_entity = e.to_entity
      )
    ORDER BY e.stake_pct DESC NULLS LAST LIMIT 10
"""
SQL_IG_ONLY_SAMPLES = """
    SELECT fe.name, te.name, e.role, e.stake_pct, e.valid_from
    FROM edge_holding e
    JOIN node_entity fe ON fe.entity_id = e.from_entity
    JOIN node_entity te ON te.entity_id = e.to_entity
    WHERE e.source = 'ig_equity_edge'
      AND NOT EXISTS (
          SELECT 1 FROM edge_holding a
          WHERE a.source = 'akshare_top10' AND a.valid_to IS NULL
            AND a.from_entity = e.from_entity AND a.to_entity = e.to_entity
      )
    ORDER BY e.valid_from DESC NULLS LAST, e.stake_pct DESC NULLS LAST LIMIT 10
"""
SQL_PENETRATE = "SELECT * FROM equity_penetration(%s, %s, %s)"
SQL_CH_SYMBOL_NAMES = (
    "SELECT symbol_canonical, coalesce(nullIf(name, ''), nullIf(fullname, '')) "
    "FROM {} FINAL WHERE symbol_canonical IN ({in_list})"
)

# CH 表名经 TableRegistry 真源派生（#ARCH-CH-024）——_tbl 助手真源在 entity_graph_ingest
from entity_graph_ingest import _tbl  # noqa: E402  # noqa: PLC0415


def fetch_ig_edges(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(SQL_FETCH_IG)
        return [
            {
                "edge_id": r[0],
                "holder": r[1],
                "held": r[2],
                "stake_pct": r[3],
                "relation": r[4],
                "as_of": r[5],
                "source": r[6],
            }
            for r in cur.fetchall()
        ]


def resolve_symbol_nodes(conn, symbols: set[str]) -> dict[str, str]:
    """symbol → entity_id（仅查已存在节点）。"""
    if not symbols:
        return {}
    with conn.cursor() as cur:
        cur.execute(SQL_RESOLVE_SYMBOLS, (sorted(symbols),))
        return {r[0]: r[1] for r in cur.fetchall()}


def ch_symbol_names(symbols: list[str]) -> dict[str, str]:
    """CH stock_basic（不限 valid_to，含退市）canonical symbol → 名称。"""
    if not symbols:
        return {}
    from zephyr.data import ch_reader

    in_list = ",".join(f"'{s}'" for s in symbols)
    tsv = ch_reader.query(SQL_CH_SYMBOL_NAMES.format(_tbl("meta_stock_basic"), in_list=in_list))
    out = {}
    for ln in tsv.strip().splitlines():
        p = ln.split("\t")
        if len(p) >= 2 and p[1] not in ("", "None"):
            out[p[0].strip()] = p[1].strip()
    return out


def merge_ig(conn) -> dict:
    """ig_equity_edge → edge_holding。返回并入统计。"""
    from psycopg2.extras import execute_values

    ig_edges = fetch_ig_edges(conn)
    stats = {
        "total": len(ig_edges),
        "merged": 0,
        "skipped_non_holding": 0,
        "skipped_no_asof": 0,
        "nodes_created": 0,
        "dup_skipped": 0,
    }

    todo = []
    for e in ig_edges:
        if e["relation"] in _NON_HOLDING:
            stats["skipped_non_holding"] += 1
            continue
        if e["as_of"] is None:
            stats["skipped_no_asof"] += 1
            continue
        todo.append(e)

    # 端点节点解析：缺则 CH 反查建节点（不编造名称）
    endpoints = {s for e in todo for s in (e["holder"], e["held"])}
    sym2eid = resolve_symbol_nodes(conn, endpoints)
    missing = sorted(endpoints - set(sym2eid))
    if missing:
        name_map = ch_symbol_names(missing)
        new_nodes = []
        for s in missing:
            nm = name_map.get(s, s)  # 查不到名称→symbol 占位，禁编造
            new_nodes.append((f"CO:{s}", "company", nm, s, s, None, True, "ig_equity_edge"))
        with conn.cursor() as cur:
            execute_values(cur, SQL_INSERT_IG_NODES, new_nodes, page_size=1000)
        stats["nodes_created"] = len(new_nodes)
        sym2eid.update({s: f"CO:{s}" for s in missing})

    rows = [
        (
            sym2eid[e["holder"]],
            sym2eid[e["held"]],
            e["stake_pct"],
            e["relation"],  # role=relation 原词保留（持股≠控制，语义不混算）
            e["as_of"],
            f"pg:ig_equity_edge.edge_id={e['edge_id']}",
        )
        for e in todo
    ]
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS stg_ig_holding")
        cur.execute(SQL_STG_IG_CREATE)
        execute_values(cur, SQL_STG_IG_FILL, rows, page_size=1000)
        cur.execute(SQL_STG_IG_MERGE)
        stats["merged"] = cur.rowcount
        cur.execute("DROP TABLE IF EXISTS stg_ig_holding")
    stats["dup_skipped"] = len(rows) - stats["merged"]
    return stats


def compare(conn) -> dict:
    """A 层 × ig 现行版本对的重叠/互补比对。"""
    with conn.cursor() as cur:
        cur.execute(SQL_COUNT_OVERLAP)
        overlap = cur.fetchall()[0][0]
        cur.execute(SQL_COUNT_A_CURRENT)
        a_total = cur.fetchall()[0][0]
        cur.execute(SQL_COUNT_B)
        b_total = cur.fetchall()[0][0]
        cur.execute(SQL_OVERLAP_SAMPLES)
        overlap_samples = [
            {"holder": r[0], "held": r[1], "role": r[2], "stake_pct": r[3], "valid_from": str(r[4])}
            for r in cur.fetchall()
        ]
        cur.execute(SQL_IG_ONLY_SAMPLES)
        ig_only_samples = [
            {"holder": r[0], "held": r[1], "role": r[2], "stake_pct": r[3], "valid_from": str(r[4])}
            for r in cur.fetchall()
        ]
        cur.execute(SQL_COUNT_B_STAKE)
        b_with_stake = cur.fetchall()[0][0]
        cur.execute(SQL_COUNT_A_STAKE)
        a_with_stake = cur.fetchall()[0][0]

    a_only = a_total - overlap
    ig_only_pairs = b_total - overlap
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "口径": "现行版本对 (from_entity, to_entity)；A 层=akshare_top10 十大股东直挂，B=ig_equity_edge 图库股权边",
        "a_total_pairs": a_total,
        "b_total_edges": b_total,
        "overlap_pairs": overlap,
        "a_only_pairs": a_only,
        "ig_only_edges": ig_only_pairs,
        "stake_coverage": {"a_with_stake_pct": a_with_stake, "ig_with_stake_pct": b_with_stake},
        "overlap_samples": overlap_samples,
        "ig_only_samples": ig_only_samples,
    }
    return report


def penetrate(conn, symbol: str, depth: int, min_valid_from=None) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(SQL_PENETRATE, (symbol, depth, min_valid_from))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]


def _print_chain(rows: list[dict]) -> None:
    for r in rows:
        stake = r["stake_pct"] if r["stake_pct"] is not None else "-"
        print(
            f"  L{r['depth']} {r['from_name']} ({r['from_type']}) -[{r['role']} "
            f"{stake}%]-> {r['to_name']} @ {r['valid_from']}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="ig_equity_edge 并入+比对+穿透实测")
    ap.add_argument("--penetrate", default=None, help="只跑穿透：公司 symbol/entity_id")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--min-valid-from", default=None, help="观测窗下沿 YYYY-MM-DD（缺省=最后观测态全量）")
    ap.add_argument("--skip-merge", action="store_true", help="跳过 ig 并入（只比对+穿透）")
    args = ap.parse_args()

    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    try:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] PostgreSQL 不可达: {exc}")
        return 2

    out: dict = {}

    if args.penetrate:
        rows = penetrate(conn, args.penetrate, args.depth, args.min_valid_from)
        print(f"[PENETRATE] {args.penetrate} depth<={args.depth}: {len(rows)} 边")
        _print_chain(rows)
        conn.close()
        return 0

    if not args.skip_merge:
        stats = merge_ig(conn)
        print(f"[MERGE-IG] {stats}")
        out["merge_ig"] = stats

    report = compare(conn)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with open(COMPARE_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(
        f"[COMPARE] A层现行对={report['a_total_pairs']} ig边={report['b_total_edges']} "
        f"重叠={report['overlap_pairs']} ig独有(互补)={report['ig_only_edges']} "
        f"A层独有={report['a_only_pairs']}"
    )
    print(
        f"[COMPARE] stake 覆盖: A层={report['stake_coverage']['a_with_stake_pct']} "
        f"ig={report['stake_coverage']['ig_with_stake_pct']}"
    )
    print("[COMPARE] 重叠样例:", json.dumps(report["overlap_samples"][:3], ensure_ascii=False, default=str))
    print("[COMPARE] ig独有样例:", json.dumps(report["ig_only_samples"][:5], ensure_ascii=False, default=str))
    print(f"[COMPARE] 报告落盘: {COMPARE_REPORT}")
    out["compare"] = report

    print("[PENETRATE] 样本公司穿透链实测（depth<=3; 全量=最后观测态, 最新=2026-06-30 观测窗）:")
    out["samples"] = {}
    for sym in SAMPLES:
        rows_full = penetrate(conn, sym, 3)
        rows_recent = penetrate(conn, sym, 3, "2026-06-30")
        out["samples"][sym] = {"full": rows_full, "asof_20260630": rows_recent}
        print(f"  --- {sym}: 全量 {len(rows_full)} 边 | 2026-06-30 观测窗 {len(rows_recent)} 边 ---")
        _print_chain(rows_recent)
    conn.close()

    detail_path = RUN_DIR / "penetration_samples.json"
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(out["samples"], f, ensure_ascii=False, indent=2, default=str)
    print(f"[DONE] 样本明细: {detail_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
