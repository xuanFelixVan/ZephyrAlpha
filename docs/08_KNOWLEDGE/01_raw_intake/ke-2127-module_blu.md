---
module_id: KE-2035
status: active
title: 3.1 双嵌入维度路由策略
category: module_blueprint
---

# 3.1 双嵌入维度路由策略

3.1 双嵌入维度路由策略

```
            ┌─────────────────────────────────────┐
            │        EmbeddingRouter               │
            │                                      │
  query ───►│  collection ∈ {decisions, lessons,   │──► BGE-M3 1024d ONNX
            │    knowledge, rules, code_context} ?  │
            │                                      │
            │  collection ∈ {blueprints,            │
            │    session_snapshots,                 │──► bge-small-zh-v1.5 512d
            │    execution_traces} ?                │
            └─────────────────────────────────────┘
```

- **路由依据**：Collection 元数据中的 `embedding_model` 字段
- **切换成本**：同一 Collection 内维度不可混用。若需升级（如 blueprints 512d→1024d），必须全量重嵌入
- **降级策略**：BGE-M3 加载失败 → 全局降级为 bge-small 512d；bge-small 也失败 → InMemory backend
