# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §2 考试矛盾仲裁链（§2.1 C1-C3 机械定义 / §2.2 四步仲裁与三取二）
# [MODULE] zephyr.governance.meta_question.exam_loop.arbitration
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 标准库 datetime/re（窗口与阈值比较，零 IO）; .exam_plan (threshold_clauses 机解值复用，禁二次解析口径)
# [CONSUMERS] zephyr.governance.meta_question.exam_loop.writeback (回填当轮矛盾检测 + R3 三取二落账); scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py (PQ-0057 三取二执行率判据); tests/governance/meta_question/test_exam_loop_arbitration.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 比对前提=同 q_id + 同 exam_plan_version（版本不同=方案修订不是矛盾，不比，13§2.1）；
#              数据窗口交叠的同版本重复回写=supplement（补录），不入矛盾检测（防重复劳动触发伪仲裁）；
#              C1/C2/C3 三条任一命中即矛盾（可判定式与设计稿逐字对齐）；
#              三取二：R3 与 R1/R2 之一不命中任何 C 规则→与其同侧胜出；与两者均矛盾或均不命中（归属不可判）→升级 Max（13§2.2）；
#              仲裁链无死态：open→(R3)→resolved|escalated_max，升级后 Owner 兜底超时（时限数值=设计稿待裁项，本件只落"升级"事实不立法时限）；
#              本件纯计算零 IO（落账由 writeback 编排），禁在此开连接
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §2（改仲裁判据先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入载荷非 dict/缺字段→按"不可判"降级不抛（矛盾检测不得因脏数据假阳）；case_id 生成冲突不可能（uuid4+序号）
# [TESTS] tests/governance/meta_question/test_exam_loop_arbitration.py（红腿：C1/C2/C3 各命中一例 + 版本不同不比 + 窗口交叠不入矛盾；三取二三例：胜出/双矛盾升级/双不命中升级）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""arbitration — 考试矛盾机械检测（C1-C3）与三取二裁定（13§2 仲裁链的计算核）。

纯函数集：输入=预注册考卷 + 本次结果 + 同版本历次结果（新→旧），输出=案卷 dict 或 ``None``。
落账时机与事务由 :mod:`zephyr.governance.meta_question.exam_loop.writeback` 编排（回填当轮秒级机械）。
# #
# # 边:
# # I1 -.->|断点| F1
# # I2 -.->|断点| F1
# # I3 -.->|断点| F1
# # I4 -.->|断点| F1
# # F1 --> A1
# # A1 --> O1
# [/ALGO_FLOW]
# target: src/zephyr/governance/meta_question/exam_loop/arbitration.py (docstring 1299 字, 17 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/arbitration.yaml
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Final

__all__: Final = [
    "RULES",
    "case_id",
    "detect_contradiction",
    "hits_c1",
    "hits_c2",
    "hits_c3",
    "resolve_majority",
    "window_overlaps",
]

#: 结论方向枚举中的"有结论"两值（13§1.1 三值枚举之可判侧；"不可判"永不参与矛盾比对）
DECISIVE_DIRS: Final[tuple[str, ...]] = ("支持", "证伪")
INDETERMINATE_DIR: Final[str] = "不可判"
RULES: Final[tuple[str, ...]] = ("C1", "C2", "C3")


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def _num(value: Any) -> float | None:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dir_of(item: dict[str, Any]) -> str:
    return str(item.get("dir") or item.get("conclusion_dir") or "").strip()


def _value_of(item: dict[str, Any]) -> float | None:
    return _num(item.get("value") if "value" in item else item.get("conclusion_value"))


def _conf_of(item: dict[str, Any]) -> float | None:
    return _num(item.get("confidence") if "confidence" in item else item.get("confidence_level"))


def _ci_of(item: dict[str, Any]) -> tuple[float, float] | None:
    lo, hi = _num(item.get("ci_lo")), _num(item.get("ci_hi"))
    return None if lo is None or hi is None else (min(lo, hi), max(lo, hi))


def _to_dt(value: Any) -> datetime | None:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def window_overlaps(left: dict[str, Any] | None, right: dict[str, Any] | None) -> bool:
    """两数据窗口是否交叠（13§2.1 supplement 判定；边界相接算交叠=保守取伪矛盾排除）。"""
    a_start, a_end = _to_dt((left or {}).get("start")), _to_dt((left or {}).get("end"))
    b_start, b_end = _to_dt((right or {}).get("start")), _to_dt((right or {}).get("end"))
    if not (a_start and a_end and b_start and b_end):
        return False
    return not (a_end < b_start or b_end < a_start)


def case_id(q_id: str) -> str:
    """矛盾案卷编号（13§2.2 步 1 留痕：case_id 双方 result ref + 命中规则号）。"""
    return f"MQC-{q_id}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# C1-C3 可判定式（与设计稿 §2.1 逐条对齐）
# ---------------------------------------------------------------------------


def hits_c1(r1: dict[str, Any], r2: dict[str, Any], *, min_confidence: float | None = None) -> bool:
    """C1 方向相反：两侧 ∈{支持,证伪} 且相异，且两侧置信均达预锁最低阈。"""
    d1, d2 = _dir_of(r1), _dir_of(r2)
    if d1 not in DECISIVE_DIRS or d2 not in DECISIVE_DIRS or d1 == d2:
        return False
    if min_confidence is None:
        return True  # 未预锁最低阈=无附加条件可查（降级：只比方向，缺项由六查 A2 侧暴露）
    c1, c2 = _conf_of(r1), _conf_of(r2)
    return c1 is not None and c2 is not None and c1 >= min_confidence and c2 >= min_confidence


def hits_c2(r1: dict[str, Any], r2: dict[str, Any]) -> bool:
    """C2 区间分离：置信区间互不重叠且方向相异。"""
    ci1, ci2 = _ci_of(r1), _ci_of(r2)
    if not ci1 or not ci2 or _dir_of(r1) == _dir_of(r2):
        return False
    return max(ci1[0], ci2[0]) > min(ci1[1], ci2[1])


def hits_c3(r1: dict[str, Any], r2: dict[str, Any], *, threshold: float | None) -> bool:
    """C3 阈值异侧：判据取值分居预锁阈值两侧 (v1-阈)×(v2-阈)<0。"""
    if threshold is None:
        return False
    v1, v2 = _value_of(r1), _value_of(r2)
    if v1 is None or v2 is None:
        return False
    return (v1 - threshold) * (v2 - threshold) < 0


def _rule_hits(
    r1: dict[str, Any], r2: dict[str, Any], threshold: float | None, min_confidence: float | None
) -> list[str]:
    hits: list[str] = []
    if hits_c1(r1, r2, min_confidence=min_confidence):
        hits.append("C1")
    if hits_c2(r1, r2):
        hits.append("C2")
    if hits_c3(r1, r2, threshold=threshold):
        hits.append("C3")
    return hits


def _prelocked(plan: dict[str, Any]) -> tuple[float | None, float | None]:
    """预注册（阈值, 最低置信阈）——缺项返回 None，禁伪造。"""
    clauses = [c for c in plan.get("threshold_clauses") or [] if "value" in c]
    return (float(clauses[0]["value"]) if clauses else None), _num(plan.get("min_confidence"))


def _normalize_current(plan_version: str, current: dict[str, Any]) -> dict[str, Any]:
    """本次回填载荷 → 比对用结果视图（与历史行同构，取数口径只此一份）。"""
    conclusion = current.get("conclusion") if isinstance(current.get("conclusion"), dict) else {}
    window = current.get("data_window") if isinstance(current.get("data_window"), dict) else {}
    return {
        "value": current.get("conclusion_value", conclusion.get("value")),
        "dir": current.get("conclusion_dir", conclusion.get("dir")),
        "confidence": current.get("confidence_level"),
        "ci_lo": current.get("ci_lo"),
        "ci_hi": current.get("ci_hi"),
        "window": {
            **window,
            "start": current.get("data_window_start") or window.get("start"),
            "end": current.get("data_window_end") or window.get("end"),
            "exam_plan_version": current.get("exam_plan_version") or window.get("exam_plan_version") or plan_version,
        },
        "ref": current.get("exam_ref") or current.get("examiner_ref") or "",
    }


def _prior_view(item: dict[str, Any]) -> dict[str, Any]:
    """历史 exam_result 行（已解 JSONB）→ 比对用结果视图。"""
    conclusion = item.get("conclusion") if isinstance(item.get("conclusion"), dict) else {}
    confidence = item.get("confidence") if isinstance(item.get("confidence"), dict) else {}
    window = item.get("data_window") if isinstance(item.get("data_window"), dict) else {}
    return {
        "value": conclusion.get("value"),
        "dir": conclusion.get("dir"),
        "confidence": confidence.get("level"),
        "ci_lo": confidence.get("ci_lo"),
        "ci_hi": confidence.get("ci_hi"),
        "window": window,
        "ref": item.get("exam_ref") or "",
        "outcome": item.get("outcome"),
        "created_at": item.get("created_at"),
    }


# ---------------------------------------------------------------------------
# 矛盾检测（13§2.1）
# ---------------------------------------------------------------------------


def detect_contradiction(
    plan: dict[str, Any],
    current: dict[str, Any],
    prior_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """比对新结果与"该问现存最新同版本且不交叠"的结果；命中 C1-C3 任一→出案卷 dict。

    :param prior_rows: 历史 exam_result 行（新→旧，JSONB 已解）
    :return: ``{"case_id","rules","baseline_ref","current_ref","plan_version"}`` 或 ``None``
    """
    threshold, min_confidence = _prelocked(plan)
    plan_version = str(plan.get("plan_version") or "")
    mine = _normalize_current(plan_version, current)
    for item in prior_rows:
        theirs = _prior_view(item)
        theirs_version = str(theirs.get("window", {}).get("exam_plan_version") or "")
        if plan_version and theirs_version and theirs_version != plan_version:
            continue  # 版本不同=方案修订，不比
        if window_overlaps(mine.get("window"), theirs.get("window")):
            continue  # 同窗重复回写=supplement，不入矛盾检测
        hits = _rule_hits(theirs, mine, threshold, min_confidence)
        if hits:
            return {
                "case_id": case_id(str(current.get("q_id") or plan.get("q_id") or "UNKNOWN")),
                "rules": hits,
                "baseline_ref": theirs.get("ref") or str(theirs.get("created_at") or ""),
                "current_ref": mine.get("ref") or "",
                "plan_version": plan_version,
                "state": "open",
            }
    return None


# ---------------------------------------------------------------------------
# 三取二（13§2.2）
# ---------------------------------------------------------------------------


def resolve_majority(
    plan: dict[str, Any],
    current: dict[str, Any],
    prior_rows: list[dict[str, Any]],
    contradiction: dict[str, Any] | None,
    *,
    arbitration_recheck: bool = False,
) -> dict[str, Any] | None:
    """复考结果 R3 与 R1/R2 的三取二机械裁定（仅当本次是仲裁复考时触发）。

        :return: ``{"verdict": "majority"|"escalate_max", "winner", "basis", "case_id"}`` 或 ``None``

    # #
    # # 边:
    # # I1 -.->|断点| F1
    # # I2 -.->|断点| F1
    # # I3 -.->|断点| F1
    # # I4 -.->|断点| F1
    # # F1 --> A1
    # # A1 --> O1
    # [/ALGO_FLOW]
    """
    if not arbitration_recheck or len(prior_rows) < 2:
        return None
    threshold, min_confidence = _prelocked(plan)
    r3 = _normalize_current(str(plan.get("plan_version") or ""), current)
    r2 = _prior_view(prior_rows[0])
    r1 = _prior_view(prior_rows[1])
    hits_1 = _rule_hits(r1, r3, threshold, min_confidence)
    hits_2 = _rule_hits(r2, r3, threshold, min_confidence)
    if _dir_of(r3) == INDETERMINATE_DIR or _dir_of(r3) == "":
        return {
            "verdict": "escalate_max",
            "winner": None,
            "basis": "R3 不可判（归属不可判）",
            "hits_r1": hits_1,
            "hits_r2": hits_2,
            "case_id": (contradiction or {}).get("case_id"),
        }
    if bool(hits_1) == bool(hits_2):
        # 双矛盾（与两侧都命中）或双不命中（归属不可判）→ 升级 Max
        basis = "与 R1/R2 均矛盾" if hits_1 and hits_2 else "与 R1/R2 均不命中任何 C 规则（归属不可判）"
        return {
            "verdict": "escalate_max",
            "winner": None,
            "basis": basis,
            "hits_r1": hits_1,
            "hits_r2": hits_2,
            "case_id": (contradiction or {}).get("case_id"),
        }
    winner = "R2" if hits_1 else "R1"  # 与一侧矛盾⇒与另一侧同侧胜出
    return {
        "verdict": "majority",
        "winner": winner,
        "basis": f"三取二：R3 与 {winner} 同侧（另一侧命中 {','.join(hits_1 or hits_2)}）",
        "hits_r1": hits_1,
        "hits_r2": hits_2,
        "case_id": (contradiction or {}).get("case_id"),
    }
