---
task_id: "TASK-INF-0037"
title: "测试覆盖漂移检测（§6.7）"
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
  - 模块代码行数增长率vs测试代码行数增长率覆盖率趋势
  - 月环比下降>10%告警
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.7"]}]
tags: ["drift-detector","integration","§6.7"]
---
# TASK-INF-0037: 测试覆盖漂移检测（§6.7）
对标 §6.7。模块代码行数增长率vs测试代码行数增长率覆盖率趋势
