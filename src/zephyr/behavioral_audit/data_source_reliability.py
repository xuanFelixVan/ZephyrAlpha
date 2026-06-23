# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.data_source_reliability
# [DOMAIN] D-BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_data_source_reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReliabilityDimension(str, Enum):
    UPTIME = "Uptime"
    ACCURACY = "Accuracy"
    TIMELINESS = "Timeliness"
    COMPLETENESS = "Completeness"
    CONSISTENCY = "Consistency"


DIMENSION_WEIGHTS: dict[ReliabilityDimension, float] = {
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
