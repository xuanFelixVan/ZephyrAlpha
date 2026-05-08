---
module_id: KE-module_blu-2_6______semantic_cache-000
title: 2.6 语义缓存（Semantic Cache）
category: module_blueprint
---

# 2.6 语义缓存（Semantic Cache）

2.6 语义缓存（Semantic Cache）

> **决策 D-024-07**：缓存是最便宜的性能优化。对齐 Anthropic cache-aware token management——对高频相同/相似请求自动缓存，hit 后零新增 token 消耗。

```yaml
semantic_cache:
  description: "嵌入向量相似度匹配的语义缓存——不仅缓存完全相同的请求，也缓存语义相似的请求"
  backend: "ChromaDB（复用已有向量库，零新增依赖）"
  cache_layers:

    layer_1_prompt_cache:
      description: "System prompt + 上下文哈希 → 缓存 completion"
      strategy: "exact_hash"     # 精确哈希匹配
      ttl: 3600                  # 1 小时
      encryption: "AES-256 at rest"
      hit_ratio_target: 0.40

    layer_2_tool_cache:
      description: "工具调用（API 查询/文件读取等）结果缓存"
      strategy: "param_hash"     # 参数哈希匹配
      ttl: 300                   # 5 分钟
      hit_ratio_target: 0.30

    layer_3_embedding_cache:
      description: "文档嵌入去重——两个 chunk 哈希相同则复用向量"
      strategy: "content_hash"
      ttl: 86400                 # 24 小时

  observability:
    metrics: ["cache_hit_rate", "cache_saved_tokens", "cache_saved_cost"]
    audit: "每次 cache hit 写入 audit trail——证明敏感数据在缓存中加密且按时过期"
```
