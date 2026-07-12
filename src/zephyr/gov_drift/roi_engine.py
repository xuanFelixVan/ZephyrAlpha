# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.roi_engine
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; tests/audit/test_roi_engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ROI计算不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_roi_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ROI Engine — roi_engine.py





module_id: MOD-INF-023


修复ROI优先级：ROI = impact_weight × frequency / effort + 4级effort + 持续校准。


对标 blueprint.md §5.5 / TASK-INF-0029 / D-023-14。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class ROIScore:
    detector_id: str

    impact_weight: float

    frequency_score: float

    effort_score: float

    roi: float

    rank: int

    effort_tier: str

    computed_at: str = ""


class ROIEngine:
    WEIGHT_MAP: dict[str, int] = {"P0": 10, "P1": 5, "P2": 2}

    SEVERITY_MULT: dict[str, int] = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    EFFORT_MAP: dict[str, int] = {
        "auto_fixable": 1,
        "suggestion_simple": 3,
        "suggestion_complex": 8,
        "needs_human": 20,
    }

    def __init__(self) -> None:
        self._effort_feedback: dict[str, float] = {}

    def record_feedback(self, detector_id: str, actual_hours: float) -> None:
        self._effort_feedback[detector_id] = actual_hours

    def compute(
        self,
        detector_id: str,
        module_tier: str = "P0",
        severity: str = "MEDIUM",
        detections_30d: int = 0,
        effort_tier: str = "suggestion_simple",
    ) -> ROIScore:
        impact = self.WEIGHT_MAP.get(module_tier, 2) * self.SEVERITY_MULT.get(severity, 2)

        freq = 1.0

        if detections_30d > 0:
            freq = 1.0 + math.log2(max(1, detections_30d))

        effort = self.EFFORT_MAP.get(effort_tier, 8)

        feedback = self._effort_feedback.get(detector_id)

        if feedback:
            effort = max(1.0, feedback)

        roi = (impact * freq) / effort

        return ROIScore(
            detector_id=detector_id,
            impact_weight=float(impact),
            frequency_score=round(freq, 4),
            effort_score=float(effort),
            roi=round(roi, 4),
            rank=0,
            effort_tier=effort_tier,
            computed_at=datetime.now(UTC).isoformat(),
        )

    def rank(self, scores: list[ROIScore]) -> list[ROIScore]:
        sorted_scores = sorted(scores, key=lambda s: s.roi, reverse=True)

        for i, s in enumerate(sorted_scores):
            s.rank = i + 1

        return sorted_scores
