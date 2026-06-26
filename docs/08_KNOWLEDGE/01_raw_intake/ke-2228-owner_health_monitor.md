---
module_id: KE-2135
status: active
title: 3.6 #22: OwnerHealthMonitor
category: module_blueprint
ttl: permanent
---

# 3.6 #22: OwnerHealthMonitor

3.6 #22: OwnerHealthMonitor

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\owner_health_monitor.py`

实现 `OwnerHealthMonitor` 类（蓝图 L2372-2427）：
- `compute_alert_fatigue_score(weekly_alerts: int, unread_pct: float, false_alarm_pct: float) -> float`
- SEV-2 级别自动响应（合并为 Morning Digest）
- `detect_burnout_risk() -> bool`：连续 2 周疲劳评分 > 0.7 触发预警
- 蓝图 L2372-2427 YAML/代码完整实现
