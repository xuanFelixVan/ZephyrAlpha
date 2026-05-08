---
task_id: "TASK-INF-0063"
title: "DOM-GOV-001 集成契约 CT-005——漂移信号→Rollback 集成"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "integration"
priority: "P0"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0005","TASK-INF-0045"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md","D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md"]
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\state_machine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\cascade_detector.py"
acceptance_criteria:
  - "本模块作为产出方：当 FIX_FAILED → 触发 MOD-INF-021 Rollback 模块的自动回滚流程"
  - "rollback_verified 字段正确写入 drift_events"
  - "cascade_detector 检测到级联修复循环 → 触发 Rollback 回滚到 cascade 前状态"
  - "回滚后状态机从 FIX_FAILED 推进到 ACKNOWLEDGED(NEEDS_HUMAN)"
rollback_instructions: "git checkout src/zephyr/drift_detector/state_machine.py cascade_detector.py"
context_assembly_manifest: [
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["DOM-GOV-001"]},
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md", sections: ["§2"]}
]
tags: ["drift-detector","contract","CT-005","DOM-GOV-001"]
---
# TASK-INF-0063: G-CT-005 契约——漂移信号→Rollback集成
对标 DOM-GOV-001 集成契约锚点 CT-005。本模块作为产出方(FIX_FAILED/级联→触发MOD-INF-021 Rollback回滚)+ rollback_verified字段完整性验证。
