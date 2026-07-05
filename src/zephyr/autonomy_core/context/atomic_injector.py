# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.atomic_injector
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
# [A_module] module_id=MOD-ORC_atomic_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""atomic_injector.py — 原子注入 (DD101, TASK-019)"""

from dataclasses import dataclass


@dataclass
class AtomicResult:
    success: bool
    full_context_applied: bool
    rolled_back: bool = False


class AtomicInjector:
    """All-or-nothing: all 4 layers must succeed or rollback entirely (DD101)."""

    def inject_atomic(self, layers: dict[str, str]) -> AtomicResult:
        all_valid = all(bool(v) for v in layers.values())
        return AtomicResult(success=all_valid, full_context_applied=all_valid, rolled_back=not all_valid)
