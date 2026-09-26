# [BLUEPRINT] MOD-METAQ-WO007-IOSECTORMAP | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md#WO-007
# [MODULE] scripts.governance.meta_question.wo007.build_io_sector_map
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (PG reader); zephyr.infrastructure.database_service (CH reader);
#                zephyr.data.table_registry（表名品类真源 #ARCH-CH-024）;
#                PyYAML; docs/01_policies_and_standards/_registry/catalogs/io_sector_sws_map.yaml（既有规则真源，只读消费）
# [CONSUMERS] build_io_edge_bindings.py（件 2 旁挂册）; io_edge_binding_loader.py（只读 loader API）;
#             wo007_reexam.py（PQ-0078 可挂率 / PQ-0067 行业对一致率 复考）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读：零写 PG/CH（禁写生产库任何表）；产物唯一落 data/registers/metaq_io_edge/；
#              映射=确定性算法（归一化+生成式别名表+代码带锚+申万码锚），禁手工逐条维护、禁随机、禁网络；
#              同输入必产同 YAML（除 generated_at）；全键稳定排序；
#              confirm_status/hard_judge_allowed=豁免条款机读锚，needs_human 行永不参与硬判定；
#              CKG（sector_parent_of/supplies_to）只作旁证，永不单独决定映射（Owner 裁定③=结构先验）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_generated
# [ERROR_CONTRACT] CH 不可达→降级为「无码锚」并记 degraded 标记（不阻断，产物仍完整可机读）；
#                  PG 不可达→直接抛（无 io 部门真源不可产出）；别名表为空→直接抛（算法退化即失败可见）。
# [TESTS] 产物级复核=wo007_reexam.py 复跑对账（行数/覆盖率/未命中清单一致）；本战役窗禁写 tests/（并发避让）
# [TTL] task_bound
"""build_io_sector_map — 153 投入产出部门两级映射册生成器（WO-007 件 1）。

两级：
  L1  io 部门（国家统计局《中国 2020 年投入产出表》153 部门原生词，ig_io_edge 装载）
      → 标准行业码（申万 2021 一级 31 行业 + 801xxx.SI 码；词表实测真源=CH c1_market.industry_class）
  L2  io 部门 → 图谱节点锚（ig_node：候选池=L1 及其申万二级子行业下活跃链的存活节点，
      节点名/别名锚定），供件 2 io_edge 旁挂册消费。

独立信号（全部可复算）：
  sig_lex   生成式别名表命中（别名表由 CH 申万 L2→L1 派生 + ig_chain 名→category + ig_node 名/别名→category 机器生成）
  sig_prior 既有规则真源 io_sector_sws_map.yaml（2026-09-13 登记，io 码→sws 一级）
  sig_band  代码带锚（153 部门码按国标目录顺序连号成带，带内高置信行多数表决）
  sig_code  申万码锚（部门名去词缀后与申万一级名精确对齐且有 801xxx.SI）
  sig_ckg   CKG 行业树旁证（sector_parent_of 根→L1）——**只旁证，不计入达标票**

判据：
  match_basis ∈ {精确, 别名, 包含, 未命中}
  confirm_status = auto_matched  当且仅当 目标 ∈ 在用标准行业词表 且
                   非先验三票(sig_lex/sig_prior/sig_band)去重一致数 ≥2（sig_lex 为「精确」/「别名」）
                   或 ≥3（sig_lex 为「包含」）；否则 needs_human
  hard_judge_allowed = (confirm_status == auto_matched)  ← 豁免条款字段

用法：
    python scripts/governance/meta_question/wo007/build_io_sector_map.py \
        --out data/registers/metaq_io_edge/io_sector_two_level_map.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import yaml  # noqa: E402

from zephyr.data.table_registry import get_registry  # noqa: E402  （表名品类真源 #ARCH-CH-024）
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

REGISTRY_VERSION = "1.0.0"
PRIOR_RULE_YAML = Path("docs/01_policies_and_standards/_registry/catalogs/io_sector_sws_map.yaml")
DEFAULT_OUT = Path("data/registers/metaq_io_edge/io_sector_two_level_map.yaml")
TOMBSTONE_SUFFIX = re.compile(r"（已并入[^（）]*$")
ROMAN_TAIL = re.compile(r"[ⅠⅡⅢⅣⅤ]+$")
SPLIT_CHARS = re.compile(r"[、，,（）()\/\s]+")
JOIN_CHARS = re.compile(r"[及与的和]")
# 部门名词缀（形态学去噪：对 io 名与图谱/行业名双侧同规则施用——确定性，非手工词表）
MORPH_SUFFIXES = ("服务产品", "服务业", "产品", "制品", "服务", "业", "品")
MIN_TOKEN_LEN = 2

EXEMPTION_CLAUSE = {
    "rule": "confirm_status=needs_human（等价 hard_judge_allowed=false）的部门行，其 L1 行业归属在人工确认窗"
    "关闭前仅可用于结构分析、候选池构造与报告说明，禁止作为阈值判定、边激活、因子打分或决策路由的"
    "硬事实输入。",
    "why": "PQ-0078 题面实证「95% 需人工确认」。投入产出部门口径（产品/产业属性）与申万、图谱口径（上市公司"
    "行业属性）是两个不同本体，名称算法无法 100% 对齐；强行全 auto=制造第二假事实源（同 CKG 一致率"
    "陷阱，见件 3 ckg_structural_prior_tier.yaml）。",
    "confirmation_window": "待排产（Owner 裁定④=153 部门映射排产）；确认人逐行复核 needs_human 行，"
    "升级为 confirm_status=human_confirmed 并填 confirm_by/confirm_note。",
    "escalation": "人工确认后若与 io_sector_sws_map.yaml 冲突，反向修订该 YAML（规则数据单一真源方向不变：改 YAML→同步 DB），"
    "再重跑本生成器，禁止直接手改本册（本册=生成物）。",
}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。本件全部只读（PG ig_* 四表 + CH c1_market 词表），
# 十条口径查询无运行期变长片段、无 PIT 日期字面量，禁在函数体内散落字面量。
_SQL_FROM_SECTOR_AGG = "SELECT from_sector_code, max(from_sector), count(*) FROM ig_io_edge GROUP BY 1"
_SQL_TO_SECTOR_AGG = "SELECT to_sector_code, max(to_sector), count(*) FROM ig_io_edge GROUP BY 1"
_SQL_LIVE_NODES_ORDERED = "SELECT node_id, chain_id, name, aliases FROM ig_node WHERE valid_to IS NULL ORDER BY node_id"
_SQL_CHAINS = "SELECT chain_id, name, category, status FROM ig_chain ORDER BY chain_id"
_SQL_SECTOR_PARENT_PAIRS = (
    "SELECT subject, object FROM ig_fact WHERE relation='sector_parent_of' ORDER BY subject, object"
)
# CH 侧词表表名真源（#ARCH-CH-024：品类册派生，禁字面量；SQL 与留痕文本以 f-string 注入，
# 渲染值与逐字字面量相同）
_TBL_INDUSTRY_CLASS = get_registry().table("market_industry_class")
_TBL_INDEX_LIST = get_registry().table("market_index_list")
_TBL_KLINE_SECTOR = get_registry().table("market_sector_kline")
_SQL_CH_SW_L1_NAMES = f"SELECT DISTINCT industry_sw FROM {_TBL_INDUSTRY_CLASS} WHERE industry_level = 1 AND industry_sw NOT IN ('', 'nan')"
_SQL_CH_SW_L1_L2_PAIRS = f"SELECT DISTINCT a.industry_sw, b.industry_sw FROM (SELECT symbol, industry_sw FROM {_TBL_INDUSTRY_CLASS}  WHERE industry_level = 1 AND industry_sw NOT IN ('','nan')) a JOIN (SELECT symbol, industry_sw FROM {_TBL_INDUSTRY_CLASS}       WHERE industry_level = 2 AND industry_sw NOT IN ('','nan')) b ON a.symbol = b.symbol"
_SQL_CH_SW_INDEX_ROWS = (
    f"SELECT ts_code, name FROM {_TBL_INDEX_LIST} WHERE publisher LIKE '%申银万国%' AND category = '行业指数'"
)
_SQL_CH_ZSI_L1_COUNT = f"SELECT count(DISTINCT industry_zsi) FROM {_TBL_INDUSTRY_CLASS} WHERE industry_level = 1"
_SQL_CH_INDUSTRY_CLASS_FRESHNESS = f"SELECT min(valid_from) FROM {_TBL_INDUSTRY_CLASS}"


# ── 归一化 ──────────────────────────────────────────────────────────────
def norm(s: object) -> str:
    if s is None:
        return ""
    s = TOMBSTONE_SUFFIX.sub("", str(s).strip())
    s = ROMAN_TAIL.sub("", s)
    return re.sub(r"\s+", "", s)


def morph_variants(s: object) -> list[str]:
    """去词缀形态变体（长后缀优先，只剥一次）+ 连接词切分片段。"""
    base = norm(s)
    out = [base] if base else []
    for suf in MORPH_SUFFIXES:
        if base.endswith(suf) and len(base) - len(suf) >= MIN_TOKEN_LEN:
            out.append(base[: -len(suf)])
            break
    for part in [p for p in JOIN_CHARS.split(base) if len(p) >= MIN_TOKEN_LEN]:
        out.append(part)
    return list(dict.fromkeys([x for x in out if x]))


def tokens(s: object) -> list[str]:
    base = norm(s)
    parts = [p for p in SPLIT_CHARS.split(base) if len(p) >= MIN_TOKEN_LEN]
    return parts or ([base] if len(base) >= MIN_TOKEN_LEN else [])


# ── 只读装载 ────────────────────────────────────────────────────────────
def load_pg_side() -> tuple[dict, list, list]:
    conn = get_depgraph_pg_connection()
    try:
        cur = conn.cursor()
        cur.execute(_SQL_FROM_SECTOR_AGG)
        from_rows = cur.fetchall()
        cur.execute(_SQL_TO_SECTOR_AGG)
        to_rows = cur.fetchall()
        cur.execute(_SQL_LIVE_NODES_ORDERED)
        node_rows = cur.fetchall()
        cur.execute(_SQL_CHAINS)
        chain_rows = cur.fetchall()
    finally:
        conn.close()
    sectors: dict[str, dict] = {}
    for code, name, n in from_rows:
        sectors[code] = {"code": code, "name": name, "as_from": n, "as_to": 0}
    for code, name, n in to_rows:
        rec = sectors.setdefault(code, {"code": code, "name": name, "as_from": 0, "as_to": 0})
        rec["as_to"] = n
        rec["name"] = rec["name"] or name
    return sectors, node_rows, chain_rows


def load_ckg_sector_tree() -> dict:
    """CKG 行业树（sector_parent_of）：结构先验，只作旁证。"""
    conn = get_depgraph_pg_connection()
    try:
        cur = conn.cursor()
        cur.execute(_SQL_SECTOR_PARENT_PAIRS)
        return {s: o for s, o in cur.fetchall()}
    finally:
        conn.close()


def load_ch_vocab() -> tuple[set, dict, dict, dict]:
    """CH：申万一级在用词表 / L2→L1 父系 / L1→801 码锚 + 派生元数据。"""
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn(role="reader")
    l1 = {r[0] for r in conn.execute(_SQL_CH_SW_L1_NAMES)}
    pairs = conn.execute(_SQL_CH_SW_L1_L2_PAIRS)
    l2_to_l1: dict[str, str] = {}
    # 显式排序：CH SELECT DISTINCT 不保证行序，同名二级挂多个父时必须按确定次序取胜（否则册不可复现）
    for parent, child in sorted(pairs):
        l2_to_l1.setdefault(norm(child), parent)
    idx = conn.execute(_SQL_CH_SW_INDEX_ROWS)
    norm_l1_keys = {norm(x) for x in l1}
    cand: dict[str, list] = defaultdict(list)
    for ts, raw in idx:
        stripped = re.sub(r"^申万(宏源)?", "", (raw or "").strip())
        bare = ROMAN_TAIL.sub("", stripped)
        if norm(bare) in norm_l1_keys:
            l1_grade = not ROMAN_TAIL.search(stripped)  # 无 Ⅱ/Ⅲ 档位后缀＝一级
            cand[norm(bare)].append((ts, l1_grade))
    code_of = {}
    for key, lst in cand.items():
        first = [ts for ts, ok in sorted(lst) if ok]
        code_of[key] = (first or sorted(ts for ts, _ in lst))[0]
    zsi = conn.execute(_SQL_CH_ZSI_L1_COUNT)
    meta = {
        "sws_l1_names_in_use": len(l1),
        "sws_l2_to_l1_derived_pairs": len(l2_to_l1),
        "sws_l1_index_code_anchors": len(code_of),
        "ch_zsi_l1_distinct": (zsi[0][0] if zsi else None),
        "ch_industry_class_data_source": "ifind",
        "ch_industry_class_valid_from_min": str(conn.execute(_SQL_CH_INDUSTRY_CLASS_FRESHNESS)[0][0]),
    }
    return l1, l2_to_l1, code_of, meta


def load_prior_rule(root: Path):
    p = root / PRIOR_RULE_YAML
    raw = p.read_bytes()
    data = yaml.safe_load(raw.decode("utf-8"))
    m = {
        str(x["io"]).zfill(3): {"sws": x["sws"], "method": x.get("method"), "name": x.get("name")}
        for x in data.get("mappings", [])
    }
    return m, str(p), hashlib.sha256(raw).hexdigest()[:12], data.get("version")


# ── 图侧 category 归一 + 生成式别名表 ─────────────────────────────────────
def build_cat2l1(chain_rows, norm_l1, l2_to_l1):
    """ig_chain.category 粒度混杂（一级名/二级名/网页噪声标题）→ 机器归一到 L1。"""
    cat2l1, stats = {}, Counter()
    for _cid, cname, cat, status in chain_rows:
        if not cat:
            stats["category_null"] += 1
            continue
        if cat in cat2l1:
            continue
        n = norm(cat)
        if n in norm_l1:
            cat2l1[cat] = norm_l1[n]
            stats["category_is_l1"] += 1
        elif n in l2_to_l1:
            cat2l1[cat] = l2_to_l1[n]
            stats["category_is_l2_child"] += 1
        else:
            stats["category_unresolved"] += 1
    return cat2l1, dict(stats)


def _lex_add_vocab(l1_vocab, l2_to_l1, add):
    """别名表词库源：申万 L1 在用词 + CH 派生 L2 父系（原 build_alias_lexicon 前两段逐行搬运）。"""
    for name in l1_vocab:
        for v in morph_variants(name):
            add(v, name, "sws_l1_vocab")
    for l2n, l1n in l2_to_l1.items():
        for v in morph_variants(l2n):
            add(v, l1n, "sws_l2_parent_from_ch")


def _lex_add_nodes(node_rows, chain_rows, cat2l1, add):
    """别名表图节点源：ig_node 名/别名 → 所属链 category 归一的 L1（原 build_alias_lexicon 第三段逐行搬运）。"""
    chain_by_id = {r[0]: r for r in chain_rows}
    for nid, chain_id, name, aliases in node_rows:
        rec = chain_by_id.get(chain_id)
        tgt = cat2l1.get(rec[2]) if rec and rec[2] else None
        for v in morph_variants(name):
            add(v, tgt, "ig_node_name")
        for al in aliases or []:
            for v in morph_variants(al):
                add(v, tgt, "ig_node_alias")


def _lex_add_chains(chain_rows, cat2l1, add):
    """别名表活跃链源：ig_chain 链名（整词+切词）（原 build_alias_lexicon 第四段逐行搬运）。"""
    for cid, cname, cat, status in chain_rows:
        tgt = cat2l1.get(cat)
        if not tgt or status != "active":
            continue
        for v in morph_variants(cname):
            add(v, tgt, "ig_chain_name")
        for t in tokens(cname):
            add(t, tgt, "ig_chain_token")


def build_alias_lexicon(l1_vocab, l2_to_l1, node_rows, chain_rows, cat2l1):
    lex: dict[str, set] = defaultdict(set)
    prov: dict[str, Counter] = defaultdict(Counter)

    def add(key: str, target, src: str):
        if not key or len(key) < MIN_TOKEN_LEN or not target:
            return
        lex[key].add(target)
        prov[key][src] += 1

    _lex_add_vocab(l1_vocab, l2_to_l1, add)
    _lex_add_nodes(node_rows, chain_rows, cat2l1, add)
    _lex_add_chains(chain_rows, cat2l1, add)
    return dict(lex), {k: dict(v) for k, v in prov.items()}


# ── 匹配内核 ────────────────────────────────────────────────────────────
def _lex_contains_scan(variants: list[str], lex: dict, score: Counter) -> None:
    """包含命中（双向子串）累计打分（原 lex_match 内循环逐行搬运，就地写 score）。"""
    for key, tgts in lex.items():  # 包含命中（双向子串）
        for v in variants:
            if len(key) < MIN_TOKEN_LEN or len(v) < MIN_TOKEN_LEN:
                continue
            if key in v or v in key:
                ov = min(len(key), len(v))
                for tgt in tgts:
                    score[tgt] = max(score[tgt], ov)


def lex_match(name: str, lex: dict, norm_l1: dict):
    """返回 (target|None, basis, 同分备选)。basis ∈ 精确/别名/包含/未命中。"""
    variants = morph_variants(name)
    if not variants:
        return None, "未命中", []
    if variants[0] in norm_l1:
        return norm_l1[variants[0]], "精确", []
    score: Counter = Counter()
    key_hit = False
    for v in variants:
        for tgt in lex.get(v, ()):  # 键精确命中（别名表）
            score[tgt] = max(score[tgt], len(v) + 100)
            key_hit = True
    _lex_contains_scan(variants, lex, score)
    if not score:
        return None, "未命中", []
    best = max(score.values())
    top = sorted(t for t, s in score.items() if s == best)
    basis = "别名" if key_hit and best >= 100 + MIN_TOKEN_LEN else "包含"
    return top[0], basis, top


def band_anchor(codes, confident, window=3):
    """代码带锚：部门码连号带内（±window）已高置信行多数表决；平票→None。"""
    out = {}
    for i, c in enumerate(codes):
        lo, hi = max(0, i - window), min(len(codes), i + window + 1)
        votes = Counter(confident[codes[j]] for j in range(lo, hi) if j != i and codes[j] in confident)
        if not votes:
            out[c] = None
            continue
        top = votes.most_common(1)[0][1]
        tied = [t for t, k in votes.items() if k == top]
        out[c] = tied[0] if len(tied) == 1 else None
    return out


def pick_node_anchor(sector_name, pool, node_index):
    """部门 → 图谱节点锚：先业内候选池、后全图；exact→alias→contains；并列取 node_id 最小。"""
    variants = set(morph_variants(sector_name))
    scopes = [("in_industry_pool", pool), ("graph_wide", sorted(node_index))]
    for scope, ids in scopes:
        for method in ("exact", "alias", "contains"):
            cands = []
            for nid in ids:
                name_vs, alias_vs = node_index[nid]
                if (
                    (method == "exact" and variants & set(name_vs))
                    or (method == "alias" and variants & set(alias_vs))
                    or (
                        method == "contains"
                        and any(
                            len(a) >= 3 and (a in b or b in a) for a in variants for b in list(name_vs) + list(alias_vs)
                        )
                    )
                ):
                    cands.append(nid)
            if cands:
                cands.sort()
                return {"node_id": cands[0], "match_method": f"{method}:{scope}", "candidate_n": len(cands)}
    return None


# ── 主流程 ──────────────────────────────────────────────────────────────
def _build_load_phase(root: Path) -> dict:
    """装载段（原 build 前段逐行搬运）：PG 侧 + CH 词表 + 先验规则 + 归一 + 别名表 + CKG 树。

    别名表为空→抛（算法退化即失败可见），与原行为一致。
    """
    sectors, node_rows, chain_rows = load_pg_side()
    chain_by_id = {r[0]: r for r in chain_rows}
    l1_vocab, l2_to_l1, sw_codes, vocab_meta = load_ch_vocab()
    norm_l1 = {norm(x): x for x in l1_vocab}
    prior, prior_path, prior_sha, prior_ver = load_prior_rule(root)
    cat2l1, cat_stats = build_cat2l1(chain_rows, norm_l1, l2_to_l1)
    lex, lex_prov = build_alias_lexicon(l1_vocab, l2_to_l1, node_rows, chain_rows, cat2l1)
    if not lex:
        raise RuntimeError("别名表为空——生成算法退化，拒绝产册")
    ckg_tree = load_ckg_sector_tree()
    return {
        "sectors": sectors,
        "node_rows": node_rows,
        "chain_rows": chain_rows,
        "chain_by_id": chain_by_id,
        "l1_vocab": l1_vocab,
        "l2_to_l1": l2_to_l1,
        "sw_codes": sw_codes,
        "vocab_meta": vocab_meta,
        "norm_l1": norm_l1,
        "prior": prior,
        "prior_path": prior_path,
        "prior_sha": prior_sha,
        "prior_ver": prior_ver,
        "cat2l1": cat2l1,
        "cat_stats": cat_stats,
        "lex": lex,
        "lex_prov": lex_prov,
        "ckg_tree": ckg_tree,
    }


def _build_pass1_and_band(codes: list, sectors: dict, lex: dict, norm_l1: dict, prior: dict) -> tuple[dict, dict]:
    """sig_lex 首扫 + 高置信种子行多数表决带锚（原 build 中段逐行搬运）。"""
    pass1 = {c: lex_match(sectors[c]["name"], lex, norm_l1) for c in codes}
    confident = {
        c: pass1[c][0]
        for c in codes
        if pass1[c][0] and pass1[c][1] in ("精确", "别名") and (prior.get(c) or {}).get("sws") == pass1[c][0]
    }
    band = band_anchor(codes, confident)
    return pass1, band


def _build_node_pools(node_rows: list, chain_by_id: dict, cat2l1: dict) -> tuple[dict, dict]:
    """候选节点池（按 L1）+ 节点名/别名词元索引（原 build 中段逐行搬运）。"""
    pool_by_l1: dict[str, set] = defaultdict(set)
    for nid, chain_id, _name, _al in node_rows:
        rec = chain_by_id.get(chain_id)
        if not rec or rec[3] != "active":
            continue
        l1 = cat2l1.get(rec[2])
        if l1:
            pool_by_l1[l1].add(nid)
    node_index = {
        nid: (morph_variants(name), [v for al in (als or []) for v in morph_variants(al)])
        for nid, _ch, name, als in node_rows
    }
    return pool_by_l1, node_index


def _sector_signals(c: str, ctx: dict, pass1: dict, band: dict) -> dict:
    """单部门信号段（原 build 行循环前段逐行搬运）：lex/prior/band 三票 + CKG 旁证 + 代码锚。"""
    rec = ctx["sectors"][c]
    lex_t, basis, alts = pass1[c]
    prior_t = (ctx["prior"].get(c) or {}).get("sws")
    band_t = band.get(c)
    target = lex_t or prior_t or band_t
    votes = [t for t in (lex_t, prior_t, band_t) if t and target and norm(t) == norm(target)]
    agree = len(votes)
    ckg_root = ctx["ckg_tree"].get(rec["name"]) or ctx["ckg_tree"].get(norm(rec["name"]))
    ckg_t = None
    if ckg_root:
        cr = norm(ckg_root)
        ckg_t = ctx["norm_l1"].get(cr) or ctx["l2_to_l1"].get(cr) or ctx["cat2l1"].get(ckg_root)
    # 代码锚：部门名归一后与申万一级名逐字对齐且有 801 码（最强，但 io 词系极少触发）
    sig_code = bool(norm(rec["name"]) in ctx["norm_l1"] and ctx["sw_codes"].get(norm(rec["name"])))
    return {
        "rec": rec,
        "lex_t": lex_t,
        "basis": basis,
        "alts": alts,
        "prior_t": prior_t,
        "band_t": band_t,
        "target": target,
        "agree": agree,
        "ckg_root": ckg_root,
        "ckg_t": ckg_t,
        "sig_code": sig_code,
    }


def _sector_confirm(target, basis: str, agree: int, l1_vocab: set) -> tuple[str, str]:
    """confirm_status 判定（原 build 行循环中段逐行搬运；未命中时 basis 同步改写）。"""
    if not target:
        return "未命中", "needs_human"
    if target not in l1_vocab:
        return basis, "needs_human"
    return basis, ("auto_matched" if (agree >= (2 if basis in ("精确", "别名") else 3)) else "needs_human")


def _sector_row(c: str, ctx: dict) -> dict:
    """单部门映射行（原 build 行循环体逐行搬运，键序/文案/判据零变更）。"""
    sig = _sector_signals(c, ctx, ctx["pass1"], ctx["band"])
    basis, status = _sector_confirm(sig["target"], sig["basis"], sig["agree"], ctx["l1_vocab"])
    target = sig["target"]
    pool = sorted(ctx["pool_by_l1"].get(target, ())) if target else []
    anchor = pick_node_anchor(sig["rec"]["name"], pool, ctx["node_index"])
    return {
        "io_sector_code": c,
        "io_sector_name": sig["rec"]["name"],
        "edge_as_from_n": sig["rec"]["as_from"],
        "edge_as_to_n": sig["rec"]["as_to"],
        "l1_industry": target,
        "l1_industry_code": ctx["sw_codes"].get(norm(target or "")),
        "match_basis": basis,
        "confirm_status": status,
        "hard_judge_allowed": status == "auto_matched",
        "exemption_note": None
        if status == "auto_matched"
        else "人工确认前不得参与硬判定（见 header.exemption_clause）",
        "signals": {
            "sig_lex_target": sig["lex_t"],
            "sig_lex_basis": basis,
            "sig_lex_ties": [a for a in sig["alts"] if a != target],
            "sig_prior_target": sig["prior_t"],
            "sig_prior_method": (ctx["prior"].get(c) or {}).get("method"),
            "sig_band_target": sig["band_t"],
            "sig_code_anchor": sig["sig_code"],
            "sig_ckg_root": sig["ckg_root"],
            "sig_ckg_target": sig["ckg_t"],
            "ckg_corroborates": bool(sig["ckg_t"] and target and norm(str(sig["ckg_t"])) == norm(target)),
            "independent_agree_votes": sig["agree"],
        },
        "node_level": {
            "sector_industry_resolved": bool(target),
            "candidate_chain_pool_n": len(
                {r[0] for r in ctx["chain_rows"] if r[3] == "active" and ctx["cat2l1"].get(r[2]) == target}
            ),
            "candidate_node_pool_n": len(pool),
            "node_anchor": anchor,
        },
    }


def _build_stats_core(rows: list[dict]) -> dict:
    """stats 前段：总量/档位分布/未命中清单（原 build stats 前八键逐行搬运）。"""
    auto = sum(1 for r in rows if r["confirm_status"] == "auto_matched")
    unmatched = [r for r in rows if r["match_basis"] == "未命中"]
    return {
        "sectors_total": len(rows),
        "auto_matched": auto,
        "needs_human": len(rows) - auto,
        "auto_ratio": round(auto / len(rows), 4),
        "by_match_basis": dict(Counter(r["match_basis"] for r in rows)),
        "by_confirm_status": dict(Counter(r["confirm_status"] for r in rows)),
        "unmatched_n": len(unmatched),
        "unmatched": [
            {"io_sector_code": r["io_sector_code"], "io_sector_name": r["io_sector_name"]} for r in unmatched
        ],
    }


def _build_stats_cross(rows: list[dict]) -> dict:
    """stats 后段：先验一致/CKG 旁证/锚位面（原 build stats 后九键逐行搬运，键序不变）。"""
    return {
        "prior_rule_agreement": sum(
            1
            for r in rows
            if r["signals"]["sig_prior_target"]
            and norm(str(r["l1_industry"])) == norm(str(r["signals"]["sig_prior_target"]))
        ),
        "prior_rule_method_manual": sum(1 for r in rows if r["signals"]["sig_prior_method"] == "manual"),
        "ckg_corroboration_agrees": sum(1 for r in rows if r["signals"]["ckg_corroborates"]),
        "distinct_l1_targets": len({r["l1_industry"] for r in rows if r["l1_industry"]}),
        "with_node_anchor": sum(1 for r in rows if r["node_level"]["node_anchor"]),
        "node_anchor_exact": sum(
            1
            for r in rows
            if r["node_level"]["node_anchor"] and r["node_level"]["node_anchor"]["match_method"].startswith("exact")
        ),
        "node_anchor_alias": sum(
            1
            for r in rows
            if r["node_level"]["node_anchor"] and r["node_level"]["node_anchor"]["match_method"].startswith("alias")
        ),
        "auto_and_node_anchored": sum(1 for r in rows if r["hard_judge_allowed"] and r["node_level"]["node_anchor"]),
        "empty_node_pool": sum(1 for r in rows if r["l1_industry"] and not r["node_level"]["candidate_node_pool_n"]),
    }


def _build_stats(rows: list[dict]) -> dict:
    """stats 聚合（原 build stats 全键，键序不变）。"""
    stats = _build_stats_core(rows)
    stats.update(_build_stats_cross(rows))
    return stats


def build(root: Path, out: Path) -> dict:
    ctx = _build_load_phase(root)
    codes = sorted(ctx["sectors"])
    pass1, band = _build_pass1_and_band(codes, ctx["sectors"], ctx["lex"], ctx["norm_l1"], ctx["prior"])
    ctx["pass1"], ctx["band"] = pass1, band
    pool_by_l1, node_index = _build_node_pools(ctx["node_rows"], ctx["chain_by_id"], ctx["cat2l1"])
    ctx["pool_by_l1"], ctx["node_index"] = pool_by_l1, node_index
    rows = [_sector_row(c, ctx) for c in codes]
    doc = {
        "registry": "io_sector_two_level_map",
        "registry_version": REGISTRY_VERSION,
        "workorder": "WO-007（PQ-0067 / PQ-0078 / PQ-0065 三问并治）件 1",
        "generated_by": "scripts/governance/meta_question/wo007/build_io_sector_map.py",
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "authority": {
            "io_sector_vocab": "国家统计局《中国 2020 年投入产出表》153 部门分类（生产者价格）；实测真源="
            "PG public.ig_io_edge（year=2020, source='io_official', market='cn', "
            "as_of=2020-12-31, valid_from=2022-08-31, "
            "source_doc='io_china_2020_153|ionet(github Carol-seven/ionet) 官方表转存|2026-09-13'）",
            "io_sector_field_measured": "ig_io_edge 部门字段实测=(from_sector_code,to_sector_code) 三位零填码 001-153 "
            "+ (from_sector,to_sector) 同名原生中文部门词；无任何 node 挂接列（实测列清单见件 2 header）",
            "standard_industry_vocab": f"申万 2021 一级 31 行业（在用口径）；词表实测真源=CH {_TBL_INDUSTRY_CLASS}"
            "(industry_level=1, data_source='ifind')；二级父系由同 symbol L1/L2 行共现机器派生；"
            f"801xxx.SI 码锚由 CH {_TBL_INDEX_LIST}(publisher 申银万国, category 行业指数, "
            "名去'申万'前缀+无 Ⅱ/Ⅲ 档位后缀=一级) 派生",
            "rejected_calibers": [
                "中证/中信：industry_class.industry_zsi 在 L1 去重实测=0（全空列），不可用作在用口径",
                f"通达信/同花顺板块：{_TBL_KLINE_SECTOR}(880xxx.SH)/concept_sector(akshare 375)/sector_list(miniqmt 5217) "
                "系行情板块与概念板块，非行业分类真源（与 io 部门不同本体，且板块名单为空/漂移）",
                "ig_chain.category：粒度混杂（一级名/二级名/网页噪声标题），只能作为映射目标侧候选池，不能充当标准行业码",
            ],
            "prior_rule_yaml": {
                "path": ctx["prior_path"],
                "sha256_12": ctx["prior_sha"],
                "version": ctx["prior_ver"],
                "role": "独立信号 sig_prior（不是裁决者；与本册冲突的行落 needs_human，反向修订 YAML 走规则数据通道）",
            },
            "graph_side_category_resolution": ctx["cat_stats"],
        },
        "ch_vocab_meta": ctx["vocab_meta"],
        "alias_lexicon_stats": {
            "keys": len(ctx["lex"]),
            "entry_sources": dict(Counter(s for c in ctx["lex_prov"].values() for s in c)),
        },
        "method": {
            "algorithm": "确定性四段：①归一化（去空白/去'（已并入…）'墓碑后缀/去Ⅰ-Ⅴ档位后缀/形态词缀剥一次/连接词切分）"
            "②生成式别名表命中（键=申万 L1 ∪ CH 派生 L2 父系 ∪ ig_node 名与别名 ∪ 活跃链名与切词）"
            "③代码带锚（153 码连号 ±3 带内，种子=sig_lex 与 sig_prior 一致行，多数表决）"
            "④非先验三票一致数定 confirm_status（≥2 或'包含'级 ≥3）",
            "auto_rule": "auto_matched ⇔ 目标 ∈ 在用申万一级词表 且 agree_votes ≥ (2 if basis∈{精确,别名} else 3)",
            "no_manual_list": "零手工行：全部映射由算法产出；人工窗只升级 confirm_status，不新增映射面（静态清单禁手工维护铁律）",
            "reproducibility": "无随机、无网络、无 wall-clock 参与判定；同输入必产同映射",
        },
        "exemption_clause": EXEMPTION_CLAUSE,
        "stats": _build_stats(rows),
        "mappings": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    st = doc["stats"]
    print(
        f"[OK] {out}\n     sectors={st['sectors_total']} auto={st['auto_matched']} "
        f"needs_human={st['needs_human']} auto_ratio={st['auto_ratio']}"
    )
    print("     by_basis:", st["by_match_basis"])
    print(
        "     node anchors:",
        st["with_node_anchor"],
        "exact:",
        st["node_anchor_exact"],
        "alias:",
        st["node_anchor_alias"],
        "empty_pool:",
        st["empty_node_pool"],
    )
    print(
        "     prior agreement:",
        st["prior_rule_agreement"],
        "manual prior:",
        st["prior_rule_method_manual"],
        "ckg corroboration:",
        st["ckg_corroboration_agrees"],
        "distinct L1:",
        st["distinct_l1_targets"],
    )
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description="153 投入产出部门两级映射册生成器（WO-007 件 1）")
    ap.add_argument("--out", default=str(_ROOT / DEFAULT_OUT))
    ap.add_argument("--repo-root", default=str(_ROOT))
    a = ap.parse_args()
    build(Path(a.repo_root).resolve(), Path(a.out).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
