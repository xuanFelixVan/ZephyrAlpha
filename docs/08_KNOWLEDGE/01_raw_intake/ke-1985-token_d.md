---
module_id: KE-1894---------token-----------d--003
status: active
title: 2.4 经济护栏 —— Token预算与成本控制（决策 D-022-03）
category: module_blueprint
---

# 2.4 经济护栏 —— Token预算与成本控制（决策 D-022-03）

2.4 经济护栏 —— Token预算与成本控制（决策 D-022-03）

> **决策 D-022-03**：每个任务启动前必须设置 Token 预算上限。预算超限触发 auto_guard，预算耗尽触发 blocked。引入模型降级策略（Model Cascading）——不同升级级别消耗不同成本的模型。
>
> **决策依据**：87%的Agent成本超支来自过度自主（AICosts.ai 2025）。1人+AI维护场景下，经济护栏是生死线。对标 Claude Code 的 token budget + Anthropic 的 model cascading。

```yaml
economic_guardrails:
  # === 预算层级 ===
  budgets:
    task_level:
      default_max_tokens: 100000
      auto_guard_warning_at: "80%"
      blocked_limit_at: "100%"
      scope: "单任务生命周期内所有操作（含委托子任务）"

    delegation_level:
      default_max_tokens: 30000
      scope: "单次委托的子任务预算"

    daily_level:
      default_max_tokens: 500000
      scope: "每日全局上限（可配置）"

    monthly_level:
      default_max_spend_usd: 50
      scope: "LLM API 月度硬顶（在 Provider 侧设置）"

  # === 模型降级策略（Model Cascading） ===
  model_cascading:
    autonomous:
      model: "sonnet"  # 性价比模型
      reason: "95%操作用便宜模型"
    auto_guard:
      model: "sonnet"  # 后验用便宜模型
      verify_model: "opus"  # 护栏校验用顶级模型（小量Token）
      reason: "校验比执行更需要准确性"
    blocked:
      model: "N/A"  # 不消耗
      reason: "被阻断，无模型调用"

  # === 成本追踪 ===
  cost_tracking:
    granularity: "per_task, per_delegation, per_session"
    storage: "Audit Trail (MOD-INF-020) JSONL"
    fields: ["task_id", "tokens_used", "estimated_cost_usd", "model_used", "budget_remaining"]

  # === 预算继承 ===
  budget_inheritance:
    rule: "委托子任务从父任务预算中扣除"
    check: "父任务剩余预算 >= 子任务预估消耗"
    insufficient_action: "子任务降级（用更便宜模型）或 父任务升级 blocked"
```

---
