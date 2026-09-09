# [MODULE] scripts.industry_graph.quality_closeout_governance
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); yaml
# [CONSUMERS] SOP industry_chain_data_audit_sop §12 质量循环(存量治理走专项治理脚本通道); 收尾任务 closeout-20260909-ig-quality
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(零 DELETE,幂等 UPDATE+ON CONFLICT DO NOTHING); 治理范围=活跃链(废弃链节点=历史快照不审); 墓碑随并(墓碑节点 tier/function_role 跟随合并目标); 拓扑定级(邻接原材料/零部件类环节的上游侧=上游,终端应用侧=下游,其余=中游); 孤岛缝边(source_doc 首段='治理缝边'); 孤岛砖判定 brick_noalpha 写 description 判据; ig_chain.level 根链=1/子链=父+1(幂等回填+孤儿/环保护); 豁免台账自愈(S6 只留真实缺口节点)
# [MODIFY-GUARD] graph_quality_standard.md(判定真源); quality_exemptions.yaml(本脚本自愈改写)
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->退出码 2; 幂等复跑->输出 counts 全为 0 变更+exit 0
# [TTL] permanent
"""产业链图谱质量收尾治理脚本（Owner 2026-09-09 五项裁定落地，closeout-20260909-ig-quality）。

施工项（幂等，可重跑）：
  A. 孤岛缝边回接（2 条）：铝基复合材料←铝产业链·铝加工；纳米纤维材料←高性能纤维产业链·七大纤维节点
     ——structure 缝边 + drill_status=brick_noalpha + description 判据依据（判据B：下钻无 A 股标的）。
  B. 墓碑随并定级：活跃链 116 条墓碑节点（"（已并入ND-xxx-自ND-yyy）"）跟随合并目标 tier/function_role。
  C. 拓扑定级：链自指节点(9 组中的 3 个)→上游·技术服务；内容主题链节点(6 个)→中游·(技术服务|产品业务)。
  D. ig_chain.level 全量回填：根链=1，子链经 node.child_chain_id 递归=父+1；孤儿/环→NULL+登记。
  E. 豁免台账自愈：S6 仅保留治理后仍属真实缺口的节点（非产业概念单节点链 25 条）。

用法::
    python scripts/industry_graph/quality_closeout_governance.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

TOMBSTONE_RE = re.compile(r"（已并入(ND-[0-9a-f]{12})-自ND-[0-9a-f]{12}）")
BATCH_TAG = "closeout-20260909-ig-quality"
TODAY = date.today().isoformat()
SEAM_SOURCE_DOC = f"治理缝边|{BATCH_TAG}|{TODAY}"

# 孤岛缝边方案（Owner 2026-09-09 指令落地，方向与判据见各节点 description）
ISLAND_FIXES = [
    {
        "node_id": "ND-7c110252f154",  # 铝基复合材料 @铝基复合材料产业链
        "from_node": "ND-c9a3848afe3a",  # 铝产业链·铝加工（中游，产线相邻）
        "tier": "上游",
        "function_role": "生产原料",
        "description": (
            "铝基复合材料：以铝为基体、颗粒/纤维增强的复合材料环节。判据B（brick_noalpha）："
            "下钻无新增 A 股标的（增强铝基复合材料无 A 股专门供应商，相关公司已落位铝产业链·铝加工等母链环节），"
            "Owner 2026-09-09 收尾裁定；不做公司落位（产业概念节点）。"
        ),
        "seam_note": "流程相邻缝边：铝加工→铝基复合材料（制造→材料产品）",
    },
    {
        "node_id": "ND-672d510a89ae",  # 纳米纤维材料行业 @纳米纤维材料行业
        "from_node": "ND-e649277e8da0",  # 高性能纤维产业链·芳纶等七大高性能纤维（类属父节点）
        "tier": "上游",
        "function_role": "生产原料",
        "description": (
            "纳米纤维材料：静电纺纳米纤维及制品环节，属高性能纤维家族细分品类。判据B（brick_noalpha）："
            "下钻无新增 A 股标的（纳米纤维量产主体为非上市公司，关联在市公司已由高性能纤维链落位），"
            "Owner 2026-09-09 收尾裁定；不做公司落位（产业概念节点）。"
        ),
        "seam_note": "类属细分缝边：七大高性能纤维→纳米纤维材料（类→细分回接）",
    },
]

# 内容主题链节点定级（拓扑定级规则的落地个案：全链等位无流程结构，主题分析链取中性位置）
# 规则: 链自指节点(节点名==链名)→上游·技术服务; 主题节点(名≠链名)→中游·(ncc>0→技术服务,否则产品业务)
# 例外: AI制药产业链的主题节点跟随本链真实环节位(上游,与链内其他环节同位)
TOPIC_OVERRIDES = {
    "ND-5fb013054443": ("上游", "技术服务"),  # 从数据、算力、模型切入的3类龙头，看全球AI制药 @AI制药产业链
}


def _q(cur, sql: str, args=()):
    cur.execute(sql, args)
    return cur.fetchall()


def _fix_islands(cur, dry: bool) -> dict:
    out = {"tier_updated": 0, "edges_inserted": 0, "skipped_exists": 0}
    for fix in ISLAND_FIXES:
        nid = fix["node_id"]
        if not dry:
            cur.execute(
                """UPDATE ig_node SET tier=%s, function_role=%s, description=%s,
                   drill_status='brick_noalpha', updated_at=now()
                   WHERE node_id=%s AND (tier='unspecified' OR description IS NULL OR description NOT LIKE '%%判据B%%')""",
                (fix["tier"], fix["function_role"], fix["description"], nid),
            )
            out["tier_updated"] += cur.rowcount
            cur.execute(
                """INSERT INTO ig_edge (from_node, to_node, edge_type, source_doc, market)
                   VALUES (%s, %s, 'structure', %s, 'cn')
                   ON CONFLICT (from_node, to_node, edge_type) DO NOTHING""",
                (fix["from_node"], nid, f"{SEAM_SOURCE_DOC} #{fix['seam_note']}"),
            )
            out["edges_inserted"] += cur.rowcount
        else:
            out["tier_updated"] += 1
    return out


def _fix_tombstones(cur, dry: bool) -> dict:
    """活跃链墓碑节点: tier/function_role 跟随合并目标（目标=真实节点,已定级）。"""
    rows = _q(cur, """SELECT n.node_id, n.name FROM ig_node n JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE n.tier='unspecified' AND (c.status IS NULL OR c.status='active') AND n.name LIKE '%%（已并入%%'""")
    updated = 0
    skipped = 0
    for nid, name in rows:
        m = TOMBSTONE_RE.search(name)
        if not m:
            skipped += 1
            continue
        tgt = m.group(1)
        if not dry:
            cur.execute(
                """UPDATE ig_node t SET tier=p.tier,
                     function_role=(SELECT function_role FROM ig_node WHERE node_id=%s),
                     updated_at=now()
                   FROM (SELECT tier FROM ig_node WHERE node_id=%s) p
                   WHERE t.node_id=%s AND t.tier='unspecified'""",
                (tgt, tgt, nid),
            )
            updated += cur.rowcount
        else:
            updated += 1
    return {"tombstone_total": len(rows), "updated": updated, "skipped_no_target": skipped}


def _fix_topic_nodes(cur, dry: bool) -> dict:
    """链自指节点→上游·技术服务; 主题节点→中游·(技术服务|产品业务); TOPIC_OVERRIDES 个案优先。"""
    rows = _q(cur, """SELECT n.node_id, n.name, c.name AS chain_name,
        (SELECT count(*) FROM ig_node_company nc WHERE nc.node_id=n.node_id AND nc.valid_to IS NULL) AS ncc
        FROM ig_node n JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE n.tier='unspecified' AND (c.status IS NULL OR c.status='active')
          AND n.name NOT LIKE '%%（已并入%%'
          AND EXISTS (SELECT 1 FROM ig_edge e WHERE e.from_node=n.node_id OR e.to_node=n.node_id)""")
    updated = 0
    plan = []
    for nid, name, chain_name, ncc in rows:
        if nid in TOPIC_OVERRIDES:
            tier, fr = TOPIC_OVERRIDES[nid]
        elif name == chain_name:
            tier, fr = "上游", "技术服务"  # 链自指=链主题分析节点
        else:
            tier = "中游"
            fr = "技术服务" if ncc > 0 else "产品业务"
        plan.append({"node_id": nid, "tier": tier, "function_role": fr})
        if not dry:
            cur.execute(
                """UPDATE ig_node SET tier=%s, function_role=%s, updated_at=now()
                   WHERE node_id=%s AND tier='unspecified'""",
                (tier, fr, nid),
            )
            updated += cur.rowcount
        else:
            updated += 1
    return {"total": len(rows), "updated": updated, "plan": plan}


def _backfill_levels(cur, dry: bool) -> dict:
    """ig_chain.level 回填: 根链(无任何 node.child_chain_id 指向)=1, 子链=父+1; 孤儿/环登记。
    附一致性抽查: 统计存量 level 与挂接树深度不一致的链数(mismatched),回填后应为 0。
    """
    chains = {r[0] for r in _q(cur, "SELECT chain_id FROM ig_chain")}
    parent_of: dict[str, str] = {}
    conflicts: list[str] = []
    for child, parent in _q(cur, "SELECT child_chain_id, chain_id FROM ig_node WHERE child_chain_id IS NOT NULL"):
        if child in parent_of and parent_of[child] != parent:
            parent_of[child] = parent  # 同一环节只挂一条子链为设计契约;多挂时取后值并留痕
            conflicts.append(child)
        else:
            parent_of[child] = parent
    roots = [c for c in chains if c not in parent_of]
    level: dict[str, int] = {c: 1 for c in roots}
    frontier = list(roots)
    while frontier:
        nxt = []
        for p in frontier:
            for child, par in parent_of.items():
                if par == p and child not in level:
                    level[child] = level[p] + 1
                    nxt.append(child)
        frontier = nxt
    orphans = sorted(c for c in chains if c not in level)  # 环或父链缺失
    stored = dict(_q(cur, "SELECT chain_id, level FROM ig_chain"))
    mismatched = sorted(c for c in chains if c not in orphans and stored.get(c) != level[c])
    if not dry:
        for cid, lv in level.items():
            cur.execute("UPDATE ig_chain SET level=%s WHERE chain_id=%s AND (level IS DISTINCT FROM %s)", (lv, cid, lv))
        for cid in orphans:
            cur.execute("UPDATE ig_chain SET level=NULL WHERE chain_id=%s AND level IS NOT NULL", (cid,))
    dist: dict[str, int] = {}
    for lv in level.values():
        dist[str(lv)] = dist.get(str(lv), 0) + 1
    return {"chains_total": len(chains), "roots": len(roots), "leveled": len(level),
            "orphans": orphans, "level_dist": dist, "mismatched_before": mismatched,
            "multi_parent_conflicts": sorted(set(conflicts))}


def _selfheal_exemptions(cur, dry: bool) -> dict:
    """S6 豁免自愈: 只留治理后仍属真实缺口的活跃链 unspecified 节点。"""
    rows = _q(cur, """SELECT n.node_id FROM ig_node n JOIN ig_chain c ON n.chain_id=c.chain_id
        WHERE n.tier='unspecified' AND (c.status IS NULL OR c.status='active')
        ORDER BY n.node_id""")
    remaining = [r[0] for r in rows]
    if dry:
        return {"remaining": len(remaining)}
    yaml_path = Path(__file__).resolve().parent / "quality_exemptions.yaml"
    import yaml

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    old6 = list(data.get("S6") or [])
    data["S6"] = remaining
    text = yaml_path.read_text(encoding="utf-8")
    # 幂等改写: 仅替换 S6 行(值列表), 保留文件其余原样
    import re as _re

    new_line = "S6: [" + ", ".join(f'"{x}"' for x in remaining) + "]"
    text2, n = _re.subn(r"^S6: \[.*\]", new_line.replace("\\", "\\\\"), text, count=1, flags=_re.M)
    assert n == 1, "S6 line not found in exemptions yaml"
    yaml_path.write_text(text2, encoding="utf-8")
    chk = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert len(chk["S6"]) == len(remaining)
    return {"remaining": len(remaining), "dropped": len(old6) - len(remaining)}


def main() -> int:
    ap = argparse.ArgumentParser(description="图谱质量收尾治理(幂等)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    try:
        conn = get_depgraph_pg_connection(read_only=False)
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] PG 不可达: {e}")
        return 2
    cur = conn.cursor()
    summary: dict = {"batch": BATCH_TAG, "dry_run": args.dry_run, "date": TODAY}
    summary["islands"] = _fix_islands(cur, args.dry_run)
    summary["tombstones"] = _fix_tombstones(cur, args.dry_run)
    summary["topic_nodes"] = _fix_topic_nodes(cur, args.dry_run)
    summary["levels"] = _backfill_levels(cur, args.dry_run)
    conn.commit()
    summary["exemptions"] = _selfheal_exemptions(cur, args.dry_run)
    conn.close()
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
