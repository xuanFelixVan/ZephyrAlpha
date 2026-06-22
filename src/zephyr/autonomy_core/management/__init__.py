# [A_module] module_id=MOD-ORC_management | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.integration.context_management.management
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""context-engine.management — auto-generated package init."""

from . import context_evictor, context_rot_model

__all__ = ["context_budget_tracker", "context_evictor", "context_rot_model"]
