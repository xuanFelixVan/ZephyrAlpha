---
module_id: KE-3045------bug-000
title: 共享契约修复（codegen 字段顺序 bug）
category: session_log
ttl: permanent
---

# 共享契约修复（codegen 字段顺序 bug）

共享契约修复（codegen 字段顺序 bug）
| 操作 | 文件路径 | 修复内容 |
|------|---------|---------|
| 编辑 | `src/zephyr/shared/contracts/system_configuration.py` | created_at/updated_at 移到 is_active 之前，给 Optional 默认值 |
| 编辑 | `src/zephyr/shared/contracts/experiment_result.py` | variant_b_improvement 移到 metrics（默认值字段）之前 |
| 编辑 | `src/zephyr/shared/contracts/telemetry_emitter.py` | labels/schema_version 移到末尾 |
| 编辑 | `src/zephyr/shared/contracts/synthesized_signal.py` | contributing_factors 移到末尾 |
