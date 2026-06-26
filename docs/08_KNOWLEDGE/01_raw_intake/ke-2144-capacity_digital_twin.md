---
module_id: KE-2052
status: active
title: 3.11 #49: CapacityDigitalTwin (M-40)
category: module_blueprint
ttl: permanent
---

# 3.11 #49: CapacityDigitalTwin (M-40)

3.11 #49: CapacityDigitalTwin (M-40)

文件：`D:\ZephyrAlpha\src\zephyr\shared\capacity_digital_twin.py`

- `simulate_merge(task_card)`: Sandbox副本中应用所有变更→测量容量
- 判定：启动退化>30% → BLOCK / 内存增长>50% → BLOCK / 新依赖>5 → WARN
- 集成到 G5 pre-merge gate
