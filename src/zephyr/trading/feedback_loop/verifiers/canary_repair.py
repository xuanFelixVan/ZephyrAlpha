# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.canary_repair
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
# [A_module] module_id=MOD-UNK_canary_repair | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Canary Repair — v0.8.0 R104b

Blindspot: Repairs deployed to all instances simultaneously.
Risk: R104b — Bad repair affects 100% of instances instantly.
"""

from dataclasses import dataclass


@dataclass
class CanaryRepair:
    canary_pct: float = 0.1
