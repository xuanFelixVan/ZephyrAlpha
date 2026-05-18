# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.value_added_baseline

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Value Added Baseline — v0.10.0 R138

Blindspot: No measurement of net value FLE provides vs. baseline automation.
Risk: R138 — FLE costs more than it saves; negative ROI undetected.
"""
from dataclasses import dataclass

@dataclass
class ValueAddedBaseline:
    cost_baseline: float = 0.0
    cost_fle: float = 0.0

    @property
    def roi(self) -> float:
        return (self.cost_baseline - self.cost_fle) / max(self.cost_fle, 1.0)
