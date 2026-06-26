---
module_id: KE-3883--------4-------shopify--000
title: 13.4 C. 数据一致性（4个）——对标 Shopify Production RAG Data Pipeline
category: module_blueprint
ttl: permanent
---

# 13.4 C. 数据一致性（4个）——对标 Shopify Production RAG Data Pipeline

13.4 C. 数据一致性（4个）——对标 Shopify Production RAG Data Pipeline

> **现状**：蓝图有 ProvenanceEnforcer 和 WriteTrace 溯源，但缺少向量层面的去重和源数据同步。Shopify 的 RAG pipeline 包含完整的 dedup + staleness detection + re-embedding 触发器。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 9 | **V-VMS-409** | **无向量去重策略**——AI 施工中同一内容可能被多次嵌入（KE 更新后重新写入但旧向量未清理）。去重应基于 content SHA256 指纹判重 + 写入前查重 + 对旧版本向量标记 superseded | 4 | 4 | 3 | **48** 🔴 | 高频写入场景 |
| 10 | **V-VMS-410** | **无 Chunk 间重叠窗口策略**——文档被分块时在边界截断，最后一个 token 属于 chunk A 还是 chunk B 会影响语义完整性。需要 N-token overlap（Anthropic 推荐 10-15% 重叠率）。蓝图 §2 定义了分块策略但无 overlap | 3 | 3 | 2 | 18 🟡 | 长文档分块 |
| 11 | **V-VMS-411** | **无向量与源文档的"过时检测"**——Blueprints/KB 源文件被 AI 修改后，ChromaDB 中对应的旧向量仍然存在。需要：记录 vectors→source_file_version 映射 + 源文件变更时标记对应向量 stale + 触发自动重嵌入 | 4 | 4 | 4 | **64** 🔴 | 蓝图/KE文档频繁变更 |
| 12 | **V-VMS-412** | **无 Collection 级统计仪表板**——每个 Collection 的条目数、存储大小、平均向量范数、嵌入维度分布、最后写入时间。ChromaDB 的 `collection.count()` 太粗粒度。需要结构化统计供 CT-BLUEPRINT-HEALTH 消费 | 2 | 3 | 3 | 18 🟡 | 系统健康巡检 |
