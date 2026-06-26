---
module_id: KE-1681
status: active
title: 2.1 trigger_monitor.py
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 trigger_monitor.py

2.1 trigger_monitor.py
- 8 个指标采集函数（每个独立可测）
- `activation_rule` 评估器：`metric_1 >= 3 AND (metric_2 >= 5 OR metric_3 >= 2)`
- `early_warning_rule` 评估器：`(metric_4 >= 15 AND metric_1 >= 2) OR metric_5 >= 1 OR metric_6 >= 1`
- v0.7.0 新增 composite_trigger（weighted: net_risk_score > 2.0）
