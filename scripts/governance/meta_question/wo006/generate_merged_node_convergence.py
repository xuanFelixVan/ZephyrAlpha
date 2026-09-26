# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.generate_merged_node_convergence
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（只读探针/旁挂册 CAS 写/同口径判据）; PG ig_node/ig_node_company 只读
# [CONSUMERS] 案卷 WO-006.yaml（收敛表达裁定）；Owner 退役/净删门位决策；后续词表治理班
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 收敛=**指向式（superseded_by）+ 旁挂收敛册**，零物理删除、零 ig_node 改动、零 ig_node_company 写入；
#            指向键从节点名内嵌的 `（已并入<目标ND>-自<本节点ND>）` 机械解析（2,225/2,225 可解析，
#            目标节点 2,225/2,225 存库=可机检闭环），解析式而非人工维护；
#            tombstone 一律**禁补挂**：实测 2,225 个已并入节点与其目标 100% 同链，把目标的 symbol 抄到墓碑
#            =同链同司双行，直接污染 build_chain_exposure_matrix（role 权重累加）与链暴露去重口径；
#            本件同时把"若抄挂可达到的占比"量化登记为 rejected_alternative（假绿可审计，不藏）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达→抛出；解析失败节点数>0→仍落册并把失败清单进 meta.unparsed（禁静默丢条目）
# [TESTS] 2026-09-24 首跑：2,225 全解析/目标全存库/100% 同链（与 p5/p6 探针一致）
# [TTL] task_bound
"""WO-006 合并节点收敛册生成器——2,225 个"已并入"节点以指向式表达，零物理删除。

用法::

    python scripts/governance/meta_question/wo006/generate_merged_node_convergence.py

产出 `data/registers/metaq_node_binding/merged_node_supersede_wo006.yaml`。

为什么不建 PG 旁挂表（裁定写进册）：①depgraph_writer 角色对 public schema 无 CREATE 权
（本件 `has_schema_privilege` 实测落册，与仓内 "CREATE TABLE 需 superuser" 先例同口径）；
②为 task_bound 产物动用 superuser DDL 进共享库=权限面扩大，违反最小写面；
③指向关系已在 YAML 册内完整可机检可重放，且 `ig_node.name` 内嵌指向串本身就是库内真源——
再建表=同一事实两处真源，违反 RULE-SSOT 与全资产净零。
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wo006_common as W  # noqa: E402

REG_PATH = W.REG_DIR / "merged_node_supersede_wo006.yaml"
# 节点名内嵌指向串：…（已并入ND-<12hex>-自ND-<12hex>）
POINTER_RE = re.compile(r"^(?P<base>.*?)（已并入(?P<target>ND-[0-9a-f]{12})-自(?P<origin>ND-[0-9a-f]{12})）$")


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。本件全部只读口径查询，无运行期变长片段，
# 逐条提为模块常量；两处同文（ig_node 三元组）共用一个常量，禁在函数体内散落字面量。
_SQL_NODE_ID_CHAIN_NAME = "select node_id, chain_id, name from ig_node"
_SQL_BOUND_NODE_ID = "select node_id from ig_node_company"
_SQL_NODE_SYMBOL = "select node_id, symbol from ig_node_company"
_SQL_WRITER_PRIVILEGES = (
    "select current_user, has_schema_privilege(current_user,'public','CREATE'), "
    "has_database_privilege(current_user,'CREATE')"
)


def build(conn) -> tuple[list[dict], dict]:
    nodes = {r[0]: {"chain_id": r[1], "name": r[2]} for r in W.rows(_SQL_NODE_ID_CHAIN_NAME, conn)}
    bound: dict[str, int] = defaultdict(int)
    for (nid,) in W.rows(_SQL_BOUND_NODE_ID, conn):
        bound[nid] += 1

    rows, unparsed = [], []
    same_chain = name_consistent = target_bound = origin_self = 0
    for nid, info in sorted(nodes.items()):
        if "已并入" not in info["name"]:
            continue
        m = POINTER_RE.match(info["name"])
        if not m:
            unparsed.append(nid)
            continue
        tgt = m.group("target")
        tinfo = nodes.get(tgt)
        sc = bool(tinfo) and tinfo["chain_id"] == info["chain_id"]
        nc = bool(tinfo) and tinfo["name"] == m.group("base")
        same_chain += sc
        name_consistent += nc
        target_bound += bool(bound.get(tgt))
        origin_self += m.group("origin") == nid
        rows.append(
            {
                "tombstone_node_id": nid,
                "chain_id": info["chain_id"],
                "base_name": m.group("base"),
                "tombstone_name": info["name"],
                "superseded_by": tgt,
                "origin_ref": m.group("origin"),
                "target_name": (tinfo or {}).get("name"),
                "target_same_chain": bool(sc),
                "target_name_consistent": bool(nc),
                "target_binding_rows": int(bound.get(tgt, 0)),
                "tombstone_binding_rows": int(bound.get(nid, 0)),
                "convergence_mode": "pointer_only_no_delete",
                "evidence": f"parsed_from_ig_node.name@{W.RUN_DATE.isoformat()}",
                "rollback": "零改动可逆：删本册条目或按 superseded_by 反查即可复原，无任何 DB 侧写",
            }
        )
    stats = {
        "merged_nodes_total": sum(1 for v in nodes.values() if "已并入" in v["name"]),
        "pointer_parsed": len(rows),
        "unparsed": unparsed,
        "target_exists_in_ig_node": sum(1 for r in rows if r["target_name"]),
        "target_same_chain": same_chain,
        "target_name_consistent": name_consistent,
        "target_has_bindings": target_bound,
        "origin_ref_equals_self_node_id": origin_self,
        "tombstones_still_unbound": sum(1 for r in rows if r["tombstone_binding_rows"] == 0),
        "note": "origin_ref==self 与 target_name_consistent 是收敛册的两条自证轴："
        "前者证解析没串位，后者证'已并入'语义=同链同名去重而非跨链改嫁",
    }
    return rows, stats


def rejected_alternative(conn) -> dict:
    """量化登记"抄挂墓碑"这条被否决的路（假绿不藏：把它的收益与代价同时报出）。"""
    nodes = {r[0]: (r[1], r[2]) for r in W.rows(_SQL_NODE_ID_CHAIN_NAME, conn)}
    syms: dict[str, set[str]] = defaultdict(set)
    for nid, sym in W.rows(_SQL_NODE_SYMBOL, conn):
        syms[nid].add(sym)
    per = defaultdict(lambda: [0, 0, 0, 0])
    for nid, (cid, nm) in nodes.items():
        merged = "已并入" in nm
        per[cid][0] += 1
        if nid in syms:
            per[cid][1] += 1
        if not merged:
            per[cid][2] += 1
            if nid in syms:
                per[cid][3] += 1
    fake = {k: list(v) for k, v in per.items()}
    n_inherited = 0
    for nid, (cid, nm) in nodes.items():
        m = POINTER_RE.match(nm)
        if not m or nid in syms:
            continue
        tgt = m.group("target")
        if syms.get(tgt):
            fake[cid][1] += 1
            n_inherited += 1

    def ratio(st):
        a = d = 0
        for nodes_n, cov, _na, _ca in st.values():
            if nodes_n > 0:
                d += 1
                if cov / nodes_n >= 0.8:
                    a += 1
        return a, d, round(a / d, 4)

    a_now, den, r_now = ratio(per)
    a_fake, _, r_fake = ratio(fake)
    return {
        "option": "把目标节点的 symbol 抄挂到 2,225 个'已并入'墓碑节点（成员穿透的墓碑版）",
        "would_attach_tombstones": n_inherited,
        "ratio_all_would_become": r_fake,
        "ratio_all_now": r_now,
        "aclass_chains_now": a_now,
        "aclass_chains_under_option": a_fake,
        "denominator": den,
        "rejected_because": "①2,225 墓碑与其目标 100% 同链（实测 target_same_chain），抄挂后同一链内同一 "
        "symbol 出现两行 → build_chain_exposure_matrix 的 role 权重累加口径被双计；"
        "②抄挂是零信息增量复制（目标行早已承载该事实），只为把指标做上去=假绿；"
        "③正确表达是收敛（指向式），不是给墓碑补身份",
        "executed": False,
    }


def main(argv=None) -> int:
    argparse.ArgumentParser(description="WO-006 合并节点指向式收敛册").parse_args(argv)
    conn = W.reader()
    try:
        rows, stats = build(conn)
        alt = rejected_alternative(conn)
        try:
            ddl = W.rows(_SQL_WRITER_PRIVILEGES, conn)
        except Exception as e:  # noqa: BLE001
            ddl = [[f"ERR {e}"]]
    finally:
        conn.close()
    payload = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "generated_at": date.today().isoformat(),
            "artifact": "2,225 合并节点收敛册（指向式 superseded_by，零物理删除，可逆）",
            "why_pointer_not_delete": "工单写面强约束禁 DELETE/TRUNCATE；图数据软删除（tombstone + 指向）"
            "与知识图谱 entity resolution 的 survivorship 惯例同构："
            "稳定键 node_id 不动、被并方保留可反查、消费方按 superseded_by 归并",
            "why_no_pg_side_table": {
                "writer_role_privileges": ddl[0],
                "reason": "见模块头裁定（最小写面 + 反 RULE-SSOT 双真源 + 全资产净零）",
            },
            "stats": stats,
            "rejected_alternative": alt,
            "downstream_obligation": "消费方（链暴露矩阵/传导图谱）读取 ig_node_company 前 SHOULD join 本册，"
            "把 tombstone 归并到 superseded_by；本册是可选增强件，不做也不出错",
        },
        "columns": list(rows[0].keys()) if rows else [],
        "rows": [[r[c] for c in (rows[0].keys() if rows else [])] for r in rows],
    }
    W.write_register(REG_PATH, payload)
    print(
        f"[CONVERGE] tombstones={len(rows)} parsed={stats['pointer_parsed']} unparsed={len(stats['unparsed'])} "
        f"same_chain={stats['target_same_chain']} name_consistent={stats['target_name_consistent']} "
        f"unbound={stats['tombstones_still_unbound']}"
    )
    import json

    print("[REJECTED_ALTERNATIVE] " + json.dumps(alt, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
