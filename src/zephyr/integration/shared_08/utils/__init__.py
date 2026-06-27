# [A_module] module_id=MOD-INT_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.utils
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""shared.utils — auto-generated package init."""

from . import context

__all__ = ["context", "db_utils", "diff_utils", "migration", "pagination", "testing", "time_utils"]
