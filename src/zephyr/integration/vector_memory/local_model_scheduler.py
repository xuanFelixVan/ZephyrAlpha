# [A_module] module_id=MOD-INT_local_model_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.4
# [MODULE] zephyr.integration.local_model.local_model_scheduler
# [CONSUMERS] auto_runtime_core
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler, LocalModelScheduler as _LocalModelScheduler  # noqa: F401

__all__ = ["LocalModelScheduler"]
