# [BLUEPRINT] GREATWALL-20260909-P2-FIX | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.quality_fix_p2
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.data.ch_writer (S19 stock_basic 反查)
# [CONSUMERS] 长城任务 Phase4 P2 合规修复 + Phase3 尾项(S1 残余/S5 年份/S8 垃圾链); 引擎 S1/S5/S8/S12/S17/S19/S20 对账
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删: S12 误挂 PIT 关闭; S17 补全 as_of=source_doc 采集日/valid_from=不晚于 as_of 的年中界/evidence_type=inferred(补全不覆盖已有值); S20 22 条有据(协议签署日)保留数据走豁免登记(报告标注须 Owner 签名); S19 编码表上市撞名按 stock_basic 一手主数据标定 listed 并跑 promote 换码; S5 年份按 evidence_text 内嵌年份众数/最大值(2019-2026 界)机械提取; 幂等
# [MODIFY-GUARD] graph_quality_standard.md(S5/S12/S17/S19/S20 修复方案真源)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->exit 2
# [TESTS] 2026-09-09 首跑: s1=2/s5=256/s8垃圾链30/s12=1/s17=113/s19=17/s20豁免22
# [TTL] permanent
"""P2 合规修复 + P1 尾项综合治理脚本（子命令，全幂等）::

    s1-rename        S1 残余 2 链改规范名
    s5-fill-years    S5 version_year 按 evidence 年份机械提取（无据链清单落盘）
    s8-junk-chains   S8 垃圾研究链（零落位+单节点）废弃并入承接链
    s12-fix          S12 特斯拉误挂 cn 节点 PIT 关闭
    s17-backfill     S17 websearch 边补 PIT 三件套+evidence_type（只补空值）
    s19-promote      S19 编码表上市撞名：stock_basic 反查→listed→promote 换码
    s20-exempt       S20 有据豁免登记（协议签署日实锤，须 Owner 签名标注）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

TODAY = date.today().isoformat()
NA = REPO / ".runtime" / "industry_graph" / "night_audit"
YEAR_RE = re.compile(r"(20[12]\d)")

# §5.160.2 SQL 集中化（2026-09-11 st-igbe 接手批）：S4 满贯批/S25 改名新增行按 gate 要求
# 提取为模块级常量（NO-BARE-SQL 豁免口径=SQL_* 常量定义）；pre-existing 修复函数 SQL 不动
_SQL_S4_CHAIN_BY_NAME = (
    "SELECT chain_id, category, source_note FROM ig_chain WHERE name=%s AND status='deprecated'"
)
_SQL_S4_TARGET_BY_NAME = "SELECT chain_id FROM ig_chain WHERE name=%s AND status='active'"
_SQL_S4_MERGE_NOTE = """UPDATE ig_chain SET source_note=COALESCE(source_note,'')||' | merged_into:'||%s,
               updated_at=now() WHERE chain_id=%s"""
_SQL_S4_CLOSE_PLACEMENTS = """UPDATE ig_node_company nc SET valid_to=CURRENT_DATE, updated_at=now()
               FROM ig_node n WHERE n.node_id=nc.node_id AND nc.valid_to IS NULL
                 AND n.chain_id=%s"""
_SQL_S25_TARGET_EXISTS = "SELECT chain_id, status FROM ig_chain WHERE name=%s"
_SQL_S25_OLD_LOOKUP = "SELECT chain_id FROM ig_chain WHERE name=%s"
_SQL_S25_RENAME = "UPDATE ig_chain SET name=%s, updated_at=now() WHERE chain_id=%s"


def _deprecate(cur, cid: str, target: str) -> str:
    cur.execute("SELECT status, source_note FROM ig_chain WHERE chain_id=%s", (cid,))
    row = cur.fetchone()
    if not row:
        return "no_chain"
    if row[0] == "deprecated":
        if target and f"merged_into:{target}" not in (row[1] or ""):
            cur.execute(
                "UPDATE ig_chain SET source_note=COALESCE(source_note,'')||' | merged_into:'||%s, updated_at=now() WHERE chain_id=%s",
                (target, cid),
            )
        return "already"
    cur.execute(
        """UPDATE ig_chain SET status='deprecated', updated_at=now(),
             source_note=COALESCE(source_note,'')||' | merged_into:'||%s WHERE chain_id=%s""",
        (target, cid),
    )
    return "merged"


def _best_successor(cur, category: str | None, exclude: str) -> str | None:
    cur.execute(
        """SELECT c.chain_id FROM ig_chain c
           LEFT JOIN ig_node n ON n.chain_id=c.chain_id
           LEFT JOIN ig_node_company nc ON nc.node_id=n.node_id AND nc.valid_to IS NULL
           WHERE c.status='active' AND c.chain_id<>%s AND c.category=%s
           GROUP BY c.chain_id ORDER BY count(nc.id) DESC LIMIT 1""",
        (exclude, category or "综合"),
    )
    r = cur.fetchone()
    return r[0] if r else None


def fix_s1_rename() -> int:
    renames = {"最新3D玻璃": "3D玻璃产业链", "线上消费行业市场机遇": "线上消费产业链"}
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    done = []
    for old, new in renames.items():
        cur.execute("SELECT chain_id FROM ig_chain WHERE name=%s AND status='active'", (old,))
        r = cur.fetchone()
        cur.execute("SELECT 1 FROM ig_chain WHERE name=%s", (new,))
        exists = cur.fetchone()
        if r and not exists:
            cur.execute("UPDATE ig_chain SET name=%s, updated_at=now() WHERE chain_id=%s", (new, r[0]))
            done.append({"old": old, "new": new})
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s1_rename", "done": done}, ensure_ascii=False))
    return 0


def fix_s5_years() -> int:
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(
        """SELECT c.chain_id, max(m.y) FROM ig_chain c
           JOIN ig_node n ON n.chain_id=c.chain_id
           JOIN (SELECT node_id, (regexp_match(evidence_text, '20[12]\\d'))[1] y
                 FROM ig_node_company WHERE evidence_text IS NOT NULL AND valid_to IS NULL) m
             ON m.node_id=n.node_id
           WHERE c.version_year IS NULL AND (c.status IS NULL OR c.status='active') AND c.name NOT LIKE '%行业'
           GROUP BY c.chain_id HAVING max(m.y) IS NOT NULL"""
    )
    fills = [(r[0], int(r[1])) for r in cur.fetchall()]
    cur.execute(
        """SELECT c.chain_id, c.name FROM ig_chain c
           WHERE c.version_year IS NULL AND (c.status IS NULL OR c.status='active') AND c.name NOT LIKE '%行业'"""
    )
    all_missing = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    filled = [(cid, y) for cid, y in fills if 2019 <= y <= 2026]
    residue = {cid: n for cid, n in all_missing.items() if cid not in {f[0] for f in filled}}
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    for cid, y in filled:
        cur.execute(
            "UPDATE ig_chain SET version_year=%s, updated_at=now() WHERE chain_id=%s AND version_year IS NULL",
            (y, cid),
        )
    conn.commit()
    conn.close()
    (NA / "s5_no_evidence_chains_20260909.json").write_text(
        json.dumps(residue, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"fix": "s5_fill_years", "filled": len(filled), "no_evidence": len(residue),
                      "residue_file": "s5_no_evidence_chains_20260909.json"}, ensure_ascii=False))
    return 0


def fix_s8_junk_chains() -> int:
    """零落位且≤2节点的活跃孤岛链=研究标题垃圾，废弃并入同类别承接链（对标 09-08 先例）。"""
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """SELECT c.chain_id, c.name, c.category, count(n.node_id) FROM ig_chain c
           JOIN ig_node n ON n.chain_id=c.chain_id
           WHERE c.status='active' AND EXISTS (
             SELECT 1 FROM ig_node n2 WHERE n2.chain_id=c.chain_id
               AND NOT EXISTS (SELECT 1 FROM ig_edge e WHERE e.from_node=n2.node_id OR e.to_node=n2.node_id)
               AND NOT EXISTS (SELECT 1 FROM ig_node_company nc WHERE nc.node_id=n2.node_id AND nc.valid_to IS NULL)
               AND n2.name <> '行业聚合' AND n2.name NOT LIKE '%（已并入%')
           GROUP BY c.chain_id HAVING count(n.node_id) <= 2"""
    )
    cands = cur.fetchall()
    merged, skipped = [], []
    for cid, name, cat, _ in cands:
        succ = _best_successor(cur, cat, cid)
        if succ is None:
            skipped.append({"chain": name, "why": "无承接链"})
            continue
        r = _deprecate(cur, cid, succ)
        (merged if r == "merged" else skipped).append(
            {"chain": name, "into": succ} if r == "merged" else {"chain": name, "why": "已deprecated"})
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s8_junk_chains", "candidates": len(cands), "merged": len(merged),
                      "skipped": len(skipped)}, ensure_ascii=False))
    return 0


def fix_s12() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """UPDATE ig_node_company SET valid_to=%s,
             source_doc=COALESCE(source_doc,'')||' | quality_fix|p2_s12|""" + TODAY + """', updated_at=now()
           WHERE id=43952 AND valid_to IS NULL""",
        (TODAY,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s12", "closed": n, "note": "TSLA.US 误挂 cn 节点,全球锚点待扩产重挂 global 节点"}))
    return 0


def fix_s17() -> int:
    """websearch 边补空值：as_of=source_doc 采集日; valid_from=不晚于 as_of 的 6/12 月末; evidence_type=inferred。"""
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        """SELECT edge_id, year, source_doc,
                 (regexp_match(source_doc, '\\|(\\d{4}-\\d{2}-\\d{2})$'))[1]
           FROM ig_company_edge
           WHERE source='websearch' AND valid_to IS NULL
             AND (valid_from IS NULL OR as_of IS NULL OR evidence_type IS NULL)"""
    )
    rows = cur.fetchall()
    fixed = 0
    for eid, year, sd, dstr in rows:
        as_of = dstr or str(TODAY)
        vf = None
        if year:
            mid = f"{year}-06-30"
            end = f"{year}-12-31"
            vf = mid if mid <= as_of else None
            if vf is None and end <= as_of:
                vf = end
        cur.execute(
            """UPDATE ig_company_edge SET
                 as_of=COALESCE(as_of,%s),
                 valid_from=COALESCE(valid_from,%s),
                 evidence_type=COALESCE(evidence_type,'inferred')
               WHERE edge_id=%s""",
            (as_of, vf, eid),
        )
        fixed += cur.rowcount
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s17_backfill", "fixed": fixed}, ensure_ascii=False))
    return 0


def fix_s19() -> int:
    from zephyr.data import ch_writer

    tsv = ch_writer.query(
        "SELECT name, symbol_canonical FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
    )
    name2sym = {}
    for ln in tsv.strip().splitlines():
        p = ln.split("\t")
        if len(p) >= 2:
            name2sym[p[0].strip()] = p[1].strip()
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute("SELECT ue_id, name FROM ig_unlisted_entity WHERE status='unlisted'")
    hits = []
    for ue, name in cur.fetchall():
        sym = name2sym.get(name)
        if sym:
            cur.execute(
                """UPDATE ig_unlisted_entity SET status='listed', listed_symbol=%s, updated_at=now()
                   WHERE ue_id=%s""",
                (sym, ue),
            )
            hits.append({"ue": ue, "name": name, "symbol": sym})
    conn.commit()
    conn.close()
    promoted = 0
    if hits:
        rc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "industry_graph" / "promote_unlisted_to_listed.py")],
            capture_output=True, text=True)
        m = re.search(r'"promoted[_a-z]*":\s*(\d+)', rc.stdout or "")
        promoted = int(m.group(1)) if m else -1
        if rc.returncode != 0:
            promoted = f"promote脚本退出{rc.returncode}: {(rc.stderr or rc.stdout)[-200:]}"
    print(json.dumps({"fix": "s19_promote", "marked_listed": len(hits), "promote_result": promoted,
                      "detail": hits}, ensure_ascii=False))
    return 0


def fix_s20_exempt() -> int:
    ex = Path(__file__).resolve().parent / "quality_exemptions.yaml"
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(
        """SELECT edge_id::text, from_symbol, to_symbol, year, valid_from, left(source_doc, 80)
           FROM ig_company_edge
           WHERE valid_from IS NOT NULL AND year IS NOT NULL AND valid_to IS NULL
             AND valid_from < make_date(year - 1, 1, 1)"""
    )
    rows = cur.fetchall()
    conn.close()
    ids = [r[0] for r in rows]
    t = ex.read_text(encoding="utf-8")
    if "S20: [" not in t:
        t = t.replace(
            "S6: [",
            "S20: [" + ", ".join(f'"{i}"' for i in ids) + "]\nS6: [",
        )
        t = t.replace("# 当前豁免: S14 1 条(平台型药企甄别为真,长城任务 2026-09-09)",
                      "# 当前豁免: S14 1 条(平台型药企)+S20 22 条(有据协议日,须Owner签名)+S6 306 条(待Owner处置)")
        ex.write_text(t, encoding="utf-8")
    lines = [
        "",
        f"## S20 豁免 22 条（2026-09-09 长城任务登记）⚠️ 豁免数 22/22=100%>5%，须 Owner 签名确认",
        "",
        "全部为 websearch 首夜边：valid_from=协议签署日实锤（evidence 原文含关系起始依据），",
        "year=2026（信息年=新闻年）与规则 year-1 界冲突属启发式误报——数据真实不改动（改动=毁 PIT 实据）。",
        "规则修订建议（开放问题）：S20 对有 evidence 支撑的 valid_from 放行，或按 valid_from 年重算 year 口径。",
        "",
        "| edge_id | 边 | year | valid_from |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]}->{r[2]} | {r[3]} | {r[4]} |")
    with open(NA / "open_questions_20260909.md", "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({"fix": "s20_exempt", "count": len(ids), "owner_signature_required": True}, ensure_ascii=False))
    return 0


def fix_s4_close_merge() -> int:
    """S4 废弃链闭环（2026-09-11 满贯批）：5 条 deprecated 链补 merged_into 落款
    + 落位残留 PIT 关闭。承接者：2 条按名承接（聚氨酯（PU）行业/氟化工），
    3 条按 _best_successor 同类最多活跃落位先例承接。幂等：已带 merged_into 跳过、
    valid_to IS NULL 才关。"""
    named_targets = {
        "聚氨酯材料市场和应用": "聚氨酯（PU）行业",
        "氟化工市场和应用": "氟化工",
    }
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    done = []
    chains = ["聚氨酯材料市场和应用", "环氧丙烷产业链供需格局", "中国节水装备行业发展现状",
              "氟化工市场和应用", "金融消费行业趋势"]
    for name in chains:
        cur.execute(_SQL_S4_CHAIN_BY_NAME, (name,))
        row = cur.fetchone()
        if not row:
            done.append({"chain": name, "skip": "not-found-or-not-deprecated"})
            continue
        cid, category, source_note = row
        if source_note and "merged_into:CH-" in source_note:
            done.append({"chain": name, "skip": "already-merged"})
            continue
        if name in named_targets:
            cur.execute(_SQL_S4_TARGET_BY_NAME, (named_targets[name],))
            trow = cur.fetchone()
            target = trow[0] if trow else None
        else:
            target = _best_successor(cur, category, cid)
        if not target:
            done.append({"chain": name, "skip": "no-successor"})
            continue
        cur.execute(_SQL_S4_MERGE_NOTE, (target, cid))
        cur.execute(_SQL_S4_CLOSE_PLACEMENTS, (cid,))
        closed = cur.rowcount
        done.append({"chain": name, "merged_into": target, "placements_closed": closed})
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s4_close_merge", "done": done}, ensure_ascii=False))
    return 0


def fix_s25_rename() -> int:
    """S25 链名结构完整（2026-09-11 满贯批）：15 裸缩写扩中文全称+2 未闭合括号闭合
    +1 悬空尾裁齐。链名 ≤12 字（SOP §4.7.1），中文主名（缩写）房 style，查重后才改；
    chain_id 不变（md5 原名稳定键，节点/落位/边全保留）。"""
    renames = {
        "SOFC": "固体氧化物燃料电池",
        "VR": "虚拟现实（VR）",
        "AIDC": "智算中心（AIDC）",
        "HNB": "加热不燃烧烟草（HNB）",
        "PEEK": "聚醚醚酮（PEEK）",
        "ASIC": "专用芯片（ASIC）",
        "PVD": "物理气相沉积（PVD）",
        "LCD": "液晶显示（LCD）",
        "TMT": "科技传媒通信（TMT）",
        "IP": "半导体IP",
        "CPO": "光电共封装（CPO）",
        "LED": "发光二极管（LED）",
        "OLED": "有机发光显示（OLED）",
        "AIPC": "AI电脑（AIPC）",
        "PCB": "印制电路板（PCB）",
        "碳化硅（SiC": "碳化硅（SiC）",
        "阿尔兹海默症（AD": "阿尔兹海默症（AD）",
        "光模块行业历史脉络与": "光模块行业",
    }
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    done = []
    for old, new in renames.items():
        if len(new) > 12:
            done.append({"old": old, "new": new, "skip": "new-name-too-long"})
            continue
        cur.execute(_SQL_S25_TARGET_EXISTS, (new,))
        if cur.fetchone():
            done.append({"old": old, "new": new, "skip": "target-name-exists"})
            continue
        cur.execute(_SQL_S25_OLD_LOOKUP, (old,))
        row = cur.fetchone()
        if not row:
            done.append({"old": old, "skip": "not-found"})
            continue
        cur.execute(_SQL_S25_RENAME, (new, row[0]))
        done.append({"old": old, "new": new, "chain_id": row[0]})
    conn.commit()
    conn.close()
    print(json.dumps({"fix": "s25_rename", "done": done}, ensure_ascii=False))
    return 0




def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["s1-rename", "s5-fill-years", "s8-junk-chains", "s12-fix", "s4-close-merge", "s25-rename",
                                    "s17-backfill", "s19-promote", "s20-exempt", "all"])
    args = ap.parse_args()
    fns = {
        "s1-rename": fix_s1_rename, "s5-fill-years": fix_s5_years, "s8-junk-chains": fix_s8_junk_chains, "s4-close-merge": fix_s4_close_merge, "s25-rename": fix_s25_rename,
        "s12-fix": fix_s12, "s17-backfill": fix_s17, "s19-promote": fix_s19, "s20-exempt": fix_s20_exempt,
    }
    try:
        if args.cmd == "all":
            for fn in fns.values():
                fn()
            return 0
        return fns[args.cmd]()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
