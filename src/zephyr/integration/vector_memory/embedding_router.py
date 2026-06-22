# [A_module] module_id=MOD-INT_embedding_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.embedding_router
# [INVARIANTS] 双后端嵌入路由;降级链BGE-M3→bge-small→InMemory
# [MODIFY-GUARD] 嵌入维度映射变更需同步MOD-INF-011
# [CONSUMERS] in_process_vector_memory;hybrid_retriever;auto_runtime_core;skill_router
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.integration.local_model.embedding_router import EmbeddingRouter

__all__ = ["EmbeddingRouter"]
