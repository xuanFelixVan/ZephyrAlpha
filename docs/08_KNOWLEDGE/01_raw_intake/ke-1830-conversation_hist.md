---
module_id: KE-1739---------conversation-hist-000
status: active
title: 2.19 对话历史税检测（Conversation History Tax Detector）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.19 对话历史税检测（Conversation History Tax Detector）

2.19 对话历史税检测（Conversation History Tax Detector）

> **决策 D-024-17（🆕 v0.5.0）**：Boris Cherny 数据——13% 的 token 浪费来自对话历史重读。长对话中，历史即使全部压缩后仍占上下文大头。Context Engine 的压缩解决"大小"但没解决"价值"——压缩后的历史 tokens 中可能 80% 对当前任务无价值。

```yaml
conversation_history_tax_detector:
  description: "跟踪对话历史中实际被当前 turn 使用的比例——未被引用的历史就是浪费"
  tracking:
    - "total_history_tokens_sent"
    - "history_tokens_referenced"            # LLM 在 response 中实际引用到的历史片段
    - "history_tax_ratio"                    # = sent / referenced
  alert:
    threshold: "history_tax_ratio > 5×"      # 5 倍浪费——发 5000 token 历史只用了 1000 token
    action: "WARN + 建议 /compact-aggressive（仅保留最近 3 轮的失败/上下文/决策摘要）"
  decay_model:
    description: "越远的 turn 价值越低——加权衰减而非均匀压缩"
    weights:
      last_3_turns: 1.0                      # 全部保留
      turns_4_10: 0.3                        # 仅保留决策 + 异常
      turns_11_plus: 0.05                    # 仅保留摘要
  synergy: "联动 Context Engine (MOD-CONTEXT_ENGINE) 的 DocCompressor 加权衰减策略"
  visual: "终端显示 '📜 历史: 12K/15K (80%) | 有效引用: 仅 22%'"
```
