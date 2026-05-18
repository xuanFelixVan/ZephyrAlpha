# [BLUEPRINT] MOD-INF-039 | docs/03_modules/l01_infrastructure/local-model/blueprint.md | §3.1
# [MODULE] zephyr.local_model.embedding_router
# [INVARIANTS] 双后端嵌入路由;降级链BGE-M3→bge-small→InMemory
# [MODIFY-GUARD] 嵌入维度映射变更需同步MOD-INF-011
# [CONSUMERS] in_process_vector_memory;hybrid_retriever;auto_runtime_core;skill_router
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.local_model.embedding_router import EmbeddingRouter, EmbeddingRouter as _EmbeddingRouter  # noqa: F401

__all__ = ["EmbeddingRouter"]
