# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.executor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (CompareCheckResult/RefuseExam/VenueUnavailable);
#                zephyr.ai_layer.comparator.experiment_store (ComparisonExperimentRecord/criteria_hash/render_criteria_ref);
#                zephyr.shared.utils.time_utils (parse_iso)
# [CONSUMERS] zephyr.ai_layer.comparator.venue_* (claim_exam 领考入口);
#             L5 工单生成器（criteria_ref 机检，设计预留）；裁定卡消费方=L5/L6 呈现件（设计预留）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 三锁机检全 fail-closed（会话互斥/时序锁/哈希锁任一不过=RefuseExam 聚合拒考，DESIGN §2.6）；
#              裁定卡必须由 experiment 卡登记的 evaluator_session 签发（运动员不兼任裁判）；
#              fairness 未检=拒考（禁跳过公平性直接开考）；时间戳一律 tz-aware（naive 拒收）；
#              机检与流转全部纯函数（时间可注入，零 now_utc 依赖——本模块不取当前时间）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.2/§2.3/§2.6（机检语义真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 时间戳缺失/畸形/naive→计入拒考 reasons（不抛裸异常不炸批）；
#                  criteria_ref 格式不合规→ValueError；非 evaluator 会话签发裁定卡→ValueError；
#                  未知考场/考场不可达→ValueError/VenueUnavailable（fail-closed 拒考）
# [TESTS] tests/ai_layer/comparator/test_executor.py（会话互斥正反/时序三序正反+naive 拒收/
#         哈希锁正反+DB 外篡改检出/公平性未检拒考/裁定卡签发权校验/锦标赛截断全枚举）
# [TTL] permanent
"""executor — L4 对比执行器：领考、三锁机检、锦标赛截断、统一裁定卡产出。

设计真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md`` §2.3 锁定机制 + §2.6 评估者
独立性机检（前五道中的前三道在本件：会话互斥/时序锁/哈希锁）+ §2.1 锦标赛制式（D-L4-02：
同批 N≥5 按 IS 排名取前 K 进 OOS，2 轮固定不加赛）。

职责边界：本件是**协议层**——不实现任何考尺（D-L4-01），开考=调用考场适配器（venue_*，
薄封装转调既有件）；裁定卡只是证据，不构成任何上线/转正动作（考场边界声明）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final, Mapping, Sequence

from zephyr.ai_layer.comparator import CompareCheckResult, RefuseExam, VENUE_IDS, VenueUnavailable
from zephyr.ai_layer.comparator.experiment_store import (
    ComparisonExperimentRecord,
    criteria_hash,
    render_criteria_ref,
)
from zephyr.shared.utils.time_utils import parse_iso

__all__: Final = [
    "ComparePreflightReport",
    "VerdictCard",
    "VerdictRuling",
    "check_hash_lock",
    "check_session_mutuality",
    "check_time_lock",
    "claim_exam",
    "issue_verdict_card",
    "parse_criteria_ref",
    "run_preflight",
    "shortlist_top_k",
    "verify_criteria_integrity",
]

SESSIONS_EQUAL_REASON: Final = "session_mutuality_violation:contractor==evaluator"


def _as_utc(value: Any, field_name: str) -> datetime:
    """时间戳归一：ISO 字符串或 aware datetime → datetime；缺失/畸形/naive 一律 ValueError。"""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = parse_iso(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"time_lock_malformed:{field_name}({exc})") from exc
    else:
        raise ValueError(f"time_lock_missing:{field_name}")
    if parsed.tzinfo is None:
        raise ValueError(f"time_lock_naive_rejected:{field_name}")
    return parsed


def check_session_mutuality(contractor_session: str, evaluator_session: str) -> CompareCheckResult:
    """机检①会话互斥（DESIGN §2.6-1）：contractor（施工方）≠ evaluator（出卷+裁定方）。"""
    passed = bool(contractor_session) and bool(evaluator_session) and (
        contractor_session != evaluator_session
    )
    reason = "ok" if passed else SESSIONS_EQUAL_REASON
    return CompareCheckResult(name="session_mutuality", passed=passed, reason=reason)


def check_time_lock(
    frozen_at: Any,
    dispatched_at: Any,
    first_commit_at: Any,
) -> CompareCheckResult:
    """机检③时序锁（DESIGN §2.6-3）：frozen_at < dispatched_at < first_commit_at，倒挂=拒绝。"""
    try:
        frozen = _as_utc(frozen_at, "frozen_at")
        dispatched = _as_utc(dispatched_at, "dispatched_at")
        first_commit = _as_utc(first_commit_at, "first_commit_at")
    except ValueError as exc:
        return CompareCheckResult(name="time_lock", passed=False, reason=str(exc))
    if not (frozen < dispatched < first_commit):
        why = (
            f"time_lock_inverted:frozen={frozen.isoformat()},"
            f"dispatched={dispatched.isoformat()},first_commit={first_commit.isoformat()}"
        )
        return CompareCheckResult(name="time_lock", passed=False, reason=why)
    return CompareCheckResult(name="time_lock", passed=True)


def check_hash_lock(expected_hash: str, actual_hash: str) -> CompareCheckResult:
    """机检④哈希锁（DESIGN §2.3-3）：开考前重算比对，不匹配=拒绝执行（防 DB 外篡改）。"""
    passed = bool(expected_hash) and expected_hash == actual_hash
    return CompareCheckResult(
        name="hash_lock", passed=passed, reason="ok" if passed else "hash_mismatch"
    )


def verify_criteria_integrity(criteria_yaml: str, recorded_hash: str) -> CompareCheckResult:
    """卡内一致性：对 criteria_yaml 文本重算 sha256 并与登记的 criteria_hash 比对。"""
    recomputed = criteria_hash(criteria_yaml)
    return check_hash_lock(recorded_hash, recomputed)


def parse_criteria_ref(criteria_ref: str) -> tuple[str, str]:
    """任务书锚点 `<experiment_id>#<hash>` → (experiment_id, hash)（DESIGN §2.3-1）。"""
    if "#" not in (criteria_ref or ""):
        raise ValueError(f"criteria_ref 缺 hash 锚点:{criteria_ref!r}")
    experiment_id, _, digest = criteria_ref.partition("#")
    return experiment_id, render_criteria_ref(experiment_id, digest).partition("#")[2]


def shortlist_top_k(
    items: Sequence[Mapping[str, Any]],
    k: int,
    trigger_n: int,
    score_key: str = "is_score",
) -> list[Mapping[str, Any]]:
    """锦标赛截断（D-L4-02 纯函数）：同批 N≥trigger_n 时按 score_key 降序取前 K，N 不足全保留。

    排序稳定（同分保持原序），K/trigger_n 来自常量层（config/comparison_policy.yaml）。
    """
    if len(items) < trigger_n:
        return list(items)
    ranked = sorted(items, key=lambda item: float(item.get(score_key) or 0.0), reverse=True)
    return ranked[: max(int(k), 0)]


@dataclass(frozen=True)
class ComparePreflightReport:
    """领考预检报告：全部机检通过才许开考（fail-closed，绝不部分通过）。"""

    passed: bool
    checks: tuple[CompareCheckResult, ...] = ()
    reasons: tuple[str, ...] = ()

    @classmethod
    def assemble(cls, checks: Sequence[CompareCheckResult]) -> "ComparePreflightReport":
        """聚合机检清单 → 报告（任一不过即 passed=False 并收拢 reasons）。"""
        reasons = tuple(c.reason for c in checks if not c.passed)
        return cls(passed=not reasons, checks=tuple(checks), reasons=reasons)

    def ensure_pass(self) -> "ComparePreflightReport":
        """fail-closed 出口：未全过 → RefuseExam（含全部 reason）。"""
        if not self.passed:
            raise RefuseExam(list(self.reasons))
        return self


def run_preflight(
    record: ComparisonExperimentRecord,
    *,
    task_criteria_ref: str | None = None,
    fairness_passed: bool | None = None,
    dispatched_at: Any | None = None,
    first_commit_at: Any | None = None,
) -> ComparePreflightReport:
    """领考预检（DESIGN §2.2+§2.3+§2.6 前三道机检+公平性闸，全过才开考）。

    :param record: 实验卡（frozen 态）
    :param task_criteria_ref: 任务书 criteria_ref 锚点（缺=拒考：时序锁要求 hash 先进任务书）
    :param fairness_passed: 公平性对齐器结论（None=未检=拒考，fail-closed）
    :param dispatched_at: 任务书派发时间（时序锁）
    :param first_commit_at: 首个施工 commit 时间（时序锁）
    """
    checks: list[CompareCheckResult] = [
        check_session_mutuality(record.contractor_session, record.evaluator_session),
        verify_criteria_integrity(record.criteria_yaml, record.criteria_hash),
    ]
    if task_criteria_ref:
        ref_id, ref_hash = parse_criteria_ref(task_criteria_ref)
        checks.append(CompareCheckResult(name="criteria_ref_id", passed=ref_id == record.experiment_id,
                                  reason="ok" if ref_id == record.experiment_id else "criteria_ref_id_mismatch"))
        checks.append(check_hash_lock(ref_hash, record.criteria_hash))
    else:
        checks.append(CompareCheckResult(name="criteria_ref_present", passed=False,
                                  reason="criteria_ref_missing:hash 未进任务书不许派工"))
    checks.append(check_time_lock(record.frozen_at, dispatched_at, first_commit_at))
    checks.append(
        CompareCheckResult(
            name="fairness_checked",
            passed=fairness_passed is True,
            reason="ok" if fairness_passed is True else
                   ("fairness_not_checked" if fairness_passed is None else "fairness_failed"),
        )
    )
    return ComparePreflightReport.assemble(checks)


def claim_exam(venue_ref: str, venues: Mapping[str, Any]) -> Any:
    """领考：按卡的 venue_ref 取考场适配器（fail-closed：未知/不可达都拒考）。

    :param venue_ref: 考场 id（venue_c4/venue_replay/venue_dual_run/venue_tool_bench）
    :param venues: {venue_id: 适配器} 注册表（适配器需提供 available() 与 run()）
    """
    if venue_ref not in VENUE_IDS:
        raise ValueError(f"unknown_venue:{venue_ref}")
    venue = venues.get(venue_ref)
    if venue is None:
        raise VenueUnavailable(f"venue_not_registered:{venue_ref}")
    if not venue.available():
        raise VenueUnavailable(f"venue_ruler_unreachable:{venue_ref}")
    return venue


@dataclass(frozen=True)
class VerdictCard:
    """统一裁定卡（DESIGN §3 L5 行载荷：verdict + evidence_pack，只增不改）。"""

    experiment_id: str
    verdict: str
    evaluator_session: str
    evidence_pack: dict[str, Any] = field(default_factory=dict)
    significance: str = ""
    too_good_exit: str | None = None
    attribution: str | None = None
    rejection_reason: str | None = None
    issued_at: str = ""


@dataclass(frozen=True)
class VerdictRuling:
    """裁定上下文打包（NO-LONG-PARAM-LIST 处方）：证据包+显著性+too-good 出口/归因。"""

    evidence_pack: Mapping[str, Any] | None = None
    significance: str = ""
    too_good_exit: str | None = None
    attribution: str | None = None
    rejection_reason: str | None = None


def issue_verdict_card(
    record: ComparisonExperimentRecord,
    verdict: str,
    *,
    ruled_by_session: str,
    ruling: VerdictRuling | None = None,
    issued_at: str = "",
) -> VerdictCard:
    """签发统一裁定卡：仅 evaluator_session 有签发权；E3 驳回必附归因三选一（DESIGN §2.5）。"""
    body = ruling or VerdictRuling()
    if ruled_by_session != record.evaluator_session:
        raise ValueError("verdict_card_must_be_signed_by_evaluator_session")
    if verdict not in {"win", "win_starred", "draw", "loss", "rejected_too_good"}:
        raise ValueError(f"unknown_verdict:{verdict}")
    if verdict == "rejected_too_good" and body.attribution not in {
        "leakage", "hidden_risk", "luck_or_gaming"
    }:
        raise ValueError(f"rejected_too_good_requires_attribution, got:{body.attribution!r}")
    if body.too_good_exit is not None and body.too_good_exit not in {"E1", "E2", "E3"}:
        raise ValueError(f"too_good_exit_must_be_E1_E2_E3, got:{body.too_good_exit!r}")
    return VerdictCard(
        experiment_id=record.experiment_id,
        verdict=verdict,
        evaluator_session=ruled_by_session,
        evidence_pack=dict(body.evidence_pack or {}),
        significance=body.significance,
        too_good_exit=body.too_good_exit,
        attribution=body.attribution,
        rejection_reason=body.rejection_reason,
        issued_at=issued_at,
    )
