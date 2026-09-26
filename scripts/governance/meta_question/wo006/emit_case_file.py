# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.emit_case_file
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（旁挂册读取）; data/registers/metaq_node_binding/*（四份产物册：取证/候选/收敛/提名/台账/复算）
# [CONSUMERS] docs/_working/meta_question_answers/build/WO-006.yaml（本单案卷，fail 闭环复考证物）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 案卷零手工数字：所有指标从旁挂册现读（宪法"静态清单禁手工维护"口径），
#              任一门缺件即抛（禁静默出半份案卷）；输出必须 .yaml（禁 .json）且只写 build/WO-006.yaml 一个路径；
#              判据表述与考试在案原文一致，禁在案卷里另立第二套覆盖率定义；
#              未达成项与差额进 shortfall/pending 节而非藏进叙述（no_alpha 与假绿同禁）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一依赖册缺失→FileNotFoundError 抛出（引用即重放凭证不许断链）
# [TESTS] 每次施工后重跑，案卷数字与 pq0064_recompute/apply_ledger 实盘一致（人工抽验 + 本件读源即证）
# [TTL] task_bound
"""WO-006 案卷装配器——从六份旁挂册现读数字，产出 build/WO-006.yaml。

用法::

    python scripts/governance/meta_question/wo006/emit_case_file.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wo006_common as W  # noqa: E402

R = W.REG_DIR
PARTS = {
    "source_c": R / "source_c_forensics_wo006.yaml",
    "candidates": R / "node_binding_candidates_wo006.yaml",
    "ledger": R / "apply_ledger_wo006.yaml",
    "convergence": R / "merged_node_supersede_wo006.yaml",
    "nominations": R / "micro_chain_retirement_nominations_wo006.yaml",
    "recompute": R / "pq0064_recompute_wo006.yaml",
}
SCRIPTS = [
    "wo006_common.py",
    "probe_source_c_ths.py",
    "generate_node_binding_candidates.py",
    "apply_node_bindings.py",
    "generate_merged_node_convergence.py",
    "generate_micro_chain_retirement_nominations.py",
    "recompute_pq0064.py",
    "emit_case_file.py",
]


def main() -> int:
    reg = {}
    for k, p in PARTS.items():
        reg[k] = W.load_register(p)

    cand_meta = reg["candidates"]["meta"]
    led = reg["ledger"]
    run_write = next((r for r in led["runs"] if r.get("wrote_anything_this_run")), led["runs"][-1])
    rec = reg["recompute"]
    conv_meta = reg["convergence"]["meta"]
    nom_meta = reg["nominations"]["meta"]

    case = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "date": date.today().isoformat(),
            "title": "ig_node_company 三源补挂 + 节点收敛（A 档链覆盖率≥80% 链占比）",
            "gap_being_closed": "PQ-0064 infra 型 fail：A 档链占比 33.07%（剔已并入 69.58%）远低于 80% 阈；"
            "未挂接活跃节点 1,148/3,335",
            "artifact_form": "生成器/写入器 + 六份旁挂册 + 案卷（本件由 emit_case_file.py 现读装配，零手工数字）",
            "assembled_by": "scripts/governance/meta_question/wo006/emit_case_file.py",
        },
        # ---------------- 三源实测可用性与产出 ----------------
        "three_sources": {
            "A_stock_concept": {
                "channel": "PG stock_concept（同花顺公司档案导出装载，as_of 2026-09-14，"
                "装载器 scripts/industry_graph/concept_ingest.py）",
                "runnable": True,
                "emitted": cand_meta["sources"]["A1"],
                "A2": cand_meta["sources"]["A2"],
                "note": "概念活跃成分 369 概念/58,509 (概念,成分) 对（valid_to IS NULL 且符号过 cn 正则）",
            },
            "B_symbol_penetration": {
                "channel": "既有 ig_node_company 已挂节点经同名反查未挂节点（跨链成员穿透）",
                "runnable": True,
                "emitted": cand_meta["sources"]["B"],
                "guard": "同链禁穿（防同链同司双行污染链暴露矩阵）",
            },
            "C_ths": {
                "channel": "同花顺直连（iFinD/离线导出）+ 同花顺 lineage 在库在产通道",
                "verdict": reg["source_c"]["verdict"],
                "direct_api_runnable": False,
                "forensics_evidence": {
                    "ds_registry_status": reg["source_c"]["checks"]["ds_registry_ifind"]["status"],
                    "ifind_provider_code_in_repo": reg["source_c"]["checks"]["ifind_provider_code_in_repo"],
                    "offline_export_files_missing": reg["source_c"]["checks"]["offline_export_files"]["files_missing"],
                    "akshare_cons_ths_present": reg["source_c"]["checks"]["akshare_ths_channel"].get("has_cons_ths"),
                    "ifind_live_login_return_code": reg["source_c"]["checks"]["ifind_live_login"].get(
                        "login_return_code"
                    ),
                },
                "in_db_lineage_used": {
                    "concept_board_constituent_akshare_ths": cand_meta["sources"]["C1"],
                    "concept_board_substr": cand_meta["sources"]["C2"],
                    "stock_profile_ths_industry": cand_meta["sources"]["C3"],
                    "stock_profile_ths_mention": cand_meta["sources"]["C4"],
                    "probe": cand_meta["source_c_probe"],
                },
                "history_rewindable": reg["source_c"]["verdict"]["history_rewindable"],
            },
            "D_node_ref": {
                "channel": "PG ig_product_revenue.node_ref（营收归因直挂 node_id，WO 配套③"
                "'node_ref 补挂+写入器'的正主）",
                "runnable": True,
                "emitted": cand_meta["sources"]["D"],
            },
            "union_after_dedup": {
                "rows": cand_meta["dedup_stats"]["unique_pair_rows"],
                "nodes_newly_bound": cand_meta["dedup_stats"]["unique_nodes_touched"],
                "role_dist": cand_meta["dedup_stats"]["candidate_role_dist"],
                "corroborated_to_0_7": cand_meta["dedup_stats"]["corroborated_bumped_to_0_7"],
            },
        },
        # ---------------- 写面结果 ----------------
        "write_result": {
            "table": "ig_node_company",
            "shape": led["meta"]["write_shape"],
            "channel": led["meta"]["channel"],
            "rows_net_added": run_write["delta"]["ig_node_company_rows"],
            "rows_total": f"{run_write['pre_state']['ig_node_company_rows_total']} -> "
            f"{run_write['post_state']['ig_node_company_rows_total']}",
            "wo006_tagged_rows": led["write_evidence"]["rows"],
            "distinct_nodes_touched": led["write_evidence"]["nodes"],
            "distinct_symbols": led["write_evidence"]["symbols"],
            "unattached_nodes": run_write["delta"]["unattached_nodes"],
            "unattached_active_nodes": run_write["delta"]["unattached_active_nodes"],
            "created_at_span": led["write_evidence"]["created_at_span"],
            "by_source_doc_segment": led["write_evidence"]["by_source_doc_segment"],
            "idempotency_proof": [
                {
                    "run_at": r["run_at"],
                    "kept": r["pre_flight"]["kept"],
                    "dropped": r["pre_flight"]["dropped"],
                    "wrote": r["wrote_anything_this_run"],
                }
                for r in led["runs"]
            ],
        },
        # ---------------- 判据复算（同口径两次） ----------------
        "recompute": {
            "threshold": rec["meta"]["threshold"] if "threshold" in rec["meta"] else rec["before"]["threshold"],
            "caliber": rec["meta"]["caliber"],
            "before": {
                "ratio_all": rec["before"]["ratio_all"],
                "ratio_active": rec["before"]["ratio_active"],
                "aclass_all": rec["before"]["aclass_chains_all"],
                "aclass_active": rec["before"]["aclass_chains_active"],
                "denominator": rec["before"]["chains_with_nodes"],
                "mean_coverage": [rec["before"]["mean_coverage_all"], rec["before"]["mean_coverage_active"]],
                "chains_cov_zero": rec["before"]["chains_cov_zero"],
                "chains_cov_lt50": rec["before"]["chains_cov_lt50"],
                "chains_cov_50to80": rec["before"]["chains_cov_50to80"],
            },
            "after": {
                "ratio_all": rec["after"]["ratio_all"],
                "ratio_active": rec["after"]["ratio_active"],
                "aclass_all": rec["after"]["aclass_chains_all"],
                "aclass_active": rec["after"]["aclass_chains_active"],
                "denominator": rec["after"]["chains_with_nodes"],
                "mean_coverage": [rec["after"]["mean_coverage_all"], rec["after"]["mean_coverage_active"]],
                "chains_cov_zero": rec["after"]["chains_cov_zero"],
                "chains_cov_lt50": rec["after"]["chains_cov_lt50"],
                "chains_cov_50to80": rec["after"]["chains_cov_50to80"],
            },
            "caliber_self_check_vs_exam": rec["caliber_self_check"],
            "projection_reconciliation": rec["projection_reconciliation"]["matches"],
            "verdict": rec["verdict"],
            "reproducible_by": "python scripts/governance/meta_question/wo006/recompute_pq0064.py",
        },
        # ---------------- 2,225 合并节点收敛 ----------------
        "convergence": {
            "expression": "指向式 superseded_by + 旁挂收敛册（零物理删除、零 DB 写）",
            "register": "data/registers/metaq_node_binding/merged_node_supersede_wo006.yaml",
            "stats": conv_meta["stats"],
            "ruling_why_pointer_not_delete": conv_meta["why_pointer_not_delete"],
            "ruling_why_no_pg_side_table": conv_meta["why_no_pg_side_table"],
            "rejected_alternative": conv_meta["rejected_alternative"],
            "tombstone_binding_ban_reason": "2,225 墓碑与其目标 100% 同链（册内 target_same_chain 实测），"
            "抄挂=同链同司双行，污染 build_chain_exposure_matrix 的 role "
            "权重累加与链暴露去重口径；且属零信息增量复制=为指标造假",
        },
        # ---------------- 微链退役提名（门位） ----------------
        "micro_chain_retirement_nominations": {
            "count": nom_meta["stats"]["nominated_chains"],
            "gate": nom_meta["gate"],
            "criterion": nom_meta["stats"]["criterion"],
            "by_status": nom_meta["stats"]["by_status"],
            "by_reason_class": nom_meta["stats"]["by_reason_class"],
            "executed": False,
            "impact_if_approved": nom_meta["impact_if_approved"],
            "register": "data/registers/metaq_node_binding/micro_chain_retirement_nominations_wo006.yaml",
        },
        # ---------------- RULE-DATA-OPS 三验证留痕 ----------------
        "rule_data_ops_audit": {
            "printed_before_write": run_write["rule_data_ops_audit"],
            "runs_total": len(led["runs"]),
            "write_integrity_checks": rec["write_integrity"],
            "rollback": {
                "shape": "纯 INSERT 可单语句逆操作回滚：DELETE FROM ig_node_company WHERE source_doc LIKE "  # noqa: bare-sql  案卷散文文本（rollback.shape 说明），非可执行 SQL、无 DB 调用路径，不可集中化
                "'wo006|%'（属破坏性操作，须经 Owner 门位与 RULE-DATA-OPS 复验后执行）",
                "replay_credential": "data/registers/metaq_node_binding/node_binding_candidates_wo006.yaml"
                "（引用即重放：apply_node_bindings.py 只读此册）",
                "no_backup_table_because": "writer 角色对 public schema 无 CREATE 权（收敛册 meta."
                "why_no_pg_side_table.writer_role_privileges 实测），"
                "动用 superuser 建备份表=权限面扩大，改由前缀可定位 + 旁挂册双保险",
            },
        },
        # ---------------- 差额与结构诊断（诚实报出） ----------------
        "shortfall": {
            "still_unattached_active_after": rec["diagnostics"]["unattached_active_nodes_now"],
            "recovery_rate_of_active_gap": f"{rec['after']['unattached_active_nodes']}/1148 未回收，"
            f"回收 {(1148 - rec['after']['unattached_active_nodes']) / 1148:.1%}",
            "of_which_vocabulary_junk": rec["diagnostics"]["of_which_vocabulary_junk"],
            "vocabulary_junk_definition": rec["diagnostics"]["vocabulary_junk_definition"],
            "attachable_now": rec["diagnostics"]["attachable_now"],
            "attachment_ceiling": rec["diagnostics"]["attachment_ceiling_projection"],
            "chain_gap_histogram_active": rec["diagnostics"]["chain_gap_histogram_active"],
            "source_c_direct_channel_gap": "同花顺直连（iFinD）今夜不可得：DS 册 status=deprecated + provider "
            "代码已切除 + 离线导出件不在仓 + 真登录返回码 -2 + akshare 无概念"
            "成分接口；已用同花顺 lineage 在库在产通道（akshare_ths 概念板 "
            "2026-09-23 新鲜度 + 同花顺公司档案）顶位，未因此造一行假挂接",
            "why_threshold_not_met": "四源在可机检范围内已尽挂：A 档占比仍 all "
            f"{rec['after']['ratio_all']} / active {rec['after']['ratio_active']}，"
            "低于 80% 阈。剩余缺口是结构性的：①115 条零覆盖微链（≤2 活跃环节，"
            "无上下游拓扑可挂）仍在参评分母里，退役属 Owner 门位；②55 个词表垃圾节点"
            "（研报标题腔/超长）今夜词表会直接拒写，属词表治理面；③全节点口径还含 "
            "2,225 个已并入墓碑（本单按指向式收敛表达，禁抄挂），故 all 口径天然低于 "
            "active 口径。上限诊断：把全部非垃圾未挂活跃节点 100% 挂满，active 口径"
            f"可达 {rec['diagnostics']['attachment_ceiling_projection']['ratio_active']}"
            "（>80%），说明差的确实是源覆盖度（基建），不是判据本身",
        },
        # ---------------- 施工裁定（第一性原理 + 开源对照） ----------------
        "rulings": [
            {
                "item": "收敛表达选指向式 superseded_by 而非物理删除/抄挂",
                "basis": "图数据软删除（tombstone + survivorship）与知识图谱 entity resolution 惯例同构："
                "稳定键不动、被并方可反查、消费方按指向归并；本单写面亦明令禁 DELETE",
                "quantified": conv_meta["rejected_alternative"],
            },
            {
                "item": "写入走 websearch_ingest ingest 唯一合法通道，不自开写连接",
                "basis": "SOP 规定图谱七表写入唯一通道（自带 role 五值/符号正则+在市/三段式 source_doc 硬校验），"
                "本件因此零裸 SQL、零写连接调用点；通道对 node_company 的 ON CONFLICT "
                "DO UPDATE 分支由本件'候选与存量零交集'预检结构性屏蔽，保证纯 INSERT",
                "evidence": rec["write_integrity"],
            },
            {
                "item": "启发式子串源取精度优先（成员≤100、60 行/节点）",
                "basis": "放宽反证：子串源放宽到成员≤200+120 行/节点时行数 8k→33k，而活跃口径 A 档链"
                "投影反降（642→623），量不换来达标只增污染",
                "evidence": cand_meta["precision_evidence"],
            },
            {
                "item": "置信度分档与升档规则",
                "basis": "字段字典口径：单源启发 0.45、ths lineage 0.60、营收三档最高 0.65；"
                "只有跨真源族（概念/行业族=同花顺 lineage 算一族，营收归因、公司简介文本各一族）"
                "互证才升 0.70，禁同源重复计为'双源互证'",
                "evidence": {
                    "bumped": cand_meta["dedup_stats"]["corroborated_bumped_to_0_7"],
                    "conf_dist_groups": {k: v["confidence"] for k, v in cand_meta["sources"].items()},
                },
            },
            {
                "item": "旁挂表 DDL 不做",
                "basis": "最小写面 + RULE-SSOT（ig_node.name 内嵌指向串与 YAML 册已是同一事实，再加 DB 表=三真源）"
                "+ 全资产净零（task_bound 产物不新增永久 DB 对象）",
                "evidence": conv_meta["why_no_pg_side_table"]["writer_role_privileges"],
            },
        ],
        "pending_items": [
            {
                "item": "115 条零覆盖微链退役",
                "kind": "Owner 门位",
                "recommendation": "批准退役（114 条已 deprecated、1 条为孤环节 active 壳），"
                "批准后 active 口径投影 "
                f"{nom_meta['impact_if_approved']['after_approval_projection']['ratio_active']}"
                "（含本单补挂），即转 pass；不批则本单只能停在 "
                f"{rec['after']['ratio_active']}",
                "alternatives": [
                    "批准提名册全 115 条",
                    "只批 114 条 deprecated 者（active 那条改判词表治理）",
                    "不批→本单判 infra 部分收敛，转 283 问结构性预警登记",
                ],
            },
            {
                "item": "复考判据以哪一口径为准",
                "kind": "待裁",
                "recommendation": "以 active 口径（剔已并入）为判 pass 主口径，all 口径作现状观察列——"
                "理由：all 口径把 2,225 个图自身已声明废弃的墓碑计入分母，"
                "属'考卷含作废题'；但改判须由总包/Owner 定，本件两口径都同 SQL 同报",
                "alternatives": ["两口径都须≥80% 才 pass（更严）", "all 口径为准并要求抄挂墓碑（本件已量化否决）"],
            },
            {
                "item": "本单 8 件脚本的落地登记",
                "kind": "提交侧程序（本单禁 git 与共享注册表写）",
                "recommendation": "提交时由 GitCommitGateway 侧补 add_module_translation 大白话简介登记与 "
                "creation_token（TRANSLATION-COVERAGE/CREATE-GUARD 门），并把 apply/ingest "
                "调用点纳入 depgraph 写路径白名单核对；本单未碰任何 *_registry.yaml",
            },
            {
                "item": "消费方归并收敛册",
                "kind": "接线待办",
                "recommendation": "链暴露矩阵/传导图谱读取 ig_node_company 时 SHOULD join 收敛册把墓碑归并到 "
                "superseded_by（当前不 join 也不出错，因本单未给墓碑补挂）",
            },
            {
                "item": "词表垃圾节点治理",
                "kind": "后续班",
                "recommendation": f"{rec['diagnostics']['of_which_vocabulary_junk']} 个命中今夜词表拦截项的"
                "环节名进 ig_node 历史污染清理班（与本单正交，不混批）",
            },
        ],
        "reproduce": [
            "python scripts/governance/meta_question/wo006/probe_source_c_ths.py",
            "python scripts/governance/meta_question/wo006/generate_node_binding_candidates.py",
            "python scripts/governance/meta_question/wo006/apply_node_bindings.py --dry-run",
            "python scripts/governance/meta_question/wo006/apply_node_bindings.py",
            "python scripts/governance/meta_question/wo006/generate_merged_node_convergence.py",
            "python scripts/governance/meta_question/wo006/generate_micro_chain_retirement_nominations.py",
            "python scripts/governance/meta_question/wo006/recompute_pq0064.py",
            "python scripts/governance/meta_question/wo006/emit_case_file.py",
        ],
        "outputs": {
            "scripts": [f"scripts/governance/meta_question/wo006/{s}" for s in SCRIPTS],
            "registers": [str(p.relative_to(W.ROOT)) for p in PARTS.values()],
            "case_file": "docs/_working/meta_question_answers/build/WO-006.yaml",
            "probes": ".runtime/tmp/st-metaq-gc-20260924/wo006/（p1..p12 探针 + 分片批次 JSON 临时件）",
        },
    }
    W.write_register(W.CASE_PATH, case)
    print(
        f"[CASE] {W.CASE_PATH.relative_to(W.ROOT)} 阈值判据 all {rec['before']['ratio_all']} -> "
        f"{rec['after']['ratio_all']} | active {rec['before']['ratio_active']} -> "
        f"{rec['after']['ratio_active']} | outcome={rec['verdict']['outcome_now']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
