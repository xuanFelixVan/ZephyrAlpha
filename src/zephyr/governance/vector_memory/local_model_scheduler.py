# [A_module] module_id=MOD-DAT_local_model_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.4
# [MODULE] zephyr.integration.local_model.local_model_scheduler
# [CONSUMERS] auto_runtime_core
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [ERROR_CONTRACT]
# [TESTS]

from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

__all__ = ["LocalModelScheduler"]
