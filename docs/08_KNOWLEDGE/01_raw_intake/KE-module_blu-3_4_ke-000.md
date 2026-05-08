---
module_id: KE-module_blu-3_4_ke-000
title: 3.4 KE 索引结构
category: module_blueprint
---

# 3.4 KE 索引结构

3.4 KE 索引结构

KE 支持三种检索方式：

| 检索方式 | 存储层 | 适用场景 |
|---------|--------|---------|
| **向量语义检索**（主） | ChromaDB `ke_entries` Collection | "找一个关于任务分解最佳实践的知识" |
| **标签精确匹配** | SQLite `knowledge_entries.tags` JSON | "所有 domain=infra AND layer=L01 的知识" |
| **全文关键词搜索** | SQLite FTS5 全文索引 | "正文中包含 'ChromaDB' 的知识" |

检索优先级：向量语义（Top-K） → 标签过滤（缩小范围） → 全文搜索（兜底）
