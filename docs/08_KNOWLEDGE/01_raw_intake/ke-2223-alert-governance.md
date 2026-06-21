---
module_id: KE-2130
status: active
title: 3.5 alert_governance 配置扩展
category: module_blueprint
---

# 3.5 alert_governance 配置扩展

3.5 alert_governance 配置扩展

在 `D:\ZephyrAlpha\config\capacity\capacity_slo.yaml` 中追加 `alert_governance` 节（蓝图 L1613-1647 YAML 直接实现），含：
- `convergence`：窗口30min，按 slo_id+module_id 聚合
- `quiet_hours`：00:00-08:00，例外 emergency/kill_switch_triggered，早上morning_digest
- `auto_remediation`：warning→auto_heal_first (max 3 tries)，cautious→log+weekly_report_only，critical→notify_owner
- `notification_routing`：realtime/hourly_digest/daily_digest/weekly_digest 四通道
