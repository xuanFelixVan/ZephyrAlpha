# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.generate_node_binding_candidates
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（同口径判据复算/旁挂册 CAS 写）; zephyr.governance.depgraph_schema（PG 只读）;
#                zephyr.infrastructure.database_service（CH 只读 reader 角色）;
#                zephyr.data.table_registry + zephyr.data.ch_reader（stock_basic 在市反查，与 ingest 通道同口径）
# [CONSUMERS] apply_node_bindings.py（唯一写入者读本册）；recompute_pq0064.py（投影 vs 实盘对账）；案卷 WO-006.yaml
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只产候选不写库（写面集中 apply 件，RULE-DATA-OPS 三验证单点留痕）；候选一律只指向
#            "未挂接 + 非已并入" 节点（已并入节点禁补挂=同链同司双计防线，理由见案卷 convergence_ruling）；
#            (node_id,symbol) 全局去重保最高 confidence；symbol 必过 cn 正则且在市（stock_basic valid_to IS NULL）；
#            每源 role/confidence/匹配口径固定，禁为凑达标放宽阈值（实测：子串源预算从 60 行/节点放宽到
#            120 行/节点+泛概念 200 成员，行数 8k→33k 而活跃口径 A 档链反降 606+31→623，即"量不换来达标"，
#            故本件取精度优先，见 meta.precision_evidence）；
#            升档只认跨真源族（概念/行业族=同花顺 lineage 视为一族，与营收归因族、公司简介文本族互证才 0.7）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达→抛出非零退出；CH 不可达→抛 SourceCUnreachable（源 C 整体记 0 产出并留证，禁静默半册）；
#                  stock_basic 反查失败→降级 warn 跳过在市过滤（degraded 计数留痕）
# [TESTS] 探针 .runtime/tmp/st-metaq-gc-20260924/wo006/p9_sizes.py + p11_tight.py + p12_union.py
#         （各源量级与放宽反证）；apply 后 recompute_pq0064.py 实盘增量须与本件 meta.projection 逐项相等
# [TTL] task_bound
"""WO-006 三源补挂候选生成器（A=stock_concept 概念 / B=同名穿透 / C=同花顺在产 lineage / D=node_ref 营收归因）。

用法::

    python scripts/governance/meta_question/wo006/generate_node_binding_candidates.py

产出 `data/registers/metaq_node_binding/node_binding_candidates_wo006.yaml`（列式旁挂册，引用即重放），
meta.projection 落"不落库同口径投影"（含 Owner 门位联动的微链退役情景）。

源 C 说明：iFinD 直连已退役（见 probe_source_c_ths.py 取证册，真登录返回码 -2），但同花顺 lineage
在库在产通道可用——CH `c1_market.concept_board(_constituent)`（data_source='akshare_ths'，SCD-2，
最新 valid_from=2026-09-23）+ `c1_market.stock_profile_ths`（同花顺公司档案：三级行业+简介全文）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wo006_common as W  # noqa: E402

from zephyr.data.table_registry import get_registry  # noqa: E402  （表名品类真源 #ARCH-CH-024）

REG_PATH = W.REG_DIR / "node_binding_candidates_wo006.yaml"
SYMBOL_CN_RE = re.compile(r"^\d{6}\.(SH|SZ|BJ)$")
CONCEPT_AS_OF = "2026-09-14"  # stock_concept 在册快照日（源 A 的 valid_from）

# ---- 每源固定口径（对齐 industry_graph_field_dictionary.yaml：ths_export 固定 0.6；
#      websearch/corpus_rag ≤0.7 且双独立源互证才 0.7；派生/启发一律压在下限）----
SRC = {
    "A1": dict(
        group="concept_ths",
        role="参与",
        conf=0.60,
        cap=300,
        doc="wo006|srcA1_stock_concept_exact",
        note="PG stock_concept：节点名==概念名（同义直连）",
    ),
    "A2": dict(
        group="concept_ths",
        role="提及",
        conf=0.45,
        cap=60,
        doc="wo006|srcA2_stock_concept_substr",
        note="PG stock_concept：名称子串互含（下位/同域启发）",
    ),
    "B": dict(
        group="graph_internal",
        role="提及",
        conf=0.40,
        cap=60,
        doc="wo006|srcB_symbol_penetration",
        note="同名跨链成员穿透（派生，零新信息，禁同链穿透）",
    ),
    "C1": dict(
        group="concept_ths",
        role="参与",
        conf=0.60,
        cap=300,
        doc="wo006|srcC1_ths_concept_board",
        note="CH akshare_ths 概念板：节点名==板名（在册在产，2026-09-23）",
    ),
    "C2": dict(
        group="concept_ths",
        role="提及",
        conf=0.45,
        cap=60,
        doc="wo006|srcC2_ths_concept_substr",
        note="CH akshare_ths 概念板：名称子串互含（下位/同域启发）",
    ),
    "C3": dict(
        group="concept_ths",
        role="参与",
        conf=0.60,
        cap=400,
        doc="wo006|srcC3_ths_industry",
        note="CH stock_profile_ths 同花顺三级行业==节点名",
    ),
    "C4": dict(
        group="profile_text",
        role="提及",
        conf=0.45,
        cap=60,
        doc="wo006|srcC4_ths_profile_mention",
        note="CH stock_profile_ths 公司简介全文提及节点名",
    ),
    "D": dict(
        group="revenue",
        role="按 revenue_pct 三档",
        conf=0.60,
        cap=400,
        doc="wo006|srcD_node_ref",
        note="PG ig_product_revenue.node_ref 营收归因（实质源，独立族）",
    ),
}
SUBSTR_MAX_MEMBERS = 100  # 泛概念（国企改革/机器人概念 400+ 成员）不作启发式挂接——精度防线
SUBSTR_MIN_LEN = 3  # 短于此的名称做子串匹配假阳率不可控
MENTION_MIN_LEN = 4  # 公司简介全文提及：≥4 字才计（3 字以内多为泛词）

# 放宽反证（p12_union.py 实测）：子串源若放宽到 成员≤200 + 120 行/节点，行数 8k→33k，
# 活跃口径 A 档链 623 < 精度优先配置的 637 —— 量换不来达标，故取精度优先。
PRECISION_EVIDENCE = {
    "loose_substr_200_members_120_per_node": {"nodes": 302, "rows": 32648, "aclass_active_projected": 623},
    "tight_substr_100_members_60_per_node": {"nodes": 86, "rows": 5120},
    "conclusion": "放宽启发式子串预算只增污染不增达标链（实测反证），故精度优先、差额如实报出",
}


# CH 侧在产通道表名真源（#ARCH-CH-024：一律由品类册派生，禁字面量；下方 SQL 以 f-string 注入）
_TBL_CONCEPT_BOARD = get_registry().table("market_concept_board")
_TBL_CONCEPT_BOARD_CONSTITUENT = get_registry().table("market_concept_board_constituent")
_TBL_STOCK_PROFILE_THS = get_registry().table("meta_stock_profile_ths")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{tbl}=table_registry 运行期解析的全限定表名（禁硬编码
# 绕过真源）、{cutoff}=PIT 闭卷切点真源 wo006_common.CUTOFF——两者一律由调用点 .format() 注入，
# 禁把表名/日期字面量写进常量。_SQL_STOCK_CONCEPT_MEMBERS 的 POSIX 正则含 {6} 量词，
# 故该条直传不做 .format()（避免花括号二次解释）。_SQL_CH_* 三条无运行期参数，表名改由上方品类
# 常量以 f-string 注入（渲染值与占位法逐字相同，真源仍唯一）。
_SQL_ALIVE_SYMBOLS = "SELECT DISTINCT symbol_canonical FROM {tbl} FINAL WHERE valid_to IS NULL"
_SQL_UNATTACHED_TARGETS = (
    "select n.node_id, n.chain_id, n.name from ig_node n\n"
    "                where n.name not like '%已并入%'\n"
    "                  and not exists (select 1 from ig_node_company x where x.node_id = n.node_id)"
)
_SQL_STOCK_CONCEPT_MEMBERS = (
    "select concept, symbol from stock_concept\n"
    "            where valid_to is null and symbol ~ '^[0-9]{6}[.](SH|SZ|BJ)$' group by 1,2"
)
_SQL_DONORS = (
    "select n.name, n.chain_id, n.node_id, nc.symbol, nc.confidence\n"
    "             from ig_node_company nc join ig_node n on n.node_id = nc.node_id\n"
    "            where n.name not like '%已并入%' and nc.valid_to is null"
)
_SQL_NODE_REF = (
    "select n.node_id, p.symbol, max(coalesce(p.revenue_pct, 0)), min(p.year), max(p.year),\n"
    "                   min(p.report_date)::text, string_agg(distinct p.source, ','),\n"
    "                   (array_agg(p.product order by coalesce(p.revenue_pct, 0) desc nulls last))[1]\n"
    "              from ig_product_revenue p join ig_node n on n.node_id = p.node_ref\n"
    "             where p.node_ref is not null\n"
    "               and (p.report_date is null or p.report_date <= date '{cutoff}')\n"
    "               and n.name not like '%已并入%'\n"
    "               and not exists (select 1 from ig_node_company x where x.node_id = n.node_id)\n"
    "          group by 1, 2"
)
_SQL_CH_BOARD_MEMBERS = (
    "select b.board_name, k.symbol_canonical\n"
    f"                 from {_TBL_CONCEPT_BOARD_CONSTITUENT} k\n"
    f"                 join {_TBL_CONCEPT_BOARD} b using (board_code)\n"
    "                where k.valid_to is null and b.valid_to is null\n"
    "                  and k.data_source = 'akshare_ths'\n"
    "                group by 1, 2"
)
_SQL_CH_THS_FRESHNESS = (
    f"select max(valid_from), max(ingest_ts) from {_TBL_CONCEPT_BOARD_CONSTITUENT}\n"
    "                where data_source='akshare_ths' and valid_to is null"
)
_SQL_CH_STOCK_PROFILES = (
    "select symbol_canonical, industry_ths_l1, industry_ths_l2, industry_ths_l3, profile\n"
    f"                 from {_TBL_STOCK_PROFILE_THS}"
)


class SourceCUnreachable(RuntimeError):
    """源 C（同花顺在库在产通道）不可达——整体记 0 产出并留证，禁静默半册。"""


def _alive_symbols() -> tuple[set[str], bool]:
    """ingest 通道同款在市反查（同源 SQL，防"过我的闸却过不了通道的闸"）。"""
    try:
        from zephyr.data import ch_reader
        from zephyr.data.table_registry import get_registry

        tbl = get_registry().table("meta_stock_basic")
        tsv = ch_reader.query(_SQL_ALIVE_SYMBOLS.format(tbl=tbl))
        return {ln.strip().split("\t")[0] for ln in tsv.strip().splitlines() if ln.strip()}, False
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] stock_basic 反查降级（跳过在市过滤）: {e}")
        return set(), True


def _targets(conn) -> dict[str, dict]:
    """补挂对象=未挂接活跃节点（已并入节点排除，理由见模块头 INVARIANTS）。"""
    return {r[0]: {"node_id": r[0], "chain_id": r[1], "name": r[2]} for r in W.rows(_SQL_UNATTACHED_TARGETS, conn)}


def _concepts(conn) -> dict[str, set[str]]:
    """源 A：PG stock_concept 活跃成分 → 概念倒排（symbol 过 cn 正则）。"""
    inv: dict[str, set[str]] = defaultdict(set)
    for concept, symbol in W.rows(_SQL_STOCK_CONCEPT_MEMBERS, conn):
        inv[concept].add(symbol)
    return inv


def _donors(conn, alive: set[str], degraded: bool) -> dict[str, list]:
    """源 B：同名供体索引 name → [(chain_id, node_id, symbol, confidence)]（活跃已挂节点）。"""
    out: dict[str, list] = defaultdict(list)
    for name, cid, nid, sym, conf in W.rows(_SQL_DONORS, conn):
        if degraded or sym in alive:
            out[name].append((cid, nid, sym, float(conf or 0)))
    return out


def _node_ref_rows(conn, alive: set[str], degraded: bool) -> list[tuple]:
    """源 D：node_ref 直指 node_id 的营收归因（PIT 限 report_date≤闭卷切点）。"""
    out = []
    for nid, sym, mx, miny, maxy, minrd, srcs, prod in W.rows(
        _SQL_NODE_REF.format(cutoff=W.CUTOFF),
        conn,
    ):
        if not SYMBOL_CN_RE.match(sym or "") or not (degraded or sym in alive):
            continue
        role, conf = ("主要", 0.65) if mx >= 0.10 else (("参与", 0.60) if mx >= 0.02 else ("提及", 0.50))
        out.append(
            (
                nid,
                sym,
                role,
                conf,
                minrd or f"{maxy or 2021}-12-31",
                f"product={prod}|max_rev_pct={round(float(mx), 4)}|years={miny}-{maxy}|pr_source={srcs}",
            )
        )
    return out


def _source_c_ch() -> tuple[dict, dict, dict, str, str]:
    """源 C1/C2/C3/C4：CH 同花顺 lineage 三表实读（只读 reader 角色）。

    返回 (概念板倒排, 三级行业倒排, 公司简介, 快照日, 探针摘要)。快照日=akshare_ths 成分
    最新 SCD-2 valid_from，即"这批同花顺归属在库的最晚已知时点"，作 C 族候选的 valid_from。
    """
    try:
        from zephyr.infrastructure.database_service import DatabaseService

        ch = DatabaseService().get_clickhouse_conn(role="reader")
        boards: dict[str, set[str]] = defaultdict(set)
        for board, sym in ch.execute(_SQL_CH_BOARD_MEMBERS):
            if sym and sym[-3:] in (".SH", ".SZ", ".BJ"):
                boards[board].add(sym)
        fresh = ch.execute(_SQL_CH_THS_FRESHNESS)[0]
        c_as_of = str(fresh[0] or date.today())
        inds: dict[str, set[str]] = defaultdict(set)
        profiles: dict[str, str] = {}
        for sym, l1, l2, l3, text in ch.execute(_SQL_CH_STOCK_PROFILES):
            if not sym or sym[-3:] not in (".SH", ".SZ", ".BJ"):
                continue
            for v in (l1, l2, l3):
                if v:
                    inds[v].add(sym)
            profiles[sym] = text or ""
        probe = (
            f"akshare_ths 概念板 {len(boards)} 个 / 三级行业 {len(inds)} 值 / "
            f"公司档案 {len(profiles)} 家 / 最新 valid_from={fresh[0]} / 最近入库 {fresh[1]}"
        )
        return boards, inds, profiles, c_as_of, probe
    except Exception as e:  # noqa: BLE001
        raise SourceCUnreachable(f"{type(e).__name__}: {str(e)[:160]}") from e


def _fill_sources_a_c1c2(targets, concepts, boards, c_as_of, fill, substr_hits) -> None:
    """源 A（stock_concept）+ 源 C1/C2（akshare_ths 概念板）：同规则双通道，禁双重标准。"""
    for node in targets.values():
        nm = node["name"]
        for bucket, inv, as_of in (
            ("A1", concepts, CONCEPT_AS_OF),
            ("A2", concepts, CONCEPT_AS_OF),
            ("C1", boards, c_as_of),
            ("C2", boards, c_as_of),
        ):
            if bucket.endswith("1"):  # 精确同名
                if nm in inv:
                    fill(bucket, node, [(len(inv[nm]), nm, inv[nm])], "exact", as_of)
            else:  # 子串互含（下位/同域启发）
                fill(bucket, node, substr_hits(nm, inv), "substr", as_of)


def _fill_source_c3c4(targets, industries, profiles, c_as_of, fill) -> None:
    """源 C3（同花顺三级行业）+ 源 C4（公司简介提及）。"""
    for node in targets.values():
        nm = node["name"]
        if nm in industries:
            fill("C3", node, [(len(industries[nm]), nm, industries[nm])], "industry_exact", c_as_of)
        if len(nm) >= MENTION_MIN_LEN:
            hit = {s for s, t in profiles.items() if t and nm in t}
            if hit:
                fill("C4", node, [(len(hit), "stock_profile_ths.profile", hit)], "profile_mention", c_as_of)


def _fill_source_b(targets, donors, emit) -> None:
    """源 B：同名跨链成员穿透（同链禁穿=同链同司双计防线）。"""
    for node in targets.values():
        pool = sorted((d for d in donors.get(node["name"], []) if d[0] != node["chain_id"]), key=lambda d: -d[3])
        for cid, dnid, sym, dconf in pool[: SRC["B"]["cap"]]:
            emit(
                "B",
                node,
                sym,
                f"from_node={dnid}|from_chain={cid}|via_name={node['name']}|donor_conf={dconf}",
                CONCEPT_AS_OF,
            )


def _fill_source_d(ref_rows, targets, emit) -> None:
    """源 D：node_ref 营收归因。"""
    for nid, sym, role, conf, valid_from, ev in ref_rows:
        node = targets.get(nid)
        if node is not None:
            emit("D", node, sym, ev, valid_from, conf=conf, role=role)


def _bump_cross_family(cand: dict[tuple[str, str], dict]) -> int:
    """跨真源族互证升档（同族多源不算独立证据），返回升档条数（原地改写候选行）。"""
    bumped = 0
    for row in cand.values():
        groups = {SRC[o]["group"] for o in row["_origins"]} - {"graph_internal"}
        if len(groups) >= 2 and row["confidence"] < 0.70:
            row["confidence"] = 0.70
            row["evidence_text"] += "|corroborated_groups=" + ",".join(sorted(groups))
            bumped += 1
    return bumped


def _dedup_rows(cand: dict[tuple[str, str], dict]) -> list[dict]:
    """候选册行化：剥离下划线内部键、汇 also_from、列序钉死 BATCH_COLUMNS。"""
    rows = []
    for key in sorted(cand):
        row = {k: v for k, v in cand[key].items() if not k.startswith("_")}
        row["also_from"] = ",".join(sorted(cand[key]["_origins"]))
        # 列序钉死为 BATCH_COLUMNS（列式旁挂册按 columns 位置解压，乱序即错列）
        rows.append({k: row[k] for k in W.BATCH_COLUMNS})
    return rows


def build(conn) -> tuple[list[dict], dict]:
    targets = _targets(conn)
    concepts = _concepts(conn)
    alive, degraded = _alive_symbols()
    donors = _donors(conn, alive, degraded)
    ref_rows = _node_ref_rows(conn, alive, degraded)
    c_unavailable = None
    try:
        boards, industries, profiles, c_as_of, c_probe = _source_c_ch()
    except SourceCUnreachable as e:
        boards, industries, profiles = {}, {}, {}
        c_as_of = CONCEPT_AS_OF
        c_probe, c_unavailable = f"源 C CH 不可达→零产出留证: {e}", str(e)

    per_src: dict[str, dict] = {k: {"nodes": set(), "pairs": set()} for k in SRC}
    cand: dict[tuple[str, str], dict] = {}

    def emit(
        src: str, node: dict, sym: str, ev: str, valid_from: str, conf: float | None = None, role: str | None = None
    ) -> None:
        """单候选入册：(node_id,symbol) 去重保最高 confidence，落败方只记互证不覆写。"""
        key = (node["node_id"], sym)
        conf = SRC[src]["conf"] if conf is None else conf
        per_src[src]["nodes"].add(node["node_id"])
        per_src[src]["pairs"].add(key)
        prev = cand.get(key)
        if prev is None or conf > prev["confidence"]:
            cand[key] = {
                "node_id": node["node_id"],
                "chain_id": node["chain_id"],
                "node_name": node["name"],
                "symbol": sym,
                "origin": src,
                "role": role or SRC[src]["role"],
                "confidence": conf,
                "evidence_text": f"origin={src}|{ev}",
                "source_doc": f"{SRC[src]['doc']}|{W.RUN_DATE.isoformat()}",
                "market": "cn",
                "valid_from": valid_from,
                "_origins": {src},
            }
        else:
            prev["_origins"].add(src)

    def substr_hits(nm: str, inv: dict[str, set[str]]) -> list[tuple[int, str, set[str]]]:
        """子串互含命中（下位/同域启发），按成员数升序=具体概念优先，泛概念与短名已被精度防线剔除。"""
        return sorted(
            (len(mem), k, mem)
            for k, mem in inv.items()
            if k != nm
            and len(mem) <= SUBSTR_MAX_MEMBERS
            and ((len(nm) >= SUBSTR_MIN_LEN and nm in k) or (len(k) >= SUBSTR_MIN_LEN and k in nm))
        )

    def fill(bucket: str, node: dict, inv: dict[str, set[str]], match: str, as_of: str) -> None:
        cap = SRC[bucket]["cap"]
        used = 0
        for mcnt, name, mem in inv:
            if used >= cap:
                break
            for sym in sorted(mem):
                if used >= cap:
                    break
                if degraded or sym in alive:
                    emit(bucket, node, sym, f"concept={name}|match={match}|members={mcnt}|as_of={as_of}", as_of)
                    used += 1

    # ---- 源 A（stock_concept）+ 源 C1/C2（akshare_ths 概念板）：同规则双通道，禁双重标准 ----
    _fill_sources_a_c1c2(targets, concepts, boards, c_as_of, fill, substr_hits)

    # ---- 源 C3（同花顺三级行业）+ 源 C4（公司简介提及）----
    _fill_source_c3c4(targets, industries, profiles, c_as_of, fill)

    # ---- 源 B：同名跨链成员穿透（同链禁穿=同链同司双计防线）----
    _fill_source_b(targets, donors, emit)

    # ---- 源 D：node_ref 营收归因 ----
    _fill_source_d(ref_rows, targets, emit)

    # ---- 跨真源族互证升档（同族多源不算独立证据）----
    bumped = _bump_cross_family(cand)

    rows = _dedup_rows(cand)

    stats = {
        "per_source": {
            k: {
                "nodes": len(v["nodes"]),
                "pairs": len(v["pairs"]),
                "role": SRC[k]["role"],
                "confidence": SRC[k]["conf"],
                "per_node_cap": SRC[k]["cap"],
                "evidence_group": SRC[k]["group"],
                "definition": SRC[k]["note"],
            }
            for k, v in per_src.items()
        },
        "unique_pair_rows": len(rows),
        "unique_nodes_touched": len({r["node_id"] for r in rows}),
        "corroborated_bumped_to_0_7": bumped,
        "stock_basic_degraded": degraded,
        "candidate_role_dist": {r: sum(1 for x in rows if x["role"] == r) for r in sorted({x["role"] for x in rows})},
        "guards": {
            "targets": "仅未挂接且非'已并入'节点（已并入禁补挂=同链双计防线）",
            "symbol": "cn 正则 ^\\d{6}\\.(SH|SZ|BJ)$ + stock_basic 在市",
            "substr": f"互含侧名称长度≥{SUBSTR_MIN_LEN} 且概念成员数≤{SUBSTR_MAX_MEMBERS}",
            "mention": f"节点名≥{MENTION_MIN_LEN} 字且在简介全文出现",
            "dedup": "(node_id,symbol) 保最高 confidence",
            "pit": f"源 D 限 report_date≤{W.CUTOFF}",
            "no_confidence_inflation": "单源启发一律 0.45，跨真源族互证才 0.70",
        },
        "source_c_probe": c_probe,
        "source_c_unavailable": c_unavailable,
    }
    return rows, stats


def _bins(state: dict[str, list]) -> tuple[int, int, int]:
    """逐链四元组 → (A_all, A_active, 分母=有节点链数)，与题面口径逐字同构。"""
    a_all = a_act = den = 0
    for nodes, covered, nodes_a, covered_a in state.values():
        if nodes > 0:
            den += 1
            if covered / nodes >= 0.8:
                a_all += 1
            if nodes_a > 0 and covered_a / nodes_a >= 0.8:
                a_act += 1
    return a_all, a_act, den


def simulate(rows: list[dict], conn) -> dict:
    """不落库投影：候选并入逐链四元组后按同口径重算（apply 后须逐项相等）。"""
    pre = W.per_chain_state(conn, exclude_wo006=True)
    post = {k: list(v) for k, v in pre.items()}
    touched = {r["node_id"]: r["chain_id"] for r in rows}  # 覆盖按节点计，同节点多挂只 +1
    for nid, cid in touched.items():
        if cid in post:
            post[cid][1] += 1  # covered（全节点口径）
            post[cid][3] += 1  # covered_a（活跃口径；候选必为非已并入节点）
    b_all, b_act, den = _bins(pre)
    p_all, p_act, _ = _bins(post)
    micro = {c for c, v in pre.items() if 0 < v[2] <= 2 and v[3] == 0}
    m_all, m_act, m_den = _bins({k: v for k, v in post.items() if k not in micro})
    return {
        "pre": {
            "a_all": b_all,
            "a_active": b_act,
            "denominator": den,
            "ratio_all": round(b_all / den, 4),
            "ratio_active": round(b_act / den, 4),
        },
        "projected_after_wo006": {
            "a_all": p_all,
            "a_active": p_act,
            "denominator": den,
            "ratio_all": round(p_all / den, 4),
            "ratio_active": round(p_act / den, 4),
            "nodes_newly_covered": len(touched),
        },
        "projected_if_micro_chains_retired": {
            "a_all": m_all,
            "a_active": m_act,
            "denominator": m_den,
            "ratio_all": round(m_all / m_den, 4),
            "ratio_active": round(m_act / m_den, 4),
            "excluded_nominated_chains": len(micro),
            "gate": "pending_owner_approval——微链退役属 Owner 门位，本战役只提名不执行",
        },
    }


def main(argv=None) -> int:
    argparse.ArgumentParser(description="WO-006 三源补挂候选生成（只读，不写库）").parse_args(argv)
    conn = W.reader()
    try:
        rows, stats = build(conn)
        sim = simulate(rows, conn)
    finally:
        conn.close()
    payload = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "generated_at": date.today().isoformat(),
            "run_date": W.RUN_DATE.isoformat(),
            "criterion": "ig_node_company 纯 INSERT 候选册（列式，引用即重放；写入者=apply_node_bindings.py）",
            "sources": stats["per_source"],
            "guards": stats["guards"],
            "precision_evidence": PRECISION_EVIDENCE,
            "source_c_probe": stats["source_c_probe"],
            "source_c_unavailable": stats["source_c_unavailable"],
            "dedup_stats": {
                k: v
                for k, v in stats.items()
                if k not in ("per_source", "guards", "precision_evidence", "source_c_probe", "source_c_unavailable")
            },
            "projection": sim,
        },
        "columns": W.BATCH_COLUMNS,
        # 列式落盘（行=list 而非 dict：6.7k 行重复键名会让册体积翻倍，且错列由 reg_rows 自检兜底）
        "rows": [[r[k] for k in W.BATCH_COLUMNS] for r in rows],
    }
    W.write_register(REG_PATH, payload)
    per_src_pairs = ", ".join(f"{k}:{v['pairs']}" for k, v in stats["per_source"].items())
    print(f"[CAND] rows={len(rows)} nodes={stats['unique_nodes_touched']} per_source={{{per_src_pairs}}}")
    print(f"[SOURCE_C] {stats['source_c_probe']}")
    print("[PROJECTION] " + json.dumps(sim, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
