---
task_id: "TASK-INF-0047"
title: "漂移取证引擎 forensics_engine.py（§6.17）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\forensics_engine.py"]
acceptance_criteria:
  - replay: git checkout还原代码状态+drift_events表活跃漂移+baseline历史
  - forensics_report: timeline+state_diffs+actor_trace+dependency_impact
rollback_instructions: "git checkout src/zephyr/drift_detector/forensics_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.17"]}]
tags: ["drift-detector","integration","§6.17"]
---
# TASK-INF-0047: 漂移取证引擎 forensics_engine.py（§6.17）
对标 §6.17。replay: git checkout还原代码状态+drift_events表活跃漂移+baseline历史
