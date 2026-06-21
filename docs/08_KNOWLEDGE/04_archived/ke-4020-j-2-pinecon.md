---
module_id: KE-3867--------2-------pinecon-000
title: 13.11 J. 测试与验证（2个）——对标 Pinecone Recall Evaluation + Qdrant Validation
category: module_blueprint
---

# 13.11 J. 测试与验证（2个）——对标 Pinecone Recall Evaluation + Qdrant Validation

13.11 J. 测试与验证（2个）——对标 Pinecone Recall Evaluation + Qdrant Validation

> **现状**：VMS 蓝图仅在 Phase 3 提到"混合检索 top-5 精度 > 纯向量 top-5"但没有可执行的测试框架。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 32 | **V-VMS-432** | **无语义搜索准确率 CI 测试**——定义 30-50 条基准查询 + 标准答案(预期 top-3 doc_ids)。CI 每次运行验证 recall@5≥0.8。检索退化了 CI 立即 FAIL，不会静默上线 | 3 | 3 | 4 | 36 🟠 | 每次PR/变更 |
| 33 | **V-VMS-433** | **无 Collection 向量完整性校验**——扫描每个 Collection：所有向量的维度是否与声称一致？metadata 是否缺失必需字段(provenance)？是否有孤立的向量(无对应源文档)？ | 2 | 2 | 3 | 12 🟡 | 定期巡检 |
