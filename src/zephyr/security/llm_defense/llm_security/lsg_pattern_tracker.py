# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.lsg_pattern_tracker
# [DOMAIN] D_AUTONOMY_CORE
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
# [A_module] module_id=MOD-ORC_lsg_pattern_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20, DD94, TASK-017)"""

from collections import Counter
from dataclasses import dataclass


@dataclass
class LSGRejectionPattern:
    reason_code: str
    count: int
    same_pattern_3x: bool
    cross_session_10x: bool
    action_needed: str


class LSGPatternTracker:
    """LSG rejection_reason_code tracking; 3x→retry; 10x cross-session → escalate (DD94)."""

    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._cross_session: Counter[str] = Counter()

    def track_rejection(self, reason_code: str) -> LSGRejectionPattern:
        self._counters[reason_code] += 1
        count = self._counters[reason_code]
        return LSGRejectionPattern(
            reason_code=reason_code,
            count=count,
            same_pattern_3x=count >= 3,
            cross_session_10x=self._cross_session.get(reason_code, 0) >= 10,
            action_needed="rebuild" if count >= 3 else "retry" if count >= 2 else "none",
        )
