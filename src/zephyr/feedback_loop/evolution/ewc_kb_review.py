# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.evolution.ewc_kb_review

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""EWC KB Review — v0.6.0 R51

Blindspot: KB entries overwritten without Elastic Weight Consolidation.
Risk: R51 — New knowledge catastrophically erases old critical knowledge.
"""
from dataclasses import dataclass, field

@dataclass
class EWCKBReview:
    importance_weights: dict[str, float] = field(default_factory=dict)

    def protect(self, param: str, importance: float) -> None:
        self.importance_weights[param] = importance
