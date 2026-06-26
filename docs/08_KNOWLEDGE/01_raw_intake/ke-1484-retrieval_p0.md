---
module_id: KE-1394
title: 11.2 Retrieval P0
category: module_blueprint
ttl: permanent
---

# 11.2 Retrieval P0

11.2 Retrieval P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-R1 | 单 Collection 语义检索 | decisions 含 ADR-0016 | `search("ChromaDB 选型", decisions)` | top_1 为 ADR-0016，score > 0.5 |
| P0-R2 | multi_search RRF 融合 | 4 Collection 均有数据 | `multi_search(query, [4 个], "rrf")` | 返回各 Collection top_k + 全局 merged_top_k，按 RRF 分数降序 |
| P0-R3 | RRF vs weighted 一致性 | 同上 | 同 query 分别用 rrf 和 weighted | 两者 top-3 overlap ≥ 2（高相关 query 应稳定） |
| P0-R4 | 过滤器语义正确 | 含 `tags=[archived]` | `search(..., filters=tags_exclude=["archived"])` | 不返回含 archived chunks |
