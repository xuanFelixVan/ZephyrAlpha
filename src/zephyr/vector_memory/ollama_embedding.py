# [BLUEPRINT] MOD-INF-039 | docs/03_modules/l01_infrastructure/local-model/blueprint.md | §3.2
# [MODULE] zephyr.local_model.ollama_embedding
# [CONSUMERS] vector_memory.__init__;embedding_router
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.local_model.ollama_embedding import OllamaEmbedder, OllamaEmbedder as _OllamaEmbedder  # noqa: F401

__all__ = ["OllamaEmbedder"]
