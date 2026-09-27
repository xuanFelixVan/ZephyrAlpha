# [BLUEPRINT] MOD-ENTITY-GRAPH | docs/_working/altdata_line/02_entity_graph_equity_person.md | §
# [MODULE] zephyr.frontend.dashboard.chainmap_equity_graph
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection, 默认 depgraph_reader 只读角色)
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py（chainmap equity 段接线预留，2026-09-27 EC1）
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 只读（六表 SELECT + equity_penetration 函数调用，零写副作用）;
#   现行版本口径=edge_holding.valid_to IS NULL（PIT 追加不覆盖，设计真源六决策②）;
#   徽章/公司卡字段契约与 ACC-F-CHAINMAP-EQUITY-BADGE rev1 逐键兼容（symbol/name/ref/stake_pct/
#   layer/relation/verification/as_of），非上市对手方 symbol='' 靠 name 展示不可点;
#   穿透优先调 PG equity_penetration(TEXT,INT,DATE)（sqlstate 42883 时等价 WITH RECURSIVE 兜底，
#   path 数组防环）; 查询异常由调用方独立降级（不拖垮图谱其余段）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败/查询异常->抛给调用方或返回空结构（各函数注明），不重试不写日志文件
# [TESTS] tests/frontend/test_chainmap_equity_graph.py（mock 连接层，零真实 PG）
# [TTL] permanent
"""entity_graph 六表 → chainmap 股权徽章/公司卡/穿透 查询模块（EC1 接线施工件，只读）。

背景（2026-09-27 业务链流通战役 EC1 车道）：股权底座已建成（commit c007caac86）——
scripts/entity_graph/ 三脚本把 akshare 十大股东灌进 PG depgraph 域六表
（node_entity/node_person/node_company/edge_holding/edge_role/edge_link，140,725 节点/150 万边），
而前端 /api/chainmap-cluster 与 /api/chainmap-company 的 equity 段仍读旧表 ig_equity_edge
（仅 804 条 THS 被投数据）。本模块提供六表现行版本（valid_to IS NULL）的三个查询面：

1. :func:`company_equity_summary`  按公司键（代码/entity_id/规范名）查现行股权聚合
   （控 N/被 M 控 + 明细行，联 node_company/node_person 富化行业/出生年）。
2. :func:`penetrate_upstream`  3 跳向上股东穿透（优先 PG equity_penetration 函数，
   函数不可用自动降级等价 WITH RECURSIVE，path 数组防环）+ 路径重构 :func:`penetration_paths`。
3. :func:`equity_domain_for_company` / :func:`cluster_equity_badge_rows`
   /api/chainmap-company equity 段与 /api/chainmap-cluster 徽章聚合的六表替换件，
   响应字段契约与 ACC-F-CHAINMAP-EQUITY-BADGE rev1 逐键兼容，切换方零前端改动。

技术栈口径校准（2026-09-27，wo_equity_penetration_v1.md 滞后项）：工单 S1 写的是 ClickHouse
DateTime64(3)+显式时区；实际底座=PostgreSQL depgraph 域六表（apply_entity_graph_ddl.py 为 DDL
真源），PIT 双轴=valid_from/valid_to DATE + ingested_at TIMESTAMPTZ。本模块按 PG 底座实现。

# [ALGO_FLOW] external: docs/03_modules/_domain_frontend/algo_flow/chainmap_equity_graph.yaml
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:  # pragma: no cover — 仅类型标注；psycopg2 由 depgraph_schema 延迟导入
    import psycopg2.extensions

__all__: Final = [
    "normalize_company_key",
    "connect",
    "resolve_entity",
    "company_equity_summary",
    "penetrate_upstream",
    "penetration_paths",
    "equity_domain_for_company",
    "cluster_equity_badge_rows",
    "PENETRATION_FN_STATE",
]

# sqlstate 42883 = undefined_function：PG 库未部署 equity_penetration 函数时的降级信号
PENETRATION_FN_STATE = "42883"

# 穿透深度护栏（M1 期=3 跳；上限 8 防失控递归）
_DEPTH_MIN, _DEPTH_MAX = 1, 8
# 路径重构输出护栏：防超大连通子图拖垮响应
_PATHS_CAP = 50
# 单公司单侧明细行上限（徽章浮层明细另由调用方按 ACC 口径截断）
_ROWS_CAP = 200

# 现行版本股权聚合：控（from=本司→我投了谁）/被控（to=本司→谁投了我）双向一条 SQL 各半。
# 联 node_company（行业）/node_person（出生年）按对手方类型富化——设计真源 §2 明细表挂点
_SQL_EQUITY_ONE_SIDE = (
    "SELECT e.to_entity, ne.name, ne.symbol, ne.entity_type, e.stake_pct, e.role, e.rank_no, "
    "nc.industry, np.birth_year, e.valid_from, e.announce_date, e.source "
    "FROM edge_holding e "
    "JOIN node_entity ne ON ne.entity_id = e.{peer}_entity "
    "LEFT JOIN node_company nc ON nc.uscc = ne.uscc "
    "LEFT JOIN node_person np ON np.person_id = ne.entity_id "
    "WHERE e.{me}_entity = %s AND e.valid_to IS NULL "
    "ORDER BY e.stake_pct DESC NULLS LAST, ne.name "
    f"LIMIT {_ROWS_CAP}"
)

# 实体解析：entity_id/代码变体/规范名多键（equity_penetration p_root 同口径）。
# 代码变体=原始输入+裸码（去 .SH/.SZ/.BJ/.HK 后缀）：底座 symbol 锚为带后缀形态
# （实测 akshare_top10 源 entity.symbol='600566.SH'，2026-09-27 EC1），裸码兜底防源口径迁移
_SQL_RESOLVE_ENTITY = (
    "SELECT entity_id, entity_type, name, name_norm, symbol, uscc, low_confidence "
    "FROM node_entity "
    "WHERE entity_id = ANY(%s) OR symbol = ANY(%s) OR name_norm = %s "
    "ORDER BY (symbol IS NOT NULL) DESC, entity_id LIMIT 1"
)

# 三跳向上穿透兜底 SQL（与 apply_entity_graph_ddl.py equity_penetration 函数体逐句等价；
# 根已先经 resolve_entity 归一为 entity_id，故基例直接 to_entity=%s；path 数组防环）
_SQL_PENETRATE_FALLBACK = (
    "WITH RECURSIVE walk AS ("
    "SELECT 1 AS depth, h.from_entity, h.to_entity, h.role, h.stake_pct, h.valid_from, "
    "ARRAY[h.to_entity, h.from_entity] AS path "
    "FROM edge_holding h "
    "WHERE h.to_entity = %s AND h.valid_to IS NULL "
    "AND (%s::DATE IS NULL OR h.valid_from >= %s) "
    "UNION ALL "
    "SELECT w.depth + 1, h.from_entity, h.to_entity, h.role, h.stake_pct, h.valid_from, "
    "w.path || h.from_entity "
    "FROM walk w "
    "JOIN edge_holding h ON h.to_entity = w.from_entity "
    "WHERE h.valid_to IS NULL "
    "AND (%s::DATE IS NULL OR h.valid_from >= %s) "
    "AND w.depth < %s "
    "AND NOT (h.from_entity = ANY(w.path)) "
    ") "
    "SELECT w.depth, w.from_entity, fe.name, fe.entity_type, "
    "w.to_entity, te.name, w.role, w.stake_pct, w.valid_from "
    "FROM walk w "
    "JOIN node_entity fe ON fe.entity_id = w.from_entity "
    "JOIN node_entity te ON te.entity_id = w.to_entity "
    "ORDER BY w.depth, w.to_entity, w.stake_pct DESC NULLS LAST"
)

# PG 内建穿透函数调用（apply_entity_graph_ddl.py DDL 真源署名签名 (TEXT, INT, DATE)）
_SQL_PENETRATE_FN = (
    "SELECT depth, from_entity, from_name, from_type, to_entity, to_name, role, stake_pct, valid_from "
    "FROM equity_penetration(%s, %s, %s)"
)

# 簇徽章批量聚合（/api/chainmap-cluster equity 段六表替换件，字段契约=_SQL_CM_EQ_AGG 行形）：
# 环节落位公司（ig_node_company 真源不动）× node_entity.symbol 锚 × edge_holding 现行版本；
# 上市对手方带 symbol，person/非上市对手方 symbol='' 靠 name 展示（ACC item1 口径）
_SQL_CLUSTER_BADGES = (
    "SELECT nc.node_id, 'out' AS dir, peer.symbol, peer.name, e.stake_pct, e.role, "
    "COALESCE(e.announce_date, e.valid_from) AS as_of, e.source, peer.entity_type AS etype "
    "FROM edge_holding e "
    "JOIN node_entity me ON me.entity_id = e.from_entity AND me.symbol IS NOT NULL "
    "JOIN ig_node_company nc ON nc.valid_to IS NULL AND nc.symbol = me.symbol "
    "JOIN node_entity peer ON peer.entity_id = e.to_entity "
    "WHERE e.valid_to IS NULL "
    "AND nc.node_id IN (SELECT node_id FROM ig_node WHERE chain_id = ANY(%s)) "
    "UNION ALL "
    "SELECT nc.node_id, 'in' AS dir, peer.symbol, peer.name, e.stake_pct, e.role, "
    "COALESCE(e.announce_date, e.valid_from) AS as_of, e.source, peer.entity_type AS etype "
    "FROM edge_holding e "
    "JOIN node_entity me ON me.entity_id = e.to_entity AND me.symbol IS NOT NULL "
    "JOIN ig_node_company nc ON nc.valid_to IS NULL AND nc.symbol = me.symbol "
    "JOIN node_entity peer ON peer.entity_id = e.from_entity "
    "WHERE e.valid_to IS NULL "
    "AND nc.node_id IN (SELECT node_id FROM ig_node WHERE chain_id = ANY(%s)) "
    "LIMIT %s"
)


def normalize_company_key(key: str) -> str:
    """600566.SH → 600566（CH 行情 6 位裸码口径）；.SH/.SZ/.BJ/.HK 后缀皆剥；其他输入原样返回。"""
    s = (key or "").strip()
    return s.split(".")[0] if s.upper().endswith((".SH", ".SZ", ".BJ", ".HK")) else s


def connect() -> psycopg2.extensions.connection:
    """depgraph PG 只读连接（depgraph_reader 角色，与 api_server._cm_pg 同入口同角色）。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection()


def _symbol_variants(raw: str) -> list[str]:
    """输入代码 → 上市代码变体清单（原始+裸码+确定性后缀猜测）。

    底座 symbol 锚实测为带后缀形态（'600566.SH'，2026-09-27 EC1），裸码输入须补后缀
    候选才能命中唯一索引；后缀规则与 api_server.chainmap_company 归一口径一致
    （6 开头=SH，0/3 开头=SZ，其余 6 位=BJ），5 位数字=HK。
    """
    out: list[str] = []
    for v in (raw, raw.upper(), normalize_company_key(raw), normalize_company_key(raw).upper()):
        if v and v not in out:
            out.append(v)
    bare = normalize_company_key(raw)
    suffix = ""
    if bare.isdigit() and len(bare) == 6:
        suffix = ".SH" if bare.startswith("6") else (".SZ" if bare[0] in "03" else ".BJ")
    elif bare.isdigit() and len(bare) == 5:
        suffix = ".HK"
    if suffix:
        for v in (bare + suffix, (bare + suffix).upper()):
            if v not in out:
                out.append(v)
    return out


def resolve_entity(cur: psycopg2.extensions.cursor, company_key: str) -> dict[str, Any] | None:
    """按 代码（裸码/带后缀皆可）/entity_id/规范名 解析实体；未命中返回 None。"""

    raw = (company_key or "").strip()
    if not raw:
        return None
    variants = _symbol_variants(raw)
    cur.execute(_SQL_RESOLVE_ENTITY, (variants, variants, raw))
    row = cur.fetchone()
    if not row:
        return None
    return {
        "entity_id": row[0],
        "entity_type": row[1],
        "name": row[2],
        "name_norm": row[3],
        "symbol": row[4] or "",
        "uscc": row[5],
        "low_confidence": bool(row[6]),
    }


def _detail_row(raw: tuple) -> dict[str, Any]:
    """聚合明细行整形：stake 两位小数；对手方 symbol 可空（person/非上市靠 name 展示）。"""
    (eid, name, symbol, etype, stake, role, rank_no, industry, birth_year, vfrom, announce, source) = raw
    return {
        "entity_id": eid,
        "name": name or "",
        "symbol": symbol or "",
        "entity_type": etype or "",
        "stake_pct": None if stake is None else round(float(stake), 2),
        "role": role or "",
        "rank_no": int(rank_no) if rank_no is not None else None,
        "industry": industry or "",
        "birth_year": int(birth_year) if birth_year is not None else None,
        "valid_from": str(vfrom) if vfrom else None,
        "announce_date": str(announce) if announce else None,
        "source": source or "",
    }


def company_equity_summary(conn: psycopg2.extensions.connection, company_key: str) -> dict[str, Any]:
    """按公司键查现行版本股权聚合（控 N/被 M 控 + 双向明细，edge_holding valid_to IS NULL）。

    未命中实体→{"entity": None, ...空计数}；查询异常向上抛（调用方独立降级）。
    """
    out: dict[str, Any] = {
        "entity": None,
        "controls_count": 0,
        "controlled_by_count": 0,
        "controls": [],
        "controlled_by": [],
    }
    with conn.cursor() as cur:
        ent = resolve_entity(cur, company_key)
    if not ent:
        return out
    out["entity"] = ent
    with conn.cursor() as cur:
        cur.execute(_SQL_EQUITY_ONE_SIDE.format(me="from", peer="to"), (ent["entity_id"],))
        out["controls"] = [_detail_row(r) for r in cur.fetchall()]
        cur.execute(_SQL_EQUITY_ONE_SIDE.format(me="to", peer="from"), (ent["entity_id"],))
        out["controlled_by"] = [_detail_row(r) for r in cur.fetchall()]
    out["controls_count"] = len(out["controls"])
    out["controlled_by_count"] = len(out["controlled_by"])
    return out


def _clamp_depth(max_depth: int | None) -> int:
    if max_depth is None:
        return 3
    return max(_DEPTH_MIN, min(int(max_depth), _DEPTH_MAX))


def _penetration_row(raw: tuple) -> dict[str, Any]:
    return {
        "depth": int(raw[0]),
        "from_entity": raw[1],
        "from_name": raw[2] or "",
        "from_type": raw[3] or "",
        "to_entity": raw[4],
        "to_name": raw[5] or "",
        "role": raw[6] or "",
        "stake_pct": None if raw[7] is None else round(float(raw[7]), 2),
        "valid_from": str(raw[8]) if raw[8] else None,
    }


def penetrate_upstream(
    conn: psycopg2.extensions.connection,
    company_key: str,
    max_depth: int = 3,
    min_valid_from: str | None = None,
) -> dict[str, Any]:
    """N 跳向上股东穿透（默认 3 跳，现行版本 valid_to IS NULL）。

    优先调 PG equity_penetration(TEXT, INT, DATE)（DDL 真源已部署 STABLE 函数）；
    函数不存在（sqlstate 42883）自动降级等价 WITH RECURSIVE（path 数组防环）。
    返回 {"root": <实体或 None>, "engine": "pg_function"|"sql_fallback", "rows": [边列表]}；
    根实体未命中→rows=[]；查询异常向上抛。
    """
    with conn.cursor() as cur:
        root = resolve_entity(cur, company_key)
    if not root:
        return {"root": None, "engine": "pg_function", "rows": []}
    depth = _clamp_depth(max_depth)
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_PENETRATE_FN, (root["entity_id"], depth, min_valid_from))
            rows = [_penetration_row(r) for r in cur.fetchall()]
        return {"root": root, "engine": "pg_function", "rows": rows}
    except Exception as exc:  # noqa: BLE001 — 仅 42883（函数未部署）走兜底，其余原样上抛
        if getattr(exc, "sqlstate", None) != PENETRATION_FN_STATE:
            raise
    # 参数序：基例(root,min_vf,min_vf) + 递归(min_vf,min_vf,depth) = 7 占位
    with conn.cursor() as cur:
        cur.execute(
            _SQL_PENETRATE_FALLBACK,
            (root["entity_id"],) + (min_valid_from, min_valid_from) * 2 + (depth,),
        )
        rows = [_penetration_row(r) for r in cur.fetchall()]
    return {"root": root, "engine": "sql_fallback", "rows": rows}


def penetration_paths(root_entity_id: str, rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """把穿透边列表重构为 根→叶 股东链路径（DFS，环由 visited 拦截，输出上限 _PATHS_CAP）。

    每条路径=根开始逐跳的边序列；叶=rows 中无更上游一跳的节点。仅服务报告/冒烟展示，
    不承担图正确性责任（正确性真源=PG 函数/兜底 SQL 的 path 防环）。
    """
    up: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        up.setdefault(r["to_entity"], []).append(r)
    paths: list[list[dict[str, Any]]] = []

    def _walk(node: str, chain: list[dict[str, Any]], visited: set[str]) -> None:
        if len(paths) >= _PATHS_CAP:
            return
        edges = [e for e in up.get(node, []) if e["from_entity"] not in visited]
        if not edges:
            if chain:
                paths.append(chain)
            return
        for e in edges:
            _walk(e["from_entity"], chain + [e], visited | {e["from_entity"]})

    _walk(root_entity_id, [], {root_entity_id})
    return paths


def _contract_row(edge_from: tuple, peer: tuple) -> dict[str, Any]:
    """公司卡 equity 行整形（ACC-F-CHAINMAP-EQUITY-BADGE/公司卡七域契约逐键兼容）。

    契约键：symbol/name/ref/stake_pct/layer/relation/verification/as_of。
    六表映射：relation←role、verification←source（诚实标注数据源系）、as_of←announce/valid_from；
    非上市对手方（person/无 symbol 实体）symbol='' 靠 name 展示、不可点（ref 留空=旧契约语义）。
    """
    (stake, role, vfrom, announce, source) = edge_from
    (eid, name, symbol, etype) = peer
    return {
        "symbol": symbol or "",
        "name": name or "",
        "ref": "",
        "stake_pct": None if stake is None else round(float(stake), 2),
        "layer": 1,
        "relation": role or "",
        "verification": source or "",
        "as_of": str(announce or vfrom) if (announce or vfrom) else None,
    }


_SQL_COMPANY_SIDE_ROWS = (
    "SELECT e.stake_pct, e.role, e.valid_from, e.announce_date, e.source, "
    "peer.entity_id, peer.name, peer.symbol, peer.entity_type "
    "FROM edge_holding e "
    "JOIN node_entity peer ON peer.entity_id = e.{peer}_entity "
    "WHERE e.{me}_entity = %s AND e.valid_to IS NULL "
    "ORDER BY e.stake_pct DESC NULLS LAST, peer.name "
    f"LIMIT {_ROWS_CAP}"
)


def equity_domain_for_company(conn: psycopg2.extensions.connection, symbol: str) -> dict[str, Any]:
    """/api/chainmap-company equity 段六表替换件（holdings_in=我投了谁/held_by=谁投了我）。

    响应逐键兼容旧 ig_equity_edge 版（多带 source 字段标注数据系=entity_graph）；
    未命中实体/查询异常返回空结构（调用方独立降级口径不变）。
    """
    out: dict[str, Any] = {
        "holdings_in": [],
        "held_by": [],
        "n_holdings": 0,
        "n_held": 0,
        "source": "entity_graph",
    }
    try:
        with conn.cursor() as cur:
            root = resolve_entity(cur, symbol)
        if not root:
            return out
        with conn.cursor() as cur:
            cur.execute(_SQL_COMPANY_SIDE_ROWS.format(me="from", peer="to"), (root["entity_id"],))
            out["holdings_in"] = [_contract_row(r[:5], r[5:]) for r in cur.fetchall()]
            cur.execute(_SQL_COMPANY_SIDE_ROWS.format(me="to", peer="from"), (root["entity_id"],))
            out["held_by"] = [_contract_row(r[:5], r[5:]) for r in cur.fetchall()]
        out["n_holdings"] = len(out["holdings_in"])
        out["n_held"] = len(out["held_by"])
    except Exception:  # noqa: BLE001 — 契约性独立降级：查询任何异常返回空结构（ACC item7 口径）
        return {
            "holdings_in": [],
            "held_by": [],
            "n_holdings": 0,
            "n_held": 0,
            "source": "entity_graph",
        }
    return out


def _main(argv: list[str] | None = None) -> int:
    """独立冒烟/查证 CLI（m11-perm-manual-legitimate：人工触发一次性查询，零常驻零定时）。

    用法：python -m zephyr.frontend.dashboard.chainmap_equity_graph <公司键> [--depth N] [--json]
    只读（depgraph_reader 角色）；输出现行聚合+3 跳穿透摘要，供验收冒烟与人工核查复用。
    """
    import argparse
    import json as _json

    ap = argparse.ArgumentParser(description="entity_graph 六表股权查询（只读冒烟 CLI）")
    ap.add_argument("company", help="公司键：股票代码（600566 / 600566.SH）/ entity_id / 规范名")
    ap.add_argument("--depth", type=int, default=3, help="向上穿透跳数（默认 3）")
    ap.add_argument("--json", action="store_true", help="输出完整 JSON（默认人读摘要）")
    args = ap.parse_args(argv)

    conn = connect()
    try:
        summary = company_equity_summary(conn, args.company)
        pen = penetrate_upstream(conn, args.company, max_depth=args.depth)
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001 — best-effort 关闭（池自愈回收，关闭失败不掩盖查询结果）
            pass
    if args.json:
        print(
            _json.dumps(
                {"summary": summary, "penetration_engine": pen["engine"], "penetration_rows": pen["rows"]},
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    root = pen.get("root") or {}
    print(
        "[equity] %s (%s): 控 %d / 被 %d 控"
        % (root.get("name", "?"), args.company, summary["controls_count"], summary["controlled_by_count"])
    )
    print("[penetration] engine=%s rows=%d depth<=%d" % (pen["engine"], len(pen["rows"]), args.depth))
    for e in pen["rows"][:10]:
        print(
            "  d%d %s --(%s %.2f%%)--> %s" % (e["depth"], e["from_name"], e["role"], e["stake_pct"] or -1, e["to_name"])
        )
    if root:
        for p in penetration_paths(root["entity_id"], pen["rows"])[:5]:
            print("  path(%d): %s" % (len(p), " <- ".join([root.get("name", "?")] + [x["from_name"] for x in p])))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


def cluster_equity_badge_rows(
    conn: psycopg2.extensions.connection, chain_ids: list[str], limit: int = 800
) -> list[dict[str, Any]]:
    """/api/chainmap-cluster 徽章聚合六表替换件（环节×现行股权边，簇级 LIMIT 防大簇失控）。

    行形与旧 _SQL_CM_EQ_AGG 消费契约对齐：node_id/dir/symbol/name/ref/stake_pct/
    relation/verification/as_of（dir=out=环节公司对外投资控、in=被控）。
    """
    if not chain_ids:
        return []
    rows: list[dict[str, Any]] = []
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_CLUSTER_BADGES, (list(chain_ids), list(chain_ids), int(limit)))
            for nid, dirn, sym, name, stake, role, asof, source, etype in cur.fetchall():
                rows.append(
                    {
                        "node_id": nid,
                        "dir": dirn,
                        "symbol": sym or "",
                        "name": name or "",
                        "ref": "",
                        "stake_pct": None if stake is None else round(float(stake), 2),
                        "relation": role or "",
                        "verification": source or "",
                        "etype": etype or "",
                        "as_of": str(asof) if asof else None,
                    }
                )
    except Exception:  # noqa: BLE001 — 契约性独立降级：徽章缺失不影响簇图其余段（ACC item7 口径）
        return []
    return rows
