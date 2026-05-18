# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.feedback_loop.gates.autonomy_credit

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Autonomy Credit System — v0.7.0 R87

Blindspot: No decay of autonomy trust over time.
Risk: R87 — Once-trusted subsystem never re-evaluated.
"""
from dataclasses import dataclass

@dataclass
class AutonomyCredit:
    score: float = 100.0
    decay_per_day: float = 1.0
