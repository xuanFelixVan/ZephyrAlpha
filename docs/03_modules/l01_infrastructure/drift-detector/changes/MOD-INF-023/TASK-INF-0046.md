---
task_id: "TASK-INF-0046"
title: "资源上限与优雅降级 resource_guard.py（D-023-23）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\resource_guard.py"]
acceptance_criteria:
  - hard_limits: 512MB内存/2GB磁盘/200文件句柄
  - graceful_degradation四级: >384MB并行减半/>448MB暂停非HIGH/>500MB GC+checkpoint+5min重试/OOM预警紧急checkpoint退出
  - scalability_validation: 10>100>500>1500模块路线
rollback_instructions: "git checkout src/zephyr/drift_detector/resource_guard.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.16"]}]
tags: ["drift-detector","integration","§6.16"]
---
# TASK-INF-0046: 资源上限与优雅降级 resource_guard.py（D-023-23）
对标 §6.16。hard_limits: 512MB内存/2GB磁盘/200文件句柄
