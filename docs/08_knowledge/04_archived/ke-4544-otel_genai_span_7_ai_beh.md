---
module_id: KE-4379-------7-ai-beh-000
title: OTel GenAI Span 属性映射（§7 ai_behavior + §6 traces）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# OTel GenAI Span 属性映射（§7 ai_behavior + §6 traces）

OTel GenAI Span 属性映射（§7 ai_behavior + §6 traces）

| OTel GenAI 标准属性 | Telemetry 对应字段 | 映射说明 |
|---------------------|-------------------|---------|
| `gen_ai.operation.name` | `AIBehaviorEvent.event_type` | `chat` / `text_completion` / `tool_call` |
| `gen_ai.provider.name` | `AIBehaviorEvent.labels["provider"]` | `openai` / `anthropic` / `gcp.gen_ai` |
| `gen_ai.request.model` | `AIBehaviorEvent.model_id` | 模型名（如 `gpt-4`） |
| `gen_ai.request.temperature` | `AIBehaviorEvent.labels["temperature"]` | 生成参数 |
| `gen_ai.request.max_tokens` | `AIBehaviorEvent.labels["max_tokens"]` | 最大 token 数 |
| `gen_ai.usage.input_tokens` | `AIBehaviorEvent.input_tokens` | 输入 token 数 |
| `gen_ai.usage.output_tokens` | `AIBehaviorEvent.output_tokens` | 输出 token 数 |
| `gen_ai.response.finish_reason` | `AIBehaviorEvent.labels["finish_reason"]` | `stop` / `length` / `tool_calls` |
| `gen_ai.conversation.id` | `AIBehaviorEvent.labels["conversation_id"]` | 对话/会话 ID |
| `gen_ai.request.seed` | `AIBehaviorEvent.labels["seed"]` | 可复现性种子 |
| `gen_ai.system` | `AIBehaviorEvent.labels["gen_ai_system"]` | 系统标识 |
| `gen_ai.output.type` | `AIBehaviorEvent.labels["output_type"]` | `text` / `json` / `image` |
