# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.reliability.blast_radius_budget
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_blast_radius_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Blast Radius Budget — v0.13.0 R178

Blindspot: No constraint on maximum simultaneous repair scope.
Risk: R178 — Simultaneous repairs across all subsystems; if wrong, total collapse.
"""

from dataclasses import dataclass


@dataclass
class BlastRadiusBudget:
    max_concurrent_repairs: int = 3
    active_repairs: int = 0
