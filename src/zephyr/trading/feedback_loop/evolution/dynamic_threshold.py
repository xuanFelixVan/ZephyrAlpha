# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.dynamic_threshold
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_dynamic_threshold | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Dynamic Threshold — v0.7.0 R71

Blindspot: Static anomaly thresholds break under regime change.
Risk: R71 — Threshold too tight in high vol; too loose in low vol.
"""

from dataclasses import dataclass


@dataclass
class DynamicThreshold:
    base: float = 2.5
    current: float = 2.5
