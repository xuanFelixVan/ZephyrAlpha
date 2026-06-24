---
module_id: KE-1836------think-time--------ll-000
status: active
title: 2.25 推理模型 Think-Time 成本感知 + LLM-Free Guard 升级路径
category: module_blueprint
---

# 2.25 推理模型 Think-Time 成本感知 + LLM-Free Guard 升级路径

2.25 推理模型 Think-Time 成本感知 + LLM-Free Guard 升级路径

> **决策 D-024-23（🆕 v0.6.0）**：Reasoning token 的价格是 output token 的 2-3x 且不可见的 think-time 消耗也是成本。v0.5.0 有 reasoning_limit 但没建立 think-time 成本模型。

```yaml
think_time_cost_model:
  description: "Reasoning tokens 和 think-time latency 的量化成本模型"

  providers:
    anthropic_extended_thinking:
      thinking_tokens: "$1-3/MTok (≈ output price × 0.5)"
      budget_tip: "thinking_tokens > task_output_tokens → 思考比产出还贵 → 切换模型"
    openai_o1_o3:
      reasoning_tokens: "隐藏（不返回，但计入 pricing）"
      detection: "actual_charges / visible_tokens → 推算 reasoning token 占比"
      budget_tip: "o1/o3 调用尽量走 batch 路由（batch 价格 50% off）"

  auto_switch:
    trigger: "thinking_tokens > 2× output_tokens AND task 非终审/审计类"
    action: "自动切到 tier_0 或 tier_1 非推理模型"
