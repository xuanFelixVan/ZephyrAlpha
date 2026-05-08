---
task_id: "TASK-INF-0043"
title: "混沌工程——主动漂移注入 chaos_injector.py（§6.13）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\chaos_injector.py"]
acceptance_criteria:
  - 4种注入类型: path_rename/yaml_field_flip/fake_todo_bomb/import_hallucination
  - schedule: 每周一次(维护窗口内)
  - safeguards: 仅P2模块+pre-chaos基线+检测通过自动回滚+未发现DEGRADED
  - metrics: detection_rate/time_to_detect/false_negative_trend
rollback_instructions: "git checkout src/zephyr/drift_detector/chaos_injector.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.13"]}]
tags: ["drift-detector","integration","§6.13"]
---
# TASK-INF-0043: 混沌工程——主动漂移注入 chaos_injector.py（§6.13）
对标 §6.13。4种注入类型: path_rename/yaml_field_flip/fake_todo_bomb/import_hallucination
