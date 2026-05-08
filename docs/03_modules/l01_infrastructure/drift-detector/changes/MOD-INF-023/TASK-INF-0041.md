---
task_id: "TASK-INF-0041"
title: "检测器金丝雀部署 canary_controller.py（§6.11）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\canary_controller.py"]
acceptance_criteria:
  - v2独立ID运行结果不入drift_events对比v1分类NEW_FINDING/LOST_FINDING/CHANGED_SEVERITY
  - Owner审查后全量切换或回退
  - auto_rollback: v2 FP率>2×v1自动回退
rollback_instructions: "git checkout src/zephyr/drift_detector/canary_controller.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.11"]}]
tags: ["drift-detector","integration","§6.11"]
---
# TASK-INF-0041: 检测器金丝雀部署 canary_controller.py（§6.11）
对标 §6.11。v2独立ID运行结果不入drift_events对比v1分类NEW_FINDING/LOST_FINDING/CHANGED_SEVERITY
