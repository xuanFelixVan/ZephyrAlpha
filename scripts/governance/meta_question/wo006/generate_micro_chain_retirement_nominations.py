# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.generate_micro_chain_retirement_nominations
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（只读探针/同口径判据/旁挂册）; scripts/industry_graph/websearch_ingest.py
#                （只 import 其 TITLE_JUNK_RE/NODE_JUNK_RE/CHAIN_STRUCT_RE 词表判据，禁复制第二真源，禁改该文件）
# [CONSUMERS] Owner 退役门位决策（微链退役=注册表净删面，high tier）；案卷 WO-006.yaml
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] **只提名不执行**：本件零写库、零链状态改动，产物 status 一律 pending_owner_approval；
#            提名判据与 PQ-0064 判据同构（活跃节点数∈[1,2] 且活跃口径零覆盖），与在案 115 条一致；
#            每条必带机械理由（status/词表命中/节点名/结构违规命中），禁"看起来没用"式主观提名；
#            退役合法执行通道唯一=ingest 的 chain 记录（status=deprecated MUST 带 merged_into），
#            本件只给出候选去向（同名近似链），去向本身也归 Owner 裁定
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] websearch_ingest 词表不可导入→抛出（判据真源缺失时禁退化为本地硬编码词表）；PG 不可达→抛出
# [TESTS] 2026-09-24 首跑提名 115 条（与在案缺口数字一致）
# [TTL] task_bound
"""WO-006 零覆盖微链退役**提名**册生成器（≤2 活跃节点且活跃口径零覆盖的链）。

用法::

    python scripts/governance/meta_question/wo006/generate_micro_chain_retirement_nominations.py

产出 `data/registers/metaq_node_binding/micro_chain_retirement_nominations_wo006.yaml`。
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "industry_graph"))

import wo006_common as W  # noqa: E402

# 词表判据真源=图谱写入通道的同名正则（import 复用，禁在此复制第二套）
from websearch_ingest import CHAIN_STRUCT_RE, NODE_JUNK_RE, TITLE_JUNK_RE  # noqa: E402

REG_PATH = W.REG_DIR / "micro_chain_retirement_nominations_wo006.yaml"


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。本件只读，两条口径查询无运行期变长片段，
# 禁在函数体内散落字面量；覆盖判定与 PQ-0064 口径同构（exclude wo006 行由 wo006_common 承担）。
_SQL_CHAINS = "select chain_id, name, status, category, level, version_year from ig_chain"
_SQL_NODE_COVERAGE = (
    "select n.chain_id, n.name,\n"
    "                  exists (select 1 from ig_node_company x where x.node_id = n.node_id) as covered\n"
    "             from ig_node n"
)


def _load_chain_state(conn) -> tuple[dict, defaultdict]:
    """链册 + 逐链节点聚合（nodes/merged/covered/names/cov_a/nodes_a），与 PQ-0064 口径同构。"""
    chains = {
        r[0]: {"name": r[1], "status": r[2], "category": r[3], "level": r[4], "version_year": r[5]}
        for r in W.rows(_SQL_CHAINS, conn)
    }
    agg = defaultdict(lambda: {"nodes": 0, "merged": 0, "covered": 0, "names": [], "cov_a": 0, "nodes_a": 0})
    for cid, nm, covered in W.rows(_SQL_NODE_COVERAGE, conn):
        a = agg[cid]
        a["nodes"] += 1
        merged = "已并入" in nm
        a["merged"] += merged
        if covered:
            a["covered"] += 1
        if not merged:
            a["nodes_a"] += 1
            a["names"].append(nm)
            a["cov_a"] += covered
    return chains, agg


def _collect_reasons(a: dict, info: dict) -> tuple[list, str | None]:
    """单链机械理由逐条判定（status/词表命中/节点名/结构违规），返回 (reasons, 首个命中 reason_class)。"""
    reasons, cls = [], None
    if info.get("status") == "deprecated":
        reasons.append("链状态已是 deprecated（图谱链状态封闭枚举里的废弃态），仍留在参评分母里拉低覆盖率")
        cls = cls or "deprecated_fragment"
    junk_node = [n for n in a["names"] if NODE_JUNK_RE.search(n) or len(n) > 15]
    if junk_node:
        reasons.append(
            f"节点名命中图谱写入通道词表拦截项（研报标题腔/超长）: {junk_node}——"
            f"这类'环节名'按现行词表今夜重放会被直接拒写，属应清理的历史污染"
        )
        cls = cls or "title_junk_chain"
    if TITLE_JUNK_RE.search(info.get("name", "")) or CHAIN_STRUCT_RE.search(info.get("name", "")):
        reasons.append("链名命中词表拦截项（标题腔/结构违规），非规范产业链名")
        cls = cls or "title_junk_chain"
    if a["nodes_a"] <= 2:
        reasons.append(
            f"活跃环节仅 {a['nodes_a']} 个（不构成可传导的链结构：无上下游可扩散拓扑），"
            f"补挂也无法达到 80% 覆盖判据所需的环节基数"
        )
        cls = cls or "unfixable_micro_chain"
    if a["merged"] and a["covered"] == 0:
        reasons.append(f"含 {a['merged']} 个'已并入'墓碑环节（收敛归并在案），链本体已无独立信息增量")
    return reasons, cls


def _build_nomination_row(cid, a: dict, info: dict, by_name: defaultdict) -> dict:
    """单条提名行：机械理由 + 同名双生链去向候选（只提名，执行归 Owner）。"""
    reasons, cls = _collect_reasons(a, info)
    # 退役去向候选：同名链（碎片重复）或同 category 活跃链兜底
    twins = [c for c in by_name.get(info.get("name", ""), []) if c != cid]
    sug = {
        "merged_into_candidates": twins[:3],
        "fallback": "无同名双生链时按 SOP 链废弃动作转 deprecated（去向归 Owner 裁）",
    }
    return {
        "chain_id": cid,
        "chain_name": info.get("name"),
        "status": info.get("status"),
        "category": info.get("category"),
        "level": info.get("level"),
        "version_year": info.get("version_year"),
        "nodes_total": a["nodes"],
        "nodes_active": a["nodes_a"],
        "active_node_names": a["names"],
        "tombstone_nodes": a["merged"],
        "coverage_all": round(a["covered"] / a["nodes"], 4) if a["nodes"] else None,
        "coverage_active": 0.0,
        "reason_class": cls or "zero_coverage_micro",
        "reasons": reasons,
        "suggested_disposition": sug,
        "execution_route": "scripts/industry_graph/websearch_ingest.py ingest 的 chain 记录"
        "（status=deprecated MUST 带 merged_into）——本件不执行",
        "approval": "pending_owner_approval",
    }


def build(conn) -> tuple[list[dict], dict]:
    chains, agg = _load_chain_state(conn)
    micro = [c for c, a in agg.items() if 0 < a["nodes_a"] <= 2 and a["cov_a"] == 0]
    by_name = defaultdict(list)
    for c, info in chains.items():
        by_name[info["name"]].append(c)

    rows = []
    for cid in sorted(micro):
        rows.append(_build_nomination_row(cid, agg[cid], chains.get(cid, {}), by_name))
    stats = {
        "nominated_chains": len(rows),
        "by_status": {s: sum(1 for r in rows if r["status"] == s) for s in {r["status"] for r in rows}},
        "by_reason_class": {
            c: sum(1 for r in rows if r["reason_class"] == c) for c in {r["reason_class"] for r in rows}
        },
        "with_twin_chain": sum(1 for r in rows if r["suggested_disposition"]["merged_into_candidates"]),
        "criterion": "活跃节点数∈[1,2] 且活跃口径覆盖=0（与 PQ-0064 判据同构，与在案 115 条一致）",
    }
    return rows, stats


def impact_if_approved(conn, nominated: set[str]) -> dict:
    """批准退役后的同口径投影（只读推算，不代表已发生）。"""
    st = W.per_chain_state(conn)
    keep = {k: v for k, v in st.items() if k not in nominated}

    def bins(state):
        a1 = a2 = d = 0
        for nodes, cov, na, ca in state.values():
            if nodes > 0:
                d += 1
                if cov / nodes >= 0.8:
                    a1 += 1
                if na > 0 and ca / na >= 0.8:
                    a2 += 1
        return a1, a2, d

    a1, a2, d = bins(keep)
    b1, b2, d0 = bins(st)
    return {
        "note": "纯投影：以当前实盘（含 wo006 补挂）为基线，把提名链从参评分母剔除后的同口径复算",
        "before_approval": {
            "a_all": b1,
            "a_active": b2,
            "denominator": d0,
            "ratio_all": round(b1 / d0, 4),
            "ratio_active": round(b2 / d0, 4),
        },
        "after_approval_projection": {
            "a_all": a1,
            "a_active": a2,
            "denominator": d,
            "ratio_all": round(a1 / d, 4),
            "ratio_active": round(a2 / d, 4),
        },
        "threshold": "A 档链占比≥80%",
        "would_pass_active": round(a2 / d, 4) >= 0.8,
        "would_pass_all": round(a1 / d, 4) >= 0.8,
    }


def main(argv=None) -> int:
    argparse.ArgumentParser(description="WO-006 微链退役提名册（只提名）").parse_args(argv)
    conn = W.reader()
    try:
        rows, stats = build(conn)
        imp = impact_if_approved(conn, {r["chain_id"] for r in rows})
    finally:
        conn.close()
    payload = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "generated_at": date.today().isoformat(),
            "artifact": "零覆盖微链退役提名册（WO-006 配套⑤，门位=Owner，本件只提名不执行）",
            "gate": "micro_chain_retirement = pending_owner_approval（注册表净删面属 high tier 人门位）",
            "stats": stats,
            "impact_if_approved": imp,
        },
        "columns": list(rows[0].keys()) if rows else [],
        "rows": [[r[c] for c in (rows[0].keys() if rows else [])] for r in rows],
    }
    W.write_register(REG_PATH, payload)
    print(
        f"[NOMINATE] chains={stats['nominated_chains']} by_status={stats['by_status']} "
        f"by_class={stats['by_reason_class']} twins={stats['with_twin_chain']}"
    )
    import json

    print("[IMPACT_IF_APPROVED] " + json.dumps(imp, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
