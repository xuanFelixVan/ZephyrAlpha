---
module_id: KE-1916
status: active
title: 2.5 Budget Enforcer 集成
category: module_blueprint
ttl: permanent
---

# 2.5 Budget Enforcer 集成

2.5 Budget Enforcer 集成

```yaml
skill_budget:
  per_skill:
    L1_metadata: "~50 tokens (always loaded, 不计入 Skill 预算)"
    L2_body: "~300-500 tokens (Domain) / ~200-300 tokens (Role)"
    L3_references: "~2000-8000 tokens per file (按需, 计入会话预算)"
  combined_budget: "Domain L2 + Role L2 ≤ 800 tokens"
  over_budget_action: "自动降级——只加载 L1 metadata + L2 CRITICAL 规则, L3 全跳过"
```
