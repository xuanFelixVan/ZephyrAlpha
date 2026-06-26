---
module_id: KE-2056
status: active
title: 3.12 #29: TimePartitionedSLO
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.12 #29: TimePartitionedSLO

3.12 #29: TimePartitionedSLO

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\time_partitioned_slo.py`

实现 `TimePartitionedSLO` 类（蓝图 L2956-3000）：
- 两时段分隔：`09:00-22:00`（tight: latency_target × 1.0）/ `22:00-09:00`（relaxed: × 2.0）
- `get_current_partition() -> TimePartition`
- `evaluate_slo(metric_value, partition)`：分区评估
