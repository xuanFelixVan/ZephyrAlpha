# [A_module] module_id=MOD-UNK_capacity_aware_repair | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.diagnosers.capacity_aware_repair

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Capacity Aware Repair — v0.9.0 R120

Blindspot: FLE executes repairs without accounting for current resource headroom.
Risk: R120 — Repair action itself causes resource exhaustion — cascading failure.
"""

from dataclasses import dataclass


@dataclass
class CapacityAwareRepair:

    def check_headroom(self, action_cost: float, available: float) -> bool:
        return available >= action_cost * 1.2
