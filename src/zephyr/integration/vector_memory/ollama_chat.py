# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain_integration/local_model/blueprint.md | §3.3
# [MODULE] zephyr.integration.vector_memory.ollama_chat
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.ollama_chat
# [CONSUMERS] local_model_scheduler;auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_ollama_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.integration.local_model.ollama_chat import OllamaChat

__all__ = ["OllamaChat"]
