# [A_module] module_id=MOD-INF-impact | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.impact
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
core.impact — auto-generated package init.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/impact/impact__init__.yaml
"""

from . import impact_propagator, llm_impact_analyzer

__all__ = ["impact_propagator", "llm_impact_analyzer"]
