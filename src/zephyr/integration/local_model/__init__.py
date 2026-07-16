# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain-integration/local-model/blueprint.md
# [MODULE] zephyr.integration.local_model
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from zephyr.integration.local_model.cache_layer import CacheLayer
from zephyr.integration.local_model.embedding_router import EmbeddingRouter
from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler
from zephyr.integration.local_model.ollama_chat import OllamaChat
from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder
from zephyr.integration.local_model.deepseek_chat import DeepSeekChat

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
