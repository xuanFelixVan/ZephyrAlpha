# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.session_learner
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_session_learner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""session_learner.py — 在线学习 (DD114, TASK-020)"""

from dataclasses import dataclass


@dataclass
class LearningEvent:
    ke_id: str
    cited: bool
    success: bool
    timestamp: str


class SessionLearner:
    """Per-session Reinforcement Learning: citation + outcome (DD114)."""

    def __init__(self) -> None:
        self._events: list[LearningEvent] = []
        self._ke_weights: dict[str, float] = {}

    def record(self, ke_id: str, cited: bool, success: bool, timestamp: str = "") -> None:
        self._events.append(LearningEvent(ke_id=ke_id, cited=cited, success=success, timestamp=timestamp))
        delta = 0.1 if cited and success else (-0.05 if not cited else 0.0)
        self._ke_weights[ke_id] = max(0.0, min(1.0, self._ke_weights.get(ke_id, 0.5) + delta))

    def get_weight(self, ke_id: str) -> float:
        return self._ke_weights.get(ke_id, 0.5)
