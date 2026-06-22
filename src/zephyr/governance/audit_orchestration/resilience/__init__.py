# [A_module] module_id=MOD-RES_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §
"""orchestrator.resilience — auto-generated package init."""

from . import deferred_queue, failure_matcher

__all__ = ["deferred_queue", "failure_matcher", "hallucination_detector", "rollback_manager"]
