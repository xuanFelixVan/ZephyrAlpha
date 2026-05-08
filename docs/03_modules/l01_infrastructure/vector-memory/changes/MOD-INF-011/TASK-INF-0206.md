---
task_id: "TASK-INF-0206"
source_blueprint: "MOD-INF-011"
source_section: "§3.2 混合检索架构 (HybridRetriever)"

title: "混合检索架构实现——HybridRetriever: Vector(HNSW) + BM25 + RRF 融合 + score threshold"
description: |
  实现蓝图 §3.2 定义的混合检索架构：
  1. dense_hits: ChromaDB HNSW 向量检索——k*3 候选召回（首次粗筛）
  2. sparse_hits: BM25 关键词检索——基于 content 文本的 TF-IDF 倒排索引
  3. RRF (Reciprocal Rank Fusion): score = Σ(1 / (k + rank_i))，k=60——融合 dense 和 sparse 排序
  4. score threshold filter: fused_hits.score ≥ 0.6 的保留，取 top-k
  5. RetrievalTrace 返回协议（V-VMS-513）：每次检索返回 score_breakdown: {dense, sparse, rrf} + why_top 解释
  6. 查询超时机制（V-VMS-511）：search(timeout_ms=2000) → 超时后返回当前最佳结果 + 标注 partial=True
  7. 检索结果时间衰减权重（V-VMS-417）：RRF 融合阶段加入 time_decay = e^(-λ·age_days)，λ 由 Collection 级 decay_rate 决定
  8. 可插拔 reranker 预留接口（Phase 3）：cross-encoder（BGE-Reranker-v2-m3）二次精排
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"
    description: "HybridRetriever 类——search(query, collection, k, timeout_ms) → list[ScoredHit] + 内部 dense_search() / sparse_search() / rrf_fusion() / score_filter()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\hybrid_retriever.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——ScoredHit / RetrievalTrace 数据模型"
  - module_id: "ADR-0031"
    section: "§4.2"
    reason: "ChromaDB HNSW 检索——dense recall 依据"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§3.2 混合检索架构——Dense+Sparse+RRF 三段式 pipeline + RRF k=60 + score_threshold 0.6 + Python 伪代码"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    reason: "EmbeddingRouter.embed()——dense search 嵌入生产"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "hybrid_search(query, collection, k=5) 返回 list[ScoredHit]——每个 hit 含 content + metadata + score + provenance"
  - "dense_hits 候选数为 k*3（=15）——Chromadb query(n_results=k*3)"
  - "sparse_hits 使用 BM25 score 排序——关键词匹配加权"
  - "RRF 融合 score = Σ(1 / (60 + rank_i))——dense 和 sparse rank 取倒数求和"
  - "score_threshold=0.6——分数低于 0.6 的结果被过滤"
  - "最终返回 ≤ k 条结果——满足 score ≥ 0.6 的取 top-k"
  - "search(timeout_ms=2000) 超时后返回当前最佳结果 + ScoredHit.partial=True"
  - "RetrievalTrace 包含 score_breakdown: {dense_score, sparse_score, rrf_score}"
  - "RetrievalTrace 包含 why_top: 'matched: governance, rules, CBAC'"
  - "time_decay 已集成到 RRF 公式——age_days > 30 则衰减权重乘以 0.5"

rollback_instructions: |
  1. 如果混合检索精度低于纯向量检索 → 设置 VMS_SEARCH_MODE=dense_only 环境变量（回退到纯向量模式）
  2. 删除 D:\ZephyrAlpha\src\zephyr\vector_memory\hybrid_retriever.py
  3. 如果 BM25 索引导致启动内存飙升 → 禁用稀疏检索（设置 sparse_enabled=False）

depends_on:
  - "TASK-INF-0204"
  - "TASK-INF-0202"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
