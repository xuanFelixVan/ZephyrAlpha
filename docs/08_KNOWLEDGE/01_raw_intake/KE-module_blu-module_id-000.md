---
module_id: KE-module_blu-module_id-000
title: 模块调用时不需要手动传 module_id
category: module_blueprint
---

# 模块调用时不需要手动传 module_id

模块调用时不需要手动传 module_id
telemetry = Telemetry("MOD-INF-008")
telemetry.metrics.counter("llm_calls_total", 1)
  → 内部自动生成 FQMN: "MOD-INF-008::llm_calls_total"
  → Schema Registry 按 FQMN 校验
  → SQLite 表存储 fqmn 列 + metric_name 列 + module_id 列（三列索引）
```
