---
module_id: KE-module_blu-2_2____sli_instrumentation_py-000
title: 2.2 创建 sli_instrumentation.py
category: module_blueprint
---

# 2.2 创建 sli_instrumentation.py

2.2 创建 sli_instrumentation.py

创建 `D:\ZephyrAlpha\src\\zephyr\\shared\\sli_instrumentation.py`，实现 `SLIInstrumentation` 类：
- `record_insert_timing(sli_id, duration_ms)`: 记录写入耗时（盲点 #4 插桩点）
- `record_correction_latency(sli_id, duration_ms)`: 记录修正延迟（盲点 #4 插桩点）
- `record_validation_timing(sli_id, duration_ms)`: 记录校验耗时
- `get_sli_stats(sli_id) -> SLIStats`: 获取统计信息
