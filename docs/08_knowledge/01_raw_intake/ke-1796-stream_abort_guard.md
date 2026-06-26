---
module_id: KE-1705-------stream-abort-guard-000
status: active
title: 2.13 事中控制——Stream Abort Guard
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.13 事中控制——Stream Abort Guard

2.13 事中控制——Stream Abort Guard

> **决策 D-024-11（🆕 v0.4.0）**：Pre-flight Gate 只能管输入端。流式输出中途无法拦截——如果模型开始输出大量无意义内容，预算已被烧掉。Stream Abort Guard 对流式输出做中间 checkpoint（每 500 token）预算二次确认。

```yaml
stream_abort_guard:
  description: "流式输出中途预算二次确认——Pre-flight 场景的缺失互补"
  lifecycle_position: "in_flight"   # 位于 Pre-flight（事前）和 Post-flight（事后）之间

  checkpoints:
    frequency: 500                   # 每 500 output token 做一次预算检查
    checks:
      - condition: "remaining_budget - estimated_completion_cost < 0"
        action: "IMMEDIATE_ABORT——发送 abort signal 给 provider + 记录 partial output"
      - condition: "output_quality_gate.score < 0.3 AND tokens_emitted > 200"
        action: "ABORT_AND_RETRY——切回 input 用更便宜模型重试"
      - condition: "cumulative_response_too_verbose（token_count > expected × 3）"
        action: "ABORT_WITH_WARNING——日志 '响应过于冗长，建议添加 'be concise' 指令'"

  partial_output_handling:
    on_abort: "保存已输出的 partial_response 到 context_budget_tracker"
    resume_strategy: "下次调用时 append partial_response 到 system prompt '之前的回答在 [X] token 处中断'"

  provider_integration:
    anthropic: "streaming SSE — 监听 stop_reason='max_tokens'"
    openai: "streaming SSE — 监听 finish_reason='length'"
    google: "streaming SSE — 监听 finishReason='MAX_TOKENS'"
    deepseek: "streaming SSE — 同 OpenAI 协议"
```
