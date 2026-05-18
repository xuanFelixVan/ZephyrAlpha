# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.decision_provenance

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Decision Provenance — v0.12.0 R166

Blindspot: FLE decisions lack audit trail of contributing factors.
Risk: R166 — Why was this repair chosen?  Invisible after the fact.
"""
from dataclasses import dataclass, field

@dataclass
class DecisionProvenance:
    decisions: list[dict] = field(default_factory=list)

    def record(self, decision: dict) -> None:
        self.decisions.append(decision)
