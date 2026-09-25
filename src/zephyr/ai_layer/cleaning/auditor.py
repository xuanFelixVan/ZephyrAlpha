# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] zephyr.ai_layer.cleaning.auditor
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.cleaning.policy (CleaningPolicy);
#                zephyr.ai_layer.cleaning.spec_store (SpecStore/SpecCard);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.intake.intake_events (audit 编排挂接=接线批);
#             zephyr.ai_layer.cleaning.washer (rewasher 回调注入)
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 裁判独立性机检（DESIGN §2.5）：reviewer_session≠wash.session/异厂
#              （model_vendor 前缀表）/异档，任一同源即拒判卷（MCE RISK-3.2 运动员
#              不兼任裁判）；单卡绝对评分制（禁 pairwise）；rubric 三维 0-2、任一维
#              0 分即 fail（禁 0 分通过）；机检前置（裁判前零成本：字段非空+值域+来源
#              四件套与 L2 卡一致+禁占位词——不过直接 rework 不耗裁判）；采样读 C1
#              非硬编码：冷启动（前 cold_start_days/前 cold_start_cards 先到者）100%，
#              此后确定性分桶抽 periodic_rate+高影响卡强制全检；级联升级 ≤1 次/卡
#              （standard→premium 唯一出口）→再 fail→mark rejected_wash+emit
#              intake_reject_due {stage:'L3'}；injection_suspect 另加 LSG 审计标记
#              （L1 待观察挂接=批注记，L1 建后接线）；周度质变监控=纯函数读数
#              （不自带定时器，宪法 §9.3）；judge 端口注入，单测禁真实外呼
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.5（抽验协议真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 活卡缺席→AuditOutcome(verdict=error)；rubric 维度缺失/越界→判 fail
#                  （不虚构通过）；judge 异常→verdict=error 不落 review（重试由事件层
#                  重放承担）；拒因越域→ValueError（编程错误即时暴露）
# [TESTS] tests/ai_layer/cleaning/test_auditor.py（冷启动 100%/周期分桶/高影响强制/
#         机检拒占位与来源不一致/同厂同档同会话拒卷/rubric 0 分 fail/pass 回填/
#         两级流转留痕/质变监控阈值）
"""auditor — L3 清洗质量抽验审计器：采样 → 机检前置 → 裁判 → rubric 判分 → 退回流转。

设计真源：``docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md`` §2.5（裁定 D-L3-03：
裁判走 OBJ_M review_judge 轨；自偏好随参数量增大→异厂异档硬性；position/verbosity
偏差→单卡绝对评分+字段锚定 rubric；外部实证 arXiv 2306.05685 / 2410.21819）。

★ judge 端口是注入式 JudgePort；生产适配器应经 lsg_gateway_call 走 review_judge 轨
（premium+异厂+不用免费窗，DESIGN §2.2 工序⑤）——本批只交付判卷协议与流转，
实调接线批注留 washer.lsg_gateway_call 同款。
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Final, Mapping

from zephyr.ai_layer.cleaning.policy import CleaningPolicy
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "AuditOutcome",
    "AuditorDeps",
    "SamplingAuditor",
    "check_judge_independence",
    "judge_quality_watch",
    "machine_precheck",
    "model_vendor",
    "rubric_pass",
    "sample_decision",
]

VENDOR_PREFIXES: Final[dict[str, tuple[str, ...]]] = {
    "deepseek": ("deepseek",),
    "anthropic": ("claude",),
    "zhipu": ("glm", "chatglm"),
    "alibaba": ("qwen",),
    "openai": ("gpt", "o1", "o3", "o4"),
    "mistral": ("mistral", "mixtral"),
}
VENDOR_UNKNOWN: Final = "unknown"
_BUCKET_MODULUS: Final = 100

JudgePort = Callable[[Any], "CleaningJudgeResult"]


@dataclass(frozen=True)
class JudgeRequest:
    """判卷请求（单卡绝对评分制：只给一张卡，禁对比对象）。"""

    spec_id: str
    spec_payload: dict[str, Any]
    rubric_dims: tuple[str, ...]


@dataclass(frozen=True)
class CleaningJudgeResult:
    """裁判回执（scores=逐维 0-2 绝对分；model/session/tier 供独立性机检）。"""

    scores: dict[str, float]
    note: str = ""
    model: str = ""
    session: str = ""
    tier: str = ""


@dataclass(frozen=True)
class SampleDecision:
    """采样裁定（reason∈cold_start/high_impact/periodic_sample/skip）。"""

    sampled: bool
    reason: str


@dataclass(frozen=True)
class AuditOutcome:
    """单卡审计结局（next_action 驱动编排层流转）。"""

    card_id: str
    spec_id: str
    sampled: bool
    verdict: str            # pass|fail|rework|not_sampled|refused|error
    next_action: str        # none|rewash_upgrade|reject|rejudge
    failures: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""


@dataclass(frozen=True)
class AuditorDeps:
    """审计依赖束（store/judge/rewasher/journal/卡写全注入，测试零真实外呼）。"""

    session_id: str
    store: Any                                    # duck: get_active/set_review/mark_status/count_cards
    policy: CleaningPolicy
    judge: JudgePort
    rewasher: Callable[[str], Any] | None = None  # duck: wash_card(card_id)->WashOutcome
    journal: Any | None = None                    # duck: emit(kind, payload)
    card_writer: Any | None = None                # duck: transition(card_id, stage, **refs)


def model_vendor(model_id: str) -> str:
    """模型厂商前缀表机检（同源检测用；unknown 与任何值同值即同源=保守拒卷）。"""
    text = str(model_id or "").strip().lower()
    for vendor, prefixes in VENDOR_PREFIXES.items():
        if any(text.startswith(p) for p in prefixes):
            return vendor
    return VENDOR_UNKNOWN


def _gate_status(four_gates: Mapping[str, Any] | None, key: str) -> str:
    raw = (four_gates or {}).get(key)
    if isinstance(raw, Mapping):
        raw = raw.get("status")
    return str(raw or "").strip().lower()


def sample_decision(
    policy: CleaningPolicy,
    *,
    card_id: str,
    cards_washed_total: int,
    cold_started_at: datetime,
    as_of: datetime,
    four_gates: Mapping[str, Any] | None,
) -> SampleDecision:
    """采样裁定纯函数（DESIGN §2.5：冷启动先到者 100%→20%+高影响强制全检）。

    确定性分桶：sha256(card_id)%100 < periodic_rate*100——零随机零时钟（as_of 注入）。
    """
    if (as_of - cold_started_at) < timedelta(days=policy.cold_start_days):
        return SampleDecision(True, "cold_start")
    if cards_washed_total <= policy.cold_start_cards:
        return SampleDecision(True, "cold_start")
    if policy.high_impact_full_check:
        status = _gate_status(four_gates, policy.high_impact_gate_key)
        if status in policy.high_impact_pass_values:
            return SampleDecision(True, "high_impact")
    bucket = int(hashlib.sha256(card_id.encode("utf-8")).hexdigest(), 16) % _BUCKET_MODULUS
    if bucket < int(round(policy.periodic_rate * _BUCKET_MODULUS)):
        return SampleDecision(True, "periodic_sample")
    return SampleDecision(False, "skip")


def _field_text(spec: Mapping[str, Any]) -> str:
    parts = [str(spec.get(k) or "") for k in ("mechanism_one_liner", "mechanism_detail", "reproduction_notes")]
    quotes = spec.get("source_quotes") or []
    parts.extend(str(q) for q in quotes)
    return " ".join(parts)


def _check_text_groups(spec: Mapping[str, Any], policy: CleaningPolicy, failures: list[str]) -> None:
    """文本组判据：三文本非空+禁占位词+骨架组（applicability/precheck/data/quotes/source）。"""
    for group in ("mechanism_one_liner", "mechanism_detail", "reproduction_notes"):
        if not str(spec.get(group) or "").strip():
            failures.append(f"empty_group:{group}")
    joined = _field_text(spec)
    for word in sorted(policy.placeholder_words):
        if word in joined:
            failures.append(f"placeholder_word:{word}")
    applicability = spec.get("applicability") or {}
    if not isinstance(applicability, Mapping) or not applicability.get("regime"):
        failures.append("empty_group:applicability")
    for group in ("data_fields", "source_quotes"):
        if not (spec.get(group) or []):
            failures.append(f"empty_group:{group}")
    if not str(spec.get("source_url") or "").strip():
        failures.append("empty_group:source")


def _check_vocab_groups(spec: Mapping[str, Any], policy: CleaningPolicy, failures: list[str]) -> None:
    """值域判据：precheck.overall 词域+adapt_needed 必带 adaptation_plan+risk_flags 词域。"""
    precheck = spec.get("ashare_precheck") or {}
    overall = str((precheck or {}).get("overall") or "")
    if overall not in policy.vocab_of("precheck_overall"):
        failures.append(f"precheck_overall_out_of_vocab:{overall}")
    if overall == "adapt_needed" and not str((precheck or {}).get("adaptation_plan") or "").strip():
        failures.append("adapt_plan_missing")
    bad_flags = set(spec.get("risk_flags") or []) - policy.vocab_of("risk_flags")
    if bad_flags:
        failures.append(f"risk_flags_out_of_vocab:{','.join(sorted(bad_flags))}")


def _check_source_inheritance(
    spec: Mapping[str, Any], l2_card: Mapping[str, Any], failures: list[str]
) -> None:
    """来源四件套只读继承断言（闸 1：防洗后断源）。"""
    for key in ("source_url", "source_name", "source_publisher", "source_year"):
        if (spec.get(key) or None) != (l2_card.get(key) or None):
            failures.append(f"source_drift:{key}")


def machine_precheck(
    spec: Mapping[str, Any], l2_card: Mapping[str, Any] | None, policy: CleaningPolicy
) -> tuple[bool, tuple[str, ...]]:
    """机检前置纯判据（裁判前零成本；DESIGN §2.5 机检前置行）。

    七组字段非空+非占位+值域+来源四件套与 L2 卡一致（只读继承断言）。
    """
    failures: list[str] = []
    _check_text_groups(spec, policy, failures)
    _check_vocab_groups(spec, policy, failures)
    if l2_card is not None:
        _check_source_inheritance(spec, l2_card, failures)
    return (not failures), tuple(failures)


def check_judge_independence(
    wash: Mapping[str, Any],
    *,
    reviewer_session: str,
    reviewer_model: str,
    reviewer_tier: str,
    policy: CleaningPolicy,
) -> tuple[bool, str]:
    """裁判独立性机检：会话互斥+异厂+异档（任一违例即拒判卷）。"""
    if policy.forbid_same_session and str(wash.get("session") or "") == str(reviewer_session):
        return False, "same_session"
    if policy.forbid_same_vendor and model_vendor(str(wash.get("model_id") or "")) == model_vendor(reviewer_model):
        return False, "same_vendor"
    if policy.forbid_same_tier and str(wash.get("model_tier") or "") == str(reviewer_tier):
        return False, "same_tier"
    return True, ""


def rubric_pass(scores: Mapping[str, float], policy: CleaningPolicy) -> tuple[bool, str]:
    """rubric 判分纯函数：三维齐全、各 0-2、任一维 0 分即 fail（禁 0 分通过）。"""
    for dim in policy.rubric_dimensions:
        if dim not in scores:
            return False, f"rubric_dim_missing:{dim}"
        value = scores[dim]
        if not 0 <= float(value) <= policy.rubric_scale_max:
            return False, f"rubric_dim_out_of_scale:{dim}:{value}"
    if policy.zero_score_fails:
        for dim in policy.rubric_dimensions:
            if float(scores[dim]) == 0:
                return False, f"rubric_zero_score:{dim}"
    return True, ""


def judge_quality_watch(rework_rate: float, policy: CleaningPolicy) -> dict[str, Any]:
    """裁判质变监控纯读数（周度调用方挂事件，零定时器）：>阈值→降档建议挂 OBJ_M。"""
    alert = float(rework_rate) > policy.rework_rate_alert
    return {
        "rework_rate": float(rework_rate),
        "threshold": policy.rework_rate_alert,
        "alert": alert,
        "suggestion": ("washer_tier_downgrade_proposal_objm_dual_run" if alert else "none"),
    }


class SamplingAuditor:
    """抽验编排：采样→机检→独立性→裁判→判分→（升级重洗一次→）退回。"""

    def __init__(self, deps: AuditorDeps) -> None:
        self._d: Final = deps

    def audit(
        self,
        card_id: str,
        *,
        l2_card: Mapping[str, Any] | None = None,
        cold_started_at: datetime | None = None,
        as_of: datetime | None = None,
        escalations_used: int = 0,
    ) -> AuditOutcome:
        """单卡审计（活卡缺席=error；未采样=留痕不动卡；fail→rewash_upgrade/reject）。"""
        spec = self._d.store.get_active(card_id)
        if spec is None:
            return AuditOutcome(card_id, "", False, "error", "none", note="no_active_spec")
        payload = self._spec_payload(spec)
        decision = self._decide(card_id, cold_started_at, as_of, l2_card)
        if not decision.sampled:
            self._record(spec, {"sampled": False, "verdict": None})
            return AuditOutcome(card_id, spec.spec_id, False, "not_sampled", "none")
        ok, failures = machine_precheck(payload, l2_card, self._d.policy)
        if not ok:
            self._record(spec, {"sampled": True, "verdict": "rework", "failures": list(failures),
                                "reviewed_at": now_utc().isoformat()})
            return self._route(card_id, spec, "rework", escalations_used, failures)
        verdict, note = self._judge(spec, payload)
        if verdict == "error":
            return AuditOutcome(card_id, spec.spec_id, True, "error", "rejudge", note=note)
        if verdict == "pass":
            return AuditOutcome(card_id, spec.spec_id, True, "pass", "none", note=note)
        return self._route(card_id, spec, "fail", escalations_used, (note,))

    def audit_and_route(
        self,
        card_id: str,
        *,
        l2_card: Mapping[str, Any] | None = None,
        cold_started_at: datetime | None = None,
        as_of: datetime | None = None,
    ) -> AuditOutcome:
        """两级流转全编排：fail→升级重洗一次（级联唯一出口）→再 fail→退回阴性。"""
        first = self.audit(card_id, l2_card=l2_card, cold_started_at=cold_started_at, as_of=as_of)
        if first.next_action != "rewash_upgrade" or self._d.rewasher is None:
            return first
        self._d.rewasher(card_id)
        # 二审 escalations_used 已尽：fail 会由 audit 内部直接 finalize（终态留痕一次）。
        return self.audit(card_id, l2_card=l2_card, cold_started_at=cold_started_at,
                          as_of=as_of, escalations_used=1)

    # ------------------------------------------------------------- 内部工序

    def _spec_payload(self, spec: Any) -> dict[str, Any]:
        return {
            "mechanism_one_liner": spec.mechanism_one_liner,
            "mechanism_detail": spec.mechanism_detail,
            "reproduction_notes": spec.reproduction_notes,
            "applicability": spec.applicability,
            "ashare_precheck": spec.ashare_precheck,
            "risk_flags": spec.risk_flags,
            "data_fields": spec.data_fields,
            "source_quotes": spec.source_quotes,
            "source_name": spec.source_name,
            "source_url": spec.source_url,
            "source_publisher": spec.source_publisher,
            "source_year": spec.source_year,
            "wash": spec.wash,
            "status": spec.status,
        }

    def _decide(
        self,
        card_id: str,
        cold_started_at: datetime | None,
        as_of: datetime | None,
        l2_card: Mapping[str, Any] | None,
    ) -> SampleDecision:
        four_gates = dict(l2_card or {}).get("four_gates") or {}
        return sample_decision(
            self._d.policy,
            card_id=card_id,
            cards_washed_total=int(self._d.store.count_cards()),
            cold_started_at=cold_started_at or now_utc(),
            as_of=as_of or now_utc(),
            four_gates=four_gates,
        )

    def _judge(self, spec: Any, payload: Mapping[str, Any]) -> tuple[str, str]:
        wash = dict(payload.get("wash") or {})
        try:
            result = self._d.judge(
                JudgeRequest(spec.spec_id, payload, self._d.policy.rubric_dimensions)
            )
        except Exception as exc:  # noqa: BLE001——裁判面异常不落 review（事件层重试承担）
            return "error", f"judge_exception:{type(exc).__name__}"
        independent, why = check_judge_independence(
            wash,
            reviewer_session=result.session,
            reviewer_model=result.model,
            reviewer_tier=result.tier,
            policy=self._d.policy,
        )
        if not independent:
            log.warning("裁判独立性机检拒卷：%s %s", spec.spec_id, why)
            return "error", f"judge_refused:{why}"
        passed, why = rubric_pass(result.scores, self._d.policy)
        verdict = "pass" if passed else "fail"
        self._record(spec, {
            "sampled": True, "verdict": verdict, "reviewer_session": result.session,
            "reviewer_model": result.model, "rubric_scores": dict(result.scores),
            "note": result.note, "reviewed_at": now_utc().isoformat(),
        })
        return verdict, why

    def _route(
        self, card_id: str, spec: Any, verdict: str, escalations_used: int, failures: tuple[str, ...]
    ) -> AuditOutcome:
        """fail/rework 流转：级联升级额度未尽→rewash_upgrade；已尽→reject 终态。"""
        if escalations_used < self._d.policy.cascade_upgrade_max_per_card:
            return AuditOutcome(card_id, spec.spec_id, True, verdict, "rewash_upgrade",
                                failures=failures,
                                note=f"upgrade_tier:{self._d.policy.upgrade_tier}")
        return self._finalize_reject(card_id, AuditOutcome(
            card_id, spec.spec_id, True, verdict, "reject", failures=failures))

    def _finalize_reject(self, card_id: str, outcome: AuditOutcome) -> AuditOutcome:
        """退回终态：spec rejected_wash 墓碑+intake_reject_due 留痕+卡 transition rejected。"""
        spec = self._d.store.get_active(card_id)
        injection = bool(spec and "injection_suspect" in (spec.risk_flags or []))
        reason = "injection_suspect" if injection else "wash_failed"
        evidence = f"review:{outcome.spec_id}:{';'.join(outcome.failures)[:160]}"
        if spec is not None:
            self._d.store.mark_status(spec.spec_id, "rejected_wash", self._d.policy)
        if injection:
            # [LSG 审计批注] injection_suspect：另加 LSG 审计标记；该 source 源头进 L1
            # 待观察——L1 待观察清单建成后在此挂事件（当前批注留痕）。
            log.warning("injection_suspect 终裁：%s（source 进 L1 待观察=批注留痕）", card_id)
        if self._d.journal is not None:
            self._d.journal.emit(
                "intake_reject_due",
                {"card_id": card_id, "stage": "L3", "rejection_reason": reason,
                 "evidence_ref": evidence},
            )
        if self._d.card_writer is not None:
            self._d.card_writer.transition(card_id, "rejected", rejection_reason=reason,
                                           evidence_ref=evidence)
        return AuditOutcome(card_id, outcome.spec_id, True, outcome.verdict, "reject",
                            failures=outcome.failures, note=reason)

    def _record(self, spec: Any, review: dict[str, Any]) -> None:
        self._d.store.set_review(spec.spec_id, review)
