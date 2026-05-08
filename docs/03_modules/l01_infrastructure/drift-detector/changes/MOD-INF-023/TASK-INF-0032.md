---
task_id: "TASK-INF-0032"
title: "语义漂移检测——YAML间概念/枚举/归属一致性（§6.2）"
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
  - concept_cardinality: 同一概念在YAML-A中定义N条目vs YAML-B中M名字差异>0语义漂移
  - enum_value_sync: 同名字段枚举值集合比对
  - ownership_consistency: 同一功能/模块owner字段多处一致性
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.2"]}]
tags: ["drift-detector","integration","§6.2"]
---
# TASK-INF-0032: 语义漂移检测——YAML间概念/枚举/归属一致性（§6.2）
对标 §6.2。concept_cardinality: 同一概念在YAML-A中定义N条目vs YAML-B中M名字差异>0语义漂移
