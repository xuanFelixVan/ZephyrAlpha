# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.meta_performance_gate
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-UNK_meta_performance_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Meta Performance Gate — v0.11.0 R158

Blindspot: FLE performance evaluated only externally; internal benchmark invisible.
"""

from dataclasses import dataclass


@dataclass
class MetaPerformanceGate:
    mttd_seconds: float = 300.0
    mttr_seconds: float = 600.0
