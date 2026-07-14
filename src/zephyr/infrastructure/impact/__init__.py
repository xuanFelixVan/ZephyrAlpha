# [A_module] module_id=MOD-INF_impact | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.impact
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""core.impact — auto-generated package init."""

from . import impact_propagator, llm_impact_analyzer

__all__ = ["impact_propagator", "llm_impact_analyzer"]
