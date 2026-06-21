# [A_module] module_id=MOD-INT_ollama_embedding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.2
# [MODULE] zephyr.integration.local_model.ollama_embedding
# [CONSUMERS] vector-memory.__init__;embedding_router
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder, OllamaEmbedder as _OllamaEmbedder  # noqa: F401

__all__ = ["OllamaEmbedder"]
