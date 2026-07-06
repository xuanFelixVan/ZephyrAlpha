# [BLUEPRINT] SRC-033 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.data_governance.data_source_reliability
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.data_governance.__init__
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
# [A_module] module_id=MOD-GOV_data_source_reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel, Field


class ReliabilityDimension(str, Enum):
    UPTIME = "Uptime"
    ACCURACY = "Accuracy"
    TIMELINESS = "Timeliness"
    COMPLETENESS = "Completeness"
    CONSISTENCY = "Consistency"


DIMENSION_WEIGHTS: Final[dict[ReliabilityDimension, float]] = {
    ReliabilityDimension.UPTIME: 0.25,
    ReliabilityDimension.ACCURACY: 0.30,
    ReliabilityDimension.TIMELINESS: 0.20,
    ReliabilityDimension.COMPLETENESS: 0.15,
    ReliabilityDimension.CONSISTENCY: 0.10,
}


class ReliabilityScore(BaseModel):
    source: str
    scores: dict[ReliabilityDimension, float] = Field(default_factory=dict)
    composite: float = 0.0

    def compute_composite(self) -> float:
        total = 0.0
        for dim, weight in DIMENSION_WEIGHTS.items():
            score = self.scores.get(dim, 0.0)
            total += score * weight
        self.composite = round(total, 4)
        return self.composite

    @property
    def rating(self) -> str:
        if self.composite >= 0.90:
            return "A — Excellent"
        if self.composite >= 0.75:
            return "B — Good"
        if self.composite >= 0.60:
            return "C — Acceptable"
        if self.composite >= 0.40:
            return "D — Degraded"
        return "F — Unreliable"


def score_source(source_name: str, dimension_scores: dict[ReliabilityDimension, float]) -> ReliabilityScore:
    rs = ReliabilityScore(source=source_name, scores=dimension_scores)
    rs.compute_composite()
    return rs


def compare_sources(*scores: ReliabilityScore) -> list[tuple[str, float]]:
    return sorted([(s.source, s.composite) for s in scores], key=lambda x: -x[1])
