# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.confidence_decomposer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Confidence Decomposer — v0.7.0 R83

Blindspot: FLE outputs single confidence score without decomposition.
Risk: R83 — Overconfident on wrong factors despite overall low confidence.
"""
from dataclasses import dataclass


@dataclass
class ConfidenceDecomposer:

    def decompose(self, confidence: float, factors: dict) -> dict:
        return {k: confidence / max(len(factors), 1) for k in factors}
