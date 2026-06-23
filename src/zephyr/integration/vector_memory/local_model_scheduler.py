# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.4
# [MODULE] zephyr.integration.local_model.local_model_scheduler
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.local_model_scheduler
# [CONSUMERS] auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_local_model_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

__all__ = ["LocalModelScheduler"]
