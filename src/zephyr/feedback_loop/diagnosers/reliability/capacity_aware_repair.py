# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.capacity_aware_repair
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_capacity_aware_repair | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Capacity Aware Repair — v0.9.0 R120

Blindspot: FLE executes repairs without accounting for current resource headroom.
Risk: R120 — Repair action itself causes resource exhaustion — cascading failure.
"""

from dataclasses import dataclass


@dataclass
class CapacityAwareRepair:
    def check_headroom(self, action_cost: float, available: float) -> bool:
        return available >= action_cost * 1.2
