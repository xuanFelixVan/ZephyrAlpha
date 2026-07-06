# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.credibility_engine
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; src/zephyr/governance/drift_detection/brain_integration.py; tests/audit/test_credibility_engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 可信度评分不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_credibility_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Credibility Engine — credibility_engine.py





module_id: MOD-INF-023


告警可信度评分：credibility = base_score × (1-fp_rate) × precision × recency_factor。


对标 blueprint.md §2.21 / TASK-INF-0022 / D-023-35。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class CredibilityScore:
    detector_id: str

    base_score: float

    fp_rate: float

    precision: float

    recency_factor: float

    credibility: float

    modulation: str

    configured_weight: float = 0.0

    computed_at: str = ""


class CredibilityEngine:
    NEW_DETECTOR_BASE: float = 0.5

    PROVEN_DETECTOR_BASE: float = 1.0

    FP_RATE_THRESHOLD_MILD: float = 0.3

    FP_RATE_THRESHOLD_SEVERE: float = 0.5

    RECENCY_STALE_DAYS: int = 90

    RECENCY_FACTOR_STALE: float = 0.8

    ALERT_HIGH: float = 0.8

    ALERT_MEDIUM: float = 0.4

    def __init__(self) -> None:
        self._owner_overrides: dict[str, float] = {}

        self._scores: dict[str, CredibilityScore] = {}

    def set_owner_override(self, detector_id: str, weight: float) -> None:
        self._owner_overrides[detector_id] = max(0.0, min(1.0, weight))

    def compute(
        self,
        detector_id: str,
        is_proven: bool = False,
        fp_count: int = 0,
        total_detections: int = 0,
        precision: float = 1.0,
        last_detected_at: datetime | None = None,
    ) -> CredibilityScore:
        base = self.PROVEN_DETECTOR_BASE if is_proven else self.NEW_DETECTOR_BASE

        if total_detections > 0:
            fp_rate = fp_count / total_detections

        else:
            fp_rate = 0.0

        fp_mult = 1.0

        if fp_rate > self.FP_RATE_THRESHOLD_SEVERE:
            fp_mult = 0.2

        elif fp_rate > self.FP_RATE_THRESHOLD_MILD:
            fp_mult = 0.5

        recency = 1.0

        if last_detected_at is not None:
            age = datetime.now(UTC).replace(tzinfo=None) - last_detected_at.replace(tzinfo=None)

            if age.days > self.RECENCY_STALE_DAYS:
                recency = self.RECENCY_FACTOR_STALE

        raw = base * (1.0 - fp_rate) * fp_mult * precision * recency

        owner_w = self._owner_overrides.get(detector_id, 0.0)

        if owner_w > 0.0:
            raw = raw * 0.3 + owner_w * 0.7

        credibility = round(max(0.0, min(1.0, raw)), 4)

        if credibility >= self.ALERT_HIGH:
            modulation = "normal_push"

        elif credibility >= self.ALERT_MEDIUM:
            modulation = "batched_aggregate"

        else:
            modulation = "shadow_observe"

        score = CredibilityScore(
            detector_id=detector_id,
            base_score=base,
            fp_rate=round(fp_rate, 4),
            precision=round(precision, 4),
            recency_factor=round(recency, 4),
            credibility=credibility,
            modulation=modulation,
            configured_weight=owner_w,
            computed_at=datetime.now(UTC).isoformat(),
        )

        self._scores[detector_id] = score

        return score

    def get_score(self, detector_id: str) -> CredibilityScore | None:
        return self._scores.get(detector_id)
