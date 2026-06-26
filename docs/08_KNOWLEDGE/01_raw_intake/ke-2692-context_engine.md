---
module_id: KE-2595
status: active
title: Context Engine 蓝图 — 四阶段上下文注入
category: module_blueprint
ttl: permanent
---

# Context Engine 蓝图 — 四阶段上下文注入

Context Engine 蓝图 — 四阶段上下文注入

> **module_id**: MOD-CONTEXT_ENGINE | **version**: 0.8.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml)。
> 代码落位：`src/zephyr/context-engine/`（85 个 .py 文件，含 support/assembly/parsing/management 子包，bounded_context=true）。

> **对标**：Anthropic Codified Context（三层记忆模型）+ Google Vertex AI Context Caching（Hot/Warm/Cold）+ Cursor Rules（Always-on Context+Token预算）+ Windsurf Rules（Context Freshness Decay）+ RAG 社区（Multi-Query Retrieval+Dedup+Re-rank）。

---
