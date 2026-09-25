# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_annual_review
# [MODULE] zephyr.ai_layer.redline.annual_review
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
#                （输入全部注入：KillSwitch 事件/gate 审计/risk_tier/era/freshness 各真源方供给）
# [CONSUMERS] OBJ_R 四步流水线（立案包 consumption 面：提案→治理立案→Owner 修标→重考历史）;
#             ruling_registry（立案后回填关联裁定号）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 负面清单年审挂 OBJ_R 标准流水线原样（DESIGN §6）：AI 年审报告提案→治理立案→
#              Owner 修标→重考历史（新清单对历史拦截集重放，误拦率不升才准换）；
#              红线语义变更零直改——本模块只产立案包草案（恒 status=draft），不修清单不修语义；
#              三个探测口：①人工紧急叫停/KillSwitch 事件同类≥2 而清单未列=事实红线候选；
#              ②near_miss warn 高频（≥阈值/季）=判据细则化候选；③条目连续 4 季零触发=
#              退役审计候选（净删=Owner 门位，宪法 §4.2 对齐）；
#              年审固定核对项四件（DESIGN §6）：实盘键命名合规/protected_paths 一致性/
#              HMAC era 覆盖完整性/禁删清单生成器 freshness；
#              墓碑标记一致性核对=report-only（不新建机制，档 B 纪律核实）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §6
# [STABILITY] new
# [SAFETY] L（纯聚合+立案包草案落参数指定目录；零裁决零清单直改）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判据为纯函数（输入形状非法抛 AnnualReviewInputError，fail-closed）；
#                  freshness 的 manifest 缺文件 → fresh=False+注记（不炸不虚构）；
#                  立案包缺 proposal_id 拒落盘（同 standard_checkup 先例）
# [TESTS] tests/ai_layer/redline/test_annual_review.py（三探测口边界：同类 2 次候选/
#         1 次不候选/清单已列不候选/warn 高频阈值/零触发退役/固定核对项四件正反/
#         墓碑一致性 report-only/立案包 schema+draft+OBJ_R 流水线锚）
"""annual_review — 负面清单年审流水线挂接（OBJ_S 施工项 S8，DESIGN §6）。

产出 ``negative_list_annual_review`` 立案包草案（YAML，恒 status=draft）→
OBJ_R 四步流水线原样：AI 年审报告提案→治理立案→Owner 修标→重考历史。

三个探测口（年审输入）+ 四个固定核对项 + 墓碑标记一致性核对（report-only）。
净删=Owner 门位（宪法 §4.2），本模块自动化的是提案与证据，不是裁决。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_R_rules_standards" / "proposals"
FACT_REDLINE_MIN_EVENTS: Final = 2
DEFAULT_WARN_THRESHOLD_PER_QUARTER: Final = 10
DEFAULT_RETIRE_QUARTERS: Final = 4
DEFAULT_FRESHNESS_MAX_AGE_DAYS: Final = 35
STATUS_DRAFT: Final = "draft"
OBJ_R_PIPELINE_STEPS: Final[tuple[str, ...]] = (
    "AI 年审报告提案",
    "治理立案",
    "Owner 修标",
    "重考历史（新清单对历史拦截集重放，误拦率不升才准换）",
)

REAL_KEY_NAME_MARKERS: Final[tuple[str, ...]] = ("_REAL_", "_LIVE_")
REAL_KEY_PREFIXES: Final[tuple[str, ...]] = ("QMT" "_REAL_",)


class AnnualReviewInputError(RuntimeError):
    """年审输入形状非法（fail-closed）。"""


# ────────────────── 探测口 ──────────────────


def fact_redline_candidates(
    emergency_stops: Sequence[Mapping[str, Any]],
    listed_patterns: Sequence[str],
    *,
    min_events: int = FACT_REDLINE_MIN_EVENTS,
) -> list[dict[str, Any]]:
    """探测口①：人工紧急叫停/KillSwitch 事件同类≥min_events 而负面清单未列 → 事实红线候选。"""
    counts: dict[str, int] = {}
    for event in emergency_stops:
        category = str(event.get("category", "")).strip()
        if category:
            counts[category] = counts.get(category, 0) + 1
    listed = {str(item) for item in listed_patterns}
    return [
        {"category": category, "events": count, "reason": "应有而未列（同类人工叫停≥2 次）"}
        for category, count in sorted(counts.items())
        if count >= min_events and category not in listed
    ]


def detail_refinement_candidates(
    near_miss_warns: Mapping[str, int],
    *,
    threshold_per_quarter: int = DEFAULT_WARN_THRESHOLD_PER_QUARTER,
) -> list[dict[str, Any]]:
    """探测口②：near_miss warn 高频模式（≥阈值/季）→ 判据细则化候选。"""
    return [
        {"rule_id": rule_id, "warns": count, "threshold_per_quarter": threshold_per_quarter}
        for rule_id, count in sorted(near_miss_warns.items())
        if count >= threshold_per_quarter
    ]


def retire_candidates(
    rule_triggers_by_quarter: Mapping[str, Sequence[int]],
    *,
    quarters: int = DEFAULT_RETIRE_QUARTERS,
) -> list[dict[str, Any]]:
    """探测口③：条目机检连续 quarters 个季度零触发 → 退役审计候选（净删=Owner 门位）。

    输入形状 {rule_id: [近 Q 个季度计数...]}; 样本不足 quarters 的条目不判（不虚构）。
    """
    candidates: list[dict[str, Any]] = []
    for rule_id, counts in sorted(rule_triggers_by_quarter.items()):
        if len(counts) < quarters:
            continue
        if all(count == 0 for count in counts[-quarters:]):
            candidates.append({"rule_id": rule_id, "quarters_zero": quarters})
    return candidates


# ────────────────── 年审固定核对项 ──────────────────


def check_real_key_naming(registry_keys: Sequence[Mapping[str, Any]]) -> list[str]:
    """固定核对项①（NL-2）：实盘 credential 键必须带 _REAL_/_LIVE_ 命名（键名-only，零值）。"""
    violations: list[str] = []
    for record in registry_keys:
        key = str(record.get("key", ""))
        if not record.get("is_live"):
            continue
        named = any(marker in key for marker in REAL_KEY_NAME_MARKERS) or key.startswith(REAL_KEY_PREFIXES)
        if not named:
            violations.append(key)
    return violations


def check_protected_paths_alignment(
    protected_paths: Sequence[str],
    constitutional_baseline: Sequence[str],
) -> dict[str, list[str]]:
    """固定核对项②（NL-3）：protected_paths 与宪法/规则真源基线一致性 → {missing, extra}。"""
    current = {str(item) for item in protected_paths}
    baseline = {str(item) for item in constitutional_baseline}
    return {
        "missing": sorted(baseline - current),
        "extra": sorted(current - baseline),
    }


def check_hmac_era_coverage(
    eras_valid_from: Sequence[str],
    first_record_ts: str,
) -> list[str]:
    """固定核对项③（NL-4）：HMAC era 覆盖完整性——最早分期必须覆盖链首记录时刻。"""
    issues: list[str] = []
    if not eras_valid_from:
        return ["eras 空：无任何分期注册（审计链验证将 fail-closed）"]
    try:
        earliest = min(datetime.fromisoformat(raw) for raw in eras_valid_from)
        first = datetime.fromisoformat(first_record_ts)
    except (ValueError, TypeError):
        return ["era/记录时刻不可解析（输入形状非法）"]
    if earliest > first:
        issues.append(
            f"era 覆盖缺口：最早分期 {earliest.isoformat()} 晚于链首记录 {first.isoformat()}"
        )
    return issues


def check_manifest_freshness(
    manifest_path: Path,
    *,
    max_age_days: float = DEFAULT_FRESHNESS_MAX_AGE_DAYS,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """固定核对项④（NL-6）：禁删清单生成器 freshness（超龄=stale 候选立案再生）。"""
    moment = as_of or now_utc()
    if not manifest_path.exists():
        return {"fresh": False, "note": f"清单缺席（生成器未跑或被删）: {manifest_path.as_posix()}"}
    generated_at = None
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            generated_at = data.get("generated_at")
    except (OSError, yaml.YAMLError):
        return {"fresh": False, "note": "清单不可读/不可解析（视作 stale）"}
    if not isinstance(generated_at, str):
        return {"fresh": False, "note": "清单缺 generated_at 字段（视作 stale）"}
    try:
        age_days = (moment - datetime.fromisoformat(generated_at)).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return {"fresh": False, "note": f"generated_at 不可解析: {generated_at}"}
    return {"fresh": age_days <= max_age_days, "age_days": round(age_days, 2), "max_age_days": max_age_days}


def tombstone_consistency(domain_fields: Mapping[str, str | None]) -> dict[str, Any]:
    """S8 顺带核对：各域 deprecation 字段一致性（report-only，不新建机制）。"""
    named = {domain: name for domain, name in domain_fields.items() if name}
    distinct = sorted({name for name in named.values() if name})
    return {
        "domains_reported": len(domain_fields),
        "distinct_field_names": distinct,
        "domains_missing": sorted(domain for domain, name in domain_fields.items() if not name),
        "consistent": len(distinct) <= 1 and not any(not name for name in domain_fields.values()),
    }


# ────────────────── 立案包（OBJ_R 流水线挂接）─────────────────


@dataclass(frozen=True)
class AnnualReviewInput:
    """年审输入载荷（三探测口+四固定核对项+墓碑核对；全部由真源方供给注入）。"""

    review_date: str
    emergency_stops: tuple[dict[str, Any], ...] = ()
    listed_patterns: tuple[str, ...] = ()
    near_miss_warns: Mapping[str, int] = field(default_factory=dict)
    rule_triggers_by_quarter: Mapping[str, tuple[int, ...]] = field(default_factory=dict)
    fixed_checklist: dict[str, Any] = field(default_factory=dict)
    tombstone: dict[str, Any] = field(default_factory=dict)


def build_annual_review_case(annual: AnnualReviewInput, *, proposal_id: str) -> dict[str, Any]:
    """组装 negative_list_annual_review 立案包（恒 status=draft；语义变更零直改）。"""
    if not proposal_id.strip():
        raise AnnualReviewInputError("立案包缺 proposal_id，拒绝组装（fail-closed）")
    return {
        "proposal_id": proposal_id,
        "proposal_type": "negative_list_annual_review",
        "date": annual.review_date,
        "status": STATUS_DRAFT,
        "obj_r_pipeline": {
            "steps": list(OBJ_R_PIPELINE_STEPS),
            "ruling_registry_ref": "",
            "note": "立案后由治理立案环节回填 ruling_registry 关联裁定号（RULE-RULING）",
        },
        "probe_fact_redlines": fact_redline_candidates(annual.emergency_stops, annual.listed_patterns),
        "probe_detail_refinements": detail_refinement_candidates(annual.near_miss_warns),
        "probe_retirements": retire_candidates(annual.rule_triggers_by_quarter),
        "fixed_checklist": dict(annual.fixed_checklist),
        "tombstone_consistency": dict(annual.tombstone),
        "replay_promise": "清单 v(n+1) 对历史拦截集重放，误拦率不升才准换（重考历史一票否决）",
    }


def write_case(case: dict[str, Any], out_dir: Path) -> Path:
    """立案包落盘 `<proposal_id>.yaml`（缺 proposal_id 拒落盘，standard_checkup 先例同款）。"""
    proposal_id = str(case.get("proposal_id", "")).strip()
    if not proposal_id:
        raise AnnualReviewInputError("立案包缺 proposal_id，拒绝落盘（fail-closed）")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{proposal_id}.yaml"
    out_path.write_text(yaml.safe_dump(case, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return out_path
