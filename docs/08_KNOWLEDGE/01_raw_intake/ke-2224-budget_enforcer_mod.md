---
module_id: KE-2131-------mod--003
status: active
title: 3.5 Budget Enforcer 集成（对接 MOD-INF-024）
category: module_blueprint
ttl: permanent
---

# 3.5 Budget Enforcer 集成（对接 MOD-INF-024）

3.5 Budget Enforcer 集成（对接 MOD-INF-024）

```yaml
skill_budget:
  description: "Skill 执行的 token 消耗计入会话预算"
  budget_per_skill:
    L1_metadata: "~50 tokens（always loaded，不计入 Skill 预算）"
    L2_body: "~300-500 tokens（Domain Skill）/ ~200-300 tokens（Role Skill）"
    L3_references: "~2000-8000 tokens per file（按需加载，计入会话预算）"
  combined_budget: "Domain Skill L2 + Role Skill L2 ≤ 800 tokens（保证在预算内）"
  over_budget_action: "自动触发降级——只加载 L1 metadata + L2 的 CRITICAL 规则，L3 全部跳过"
```
