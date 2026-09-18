# [BLUEPRINT] GREATWALL-20260909-R1-EXEC | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.execute_r1_chain_plans
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] 长城任务 Phase3 R1 治理四方案执行(Owner 2026-09-08 预审批准); 引擎 S1/S2/S4 对账
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只增不删(链只 UPDATE name/status/source_note,零 DELETE); 幂等(改名按现链名匹配跳过已改; deprecated 幂等追加 merged_into 不覆盖 source_note; 新建母链 ON CONFLICT 跳过); 改名目标撞名自动降级为并入(§8.6 四条撞名改判规则的通用化); 废弃无承接链时并入同类别最大活跃承接链(对标 09-08 AI+厨电先例); 全程落 JSON 审计 .runtime/industry_graph/night_audit/r1_execution_20260909.json
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 方案文件缺失->exit 2; 目标链不存在->计入 skipped 不阻断
# [TESTS] 2026-09-09 首跑: 撞名并入4/废弃29/新建母链3/补指向80; 幂等复跑零新增
"""R1 链级治理方案执行器（Owner 2026-09-08 预审批准的四方案，链级处置）。

执行对象（链级：改名/deprecated+merged_into/新建母链；节点与公司并集归并明细不在本通道，
随 deprecated 链落位 PIT 关闭由 quality_fix_p0 s4-residue 收口，登记为后续工作）::

    python scripts/industry_graph/execute_r1_chain_plans.py            # 全部执行+审计落盘

方案真源：
    .runtime/industry_graph/night_audit/r1_rename_plan.md   （148 行表：改名46/并入73/废弃29）
    .runtime/industry_graph/night_audit/r1_merge_plan_[A-D].md（吸收子链 行，含 3 组新建母链）
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

NA = Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph" / "night_audit"
TODAY = date.today().isoformat()


def _chain_id(name: str) -> str:
    return f"CH-{hashlib.md5(name.encode('utf-8')).hexdigest()[:12]}"


def _note_has_merged(cur_note: str | None, cid: str) -> bool:
    return bool(cur_note) and f"merged_into:{cid}" in cur_note


def _deprecate(cur, cid: str, target: str | None) -> str:
    """deprecated + merged_into 幂等追加。返回 'merged'/'already'/'no_chain'。"""
    cur.execute("SELECT status, source_note FROM ig_chain WHERE chain_id=%s", (cid,))
    row = cur.fetchone()
    if not row:
        return "no_chain"
    if row[0] == "deprecated":
        if target and not _note_has_merged(row[1], target):
            cur.execute(
                "UPDATE ig_chain SET source_note=COALESCE(source_note,'')||' | merged_into:'||%s, updated_at=now() WHERE chain_id=%s",
                (target, cid),
            )
        return "already"
    cur.execute(
        """UPDATE ig_chain SET status='deprecated', updated_at=now(),
             source_note=COALESCE(source_note,'')||' | merged_into:'||%s
           WHERE chain_id=%s""",
        (target or "UNKNOWN", cid),
    )
    return "merged"


def _find_by_name(cur, name: str) -> tuple[str, str] | None:
    cur.execute("SELECT chain_id, status FROM ig_chain WHERE name=%s ORDER BY (status='active') DESC LIMIT 1", (name,))
    r = cur.fetchone()
    return (r[0], r[1]) if r else None


def _best_successor(cur, category: str | None, exclude: str) -> str | None:
    """同类别活跃链中落位最多者为承接链（对标 09-08 废弃链先例）。"""
    cur.execute(
        """SELECT c.chain_id FROM ig_chain c
           LEFT JOIN ig_node n ON n.chain_id=c.chain_id
           LEFT JOIN ig_node_company nc ON nc.node_id=n.node_id AND nc.valid_to IS NULL
           WHERE c.status='active' AND c.chain_id<>%s AND c.category=%s
           GROUP BY c.chain_id ORDER BY count(nc.id) DESC LIMIT 1""",
        (exclude, category or "综合"),
    )
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "SELECT chain_id FROM ig_chain WHERE status='active' AND name=%s",
        ((category or "综合") + "行业",),
    )
    r = cur.fetchone()
    return r[0] if r else None


def exec_rename_plan(cur, audit: dict) -> None:
    text = (NA / "r1_rename_plan.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (.+?) \| (改名|并入|废弃) \| (.+?) \| .+?\|$", text, re.M)
    audit["rename_plan"] = {"total": len(rows), "renamed": [], "merged": [], "deprecated": [], "skipped": []}
    # 先改名后并入（并入目标含改名产生的新母链）
    plan = [r for r in rows if r[1] == "改名"]
    for old, _, new, in plan:
        src = _find_by_name(cur, old)
        if src is None:
            audit["rename_plan"]["skipped"].append({"old": old, "why": "现链名不存在(已处置)"})
            continue
        sid, sst = src
        tgt = _find_by_name(cur, new)
        if tgt and tgt[0] != sid and tgt[1] == "active":
            # 撞名自动降级为并入（§8.6 改判规则通用化）
            r = _deprecate(cur, sid, tgt[0])
            audit["rename_plan"]["merged"].append({"old": old, "into": tgt[0], "why": "目标名已存在,改判并入"})
        elif tgt and tgt[0] != sid:
            audit["rename_plan"]["skipped"].append({"old": old, "why": "目标名存在但非活跃"})
        else:
            cur.execute("UPDATE ig_chain SET name=%s, updated_at=now() WHERE chain_id=%s", (new, sid))
            audit["rename_plan"]["renamed"].append({"old": old, "new": new, "chain_id": sid})
    for old, act, target, in [r for r in rows if r[1] != "改名"]:
        src = _find_by_name(cur, old)
        if src is None:
            audit["rename_plan"]["skipped"].append({"old": old, "why": f"{act}源链不存在(已处置)"})
            continue
        sid = src[0]
        if act == "并入":
            tgt = _find_by_name(cur, target)
            if tgt is None:
                audit["rename_plan"]["skipped"].append({"old": old, "why": f"母链不存在: {target}"})
                continue
            r = _deprecate(cur, sid, tgt[0])
            audit["rename_plan"]["merged" if r == "merged" else "skipped"].append(
                {"old": old, "into": tgt[0]} if r == "merged" else {"old": old, "why": "已deprecated"})
        else:  # 废弃
            cur.execute("SELECT category FROM ig_chain WHERE chain_id=%s", (sid,))
            cat = cur.fetchone()[0]
            succ = _best_successor(cur, cat, sid)
            if succ is None:
                audit["rename_plan"]["skipped"].append({"old": old, "why": "废弃无承接链,留开放问题"})
                continue
            r = _deprecate(cur, sid, succ)
            audit["rename_plan"]["deprecated"].append({"old": old, "into": succ})


def exec_merge_plans(cur, audit: dict) -> None:
    audit["merge_plans"] = {"merged": [], "created": [], "skipped": []}
    for letter in "ABCD":
        p = NA / f"r1_merge_plan_{letter}.md"
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        pending_new: dict | None = None  # 新建母链 {name, category}
        for ln in lines:
            m_new = re.search(r"\*{0,2}新建\*{0,2}「(.+?)」.*?category=([^—，,\-）]+)", ln)
            if m_new:
                pending_new = {"name": m_new.group(1), "category": m_new.group(2).strip()}
                continue
            if "吸收子链" not in ln:
                continue
            pairs = re.findall(r"([^\s（、|]+)\s*（?CH-([0-9a-f]{12})", ln)
            new_target = "merged_into:<新chain_id>" in ln or "merged_into:<新chain_id>" in ln
            tgt_m = re.search(r"merged_into:CH-([0-9a-f]{12})", ln)
            if new_target:
                if not pending_new:
                    audit["merge_plans"]["skipped"].append({"line": ln[:60], "why": "新链名缺失"})
                    continue
                name, cat = pending_new["name"], pending_new["category"]
                cid = _chain_id(name)
                cur.execute(
                    """INSERT INTO ig_chain (chain_id,name,category,version_year,market,status,source_note,created_at,updated_at)
                    VALUES (%s,%s,%s,2026,'cn','active','r1_merge_plan_new|长城任务|' || %s,now(),now())
                    ON CONFLICT (chain_id) DO UPDATE SET updated_at=now()""",
                    (cid, name, cat, TODAY),
                )
                audit["merge_plans"]["created"].append({"name": name, "chain_id": cid, "category": cat})
                target = cid
            elif tgt_m:
                target = f"CH-{tgt_m.group(1)}"
            else:
                audit["merge_plans"]["skipped"].append({"line": ln[:60], "why": "目标链解析失败"})
                continue
            for name_, cid in pairs:
                cur.execute("SELECT chain_id FROM ig_chain WHERE chain_id=%s", (f"CH-{cid}",))
                if cur.fetchone() is None or f"CH-{cid}" == target:
                    audit["merge_plans"]["skipped"].append({"chain": f"CH-{cid}", "why": "不存在或即目标"})
                    continue
                r = _deprecate(cur, f"CH-{cid}", target)
                if r == "merged":
                    audit["merge_plans"]["merged"].append({"chain": name_, "id": f"CH-{cid}", "into": target})
                elif r == "already":
                    # 已 deprecated：补 merged_into 指向（幂等）
                    audit["merge_plans"]["merged"].append({"chain": name_, "id": f"CH-{cid}", "into": target, "note": "补指向"})


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    audit: dict = {"executed_at": TODAY}
    exec_rename_plan(cur, audit)
    exec_merge_plans(cur, audit)
    conn.commit()
    conn.close()
    out = NA / "r1_execution_20260909.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = {
        "rename": {k: (v if isinstance(v, int) else len(v)) for k, v in audit["rename_plan"].items()},
        "merge_plans": {k: len(v) for k, v in audit["merge_plans"].items()},
        "audit_file": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] {e}")
        sys.exit(2)
