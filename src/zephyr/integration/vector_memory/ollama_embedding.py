# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain_integration/blueprint.md | §3.2
# [MODULE] zephyr.integration.vector_memory.ollama_embedding
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.ollama_embedding
# [CONSUMERS] vector-memory.__init__;embedding_router
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_ollama_embedding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder

__all__ = ["OllamaEmbedder"]
