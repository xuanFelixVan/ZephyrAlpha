# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] zephyr.integration.local_model
# [DOMAIN] D_INTEGRATION
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_integration/algo_flow/local_model__init__.yaml
"""

from zephyr.integration.local_model.cache_layer import CacheLayer
from zephyr.integration.local_model.deepseek_chat import DeepSeekChat
from zephyr.integration.local_model.embedding_router import EmbeddingRouter
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
from zephyr.integration.local_model.ollama_chat import OllamaChat
from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder

__all__ = [
    "CacheLayer",
    "EmbeddingRouter",
    "LocalModelScheduler",
    "OllamaChat",
    "OllamaEmbedder",
    "DeepSeekChat",
    "cache_layer",
    "embedding_router",
    "local_model_scheduler",
    "ollama_chat",
    "ollama_embedding",
    "deepseek_chat",
]
