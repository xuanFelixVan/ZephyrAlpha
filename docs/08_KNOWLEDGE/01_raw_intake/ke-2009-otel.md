---
module_id: KE-1918
status: active
title: 2.5 OTel 语义规范跨模块传播
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.5 OTel 语义规范跨模块传播

2.5 OTel 语义规范跨模块传播

所有跨模块集成调用必须：
- 创建新的 OTel Span，手工设定 `traceparent`/`tracestate`
- 包含 `gen_ai.integration.name` 属性 = 集成契约 ID
- 包含错误状态码（OK/UNAVAILABLE/THROTTLED/DEGRADED）
