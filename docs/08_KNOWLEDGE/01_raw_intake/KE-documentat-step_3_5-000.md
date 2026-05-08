---
module_id: KE-documentat-step_3_5-000
title: Step 3.5：幂等性检查
category: documentation
---

# Step 3.5：幂等性检查

Step 3.5：幂等性检查

1. 检查当日管线是否已运行过
2. 如已运行：确认此次是重跑还是重复触发
3. 重跑 → 覆盖前次结果，生成时间戳更新
4. 重复触发 → 拒绝执行，记录警告日志，通知 Owner
5. 幂等性由管线状态表 `pipeline_run_log` 保证（key: 日期 + 报告类型）
