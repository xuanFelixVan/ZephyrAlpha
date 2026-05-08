---
task_id: "TASK-INF-0038"
title: "AI上下文注入——施工前预检 ai_context_injector.py（D-023-16）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\ai_context_injector.py"]
acceptance_criteria:
  - minimal(<100token): 模块健康度+活跃漂移数+预算剩余
  - standard(<300token): 活跃漂移TOP3按ROI排序
  - full(<1000token): 全量漂移+趋势+基线diff
  - injection_point: session_manager派发task时+MCP discover_applicable_gates
rollback_instructions: "git checkout src/zephyr/drift_detector/ai_context_injector.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.8"]}]
tags: ["drift-detector","integration","§6.8"]
---
# TASK-INF-0038: AI上下文注入——施工前预检 ai_context_injector.py（D-023-16）
对标 §6.8。minimal(<100token): 模块健康度+活跃漂移数+预算剩余
