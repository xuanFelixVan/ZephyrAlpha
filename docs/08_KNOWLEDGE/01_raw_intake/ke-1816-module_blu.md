---
module_id: KE-1725
status: active
title: 2.16 预算策略沙盘 + 策略版本管理
category: module_blueprint
ttl: permanent
---

# 2.16 预算策略沙盘 + 策略版本管理

2.16 预算策略沙盘 + 策略版本管理

> **决策 D-024-14（🆕 v0.4.0）**：你怎么知道五级预算+六级降级不会把系统卡死？预算策略需要在不上线的情况下验证——dry-run 模拟路径。策略变更需要版本管理——改坏了可以回滚。

```yaml
policy_sandbox:
  description: "预算策略的 dry-run 模拟环境——不实际调用 AI，模拟预算消耗路径"
  trigger: "budget_policy.yaml 变更后自动执行 OR `zephyr budget sandbox --scenario aggressive`"

  scenarios:
    low_complexity:
      tasks: 20
      task_type: "lint_fix"
      simulation: "模拟单天 20 个 Lint 修复任务——验证 tier_0_free 是否被正确路由"
      expected: "全部走 tier_0，零成本"

    medium_load:
      tasks: 50
      task_type: "mixed"
      simulation: "模拟中等施工量——50 个混合任务中包含 5 个需要升级到 tier_2 的复杂任务"
      expected: "tier_0 处理 45 个，tier_1 处理 3 个，tier_2 处理 2 个"

    budget_exhaustion:
      tasks: 100
      task_type: "heavy_refactor"
      simulation: "模拟预算耗尽场景——连续大规模重构直到触发 L5_halt"
      expected: "系统正确执行降级链且不进入 spiral"

    runaway_agent:
      tasks: 10
      task_type: "runaway_simulation"
      simulation: "模拟一个 Agent 在单个 Task 上持续重试——触发 per-agent sub-pool 限制"
      expected: "sub-pool 触顶后 spillover 被全局池 60% 总预算限制截断"

  output: "sandbox 执行后生成 `budget_sandbox_report.md`——包括通过/警告/失败的 checklist"

policy_versioning:
  description: "budget_policy.yaml 的版本管理——改坏了可以回滚"
  storage: "config/budget_policy_history/{version}/budget_policy.yaml"
  auto_version: "每次 git commit 时在 pre-commit hook 中快照当前 policy"
  rollback: "zephyr budget policy rollback --version v{N}"
  diff: "zephyr budget policy diff --v1 v2 — 对比两个版本的策略差异"
```
