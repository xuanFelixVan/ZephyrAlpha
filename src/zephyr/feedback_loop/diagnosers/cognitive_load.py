# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.cognitive_load

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
