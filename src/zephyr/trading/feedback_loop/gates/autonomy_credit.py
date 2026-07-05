# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.autonomy_credit
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_autonomy_credit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Autonomy Credit System — v0.7.0 R87

Blindspot: No decay of autonomy trust over time.
Risk: R87 — Once-trusted subsystem never re-evaluated.
"""

from dataclasses import dataclass


@dataclass
class AutonomyCredit:
    score: float = 100.0
    decay_per_day: float = 1.0
