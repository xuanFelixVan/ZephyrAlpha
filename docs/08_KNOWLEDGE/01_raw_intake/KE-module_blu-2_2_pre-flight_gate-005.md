---
module_id: KE-module_blu-2_2_pre-flight_gate-005
title: 2.2 Pre-flight Gate（事前拦截门）
category: module_blueprint
---

# 2.2 Pre-flight Gate（事前拦截门）

2.2 Pre-flight Gate（事前拦截门）

> **决策 D-024-03**：专业机构要求 pre-request blocking——在 tokens 被实际消耗之前就拦截。Pre-flight Gate 是 v0.3.0 新增的核心组件，位于每次 API 调用的咽喉位置。

```yaml
pre_flight_gate:
  position: "每次 API 调用前，在任何 token 消耗之前执行"
  checks:
    - check_id: "global_budget_check"
      rule: "本周 global soft_limit 剩余 < 预估消耗 × 1.2"
      on_fail: "DENY → 建议推迟到下周"
      exception: "Owner 临时提额令可覆盖"

    - check_id: "session_budget_check"
      rule: "会话 hard_limit 剩余 < 预估消耗"
      on_fail: "DEGRADE → 强制 /compact 后再试"

    - check_id: "task_budget_check"
      rule: "任务 hard_limit 剩余 < 预估消耗"
      on_fail: "DEGRADE → 任务拆分 + 委托子任务到新对话"

    - check_id: "turn_budget_check"
      rule: "本轮 soft_limit 剩余 < 预估消耗"
      on_fail: "WARN → 检查循环指纹 + 建议跳过冗余工具调用"

    - check_id: "request_size_check"
      rule: "预估 input_tokens > request_level.input_limit"
      on_fail: "DENY → 请求太大，建议拆分"

    - check_id: "cost_threshold_check"
      rule: "预估单次调用成本 > $0.50"
      on_fail: "DEGRADE → 自动切换到 Tier-1 模型"

  estimator: "TikToken-based + model-specific tokenizer，误差 < 10%"
  decision_outcomes: ["ALLOW", "WARN", "DEGRADE", "DENY", "BORROW"]

  # Borrow 机制：从 Budget Pool 临时借用
  borrow:
    enabled: true
    max_borrow_ratio: 0.20       # 最多借 20% 其他任务预算
    payback: "同 Session 下次任务少分 30% 直到还清"
```
