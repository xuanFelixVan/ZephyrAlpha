# [BLUEPRINT] GREATWALL-20260909-P0-FIX | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.quality_fix_p0
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 长城任务 Phase2 P0 污染源清除(SOP §12.3 优先级1); 引擎 graph_quality_check S4/S14/S15/S16 对账
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删: 修复一律 PIT 关闭(valid_to=修复日)+source_doc 追加留痕(quality_fix|批次|日期),零物理 DELETE; 幂等(仅 valid_to IS NULL 行受影响,复跑零变更); S14 甄别保留规则=role 龙头核心 ∪ websearch 三段式来源 ∪ 链 category=公司行业锚点 category ∪ 链名含锚点行业词干 ∪ 000591 Owner 裁定关键词(光伏/太阳能/发电/电站/新能源/电力); --apply 才落库
# [MODIFY-GUARD] graph_quality_standard.md(S14/S15/S16/S4 修复方案真源)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2
# [TESTS] 2026-09-09 首跑: s15=1874/s4=129/s16=105/s14 甄别关闭1898+豁免1; 引擎 S4/S14/S15/S16 清零
"""Phase2 P0 污染源清除治理脚本（SOP §12.3 优先级1，SOP v1.5.0）。

子命令（全部幂等，PIT 关闭=唯一处置，零物理 DELETE）::

    s15-selfloops            自环边全量 PIT 关闭(from_symbol=to_symbol)
    s16-bidir                事故性双向边：保留证据强者(evidence_type>weight>edge_id)，弱者关闭
    s4-residue               废弃链上的落位残留全量 PIT 关闭
    s14-triage [--apply]     挂链>20 甄别：按保留规则出清单，--apply 才落库

修复批次留痕：source_doc 追加 ' | quality_fix|p0_<批次>|YYYY-MM-DD'（不覆盖原值）。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

TODAY = date.today().isoformat()
# 000591.SZ 业务范围（Owner 2026-09-09 指令书裁定：光伏真实、其余污染）
SYM000591_KW = "(光伏|太阳能|发电|电站|新能源|电力|节能)"


def fix_s15_selfloops() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """UPDATE ig_company_edge SET valid_to=%s,
             source_doc = COALESCE(source_doc,'') || ' | quality_fix|p0_s15_selfloop|""" + TODAY + """'
           WHERE from_symbol=to_symbol AND from_symbol<>'' AND valid_to IS NULL""",
        (TODAY,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s15_selfloops", "closed": n}, ensure_ascii=False))
    return 0


def fix_s4_residue() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """UPDATE ig_node_company nc SET valid_to=%s,
             source_doc = COALESCE(nc.source_doc,'') || ' | quality_fix|p0_s4_residue|""" + TODAY + """',
             updated_at = now()
           FROM ig_node n JOIN ig_chain c ON n.chain_id=c.chain_id
           WHERE nc.node_id=n.node_id AND c.status='deprecated' AND nc.valid_to IS NULL""",
        (TODAY,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s4_residue", "closed": n}, ensure_ascii=False))
    return 0


def fix_s16_bidir() -> int:
    """双向边对：保留证据强者，弱者 PIT 关闭。

    强者排序：evidence_type('disclosed'>'inferred'/'estimated'>NULL) > weight 非空且大 > edge_id 小(先入为主)。
    幂等：valid_to IS NULL 的行才参与配对与关闭。
    """
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """SELECT a.edge_id FROM ig_company_edge a
           JOIN ig_company_edge b
             ON b.from_symbol=a.to_symbol AND b.to_symbol=a.from_symbol AND b.year=a.year
            AND a.valid_to IS NULL AND b.valid_to IS NULL
           WHERE a.edge_id < b.edge_id
           ORDER BY a.edge_id"""
    )
    pairs = [r[0] for r in cur.fetchall()]
    if not pairs:
        conn.close()
        print(json.dumps({"fix": "s16_bidir", "pairs": 0, "closed": 0}, ensure_ascii=False))
        return 0
    closed = []
    for a_id in pairs:
        # 取该对两条边（仅未关闭行）
        cur.execute(
            """SELECT edge_id,
                      CASE evidence_type WHEN 'disclosed' THEN 3 WHEN 'inferred' THEN 2 WHEN 'estimated' THEN 1 ELSE 0 END ev,
                      COALESCE(weight, -1) w, edge_id tie
               FROM ig_company_edge
               WHERE ((edge_id=%s) OR (edge_id IN (
                   SELECT b.edge_id FROM ig_company_edge a
                   JOIN ig_company_edge b
                     ON b.from_symbol=a.to_symbol AND b.to_symbol=a.from_symbol AND b.year=a.year
                   WHERE a.edge_id=%s AND a.valid_to IS NULL AND b.valid_to IS NULL)))
                 AND valid_to IS NULL
               ORDER BY ev DESC, w DESC, tie ASC LIMIT 2""",
            (a_id, a_id),
        )
        rows = cur.fetchall()
        if len(rows) < 2:
            continue
        loser = rows[1][0]
        cur.execute(
            """UPDATE ig_company_edge SET valid_to=%s,
                 source_doc = COALESCE(source_doc,'') || ' | quality_fix|p0_s16_bidir|""" + TODAY + """'
               WHERE edge_id=%s AND valid_to IS NULL""",
            (TODAY, loser),
        )
        if cur.rowcount:
            closed.append(loser)
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s16_bidir", "pairs": len(pairs), "closed": len(closed), "closed_ids": closed[:200]},
                     ensure_ascii=False))
    return 0


def s14_triage(apply: bool) -> int:
    """S14 挂链>20 甄别。保留规则（机械，落 JSON 报告）：

    K1 role ∈ {龙头,核心}
    K2 source_doc 三段式含 URL（websearch 时代已核证落位）
    K3 链 category = 公司行业锚点 category（THS 行业聚合链）
    K4 链名含锚点行业词干（锚点名去"行业"后缀）
    K5 symbol='000591.SZ' 且链名命中 Owner 裁定业务关键词
    其余（采购包模糊匹配污染）→ PIT 关闭。
    """
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(
        """SELECT nc.symbol, count(DISTINCT n.chain_id) FROM ig_node_company nc
           JOIN ig_node n ON nc.node_id=n.node_id
           JOIN ig_chain c ON n.chain_id=c.chain_id
           WHERE (c.status IS NULL OR c.status='active') AND nc.valid_to IS NULL
           GROUP BY nc.symbol HAVING count(DISTINCT n.chain_id) > 20"""
    )
    symbols = [r[0] for r in cur.fetchall()]
    # 锚点（行业聚合落位 -> 锚点链名/category）
    cur.execute(
        """SELECT nc.symbol, c.name, c.category FROM ig_node_company nc
           JOIN ig_node n ON nc.node_id=n.node_id
           JOIN ig_chain c ON n.chain_id=c.chain_id
           WHERE n.name='行业聚合' AND nc.valid_to IS NULL AND nc.symbol = ANY(%s)""",
        (symbols,),
    )
    anchor = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    report = {}
    for sym in symbols:
        a_name, a_cat = anchor.get(sym, ("", ""))
        stem = a_name[:-2] if a_name.endswith("行业") and len(a_name) > 2 else a_name
        kws = SYM000591_KW if sym == "000591.SZ" else None
        cur.execute(
            """SELECT nc.id, c.category, c.name,
                      (nc.role IN ('龙头','核心')) OR nc.source_doc LIKE '%%|http%%'
                      OR (%s<>'' AND c.category=%s)
                      OR (%s<>'' AND position(%s in c.name)>0)
                      OR (%s IS NOT NULL AND c.name ~ %s) AS keep
               FROM ig_node_company nc
               JOIN ig_node n ON nc.node_id=n.node_id
               JOIN ig_chain c ON n.chain_id=c.chain_id
               WHERE nc.symbol=%s AND (c.status IS NULL OR c.status='active') AND nc.valid_to IS NULL""",
            (a_cat, a_cat, stem, stem, kws, kws, sym),
        )
        rows = cur.fetchall()
        keep_ids = [r[0] for r in rows if r[3]]
        close_ids = [r[0] for r in rows if not r[3]]
        keep_chains = len({r[2] for r in rows if r[3]})
        report[sym] = {
            "anchor": f"{a_name}/{a_cat}",
            "placements": len(rows),
            "keep": len(keep_ids),
            "close": len(close_ids),
            "keep_chains_est": keep_chains,
            "_close_ids": close_ids,
        }
    conn.close()

    out = {s: {k: v for k, v in r.items() if k != "_close_ids"} for s, r in report.items()}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if not apply:
        print("[DRY-RUN] 仅出清单，未落库。--apply 执行 PIT 关闭。")
        return 0
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    total = 0
    for sym, r in report.items():
        ids = r["_close_ids"]
        if not ids:
            continue
        cur.execute(
            """UPDATE ig_node_company SET valid_to=%s,
                 source_doc = COALESCE(source_doc,'') || ' | quality_fix|p0_s14_triage|""" + TODAY + """',
                 updated_at=now()
               WHERE id = ANY(%s) AND valid_to IS NULL""",
            (TODAY, ids),
        )
        total += cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s14_triage", "applied": True, "closed": total}, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P0 污染源清除（PIT 关闭，幂等）")
    ap.add_argument("fix", choices=["s15-selfloops", "s16-bidir", "s4-residue", "s14-triage"])
    ap.add_argument("--apply", action="store_true", help="s14-triage 落库开关")
    args = ap.parse_args()
    if args.fix == "s15-selfloops":
        return fix_s15_selfloops()
    if args.fix == "s4-residue":
        return fix_s4_residue()
    if args.fix == "s16-bidir":
        return fix_s16_bidir()
    if args.fix == "s14-triage":
        return s14_triage(apply=args.apply)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        sys.exit(2)
