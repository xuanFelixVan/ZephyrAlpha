# [A_module] module_id=MOD-DAT_cache_layer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.5
# [MODULE] zephyr.integration.local_model.cache_layer
# [CONSUMERS] in_process_vector_memory
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [ERROR_CONTRACT]
# [TESTS]

from zephyr.integration.local_model.cache_layer import CacheLayer

__all__ = ["CacheLayer"]
