---
task_id: "TASK-INF-0044"
title: "跨Session修复上下文交接 handoff_manager.py（§6.14）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\handoff_manager.py"]
acceptance_criteria:
  - handoff_package: 单JSON(drift_runbook+git bisect+pre-fix快照+baseline diff+关联漂移)<5000token
  - resume_workflow: 自动加载注入context按演练手册修复推进状态
  - abort: 文件状态与手册不一致重新生成+通知Owner
rollback_instructions: "git checkout src/zephyr/drift_detector/handoff_manager.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.14"]}]
tags: ["drift-detector","integration","§6.14"]
---
# TASK-INF-0044: 跨Session修复上下文交接 handoff_manager.py（§6.14）
对标 §6.14。handoff_package: 单JSON(drift_runbook+git bisect+pre-fix快照+baseline diff+关联漂移)<5000token
