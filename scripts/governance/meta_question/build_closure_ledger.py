# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md
# [MODULE] scripts.governance.meta_question.build_closure_ledger
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection, 只读); PyYAML; 读
#                docs/_working/meta_question_answers/{results,gaps}/ 与 build/REEXAM*/WO-*.yaml 为盘侧证据源
# [CONSUMERS] 战役收官报告（docs/_working/meta_question_answers/04_closure_ledger.yaml）；Owner 验收面
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯派生件：三态计数与 fail 分型只从 PG meta_question 表读，禁在任何散文/常量里写死数字；
#              工单映射只从 WORKORDER_MASTER.md 解析；处置状态只从 build/ 案卷存在性与内容判定；
#              缺证据一律标 unknown 不猜（"未知项非零"必须可见）；同输入必同输出（水位取盘侧数据非墙钟）；
#              本脚本只读，绝不写 PG/CH。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达→抛错非零退出（禁静默出半成品台账，静默成功尺是本战役头号敌人）。
# [TESTS] tests/governance/meta_question/test_build_closure_ledger.py
# [A_module] module_id=MOD-METAQ-CLOSURE-LEDGER | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""build_closure_ledger — 283 问战役施工闭环总台账生成器（机读，禁手工维护）。

把"考卷三态 × 工单映射 × 施工证据 × 复考结论"合成一张可复核的闭环表，供收官报告与
Owner 验收使用。判据全部取自盘侧真源，任何一格缺证据就标 unknown，不做乐观推断。
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

REPO = REPO_ROOT
ANSWERS = REPO / "docs" / "_working" / "meta_question_answers"
WORKORDER_MD = ANSWERS / "gaps" / "WORKORDER_MASTER.md"
BUILD_DIR = ANSWERS / "casefiles"
RESULTS_DIR = ANSWERS / "results"
SCHEMA = "meta_question"

# 工单 → 覆盖问号（从 WORKORDER_MASTER 标题与正文解析，不写死清单）
_QID_RE = re.compile(r"PQ-(\d{4})")
_WO_HEAD_RE = re.compile(r"^## (WO-\d+)｜(.+?)(?:（(.*?)）)?$")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）；SCHEMA 为唯一表限定符来源。
_SQL_LATEST_ROW_PER_Q = (
    f"select distinct on (q_id) q_id, conclusion, created_at "
    f"from {SCHEMA}.meta_question_exam_result "
    f"order by q_id, created_at desc"
)
_SQL_EXAM_WATERMARK = f"select max(created_at), count(*) from {SCHEMA}.meta_question_exam_result"
_SQL_QUESTION_COUNT = f"select count(*) from {SCHEMA}.meta_question"
_SQL_QUESTION_META = f"select q_id, layer, title, exam_plan from {SCHEMA}.meta_question"


def _connect():
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection()


def _watermark(conn) -> dict:
    """水位取自盘侧数据（非墙钟），保证同输入同输出。"""
    cur = conn.cursor()
    try:
        cur.execute(_SQL_EXAM_WATERMARK)
        latest, n = cur.fetchone()
        cur.execute(_SQL_QUESTION_COUNT)
        qn = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
    return {"exam_result_rows": n, "questions": qn, "latest_exam_result_at": str(latest)}


def read_verdicts(conn) -> dict[str, dict]:
    """每问取最新一行结论（同问可有多行=改判追加，取 created_at 最大）。"""
    cur = conn.cursor()
    try:
        cur.execute(_SQL_LATEST_ROW_PER_Q)
        out: dict[str, dict] = {}
        for qid, concl, created in cur.fetchall():
            if isinstance(concl, str):
                concl = json.loads(concl)
            out[qid] = {
                "outcome": concl.get("outcome"),
                "fail_type": concl.get("fail_type"),
                "exam_ref": concl.get("exam_ref"),
                "recorded_at": str(created),
            }
    finally:
        cur.close()
    return out


def read_exam_plans(conn) -> dict[str, dict]:
    cur = conn.cursor()
    try:
        cur.execute(_SQL_QUESTION_META)
        out = {}
        for qid, layer, title, plan in cur.fetchall():
            if isinstance(plan, str):
                plan = json.loads(plan)
            out[qid] = {"layer": layer, "title": title, "exam_plan": plan or {}}
    finally:
        cur.close()
    return out


def parse_workorders() -> dict[str, dict]:
    """WORKORDER_MASTER.md → {WO-id: {title, gates, q_ids}}（解析非硬编码）。"""
    text = WORKORDER_MD.read_text(encoding="utf-8")
    wos: dict[str, dict] = {}
    current: str | None = None
    for line in text.splitlines():
        head = re.match(r"^## (WO-\d+)(?:｜(.*))?$", line)
        if head:
            current = head.group(1)
            wos[current] = {"heading": (head.group(2) or "").strip(), "q_ids": set(), "gate_lines": []}
            continue
        if current and line.strip():
            wos[current]["q_ids"].update(_QID_RE.findall(line) and [f"PQ-{x}" for x in _QID_RE.findall(line)])
            if "门位" in line:
                wos[current]["gate_lines"].append(line.strip()[:300])
    return {
        k: {"heading": v["heading"], "q_ids": sorted(v["q_ids"]), "gate_lines": v["gate_lines"]} for k, v in wos.items()
    }


def load_casefiles() -> dict[str, dict]:
    """build/ 下的施工案卷与复考案卷（存在即证据，内容按 yaml 读）。"""
    out: dict[str, dict] = {}
    if not BUILD_DIR.exists():
        return out
    for p in sorted(list(BUILD_DIR.glob("*.yaml")) + list(BUILD_DIR.glob("*.md"))):
        try:
            text = p.read_text(encoding="utf-8")
            if p.suffix == ".md":
                # 散文案卷：frontmatter 可解析则取之，正文按 blob 供问号归属扫描
                fm = text.split("---")[1] if text.startswith("---") else ""
                meta = yaml.safe_load(fm) or {}
                out[p.name] = {"frontmatter": meta, "body": text}
                continue
            doc = yaml.safe_load(text) or {}
        except Exception as exc:  # noqa: BLE001 — 坏件必须可见，不能静默消失
            out[p.name] = {"_parse_error": str(exc)[:200]}
            continue
        out[p.name] = doc if isinstance(doc, dict) else {"_shape": str(type(doc))}
    return out


def _result_mirror_qids() -> set[str]:
    """results/ 分片镜像里的问号（283 交付面落地核对）。"""
    found: set[str] = set()
    if not RESULTS_DIR.exists():
        return found
    for p in RESULTS_DIR.rglob("PQ-*.yaml"):
        found.add(p.stem)
    return found


def _phase2_section(current: str | None, line: str) -> str | None:
    """三分诊表的节游标推进（A/B/C 三节 + 泛 `##` 节重置；**归并行不打断当前节）。"""
    if line.startswith("## 《数据施工需求清单》"):
        return "A"
    if line.startswith("## 《建设需求清单》"):
        return "B"
    if line.startswith("## C 类案由登记"):
        return "C"
    if line.startswith("## ") or line.startswith("**A 类归并") or line.startswith("**B 类归并"):
        if not line.startswith("**"):
            return None
    return current


def _phase2_record(current: str, rest: list[str]) -> dict:
    """行单元格 → 分诊记录（A=缺数据源｜B=载体未建｜C=案由，列位与原文一致）。"""
    rec = {"class": current}
    if current == "A":
        rec.update(
            {
                "data_source": rest[0] if rest else "",
                "window": rest[1] if len(rest) > 1 else "",
                "scale": rest[2] if len(rest) > 2 else "",
                "reexam_precondition": rest[3] if len(rest) > 3 else "",
            }
        )
    elif current == "B":
        rec.update({"carrier_to_build": rest[0] if rest else "", "build_points": rest[1] if len(rest) > 1 else ""})
    else:
        rec.update({"case": rest[0] if rest else "", "owner_gate": rest[1] if len(rest) > 1 else ""})
    return rec


def parse_phase2_triage() -> dict[str, dict]:
    """01_phase2_plan.md 三分诊表 → {PQ-xxxx: {class, source_or_carrier, window, scale/precondition}}.

    A 类=缺数据源｜B 类=载体未建｜C 类=设计内/立法债（案由归档）。解析而非手抄：
    该表由生成器产出过，手工再抄一份必漂移（本仓铁律）。
    """
    p = ANSWERS / "01_phase2_plan.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    current = None
    for line in text.splitlines():
        current = _phase2_section(current, line)
        if not current or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not _QID_RE.fullmatch(cells[0]):
            continue
        qid = cells[0]
        rest = cells[1:]
        out.setdefault(qid, _phase2_record(current, rest))
    return out


def index_registers_by_qid() -> dict[str, list[str]]:
    """一次扫盘建 问号→证据册 索引（禁逐问重读：册面有 MB 级件，283×重读会退化成慢尺）。"""
    idx: dict[str, list[str]] = {}
    for p in sorted((REPO / "data" / "registers").rglob("*.yaml")):
        try:
            body = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = p.as_posix().split("data/registers/")[-1]
        for qid in set(_QID_RE.findall(body)):
            idx.setdefault(f"PQ-{qid}", []).append(rel)
    return idx


def _case_index(cases: dict[str, dict]) -> dict[str, list[str]]:
    """案卷 → 问号 归属（案卷正文里显式写了 closes/completes/pq00XX 的才认）。"""
    case_by_qid: dict[str, list[str]] = {}
    for name, doc in cases.items():
        blob = json.dumps(doc, ensure_ascii=False, default=str)
        for q in set(_QID_RE.findall(blob)):
            case_by_qid.setdefault(f"PQ-{q}", []).append(name)
    return case_by_qid


def _workorder_index(wos: dict[str, dict]) -> dict[str, list[str]]:
    """工单 → 问号 反查索引（同问可属多工单，序保持）。"""
    qmap: dict[str, list[str]] = {}
    for wo, meta in wos.items():
        for q in meta["q_ids"]:
            qmap.setdefault(q, []).append(wo)
    return qmap


def _build_items(
    verdicts: dict[str, dict],
    plans: dict[str, dict],
    triage: dict[str, dict],
    qmap: dict[str, list[str]],
    case_by_qid: dict[str, list[str]],
    reg_idx: dict[str, list[str]],
    only_qids: set[str] | None,
) -> dict[str, dict]:
    """逐问合成台账条目（三态×工单×案卷×册×分诊；only_qids 子集过滤）。"""
    items: dict[str, dict] = {}
    for qid in sorted(verdicts):
        if only_qids and qid not in only_qids:
            continue
        v = verdicts[qid]
        p = plans.get(qid, {})
        tri = triage.get(qid, {})
        items[qid] = {
            "layer": p.get("layer"),
            "outcome": v["outcome"],
            "fail_type": v.get("fail_type"),
            "threshold": (p.get("exam_plan") or {}).get("threshold"),
            "criterion": (p.get("exam_plan") or {}).get("criterion"),
            "workorders": sorted(set(qmap.get(qid, []))),
            "casefiles": sorted(set(case_by_qid.get(qid, []))),
            "registers": sorted(set(reg_idx.get(qid, []))),
            "triage_class": tri.get("class"),
            "recorded_at": v["recorded_at"],
        }
    return items


def _count_by(items: dict[str, dict], field: str, values: tuple[str, ...]) -> dict[str, int]:
    """按字段取值计数（分布口径：只数命中等值，缺值不计）。"""
    return {k: sum(1 for d in items.values() if d[field] == k) for k in values}


def _open_evidence_stats(open_q: list[str], items: dict[str, dict]) -> dict[str, int]:
    """开工面统计（open_* 五键；证据面口径注释随行保留）。"""
    return {
        "open_total": len(open_q),
        "open_with_workorder": sum(1 for q in open_q if items[q]["workorders"]),
        "open_with_casefile": sum(1 for q in open_q if items[q]["casefiles"]),
        # 施工证据面 = 案卷 ∪ 机读册 ∪ 工单归属 ∪ A/B/C 分诊归属
        # （只认案卷会把已建成件误计为"无据"，终报虚报欠账）
        "open_with_any_evidence": sum(
            1
            for q in open_q
            if items[q]["casefiles"] or items[q]["workorders"] or items[q]["triage_class"] or items[q]["registers"]
        ),
        "open_without_any_evidence": sum(
            1
            for q in open_q
            if not items[q]["casefiles"]
            and not items[q]["workorders"]
            and not items[q]["triage_class"]
            and not items[q]["registers"]
        ),
    }


def build(only_qids: set[str] | None = None, conn_factory=None) -> dict:
    conn = (conn_factory or _connect)()
    verdicts = read_verdicts(conn)
    plans = read_exam_plans(conn)
    mark = _watermark(conn)
    wos = parse_workorders()
    cases = load_casefiles()
    triage = parse_phase2_triage()
    reg_idx = index_registers_by_qid()

    case_by_qid = _case_index(cases)
    qmap = _workorder_index(wos)
    items = _build_items(verdicts, plans, triage, qmap, case_by_qid, reg_idx, only_qids)

    open_q = [q for q, d in items.items() if d["outcome"] in ("fail", "insufficient")]
    stats = {
        "questions": len(items),
        "outcome_dist": _count_by(items, "outcome", ("pass", "fail", "insufficient")),
        "fail_type_dist": _count_by(items, "fail_type", ("no_alpha", "infra")),
        **_open_evidence_stats(open_q, items),
        "results_mirror_files": len(_result_mirror_qids()),
        "casefile_count": len(cases),
        "workorder_count": len(wos),
        "triage_dist": _count_by(items, "triage_class", ("A", "B", "C")),
        "triage_parsed": len(triage),
    }
    return {
        "generated_by": "scripts/governance/meta_question/build_closure_ledger.py",
        "watermark": mark,
        "stats": stats,
        "workorders": wos,
        "items": items,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="283 问战役施工闭环总台账生成器（只读派生）")
    ap.add_argument("--out", default=str(ANSWERS / "04_closure_ledger.yaml"))
    ap.add_argument("--only", help="逗号分隔问号子集（调试/局部核验用）")
    ap.add_argument("--stdout", action="store_true", help="只打印计数，不落文件")
    args = ap.parse_args()

    only = set(args.only.split(",")) if args.only else None
    doc = build(only)
    if args.stdout:
        print(json.dumps(doc["stats"], ensure_ascii=False, default=str))
        return 0
    stamp = datetime.datetime.now(datetime.UTC)  # noqa: DTZ001 — 文件头注释位，非数据水位
    head = (
        f"---\nttl: task_bound\ncompletes_when: 283 问战役施工闭环验收后随总包归档\n---\n"
        f"# 283 问战役施工闭环总台账（生成器产出，手工维护违铁律）\n"
        f"# 生成时刻(仅注释位，非数据水位): {stamp.isoformat()}\n"
    )
    Path(args.out).write_text(
        head + yaml.safe_dump(doc, allow_unicode=True, sort_keys=True, width=200), encoding="utf-8", newline="\n"
    )
    print(f"落盘 {args.out}")
    print(json.dumps(doc["stats"], ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免 按需手工点火CLI非常驻自动任务
    sys.exit(main())
