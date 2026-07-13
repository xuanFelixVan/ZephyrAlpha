# [DOMAIN] D_ORCHESTRATOR
# [A_module] module_id=MOD-RES_resilience_orchestrator_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.resilience
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""orchestrator.resilience — auto-generated package init.

5.159.4 修复: 死副本文件已删除 (deferred_queue/rollback_manager/hallucination_detector 与顶层重复).
保留 failure_matcher (tests/trading/test_failure_matcher.py 导入).
"""

from . import failure_matcher

__all__ = ["failure_matcher"]
