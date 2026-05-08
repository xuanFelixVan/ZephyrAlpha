---
module_id: KE-module_blu-12_2_w3c_tracecontext-000
title: 12.2 W3C TraceContext 传播
category: module_blueprint
---

# 12.2 W3C TraceContext 传播

12.2 W3C TraceContext 传播

跨模块调用时传播 TraceContext，确保端到端追踪不断裂：

- 所有 ContractBus 调用自动注入 `traceparent` + `tracestate`
- 所有事件总线消息携带 `trace_context` 字段
- 与 `behavior_audit_logger.py` 集成，审计日志关联 Trace ID

---
