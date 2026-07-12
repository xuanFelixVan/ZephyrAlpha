# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.ewc_kb_review
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_ewc_kb_review | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
