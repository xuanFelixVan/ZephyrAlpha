---
module_id: KE-1509------6-002
title: 14.1 盲点总览（6 项）
category: module_blueprint
ttl: permanent
---

# 14.1 盲点总览（6 项）

14.1 盲点总览（6 项）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase | 专业对标 |
|:---:|:---:|------|:---:|------|
| 🔴 | B51 | **Prompt Injection Defense — 标签式信任传播** | 19 | Microsoft FIDES (2026.4)、Entra AI Gateway |
| 🔴 | B52 | **Structured Output Guarantee — LLM 输出强制校验+自动重试** | 19 | Instructor、PydanticAI |
| 🟠 | B53 | **LLM API 专属速率限制 + Provider 降级** | 19 | OpenAI tiers、LiteLLM router |
| 🟠 | B54 | **Tool Call Parameter Validation — 工具调用参数护栏** | 20 | agent-rbac input_guard |
| 🟡 | B55 | **Prompt Caching Strategy — 上下文缓存策略** | 20 | Anthropic/OpenAI prompt caching |
| 🟡 | B56 | **Multi-Provider Semantic Equivalence Fallback** | 20 | LiteLLM、OpenRouter |
