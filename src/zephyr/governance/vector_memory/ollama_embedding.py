# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/local_model/blueprint.md | §3.2
# [MODULE] zephyr.integration.local_model.ollama_embedding
# [DOMAIN] D-KNOWLEDGE
# [DEPENDENCIES] zephyr.integration.local_model.ollama_embedding
# [CONSUMERS] vector-memory.__init__;embedding_router
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_ollama_embedding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder

__all__ = ["OllamaEmbedder"]
