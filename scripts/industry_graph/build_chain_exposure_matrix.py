# [BLUEPRINT] MOD-DATA-CHAIN-EXPOSURE
# [BLUEPRINT-NOTE] 研究件无蓝图正本, 登记见 depgraph 设计节点
# [MODULE] scripts.industry_graph.build_chain_exposure_matrix
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service
# [CONSUMERS] 线A 批1 因子构造(上游成本冲击/生猪链/客户动量); E5 链感知聚类; 线D Entity Master 消费方清单
# [STARTUP] manual
# [MATURITY] research
# [INVARIANTS] 只读 PG depgraph(ig_* valid_to IS NULL 现视图); 输出确定性=全部 CSV 行排序后哈希(不含墙钟); 暴露语义=自身角色权重×(1+同链可达衰减和), 跳衰减 0.5/跳 ≤3 跳, 自身项=hop0 基线 1.0; BFS 限同链; 直连边按(from,to,year)取最大权重去重; revenue_pct 一律按百分数/100 钳[0,1], 负值丢行计数; 输出仅 .runtime/tmp/chain_alpha/(禁写生产路径)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 图数据为空->退出码2; 空结果或自检不通过->退出码3
# [TESTS] 内建 --self-check 两遍确定性+完整性断言(证据件, 独立 pytest 待因子入库批)
# [TTL-PROMOTE] 因子入库晋升 permanent 走正门
# [TTL] task_bound
"""链暴露矩阵构建 v1.1（总账 D6，批1 第一件；红蓝对抗修复版）。

从产业链图谱（PG depgraph ig_* 现视图）构建"公司×链×环节"暴露长表：
  1) 环节图: ig_edge (from=上游 -> to=下游)，BFS 限同链可达，跳衰减 0.5^h ≤3 跳；
  2) 公司落位: ig_node_company role 权重(龙头1.0/核心0.8/主要0.6/参与0.4/提及0.2)；
  3) 暴露语义(v1 裁定): up/down_strength = 自身 role 权重 × (1 + Σ 同链可达节点跳衰减),
     自身项即 hop0 基线 1.0——含义是"自身重要度×链连接度"，不是"可达环节自身重要度"
     （后者需可达节点 placement 聚合，留 v2 待 E4 迭代裁定）;
  4) 公司直连边: ig_company_edge revenue_pct 一律按百分数 /100 钳 [0,1]，
     按 (from,to,year) 取最大权重去重。

确定性: 指纹=两份 CSV 全部行排序后 JSON 的 sha256（不含生成日期/墙钟）。

输出 .runtime/tmp/chain_alpha/:
  exposure_matrix.csv / company_edges.csv / summary.json

用法::
    python scripts/industry_graph/build_chain_exposure_matrix.py [--self-check]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from zephyr.infrastructure.database_service import get_db_service

OUT_DIR = Path(".runtime/tmp/chain_alpha")

SQL_CHAINS: str = "SELECT chain_id, name, market FROM ig_chain WHERE status='active' ORDER BY chain_id"
SQL_NODES: str = "SELECT node_id, chain_id, name FROM ig_node WHERE valid_to IS NULL ORDER BY node_id"
SQL_EDGES: str = "SELECT from_node, to_node, edge_type FROM ig_edge WHERE valid_to IS NULL ORDER BY from_node, to_node"
SQL_PLACEMENTS: str = "SELECT node_id, symbol, role FROM ig_node_company WHERE valid_to IS NULL ORDER BY node_id, symbol"
SQL_COMPANY_EDGES: str = "SELECT from_symbol, to_symbol, year, weight_type, revenue_pct, weight, source FROM ig_company_edge WHERE valid_to IS NULL ORDER BY from_symbol, to_symbol, year, source"
ROLE_WEIGHT = {"龙头": 1.0, "核心": 0.8, "主要": 0.6, "参与": 0.4, "提及": 0.2}
HOP_DECAY = 0.5
MAX_HOPS = 3
_UNKNOWN_ROLE_W = 0.4


def _fetch_graph() -> dict:
    db = get_db_service()
    conn = db.get_depgraph_conn(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT chain_id, name, market FROM ig_chain WHERE status='active'"
            " ORDER BY chain_id"
        )
        chains = cur.fetchall()
        cur.execute(
            "SELECT node_id, chain_id, name FROM ig_node WHERE valid_to IS NULL"
            " ORDER BY node_id"
        )
        nodes = cur.fetchall()
        cur.execute(
            "SELECT from_node, to_node, edge_type FROM ig_edge WHERE valid_to IS NULL"
            " ORDER BY from_node, to_node"
        )
        edges = cur.fetchall()
        cur.execute(
            "SELECT node_id, symbol, role FROM ig_node_company WHERE valid_to IS NULL"
            " ORDER BY node_id, symbol"
        )
        placements = cur.fetchall()
        cur.execute(
            SQL_COMPANY_EDGES
        )
        company_edges = cur.fetchall()
        cur.close()
    finally:
        conn.close()
    return {
        "chains": chains,
        "nodes": nodes,
        "edges": edges,
        "placements": placements,
        "company_edges": company_edges,
    }


def _bfs_reach(adj: dict[str, list[str]]) -> dict[str, dict[str, float]]:
    """从每个节点出发沿 adj 的可达权重表: {node: {reachable: weight}}。"""
    reach: dict[str, dict[str, float]] = {}
    for start in adj:
        w: dict[str, float] = {}
        frontier = [start]
        seen = {start}
        hops = 0
        while frontier and hops < MAX_HOPS:
            nxt: list[str] = []
            hops += 1
            decay = HOP_DECAY**hops
            for node in frontier:
                for nb in adj.get(node, ()):
                    if nb in seen:
                        continue
                    seen.add(nb)
                    w[nb] = decay
                    nxt.append(nb)
            frontier = nxt
        reach[start] = w
    return reach


def _build_adj(
    edges: list[dict], node_chain: dict
) -> tuple[dict, dict, dict, int]:
    up_adj: dict[str, list[str]] = defaultdict(list)
    down_adj: dict[str, list[str]] = defaultdict(list)
    composition: dict[str, int] = defaultdict(int)
    cross = 0
    for e in edges:
        et = e.get("edge_type") or "unknown"
        composition[et] += 1
        fn, tn = e["from_node"], e["to_node"]
        src_chain = node_chain.get(fn)
        if src_chain is None or src_chain != node_chain.get(tn):
            cross += 1  # BFS 限同链
            continue
        up_adj[tn].append(fn)    # to 的上游=from
        down_adj[fn].append(tn)  # from 的下游=to
    return up_adj, down_adj, dict(composition), cross


def _build_rows(
    g: dict,
    node_chain: dict,
    chain_name: dict,
    node_name: dict,
    up_reach: dict,
    down_reach: dict,
) -> tuple[list[dict], int]:
    rows: list[dict] = []
    unknown = 0
    for p in g["placements"]:
        nid = p["node_id"]
        cid = node_chain.get(nid)
        if cid is None:
            continue
        role = (p["role"] or "").strip()
        role_w = ROLE_WEIGHT.get(role, _UNKNOWN_ROLE_W)
        if role and role not in ROLE_WEIGHT:
            unknown += 1
        rows.append(
            {
                "symbol": p["symbol"],
                "chain_id": cid,
                "chain_name": chain_name.get(cid, ""),
                "node_id": nid,
                "node_name": node_name.get(nid, ""),
                "role": role,
                "up_strength": round(
                    role_w * (1 + sum(up_reach.get(nid, {}).values())), 4
                ),
                "down_strength": round(
                    role_w * (1 + sum(down_reach.get(nid, {}).values())), 4
                ),
            }
        )
    return rows, unknown


def _dedup_company_edges(company_edges: list[dict]) -> tuple[list[dict], int]:
    dedup: dict[tuple, dict] = {}
    neg = 0
    for e in company_edges:
        raw = e.get("revenue_pct") or 0.0
        w = raw / 100.0 if raw else (float(e["weight"] or 0.0))
        if w < 0:
            neg += 1
            continue
        w = min(w, 1.0)
        key = (e["from_symbol"], e["to_symbol"], e.get("year"))
        prev = dedup.get(key)
        if prev is None or w > prev["weight"]:
            dedup[key] = {
                "from_symbol": e["from_symbol"],
                "to_symbol": e["to_symbol"],
                "year": e.get("year"),
                "weight": round(w, 4),
                "weight_type": e.get("weight_type") or "",
            }
    edge_rows = [
        dedup[k]
        for k in sorted(dedup, key=lambda k: (str(k[0]), str(k[1]), str(k[2])))
    ]
    return edge_rows, neg


def build() -> tuple[list[dict], list[dict], dict]:
    g = _fetch_graph()
    if not g["nodes"] or not g["placements"]:
        print("ERROR: 图数据为空", file=sys.stderr)
        sys.exit(2)

    node_chain = {r["node_id"]: r["chain_id"] for r in g["nodes"]}
    chain_name = {r["chain_id"]: r["name"] for r in g["chains"]}
    node_name = {r["node_id"]: r["name"] for r in g["nodes"]}
    up_adj, down_adj, composition, cross = _build_adj(g["edges"], node_chain)
    up_reach = _bfs_reach(up_adj)
    down_reach = _bfs_reach(down_adj)
    rows, unknown_role = _build_rows(
        g, node_chain, chain_name, node_name, up_reach, down_reach
    )
    edge_rows, neg_dropped = _dedup_company_edges(g["company_edges"])

    summary = {
        "active_chains": len(g["chains"]),
        "nodes": len(g["nodes"]),
        "edges": len(g["edges"]),
        "edge_type_composition": composition,
        "cross_chain_edges_dropped": cross,
        "placements": len(g["placements"]),
        "unknown_role_rows": unknown_role,
        "exposure_rows": len(rows),
        "companies": len({r["symbol"] for r in rows}),
        "company_edges_deduped": len(edge_rows),
        "company_edges_neg_dropped": neg_dropped,
        "params": {
            "role_weight": ROLE_WEIGHT,
            "unknown_role_weight": _UNKNOWN_ROLE_W,
            "hop_decay": HOP_DECAY,
            "max_hops": MAX_HOPS,
            "hop0_baseline": "自身 role 权重×(1+Σ衰减), 自身项=1.0",
            "revenue_pct_semantics": "恒为百分数/100 钳[0,1], 负值丢行",
            "edge_scope": "BFS 限同链; edge_type 全保留(构成见 edge_type_composition)",
        },
    }
    return rows, edge_rows, summary


def _content_fingerprint(rows: list[dict], edge_rows: list[dict]) -> str:
    payload = json.dumps(
        {"rows": sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows),
         "edges": sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in edge_rows)},
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _atomic_write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def write_outputs(
    rows: list[dict], edge_rows: list[dict], summary: dict, fingerprint: str
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not rows or not edge_rows:
        print("ERROR: 空结果，拒绝写出（契约退出码 3）", file=sys.stderr)
        sys.exit(3)
    _atomic_write_csv(
        OUT_DIR / "exposure_matrix.csv", list(rows[0].keys()), rows
    )
    _atomic_write_csv(
        OUT_DIR / "company_edges.csv", list(edge_rows[0].keys()), edge_rows
    )
    summary["fingerprint"] = fingerprint
    summary["generated_on"] = str(date.today())  # 墙钟不入指纹
    tmp = OUT_DIR / "summary.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_DIR / "summary.json")


def self_check() -> int:
    """跑两遍比内容指纹(确定性, 不含墙钟) + 基础完整性。"""
    problems: list[str] = []
    fp1 = fp2 = ""
    for run in (1, 2):
        rows, edge_rows, _summary = build()
        if not rows or not edge_rows:
            print("ERROR: 空结果（契约退出码 3）", file=sys.stderr)
            return 3
        fp = _content_fingerprint(rows, edge_rows)
        bad = [r for r in rows if r["up_strength"] < 0 or r["down_strength"] < 0]
        if bad:
            problems.append(f"negative strength x{len(bad)}")
        if run == 1:
            fp1 = fp
            write_outputs(rows, edge_rows, _summary, fp)
            print(f"run{run}: rows={len(rows)} edges={len(edge_rows)} fp={fp}")
        else:
            fp2 = fp
            print(f"run{run}: fp={fp}")
    if fp1 != fp2:
        problems.append(f"非确定性: {fp1} != {fp2}")
    if problems:
        print("SELF-CHECK FAILED:", problems, file=sys.stderr)
        return 3
    print("SELF-CHECK PASS (内容确定性+完整性)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-check", action="store_true", help="跑两遍验证内容确定性")
    args = ap.parse_args()
    if args.self_check:
        return self_check()
    rows, edge_rows, summary = build()
    if not rows or not edge_rows:
        print("ERROR: 空结果（契约退出码 3）", file=sys.stderr)
        return 3
    fp = _content_fingerprint(rows, edge_rows)
    write_outputs(rows, edge_rows, summary, fp)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("fingerprint:", fp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
