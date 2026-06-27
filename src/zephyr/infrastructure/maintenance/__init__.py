# [A_module] module_id=MOD-INF_maintenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-115 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.maintenance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""core.maintenance — auto-generated package init."""

from . import autonomy_monitor, dogfooding, handbook, zero_config

__all__ = ["autonomy_monitor", "dogfooding", "handbook", "zero_config"]
