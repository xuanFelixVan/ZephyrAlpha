# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.confidence_decomposer
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_confidence_decomposer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Confidence Decomposer — v0.7.0 R83

Blindspot: FLE outputs single confidence score without decomposition.
Risk: R83 — Overconfident on wrong factors despite overall low confidence.
"""

from dataclasses import dataclass


@dataclass
class ConfidenceDecomposer:
    def decompose(self, confidence: float, factors: dict) -> dict:
        return {k: confidence / max(len(factors), 1) for k in factors}
