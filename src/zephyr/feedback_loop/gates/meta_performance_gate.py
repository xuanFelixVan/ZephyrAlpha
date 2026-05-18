# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.feedback_loop.gates.meta_performance_gate

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Meta Performance Gate — v0.11.0 R158

Blindspot: FLE performance evaluated only externally; internal benchmark invisible.
"""
from dataclasses import dataclass

@dataclass
class MetaPerformanceGate:
    mttd_seconds: float = 300.0
    mttr_seconds: float = 600.0
