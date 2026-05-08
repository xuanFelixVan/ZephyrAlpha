---
module_id: KE-module_blu-3_1__12____3__alertmanager-003
title: 3.1 #12 + #3: AlertManager + 告警收敛
category: module_blueprint
---

# 3.1 #12 + #3: AlertManager + 告警收敛

3.1 #12 + #3: AlertManager + 告警收敛

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\alert_manager.py`

实现 `AlertManager` 类（集成 `AlertGovernanceConfig`）：
- `should_notify(alert: Alert) -> (bool, str)`：
  - 静默期检查（00:00-08:00，emergency/kill_switch_triggered 除外）
  - 收敛检查（30min内同 SLO+Module 重复告警 → 合并）
  - 自愈优先（warning 级别先尝试 auto_heal，成功→不入通知）
- `generate_morning_digest() -> str`：每天早上 8 点聚合摘要
- 消息优先级路由：realtime→emergency/critical/kill_switch；hourly→cautious；daily→warning
- 对应 capacity_slo.yaml v2.2.0 `alert_governance` 节（蓝图 L1613-1647）完整实现
