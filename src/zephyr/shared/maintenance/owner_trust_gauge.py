# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.maintenance.owner_trust_gauge
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TrustLevel(Enum):
    FULL_AUTONOMY = "full_autonomy"
    SUPERVISED = "supervised"
    HUMAN_GATED = "human_gated"
    REVOKED = "revoked"


@dataclass
class TrustAssessment:
    agent_id: str
    trust_level: TrustLevel
    score: float
    reason: str


class OwnerTrustGauge:
    def __init__(self, default_score: float = 0.5):
        self._scores: dict[str, float] = {}
        self._default = default_score

    def update(self, agent_id: str, delta: float) -> TrustAssessment:
        current = self._scores.get(agent_id, self._default)
        new_score = max(0.0, min(1.0, current + delta))
        self._scores[agent_id] = new_score
        if new_score >= 0.8:
            level = TrustLevel.FULL_AUTONOMY
        elif new_score >= 0.5:
            level = TrustLevel.SUPERVISED
        elif new_score >= 0.2:
            level = TrustLevel.HUMAN_GATED
        else:
            level = TrustLevel.REVOKED
        return TrustAssessment(agent_id, level, new_score, f"score={new_score:.2f}")

    def assess(self, agent_id: str) -> TrustAssessment:
        return self.update(agent_id, 0.0)
