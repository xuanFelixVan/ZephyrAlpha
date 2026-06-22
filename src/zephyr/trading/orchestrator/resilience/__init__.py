# [A_module] module_id=MOD-RES_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.integration.runtime_core.orchestrator.resilience
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""orchestrator.resilience — auto-generated package init."""

from . import deferred_queue, failure_matcher

__all__ = ["deferred_queue", "failure_matcher", "hallucination_detector", "rollback_manager"]
