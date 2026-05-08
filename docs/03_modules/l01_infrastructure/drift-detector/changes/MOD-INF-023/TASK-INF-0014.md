---
task_id: "TASK-INF-0014"
title: "环境感知与渐进部署漂移（D-023-20）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P2"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "context_tags: 每个模块可声明运行环境标签(python_version/config_profile/feature_flags)"
  - "differential_detection: 差异仅出现在env_A而不在env_B→ENV_DIFF(非漂移)；同时出现在所有环境→真漂移"
  - "partial_deployment: 检测模块A/B不同结构→MIGRATION_IN_PROGRESS；24h未完成→PARTIAL_MIGRATION_STALLED"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.13"]}]
tags: ["drift-detector","environment","D-023-20"]
---

# TASK-INF-0014: 环境感知（D-023-20）
对标 §2.13。实现context_tags声明、差异分类(ENV_DIFF vs DRIFT)、渐进部署感知(MIGRATION_IN_PROGRESS → STALLED)。
