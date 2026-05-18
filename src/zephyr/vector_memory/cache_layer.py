# [BLUEPRINT] MOD-INF-039 | docs/03_modules/l01_infrastructure/local-model/blueprint.md | §3.5
# [MODULE] zephyr.local_model.cache_layer
# [CONSUMERS] in_process_vector_memory
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.local_model.cache_layer import CacheLayer, CacheLayer as _CacheLayer  # noqa: F401

__all__ = ["CacheLayer"]
