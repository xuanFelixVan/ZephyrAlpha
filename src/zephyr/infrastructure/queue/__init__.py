# [A_module] module_id=MOD-INF-queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.queue
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
core.queue — auto-generated package init.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/queue/queue__init__.yaml
"""

from . import task_scheduler

__all__ = ["task_queue", "task_scheduler"]
