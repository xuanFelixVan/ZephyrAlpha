# [BLUEPRINT] GREATWALL-20260909-S6S7-NODES | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.fix_s6_s7_nodes
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 长城任务 Phase3 S6 tier 方案落地 + S7 后缀名剥离; 引擎 S6/S7/S8/S9 对账
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(节点零 DELETE,合并失败者改墓碑名"（已并入ND-xxx）"保留行); 幂等(tier 仅 unspecified 行触发; 剥离仅后缀名触发,墓碑名不再命中后缀正则); S6 按 Owner 预审 r1_tier_plan.md 落地(v0.4 映射: 设备->生产设备/材料->生产原料,位置归上游); S7 剥离撞名组保留落位最多者,落位重挂(UNIQUE 冲突则 PIT 关闭),边重挂(冲突则留在墓碑); 306 待Owner处置节点出清单进 S6 豁免
# [MODIFY-GUARD] graph_quality_standard.md(S6/S7/S8 修复方案真源)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 方案文件缺失->exit 2
# [TESTS] 2026-09-09 首跑: tier-plan 380落地+306豁免; strip 686保留+2225墓碑; dedupe 2225; 引擎 S6/S7/S9 清零
# [TTL] permanent
"""S6 tier 方案落地 + S7 后缀名剥离合并治理脚本。

子命令::

    tier-plan      r1_tier_plan.md 380 条判定落地（v0.4 映射）+ 306 待Owner 豁免清单
    strip-names    全库 -tier 后缀节点名剥离 + 同链撞名合并（墓碑保留）

墓碑约定：合并失败节点改名 "<base>（已并入ND-xxxxxxxxxxxx）"——不再命中 S7 后缀正则、
S9 不撞名；引擎 S8 对墓碑名豁免（无内容残留的历史行）。
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

NA = Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph" / "night_audit"
TODAY = date.today().isoformat()
SUFFIX_RE = re.compile(r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$")
# v0.4 职能映射（与 migrate_tier_to_function_role 同表）
SUFFIX_FUNC = {"设备": "生产设备", "材料": "生产原料", "原材料": "生产原料", "辅材": "辅助材料", "零部件": "产品业务"}
TIER_PLAN_TIER = {"上游": "上游", "中游": "中游", "下游": "下游", "设备": "上游", "材料": "上游"}
TIER_PLAN_FUNC = {"设备": "生产设备", "材料": "生产原料"}


def cmd_tier_plan() -> int:
    text = (NA / "r1_tier_plan.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (ND-[0-9a-f]{12}) \| .+? \| .+? \| (上游|中游|下游|设备|材料|待Owner处置) \|", text, re.M)
    applied, pending_owner = [], []
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    for nid, tier in rows:
        if tier == "待Owner处置":
            pending_owner.append(nid)
            continue
        pos, func = TIER_PLAN_TIER[tier], TIER_PLAN_FUNC.get(tier)
        cur.execute(
            """UPDATE ig_node SET tier=%s, function_role=COALESCE(%s, function_role), updated_at=now()
               WHERE node_id=%s AND tier='unspecified'""",
            (pos, func, nid),
        )
        if cur.rowcount:
            applied.append(nid)
    conn.commit()
    conn.close()
    # 306 待Owner 豁免登记（S6）
    if pending_owner:
        from pathlib import Path as P
        ex = P(__file__).resolve().parent / "quality_exemptions.yaml"
        t = ex.read_text(encoding="utf-8")
        block = "S6: [" + ", ".join(f'"{n}"' for n in pending_owner) + "]"
        t = t.replace("S6: []", block)
        ex.write_text(t, encoding="utf-8")
        rq = NA / "open_questions_20260909.md"
        with open(rq, "a", encoding="utf-8") as f:
            f.write(f"\n## S6 待Owner处置 306 条 unspecified 节点（2026-09-09 长城任务登记）\n\n"
                    f"来源 r1_tier_plan.md 判定=待Owner处置（研报标题残留/图解标题/名称损坏/领域级大主题，非环节功能名，不硬猜 tier）。\n"
                    f"已按 graph_quality_standard S6 豁免登记（node_id 见 quality_exemptions.yaml S6 段）。\n"
                    f"处置选项：重命名/重抽取/随所在链废弃。共 {len(pending_owner)} 条。\n")
    print(json.dumps({"applied": len(applied), "pending_owner_exempted": len(pending_owner),
                      "plan_rows": len(rows)}, ensure_ascii=False))
    return 0


def cmd_strip_names() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute("SELECT node_id, chain_id, name, tier FROM ig_node")
    nodes = cur.fetchall()
    groups: dict[tuple, list] = {}
    for nid, cid, name, tier in nodes:
        m = SUFFIX_RE.search(name)
        base = SUFFIX_RE.sub("", name) if m else name
        groups.setdefault((cid, base), []).append({"id": nid, "name": name, "tier": tier, "suffix": m.group(1) if m else None})

    renamed, repointed_nc, closed_nc, repointed_edge, tombstones = 0, 0, 0, 0, 0
    for (cid, base), members in groups.items():
        suffix_nodes = [m for m in members if m["suffix"]]
        if not suffix_nodes:
            continue
        if len(members) == 1:
            m = members[0]
            _apply_strip(cur, m, base)
            renamed += 1
            continue
        # 撞名组：保留落位最多者
        cur.execute(
            """SELECT node_id, count(*) c FROM ig_node_company
               WHERE valid_to IS NULL AND node_id = ANY(%s) GROUP BY node_id ORDER BY c DESC""",
            ([m["id"] for m in members],),
        )
        cnt = {r[0]: r[1] for r in cur.fetchall()}
        keeper = max(members, key=lambda m: (cnt.get(m["id"], 0), [-ord(ch) for ch in m["id"]]))
        for m in members:
            if m["id"] == keeper["id"]:
                continue
            # 落位重挂
            cur.execute(
                """SELECT id, symbol FROM ig_node_company
                   WHERE node_id=%s AND valid_to IS NULL""", (m["id"],),
            )
            for rid, sym in cur.fetchall():
                cur.execute("SELECT 1 FROM ig_node_company WHERE node_id=%s AND symbol=%s AND valid_to IS NULL", (keeper["id"], sym))
                if cur.fetchone():
                    cur.execute(
                        """UPDATE ig_node_company SET valid_to=%s,
                             source_doc=COALESCE(source_doc,'')||' | quality_fix|p1_s7_merge|""" + TODAY + """',
                             updated_at=now() WHERE id=%s""",
                        (TODAY, rid),
                    )
                    closed_nc += 1
                else:
                    cur.execute("UPDATE ig_node_company SET node_id=%s, updated_at=now() WHERE id=%s", (keeper["id"], rid))
                    repointed_nc += 1
            # 边重挂：直接改端点，UNIQUE 冲突则跳过该边（留墓碑）
            for col in ("from_node", "to_node"):
                cur.execute(f"SELECT edge_id, from_node, to_node, edge_type FROM ig_edge WHERE {col}=%s", (m["id"],))
                for eid, fn, tn, et in cur.fetchall():
                    nfn, ntn = (keeper["id"], tn) if col == "from_node" else (fn, keeper["id"])
                    cur.execute("SELECT 1 FROM ig_edge WHERE from_node=%s AND to_node=%s AND edge_type=%s", (nfn, ntn, et))
                    if cur.fetchone():
                        continue
                    cur.execute(f"UPDATE ig_edge SET {col}=%s WHERE edge_id=%s", (keeper["id"], eid))
                    repointed_edge += 1
            # 墓碑改名（含自身 id 保证同组多墓碑互不撞名）
            cur.execute(
                "UPDATE ig_node SET name=%s, updated_at=now() WHERE node_id=%s",
                (f"{base}（已并入{keeper['id']}-自{m['id']}）", m["id"]),
            )
            tombstones += 1
        _apply_strip(cur, keeper, base)
        renamed += 1
    conn.commit()

    cur.execute("SELECT count(*) FROM ig_node WHERE name ~ %s", (r"-(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified)$",))
    remaining = cur.fetchone()[0]
    conn.close()
    print(json.dumps({"renamed_keepers": renamed, "repointed_placements": repointed_nc,
                      "closed_dup_placements": closed_nc, "repointed_edges": repointed_edge,
                      "tombstones": tombstones, "suffix_remaining": remaining}, ensure_ascii=False))
    return 0


def _apply_strip(cur, m: dict, base: str) -> None:
    sets, params = ["name=%s", "updated_at=now()"], [base]
    if m["suffix"] in ("上游", "中游", "下游"):
        sets.append("tier=%s")
        params.append(m["suffix"])
    elif m["suffix"] in SUFFIX_FUNC:
        sets.append("function_role=COALESCE(function_role,%s)")
        params.append(SUFFIX_FUNC[m["suffix"]])
    params.append(m["id"])
    cur.execute(f"UPDATE ig_node SET {', '.join(sets)} WHERE node_id=%s", params)


def cmd_dedupe_tombstones() -> int:
    """历史墓碑名补自身 id 去重（修 2026-09-09 首轮墓碑同名缺陷，幂等）。"""
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute("SELECT node_id, name FROM ig_node WHERE name LIKE '%（已并入%'")
    rows = cur.fetchall()
    fixed = 0
    for nid, name in rows:
        if f"-自{nid}）" in name:
            continue
        new_name = name[:-1] + f"-自{nid}）" if name.endswith("）") else name + f"-自{nid}"
        cur.execute("UPDATE ig_node SET name=%s, updated_at=now() WHERE node_id=%s", (new_name, nid))
        fixed += cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"tombstones": len(rows), "fixed": fixed}, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["tier-plan", "strip-names", "dedupe-tombstones"])
    args = ap.parse_args()
    try:
        if args.cmd == "tier-plan":
            return cmd_tier_plan()
        if args.cmd == "strip-names":
            return cmd_strip_names()
        return cmd_dedupe_tombstones()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        return 2


if __name__ == "__main__":
    import argparse

    sys.exit(main())
