# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/local_model/blueprint.md | §3.4
# [MODULE] zephyr.integration.local_model.local_model_scheduler
# [DOMAIN] D-KNOWLEDGE
# [DEPENDENCIES] zephyr.integration.local_model.local_model_scheduler
# [CONSUMERS] auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_local_model_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

__all__ = ["LocalModelScheduler"]
