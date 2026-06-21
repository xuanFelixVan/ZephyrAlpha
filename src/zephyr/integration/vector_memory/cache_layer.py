# [A_module] module_id=MOD-INT_cache_layer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.5
# [MODULE] zephyr.integration.local_model.cache_layer
# [CONSUMERS] in_process_vector_memory
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.integration.local_model.cache_layer import CacheLayer, CacheLayer as _CacheLayer  # noqa: F401

__all__ = ["CacheLayer"]
