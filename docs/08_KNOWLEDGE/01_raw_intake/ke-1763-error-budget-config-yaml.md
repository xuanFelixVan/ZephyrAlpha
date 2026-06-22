---
module_id: KE-1672
status: active
title: 2.1 error_budget_config.yaml
category: module_blueprint
---

# 2.1 error_budget_config.yaml

2.1 error_budget_config.yaml

创建 `D:\ZephyrAlpha\config\capacity\error_budget_config.yaml`：

```yaml
version: "2.6.0"
error_budget:
  windows:
    fast_cycle:
      intervals: ["1h", "6h"]
      burn_rate_multiplier: 14.4
    medium_cycle:
      intervals: ["24h", "7d"]
      burn_rate_multiplier: 6.0
    slow_cycle:
      intervals: ["28d"]
      burn_rate_multiplier: 3.0

  response_tiers:
    - tier: L0 (GREEN)
      burn_rate_range: [0, 1.0)
      action: "指标仪表板更新"
      notification_channel: "metrics_dashboard"
      auto_recovery: true

    - tier: L1 (YELLOW)
      burn_rate_range: [1.0, 3.0)
      action: "模块日志告警 + 频率限制建议"
      notification_channel: "module_logs"
      auto_recovery: true

    - tier: L2 (ORANGE)
      burn_rate_range: [3.0, 6.0)
      action: "AI 代理工作区通知 + Token Budget 收紧"
      notification_channel: "ai_workspace"
      auto_recovery: false
      escalation_timeout_minutes: 30

    - tier: L3 (RED)
      burn_rate_range: [6.0, 14.4)
      action: "模型路由切换 + 全局通知"
      notification_channel: "global_notification"
      auto_recovery: false
      triggers: ["CT-1 模型路由切换"]
      escalation_timeout_minutes: 15

    - tier: L4 (BLACK)
      burn_rate_range: [14.4, inf)
      action: "全平台通知 + Kill Switch 触发"
      notification_channel: "platform_wide"
      auto_recovery: false
      triggers: ["Kill Switch"]

  burn_rate_calculation:
    formula: "burn_rate = (error_ratio / (1 - slo_target)) * (alert_window / evaluation_window)"

  conservation:
    max_budget_consumption_pct: 100.0
    min_budget_remaining_pct: 0.0
    invariant_check: "|累计消耗 - Σ(分窗口消耗)| ≤ 1%"
```
