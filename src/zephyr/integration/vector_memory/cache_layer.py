# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain_integration/blueprint.md | §3.5
# [MODULE] zephyr.integration.vector_memory.cache_layer
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.cache_layer
# [CONSUMERS] in_process_vector_memory
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.integration.local_model.cache_layer import CacheLayer

__all__ = ["CacheLayer"]
