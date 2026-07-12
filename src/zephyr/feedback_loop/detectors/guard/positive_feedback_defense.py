# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.positive_feedback_defense
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_positive_feedback_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Positive Feedback Defense — v0.4.0 R28

Blindspot: FLE repair triggers metric improvement that triggers new FLE cycle; infinite loop.
Risk: R28 — Positive feedback loop between FLE action and metric causes runaway repairs.
"""

from dataclasses import dataclass, field


@dataclass
class PositiveFeedbackDefense:
    recent_actions: list[str] = field(default_factory=list)

    def detect_loop(self, action: str) -> bool:
        self.recent_actions.append(action)
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
        return self.recent_actions.count(action) >= 3
