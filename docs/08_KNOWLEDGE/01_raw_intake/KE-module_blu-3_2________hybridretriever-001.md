---
module_id: KE-module_blu-3_2________hybridretriever-001
title: 3.2 混合检索架构（HybridRetriever）
category: module_blueprint
---

# 3.2 混合检索架构（HybridRetriever）

3.2 混合检索架构（HybridRetriever）

```python
def hybrid_search(query: str, collection: str, k: int) -> list[ScoredHit]:
    # Stage 1: 多路召回
    dense_hits  = collection.query(query_embeddings=BGE_M3(query), n_results=k*3)
    sparse_hits = bm25_search(query, collection, k*3)

    # Stage 2: RRF 融合
    fused = reciprocal_rank_fusion(dense_hits, sparse_hits, k=60)

    # Stage 3: score filter
    return [h for h in fused if h.score >= 0.6][:k]
```

- RRF (Reciprocal Rank Fusion)：`score = Σ(1 / (k + rank_i))`，k=60
- 可插拔 reranker（Phase 3）：cross-encoder（BGE-Reranker-v2-m3）对融合结果二次精排

---
