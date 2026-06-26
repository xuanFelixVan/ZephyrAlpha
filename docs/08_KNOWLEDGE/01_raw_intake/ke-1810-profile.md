---
module_id: KE-1719--------profile-000
status: active
title: 2.15 环境感知预算 Profile
category: module_blueprint
ttl: permanent
---

# 2.15 环境感知预算 Profile

2.15 环境感知预算 Profile

> **决策 D-024-13（🆕 v0.4.0）**：业界标准实践——dev 环境永远只用最便宜模型，prod 才开全能力。Solo maintainer 最容易在 dev 调试时不小心烧掉一周预算。

```yaml
env_aware_budget_profiles:
  description: "根据环境自动切换预算策略——不需要手动切换 model/router 配置"
  detection: "环境变量 ZEPHYR_ENV 或自动检测（IDE 集成 → development, CI/CD → staging, deployed → production）"

  profiles:
    development:
      default_model_tier: "tier_0_free"
      max_model_tier: "tier_1_cheap"
      daily_cost_cap: "$1.00"
      task_cost_cap: "$0.10"
      cache_enabled: true
      audit_level: "minimal"
      notes: "调试/实验环境——绝不用付费模型，除非 Owner 显式 /switch-model"

    staging:
      default_model_tier: "tier_1_cheap"
      max_model_tier: "tier_2_standard"
      daily_cost_cap: "$5.00"
      task_cost_cap: "$0.50"
      cache_enabled: true
      audit_level: "standard"
      notes: "集成测试/预发——允许标准模型做质量验证"

    production:
      default_model_tier: "tier_1_cheap"
      max_model_tier: "tier_3_premium"
      daily_cost_cap: "$10.00"
      task_cost_cap: "$1.00"
      cache_enabled: true
      audit_level: "full"
      notes: "正式施工——全能力可用，但仍有日/任务成本硬顶"

  dev_trap_protection:
    description: "防止在 development 环境手动切换到 Tier-3 后忘记切回"
    auto_revert: "每次新 Task 开始时重置到当前 Profile 的 default_model_tier"
    persistent_override: "通过 `zephyr env override-production` 显式命令切换（需二次确认）"
```
