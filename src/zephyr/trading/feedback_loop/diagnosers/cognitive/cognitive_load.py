# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.cognitive.cognitive_load
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_cognitive_load | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Cognitive Load Estimator — v0.6.0 R68

Blindspot: Owner cognitive bandwidth not modeled — notification flood causes fatigue.
Risk: R68 — 1-person operator overwhelmed, critical alerts missed.
"""

from dataclasses import dataclass


@dataclass
class CognitiveLoad:
    notifications_per_hour: float = 0.0
    fatigue_score: float = 0.0

    def update(self, new_notifications: int) -> None:
        self.notifications_per_hour = new_notifications
        self.fatigue_score = min(1.0, self.fatigue_score + 0.1 * new_notifications)
