---
module_id: KE-3874----------4-------anthro-000
title: 13.2 A. 检索质量与评估（4个）——对标 Anthropic RAG Evaluation + Qdrant Search Quality Metrics
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.2 A. 检索质量与评估（4个）——对标 Anthropic RAG Evaluation + Qdrant Search Quality Metrics

13.2 A. 检索质量与评估（4个）——对标 Anthropic RAG Evaluation + Qdrant Search Quality Metrics

> **现状**：蓝图有 HybridRetriever(Vector+BM25+RRF)+Phase 3 reranker，但**没有定义"好检索"的标准和度量**。Anthropic 的内部 RAG 系统每个检索 pipeline 都配备了 evaluation benchmark；Qdrant 有内置的 search quality scoring。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 1 | **V-VMS-401** | **无检索质量评估 Benchmark**——没有 50 条标准查询 + 预期正确答案的黄金测试集。每次修改 HybridRetriever/更换嵌入模型后，无法知道 recall@5/precision@5/MRR 是升是降 | 4 | 3 | 4 | **48** 🔴 | 任何检索链变更 |
| 2 | **V-VMS-402** | **无 MMR 检索结果多样性控制**——当 AI 搜索"如何初始化 ChromaDB"，top-5 结果可能是同一文档的 5 个相邻段落，浪费上下文窗口。Maximal Marginal Relevance 可按相似度+多样性平衡重排结果 | 3 | 4 | 3 | 36 🔴 | 大文档被分块后检索 |
| 3 | **V-VMS-403** | **无查询改写/扩展**——用户/AI 查询用词可能与存储文档用词不同（"ChromaDB怎么存" vs "PersistentClient初始化"）。查询扩展（同义词/术语映射/子问题拆解）可大幅提升召回 | 3 | 3 | 3 | 27 🟠 | AI用口语化术语检索 |
| 4 | **V-VMS-404** | **无查询意图分类**——不应所有查询走同一条检索链。精确ID查询→不走向量，模糊语义→走向量+BM25，跨Collection关联查询→走 CrossCollectionRetriever。意图分类可减少 30-50% 无效检索 | 2 | 3 | 2 | 12 🟡 | 高频混合操作场景 |
