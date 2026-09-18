# [A_module] module_id=MOD-INF-reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.reliability
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
core.reliability — auto-generated package init.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/reliability/reliability__init__.yaml
"""

from . import circuit_breaker, context_guard

__all__ = ["circuit_breaker", "context_guard"]
