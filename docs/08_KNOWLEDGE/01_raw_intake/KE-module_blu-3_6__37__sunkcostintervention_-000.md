---
module_id: KE-module_blu-3_6__37__sunkcostintervention_-000
title: 3.6 #37: SunkCostIntervention (M-35)
category: module_blueprint
---

# 3.6 #37: SunkCostIntervention (M-35)

3.6 #37: SunkCostIntervention (M-35)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\sunk_cost_intervention.py`

实现 `SunkCostIntervention` 类（蓝图 L3416-3467）：
- `check_sunk_limit(task: TaskContext) -> bool`：判断任务是否触发沉没成本门槛
- `intervene(task_id, reason) -> InterventionResult`：中止/暂停/降级
- 蓝图 L3428-3467 干预逻辑完整实现
