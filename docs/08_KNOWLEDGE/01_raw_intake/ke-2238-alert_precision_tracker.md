---
module_id: KE-2145
status: active
title: 3.7 #45: AlertPrecisionTracker
category: module_blueprint
ttl: permanent
---

# 3.7 #45: AlertPrecisionTracker

3.7 #45: AlertPrecisionTracker

文件：`D:\ZephyrAlpha\src\zephyr\shared\alert_precision_tracker.py`

- `record_alert_and_outcome(alert, outcome)`: 以Owner实际行动为Ground Truth
- `compute_precision_recall(window_days=30)`: Precision<30%→自动抑制高误报规则
- 每周一自动生成AlertQualityReport
