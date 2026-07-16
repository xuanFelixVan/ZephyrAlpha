# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_outcome_tracker
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""context_outcome_tracker.py — 因果链追踪 (B14, DD88, TASK-017)"""

from dataclasses import dataclass


@dataclass
class ContextOutcomeLink:
    context_block_id: str
    agent_actions: list[str]
    action_successes: list[bool]
    success_rate: float = 0.0
    suspect: bool = False


class ContextOutcomeTracker:
    """ContextBlock -> Agent Action -> Action Success 三级因果关联 (DD88)."""

    def __init__(self) -> None:
        self._links: dict[str, ContextOutcomeLink] = {}

    def record(self, context_id: str, actions: list[str], successes: list[bool]) -> ContextOutcomeLink:
        rate = sum(successes) / max(1, len(successes))
        link = ContextOutcomeLink(
            context_block_id=context_id,
            agent_actions=actions,
            action_successes=successes,
            success_rate=round(rate, 3),
            suspect=rate < 0.5,
        )
        self._links[context_id] = link
        return link

    def low_success_ke(self) -> list[str]:
        return [k for k, v in self._links.items() if v.suspect]
