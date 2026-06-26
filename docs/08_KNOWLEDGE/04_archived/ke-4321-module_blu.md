---
module_id: KE-4161
title: 6.1 模块接口契约
category: module_blueprint
ttl: permanent
---

# 6.1 模块接口契约

6.1 模块接口契约

| 模块 | 接口 | 调用方 |
|------|------|------|
| CollectionManager | `create_collection(name, dim, chunk_strategy, ttl)`, `migrate_collection(from, to)`, `archive_collection(name)` | Phase 2 施工脚本 |
| EmbeddingRouter | `embed(text, collection_name) -> ndarray` | InProcessVectorMemory, HybridRetriever |
| HybridRetriever | `search(query, collection, k) -> list[ScoredHit]` | VectorBridge → CE |
| ProvenanceEnforcer | `validate(WriteTrace) -> bool`, `attach(vector_id, provenance)` | 所有写入方 |
| IndexHealthMonitor | `check_all() -> HealthReport`, `auto_repair(collection)` | Phase 4 cron |
| RetrievalFeedback | `record(hit_id, was_useful: bool, task_id)` | FLE (auto_evolution.py) |
| CacheLayer | `get_embedding(text_hash) -> ndarray | None`, `put_embedding(text_hash, vec)` | EmbeddingRouter |

---
