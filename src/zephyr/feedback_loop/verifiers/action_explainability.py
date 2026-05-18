# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.verifiers.action_explainability

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Action Explainability — v0.3.0 R15

Blindspot: FLE actions opaque; owner cannot understand why a repair was chosen.
Risk: R15 — Trust eroded; owner overrides correct repairs due to lack of explainability.
"""
from dataclasses import dataclass

@dataclass
class ActionExplainability:

    def explain(self, action: dict) -> str:
        return f"Action: {action.get('type')} — Reason: {action.get('reason')}"
