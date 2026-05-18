# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.verifiers.canary_repair

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Canary Repair — v0.8.0 R104b

Blindspot: Repairs deployed to all instances simultaneously.
Risk: R104b — Bad repair affects 100% of instances instantly.
"""
from dataclasses import dataclass

@dataclass
class CanaryRepair:
    canary_pct: float = 0.1
