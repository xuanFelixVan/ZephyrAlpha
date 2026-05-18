# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.blast_radius_budget

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Blast Radius Budget — v0.13.0 R178

Blindspot: No constraint on maximum simultaneous repair scope.
Risk: R178 — Simultaneous repairs across all subsystems; if wrong, total collapse.
"""
from dataclasses import dataclass

@dataclass
class BlastRadiusBudget:
    max_concurrent_repairs: int = 3
    active_repairs: int = 0
