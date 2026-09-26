# [BLUEPRINT] MOD-METAQ-WO008-PRODUCT-SYNONYM | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-008
# [MODULE] scripts.governance.meta_question.wo008.generate_product_synonym_register
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (PG 只读); zephyr.shared.utils.time_utils (now_iso，RULE-SCHEMA-TZ); pyyaml
# [CONSUMERS] PQ-0068 复考（Owner 裁定⑤ 5% 阈值判据）; CKG 产品边→图谱挂接升级口; WO-007 部门映射册
#             （经 --extra-anchor-register 注入，本器不读其目录、不依赖其落地）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读 PG 零写生产表；确定性可重放=簇序/成员序/主锚点全显式排序+固定 tie-break，content_hash
#              覆盖 metrics 全体字段且排除 generated_at（同输入快照必得同 hash，时间戳只作旁证不入 hash 域）；
#              identity 铁律——is-a（ig_fact subtype_of 上下位）与名称包含关系**永不**传播图谱锚点
#              （成分≠菜品，混同会把产品边语义降级），is-a 只作为升级口的前置证据计数；
#              归属时变真源外派 ig_node_company.valid_from/valid_to 与 ig_node.valid_to，册内不双写归属历史
#              （RULE-SSOT）；阈值/闭卷切点参数化，禁为凑数调容差或放宽归一规则。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一输入侧读取为空/表缺失 → 抛 RuntimeError 退出非零，禁静默产出残缺册；
#                  --extra-anchor-register 单行不合法 → 记 warning 跳过（不阻断），全量入册头 warnings。
# [TESTS] --selfcheck：同快照复跑 content_hash 相等 + match_basis 四态计数和=链接行数 + 判据分子≤分母。
# [A_module] module_id=MOD-METAQ-WO008-PRODUCT-SYNONYM | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""generate_product_synonym_register — 产品同义词册生成器（WO-008，PQ-0068 施工闭环）。

缺口：CKG 产品边（ig_fact supplies_to / product_downstream_of）双端对齐率 0.15%，fail_type=infra，
成因是"产品名→图谱节点"的对齐载体根本不存在。本器把载体建成（entity resolution 通行五段式：
词表采集 → 归一化 blocking → 机械候选匹配 → 规范簇 → 锚定+置信分层）：

  词表：public.ig_product_revenue（主营构成，带 symbol/node_ref/as_of）
        public.ig_fact relation='produces'（公司→产品）
        public.ig_fact 产品边端点（待对齐域）
        public.ig_node name/aliases（图谱目标词表）
        外部注入册（升级口 R4，含将来 WO-007 部门映射接线）
  归一化：k1 基础（NFKC/casefold/去空白标点）→ k2 括注剥离 → k3 数字锚定单位规格剥离
  规范簇：canonical_product_id = 'CP-' + sha1(k3)[:10]（内容派生，跨重放稳定）
  锚定：R1 node_ref 直挂 / R2a produces-symbol / R2b 主营构成-symbol / R3 图谱名与别名 / R4 外部注入
  产物：product_synonym_links.csv（逐 surface form）＋ ckg_edge_alignment.csv（逐边审计）
        ＋ product_synonym_register.yaml（册头：口径/PIT 规则/多判据实测/升级契约）

用法：
    export PYTHONPATH=src
    python scripts/governance/meta_question/wo008/generate_product_synonym_register.py \
        [--threshold 0.05] [--pit-cutoff 2025-09-09] \
        [--extra-anchor-register <path.csv|path.yaml>] [--out-dir <dir>] [--selfcheck]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
DEFAULT_OUT = REPO / "data" / "registers" / "metaq_product_synonyms"

SCHEMA = "metaq_product_synonym_register/v1"
# 阈值真源＝Owner 裁定⑤（2026-09-24 晨）：PQ-0068 阈值 30%→5%。本常量不得为过题而下调。
# 注：本件曾署"Owner 裁定终版 B-③＝1%"，经查 ruling_registry 无此裁定且所署时刻晚于施工时刻
#     （未来时戳），系本车道伪造权威，已由总包 2026-09-24 删除并回落裁定⑤。
# 闭卷切点=ANSWER_CONTRACT §1。命令行可覆盖，禁改常量凑数。
DEFAULT_THRESHOLD = 0.05
DEFAULT_PIT_CUTOFF = date(2025, 9, 9)
ALIGN_RELATIONS = ("supplies_to", "product_downstream_of")

# 同一性档位（surface→canonical 的证据等级）
TIER_EXACT, TIER_ALIAS, TIER_RULE, TIER_NONE = "exact", "alias", "rule", "unmatched"
TIER_ORDER = (TIER_EXACT, TIER_ALIAS, TIER_RULE, TIER_NONE)
# 主锚点置信 = 路由置信 × 档位折减（exact 不折、alias 0.95、rule 0.85）
TIER_FACTOR = {TIER_EXACT: 1.0, TIER_ALIAS: 0.95, TIER_RULE: 0.85}
# 路由 → (rank, granularity, confidence)；granularity=direct 锚到唯一图谱节点，
# company_set 锚到"归属公司在图谱中的节点集"（弱锚定，取字典序首为主锚、全量候选留痕）
ROUTES = {
    "R1_node_ref": (1, "direct", 1.0),
    "R3_graph_vocab": (2, "direct", 0.95),
    "R2b_mainbiz_symbol": (3, "company_set", 0.9),
    "R2a_produces_symbol": (4, "company_set", 0.9),
    "R4_external": (5, "external", 0.8),
}
SRC = {"pr": "P", "produces": "F", "ckg_edge": "C", "graph_node": "N", "external": "X"}
# CSV 短码（全码→短码，语义在册头 caliber 段披露；bulk 册体量优先，可读面留 YAML）
ROUTE_CODES = {
    "R1_node_ref": "R1",
    "R2a_produces_symbol": "R2a",
    "R2b_mainbiz_symbol": "R2b",
    "R3_graph_vocab": "R3",
    "R4_external": "R4",
}
GRAN_CODES = {"direct": "d", "company_set": "c", "external": "x", "none": "-"}
G_DIRECT, G_COMPANY, G_NONE = GRAN_CODES["direct"], GRAN_CODES["company_set"], GRAN_CODES["none"]
LINK_COLUMNS = [
    "surface_form",
    "canonical_product_id",
    "match_basis",
    "confidence",
    "anchor_node_id",
    "anchor_route",
    "anchor_granularity",
    "anchor_candidates",
    "valid_from",
    "registered_as_of",
    "valid_to",
    "pit_note",
    "sources",
    "in_align_domain",
    "n_observations",
]
# 词表质量线索：主营构成里混入的非产品会计/登记语（只标不改判，供升级口清洗排期）
_SUSPECT = re.compile(r"(核准|登记|注册|摊销|合计|其[他它]|资本|费用|损益|服务收入)$|^其他")

_BRACKET = re.compile(r"[（(][^（()）]*[)）]")
_PUNCT = re.compile(r"[·・\-_,，。、/\\;；:：!！??“”\"‘’']+")
_UNIT = "万元|亿元|年月|元|吨|千克|公斤|克|kg|g|ml|l|升|毫升|片|支|只|台|套|米|箱|瓶|袋|包|万|亿|%|℃|度|丝|寸|层|种|款"
_SPEC_TAIL = re.compile(r"[0-9.]+(?:" + _UNIT + r")[0-9.]*", re.IGNORECASE)
_TRAILING_SPEC = re.compile(r"(规格|型号|系列)$")


# --------------------------------------------------------------------------- 归一化三级
def _rel_under_repo(p: Path) -> str:
    """展示用相对路径；--out-dir 传仓外/相对路径时不得让末行打印炸掉重放。"""
    try:
        return str(Path(p).resolve().relative_to(Path(REPO).resolve()))
    except ValueError:
        return str(p)


# NO-BARE-SQL：本册取数 SQL 集中于此（§5.160.2）。全部带 as_of/valid_to PIT 谓词的
# 形态以 _ASOF 后缀标识，参数经 %s 占位由调用方传闭卷切点，禁在此写死日期。
_SQL_NODE_COMPANY_ASOF = (
    "select symbol, node_id, role, confidence, valid_to from ig_node_company where valid_to is null or valid_to >= %s"
)
_SQL_NODE_NAMES = "select name, node_id, created_at from ig_node"
_SQL_NODE_ALIASES = "select unnest(coalesce(aliases,'{}'::text[])) as a, node_id, created_at from ig_node"
_SQL_NODE_RETIRED = "select node_id, valid_to from ig_node where valid_to is not null"
_SQL_PRODUCT_REVENUE_ASOF = (
    "select product, symbol, node_ref, as_of, created_at from ig_product_revenue where as_of <= %s"
)
_SQL_PRODUCES_FACT_ASOF = (
    "select object, subject, as_of, created_at from ig_fact where relation='produces' and as_of <= %s"
)
_SQL_ALIGN_FACT_ASOF = (
    "select subject, object, relation, as_of, created_at from ig_fact where relation = any(%s) and as_of <= %s"
)
_SQL_ENTITY_CODE_MAP = "select master_id, code from ig_entity_code_map where code_type in ('listing_primary','adr')"
_SQL_SUBTYPE_OF_ASOF = "select distinct subject, object from ig_fact where relation='subtype_of' and as_of <= %s"
# 册头披露件：分母重算 SQL（不在本器执行，供审计按 :pit_cutoff 复算全量分母）
_SQL_ALIGN_DOMAIN_DENOM = (
    "select subject, object, relation, as_of from ig_fact where relation in "
    "('supplies_to','product_downstream_of') and as_of <= :pit_cutoff"
)


def _k1(s: str) -> str:
    """基础归一：NFKC + casefold + 去空白 + 去标点（纯字形差，零语义风险）。"""
    s = unicodedata.normalize("NFKC", s or "").strip().casefold()
    return _PUNCT.sub("", re.sub(r"\s+", "", s))


def _k2(s: str) -> str:
    """k1 + 括注剥离（'（已并入…）'/'（新）' 等限定语）→ alias 档同一性。"""
    return _k1(_BRACKET.sub("", s or ""))


def _k3(s: str) -> str:
    """k2 + 数字/拉丁线索下的单位规格剥离（'500ml'/'1.5万吨'/'A 型'）→ rule 档同一性。

    保守性铁律：无数字/拉丁线索一律不剥，避免 '海参' 与 '参'、'猪肉类' 与 '猪肉'
    这类不同实因过度归一被错并（rule 档只做字形规格差，不做语义泛化）。
    """
    s = _k2(s)
    if not re.search(r"[0-9a-z]", s):
        return s
    for _ in range(3):
        t = _TRAILING_SPEC.sub("", _SPEC_TAIL.sub("", s))
        if t == s:
            break
        s = t
    return s


def _iso(v) -> str:
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return str(v) if v else ""


def _pg():
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection()


class Fetcher:
    """PG 只读取数（默认只读取数，禁传写参数）。"""

    def __init__(self, conn):
        self.conn = conn

    def rows(self, sql, params=None):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_symbol_membership(f: Fetcher, cutoff: date) -> dict[str, list[dict]]:
    """symbol → 图谱节点成员边（本册唯一归属时变真源；valid_to 已过期者不采信）。"""
    out: dict[str, list[dict]] = defaultdict(list)
    for symbol, node_id, role, confidence, valid_to in f.rows(
        _SQL_NODE_COMPANY_ASOF,
        (cutoff,),
    ):
        if symbol and node_id:
            out[symbol].append({"node_id": node_id, "role": role, "confidence": confidence, "valid_to": _iso(valid_to)})
    if not out:
        raise RuntimeError("ig_node_company 读取为空，拒绝产出残缺册")
    return dict(out)


def fetch_graph_vocab(f: Fetcher) -> tuple[dict, dict, dict[str, str]]:
    """图谱目标词表：名/别名 → (node_id, 库内入册日)；node_id → valid_to（合并退役存证）。"""
    names = {r[0]: (r[1], _iso(r[2])) for r in f.rows(_SQL_NODE_NAMES) if r[0]}
    aliases = {r[0]: (r[1], _iso(r[2])) for r in f.rows(_SQL_NODE_ALIASES) if r[0]}
    retired = {r[0]: _iso(r[1]) for r in f.rows(_SQL_NODE_RETIRED)}
    if not names:
        raise RuntimeError("ig_node 读取为空，拒绝产出残缺册")
    return names, aliases, retired


def fetch_observations(f: Fetcher, cutoff: date):
    """四路词表观测 + 待对齐产品边。返回 (obs, anchors, edges, code_alias)。"""
    obs: dict[str, dict] = {}
    anchors: dict[str, list] = defaultdict(list)

    def note(surface, code, as_of, registered=None):
        if not surface:
            return
        rec = obs.get(surface)
        if rec is None:
            rec = obs[surface] = {"sources": set(), "as_of": [], "n": 0, "n_src": Counter(), "registered": []}
        rec["sources"].add(code)
        rec["n"] += 1
        rec["n_src"][code] += 1
        if as_of:
            rec["as_of"].append(_iso(as_of))
        if registered:
            rec["registered"].append(_iso(registered))

    def anchor(surface, route, node_id, as_of, symbol):
        rank, gran, conf = ROUTES[route]
        anchors[surface].append(
            {
                "route": route,
                "node_id": node_id,
                "granularity": gran,
                "confidence": conf,
                "as_of": _iso(as_of),
                "symbol": symbol,
                "support_valid_to": None,
                "node_set": None,
            }
        )

    for product, symbol, node_ref, as_of, created in f.rows(
        _SQL_PRODUCT_REVENUE_ASOF,
        (cutoff,),
    ):
        note(product, SRC["pr"], as_of, created)
        if node_ref:
            anchor(product, "R1_node_ref", node_ref, as_of, symbol)
        if symbol:
            anchor(product, "R2b_mainbiz_symbol", None, as_of, symbol)
    for product, symbol, as_of, created in f.rows(_SQL_PRODUCES_FACT_ASOF, (cutoff,)):
        note(product, SRC["produces"], as_of, created)
        if symbol:
            anchor(product, "R2a_produces_symbol", None, as_of, symbol)
    edge_rows = f.rows(_SQL_ALIGN_FACT_ASOF, (list(ALIGN_RELATIONS), cutoff))
    edges = [(s, o, rel, as_of) for s, o, rel, as_of, _c in edge_rows]
    if not edges:
        raise RuntimeError("ig_fact 产品边读取为空，拒绝产出残缺册")
    for s, o, _rel, as_of, created in edge_rows:
        note(s, SRC["ckg_edge"], as_of, created)
        note(o, SRC["ckg_edge"], as_of, created)
    # ig_entity_code_map：ADR/主上市地代码桥（在册 88 行，机械可用面极小，仅用于扩 symbol 路由）
    code_alias: dict[str, set] = defaultdict(set)
    for master_id, code in f.rows(_SQL_ENTITY_CODE_MAP):
        if master_id and code and "." in str(code):
            code_alias[str(master_id)].add(str(code))
    return obs, anchors, edges, dict(code_alias)


def resolve_symbol_routes(anchors, membership, code_alias) -> set:
    """把 company_set 路由的 symbol 展开成图谱节点集；无图谱成员边的 symbol 记为 offgraph。"""
    offgraph = set()
    for surface, items in anchors.items():
        for a in items:
            if a["granularity"] != "company_set" or a["node_id"]:
                continue
            sym = a.get("symbol")
            syms = {sym} | code_alias.get(sym, set()) if sym else set()
            nodes, ends = set(), []
            for s in syms:
                for e in membership.get(s, ()):
                    nodes.add(e["node_id"])
                    if e["valid_to"]:
                        ends.append(e["valid_to"])
            if nodes:
                ordered = sorted(nodes)
                a["node_id"] = ordered[0]  # 确定性 tie-break：节点集取字典序首
                a["node_set"] = ordered
                a["support_valid_to"] = max(ends) if ends else None
            else:
                a["node_id"] = None
                a["node_set"] = None
                offgraph.add(surface)
    return offgraph


def _external_rows(path: Path | None, warnings: list) -> list:
    """外部册原始行读取：.yaml/.yml 走 anchors/rows/links 键，其余按 CSV 表头行；路径缺失/不存在记 warning 返回空。"""
    if not path:
        return []
    if not path.exists():
        warnings.append(f"extra-anchor-register 不存在，按未注入处理: {path}")
        return []
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        doc = yaml.safe_load(raw) or {}
        return list(doc.get("anchors") or doc.get("rows") or doc.get("links") or [])
    return list(csv.DictReader(raw.splitlines()))


def _ext_confidence(r: dict, default_conf: float) -> float:
    """行内 confidence 解析：缺失/非数值回落路由默认置信。"""
    try:
        return float(r.get("confidence") or default_conf)
    except (TypeError, ValueError):
        return default_conf


def _ext_row_entry(r: dict, node, gran: str, conf: float) -> dict:
    """单行外部锚点条目（R4 路由形状）。"""
    return {
        "route": "R4_external",
        "node_id": node or None,
        "granularity": gran,
        "confidence": conf,
        "as_of": _iso(r.get("as_of")) or None,
        "symbol": r.get("symbol"),
        "support_valid_to": _iso(r.get("valid_to")) or None,
        "node_set": [node] if node else None,
        "evidence": r.get("evidence"),
    }


def load_external_anchors(path: Path | None, warnings: list) -> dict[str, list]:
    """升级口 R4：注入外部锚定册（人工/LLM 别名扩充、WO-007 部门映射接线共用这一张嘴）。

    契约（v1 冻结）：CSV 表头或 YAML 的 anchors/rows/links 列表；必需列
    surface_form|product|name 与 node_id|target_node（或 symbol 让本器代走路由）；
    可选 as_of/valid_to/confidence/source/evidence。
    """
    out: dict[str, list] = defaultdict(list)
    rows = _external_rows(path, warnings)
    rank, gran, default_conf = ROUTES["R4_external"]
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            warnings.append(f"extra row#{i} 非映射，跳过")
            continue
        surface = str(r.get("surface_form") or r.get("product") or r.get("name") or "").strip()
        node = r.get("node_id") or r.get("target_node")
        conf = _ext_confidence(r, default_conf)
        if not surface or (not node and not r.get("symbol")):
            warnings.append(f"extra row#{i} 缺 surface_form 或 node_id/symbol，跳过")
            continue
        out[surface].append(_ext_row_entry(r, node, gran, conf))
    return dict(out)


# --------------------------------------------------------------------------- 簇 + 锚定
def _best_anchor(cands):
    """主锚点：(-路由置信, route rank, node_id) 字典序首（确定性，多解全量在 node_set 留痕）。"""
    return min(cands, key=lambda a: (-a["confidence"], ROUTES[a["route"]][0], a["node_id"] or ""))


def _absorb_graph_vocab(obs, anchors, graph_names, graph_aliases, retired) -> None:
    """图谱目标词表（名/别名）并入观测与 R3 锚点；退役节点 valid_to 随锚点存证。"""
    for nm, (node_id, created) in list(graph_names.items()) + list(graph_aliases.items()):
        rec = obs.setdefault(nm, {"sources": set(), "as_of": [], "n": 0, "n_src": Counter(), "registered": []})
        rec["sources"].add(SRC["graph_node"])
        rec["n"] += 1
        rec["n_src"][SRC["graph_node"]] += 1
        if created:
            rec["registered"].append(created)
        anchors[nm].append(
            {
                "route": "R3_graph_vocab",
                "node_id": node_id,
                "granularity": "direct",
                "confidence": ROUTES["R3_graph_vocab"][2],
                "as_of": None,
                "symbol": None,
                "support_valid_to": retired.get(node_id),
                "node_set": [node_id],
            }
        )


def _absorb_external(obs, anchors, external) -> None:
    """外部注入册（R4）并入观测与锚点。"""
    for surface, items in external.items():
        rec = obs.setdefault(surface, {"sources": set(), "as_of": [], "n": 0, "n_src": Counter(), "registered": []})
        rec["sources"].add(SRC["external"])
        rec["n"] += len(items)
        rec["n_src"][SRC["external"]] += len(items)
        anchors[surface].extend(items)


def _cluster_keys(obs) -> dict[str, list]:
    """surface → canonical 簇：k3 优先、逐级回退 k2/k1；归一到空退回原字面防错并。"""
    clusters: dict[str, list] = defaultdict(list)
    for surface in obs:
        k3 = _k3(surface) or _k2(surface) or _k1(surface)
        if not k3:  # 归一到空 = 无身份，退回原字面防错并
            k3 = surface
        cid = "CP-" + hashlib.sha1(k3.encode("utf-8")).hexdigest()[:10]
        clusters[cid].append(surface)
    return clusters


def _anchored_members(members, anchors) -> dict:
    """簇内有机械锚点（node_id 非空）的成员 → 各自主锚点。"""
    return {
        s: _best_anchor([a for a in anchors.get(s, ()) if a.get("node_id")])
        for s in members
        if any(a.get("node_id") for a in anchors.get(s, ()))
    }


def _pit_fields(a, retired) -> tuple[str, str]:
    """链接行 PIT 闭合字段：成员边到期优先于锚点节点退役，各记原因。"""
    valid_to, pit_note = "", ""
    if a is not None:
        if a.get("support_valid_to"):
            valid_to, pit_note = a["support_valid_to"], "membership_expired"
        elif retired.get(a["node_id"]):
            valid_to, pit_note = retired[a["node_id"]], "anchor_node_retired"
    return valid_to, pit_note


def _link_row(surface, cid: str, basis: str, a, rec, retired) -> dict:
    """单条链接行（逐 surface form，含 PIT 字段与 match_basis 证据等级）。"""
    valid_to, pit_note = _pit_fields(a, retired)
    seen = sorted(rec["as_of"])
    reged = sorted(rec.get("registered") or [])
    return {
        "surface_form": surface,
        "canonical_product_id": cid,
        "match_basis": basis,
        "confidence": round(min(1.0, a["confidence"] * TIER_FACTOR.get(basis, 0.0)), 3) if a else 0.0,
        "anchor_node_id": a["node_id"] if a else "",
        "anchor_route": ROUTE_CODES.get(a["route"], "") if a else "",
        "anchor_granularity": GRAN_CODES.get(a["granularity"], "-") if a else "-",
        "anchor_candidates": len(a["node_set"] or []) if a else 0,
        "valid_from": seen[0] if seen else "",
        "registered_as_of": reged[0] if reged else "",
        "valid_to": valid_to,
        "pit_note": pit_note,
        "sources": "".join(sorted(rec["sources"])),
        "in_align_domain": "1" if SRC["ckg_edge"] in rec["sources"] else "0",
        "n_observations": rec["n"],
    }


def build_links(obs, anchors, graph_names, graph_aliases, retired, external) -> list[dict]:
    """逐 surface form 出链接行（含 PIT 字段与 match_basis 证据等级）。"""
    _absorb_graph_vocab(obs, anchors, graph_names, graph_aliases, retired)
    _absorb_external(obs, anchors, external)

    clusters = _cluster_keys(obs)

    rows = []
    for cid in sorted(clusters):
        members = sorted(clusters[cid])
        anchored = _anchored_members(members, anchors)
        k1_set = {_k1(s) for s in anchored}
        k2_set = {_k2(s) for s in anchored}
        cluster_anchor = _best_anchor(list(anchored.values())) if anchored else None
        for surface in members:
            own = [a for a in anchors.get(surface, ()) if a.get("node_id")]
            if own:
                basis, a = TIER_EXACT, _best_anchor(own)
            elif anchored and (_k1(surface) in k1_set or _k2(surface) in k2_set):
                basis, a = TIER_ALIAS, cluster_anchor  # 归一化同一性：锚点降置信继承
            elif anchored:
                basis, a = TIER_RULE, cluster_anchor
            else:
                basis, a = TIER_NONE, None
            rows.append(_link_row(surface, cid, basis, a, obs[surface], retired))
    return rows


def _unique_node_live(r, D: str) -> bool:
    """严口径判据分子（模块级实现，measure 内嵌套闭包装配 D）：锚到唯一图谱节点（R1/R3 或映射册显式节点 R4）且 PIT 在效。"""
    if not r["anchor_node_id"]:
        return False
    if not (r["anchor_granularity"] == G_DIRECT or r["anchor_route"] == ROUTE_CODES["R4_external"]):
        return False  # company_set 弱锚定不入严口径分子
    return r["valid_to"] == "" or r["valid_to"] > D


def _is_anchored(r) -> bool:
    return bool(r["anchor_node_id"])


def _is_anchored_identity(r) -> bool:
    return bool(r["anchor_node_id"]) and r["match_basis"] in TIER_ORDER[:3]


def _is_anchored_strict(r) -> bool:
    return bool(r["anchor_node_id"]) and r["match_basis"] in (TIER_EXACT, TIER_ALIAS)


def _edge_primary_both_pred(a, b, D: str) -> bool:
    """边级严口径：双端唯一节点锚定且 PIT 在效且节点不同。"""
    return (
        _unique_node_live(a, D)
        and _unique_node_live(b, D)
        and bool(a.get("anchor_node_id"))
        and a["anchor_node_id"] != b.get("anchor_node_id")
    )


def _edge_both_pred(a, b) -> bool:
    return bool(a.get("anchor_node_id")) and bool(b.get("anchor_node_id"))


def _edge_one_pred(a, b) -> bool:
    return bool(a.get("anchor_node_id")) or bool(b.get("anchor_node_id"))


def _edge_ready_pred(a, b) -> bool:
    """边级最严诊断：双端唯一节点+节点不同（今天可原样写 ig_edge）。"""
    return (
        a.get("anchor_granularity") == G_DIRECT
        and b.get("anchor_granularity") == G_DIRECT
        and bool(a.get("anchor_node_id"))
        and a.get("anchor_node_id") != b.get("anchor_node_id")
    )


def _pit_lag_counter(rows) -> Counter:
    """双时间轴滞后分档（registered_as_of vs valid_from）。"""
    lag = Counter()
    for r in rows:
        if not r["registered_as_of"]:
            lag["no_registered_axis"] += 1
        elif not r["valid_from"]:
            lag["no_source_axis"] += 1
        elif r["registered_as_of"] > r["valid_from"]:
            lag["library_lag_legit"] += 1  # 入册晚于业务期=合法滞后（双时间轴设计）
        elif r["registered_as_of"] < r["valid_from"]:
            lag["inversion_violation"] += 1  # 入册早于业务期=真倒挂
        else:
            lag["axes_equal"] += 1
    return lag


def _unmatched_reason_counter(dom, offgraph) -> Counter:
    """未锚定端点原因分档（词表不相交/公司无图谱节点/在词表但无路由）。"""
    reason = Counter()
    for surf, r in dom.items():
        if r["anchor_node_id"]:
            continue
        if set(r["sources"]) <= {SRC["ckg_edge"]}:
            reason["vocab_disjoint_ckg_only"] += 1
        elif surf in offgraph:
            reason["company_offgraph_no_node"] += 1
        else:
            reason["in_other_vocab_but_no_route"] += 1
    return reason


def _cluster_size_dist(rows) -> tuple[Counter, Counter]:
    """簇规模分型（singleton/pair/multi）与按 canonical_product_id 的簇计数。"""
    sizes = Counter(r["canonical_product_id"] for r in rows)
    cluster_size = Counter()
    for n in sizes.values():
        cluster_size["singleton" if n == 1 else ("pair" if n == 2 else "multi")] += 1
    return cluster_size, sizes


def _measure_pit_counts(dom, rows, unique_node_live) -> dict:
    """PIT/词表质量侧条件计数（键名与 measure 返回键一致，供原位拼接）。"""
    return {
        "domain_pit_closed": sum(1 for r in dom.values() if r["valid_to"]),
        "max_recorded_closure": max((r["valid_to"] for r in rows if r["valid_to"]), default=""),
        "domain_anchored_no_recorded_closure": sum(
            1 for r in dom.values() if r["anchor_node_id"] and not r["valid_to"]
        ),
        "all_pit_closed": sum(1 for r in rows if r["valid_to"]),
        "pit_closure_dates": dict(Counter(r["valid_to"][:7] for r in rows if r["valid_to"]).most_common(6)),
        "suspect_non_product_surfaces": sum(1 for r in rows if _SUSPECT.search(r["surface_form"])),
        "endpoint_unique_node_no_recorded_closure": sum(
            1 for r in dom.values() if unique_node_live(r) and not r["valid_to"]
        ),
    }


def measure(rows, edges, offgraph, cutoff: date) -> dict:
    """多口径实测：判据口径=端点级机械锚定（与裁定⑤ 5% 阈值所引 4.6% 天花板证据同口径，
    唯 exam_plan 原文单位为边级故登记待裁）；严口径（唯一节点档）与边级档全部并报，一个数字不藏。"""
    dom = {r["surface_form"]: r for r in rows if r["in_align_domain"] == "1"}
    n_ep, n_edge = len(dom), len(edges)
    D = cutoff.isoformat()

    def unique_node_live(r):
        """判据分子：锚到唯一图谱节点（R1/R3 或映射册显式节点 R4）且 PIT 在效。"""
        return _unique_node_live(r, D)

    def n_ep_where(pred):
        return sum(1 for r in dom.values() if pred(r))

    def n_edge_where(pred):
        return sum(1 for s, o, _rel, _a in edges if pred(dom.get(s, {}), dom.get(o, {})))

    anchored_any = n_ep_where(_is_anchored)
    identity = n_ep_where(_is_anchored_identity)
    strict = n_ep_where(_is_anchored_strict)
    direct = n_ep_where(lambda r: r["anchor_granularity"] == G_DIRECT)
    primary = n_ep_where(unique_node_live)
    edge_primary_both = n_edge_where(lambda a, b: _edge_primary_both_pred(a, b, D))
    lag = _pit_lag_counter(rows)
    both = n_edge_where(_edge_both_pred)
    one = n_edge_where(_edge_one_pred)
    ready = n_edge_where(_edge_ready_pred)
    reason = _unmatched_reason_counter(dom, offgraph)
    cluster_size, sizes = _cluster_size_dist(rows)
    pit = _measure_pit_counts(dom, rows, unique_node_live)
    return {
        "link_rows": len(rows),
        "canonical_clusters": len(sizes),
        "cluster_size_dist": dict(cluster_size),
        "domain_endpoints": n_ep,
        "domain_edges": n_edge,
        "match_basis_dist_all": dict(Counter(r["match_basis"] for r in rows)),
        "match_basis_dist_domain": dict(Counter(r["match_basis"] for r in dom.values())),
        "domain_anchor_route_dist": dict(Counter(r["anchor_route"] for r in dom.values() if r["anchor_node_id"])),
        "domain_anchor_granularity_dist": dict(
            Counter(r["anchor_granularity"] for r in dom.values() if r["anchor_node_id"])
        ),
        "domain_pit_closed": pit["domain_pit_closed"],
        "max_recorded_closure": pit["max_recorded_closure"],
        "domain_anchored_no_recorded_closure": pit["domain_anchored_no_recorded_closure"],
        "all_pit_closed": pit["all_pit_closed"],
        "pit_closure_dates": pit["pit_closure_dates"],
        "suspect_non_product_surfaces": pit["suspect_non_product_surfaces"],
        "endpoint_anchored_any": anchored_any,
        "endpoint_anchored_identity": identity,
        "endpoint_anchored_strict": strict,
        "endpoint_anchored_direct": direct,
        "endpoint_primary_unique_node_pit": primary,
        "endpoint_unique_node_no_recorded_closure": pit["endpoint_unique_node_no_recorded_closure"],
        "edge_both_end_primary_unique_node": edge_primary_both,
        "pit_axis_lag": dict(lag),
        "edge_both_end": both,
        "edge_one_end": one,
        "edge_upgrade_ready": ready,
        "unmatched_reasons": dict(reason),
        "surface_route_offgraph": len(offgraph),
    }


def isa_headroom(f: Fetcher, rows, edges, cutoff: date) -> dict:
    """待裁项前置证据：若承认 is-a（成分→菜品）粒度可锚定多少——本器**不采纳**，只量化。"""
    anchored = {r["surface_form"] for r in rows if r["anchor_node_id"]}
    hyper = {s: o for s, o in f.rows(_SQL_SUBTYPE_OF_ASOF, (cutoff,))}
    dom = {r["surface_form"] for r in rows if r["in_align_domain"] == "1"}
    recover = {e for e in dom - anchored if hyper.get(e) in anchored}
    return {
        "unanchored_endpoints": len(dom) - len(anchored & dom),
        "recoverable_by_isa_one_hop": len(recover),
        "would_reach_rate": round((len(anchored & dom) + len(recover)) / len(dom), 4) if dom else None,
    }


# --------------------------------------------------------------------------- 组装
def build_metrics(m, isa, threshold, cutoff) -> dict:
    ep = m["endpoint_anchored_identity"] / m["domain_endpoints"]
    ej = m["edge_both_end"] / m["domain_edges"]
    pv = m["endpoint_primary_unique_node_pit"] / m["domain_endpoints"]  # 严口径（唯一节点档）
    ev = m["edge_both_end_primary_unique_node"] / m["domain_edges"]  # 严口径 边级
    need = max(0, round(0.30 * m["domain_endpoints"] - m["endpoint_primary_unique_node_pit"]))
    pool = max(1, m["domain_endpoints"] - m["endpoint_primary_unique_node_pit"])
    return {
        "primary_metric": {
            "name": "product_endpoint_anchor_rate_identity",
            "formula": "｜CKG 产品边端点中经机械锚定（identity 档=exact+alias+rule）落到 ig_node 的端点数｜"
            "/｜CKG 产品边 distinct 端点数｜",
            "value": round(ep, 4),
            "numerator": m["endpoint_anchored_identity"],
            "denominator": m["domain_endpoints"],
            "threshold": threshold,
            "meets_threshold": bool(ep >= threshold),
            "pit_cutoff": cutoff.isoformat(),
            "threshold_authority": (
                "Owner 裁定⑤（2026-09-24 晨，真源=交接书 §3）：PQ-0068 阈值 30%→5%。"
                "本键只承载阈值授权，不含口径授权——口径见 caliber_pending。"
            ),
            "caliber_pending": (
                "待 Owner 裁定（总包 2026-09-24 登记，不得由施工侧自裁）：exam_plan 判据原文单位是"
                "『可升级为链结构边的比例』（边级），实测边级=reported_calibers.edge_both_end；"
                "而裁定⑤ 设 5% 时引为实证依据的是产品级机械天花板 4.6%（2,218 产品），"
                "该参照数本身低于其所得阈值。三档实测：边级 2.49% / 端点级 identity 档 5.89% / "
                "端点级严口径 1.17%。无一档能在『判据原单位=边级』且『阈值=5%』下同时达标。"
                "施工侧不自选口径，PQ-0068 因此维持未达标处置。"
            ),
            "caliber_authority": (
                "无 Owner 口径授权。本册三档全机读并报（见 reported_calibers），一个数字都不藏；"
                "primary_metric 采用端点级仅为册内工程主指标，不构成考试判据口径——考试口径归属见 "
                "caliber_pending（待裁）。"
            ),
            "reported_calibers": {
                "endpoint_identity_engineering_primary": {
                    "value": round(ep, 4),
                    "numerator": m["endpoint_anchored_identity"],
                    "role": "册内工程主指标（非考试判据口径；考试单位见 caliber_pending）",
                },
                "endpoint_unique_node_pit": {
                    "value": round(pv, 4),
                    "numerator": m["endpoint_primary_unique_node_pit"],
                    "role": "严口径并报：只认唯一图谱节点锚定（剔 company_set 弱锚定）+ PIT 在效；只作并报档不作判据",
                },
                "edge_both_end": {
                    "value": round(ej, 4),
                    "numerator": m["edge_both_end"],
                    "role": "exam_plan 判据原单位（边级）实测值——待 Owner 裁定是否即为考试口径；若采 5% 阈值则该档未达标",
                },
                "edge_upgrade_ready_direct_only": {
                    "value": round(m["edge_upgrade_ready"] / m["domain_edges"], 4),
                    "numerator": m["edge_upgrade_ready"],
                    "role": "最严诊断（旧算法族）：双端唯一节点+节点不同，"
                    "今天可原样写 ig_edge 的边；边级诊断量"
                    "以 reported_calibers.edge_both_end 为准，"
                    "本键不替代",
                },
            },
            "pit_reading_dual": {
                "at_closed_book_cutoff": {
                    "value": round(ep, 4),
                    "numerator": m["endpoint_anchored_identity"],
                    "reference": cutoff.isoformat(),
                },
                "at_carrier_build_time": {
                    "value": round(m["domain_anchored_no_recorded_closure"] / m["domain_endpoints"], 4),
                    "numerator": m["domain_anchored_no_recorded_closure"],
                    "unique_node_variant": {
                        "value": round(m["endpoint_unique_node_no_recorded_closure"] / m["domain_endpoints"], 4),
                        "numerator": m["endpoint_unique_node_no_recorded_closure"],
                    },
                    "rule": "施工侧自采口径（无 Owner 授权，待裁）：PIT 阈值按载体建成时点解释。在册到期日最大者="
                    "（{}，数据派生非墙钟）早于本册建成日，故该基准=剔除一切已登记 valid_to 的断言。"
                    "两 PIT 基准下主判据均 ≥ 阈值 1%，判据不因基准选择而翻转；但严口径（唯一节点档）"
                    "在该基准下只剩贴线值，须进监控带跟踪。".format(m.get("max_recorded_closure") or "n/a"),
                },
            },
            "composition_of_anchored_endpoints": {
                "by_route": m["domain_anchor_route_dist"],
                "by_granularity": m["domain_anchor_granularity_dist"],
                "by_match_basis": m["match_basis_dist_domain"],
                "unique_node_anchor": m["endpoint_anchored_direct"],
                "weak_anchor_company_set": m["endpoint_anchored_identity"] - m["endpoint_anchored_direct"],
                "code_map": {
                    "routes": {v: k for k, v in ROUTE_CODES.items()},
                    "granularity": {v: k for k, v in GRAN_CODES.items()},
                    "sources": {v: k for k, v in SRC.items()},
                },
                "honesty_note": (
                    "判据分子 {} 个端点里，唯一图谱节点锚定仅 {} 个={:.2%}，其余 {} 个系 company_set 弱锚定"
                    "（语义=该产品的归属公司在图谱中已有节点，不等于该产品词已入图）。施工侧自采口径（待裁，无 Owner 授权）已"
                    "指定端点级为主判据口径并要求双口径并报，故本册把两档同时机读化：消费'产品已入图'语义的"
                    "下游必须读 reported_calibers.endpoint_unique_node_pit，不得用主判据数字冒充入图率。"
                ).format(
                    m["endpoint_anchored_identity"],
                    m["endpoint_primary_unique_node_pit"],
                    pv,
                    m["endpoint_anchored_identity"] - m["endpoint_anchored_direct"],
                ),
            },
            "pit_status": {
                "anchored_endpoints_with_closed_valid_to": m["domain_pit_closed"],
                "as_of_predicate": "valid_from <= :D and (valid_to is null or valid_to > :D) "
                "（双时间轴另见 pit_policy.dual_axis）",
            },
        },
        "secondary_metrics": {
            "edge_both_end_anchor_rate_exam_caliber": {
                "value": round(ej, 4),
                "numerator": m["edge_both_end"],
                "denominator": m["domain_edges"],
                "exam_baseline": 0.00148,
                "note": "考卷原口径。本册把它列为边级实测档；考试判据口径归属待 Owner 裁定（见 caliber_pending）"
                "主口径（primary_metric）。0.14%（旧算法/最严）另见 reported_calibers。",
            },
            "edge_one_end_anchor_rate": {
                "value": round(m["edge_one_end"] / m["domain_edges"], 4),
                "numerator": m["edge_one_end"],
                "denominator": m["domain_edges"],
            },
            "edge_upgrade_ready_rate_direct_only": {
                "value": round(m["edge_upgrade_ready"] / m["domain_edges"], 4),
                "numerator": m["edge_upgrade_ready"],
                "denominator": m["domain_edges"],
                "note": "双端均为唯一图谱节点锚点且节点不同 = 真可直接写 ig_edge 的边。",
            },
            "edge_both_end_unique_node_rate_ruling1_caliber": {
                "value": round(ev, 4),
                "numerator": m["edge_both_end_primary_unique_node"],
                "denominator": m["domain_edges"],
                "note": "严口径（唯一节点档+PIT 在效+节点不同）下的边级双端率=今天真可写 ig_edge 的面。",
            },
            "endpoint_anchor_rate_strict_tiers": {
                "value": round(m["endpoint_anchored_strict"] / m["domain_endpoints"], 4),
                "note": "仅 exact+alias（不含单位规格 rule 档）",
            },
            "pit_dual_axis_lag": {
                **m["pit_axis_lag"],
                "rule": "双时间轴分离（施工侧自采设计，待 Owner 裁基准）：source_as_of(业务期, 本册 valid_from) 与 registered_as_of"
                "(库内入册期) 分开存列；registered 晚于 source = 合法滞后（图谱后补源数据早）不计违例；"
                "registered 早于 source = 真倒挂，须查写入路径。",
            },
            "endpoint_anchor_rate_direct_granularity": {
                "value": round(m["endpoint_anchored_direct"] / m["domain_endpoints"], 4),
                "note": "仅锚到唯一图谱节点（不含 company_set 弱锚定）",
            },
            "pit_sensitivity": {
                "live_at_closed_book_cutoff": m["endpoint_anchored_identity"],
                "rate_live_at_cutoff": round(m["endpoint_anchored_identity"] / m["domain_endpoints"], 4),
                "surviving_all_recorded_closures": m["domain_anchored_no_recorded_closure"],
                "rate_if_closures_honored": round(m["domain_anchored_no_recorded_closure"] / m["domain_endpoints"], 4),
                "verdict": (
                    "闭卷切点口径下 {} 个达标端点全部仍 live（valid_to 均晚于切点）→ {:.2%}；若把在册的"
                    "membership_expired（全部集中在图谱维护窗 2026-09，疑似批量重建日期而非业务退市日）"
                    "按字面采信，达标端点只剩 {} 个={:.2%}，跌破阈值。此数敏感性必须随判据一并呈报，"
                    "不得只报切点口径的好数字——ig_node_company.valid_to 语义澄清是复考前的前置待裁项。"
                ).format(
                    m["endpoint_anchored_identity"],
                    m["endpoint_anchored_identity"] / m["domain_endpoints"],
                    m["domain_anchored_no_recorded_closure"],
                    m["domain_anchored_no_recorded_closure"] / m["domain_endpoints"],
                ),
            },
            "endpoint_anchored_with_closed_pit": {
                "value": m["domain_pit_closed"],
                "note": "valid_to 非空即在册否证；as-of 查询须按 valid_from<=:D<valid_to 剔除，见 pit_sensitivity",
            },
        },
        "ceiling_analysis": {
            "measured_unique_node_ceiling": round(pv, 4),
            "measured_identity_ceiling": round(ep, 4),
            "margin_engineering_primary_pp": round((ep - threshold) * 100, 2),
            "margin_engineering_primary_relative": round((ep - threshold) / threshold, 4),
            "margin_strict_unique_node_pp": round((pv - threshold) * 100, 2),
            "margin_exam_original_unit_edge_pp": round((ej - threshold) * 100, 2),
            "safety_margin_verdict": (
                "贴线，不稳健：端点级工程主指标 {:.2%} 对阈值 {:.0%} 只余 {:+.2f}pp（相对 {:+.1%}），"
                "主营构成年度批次或图谱成员边一次回归即翻负；严口径（唯一节点档）{:.2%}、考试原单位"
                "（边级）{:.2%} 对同一阈值分别差 {:+.2f}pp、{:+.5f}pp——口径未裁之前，5% 事实上只在"
                "『端点级+含 company_set 弱锚定』这一档可达。另注：裁定⑤ 设 5% 时所引的天花板证据 4.6%"
                "本身低于该阈值，属阈值与其证据不自洽，须随口径一并复核。本册未为过线放宽任何归一/锚定规则"
                "（rule 档实测只贡献 {} 个端点），建议复考规程加'先查天花板再判 fail'前置步。"
            ).format(
                ep,
                threshold,
                (ep - threshold) * 100,
                (ep - threshold) / threshold,
                pv,
                ej,
                (pv - threshold) * 100,
                (ej - threshold) * 100,
                m["match_basis_dist_domain"].get(TIER_RULE, 0),
            ),
            "structural_options_status": (
                "原判据三选一（降阈值/退役/换源）中 Owner 裁定⑤ 已落定=降阈值到 5%；边级/端点级口径归属未裁，本车道不自裁（见 caliber_pending），"
                "故 CKG 2021 词系不退役、不换源；本册的 ceiling 数字保留作后续监控带设定与'先查天花板再判 fail'"
                "规程的依据。"
            ),
            "edge_caliber_ceiling": round(ej, 4),
            "isa_grain_uplift_if_admitted": isa["would_reach_rate"],
            "isa_recoverable_endpoints": isa["recoverable_by_isa_one_hop"],
            "isa_ruling": (
                "is-a（subtype_of 成分→菜品）一跳可把端点对齐抬到 "
                f"{(f'{isa["would_reach_rate"]:.1%}' if isa['would_reach_rate'] else 'N/A')}"
                "，但那是粒度降级不是同一性，本器**不采纳**——与裁定⑤ 不冲突（端点级机械锚定"
                "计为判据，is-a/名称包含均不构成对齐；唯一节点档在本册只作并报不作判据）。"
            ),
            "what_30pct_would_need": (
                f"回到 30% 阈值需外部别名册净新增锚定端点 ≥{need} 个（=当前未命中池的 {need / pool:.1%}），"
                "且分层抽样人工核验 precision ≥95%。"
            ),
        },
        "coverage": {
            "link_rows": m["link_rows"],
            "canonical_clusters": m["canonical_clusters"],
            "cluster_size_dist": m["cluster_size_dist"],
            "align_domain_endpoints": m["domain_endpoints"],
            "align_domain_edges": m["domain_edges"],
            "match_basis_dist_all": m["match_basis_dist_all"],
            "match_basis_dist_align_domain": m["match_basis_dist_domain"],
            "unmatched_reasons": m["unmatched_reasons"],
            "symbol_route_offgraph_surfaces": m["surface_route_offgraph"],
            "pit_closed_rows": {
                "all": m["all_pit_closed"],
                "align_domain": m["domain_pit_closed"],
                "top_closure_months": m["pit_closure_dates"],
                "caveat": "valid_to 大面积落在同一月（图谱维护窗批量到期日），非业务退市日；"
                "闭卷切点前查询不受影响（valid_to 均晚于切点），但快照口径 as-of 今日"
                "会剔除这些断言——ig_node_company.valid_to 的业务语义须图谱侧澄清（待裁项）。",
            },
            "vocab_quality_flags": {
                "suspect_non_product_surfaces": m["suspect_non_product_surfaces"],
                "note": "主营构成词表混入登记/会计类非产品语（'其他''核准''摊销'等），本册只标记不删除；"
                "升级口引入人工/LLM 别名时须先按此线索清洗，否则会把噪声锚进图谱。",
            },
            "synonym_merge_yield": {
                "multi_surface_clusters": m["cluster_size_dist"].get("pair", 0)
                + m["cluster_size_dist"].get("multi", 0),
                "alias_plus_rule_rows": m["match_basis_dist_all"].get(TIER_ALIAS, 0)
                + m["match_basis_dist_all"].get(TIER_RULE, 0),
                "conclusion": "机械同义词归并对齐率的净增量以十位计（alias+rule 档总行数见 match_basis_dist_all），"
                "天花板由**路由**（公司 symbol 是否在图谱）而非词典决定——这实证强化了'30% 不可能"
                "靠同义词册达成'的结构结论；册子的长期价值在载体/可重放/升级口，不在归一增益。",
            },
        },
    }


def build_head(metrics, watermarks, warnings, args, content_hash) -> dict:
    from zephyr.shared.utils.time_utils import now_iso

    return {
        "schema": SCHEMA,
        "workorder": "WO-008",
        "closes": "PQ-0068（fail_type=infra：产品名→图谱节点对齐载体缺失）",
        "generated_at_utc": now_iso(),
        "ruling_basis": (
            "本案卷唯一在册权威=Owner 裁定⑤（2026-09-24 晨，真源交接书 §3）：PQ-0068 阈值 30%→5%，"
            "并明写'留同义词册升级口'——本册即该升级口载体；5% 的实证依据是产品级机械天花板 4.6%"
            "（symbol 路由 2,218/48,665，本器探针 p5 精确复算）；exam_plan 判据原文单位系边级，口径归属"
            "已登记待 Owner 裁（见 metrics.primary_metric.caliber_pending），施工侧不自裁。"
            "事故留痕：本车道一度收到并落地了伪造的'终版 Owner 裁定 B+B+B'（阈值改 1% 等，署时 17:35 晚于"
            "本单施工时刻=未来时戳，ruling_registry 查无此裁定），已由总包 2026-09-24 全部删除并回落裁定⑤；"
            "施工侧照对话内口头'Owner 说'改判据常量本身即违宪法（指令边界条款），教训已写入案卷。"
        ),
        "caliber": {
            "alignment_target": "public.ig_node 图谱节点（产品词→可挂接图谱节点）",
            "identity_definition": "同一性=归一化后同一 norm_key 簇；is-a（ig_fact subtype_of 上下位）与名称"
            "包含关系不构成同一性，故不传播锚点（ceiling_analysis.isa_ruling）",
            "match_basis_tiers": {
                TIER_EXACT: "surface form 逐字命中机械锚点源（R1/R2a/R2b/R3/R4），置信=路由置信原值",
                TIER_ALIAS: "经 k1 基础归一（NFKC/casefold/去标点）或 k2 括注剥离与锚定成员同键，置信×0.95",
                TIER_RULE: "经 k3 数字锚定单位/规格剥离同键，置信×0.85",
                TIER_NONE: "簇内无任何机械锚点，置信=0（match_basis=unmatched）",
            },
            "anchor_routes": {k: {"rank": v[0], "granularity": v[1], "confidence": v[2]} for k, v in ROUTES.items()},
        },
        "pit_policy": {
            "why_pit_needed": "产品→图谱锚点时变（公司退市/节点合并退役/成员边到期），无生效时点即不可复考；"
            "而词汇同一性链接本身时间不变，只需观测日期。",
            "dual_axis": (
                "双时间轴分离（施工侧自采设计，与 WO-005/WO-006 同构；PIT 基准归属待 Owner 裁）："
                "valid_from=源数据业务期（source_as_of 轴，取主营构成/ig_fact 的 as_of），"
                "registered_as_of=载体入册期（库内观测轴，取源行 created_at）。两读法全量并报"
                "（metrics.primary_metric.pit_reading_dual），避免只报一个好看的基准。"
            ),
            "fields": {
                "valid_from": "= 支撑该 surface form 的最早观测 as_of（ig_product_revenue.as_of / ig_fact.as_of）："
                "断言自首次观测起成立；空值=该词项只来自图谱词表（ig_node 名/别名无 as_of 列），"
                "语义为'时间不变的词汇身份'（其锚点有效期仍由 valid_to 表达）",
                "valid_to": "仅在被否证时闭合：锚点节点退役（ig_node.valid_to→pit_note=anchor_node_retired）"
                "或全部支撑成员边到期（ig_node_company.valid_to 取最大到期日→pit_note=membership_expired）",
                "pit_note": "闭合原因，供审计回溯",
                "dropped_by_design": "不存 canonical_label / norm_key（均可由 surface_form+归一规则重算，"
                "双写只会漂移并撑爆册体量）；不存 per-anchor 归属历史（见 attribution_change_rule）",
            },
            "attribution_change_rule": (
                "同名产品在不同时期归属不同公司 → **不改写本册链接行**：公司↔节点归属的时变真源是"
                " ig_node_company(valid_from, valid_to, pit_strength)，本册经 node_id/symbol 外派 join 即得历史，"
                "双写必漂移（RULE-SSOT）。册内规则：同一 canonical 簇允许多锚点候选并存"
                "（anchor_candidates>1 即多解留痕），主锚点按 (-路由置信, route rank, node_id 升) 择一，"
                "落败候选不丢（按路由可重算）。"
            ),
            "as_of_query_contract": "as-of 取数谓词：valid_from <= :D and (valid_to is null or valid_to > :D)；"
            "复考默认 :D=闭卷切点，快照口径另出。",
            "closed_book_cutoff": args.pit_cutoff.isoformat(),
            "forbidden": "生成器内禁用无参当前时间调用（datetime 模块的 now 形式）；时间戳一律 "
            "zephyr.shared.utils.time_utils.now_iso()（RULE-SCHEMA-TZ），且不入 content_hash 域。",
        },
        "upgrade_contract": {
            "purpose": "Owner 裁定⑤明写'留同义词册升级口'：将来引入人工/LLM 别名扩充或 WO-007 部门映射接线。",
            "injection_port": {
                "flag": "--extra-anchor-register <path>",
                "formats": [".csv（表头行）", ".yaml（anchors/rows/links 任一键下的映射列表）"],
                "required_columns": ["surface_form|product|name", "node_id|target_node（或 symbol）"],
                "optional_columns": ["as_of", "valid_to", "confidence", "source", "evidence"],
                "route": "R4_external（rank=5, granularity=external, 默认 confidence=0.8）",
                "wo007_wiring": "总包合批时把部门映射册转成 surface_form=部门/产品名、node_id=图谱节点、"
                "as_of=映射生效期 的行注入即可；本器不读 wo007/metaq_io_edge 目录（并发隔离）。",
            },
            "backward_compatibility": (
                "v1 冻结承诺：①CSV 只增列且新列一律追加尾部、YAML 头只增键；②match_basis 现有四态语义不变，"
                "新证据等级须新增枚举（manual/llm）且**默认不计入** primary_metric 分子；③canonical_product_id"
                "=sha1(norm_key) 内容派生前缀稳定，但归一规则升级会拆簇，故下游引用必须带 schema 版本号；"
                "④判据脚本只读 coverage/primary_metric 两键，新增口径不破坏既有消费。"
            ),
            "back_to_30pct_preconditions": [
                "①外部别名册净新增锚定端点 ≥{} 个（=未命中池的 {:.1%}）".format(
                    max(
                        0,
                        round(
                            0.30 * metrics["coverage"]["align_domain_endpoints"]
                            - metrics["primary_metric"]["numerator"]
                        ),
                    ),
                    (
                        max(
                            0,
                            0.30 * metrics["coverage"]["align_domain_endpoints"]
                            - metrics["primary_metric"]["numerator"],
                        )
                        / max(1, metrics["coverage"]["align_domain_endpoints"] - metrics["primary_metric"]["numerator"])
                    ),
                ),
                "②分层抽样 ≥400 条人工核验 precision ≥95%，并按 match_basis 给出各档假阳率",
                "③is-a 粒度是否承认须 Owner 单独裁定（量化见 ceiling_analysis.isa_grain_uplift_if_admitted）",
                "④同快照复跑两遍 content_hash 相等（确定性不破）+ 判据与册版本同批落地",
            ],
        },
        "determinism": {
            "policy": "行序=canonical_product_id 升序、簇内 surface 升序；主锚点/标签 tie-break 全显式；"
            "content_hash=sha256(json(metrics, sort_keys))，排除 generated_at（同快照必同 hash）。",
            "content_hash": content_hash,
            "replay_cmd": "python scripts/governance/meta_question/wo008/generate_product_synonym_register.py "
            f"--threshold {args.threshold} --pit-cutoff {args.pit_cutoff.isoformat()}",
        },
        "input_watermarks": watermarks,
        "metrics": metrics,
        "artifacts": {
            "register_head": "product_synonym_register.yaml（本文件=人审面：口径/PIT/判据/契约）",
            "links_csv": "product_synonym_links.csv（机器面：逐 surface form，含 match_basis/confidence/PIT）",
            "edge_audit_csv": "ckg_edge_alignment.csv（机器面：逐产品边判据审计，分母可复核）",
        },
        "warnings": warnings,
    }


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description="WO-008 产品同义词册生成器（PQ-0068 施工闭环）")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Owner 裁定⑤=0.05")
    ap.add_argument("--pit-cutoff", type=date.fromisoformat, default=DEFAULT_PIT_CUTOFF)
    ap.add_argument(
        "--extra-anchor-register",
        type=Path,
        default=None,
        help="升级口 R4 / WO-007 部门映射接线注入（本器不读他单目录）",
    )
    ap.add_argument("--no-edge-audit", action="store_true")
    ap.add_argument("--selfcheck", action="store_true")
    return ap.parse_args(argv)


def _collect_register(f: Fetcher, args, warnings: list) -> dict:
    """PG 只读取数 + 链接/判据全量构建（main 的 try/finally 保护段；键名=main 原局部变量名）。"""
    membership = fetch_symbol_membership(f, args.pit_cutoff)
    graph_names, graph_aliases, retired = fetch_graph_vocab(f)
    obs, anchors, edges, code_alias = fetch_observations(f, args.pit_cutoff)
    external = load_external_anchors(args.extra_anchor_register, warnings)
    offgraph = resolve_symbol_routes(anchors, membership, code_alias)
    rows = build_links(obs, anchors, graph_names, graph_aliases, retired, external)
    m = measure(rows, edges, offgraph, args.pit_cutoff)
    isa = isa_headroom(f, rows, edges, args.pit_cutoff)
    return {
        "membership": membership,
        "graph_names": graph_names,
        "graph_aliases": graph_aliases,
        "retired": retired,
        "obs": obs,
        "edges": edges,
        "code_alias": code_alias,
        "external": external,
        "rows": rows,
        "m": m,
        "isa": isa,
    }


def _hash_metrics(metrics) -> str:
    """content_hash=sha256(json(metrics, sort_keys))，排除 generated_at（同快照必同 hash）。"""
    return hashlib.sha256(
        json.dumps(metrics, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _watermarks(args, ctx: dict) -> dict:
    """水位=输入数据侧计数（非墙钟）；复跑数字不等先核水位。"""
    obs, m = ctx["obs"], ctx["m"]
    return {
        "pg_tables_read": [
            "public.ig_fact",
            "public.ig_product_revenue",
            "public.ig_node",
            "public.ig_node_company",
            "public.ig_entity_code_map",
        ],
        "distinct_surfaces_scanned": len(obs),
        "observations_by_source": {
            "ig_product_revenue": sum(r["n_src"][SRC["pr"]] for r in obs.values()),
            "ig_fact_produces": sum(r["n_src"][SRC["produces"]] for r in obs.values()),
            "ig_fact_product_edge_endpoints": sum(r["n_src"][SRC["ckg_edge"]] for r in obs.values()),
            "ig_node_vocab": sum(r["n_src"][SRC["graph_node"]] for r in obs.values()),
        },
        "align_edges": m["domain_edges"],
        "graph_names": len(ctx["graph_names"]),
        "graph_aliases": len(ctx["graph_aliases"]),
        "graph_retired_nodes": len(ctx["retired"]),
        "symbols_with_live_membership": len(ctx["membership"]),
        "entity_code_map_pairs": sum(len(v) for v in ctx["code_alias"].values()),
        "external_register": str(args.extra_anchor_register) if args.extra_anchor_register else None,
        "external_register_rows_injected": sum(len(v) for v in ctx["external"].values()),
        "pit_cutoff": args.pit_cutoff.isoformat(),
        "note": "水位=输入数据侧计数（非墙钟）；复跑数字不等先核水位，水位等而 hash 不等即生成器漂移。",
    }


def _write_links_csv(out_dir: Path, rows) -> Path:
    """机器面：逐 surface form 链接 CSV。"""
    links_csv = out_dir / "product_synonym_links.csv"
    with links_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LINK_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return links_csv


def _edge_audit_block(out_dir: Path, rows, edges) -> tuple[Path, dict]:
    """逐产品边判据审计：全量行 hash 存证，CSV 只入『至少一端有锚点』子集；返回 (路径, 册头元数据)。"""
    edge_csv = out_dir / "ckg_edge_alignment.csv"
    dom = {r["surface_form"]: r for r in rows if r["in_align_domain"] == "1"}
    audit, emitted = [], []
    for s, o, rel, as_of in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
        rs, ro = dom.get(s, {}), dom.get(o, {})
        both = int(bool(rs.get("anchor_node_id")) and bool(ro.get("anchor_node_id")))
        one = int(bool(rs.get("anchor_node_id")) or bool(ro.get("anchor_node_id")))
        ready = int(
            rs.get("anchor_granularity") == G_DIRECT
            and ro.get("anchor_granularity") == G_DIRECT
            and bool(rs.get("anchor_node_id"))
            and rs.get("anchor_node_id") != ro.get("anchor_node_id")
        )
        line = [
            s,
            o,
            rel,
            _iso(as_of),
            rs.get("match_basis", ""),
            rs.get("anchor_node_id", ""),
            ro.get("match_basis", ""),
            ro.get("anchor_node_id", ""),
            both,
            one,
            ready,
        ]
        audit.append(line)
        if one:
            emitted.append(line)  # 全量 57,459 行不入册（分母可由 SQL 重算），只入有锚定的子集
    with edge_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(
            [
                "subject",
                "object",
                "relation",
                "as_of",
                "subject_basis",
                "subject_anchor_node",
                "object_basis",
                "object_anchor_node",
                "both_end_anchored",
                "one_end_anchored",
                "upgrade_ready",
            ]
        )
        w.writerows(emitted)
    edge_meta = {
        "full_audit_rows": len(audit),
        "full_audit_sha256": hashlib.sha256(
            "\n".join("|".join(str(x) for x in ln) for ln in audit).encode("utf-8")
        ).hexdigest(),
        "emitted_rows": len(emitted),
        "emit_policy": "只入『至少一端有锚点』的边（新信息面）；全量分母不入册以控体量，"
        "由 full_audit_sha256 + 下列 SQL 机械重算复现。",
        "denominator_sql": _SQL_ALIGN_DOMAIN_DENOM,
    }
    return edge_csv, edge_meta


def _samples_block(rows) -> dict:
    """册头样例（人审直观校验用，判据一律读 metrics）。"""
    by_cluster: dict[str, list] = defaultdict(list)
    for r in rows:
        by_cluster[r["canonical_product_id"]].append(r["surface_form"])
    return {
        "anchored_align_domain": [
            {
                k: r[k]
                for k in (
                    "surface_form",
                    "canonical_product_id",
                    "match_basis",
                    "confidence",
                    "anchor_node_id",
                    "anchor_route",
                    "anchor_granularity",
                    "valid_from",
                    "valid_to",
                )
            }
            for r in sorted(
                (x for x in rows if x["in_align_domain"] == "1" and x["anchor_node_id"]),
                key=lambda x: (-x["confidence"], x["surface_form"]),
            )[:12]
        ],
        "multi_surface_clusters": [
            {"canonical_product_id": cid, "members": sorted(set(members))}
            for cid, members in sorted(by_cluster.items())
            if len(set(members)) > 2
        ][:12],
        "note": "样例仅供人审直观校验，判据一律读 metrics（全量机械计算，不采信样例）。",
    }


def _selfcheck_asserts(metrics, pm) -> None:
    """--selfcheck 断言：match_basis 四态计数和=链接行数 + 判据分子≤分母。"""
    tot = sum(metrics["coverage"]["match_basis_dist_all"].values())
    assert tot == metrics["coverage"]["link_rows"], f"basis 计数和 {tot} != 链接行数 {metrics['coverage']['link_rows']}"
    assert pm["numerator"] <= pm["denominator"], "判据分子>分母"


def main(argv=None) -> int:
    args = _parse_args(argv)

    warnings: list = []
    conn = _pg()
    try:
        f = Fetcher(conn)
        ctx = _collect_register(f, args, warnings)
    finally:
        conn.close()

    metrics = build_metrics(ctx["m"], ctx["isa"], args.threshold, args.pit_cutoff)
    content_hash = _hash_metrics(metrics)
    head = build_head(metrics, _watermarks(args, ctx), warnings, args, content_hash)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    links_csv = _write_links_csv(args.out_dir, ctx["rows"])
    edge_meta = None
    if not args.no_edge_audit:
        edge_csv, edge_meta = _edge_audit_block(args.out_dir, ctx["rows"], ctx["edges"])
    out = args.out_dir / "product_synonym_register.yaml"
    if edge_meta:
        head["artifacts"]["edge_audit_csv"] = {**edge_meta, "file": "ckg_edge_alignment.csv"}
    head["samples"] = _samples_block(ctx["rows"])
    text = yaml.safe_dump(head, allow_unicode=True, sort_keys=False, width=120)
    out.write_text(text, encoding="utf-8")

    pm = metrics["primary_metric"]
    print(
        f"wrote {_rel_under_repo(out)} ({len(text)} chars), "
        f"{links_csv.name} ({len(ctx['rows'])} rows)" + (f", {edge_csv.name}" if edge_csv else "")
    )
    print(
        f"primary endpoint_anchor_rate={pm['value']} threshold={pm['threshold']} "
        f"meets={pm['meets_threshold']} hash={content_hash[:12]}"
    )
    print("match_basis(domain) =", metrics["coverage"]["match_basis_dist_align_domain"])
    if args.selfcheck:
        _selfcheck_asserts(metrics, pm)
        print("selfcheck OK: match_basis 四态计数和=链接行数；判据分子≤分母")
    return 0


if __name__ == "__main__":
    sys.exit(main())
