# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 批5总册+家底总表+缺口单+原问题匹配
# [MODULE] scripts.backtest.fexam.campaign_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.fexam.roster; yaml（八册底册只读）
# [CONSUMERS] run_fexam.py; Owner 晨报
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 总表机生禁手填（八底册合成，映射规则随文件头落盘）；四缺口单=纯集合运算可复算；
#              原问题匹配只读册+快照，回填仅走 writeback API 且六查合规（不合规只出对照表）；
#              H11 覆盖册只读引用不代写；计数全部用字段
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 底册缺失→该册记 missing 继续其余（总表列 missing_sources）；分数册缺失→总册记 pending
# [TESTS] tests/backtest/fexam/test_campaign_report.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（缺口单集合运算规则禁改）
# [TTL] permanent
# create-guard-not-dup: 战役汇总器（'load yaml'为读取手段非能力本体），与命名检查/n16加载器无交集
"""campaign_report — 批5：考试总册 + matrix_inventory 家底总表 + 四张缺口单 + 原问题匹配表。

底册八册（真源指针随行）：
①data_asset_registry ②factor_registry ③strategy_registry ④trading_decision_map
⑤tasks(经 data_asset_registry produced_by/consumed_by 字段投影) ⑥trial_ledger_registry
⑦map_census ⑧meta_question（快照 registry_latest.yaml + question_batch_w6.yaml）
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

CATALOGS = RUN_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
FEXAM_DIR = RUN_ROOT / "docs" / "_working" / "fexam"
FULLCIRC = RUN_ROOT / "docs" / "_working" / "fullcirc_closeout_chief"
METAQ_SNAP = RUN_ROOT / "docs" / "_working" / "chain_piling_campaign" / "snapshots"

#: metaq 标题清单查询（SQL 集中化：唯一只读查询，禁内联扩散）
SQL_METAQ_TITLES = "SELECT q_id, title FROM meta_question.meta_question ORDER BY q_id"

BOOKS = {
    "factor": FEXAM_DIR / "factor_exam_scores_v1.yaml",
    "indicator": FEXAM_DIR / "indicator_exam_scores_v1.yaml",
    "strategy": FEXAM_DIR / "strategy_exam_scores_v1.yaml",
    "allocator": FEXAM_DIR / "allocator_shadow_report_v1.yaml",
}


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------- 批5 总册 ----------


def build_summary(out_path: Path) -> dict[str, Any]:
    """批5：四类计数/及格率/退役候选清单/建议呈批项；对接 H11 覆盖册（只读）。"""
    sections: dict[str, Any] = {}
    for kind, path in BOOKS.items():
        book = _load_yaml(path)
        if book is None:
            sections[kind] = {"status": "pending", "note": f"分数册缺失: {path.name}"}
            continue
        results = book.get("results", [])
        sections[kind] = {
            "status": "done",
            "counts": book.get("counts", {}),
            "retire_candidates": [r["object_id"] for r in results if r.get("verdict") == "retire_candidate"],
            "passes": [r["object_id"] for r in results if r.get("verdict") == "pass"],
        }

    coverage_ledger = _load_yaml(FULLCIRC / "backtest_coverage_ledger.yaml")
    coverage_join = {
        "source": str(FULLCIRC.relative_to(RUN_ROOT)).replace("\\", "/") + "/backtest_coverage_ledger.yaml",
        "status": "referenced_readonly",
    }
    if isinstance(coverage_ledger, dict):
        coverage_join["version"] = coverage_ledger.get("version")
        coverage_join["generated_at"] = coverage_ledger.get("generated_at")

    approvals: list[str] = []
    passes_n = len(sections.get("strategy", {}).get("passes") or [])
    if passes_n:
        approvals.append(
            f"activation 升档单：{passes_n} 个策略 pass 建议入 paper 档"
            f"（weight_band={ {'floor': 0, 'current': 0.1, 'ceiling': 0.3, 'step_cap': 0.2} }）——等 Owner 批"
        )
    f_pass = len(sections.get("factor", {}).get("passes") or [])
    if f_pass:
        approvals.append(f"因子晋升门呈批：{f_pass} 个因子过 prereg 线，建议走 factor_registry 晋升流程（另行批回写）")
    approvals.append("及格线初拟全部待 Owner 校（prereg v1 内标注）")
    approvals.append("第三波立项建议：ML 模型与形态库考试（M2 卡 S=3/M=28/L=11 已落 mining/m2_exit_sector/）")

    summary = {
        "doc_type": "fexam_campaign_summary",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "batches": sections,
        "coverage_ledger_join": coverage_join,
        "approvals_pending_owner": approvals,
        "negative_result_discipline": "全部 rework/retire/缺数据结论如实入册（exam_policy §5/§6），零隐藏",
    }
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(summary, allow_unicode=True, sort_keys=False, width=120))
    _summary_md(summary, out_path.with_name("00_exam_campaign_summary_v1.md"))
    return summary


def _summary_md(summary: dict[str, Any], md_path: Path) -> None:
    lines = [
        "# 全量考试战役总册（v1，机生）",
        "",
        f"- 生成：{summary['generated_at_utc']}（scripts/backtest/fexam/campaign_report.py）",
        "",
        "| 批 | 状态 | pass | rework | retire_candidate | 总数 |",
        "|----|------|------|--------|------------------|------|",
    ]
    label = {"factor": "批1因子", "indicator": "批3指标", "strategy": "批2策略", "allocator": "批4分配器"}
    for kind in ("factor", "strategy", "indicator", "allocator"):
        sec = summary["batches"].get(kind, {})
        if sec.get("status") != "done":
            lines.append(f"| {label[kind]} | pending | - | - | - | - |")
            continue
        c = sec.get("counts", {})
        lines.append(
            f"| {label[kind]} | done | {c.get('pass', 0)} | {c.get('rework', 0)} "
            f"| {c.get('retire_candidate', 0)} | {c.get('total', 0)} |"
        )
    lines += ["", "## 建议呈批项（等 Owner）", ""]
    lines += [f"- {a}" for a in summary["approvals_pending_owner"]]
    lines += [
        "",
        "## 退役候选清单",
        "",
    ]
    for kind in ("factor", "strategy", "indicator"):
        rets = summary["batches"].get(kind, {}).get("retire_candidates") or []
        if rets:
            lines.append(f"- {label[kind]}: {', '.join(rets[:20])}{' …' if len(rets) > 20 else ''}")
    lines += ["", f"> 负结果纪律：{summary['negative_result_discipline']}"]
    from zephyr.shared.io.file_utils import safe_write_text

    md_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(md_path, "\n".join(lines) + "\n")


# ---------- 家底总表 + 四缺口单 ----------

#: L1-L4 接线级判定规则（机生，随册落盘禁口传）
WIRING_RULES = {
    "L1_data_leg": "dataset 在 data_asset_registry 且存在 produced_by_job 或 consumed_by_job（采集/消费任务在册=数据腿在跑）",
    "L2_factor_leg": "≥1 个 ch_backed 因子的 ch_backings 引用该数据集所属表（真实因子消费）",
    "L3_strategy_leg": "≥1 个 harness_examinable 策略的 backed_alpha_sources 引用消费该表的因子（策略配方引用）",
    "L4_mount": "TDM 182 节点中存在引用该数据集/源线的 node（TDM 环节映射）",
}


def build_inventory(out_path: Path, gap_path: Path) -> dict[str, Any]:
    """家底总表（八底册）+ 四张缺口单。全机生。"""
    missing: list[str] = []
    ds_reg = _load_yaml(CATALOGS / "data_asset_registry.yaml")
    ds_rows: list[dict[str, Any]] = []
    if isinstance(ds_reg, dict):
        for v in ds_reg.values():  # 顶层键随册而异——扫描首个以 dataset_id 为键的字典列表
            if isinstance(v, list) and v and isinstance(v[0], dict) and "dataset_id" in v[0]:
                ds_rows = [d for d in v if isinstance(d, dict) and d.get("dataset_id")]
                break
    if not ds_rows:
        missing.append("data_asset_registry")

    roster = _load_yaml(FEXAM_DIR / "bt_p0_roster_v1.yaml")
    if not isinstance(roster, dict):
        missing.append("bt_p0_roster")
        roster = {"factor": [], "strategy": [], "indicator": [], "allocator": []}

    tdm = _load_yaml(RUN_ROOT / "config" / "trading_decision_map.yaml")
    tdm_nodes = tdm.get("nodes", []) if isinstance(tdm, dict) else []
    if not tdm_nodes:
        missing.append("trading_decision_map")

    trial = _load_yaml(CATALOGS / "trial_ledger_registry.yaml")
    if not isinstance(trial, dict):
        missing.append("trial_ledger_registry")

    census = RUN_ROOT / "docs" / "_working" / "map_census" / "00_panorama_map_census_v1.md"
    if not census.exists():
        missing.append("map_census")

    metaq = _load_yaml(METAQ_SNAP / "registry_latest.yaml")
    metaq_n = 0
    if isinstance(metaq, dict):
        metaq_n = int(metaq.get("row_count") or len(metaq.get("questions", [])) or 0)
    else:
        missing.append("meta_question_snapshot")

    # 表→因子/策略消费投影（键=db.table 全名；backings 形如 db.table.column）
    factor_by_table: dict[str, list[str]] = {}
    for f in roster.get("factor", []):
        for b in f.get("ch_backings") or []:
            factor_by_table.setdefault(b.rsplit(".", 1)[0], []).append(f["object_id"])
    strategy_by_table: dict[str, list[str]] = {}
    for s in roster.get("strategy", []):
        for fid in s.get("backed_alpha_sources") or []:
            fentry = next((x for x in roster.get("factor", []) if x["object_id"] == fid), {})
            for b in fentry.get("ch_backings") or []:
                strategy_by_table.setdefault(b.rsplit(".", 1)[0], []).append(s["object_id"])

    rows: list[dict[str, Any]] = []
    for d in ds_rows:
        entity = str(d.get("entity_name") or d.get("name") or "")
        table = entity  # entity 形如 db.table，直接作映射键
        has_job = bool(d.get("produced_by_job") or d.get("consumed_by_jobs"))
        consumers = factor_by_table.get(table, [])
        strategy_consumers = strategy_by_table.get(table, [])
        tdm_hit = [n.get("node_id") for n in tdm_nodes if entity and entity in yaml.safe_dump(n, allow_unicode=True)]
        levels = {
            "L1_data_leg": has_job,
            "L2_factor_leg": bool(consumers),
            "L3_strategy_leg": bool(strategy_consumers),
            "L4_mount": bool(tdm_hit),
        }
        rows.append(
            {
                "dataset_id": d.get("dataset_id"),
                "entity": entity,
                "wiring": {k: bool(v) for k, v in levels.items()},
                "wiring_level_max": max([k for k, v in levels.items() if v], default="L0_orphan"),
                "factor_consumers": consumers[:8],
                "strategy_consumers": strategy_consumers[:8],
                "tdm_nodes": [t for t in tdm_hit if t][:8],
            }
        )

    # 四张缺口单（纯集合运算）
    consumed_factors: set[str] = set()
    for s in roster.get("strategy", []):
        consumed_factors.update(s.get("backed_alpha_sources") or [])
        consumed_factors.update(s.get("alpha_sources") or [])
    gap_lists = {
        "g1_data_no_factor": [
            r["dataset_id"] for r in rows if r["wiring"]["L1_data_leg"] and not r["wiring"]["L2_factor_leg"]
        ],
        "g2_factor_no_strategy": [
            f["object_id"] for f in roster.get("factor", []) if f["object_id"] not in consumed_factors
        ],
        "g3_strategy_no_exam": [
            s["object_id"] for s in roster.get("strategy", []) if s["bucket"] != "harness_examinable"
        ],
        "g4_fully_disconnected": [r["dataset_id"] for r in rows if not any(r["wiring"].values())],
    }

    counts = {
        "datasets": len(rows),
        "wiring_max": {
            lvl: sum(1 for r in rows if r["wiring_level_max"] == lvl)
            for lvl in ("L0_orphan", "L1_data_leg", "L2_factor_leg", "L3_strategy_leg", "L4_mount")
        },
        "factors_total": len(roster.get("factor", [])),
        "strategies_total": len(roster.get("strategy", [])),
        "indicators_total": len(roster.get("indicator", [])),
        "allocators_total": len(roster.get("allocator", [])),
        "tdm_nodes": len(tdm_nodes),
        "meta_questions": metaq_n,
    }
    inventory = {
        "doc_type": "matrix_inventory",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "generator": "scripts/backtest/fexam/campaign_report.py build_inventory（机生禁手填）",
        "wiring_rules": WIRING_RULES,
        "missing_sources": missing,
        "counts": counts,
        "gap_lists": gap_path.name,
        "datasets": rows,
    }
    gaps = {
        "doc_type": "matrix_gap_lists",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "rules": WIRING_RULES,
        "gap_lists": gap_lists,
        "gap_counts": {k: len(v) for k, v in gap_lists.items()},
    }
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(inventory, allow_unicode=True, sort_keys=False, width=120))
    safe_write_text(gap_path, yaml.safe_dump(gaps, allow_unicode=True, sort_keys=False, width=120))
    return {"inventory_counts": counts, "gap_counts": gaps["gap_counts"], "missing_sources": missing}


# ---------- 原问题匹配 ----------


def _resolve_qids() -> dict[str, str]:
    """PG 侧 normalize_title→q_id 解析（只读）。PG 不可达返回空表（上层如实降级）。"""
    try:
        from zephyr.governance.meta_question.meta_question_registry import (
            MetaQuestionRegistry,
            normalize_title,
        )

        reg = MetaQuestionRegistry()
        conn = reg.get_conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(SQL_METAQ_TITLES)  # SQL 集中化（NO-BARE-SQL）
            rows = cur.fetchall()
        finally:
            conn.close()
        return {normalize_title(str(r[1])): str(r[0]) for r in rows if r and r[1]}
    except Exception:  # noqa: BLE001 — PG 不可达/表缺失=降级对照表模式（ERROR_CONTRACT）
        return {}


def _extract_object_verdicts() -> dict[str, dict[str, Any]]:
    """从三本分数册抽 {object_id: verdict快照} 供逐问回填证据。"""
    out: dict[str, dict[str, Any]] = {}
    for kind, path in BOOKS.items():
        book = _load_yaml(path)
        if not isinstance(book, dict):
            continue
        for r in book.get("results", []):
            oid = r.get("object_id")
            if oid:
                out[oid] = {
                    "kind": kind,
                    "verdict": r.get("verdict"),
                    "reason": r.get("reason"),
                    "book": str(path.relative_to(RUN_ROOT)).replace("\\", "/"),
                }
    return out


def _attempt_writeback(report: dict[str, Any], session_id: str, questions: list[dict[str, Any]]) -> None:
    """严格子集回填：问题文本点名今晚分数册内具体资产ID 且 判据可机解 → claim+record。

    六查纪律：A3（判据+阈值双填充）不满足的问一律不回填，逐条留痕 defer_reason。
    全程异常降级为对照表模式（writeback_mode 字段如实反映）。
    """
    import re

    title_map = _resolve_qids()
    verdicts = _extract_object_verdicts()
    written: list[dict[str, str]] = []
    deferred: list[dict[str, str]] = []
    claimed_ops = None
    if title_map:
        try:
            from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry

            claimed_ops = MetaQuestionRegistry()
        except Exception as exc:  # noqa: BLE001
            report["writeback_mode"] = f"对照表模式（ops 初始化失败: {exc}）"
            return
    for m in report.get("matches", []):
        if not m.get("answerable_now"):
            continue
        q = m.get("_q") or {}
        title = str(q.get("title") or "")
        q_id = title_map.get(_norm_title_safe(title))
        if not q_id:
            deferred.append({"q_title": title[:60], "reason": "title→PQ解析未命中（快照与PG不同步或非在册问）"})
            continue
        ids = set(re.findall(r"(?:FCT|IND|STR)-[A-Z]+-\d+", title))
        hit = {i: verdicts[i] for i in ids if i in verdicts}
        if not hit:
            deferred.append(
                {
                    "q_id": q_id,
                    "reason": "题面未点名分数册内具体资产ID，判据无法无条件机解（A3不满足）——逐问工程见施工队列M-9",
                }
            )
            continue
        try:
            claimed_ops.claim(q_id, actor=session_id, lease_hours=24)
            claimed_ops.record_exam_result(
                q_id,
                {
                    "outcome": "answered",
                    "exam_ref": f"fexam-20261006/{next(iter(hit.values()))['book']}",
                    "conclusion": {oid: v["verdict"] for oid, v in hit.items()},
                    "confidence": {"level": None, "note": "批次三态verdict直证，无置信区间口径"},
                    "data_window": {"start": "2025-10-09", "end": "2026-09-30"},
                    "pit_assertion": True,
                    "evidence": [v["book"] for v in hit.values()],
                },
                actor=session_id,
            )
            written.append({"q_id": q_id, "objects": sorted(hit)})
        except Exception as exc:  # noqa: BLE001 — 单问失败不阻断（认领冲突/状态机拒绝均如实）
            deferred.append({"q_id": q_id, "reason": f"writeback_error: {type(exc).__name__}: {exc}"[:180]})
    report["writeback_written"] = written
    report["writeback_deferred"] = deferred
    report["writeback_mode"] = (
        f"严格子集回写 {len(written)} 件 / 延迟 {len(deferred)} 件（deferred 逐条留痕）"
        if claimed_ops
        else "对照表模式（PG解析不可达）"
    )


def _norm_title_safe(title: str) -> str:
    try:
        from zephyr.governance.meta_question.meta_question_registry import normalize_title

        return normalize_title(title)
    except Exception:  # noqa: BLE001
        return title.strip().lower()


def build_metaq_matching(out_path: Path, *, writeback: bool = False, session_id: str = "") -> dict[str, Any]:
    """原问题（meta_question 283 问）×今晚考试产物 匹配表。

    回填纪律（13_exam_backfill_loop_design §1）：只走 writeback API 且六查合规；
    writeback=False 时只出对照表（回填 Owner 醒后过目模式）。
    """
    questions: list[dict[str, Any]] = []
    for snap in ("question_batch_w6.yaml", "registry_latest.yaml"):
        doc = _load_yaml(METAQ_SNAP / snap)
        if isinstance(doc, dict):
            for q in doc.get("questions", []) or []:
                if isinstance(q, dict) and q.get("title"):
                    questions.append(dict(q, _snapshot=snap))
            if questions:
                break

    # 今晚可答事实面（证据引用=分数册路径，六查 A6 可核）
    facts: list[dict[str, str]] = []
    for kind, path in BOOKS.items():
        if path.exists():
            facts.append({"artifact": path.name, "path": str(path.relative_to(RUN_ROOT)).replace("\\", "/")})

    matches: list[dict[str, Any]] = []
    for q in questions:
        text = yaml.safe_dump(q, allow_unicode=True)
        hit_kinds = [k for k, p in BOOKS.items() if p.exists() and _q_relevant(q, k, text)]
        matches.append(
            {
                "q_title": q["title"][:80],
                "layer": q.get("layer"),
                "frequency": q.get("frequency"),
                "exam_plan_criterion": (q.get("exam_plan") or {}).get("criterion"),
                "matched_batches": hit_kinds,
                "answerable_now": bool(hit_kinds) and _q_infra_examinable(q, text),
                "evidence_candidates": [f["path"] for f in facts if hit_kinds],
                "_q": q,
            }
        )

    n_answerable = sum(1 for m in matches if m["answerable_now"])
    report = {
        "doc_type": "metaq_matching",
        "version": "v1",
        "generated_at_utc": str(now_utc()),
        "questions_total": len(questions),
        "answerable_now": n_answerable,
        "writeback_mode": "对照表模式（未启用回填）",
        "matches": matches,
        "note": "L0 治理元问题（表自检/流程自检类）本就不由资产考试回答——answerable_now 只收资产面问题，"
        "治理面问题走 run_exam_loop --reconcile 常规通道，非遗漏",
    }
    if writeback:
        _attempt_writeback(report, session_id or "st-matrix-20261006", questions)
    for m in report["matches"]:
        m.pop("_q", None)  # 内存字段不落盘
    from zephyr.shared.io.file_utils import safe_write_text

    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(out_path, yaml.safe_dump(report, allow_unicode=True, sort_keys=False, width=120))
    return report


def _q_relevant(q: dict[str, Any], kind: str, text: str) -> bool:
    """关键词匹配：问题文本涉及该批对象面（因子/指标/策略/分配器）。"""
    kws = {
        "factor": ("因子", "IC", "ICIR", "FCT", "alpha"),
        "indicator": ("指标", "IND", "技术指标"),
        "strategy": ("策略", "回测", "夏普", "Sharpe", "STR", "整装"),
        "allocator": ("分配", "权重", "仓位", "资金配置", "RK-08", "PA-015", "SIG-131"),
    }[kind]
    return any(k in text for k in kws)


def _q_infra_examinable(q: dict[str, Any], text: str) -> bool:
    """L0 治理元问题（表自检/流程自检）不由资产考试回答。"""
    infra_kws = ("拒绝率", "重复对占比", "入库闸", "审计", "快照", "台账", "token", "登记")
    return not any(k in text for k in infra_kws)
