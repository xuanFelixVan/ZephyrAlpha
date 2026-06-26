---
module_id: KE-1345----slo-experimental-chrom-000
title: 10.1 稳态 SLO（experimental，ChromaDB 已加载完毕后）
category: module_blueprint
ttl: permanent
---

# 10.1 稳态 SLO（experimental，ChromaDB 已加载完毕后）

10.1 稳态 SLO（experimental，ChromaDB 已加载完毕后）

| 指标 | 目标 | 测试条件 |
|------|------|---------|
| `search()` p50 延迟 | ≤ 80 ms | top_k=10，数据量 < 50k chunks |
| `search()` p95 延迟 | ≤ 250 ms | 同上 |
| `multi_search()` p50 延迟 | ≤ 200 ms | 4 个 Collection，top_k_per=5，RRF 融合 |
| `multi_search()` p95 延迟 | ≤ 500 ms | 同上 |
| `sync_document()` 单文件 | ≤ 300 ms | 含 embedding |
| `bulk_bootstrap()` 稳态吞吐 | ≥ 50 docs/s | batch_size=50 |
| 内存占用（稳态） | ≤ 700 MB | 含模型 + 元数据索引 |
