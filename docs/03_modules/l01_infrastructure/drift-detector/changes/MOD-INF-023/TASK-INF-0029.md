---
task_id: "TASK-INF-0029"
title: "修复ROI优先级引擎 roi_engine.py（D-023-14）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0005"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\roi_engine.py"]
acceptance_criteria:
  - "formula: ROI = (impact_weight × frequency_score) / effort_score"
  - "impact_weight: P0_module=10/P1=5/P2=2 × severity(HIGH=3/MEDIUM=2/LOW=1)"
  - "frequency_score: 1 + log2(30天检测次数)"
  - "effort_score: auto_fixable=1/suggestion_simple=3/suggestion_complex=8/needs_human=20"
  - "sort: ROI降序→Top N推送; feedback: 实际耗时vs effort校准"
rollback_instructions: "git checkout src/zephyr/drift_detector/roi_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.5"]}]
tags: ["drift-detector","ROI","priority","D-023-14"]
---
# TASK-INF-0029: 修复ROI优先级引擎（D-023-14）
对标 §5.5。实现 ROI = impact_weight × frequency / effort 公式 + 四级effort + 持续校准feedback。
