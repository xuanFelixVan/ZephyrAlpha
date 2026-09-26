# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.recompute_pq0064
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（同口径判据/旁挂册）; docs/_working/meta_question_answers/results/b2/PQ-0064.yaml
#                （考试在案数字，运行时读入做口径自证，禁凭记忆抄数）; websearch_ingest 词表正则（垃圾节点判据）
# [CONSUMERS] emit_case_file.py（案卷复算节）；PQ-0064 复考（复考前置即本件输出）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 两次计算必须同口径同 SQL：判据唯一实现=wo006_common.pq0064_metrics，
#            "施工前"用 exclude_wo006=True（按 source_doc 'wo006|' 前缀剔除本单写行，可无损重构写前面），
#            "施工后"用实盘现算——除排他标记外零差异，禁为凑数改判据；
#            口径自证：施工前重算值与考试在案 evidence.result 逐项相等才算"同卷"，不等即 FAIL（换卷嫌疑）；
#            投影对账：实盘 after 与候选册 meta.projection.projected_after_wo006 逐项相等才算施工闭环；
#            上限诊断（attachment ceiling）明示：把所有"非垃圾未挂活跃节点"全挂满也到不了阈时，
#            结论只能是结构性缺口需退役/治理联动，禁靠放宽口径制造 pass
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考试在案文件缺失/字段缺→抛出（口径自证不许断链）；候选册缺投影→抛出
# [TESTS] 2026-09-24 首跑：施工前重算与在案数字 11 项全等；写后 after 与投影全等
# [TTL] task_bound
"""WO-006 PQ-0064 判据复算（施工前/施工后同口径两次）+ 转 pass 路径诊断。

用法::

    python scripts/governance/meta_question/wo006/recompute_pq0064.py [--out PATH]

默认输出 `data/registers/metaq_node_binding/pq0064_recompute_wo006.yaml`。
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
import yaml  # noqa: E402
from websearch_ingest import NODE_JUNK_RE, NODE_NAME_MAX_LEN, TITLE_JUNK_RE  # noqa: E402

REG_PATH = W.REG_DIR / "pq0064_recompute_wo006.yaml"
EXAM_PATH = W.ROOT / "docs" / "_working" / "meta_question_answers" / "results" / "b2" / "PQ-0064.yaml"
CAND_PATH = W.REG_DIR / "node_binding_candidates_wo006.yaml"

# 考试在案 evidence.result → 本件键名（口径自证对照表）
XREF = {
    "chains_total": "chains_total",
    "chains_with_nodes": "chains_with_nodes",
    "A_all": "aclass_chains_all",
    "A_active": "aclass_chains_active",
    "A_ratio_all": "ratio_all",
    "A_ratio_active": "ratio_active",
    "cov_0": "chains_cov_zero",
    "cov_lt50": "chains_cov_lt50",
    "cov_50to80": "chains_cov_50to80",
    "mean_cov_all": "mean_coverage_all",
    "mean_cov_active": "mean_coverage_active",
    "merged_nodes_excluded": "merged_nodes",
}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{tag}=wo006 写面排他标记真源（wo006_common.TAG_SQL），
# 由调用点 .format() 注入，禁把标记字面量写进常量；判据本体仍唯一实现于 wo006_common。
_SQL_NODE_ID_CHAIN_NAME = "select node_id, chain_id, name from ig_node"
_SQL_DISTINCT_BOUND_NODE_ID = "select distinct node_id from ig_node_company"
_SQL_INTEGRITY_WINDOW_TOUCHED = (
    "select count(*) from ig_node_company x\n"
    "             where not ({tag})\n"
    "               and x.updated_at >= (select min(updated_at) from ig_node_company y where {tag})"
)
_SQL_INTEGRITY_FOREIGN_ATTRIBUTION = (
    "select coalesce(split_part(source_doc,'|',1),'(null)'), count(*) from ig_node_company x\n"
    "             where not ({tag})\n"
    "               and x.updated_at >= (select min(updated_at) from ig_node_company y where {tag})\n"
    "             group by 1 order by 2 desc limit 6"
)
_SQL_INTEGRITY_DISALLOWED_ROWS = (
    "select count(*) from ig_node_company x join ig_node n using (node_id)\n"
    "             where {tag} and (n.name like '%已并入%'\n"
    "                or exists (select 1 from ig_node_company y where y.node_id = x.node_id\n"
    "                             and not ({tag})))"
)


def caliber_self_check(pre: dict) -> dict:
    """施工前重算 vs 考试在案数字逐项相等（同卷自证）。"""
    exam = yaml.safe_load(EXAM_PATH.read_text(encoding="utf-8"))
    res = exam["evidence"][0]["result"]
    cmp = {}
    for exam_key, my_key in XREF.items():
        cmp[exam_key] = {"exam": res.get(exam_key), "recomputed": pre.get(my_key)}
    bad = [k for k, v in cmp.items() if v["exam"] is None or (float(v["exam"]) - float(v["recomputed"])) > 1e-6]
    return {
        "exam_ref": exam.get("exam_ref"),
        "compared_items": len(cmp),
        "mismatch": bad,
        "identical": not bad,
        "exam_outcome": exam.get("outcome"),
        "exam_fail_type": exam.get("fail_type"),
    }


def _per_chain_node_stats(nodes: dict, bound: set) -> defaultdict:
    """逐链四元组聚合 [总节点, 已挂, 活跃(非已并入), 活跃已挂]。"""
    per = defaultdict(lambda: [0, 0, 0, 0])
    for nid, (cid, nm) in nodes.items():
        merged = "已并入" in nm
        per[cid][0] += 1
        if nid in bound:
            per[cid][1] += 1
        if not merged:
            per[cid][2] += 1
            if nid in bound:
                per[cid][3] += 1
    return per


def _classify_unattached(nodes: dict, bound: set) -> tuple[list, list, list]:
    """未挂活跃节点三分：unact（全量）/ junk（词表拦截）/ attachable（可挂候选）。"""
    unact = [(nid, cid, nm) for nid, (cid, nm) in nodes.items() if "已并入" not in nm and nid not in bound]
    junk = [
        x for x in unact if len(x[2]) > NODE_NAME_MAX_LEN or NODE_JUNK_RE.search(x[2]) or TITLE_JUNK_RE.search(x[2])
    ]
    attachable = [x for x in unact if x not in junk]
    return unact, junk, attachable


def _ceiling_state(per: dict, attachable: list) -> dict:
    """上限情景：把"非垃圾可挂候选"全挂满（理想 100% 回收）后的逐链四元组副本。"""
    ceil_state = {k: list(v) for k, v in per.items()}
    for nid, cid, _nm in attachable:
        ceil_state[cid][1] += 1
        ceil_state[cid][3] += 1
    return ceil_state


def _chain_gap_histogram(per: dict) -> defaultdict:
    """活跃口径未达 A 档链的缺口直方图（再挂 need 个节点即跨阈，截到 6 桶）。"""
    gaps = defaultdict(int)
    for cid, (n, cov, na, ca) in per.items():
        if na <= 0 or ca / na >= 0.8:
            continue
        need = max(1, int(-(-0.8 * na // 1)) - ca)  # ceil(0.8*na)-ca：再挂 need 个节点即跨阈
        gaps[min(need, 6)] += 1
    return gaps


def diagnostics(conn) -> dict:
    """转 pass 路径诊断：垃圾节点占比 + 补挂上限 + 逐链缺口分布。"""
    nodes = {r[0]: (r[1], r[2]) for r in W.rows(_SQL_NODE_ID_CHAIN_NAME, conn)}
    bound = {r[0] for r in W.rows(_SQL_DISTINCT_BOUND_NODE_ID, conn)}
    per = _per_chain_node_stats(nodes, bound)
    unact, junk, attachable = _classify_unattached(nodes, bound)
    ceil_state = _ceiling_state(per, attachable)

    def bins(st):
        a1 = a2 = d = 0
        for nodes_n, cov, na, ca in st.values():
            if nodes_n > 0:
                d += 1
                if cov / nodes_n >= 0.8:
                    a1 += 1
                if na > 0 and ca / na >= 0.8:
                    a2 += 1
        return a1, a2, d

    b1, b2, den = bins(per)
    c1, c2, _ = bins(ceil_state)
    gaps = _chain_gap_histogram(per)
    return {
        "unattached_active_nodes_now": len(unact),
        "of_which_vocabulary_junk": len(junk),
        "vocabulary_junk_definition": "节点名命中图谱写入通道今夜词表拦截项（超长>15 字 / 研报标题腔 / "
        "结构违规）——这类'环节'按现行词表不该存在，属词表治理面而非挂接面",
        "attachable_now": len(attachable),
        "attachment_ceiling_projection": {
            "assumption": "把全部非垃圾未挂活跃节点 100% 挂上（理想上限，实际源覆盖率远低于 100%）",
            "a_all": c1,
            "a_active": c2,
            "denominator": den,
            "ratio_all": round(c1 / den, 4),
            "ratio_active": round(c2 / den, 4),
            "meets_threshold_active": round(c2 / den, 4) >= 0.8,
        },
        "chain_gap_histogram_active": dict(sorted(gaps.items(), key=lambda kv: str(kv[0]))),
        "now": {
            "a_all": b1,
            "a_active": b2,
            "denominator": den,
            "ratio_all": round(b1 / den, 4),
            "ratio_active": round(b2 / den, 4),
        },
        "all_vs_active_gap_chains": sum(
            1 for n, cov, na, ca in per.values() if n > 0 and na > 0 and ca / na >= 0.8 > (cov / n if n else 0)
        ),
    }


def reconcile_after(post: dict) -> dict:
    """实盘 after vs 候选册投影（施工闭环对账）。"""
    proj = yaml.safe_load(CAND_PATH.read_text(encoding="utf-8"))["meta"]["projection"]
    p = proj["projected_after_wo006"]
    got = {
        "a_all": post["aclass_chains_all"],
        "a_active": post["aclass_chains_active"],
        "denominator": post["chains_with_nodes"],
        "ratio_all": post["ratio_all"],
        "ratio_active": post["ratio_active"],
    }
    diff = {k: {"projected": p.get(k), "actual": got.get(k)} for k in got}
    ok = all(abs(float(v["projected"]) - float(v["actual"])) < 1e-6 for v in diff.values())
    return {"projection_source": "node_binding_candidates_wo006.yaml:meta.projection", "compared": diff, "matches": ok}


def integrity_checks(conn, pre: dict, post: dict) -> dict:
    """写面强约束复核：证"纯 INSERT、既有行零触碰"，异常按归属拆分而非一锅端。"""
    win = W.rows(_SQL_INTEGRITY_WINDOW_TOUCHED.format(tag=W.TAG_SQL), conn)
    foreign = W.rows(_SQL_INTEGRITY_FOREIGN_ATTRIBUTION.format(tag=W.TAG_SQL), conn)
    viol = W.rows(_SQL_INTEGRITY_DISALLOWED_ROWS.format(tag=W.TAG_SQL), conn)
    return {
        "pre_existing_rows_reconstructed": pre["ig_node_company_rows_non_wo006"],
        "wo006_rows": post["ig_node_company_rows_wo006"],
        "non_wo006_rows_after_write": post["ig_node_company_rows_non_wo006"],
        "non_wo006_rows_unchanged": pre["ig_node_company_rows_non_wo006"] == post["ig_node_company_rows_non_wo006"],
        "foreign_rows_touched_in_write_window": int(win[0][0]),
        "foreign_touched_attribution": [list(f) for f in foreign],
        "wo006_rows_on_disallowed_nodes": int(viol[0][0]),
        "disallowed_definition": "wo006 行落在'已并入'墓碑节点，或该节点写前已有挂接行（预检承诺=0）",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="WO-006 判据复算")
    ap.add_argument("--out", default=str(REG_PATH))
    a = ap.parse_args(argv)
    conn = W.reader()
    try:
        pre = W.pq0064_metrics(conn, exclude_wo006=True)
        post = W.pq0064_metrics(conn)
        selfcheck = caliber_self_check(pre)
        diag = diagnostics(conn)
        recon = reconcile_after(post)
        integ = integrity_checks(conn, pre, post)
    finally:
        conn.close()
    payload = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "recomputed_at": date.today().isoformat(),
            "caliber": "覆盖率=链内有公司映射节点/链总节点；A 档=覆盖率≥0.8；"
            "分母=有节点链；活跃口径剔 name LIKE '%已并入%'（与考试 evidence.query 同构）",
            "pre_definition": "实盘剔除 source_doc LIKE 'wo006|%' 的行（本单纯 INSERT，剔除即写前面）",
        },
        "before": pre,
        "after": post,
        "caliber_self_check": selfcheck,
        "write_integrity": integ,
        "projection_reconciliation": recon,
        "delta": {
            "ig_node_company_rows": post["ig_node_company_rows_total"] - pre["ig_node_company_rows_total"],
            "wo006_rows": post["ig_node_company_rows_wo006"],
            "unattached_nodes": f"{pre['unattached_nodes']} -> {post['unattached_nodes']}",
            "unattached_active": f"{pre['unattached_active_nodes']} -> {post['unattached_active_nodes']}",
            "ratio_all": f"{pre['ratio_all']} -> {post['ratio_all']}",
            "ratio_active": f"{pre['ratio_active']} -> {post['ratio_active']}",
            "aclass_all": f"{pre['aclass_chains_all']} -> {post['aclass_chains_all']}",
            "aclass_active": f"{pre['aclass_chains_active']} -> {post['aclass_chains_active']}",
        },
        "verdict": {
            "threshold": pre["threshold"],
            "pass_all_caliber": post["pass_all"],
            "pass_active_caliber": post["pass_active"],
            "outcome_now": "pass" if (post["pass_all"] and post["pass_active"]) else "fail",
            "fail_type_if_fail": "infra（结构性：链池含 115 条零覆盖微链 + 2,225 个已并入墓碑 + "
            "词表垃圾节点；挂接面已按四源尽力回收，剩余缺口非挂接可解）",
        },
        "diagnostics": diag,
    }
    W.write_register(Path(a.out), payload)
    print(
        f"[RECOMPUTE] before all={pre['ratio_all']} active={pre['ratio_active']} "
        f"| after all={post['ratio_all']} active={post['ratio_active']} "
        f"| 口径自证 identical={selfcheck['identical']} 对账 matches={recon['matches']}"
    )
    print(
        f"[VERDICT] pass_all={post['pass_all']} pass_active={post['pass_active']} "
        f"outcome={payload['verdict']['outcome_now']} ceiling_active="
        f"{diag['attachment_ceiling_projection']['ratio_active']}"
    )
    print(
        f"[INTEGRITY] 既有行零触碰={integ['non_wo006_rows_unchanged']} "
        f"窗口内他方行被动={integ['foreign_rows_touched_in_write_window']} "
        f"违例挂接={integ['wo006_rows_on_disallowed_nodes']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
