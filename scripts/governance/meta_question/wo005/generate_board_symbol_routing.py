# [BLUEPRINT] MOD-METAQ-WO005-BOARD-ROUTING | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-005
# [MODULE] scripts.governance.meta_question.wo005.generate_board_symbol_routing
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (PG 只读); zephyr.infrastructure.database_service (CH reader); zephyr.data.table_registry (表名品类真源 #ARCH-CH-024); pyyaml
# [CONSUMERS] PQ-0018 复考（映射册+判据重述）; 后续图谱↔行情口径消费方（板块视角聚合）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读两侧库、零写生产表；输出确定性——同输入必同输出（全清单排序+显式
#              tie-break，快照水位取自输入数据而非墙钟，生成器内禁 datetime.now()）；
#              主从口径=Owner 裁定②（TQCENTER 行情为主、知识图谱为从），方向恒为从→主路由；
#              成员断言分级：role∈{参与,主要,龙头,核心}=membership，'提及'=研报弱证据不计成员。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一输入侧读取失败/空表 → 立即抛错退出非零，禁静默产出残缺册。
# [TESTS] 复跑幂等（两次生成 content_hash 相等）即自检；判据数字入册头可人工复核。
# [A_module] module_id=MOD-METAQ-WO005-BOARD-ROUTING | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""generate_board_symbol_routing — 板块口径映射册生成器（WO-005，PQ-0018 施工闭环）。

以 TQCENTER 板块成分（c1_market.sector_constituent，live 且具名 223 板块）为主表，
把知识图谱成员（PG ig_node_company×ig_node，live）经六位裸码 symbol 路由挂到板块，
产出映射册 data/registers/metaq_board_routing/board_symbol_routing.yaml：
节点→板块（primary+secondary，含 evidence 命中符号与来源表）、板块→节点聚合视图、
coverage 统计头、未命中清单及原因分类、PQ-0018 复考前置自检（主从判据重述）。

用法： python scripts/governance/meta_question/wo005/generate_board_symbol_routing.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from zephyr.data.table_registry import get_registry

REPO = Path(__file__).resolve().parents[4]
OUT_DIR = REPO / "data" / "registers" / "metaq_board_routing"
OUT_FILE = OUT_DIR / "board_symbol_routing.yaml"

# 口径常量（真源：Owner 裁定② + WORKORDER_MASTER §WO-005；表名真源=品类册 #ARCH-CH-024；
# 阈值语义见 [INVARIANTS]）
CH_BOARD_TABLE = get_registry().table("market_sector_constituent_880")
CH_SECTOR_LIST_TABLE = get_registry().table("market_sector_list")  # 未命中原因分类的 symbol 宇宙对照表
PG_MEMBER_TABLES = "public.ig_node_company × public.ig_node"
STRONG_ROLES = frozenset({"参与", "主要", "龙头", "核心"})
A_SUFFIXES = ("SH", "SZ", "BJ")
MEMBER_CONTAINMENT_TH = 0.6  # 成员级挂接：节点强成员符号落入板块成分池的比例下限
ANY_CONTAINMENT_TH = 0.0  # advisory 路由：交集≥1 即登记（grade 降档，不计成员断言）
PQ0018_THRESHOLD = 0.80


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{CH_BOARD_TABLE} 由模块常量注入，PG 侧表名经
# ig_node_company/ig_node/stock_concept 实测真源，禁散落字面量。
_SQL_BOARDS = (
    f"select sector_code, sector_name, stock_code from {CH_BOARD_TABLE} where valid_to IS NULL and sector_name != ''"
)
_SQL_GRAPH_MEMBERS = (
    "select c.node_id, c.symbol, c.role, n.name, n.chain_id, n.tier "
    "from ig_node_company c join ig_node n on n.node_id = c.node_id "
    "where c.valid_to is null and n.valid_to is null"
)
_SQL_LIVE_NODE_COUNT = "select count(*) from ig_node where valid_to is null"
_SQL_MARKET_UNIVERSE = f"select symbol_canonical from {CH_SECTOR_LIST_TABLE} FINAL where valid_to IS NULL"
_SQL_CONCEPT_LAYER = "select distinct symbol from stock_concept where valid_to is null"


def _bare(sym: str) -> str:
    return sym.split(".", 1)[0] if "." in sym else sym


def _suffix(sym: str) -> str:
    return sym.split(".", 1)[1] if "." in sym else ""


def fetch_boards():
    """主表：TQCENTER 具名 live 板块 → {code: {name, members}}；剔除 999999 指数占位行。"""
    from zephyr.infrastructure.database_service import DatabaseService

    rows = DatabaseService().get_clickhouse_conn(role="reader").execute(_SQL_BOARDS)
    boards: dict[str, dict] = {}
    for code, name, stock in rows:
        b = boards.setdefault(code, {"name": name, "members": set()})
        bare = _bare(stock)
        if bare == "999999":
            continue
        if _suffix(stock) in A_SUFFIXES:
            b["members"].add(bare)
    if not boards:
        raise RuntimeError("CH 板块主表读取为空，拒绝产出残缺册")
    return boards


def fetch_nodes():
    """从表：图谱 live 节点成员边 → {node_id: {name, chain, tier, syms_all, syms_strong, foreign}}。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute(_SQL_GRAPH_MEMBERS)
    nodes: dict[str, dict] = {}
    for node_id, symbol, role, name, chain_id, tier in cur.fetchall():
        nd = nodes.setdefault(
            node_id,
            {
                "name": name,
                "chain_id": chain_id,
                "tier": tier,
                "syms_all": set(),
                "syms_strong": set(),
                "foreign": set(),
            },
        )
        if _suffix(symbol) in A_SUFFIXES:
            nd["syms_all"].add(_bare(symbol))
            if role in STRONG_ROLES:
                nd["syms_strong"].add(_bare(symbol))
        else:
            nd["foreign"].add(_bare(symbol))
    # 无 live 成员边的 live 节点（未命中分类要计数，不登记逐条）
    cur.execute(_SQL_LIVE_NODE_COUNT)
    live_node_count = cur.fetchone()[0]
    if not nodes:
        raise RuntimeError("PG 图谱成员读取为空，拒绝产出残缺册")
    return nodes, live_node_count


def fetch_market_universe():
    """symbol 有效性对照宇宙（sector_list live，全部 A 股），用于未命中原因分类。"""
    from zephyr.infrastructure.database_service import DatabaseService

    rows = DatabaseService().get_clickhouse_conn(role="reader").execute(_SQL_MARKET_UNIVERSE)
    return {_bare(r[0]) for r in rows}


def fetch_concept_layer():
    """图谱自有 THS 概念层（stock_concept live）symbol 池：未命中节点的回收线索。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute(_SQL_CONCEPT_LAYER)
    return {_bare(r[0]) for r in cur.fetchall()}


def route(nodes, boards):
    """核心路由（确定性）：
    R1 方向恒为 从(节点)→主(板块)；R2 成员断言=STRONG_ROLES；
    R3 primary_board = best-1，排序键 (containment desc, 板块规模 asc, board_code asc)；
       containment≥MEMBER_CONTAINMENT_TH 按评估符号集口径记 grade=member_assertion，
       否则有交集时 grade=mention_support/weak（advisory，不计成员断言）；
    R4 secondary = 除 primary 外全部 containment≥TH 的板块（同键排序，多节点并集去重）。
    """
    sym2boards: dict[str, list] = defaultdict(list)
    for code in sorted(boards):
        for s in sorted(boards[code]["members"]):
            sym2boards[s].append(code)

    def _route_one(nid, syms):
        if not syms:
            return None
        inter = defaultdict(int)
        for s in syms:
            for bc in sym2boards.get(s, ()):
                inter[bc] += 1
        if not inter:
            return None
        ranked = sorted(
            inter.items(),
            key=lambda x: (-(x[1] / len(syms)), len(boards[x[0]]["members"]), x[0]),
        )
        links = []
        for bc, k in ranked:
            cont = k / len(syms)
            if bc == ranked[0][0] or cont >= MEMBER_CONTAINMENT_TH:
                links.append(
                    {
                        "board_code": bc,
                        "containment": round(cont, 4),
                        "matched_symbols": sorted(s for s in syms if s in boards[bc]["members"]),
                    }
                )
        return links

    results = {}
    for nid, nd in nodes.items():
        prim_all = _route_one(nid, nd["syms_all"])
        prim_strong = _route_one(nid, nd["syms_strong"])
        results[nid] = {"links_all": prim_all, "links_strong": prim_strong}
    return results


def anchored_eval(nodes, boards, routed):
    """PQ-0018 复考前置自检（非循环评估域）：
    主题锚定=节点名↔板块名（精确或包含，名称证据独立于成员交集）；
    锚定域上按强成员口径算一致率 Σ|A∩B|/Σ|A|（A=节点强成员集，B=锚定板块中按 R3 键
    择一的成分集）。mis-anchor（细粒度名包含粗板块名）保留在域内——只压低数字，不豁免。"""
    board_names = {bc: b["name"] for bc, b in boards.items()}
    num = den = sum_b = 0
    n_nodes = 0
    for nid in sorted(nodes):
        A = nodes[nid]["syms_strong"]
        nm = nodes[nid]["name"] or ""
        if not A or not nm:
            continue
        cands = [bc for bc, bn in board_names.items() if bn and (bn == nm or (len(bn) >= 2 and (bn in nm or nm in bn)))]
        if not cands:
            continue
        bc = sorted(cands, key=lambda b: (-(len(A & boards[b]["members"])), len(boards[b]["members"]), b))[0]
        num += len(A & boards[bc]["members"])
        den += len(A)
        sum_b += len(boards[bc]["members"])
        n_nodes += 1
    return n_nodes, num, den, sum_b


def _strong_cont(nid, nodes, boards, routed):
    """节点强成员集在其 primary（全符号路由首链）板块中的承认率。"""
    A = nodes[nid]["syms_strong"]
    links = routed[nid]["links_all"]
    if not A or not links:
        return None
    return len(A & boards[links[0]["board_code"]]["members"]) / len(A)


def _routing_sets(nodes, routed) -> tuple[set, set, set]:
    """节点三集合：有 A 股符号的节点 / 有强成员断言的节点 / 任一路由命中的节点。"""
    a_nodes = {n for n, d in nodes.items() if d["syms_all"]}
    strong_nodes = {n for n, d in nodes.items() if d["syms_strong"]}
    routed_any = {n for n in a_nodes if routed[n]["links_all"]}
    return a_nodes, strong_nodes, routed_any


def _member_grade_nodes(strong_nodes, nodes, boards, routed) -> set:
    """成员断言节点集：强成员集在 primary 板块承认率 ≥ MEMBER_CONTAINMENT_TH。"""
    return {
        n
        for n in strong_nodes
        if (_c := _strong_cont(n, nodes, boards, routed)) is not None and _c >= MEMBER_CONTAINMENT_TH
    }


def _node_row(nid, nodes, boards, routed) -> dict | None:
    """单个节点→板块行（从→主路由册主体）；无路由链接返回 None（不入册）。"""
    nd = nodes[nid]
    links = routed[nid]["links_all"]
    if not links:
        return None
    prim = links[0]
    _c = _strong_cont(nid, nodes, boards, routed)
    grade = (
        "member_assertion"
        if _c is not None and _c >= MEMBER_CONTAINMENT_TH
        else ("mention_only" if not nd["syms_strong"] else "weak")
    )
    row = {
        "node_id": nid,
        "node_name": nd["name"],
        "chain_id": nd["chain_id"],
        "tier": nd["tier"],
        "grade": grade,
        "evidence_strength": (
            "solid"
            if len(prim["matched_symbols"]) >= 5
            else ("few" if len(prim["matched_symbols"]) >= 2 else "single_member")
        ),
        "member_count_all": len(nd["syms_all"]),
        "member_count_strong": len(nd["syms_strong"]),
        "primary_board": {
            "board_code": prim["board_code"],
            "board_name": boards[prim["board_code"]]["name"],
            "board_class": "同花顺行业板块" if prim["board_code"].startswith("881") else "同花顺板块/概念(880)",
            "containment": prim["containment"],
            "matched_symbols": prim["matched_symbols"],
            "matched_count": len(prim["matched_symbols"]),
            "evidence": f"symbol_routing via {CH_BOARD_TABLE} ∩ {PG_MEMBER_TABLES}",
        },
        "secondary_boards": [
            {
                "board_code": l["board_code"],
                "board_name": boards[l["board_code"]]["name"],
                "containment": l["containment"],
                "matched_count": len(l["matched_symbols"]),
            }
            for l in links[1:]
        ],
    }
    if nd["foreign"]:
        row["foreign_symbols_excluded"] = sorted(nd["foreign"])
    return row


def _node_rows(a_nodes, nodes, boards, routed) -> list[dict]:
    """节点→板块行集合（node_id 升序，确定性）。"""
    rows = []
    for nid in sorted(a_nodes):
        row = _node_row(nid, nodes, boards, routed)
        if row is not None:
            rows.append(row)
    return rows


def _board_rows(boards, node_rows, nodes) -> list[dict]:
    """板块→节点聚合视图（主侧视角，多节点并集去重）。"""
    board_rows = []
    for bc in sorted(boards):
        linked = [
            r
            for r in node_rows
            if r["primary_board"]["board_code"] == bc or any(s["board_code"] == bc for s in r["secondary_boards"])
        ]
        union = set()
        for r in linked:
            if r["primary_board"]["board_code"] == bc:
                union |= set(r["primary_board"]["matched_symbols"])
            for s in r["secondary_boards"]:
                if s["board_code"] == bc:
                    union |= set(nodes[r["node_id"]]["syms_strong"] & boards[bc]["members"])
        board_rows.append(
            {
                "board_code": bc,
                "board_name": boards[bc]["name"],
                "member_count": len(boards[bc]["members"]),
                "kg_linked_nodes": len(linked),
                "kg_member_union": len(union),
                "nodes": [{"node_id": r["node_id"], "grade": r["grade"]} for r in linked],
            }
        )
    return board_rows


def _unmapped_nodes(nodes, routed_any, live_node_count, universe, concept_layer) -> tuple[list, defaultdict]:
    """未命中清单及原因分类（no_live_member_edges 只聚合计数不逐条入册）。"""
    unmapped = []
    reason_count = defaultdict(int)
    reason_count["no_live_member_edges"] = max(live_node_count - len(nodes), 0)
    for nid in sorted(nodes):
        nd = nodes[nid]
        if nd["syms_all"] and nid in routed_any:
            continue
        if nd["syms_all"]:
            reason = "symbols_out_of_board_pool"  # 有效 A 代码但不在 223 板块任何成分池
        elif nd["foreign"]:
            reason = "foreign_symbols_only"  # 仅港/美/台等外盘代码，超出 A 股板块宇宙
        else:
            reason = "no_live_member_edges"
        hint = bool(nd["syms_all"] & concept_layer) if reason == "symbols_out_of_board_pool" else False
        valid_universe = bool(nd["syms_all"] & universe) if nd["syms_all"] else False
        reason_count[reason] += 1
        if reason == "no_live_member_edges":
            continue  # 聚合计数即可，不逐条入册（体量大、信息量低）
        unmapped.append(
            {
                "node_id": nid,
                "node_name": nd["name"],
                "reason": reason,
                "symbols": sorted(nd["syms_all"] | nd["foreign"])[:10],
                "symbol_in_market_universe": valid_universe,
                "recoverable_via_stock_concept": hint,
            }
        )
    return unmapped, reason_count


def _micro_jaccard(node_rows, nodes, boards) -> tuple[int, int]:
    """精确微 Jaccard（routed 域，透明对照用；主判据见 selfcheck.restated_criterion）。"""
    jac_num = jac_den = 0
    for r in node_rows:
        A = nodes[r["node_id"]]["syms_all"]
        B = boards[r["primary_board"]["board_code"]]["members"]
        jac_num += len(A & B)
        jac_den += len(A | B)
    return jac_num, jac_den


def _selfcheck_pq0018(nodes, boards, node_rows, routed, stats) -> tuple[dict, float, float]:
    """PQ-0018 复考前置自检（主从判据重述）；返回 (selfcheck, anchored_rate, cov_rate)。"""
    an, anum, aden, ansum_b = anchored_eval(nodes, boards, routed)
    anchored_rate = anum / aden if aden else 0.0
    cov_rate = len(stats["routed_any"]) / len(stats["a_nodes"]) if stats["a_nodes"] else 0.0
    jac_num, jac_den = _micro_jaccard(node_rows, nodes, boards)

    selfcheck = {
        "q_id": "PQ-0018",
        "original_threshold_symmetric_jaccard": "≥80%（ig_node_company 聚合 vs TQCENTER 板块成分池对称 Jaccard）",
        "original_exam_value": 0.1345,
        "restated_criterion": (
            "Owner 裁定②确立主从口径后，对称 Jaccard 不再适合作判据：两侧粒度结构性不同"
            "（板块池均值≈50 vs 节点成员均值≈5.3），锚定域即使从侧成员 100% 被承认，对称"
            f"Jaccard 上限也仅 Σ|A|/Σ|B|={aden}/{ansum_b}={aden / ansum_b:.1%}≪80%；本册 routed 域"
            f"实测微 Jaccard={jac_num / jac_den:.1%}（考卷口径 13.45% 同量级），实证对称判据结构性不可达。"
            "判据重述为非对称的『从口径成员被主口径承认率』=Σ|A∩B|/Σ|A|，评估域取主题锚定"
            "（名称证据独立于 symbol 交集，避免路由规则自我实现循环），细粒度 mis-anchor 保留"
            "域内只压低不豁免。重述理由：主从裁定本意即放弃对称口径；量化对照（同花顺/申万"
            "板块↔概念映射工具如 akshare stock_board_*_ths_cons 等开源先例）亦按成分归属做单向"
            "映射校验而非对称重合率。"
        ),
        "symmetric_jaccard_ceiling_anchored_domain": round(aden / ansum_b, 4),
        "primary_metric_name_anchored_strong_recall": {
            "value": round(anchored_rate, 4),
            "formula": "Σ|节点强成员∩锚定板块成分| / Σ|节点强成员|（名称锚定域）",
            "nodes_in_domain": an,
            "numerator": anum,
            "denominator": aden,
            "threshold": PQ0018_THRESHOLD,
            "meets_threshold": anchored_rate >= PQ0018_THRESHOLD,
        },
        "supporting_metrics": {
            "symbol_routing_coverage": {
                "value": round(cov_rate, 4),
                "routed": len(stats["routed_any"]),
                "of_a_share_nodes": len(stats["a_nodes"]),
            },
            "member_assertion_nodes": {
                "value": len(stats["routed_member"]),
                "of_strong_nodes": len(stats["strong_nodes"]),
            },
            "micro_jaccard_routed_symmetric": round(jac_num / jac_den, 4) if jac_den else None,
        },
        "verdict": (
            f"PASS-CANDIDATE：映射后主题锚定一致率 {anchored_rate:.2%} ≥ 80%，可按重述判据复考转绿"
            if anchored_rate >= PQ0018_THRESHOLD
            else f"NOT-YET：映射后一致率 {anchored_rate:.2%} < 80%，复考维持 fail 并回销缺口"
        ),
    }
    return selfcheck, anchored_rate, cov_rate


def _coverage_block(boards, node_rows, stats) -> dict:
    """coverage 统计头（机读计数，全部由输入数据派生）。"""
    return {
        "boards_total": len(boards),
        "boards_881_industry": sum(1 for b in boards if b.startswith("881")),
        "boards_880_sector": sum(1 for b in boards if b.startswith("880")),
        "board_member_pairs": sum(len(b["members"]) for b in boards.values()),
        "graph_live_nodes": stats["live_node_count"],
        "graph_nodes_with_live_members": stats["n_nodes"],
        "graph_a_share_nodes": len(stats["a_nodes"]),
        "routed_any": len(stats["routed_any"]),
        "routed_any_rate": round(stats["cov_rate"], 4),
        "routed_member_grade": len(stats["routed_member"]),
        "strong_nodes_total": len(stats["strong_nodes"]),
        "node_link_rows": len(node_rows),
        "grade_dist": {
            g: sum(1 for r in node_rows if r["grade"] == g) for g in ("member_assertion", "weak", "mention_only")
        },
        "evidence_strength_dist": {
            g: sum(1 for r in node_rows if r["evidence_strength"] == g) for g in ("single_member", "few", "solid")
        },
        "secondary_links": sum(len(r["secondary_boards"]) for r in node_rows),
        "unmapped_reasons": dict(sorted(stats["reason_count"].items())),
        "name_collisions_in_boards": (len(boards) - len({b["name"] for b in boards.values()})),
    }


def _watermarks_block(nodes, coverage) -> dict:
    """快照水位（输入数据侧计数，非墙钟）。"""
    return {
        "ch_boards_rows_scanned": coverage["board_member_pairs"],
        "pg_member_edges_live": sum(len(d["syms_all"] | d["syms_strong"]) for d in nodes.values()),
        "source_tables": [
            CH_BOARD_TABLE,
            PG_MEMBER_TABLES,
            f"{CH_SECTOR_LIST_TABLE}(宇宙对照)",
            "public.stock_concept(回收线索)",
        ],
    }


def main() -> int:
    boards = fetch_boards()
    nodes, live_node_count = fetch_nodes()
    universe = fetch_market_universe()
    concept_layer = fetch_concept_layer()
    routed = route(nodes, boards)

    a_nodes, strong_nodes, routed_any = _routing_sets(nodes, routed)
    routed_member = _member_grade_nodes(strong_nodes, nodes, boards, routed)

    # ---- 节点→板块行（从→主路由册主体）----
    node_rows = _node_rows(a_nodes, nodes, boards, routed)

    # ---- 板块→节点聚合视图（主侧视角，多节点并集去重）----
    board_rows = _board_rows(boards, node_rows, nodes)

    # ---- 未命中清单及原因分类 ----
    unmapped, reason_count = _unmapped_nodes(nodes, routed_any, live_node_count, universe, concept_layer)

    # ---- 复考前置自检 + 统计头 ----
    stats = {
        "a_nodes": a_nodes,
        "strong_nodes": strong_nodes,
        "routed_any": routed_any,
        "routed_member": routed_member,
        "live_node_count": live_node_count,
        "reason_count": reason_count,
        "n_nodes": len(nodes),
    }
    selfcheck, anchored_rate, cov_rate = _selfcheck_pq0018(nodes, boards, node_rows, routed, stats)
    stats["cov_rate"] = cov_rate
    coverage = _coverage_block(boards, node_rows, stats)
    watermarks = _watermarks_block(nodes, coverage)

    body = {
        "schema": "metaq_board_symbol_routing/v1",
        "caliber_ruling": (
            "Owner 裁定②（2026-09-24）：板块口径以 TQCENTER 行情口径为主、知识图谱为从，"
            "按 symbol（六位裸码）路由建映射册。"
        ),
        "aggregation_rule": (
            "R1 方向恒为从(图谱节点)→主(TQCENTER板块)；R2 图谱成员断言分级：role∈"
            "{参与,主要,龙头,核心}计成员(membership)，『提及』(研报弱证据,confidence≈0.6)仅入"
            "evidence 不计成员；R3 primary_board 取 containment(=交集/节点成员)最大之一，tie-break="
            "(containment 降序, 板块规模升序【更细粒度优先】, board_code 字典序升序)，containment≥0.6 "
            "记 grade=member_assertion，未达阈值但有交集记 mention_only/weak（advisory）；R4 多节点对同"
            "板块→板块视图按并集去重聚合（符号只计一次），节点对多板块→primary 唯一 + secondary_boards "
            "登记全部达阈值链接（不截断，保持完整可审计）。外盘符号（KS/HK/TW 等）不入路由、单列留痕。"
        ),
        "determinism": "全清单显式排序+固定 tie-break 键；水位取自输入数据非墙钟；重放=content_hash 相等。",
        "coverage": coverage,
        "selfcheck_pq0018": selfcheck,
        "snapshot_watermarks": watermarks,
        "nodes": node_rows,
        "boards": board_rows,
        "unmapped_nodes": unmapped,
    }
    payload = json.dumps(body, ensure_ascii=False, sort_keys=True, default=str)
    body["meta"] = {
        "generated_by": "scripts/governance/meta_question/wo005/generate_board_symbol_routing.py",
        "workorder": "WO-005",
        "content_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(body, allow_unicode=True, sort_keys=False, width=120)
    OUT_FILE.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_FILE} ({len(text)} chars) hash={body['meta']['content_hash'][:12]}")
    print("anchored_strong_recall =", round(anchored_rate, 4), "routing_coverage =", round(cov_rate, 4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
