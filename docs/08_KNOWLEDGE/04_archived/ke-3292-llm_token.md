---
module_id: KE-3180
title: 11.2 LLM Token 预算
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 11.2 LLM Token 预算

11.2 LLM Token 预算

| 类型 | 月预算（$） | 监控指标 |
|------|-----------|---------|
| Cursor IDE 内置 | $20-40（订阅固定） | Cursor 用量面板 |
| Runtime API（当前） | ~$5 | `zephyr_llm_tokens_total` |
| Runtime API（AI Operator 激活后） | ~$100-200 | 同上 |
| 便宜模型（Kimi/DeepSeek） | ~$20-50 | 同上 |
| **月度总上限** | **~$200** | Grafana 月报警板 |
