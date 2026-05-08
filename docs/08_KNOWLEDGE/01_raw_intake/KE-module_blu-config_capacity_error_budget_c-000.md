---
module_id: KE-module_blu-config_capacity_error_budget_c-000
title: config/capacity/error_budget_config.yaml 完整示例
category: module_blueprint
---

# config/capacity/error_budget_config.yaml 完整示例

config/capacity/error_budget_config.yaml 完整示例
error_budgets:
  - slo_id: "CAP-001-startup-time"
    budget_window: "30d"
    burn_rate_alerts:
      - rate: 2.0      # 2× 正常消耗率
        tier: warning
        window: "7d"
        description: "7 天内消耗率超过正常 2 倍"
      - rate: 5.0
        tier: critical
        window: "3d"
        description: "3 天内消耗率超过正常 5 倍"
      - rate: 10.0
        tier: emergency
        window: "1d"
        description: "1 天内消耗率超过正常 10 倍"
    response_tiers:
      healthy:
        threshold: 0.6
        actions: []
      warning:
        threshold: 0.4
        actions: ["log_warning", "weekly_report"]
      cautious:
        threshold: 0.2
        actions: ["log_warning", "notify_owner", "reduce_release_frequency"]
      critical:
        threshold: 0.05
        actions: ["log_critical", "freeze_releases", "auto_escalate"]
      emergency:
        threshold: 0.0
        actions: ["log_emergency", "kill_switch_conservative", "notify_owner_urgent"]
    auto_recovery:
      emergency_to_critical:
        condition: "budget_remaining > 5% AND burn_rate_1d < 5×"
        cooldown: "6h"
      critical_to_cautious:
        condition: "budget_remaining > 20% AND burn_rate_3d < 3×"
        cooldown: "24h"
```
