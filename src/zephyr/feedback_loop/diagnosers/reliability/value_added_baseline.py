# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.value_added_baseline
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_value_added_baseline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
