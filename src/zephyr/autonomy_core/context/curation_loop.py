# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.curation_loop
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
# [A_module] module_id=MOD-ORC_curation_loop | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
curation_loop.py — Per-Turn Curation 策展 (DD10, TASK-014 beta b)
==================================================================
多轮对话中不重复注入已注入的 KE，渐进式策展上下文。
"""

from dataclasses import dataclass, field


@dataclass
class CurationRecord:
    turn: int
    injected_ke_ids: list[str] = field(default_factory=list)
    token_count: int = 0
    timestamp: str = ""


class CurationLoop:
    """Per-Turn 渐进策展器 (DD10)。

    追踪已注入的 KE ID，确保后续 turn 不重复注入。

    Using::

        loop = CurationLoop()
        ke_ids = loop.select_ke(["KE-001", "KE-002", "KE-003"], turn=1)
        ke_ids = loop.select_ke(["KE-001", "KE-004"], turn=2)
        # KE-001 skipped on turn 2 — already injected on turn 1
    """

    def __init__(self) -> None:
        self._history: dict[int, CurationRecord] = {}

    def select_ke(self, ke_ids: list[str], turn: int) -> list[str]:
        seen = self._collect_seen_ids(max_turn=turn - 1)
        fresh = [k for k in ke_ids if k not in seen]
        self._history[turn] = CurationRecord(
            turn=turn,
            injected_ke_ids=fresh,
            token_count=len(fresh) * 100,
        )
        return fresh

    def _collect_seen_ids(self, max_turn: int) -> set[str]:
        seen: set[str] = set()
        for t in range(1, max_turn + 1):
            record = self._history.get(t)
            if record:
                seen.update(record.injected_ke_ids)
        return seen

    def get_history(self) -> dict[int, CurationRecord]:
        return dict(self._history)

    def reset(self) -> None:
        self._history.clear()
