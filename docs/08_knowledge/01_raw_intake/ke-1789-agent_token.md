---
module_id: KE-1698---------agent----token-003
status: active
title: 2.12 经济护栏——跨 Agent 链的 Token 预算
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.12 经济护栏——跨 Agent 链的 Token 预算

2.12 经济护栏——跨 Agent 链的 Token 预算

> **对标**：MOD-INF-022 §2.4 Token 预算 + AICosts.ai 87% 成本超支来自过度自主。

```yaml
a2a_economics:
  # === 委托代价评估 ===
  delegation_cost:
    overhead_tokens: "每次 A2A 委托固定开销 ≈ 500 tokens（上下文包 + ACK）"
    breakeven_rule: "预估委托省下的 tokens > overhead_tokens × 2 → 委托值得"
    auto_reject: "预估 cost > benefit → Coordinator 拒绝委托 → 当前 Agent 自行处理或拆分子任务"

  # === 全链路 Token 预算 ===
  chain_budget:
    root_task_budget: "由 MOD-INF-022 economic_guardrails 定义"
    delegation_budget: "从 root 预算中扣除——parent.remaining >= child.estimated × 1.2"
    hard_cap: "全链路 Token 耗尽 → 剩余子任务全部 CANCELED → 通知 Owner"

  # === 模型路由 ===
  model_routing:
    autonomous_agent: "sonnet（性价比模型）— 95% 操作"
    auto_guard_scenario: "sonnet 执行 + opus 校验"
    blocked_scenario: "不消耗 — 等待 Owner"
```
