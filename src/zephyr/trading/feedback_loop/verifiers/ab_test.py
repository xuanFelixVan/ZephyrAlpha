# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.ab_test
# [DOMAIN] D_FBL_VERIFICATION
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
# [A_module] module_id=MOD-UNK_ab_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A/B Test Verifier — v0.9.0 R117

Blindspot: Repair effectiveness unverified via controlled experiment.
Risk: R117 — Cannot prove repair caused improvement vs. self-healing.
"""

from dataclasses import dataclass


@dataclass
class ABTest:
    control_group: float = 0.0
    treatment_group: float = 0.0

    @property
    def lift(self) -> float:
        return self.treatment_group - self.control_group
