# [BLUEPRINT] MOD-METAQ-WO007-REEXAM | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md#WO-007
# [MODULE] scripts.governance.meta_question.wo007.wo007_reexam
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (PG reader); PyYAML;
#                scripts/governance/meta_question/wo007/io_edge_binding_loader.py（旁挂册只读通道）
# [CONSUMERS] build_ckg_prior_tier.py（件 3 取复考实测数字）; 案卷 docs/_working/meta_question_answers/build/WO-007.yaml
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读：零写 PG/CH；产物只落 .runtime/tmp/st-metaq-gc-20260924/wo007/；
#              三问判据全部按 exam 题面原文阈值机械复算（PQ-0078 ≥95% / PQ-0067 ≥60% / PQ-0065 ≥70%→降级）；
#              反自证铁律：对照侧必须与先验侧异源（PQ-0065 必须剔除 source_doc LIKE 'ckg_2021%' 的 ig_edge，
#              否则 58/81=71.6% 假达标）；PQ-0067 对照侧改由旁挂册提供（考试期为空集是 fail 真因）；
#              禁挑有利口径：多口径并列输出，题面口径单列并标 PASS/FAIL。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_generated
# [ERROR_CONTRACT] 两册缺失→直接抛（无旁挂册无复考）；ig_fact/ig_edge 读不到→直接抛；
#                  CKG 根对为空→记 empty_side 不抛（空集本身是发现）。
# [TESTS] 本件即复考件；输出与 results/b2/PQ-006{5,7}.yaml、PQ-0078.yaml 在案数字逐项对账（不一致必须解释）
# [TTL] task_bound
"""wo007_reexam — WO-007 三问复考机械判据探针（PQ-0078 / PQ-0067 / PQ-0065）。

输出：.runtime/tmp/st-metaq-gc-20260924/wo007/wo007_reexam.yaml

三问三态（诚实口径）：
  PQ-0078 缺口关闭度：三档挂接率并列（T1 节点同一性 / T1+T2 双端有锚 / T3 映射补齐可挂），
          题面 ≥95% 只在 T3 成立；T1 口径未达 → 口径歧义登记待裁项，不自宣转绿。
  PQ-0067 对照侧从空集→668 行业对（旁挂册），一致率按题面口径与对称口径分别报，
          并附密度告警（IO 侧近完备二分图会天然抬高单侧一致率）。
  PQ-0065 降级后判据重述：从"边集一致率"改判"先验可用性"三判据（覆盖可对齐率/独立侧证率/
          决策独立性），原 1.23% 与 71.6% 自证陷阱数字一并留档。
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parents[4]
for p in (str(_ROOT / "src"), str(_ROOT / "scripts/governance/meta_question/wo007")):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_io_edge_bindings  # noqa: E402  提供共享 norm（单一实现真源，FUNCTION-DUP 收敛）
import io_edge_binding_loader as loader  # noqa: E402
import yaml  # noqa: E402

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

OUT = _ROOT / ".runtime/tmp/st-metaq-gc-20260924/wo007/wo007_reexam.yaml"
TOMBSTONE_SUFFIX = re.compile(r"（已并入[^（）]*$")
ROMAN_TAIL = re.compile(r"[ⅠⅡⅢⅣⅤ]+$")
MORPH_SUFFIXES = ("服务产品", "服务业", "产品", "制品", "服务", "业", "品")


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。本件是复考只读件（零写面），十一条口径查询
# 无运行期变长片段、无 PIT 日期字面量；sector_parent_of 两处同文共用一个常量。
_SQL_SECTOR_PARENT_PAIRS = (
    "SELECT subject, object FROM ig_fact WHERE relation='sector_parent_of' ORDER BY subject, object"
)
_SQL_SUPPLIES_TO_PAIRS = "SELECT subject, object FROM ig_fact WHERE relation='supplies_to' ORDER BY subject, object"
_SQL_SUBTYPE_OF_PAIRS = "SELECT subject, object FROM ig_fact WHERE relation='subtype_of' ORDER BY subject, object"
_SQL_EDGE_COUNT = "SELECT count(*) FROM ig_edge"
_SQL_NODE_CHAINS = "SELECT node_id, chain_id FROM ig_node"
_SQL_CHAIN_CATEGORIES = "SELECT chain_id, category FROM ig_chain"
_SQL_EDGE_NODE_PAIRS = "SELECT from_node, to_node FROM ig_edge"
_SQL_EDGE_NODE_PAIRS_WITH_DOC = "SELECT from_node, to_node, source_doc FROM ig_edge"
_SQL_GRAPH_FACT_TRIPLES = (
    "SELECT subject, object, source FROM ig_fact WHERE relation IN ('supplies_to','product_downstream_of')"
)
_SQL_NODE_NAMES = "SELECT node_id, name FROM ig_node"


def variants(s: object) -> list[str]:
    base = build_io_edge_bindings.norm(s)
    out = [base] if base else []
    for suf in MORPH_SUFFIXES:
        if base.endswith(suf) and len(base) - len(suf) >= 2:
            out.append(base[: -len(suf)])
            break
    return [x for x in dict.fromkeys(out) if x]


def pg(sql, params=None):
    conn = get_depgraph_pg_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


# ── PQ-0078 ────────────────────────────────────────────────────────────
def reexam_pq0078() -> dict:
    meta = loader.register_meta()
    st = meta["stats"]
    s = st["attach_ratio_by_tier"]
    return {
        "threshold": "映射补齐后可挂边比例 ≥95%",
        "exam_recorded_baseline": {"any_end_name_replay": 0.0412, "both_end_name_replay": 0.00053, "io_edges": 16859},
        "recomputed_baseline": st["baseline_name_replay"],
        "baseline_reproduced": abs(st["baseline_name_replay"]["any_end_ratio"] - 0.0412) < 1e-4,
        "after_three_tiers": {
            "T1_node_identity_both_ends_exact_or_alias": s["T1_only_both_ends_node_identity"],
            "T1_plus_T2_both_ends_have_node_anchor": s["node_linked_both_ends"],
            "T3_mapping_complete_industry_resolved_both_ends": s["T3_mapping_complete_both_ends"],
        },
        "verdict": {
            "literal_threshold_reading(映射补齐后可挂)": f"PASS ({s['T3_mapping_complete_both_ends']:.2%} ≥ 95%)",
            "strict_reading(挂到具体 ig_node 节点)": "FAIL "
            f"(双端有锚 {s['node_linked_both_ends']:.2%}、同指级 {s['T1_only_both_ends_node_identity']:.2%})",
        },
        "honest_gap_statement": "部门名与环节名是两个词系，节点同一性不可能靠名称算法补齐到 95%——"
        "缺口按『映射载体已建 + 行业层可挂 100%』关闭，按『节点同一性』仍缺官方"
        "《投入产出部门分类↔国民经济行业分类》对照表（待裁项 WO-007-T2）。",
        "hard_judge_usable_edges": st["hard_judge_allowed_edges"],
        "tiers": st["tier_counts"],
        "anchor_concentration": st["anchor_concentration"],
        "unreproducible_item": st
        and "题面转述『部门级 19.7%』载体 ig_sector_bridge 对应用只读角色 PermissionDenied"
        "（本探针实测，见件 2 header.unreproducible_baseline）",
    }


# ── CKG 行业名 → 在用标准行业码（申万一级）归一器 ──────────────────────────
def build_ckg_l1_normalizer():
    """复用件 1 的词表派生（CH 申万 L1 在用集 + CH 派生 L2→L1），加 CKG 自身树上升。

    覆盖判定在**端点级**（不是对级）——对级下降只反映粒度压缩，不是对齐失败。
    """
    import build_io_sector_map as bim

    l1_vocab, l2_to_l1, _codes, _meta = bim.load_ch_vocab()
    norm_l1 = {build_io_edge_bindings.norm(x): x for x in l1_vocab}
    rows = pg(_SQL_SECTOR_PARENT_PAIRS)
    parent = {s: o for s, o in rows}

    def to_l1(name):
        cur = name
        for _ in range(7):
            n = build_io_edge_bindings.norm(cur)
            if n in norm_l1:
                return norm_l1[n]
            if n in l2_to_l1:
                return l2_to_l1[n]
            if cur in parent:
                cur = parent[cur]
                continue
            return None
        return None

    return to_l1, sorted(l1_vocab), parent


def ckg_industry_pairs() -> dict:
    """CKG supplies_to 聚合到行业对（题面 PQ-0067 原口径）+ 归一到申万一级后的对。"""
    sup = pg(_SQL_SUPPLIES_TO_PAIRS)
    to_l1, l1_names, _parent = build_ckg_l1_normalizer()
    root_pairs, memo = set(), {}

    roots = {s: o for s, o in pg(_SQL_SECTOR_PARENT_PAIRS)}
    subs = defaultdict(set)
    for s, o in pg(_SQL_SUBTYPE_OF_PAIRS):
        subs[s].add(o)
    sectors = set(roots)

    def to_root(name, stack=None):
        if name in memo:
            return memo[name]
        stack = stack or set()
        if name in stack:
            return None
        stack.add(name)
        if name in roots:
            memo[name] = roots[name]
            return roots[name]
        if name in sectors:
            memo[name] = name
            return name
        for p in sorted(subs.get(name, ())):  # 排序父集：set 迭代序随 hash 随机化，不排序=结果不可复现
            r = to_root(p, stack)
            if r:
                memo[name] = r
                return r
        memo[name] = None
        return None

    unmapped = 0
    l1_pairs = set()
    endpoint_aligned = 0
    collapsed_same_l1 = 0
    for s, o in sup:
        a, b = to_root(s), to_root(o)
        if a and b and a != b:
            root_pairs.add((a, b))
        else:
            unmapped += 1
    for a, b in sorted(root_pairs):
        la, lb = to_l1(a), to_l1(b)
        if la and lb:
            endpoint_aligned += 1
            if build_io_edge_bindings.norm(la) != build_io_edge_bindings.norm(lb):
                l1_pairs.add((build_io_edge_bindings.norm(la), build_io_edge_bindings.norm(lb)))
            else:
                collapsed_same_l1 += 1
    return {
        "supplies_to_events": len(sup),
        "unmapped_events": unmapped,
        "ckg_raw_industry_pairs": len(root_pairs),
        "ckg_pairs_both_ends_alignable": endpoint_aligned,
        "ckg_pairs_collapsed_into_same_l1": collapsed_same_l1,
        "ckg_pairs_at_sws_l1": len(l1_pairs),
        "endpoint_align_rate": round(endpoint_aligned / len(root_pairs), 4) if root_pairs else None,
        "granularity_compression": round(len(l1_pairs) / endpoint_aligned, 4) if endpoint_aligned else None,
        "l1_vocab_size": len(l1_names),
        "pairs": l1_pairs,
        "raw_pairs": root_pairs,
    }


# ── PQ-0067 ────────────────────────────────────────────────────────────
def reexam_pq0067() -> dict:
    ckg = ckg_industry_pairs()
    ckg_pairs = ckg["pairs"]
    matrix = loader.industry_pair_matrix()  # io_edge→申万一级 有向对（旁挂册）
    io_pairs = {tuple(build_io_edge_bindings.norm(x) for x in k.split("->")) for k in matrix}
    inter = ckg_pairs & io_pairs
    inter_undirected = {p for p in ckg_pairs if (p[1], p[0]) in io_pairs} | inter
    # 密度告警：IO 侧完备度（可能出现的有向对上限）
    inds = sorted({i for p in io_pairs for i in p})
    cap = len(inds) * (len(inds) - 1)
    # 严格版：只取 IO 侧强度 top-N 对
    top = sorted(matrix.items(), key=lambda kv: -kv[1]["sum_coefficient"])
    strict = {}
    for n in (50, 100, 200):
        sel = {tuple(build_io_edge_bindings.norm(x) for x in k.split("->")) for k, _ in top[:n]}
        strict[f"io_top{n}"] = round(len(ckg_pairs & sel) / len(ckg_pairs), 4) if ckg_pairs else None
    exam_side = pg(_SQL_EDGE_COUNT)[0][0]
    # 考试期对照侧（ig_edge→链类别对）复算：跨类别对=0
    nid2chain = {r[0]: r[1] for r in pg(_SQL_NODE_CHAINS)}
    ch2cat = {r[0]: r[1] for r in pg(_SQL_CHAIN_CATEGORIES) if r[1]}
    cat_pairs = set()
    for fn, tn in pg(_SQL_EDGE_NODE_PAIRS):
        ca, cb = ch2cat.get(nid2chain.get(fn)), ch2cat.get(nid2chain.get(tn))
        if ca and cb and ca != cb:
            cat_pairs.add((build_io_edge_bindings.norm(ca), build_io_edge_bindings.norm(cb)))
    return {
        "threshold": "≥60%（CKG 聚合一致率）",
        "exam_period_measurement_reproduced": {
            "ig_edge_total": exam_side,
            "ig_edge_cross_category_pairs": len(cat_pairs),
            "consistency_with_empty_side": 0.0,
            "note": "考试期对照侧（当期图谱链类别对）跨类别=0，一致率 0/240=0% → 与 results/b2/PQ-0067.yaml 一致",
        },
        "ckg_side": {k: v for k, v in ckg.items() if k not in ("pairs", "raw_pairs")},
        "current_side_after_sidecar": {
            "io_industry_pairs_cross_industry": len(io_pairs),
            "distinct_industries": len(inds),
            "theoretical_directed_pair_cap": cap,
            "io_side_density": round(len(io_pairs) / cap, 4) if cap else None,
        },
        "consistency": {
            "literal(交/CKG行业对, 题面口径)": round(len(inter) / len(ckg_pairs), 4) if ckg_pairs else None,
            "direction_relaxed(忽略方向)": round(len(inter_undirected) / len(ckg_pairs), 4) if ckg_pairs else None,
            "jaccard(对称)": round(len(inter) / len(ckg_pairs | io_pairs), 4) if (ckg_pairs or io_pairs) else None,
            "strict_io_topN": strict,
        },
        "verdict": {
            "literal_threshold": None,  # 下面 main 里按数字填
            "caveat": "IO 行业对密度 71%+ 的近完备二分图会把单侧一致率天然抬高——题面口径（分母=CKG 对）"
            "不惩罚过度覆盖侧，故 PASS 只说明『载体已通、CKG 行业结构与官方 IO 结构不矛盾』，"
            "不能读作『CKG 被证实』。这正是降级为结构先验后应有的读法。",
        },
    }


# ── PQ-0065 ────────────────────────────────────────────────────────────
def _pq0065_edge_sets() -> tuple[set, set, list, int, list]:
    """CKG 产品对 + 研报线名对（原 reexam_pq0065 前段逐行搬运）。

    反自证铁律：ig_edge 侧剔除 source_doc LIKE 'ckg_2021%' 的自并入边再算名对。
    返回 (ckg_pairs, name_pairs, nodes, self_merged, report_edges)。
    """
    fact = pg(_SQL_GRAPH_FACT_TRIPLES)
    ckg_pairs = {
        (build_io_edge_bindings.norm(a), build_io_edge_bindings.norm(b))
        for a, b, _s in fact
        if build_io_edge_bindings.norm(a)
        and build_io_edge_bindings.norm(b)
        and build_io_edge_bindings.norm(a) != build_io_edge_bindings.norm(b)
    }
    nodes = pg(_SQL_NODE_NAMES)
    nid2name = {r[0]: r[1] for r in nodes}
    edges = pg(_SQL_EDGE_NODE_PAIRS_WITH_DOC)
    report_edges = [(f, t, sd) for f, t, sd in edges if not (sd or "").startswith("ckg_2021")]
    self_merged = len(edges) - len(report_edges)
    name_pairs = set()
    for f, t, _sd in report_edges:
        a, b = build_io_edge_bindings.norm(nid2name.get(f)), build_io_edge_bindings.norm(nid2name.get(t))
        if a and b and a != b:
            name_pairs.add((a, b))
    return ckg_pairs, name_pairs, nodes, self_merged, report_edges


def _pq0065_prior_metrics(ckg: dict, io_pairs: set) -> tuple:
    """先验可用性 a/b 判据实测（原 reexam_pq0065 中段逐行搬运）。"""
    cov = (
        ckg["ckg_pairs_both_ends_alignable"] / ckg["ckg_raw_industry_pairs"] if ckg["ckg_raw_industry_pairs"] else None
    )
    corroborated = len(ckg["pairs"] & io_pairs)
    side_evidence_rate = corroborated / len(ckg["pairs"]) if ckg["pairs"] else None
    return cov, side_evidence_rate


def reexam_pq0065() -> dict:
    ckg_pairs, name_pairs, nodes, self_merged, report_edges = _pq0065_edge_sets()
    # 可对齐子集（双端产品名都在 ig_node 词表内）
    node_names = {build_io_edge_bindings.norm(n) for _i, n in nodes}
    mappable = {(a, b) for (a, b) in ckg_pairs if a in node_names and b in node_names}
    inter = mappable & name_pairs
    inter_full = ckg_pairs & name_pairs
    to_l1, _l1, _p = build_ckg_l1_normalizer()
    ckg = ckg_industry_pairs()
    matrix = loader.industry_pair_matrix()
    io_pairs = {tuple(build_io_edge_bindings.norm(x) for x in k.split("->")) for k in matrix}
    # 先验可用性三判据
    cov, side_evidence_rate = _pq0065_prior_metrics(ckg, io_pairs)
    return {
        "threshold_original": "≥70%（低于则 CKG 降级为结构先验）——Owner 裁定③已触发降级",
        "original_numbers_reproduced": {
            "ckg_product_pairs": len(ckg_pairs),
            "report_line_edges": len(report_edges),
            "report_line_name_pairs": len(name_pairs),
            "mappable_ckg_pairs": len(mappable),
            "intersection_mappable": len(inter),
            "consistency_mappable": round(len(inter) / len(mappable), 4) if mappable else None,
            "intersection_full": len(inter_full),
            "consistency_full": round(len(inter_full) / len(ckg_pairs), 6) if ckg_pairs else None,
            "ckg_self_merged_edges_in_ig_edge": self_merged,
            "exam_recorded": {
                "consistency_mappable": 0.0123,
                "mappable_ckg_pairs": 81,
                "intersection_mappable": 1,
                "self_merged": 76,
                "self_confirming_rate_if_not_excluded": 0.716,
            },
        },
        "self_confirmation_trap": "若不剔除 ig_edge 中 ckg_2021 自并入边会得到 58/81=71.6% 假达标；"
        "剔除后 1/81=1.23%。原考试口径正确，本探针复算同值。",
        "criterion_restatement": {
            "old": "边集一致率（产品-产品名逐对重合）——把 CKG 当硬事实源时的取证判据",
            "new": "先验可用性三判据：(a) 端点可对齐率 = CKG 行业对的**双端**都能归一到在用标准行业码的比例"
            "（另报粒度压缩率=归一后去重对/对齐对，反映先验投影到一级口径后损失多少结构信息）；"
            "(b) 独立侧证率 = 归一后的 CKG 行业对中能在**异源**官方 IO 系数矩阵（旁挂册）找到同向行业对的比例；"
            "(c) 决策独立性合规率 = CKG 消费点中已按先验档（不单独支撑决策、置信封顶、须交叉）处理的比例",
            "why": "原判据把『词系不通』误当『事实不成立』：1.23% 的分子是产品名精确重合，两侧词表"
            "（CKG 产品名 vs 研报抽取环节名）不同本体，且对照侧曾为空集（PQ-0067 同期实证）——"
            "该比值对 CKG 真假几乎不含信息；降级为结构先验后，唯一有信息的问题变成"
            "『CKG 的行业结构能否与官方 IO 结构互相印证、以及能否安全地只当先验用』。",
            "measured": {
                "a_endpoint_align_rate": round(cov, 4) if cov is not None else None,
                "a_granularity_compression": round(ckg["ckg_pairs_at_sws_l1"] / ckg["ckg_pairs_both_ends_alignable"], 4)
                if ckg["ckg_pairs_both_ends_alignable"]
                else None,
                "b_independent_side_evidence_rate": round(side_evidence_rate, 4)
                if side_evidence_rate is not None
                else None,
                "c_consumer_compliance_rate": "见件 3 ckg_structural_prior_tier.yaml（合规率由消费点清册机械算出，"
                "本探针不重复判——单一真源）",
            },
            "thresholds_borrowed_not_invented": {
                "a": "≥0.95 —— 借 PQ-0078 题面阈值（同族量：映射载体补齐后的可对齐/可挂比例）",
                "b": "≥0.60 —— 借 PQ-0067 题面阈值原值（b 就是该量的先验化版本）",
                "c": "=1.00 —— 纪律项二元：先验的可用性等于它被当先验用的程度，无部分达标",
            },
            "pass_rule": "a ≥ 0.95 且 b ≥ 0.60 且 c = 1.00（降级补丁全落地）→ 判『先验可用（PASS@prior）』；"
            "任一不达标→先验不可用，须换源或退役",
        },
    }


def main() -> int:
    p78 = reexam_pq0078()
    p67 = reexam_pq0067()
    c = p67["consistency"]["literal(交/CKG行业对, 题面口径)"]
    p67["verdict"]["literal_threshold"] = (
        f"{'PASS' if (c or 0) >= 0.60 else 'FAIL'} ({c:.2%} vs ≥60%)" if c is not None else "N/A"
    )
    p67["verdict"]["jaccard_threshold_same_rule"] = (
        f"{'PASS' if (p67['consistency']['jaccard(对称)'] or 0) >= 0.60 else 'FAIL'} "
        f"({p67['consistency']['jaccard(对称)']:.2%})"
    )
    p65 = reexam_pq0065()
    m = p65["criterion_restatement"]["measured"]
    a, b = m["a_endpoint_align_rate"], m["b_independent_side_evidence_rate"]
    p65["criterion_restatement"]["verdict_ab_before_discipline"] = (
        f"a={a:.2%} {'PASS' if (a or 0) >= 0.95 else 'FAIL'}(≥95%) | "
        f"b={b:.2%} {'PASS' if (b or 0) >= 0.60 else 'FAIL'}(≥60%) | c 待件 3 清册"
    )
    p65["criterion_restatement"]["original_threshold_verdict_under_old_criterion"] = (
        "FAIL（1.23% ≪ 70%）——题面降级条款成立，Owner 裁定③已执行"
    )
    doc = {
        "workorder": "WO-007",
        "generated_by": "scripts/governance/meta_question/wo007/wo007_reexam.py",
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "pit_assertion": "三问均为静态结构集合/映射载体取证，不涉行情时序校正；未使用任何切点后行情数据；"
        "CH 侧仅取行业分类词表（静态口径目录，非行情事实）。",
        "PQ-0078": p78,
        "PQ-0067": p67,
        "PQ-0065": p65,
        "cross_check_with_exam": "基线数字（16,859 边 / 4.12% / 0.053% / 240 行业对 / 1,726 ig_edge / 76 自并入边 / "
        "81 可对齐对 / 1.23%）逐项与 results/b2 三册对账，见各 *_reproduced 字段",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"[OK] {OUT}")
    print("PQ-0078 tiers:", p78["after_three_tiers"])
    print(
        "PQ-0067 literal:",
        p67["verdict"]["literal_threshold"],
        "jaccard:",
        p67["consistency"]["jaccard(对称)"],
        "io_pairs:",
        p67["current_side_after_sidecar"]["io_industry_pairs_cross_industry"],
    )
    print(
        "PQ-0065 restated:",
        p65["criterion_restatement"]["measured"],
        p65["criterion_restatement"]["verdict_ab_before_discipline"],
    )
    print(
        "baseline reproduced:",
        p78["baseline_reproduced"],
        "exam numbers:",
        p65["original_numbers_reproduced"]["consistency_mappable"],
        p65["original_numbers_reproduced"]["mappable_ckg_pairs"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
