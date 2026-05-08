---
task_id: "TASK-INF-0034"
title: "依赖版本漂移检测（§6.4）"
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
  - requirements.txt vs pip freeze行级对比
  - auto_fixable自动更新requirements.txt保留>=/~=语义不暴力锁定==
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.4"]}]
tags: ["drift-detector","integration","§6.4"]
---
# TASK-INF-0034: 依赖版本漂移检测（§6.4）
对标 §6.4。requirements.txt vs pip freeze行级对比
