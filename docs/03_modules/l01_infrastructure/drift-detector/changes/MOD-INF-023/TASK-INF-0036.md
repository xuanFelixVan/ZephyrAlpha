---
task_id: "TASK-INF-0036"
title: "文档-代码共演化漂移检测（§6.6）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - code_newer_than_blueprint: max(代码mtime)>blueprint mtime+7天标记
  - blueprint_interface_vs_code: 蓝图§3接口vs代码公开接口任一方向不一致漂移
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.6"]}]
tags: ["drift-detector","integration","§6.6"]
---
# TASK-INF-0036: 文档-代码共演化漂移检测（§6.6）
对标 §6.6。code_newer_than_blueprint: max(代码mtime)>blueprint mtime+7天标记
