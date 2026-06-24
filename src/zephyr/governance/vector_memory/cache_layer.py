# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/local_model/blueprint.md | §3.5
# [MODULE] zephyr.integration.local_model.cache_layer
# [DOMAIN] D-KNOWLEDGE
# [DEPENDENCIES] zephyr.integration.local_model.cache_layer
# [CONSUMERS] in_process_vector_memory
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_cache_layer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from zephyr.integration.local_model.cache_layer import CacheLayer

__all__ = ["CacheLayer"]
