---
task_id: "TASK-INF-0023"
title: "漂移维度完整清单实现——31维检测器覆盖矩阵与状态追踪"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "2h"
depends_on: ["TASK-INF-0003"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\_detector_registry.yaml"]
acceptance_criteria:
  - "31个漂移维度完整映射：18个existing维度(D5-BP-SYNC~D5-HANDOFF) + 6个AI维度(AI-IMPORT~AI-DEPRECATED-API) + 7个集成维度(D5-CONTRACT-IMPL~D5-TEST-COV)"
  - "每个维度标注检测器ID、严重度(HIGH/MEDIUM/LOW)、状态(✅/📋)"
  - "生成 detector_coverage_matrix YAML: dimension × detector 交叉表"
  - "盲区检测：任何维度无检测器覆盖 → MISSING_COVERAGE 告警"
rollback_instructions: "git checkout src/zephyr/drift_detector/_detector_registry.yaml"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§3"]}]
tags: ["drift-detector","dimensions","coverage-matrix"]
---
# TASK-INF-0023: 漂移维度完整清单（§3）
对标 §3 漂移维度完整清单。实现31维检测器覆盖矩阵(dimension→detector mapping)，盲区检测(MISSING_COVERAGE告警)。
