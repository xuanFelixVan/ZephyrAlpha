# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.anti_automation_bias
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_anti_automation_bias | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Anti-Automation Bias — D-022-09 mandatory human oversight enforcement.

Actively counters Owner automation bias through:
1. Forced random sampling — 5% of autonomous operations paused for review
2. Review rate monitoring — response time trend, confirmation rate, fatigue detection
3. Review quality assessment — miss rate from audit cross-reference
4. Anti-sycophancy calibration — engine ignores actor identity/emotion, only content

Reference: Georgetown CSET automation bias report, EU AI Act Art.14,
Anthropic Sycophancy 58.19%, UPenn Cialdini six principles.
"""

from __future__ import annotations

import hashlib
import random
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OversightAction(str, Enum):
    PASS = "pass"
    FORCE_REVIEW = "force_review"
    BLOCK_AND_NOTIFY = "block_and_notify"


class ReviewDecision(str, Enum):
    CONFIRMED_SAFE = "confirmed_safe"
    OVERRIDDEN = "overridden"
    TIMED_OUT = "timed_out"


class FatigueLevel(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    FATIGUED = "fatigued"


class BiasPattern(str, Enum):
    MECHANICAL_CONFIRM = "mechanical_confirm"
    RESPONSE_LATENCY_GROWTH = "response_latency_growth"
    CONFIRMATION_DROPOUT = "confirmation_dropout"
    PATTERN_REPETITION = "pattern_repetition"


@dataclass
class ReviewRecord:
    operation_id: str
    timestamp: float = field(default_factory=time.time)
    decision: ReviewDecision = ReviewDecision.TIMED_OUT
    response_time_s: float = 0.0
    was_safe_in_audit: bool | None = None


@dataclass
class SycophancyProbe:
    content_hash: str
    original_framing: str
    alternate_framing: str
    original_decision: str
    alternate_decision: str
    consistent: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class OversightResult:
    action: OversightAction
    reason: str
    forced_review: bool = False
    timeout_s: float = 30.0


class AntiAutomationBias:
    """Enforces human oversight to prevent automation bias and review fatigue.

    Integrates forced review sampling, response time monitoring, fatigue
    detection, and anti-sycophancy calibration into the escalation pipeline.
    """

    def __init__(self, forced_review_ratio: float = 0.05, review_timeout_s: float = 30.0):
        self._forced_review_ratio = forced_review_ratio
        self._review_timeout_s = review_timeout_s
        self._autonomous_count = 0
        self._review_records: list[ReviewRecord] = []
        self._sycophancy_probes: list[SycophancyProbe] = []
        self._fatigue_level = FatigueLevel.NORMAL
        self._last_response_times: list[float] = []
        self._consecutive_confirms = 0
        self._audit_feedback: dict[str, bool] = {}

    @property
    def forced_review_ratio(self) -> float:
        return self._forced_review_ratio

    @forced_review_ratio.setter
    def forced_review_ratio(self, value: float) -> None:
        self._forced_review_ratio = max(0.01, min(0.20, value))

    @property
    def fatigue_level(self) -> FatigueLevel:
        return self._fatigue_level

    def evaluate(
        self,
        operation_id: str,
        is_autonomous: bool = False,
        actor_identity: str = "",
        operation_content: str = "",
    ) -> OversightResult:
        """Evaluate whether an operation needs forced human review.

        Decision matrix:
          - Random sampling hits → force_review
          - Fatigue detected → block_and_notify (escalate more aggressively)
          - Mechanical confirmation pattern → force_review
          - Normal → pass
        """
        if not is_autonomous:
            return OversightResult(OversightAction.PASS, "Not autonomous — no sampling needed")
        self._autonomous_count += 1

        if self._fatigue_level is FatigueLevel.FATIGUED:
            return OversightResult(
                OversightAction.BLOCK_AND_NOTIFY,
                "Owner fatigue critical — blocking autonomous path",
            )
        if self._fatigue_level is FatigueLevel.ELEVATED:
            return OversightResult(
                OversightAction.FORCE_REVIEW,
                "Owner fatigue elevated — forcing additional review",
                forced_review=True,
                timeout_s=self._review_timeout_s,
            )
        if self._consecutive_confirms >= 10:
            return OversightResult(
                OversightAction.FORCE_REVIEW,
                f"Mechanical confirmation pattern detected ({self._consecutive_confirms} consecutive) — forcing review",
                forced_review=True,
                timeout_s=self._review_timeout_s,
            )

        if self._should_force_review():
            return OversightResult(
                OversightAction.FORCE_REVIEW,
                f"Random sampling hit (1/{int(1 / self._forced_review_ratio)} autonomous ops)",
                forced_review=True,
                timeout_s=self._review_timeout_s,
            )
        return OversightResult(OversightAction.PASS, "Passed sampling gate")

    def record_review(
        self,
        operation_id: str,
        decision: ReviewDecision,
        response_time_s: float = 0.0,
    ) -> None:
        record = ReviewRecord(
            operation_id=operation_id,
            decision=decision,
            response_time_s=response_time_s,
        )
        self._review_records.append(record)
        if decision is ReviewDecision.TIMED_OUT:
            return
        self._last_response_times.append(response_time_s)
        if len(self._last_response_times) > 20:
            self._last_response_times = self._last_response_times[-20:]

        if decision is ReviewDecision.CONFIRMED_SAFE:
            self._consecutive_confirms += 1
        else:
            self._consecutive_confirms = 0

        self._update_fatigue_level()

    def record_audit_feedback(self, operation_id: str, actually_unsafe: bool) -> None:
        self._audit_feedback[operation_id] = actually_unsafe
        for rec in self._review_records:
            if rec.operation_id == operation_id:
                rec.was_safe_in_audit = not actually_unsafe

    def evaluate_review_quality(self) -> dict[str, Any]:
        reviewed = [
            r
            for r in self._review_records
            if r.decision is ReviewDecision.CONFIRMED_SAFE and r.was_safe_in_audit is not None
        ]
        if not reviewed:
            return {"miss_rate": None, "total_reviewed": 0, "target": "≤ 1%"}
        misses = sum(1 for r in reviewed if r.was_safe_in_audit is False)
        return {
            "miss_rate": misses / len(reviewed),
            "total_reviewed": len(reviewed),
            "misses": misses,
            "target": "≤ 1%",
        }

    def probe_sycophancy(
        self,
        operation_content: str,
        framing_a: str,
        framing_b: str,
        decision_a: str,
        decision_b: str,
    ) -> SycophancyProbe:
        content_hash = hashlib.sha256(operation_content.encode()).hexdigest()[:16]
        consistent = decision_a == decision_b
        probe = SycophancyProbe(
            content_hash=content_hash,
            original_framing=framing_a,
            alternate_framing=framing_b,
            original_decision=decision_a,
            alternate_decision=decision_b,
            consistent=consistent,
        )
        self._sycophancy_probes.append(probe)
        return probe

    def get_sycophancy_rate(self) -> float:
        if not self._sycophancy_probes:
            return 0.0
        inconsistent = sum(1 for p in self._sycophancy_probes if not p.consistent)
        return inconsistent / len(self._sycophancy_probes)

    def get_review_monitoring(self) -> dict[str, Any]:
        confirmed = [r for r in self._review_records if r.decision is not ReviewDecision.TIMED_OUT]
        blocked = [r for r in self._review_records if r.decision is ReviewDecision.OVERRIDDEN]
        confirmation_rate = len(blocked) / max(1, len(confirmed))

        avg_response = (
            sum(self._last_response_times) / max(1, len(self._last_response_times))
            if self._last_response_times
            else 0.0
        )
        trend = self._compute_response_trend()
        quality = self.evaluate_review_quality()

        return {
            "confirmation_rate": confirmation_rate,
            "avg_response_time_s": avg_response,
            "response_time_trend": trend,
            "consecutive_confirms": self._consecutive_confirms,
            "fatigue_level": self._fatigue_level.value,
            "review_quality": quality,
            "sycophancy_rate": self.get_sycophancy_rate(),
            "total_autonomous_ops": self._autonomous_count,
            "total_reviews_triggered": len(self._review_records),
        }

    def summary(self) -> dict[str, Any]:
        return self.get_review_monitoring()

    def _should_force_review(self) -> bool:
        return random.random() < self._forced_review_ratio

    def _compute_response_trend(self) -> str:
        if len(self._last_response_times) < 4:
            return "insufficient_data"
        half = len(self._last_response_times) // 2
        recent_avg = sum(self._last_response_times[-half:]) / half
        older_avg = sum(self._last_response_times[:half]) / half
        if older_avg == 0:
            return "stable"
        ratio = recent_avg / older_avg
        if ratio > 1.5:
            return "growing_significantly"
        elif ratio > 1.15:
            return "growing_slightly"
        elif ratio < 0.85:
            return "improving"
        return "stable"

    def _update_fatigue_level(self) -> None:
        if len(self._last_response_times) < 8:
            return
        half = len(self._last_response_times) // 2
        recent_avg = sum(self._last_response_times[-half:]) / half
        older_avg = sum(self._last_response_times[:half]) / half
        if older_avg > 0 and recent_avg / older_avg > 1.5:
            self._fatigue_level = FatigueLevel.FATIGUED
        elif older_avg > 0 and recent_avg / older_avg > 1.25:
            self._fatigue_level = FatigueLevel.ELEVATED
        else:
            confirmed = [r for r in self._review_records[-20:] if r.decision is not ReviewDecision.TIMED_OUT]
            if confirmed:
                block_rate = sum(1 for r in confirmed if r.decision is ReviewDecision.OVERRIDDEN) / len(confirmed)
                if block_rate < 0.3:
                    self._fatigue_level = FatigueLevel.ELEVATED
                else:
                    self._fatigue_level = FatigueLevel.NORMAL


class AntiSycophancyFilter:
    """Strips identity metadata and emotional framing from escalation input.

    The escalation engine must not see actor identity, emotional valence,
    or linguistic framing — only the raw operation content. This prevents
    sycophantic bias where the engine "agrees" with a confident/authoritative tone.
    """

    IDENTITY_KEYS = frozenset(
        {
            "actor_name",
            "actor_role",
            "actor_level",
            "actor_tenure",
            "owner_id",
            "agent_version",
            "session_id",
        }
    )
    EMOTIONAL_MARKERS = frozenset(
        {
            "urgent",
            "critical",
            "please",
            "kindly",
            "important",
            "asap",
            "immediately",
            "trust me",
            "i promise",
            "you must",
            "don't worry",
            "it's fine",
            "nothing to see",
            "harmless",
        }
    )

    @classmethod
    def strip_identity(cls, metadata: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in metadata.items() if k not in cls.IDENTITY_KEYS}

    @classmethod
    def detect_emotional_markers(cls, text: str) -> list[str]:
        text_lower = text.lower()
        return [m for m in cls.EMOTIONAL_MARKERS if m in text_lower]

    @classmethod
    def normalize_framing(cls, content: str) -> str:
        import re

        markers = cls.detect_emotional_markers(content)
        normalized = content
        for marker in markers:
            normalized = re.sub(marker, "[FILTERED]", normalized, flags=re.IGNORECASE)
        return normalized

    @classmethod
    def verify_consistency(
        cls,
        operation_content: str,
        framing_variants: Sequence[str],
        decision_fn,  # Callable[[str], str]
    ) -> list[SycophancyProbe]:
        probes: list[SycophancyProbe] = []
        base_decision = decision_fn(operation_content)
        content_hash = hashlib.sha256(operation_content.encode()).hexdigest()[:16]
        for variant in framing_variants:
            variant_decision = decision_fn(variant)
            probes.append(
                SycophancyProbe(
                    content_hash=content_hash,
                    original_framing=operation_content,
                    alternate_framing=variant,
                    original_decision=base_decision,
                    alternate_decision=variant_decision,
                    consistent=base_decision == variant_decision,
                )
            )
        return probes
