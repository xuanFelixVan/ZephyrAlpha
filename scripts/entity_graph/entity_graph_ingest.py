# [BLUEPRINT] MOD-ENTITY-GRAPH | docs/_working/altdata_line/02_entity_graph_equity_person.md | §
# [MODULE] scripts.entity_graph.entity_graph_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader (top10_shareholders/stock_basic); zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.entity_graph.equity_penetration (边数据供给方)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] A 层=akshare 十大股东直挂(设计 §3 数据源四层); 节点身份三级判定:
#   上市( fullname 匹配 stock_basic→CO:<symbol>, low_confidence=FALSE ) / 机构关键词( CO:<md5>, low_confidence=TRUE ) /
#   自然人( PE:<md5>, low_confidence=TRUE ); uscc A 层无源一律 NULL(缺失=名字符串键+low_confidence 标记, 按设计决策①);
#   边幂等(UNIQUE from,to,role,valid_from,source ON CONFLICT DO NOTHING); PIT 变更追加新版本不覆盖(设计决策②),
#   同源同对新 valid_from 到来时旧版本盖 valid_to; 持股≠控制(决策③, role=shareholder 不含控制语义);
#   解析不到的股东不编造边(决策④); 重跑安全(COPY→staging TEMP→ON CONFLICT); rank_no=期内 hold_ratio 降序次序
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/Owner 按需调用的批量灌入 CLI 工具（单次跑批即退出，无常驻进程不订阅事件），非"永久系统"运行体
# [ERROR_CONTRACT] CH 不可达->退出码2; PG 不可达->退出码2; 单期失败->记 progress 后继续(回执汇报)
# [TESTS] 2026-09-19 首跑: 1,500,427 源行→1,500,341 边/140,725 节点(含 91 身份修正迁移); 2026-06-30 复跑=幂等(46 条新关键词修正重分类后迁移, 余 0 新增)
# [TTL] permanent
"""A 层灌入：c3_fundamental.top10_shareholders → node_entity + edge_holding（PG depgraph 图谱域）。

数据流（W7-2，2026-09-19）：
    CH top10_shareholders(全报告期, 150 万行) → 股东名三级判定成节点 → 节点 upsert(LEAST/GREATEST PIT 观测轴)
    → 边 COPY→staging TEMP→INSERT ON CONFLICT DO NOTHING → 同对旧版本 valid_to 关闭。

shareholder_name 无类型列——公司/自然人判定为启发式(上市注册名匹配+机构关键词)，
误判风险由 low_confidence=TRUE 显式标记；同名自然人合并为同节点=设计 §7 已知边界
(消歧靠 B 层简历/出生年富化，禁在 A 层拍合并)。
被持股公司(to 侧)=上市主体，身份锚 symbol(CO:<symbol_canonical>)，名取 stock_basic 简称。

用法::

    python scripts/entity_graph/entity_graph_ingest.py            # 全报告期灌入
    python scripts/entity_graph/entity_graph_ingest.py --periods 2026-06-30,2026-03-31
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RUN_DIR = REPO / ".runtime" / "entity_graph"
PROGRESS_PATH = RUN_DIR / "ingest_progress.jsonl"
EDGE_SOURCE = "akshare_top10"

# ========== SQL 集中化（§5.160.2：裸 SQL 禁止，一律模块级常量） ==========
# CH 表名经 TableRegistry 真源派生（#ARCH-CH-024），禁硬编码（惰性查表防导入副作用）


def _tbl(category_id: str) -> str:
    from zephyr.data.table_registry import get_registry

    return get_registry().table(category_id)


SQL_LISTED_MAPS = "SELECT symbol_canonical, name, fullname FROM {} FINAL WHERE valid_to IS NULL"
SQL_PERIODS = "SELECT DISTINCT toString(report_period) FROM {} FINAL ORDER BY 1"
SQL_PERIOD_ROWS = (
    "SELECT symbol_canonical, shareholder_name, hold_ratio, hold_shares, hold_change, "
    "shareholder_type, toString(announce_date), toString(report_period) "
    "FROM {} FINAL WHERE report_period IN ({in_list})"
)
SQL_IDENTITY_SEED = "SELECT entity_id, entity_type, name_norm FROM node_entity WHERE uscc IS NULL"
SQL_COUNT_NODES = "SELECT count(*) FROM node_entity"
SQL_COUNT_EDGES = "SELECT count(*) FROM edge_holding"
SQL_NODE_SPLIT = "SELECT entity_type, low_confidence, count(*) FROM node_entity GROUP BY 1, 2 ORDER BY 1, 2"
SQL_COUNT_CLOSED = "SELECT count(*) FROM edge_holding WHERE valid_to IS NOT NULL"
SQL_UPSERT_NODES = """
    INSERT INTO node_entity
        (entity_id, entity_type, name, name_norm, symbol, uscc, low_confidence,
         source, first_seen, last_seen)
    VALUES %s
    ON CONFLICT (entity_id) DO UPDATE SET
        first_seen = LEAST(COALESCE(node_entity.first_seen, EXCLUDED.first_seen),
                           EXCLUDED.first_seen),
        last_seen  = GREATEST(COALESCE(node_entity.last_seen, EXCLUDED.last_seen),
                              EXCLUDED.last_seen),
        symbol = COALESCE(node_entity.symbol, EXCLUDED.symbol),
        low_confidence = CASE WHEN COALESCE(node_entity.symbol, EXCLUDED.symbol) IS NOT NULL
                              THEN FALSE ELSE node_entity.low_confidence END,
        updated_at = now()
"""
SQL_STG_EDGE_CREATE = """
    CREATE TEMP TABLE stg_edge_holding (
        from_entity TEXT, to_entity TEXT, stake_pct NUMERIC, shares NUMERIC,
        shares_type TEXT, role TEXT, rank_no SMALLINT, hold_change NUMERIC,
        valid_from DATE, announce_date DATE, source TEXT, source_ref TEXT
    )
"""
SQL_STG_EDGE_INSERT = """
    INSERT INTO edge_holding
        (from_entity, to_entity, stake_pct, shares, shares_type, role, rank_no,
         hold_change, valid_from, announce_date, source, source_ref)
    SELECT from_entity, to_entity, stake_pct, shares, shares_type, role, rank_no,
           hold_change, valid_from, announce_date, source, source_ref
    FROM stg_edge_holding
    ON CONFLICT (from_entity, to_entity, role, valid_from, source) DO NOTHING
"""
SQL_CLOSE_SUPERSEDED = """
    UPDATE edge_holding e
    SET valid_to = t.next_from
    FROM (
        SELECT edge_id,
               lead(valid_from) OVER (
                   PARTITION BY from_entity, to_entity, role
                   ORDER BY valid_from
               ) AS next_from
        FROM edge_holding
        WHERE source = %s
    ) t
    WHERE e.edge_id = t.edge_id
      AND t.next_from IS NOT NULL
      AND e.valid_to IS NULL
"""

# 机构/产品账户关键词（A 层启发式，命中→company）
_ORG_KEYWORDS = (
    "公司",
    "企业",
    "合伙",
    "基金",
    "信托",
    "银行",
    "证券",
    "保险",
    "资管",
    "资产管理",
    "投资",
    "控股",
    "集团",
    "中心",
    "计划",
    "工作室",
    "研究所",
    "研究院",
    "大学",
    "工会",
    "委员会",
    "财政局",
    "财政厅",
    "管理局",
    "事务所",
    "国资",
    "社保",
    "汇金",
    "结算",
    "组合",
    "账户",
)


def norm_name(s: str) -> str:
    """名称规范化：NFKC（全角→半角）→去空白→大写。消歧用 name_norm 同款。"""
    return unicodedata.normalize("NFKC", s).replace(" ", "").replace("\u3000", "").upper()


def md20(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:20]


def is_org(name: str) -> bool:
    return any(k in name for k in _ORG_KEYWORDS)


def load_listed_maps():
    """stock_basic 当前有效清单 → 简称/全称 → canonical symbol 映射（norm 键）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(SQL_LISTED_MAPS.format(_tbl("meta_stock_basic")))
    name2sym: dict[str, str] = {}
    sym2name: dict[str, str] = {}
    for ln in tsv.strip().splitlines():
        parts = ln.split("\t")
        if len(parts) < 3:
            continue
        sym, name, fullname = parts[0].strip(), parts[1].strip(), parts[2].strip()
        sym2name[sym] = name or fullname or sym
        if name:
            name2sym[norm_name(name)] = sym
        if fullname:
            name2sym.setdefault(norm_name(fullname), sym)
    return name2sym, sym2name


def build_entity_id(entity_type: str, name_norm_v: str, symbol: str | None) -> str:
    """确定性代理键：上市=CO:<symbol>；机构/自然人=<前缀>:<md5(name_norm)[:20]>。

    人不存真实身份证号（设计 §2）；md5 代理键跨跑稳定=幂等前提。
    """
    if entity_type == "company" and symbol:
        return f"CO:{symbol}"
    prefix = "CO" if entity_type == "company" else "PE"
    return f"{prefix}:{md20(name_norm_v)}"


def classify(name: str, name2sym: dict[str, str]) -> tuple[str, str | None, bool]:
    """三级判定 → (entity_type, symbol, low_confidence)。"""
    nv = norm_name(name)
    sym = name2sym.get(nv)
    if sym:
        return "company", sym, False  # 上市注册名匹配=身份锚到交易所清单
    if is_org(name):
        return "company", None, True
    return "person", None, True


def parse_float(v: str) -> float | None:
    if v in ("None", "", "\\N", "nan", "NULL"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_date(v: str) -> date | None:
    if v in ("None", "", "\\N", "1970-01-01"):
        return None
    try:
        return datetime.strptime(v[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def fetch_periods() -> list[str]:
    from zephyr.data import ch_reader

    tsv = ch_reader.query(SQL_PERIODS.format(_tbl("fund_top10_shareholders")))
    return [ln.strip() for ln in tsv.strip().splitlines() if ln.strip()]


def fetch_period_rows(periods: list[str]) -> list[dict]:
    """一批报告期的十大股东行（显式列序）。periods 非空。"""
    from zephyr.data import ch_reader

    in_list = ",".join(f"'{p}'" for p in periods)
    tsv = ch_reader.query(SQL_PERIOD_ROWS.format(_tbl("fund_top10_shareholders"), in_list=in_list))
    rows = []
    for ln in tsv.strip().splitlines():
        p = ln.split("\t")
        if len(p) < 8:
            continue
        rows.append(
            {
                "symbol": p[0].strip(),
                "holder_name": p[1].strip(),
                "hold_ratio": parse_float(p[2]),
                "hold_shares": parse_float(p[3]),
                "hold_change": parse_float(p[4]),
                "shares_type": p[5].strip() or None,
                "announce_date": parse_date(p[6]),
                "period": parse_date(p[7]),
            }
        )
    return rows


def upsert_nodes(cur, nodes: list[dict]) -> None:
    """节点 upsert：first_seen/last_seen 双观测轴 + symbol 富化 + low_confidence 联动。"""
    if not nodes:
        return
    from psycopg2.extras import execute_values

    vals = [
        (
            n["entity_id"],
            n["entity_type"],
            n["name"],
            n["name_norm"],
            n["symbol"],
            None,
            n["low_confidence"],
            EDGE_SOURCE,
            n["seen"],
            n["seen"],
        )
        for n in nodes
    ]
    execute_values(cur, SQL_UPSERT_NODES, vals, page_size=2000)


def insert_edges(cur, edges: list[dict]) -> int:
    """边 COPY→staging TEMP→ON CONFLICT DO NOTHING（幂等+追加）。返回实际新插行数。"""
    if not edges:
        return 0
    cur.execute("DROP TABLE IF EXISTS stg_edge_holding")
    cur.execute(SQL_STG_EDGE_CREATE)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for e in edges:
        w.writerow(
            [
                e["from_entity"],
                e["to_entity"],
                "" if e["stake_pct"] is None else e["stake_pct"],
                "" if e["shares"] is None else e["shares"],
                e["shares_type"] or "",
                e["role"],
                "" if e["rank_no"] is None else e["rank_no"],
                "" if e["hold_change"] is None else e["hold_change"],
                e["valid_from"].isoformat(),
                e["announce_date"].isoformat() if e["announce_date"] else "",
                e["source"],
                e["source_ref"],
            ]
        )
    buf.seek(0)
    cur.copy_expert("COPY stg_edge_holding FROM STDIN WITH (FORMAT csv, NULL '')", buf)
    cur.execute(SQL_STG_EDGE_INSERT)
    inserted = cur.rowcount
    cur.execute("DROP TABLE IF EXISTS stg_edge_holding")
    return inserted


def close_superseded_versions(cur) -> int:
    """同源同(from,to,role)出现更新 valid_from 时，旧版本盖 valid_to（追加不覆盖的关闭侧）。"""
    cur.execute(SQL_CLOSE_SUPERSEDED, (EDGE_SOURCE,))
    return cur.rowcount


def rank_rows(rows: list[dict]) -> None:
    """期内 rank：同 (symbol, period) 按 hold_ratio 降序（十大排名语义），原地写 r['rank']。"""
    by_grp: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["symbol"], r["period"].isoformat() if r["period"] else "")
        by_grp.setdefault(key, []).append(r)
    for grp_rows in by_grp.values():
        grp_rows.sort(key=lambda x: (x["hold_ratio"] is None, -(x["hold_ratio"] or 0)))
        for i, r in enumerate(grp_rows, 1):
            r["rank"] = i


def build_batch_payload(
    rows: list[dict],
    identity_map: dict[tuple[str, str], str],
    name2sym: dict[str, str],
    sym2name: dict[str, str],
) -> tuple[dict[str, dict], list[dict], int]:
    """一批源行 → (节点表, 边表, 跳过行数)。三级身份判定+确定性代理键在此收敛。"""
    nodes_by_id: dict[str, dict] = {}
    edges: list[dict] = []
    skipped = 0
    for r in rows:
        holder = r["holder_name"]
        nv = norm_name(holder)
        if not nv:
            skipped += 1
            continue
        etype, sym, lowc = classify(holder, name2sym)
        nid = identity_map.get((etype, nv)) or build_entity_id(etype, nv, sym)
        identity_map[(etype, nv)] = nid
        seen = r["period"] or r["announce_date"]
        if nid not in nodes_by_id:
            nodes_by_id[nid] = {
                "entity_id": nid,
                "entity_type": etype,
                "name": holder,
                "name_norm": nv,
                "symbol": sym,
                "low_confidence": lowc,
                "seen": seen,
            }
        else:  # 同名节点期内复用（PIT 观测轴取最晚）
            nodes_by_id[nid]["seen"] = max(nodes_by_id[nid]["seen"], seen)
        to_id = f"CO:{r['symbol']}"  # 被持股公司=上市主体，身份锚 symbol
        if to_id not in nodes_by_id:
            disp = sym2name.get(r["symbol"], r["symbol"])
            nodes_by_id[to_id] = {
                "entity_id": to_id,
                "entity_type": "company",
                "name": disp,
                "name_norm": norm_name(disp),
                "symbol": r["symbol"],
                "low_confidence": False,
                "seen": seen,
            }
        edges.append(
            {
                "from_entity": nid,
                "to_entity": to_id,
                "stake_pct": r["hold_ratio"],
                "shares": r["hold_shares"],
                "shares_type": r["shares_type"],
                "role": "shareholder",
                "rank_no": r["rank"],
                "hold_change": r["hold_change"],
                "valid_from": r["period"] or r["announce_date"],
                "announce_date": r["announce_date"],
                "source": EDGE_SOURCE,
                "source_ref": (
                    f"ch:{_tbl('fund_top10_shareholders')}|{r['symbol']}|"
                    f"{r['period'].isoformat() if r['period'] else 'NA'}|{nv}"
                ),
            }
        )
    return nodes_by_id, edges, skipped


def run(periods: list[str] | None) -> int:
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    all_periods = fetch_periods()
    if not all_periods:
        print("[ERROR] CH top10_shareholders 不可达或为空")
        return 2
    targets = [p for p in all_periods if not periods or p in periods]
    print(f"[PLAN] 报告期 {len(targets)}/{len(all_periods)}: {targets}")

    name2sym, sym2name = load_listed_maps()
    print(f"[PLAN] stock_basic 当前有效: {len(name2sym)} 名称键")

    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)

    # 身份表播种：重跑时 (entity_type, name_norm) 沿用既有 entity_id，防同名部分唯一索引冲突
    with conn.cursor() as cur:
        cur.execute(SQL_IDENTITY_SEED)
        identity_map = {(r[1], r[2]): r[0] for r in cur.fetchall()}
    print(f"[PLAN] 既有节点身份播种: {len(identity_map)}")

    totals = {"periods": 0, "rows": 0, "nodes_upserted": 0, "edges_new": 0, "skipped_rows": 0}
    CHUNK = 200  # 期/批：控内存上限（报告期粒度约 0.5-5 万行/期 → 批 ≤ 数十万行）
    with conn.cursor() as cur:
        for ci in range(0, len(targets), CHUNK):
            batch_periods = targets[ci : ci + CHUNK]
            rows = fetch_period_rows(batch_periods)
            rank_rows(rows)
            nodes_by_id, edges, skipped = build_batch_payload(rows, identity_map, name2sym, sym2name)
            upsert_nodes(cur, list(nodes_by_id.values()))
            new_edges = insert_edges(cur, edges)
            totals["periods"] += len(batch_periods)
            totals["rows"] += len(rows)
            totals["nodes_upserted"] += len(nodes_by_id)
            totals["edges_new"] += new_edges
            totals["skipped_rows"] += skipped
            rec = {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "periods": f"{batch_periods[0]}..{batch_periods[-1]}",
                "n_periods": len(batch_periods),
                "rows": len(rows),
                "nodes": len(nodes_by_id),
                "edges_new": new_edges,
                "skipped": skipped,
            }
            with open(PROGRESS_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(
                f"[BATCH] {batch_periods[0]}..{batch_periods[-1]} ({len(batch_periods)}期): "
                f"rows={len(rows)} nodes={len(nodes_by_id)} edges_new={new_edges}"
            )

        closed = close_superseded_versions(cur)

    # 回执口径以 DB 终态为准（禁跑批计数虚报）
    with conn.cursor() as cur:
        cur.execute(SQL_COUNT_NODES)
        n_nodes = cur.fetchall()[0][0]
        cur.execute(SQL_COUNT_EDGES)
        n_edges = cur.fetchall()[0][0]
        cur.execute(SQL_NODE_SPLIT)
        node_split = cur.fetchall()
        cur.execute(SQL_COUNT_CLOSED)
        n_closed = cur.fetchall()[0][0]
    conn.close()

    print(
        f"[DONE] 期数={totals['periods']} 源行={totals['rows']} 跳过行={totals['skipped_rows']} "
        f"本轮新边={totals['edges_new']} 旧版本关闭={closed}"
    )
    print(f"[DB] node_entity={n_nodes} edge_holding={n_edges} (valid_to 已关闭={n_closed})")
    print(f"[DB] node_entity 分型(type,low_confidence,count): {node_split}")
    print(f"[DONE] progress 落盘: {PROGRESS_PATH}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="A 层十大股东灌入 entity_graph")
    ap.add_argument("--periods", default=None, help="逗号分隔报告期白名单（缺省=全量）")
    args = ap.parse_args()
    periods = [p.strip() for p in args.periods.split(",")] if args.periods else None
    return run(periods)


if __name__ == "__main__":
    sys.exit(main())
