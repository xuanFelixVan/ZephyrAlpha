---
task_id: "TASK-INF-0045"
title: "级联故障检测 cascade_detector.py（D-023-22）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\cascade_detector.py"]
acceptance_criteria:
  - trigger: 同一module 30min内>=3新漂移且每次前一个被修复
  - action: 暂停自动修复锁定1h P0通知Owner cascade_forensics report(每次修复diff+新漂移)
  - prevention: dry-run影响面分析(临时目录模拟修复diff跑关联检测器)
rollback_instructions: "git checkout src/zephyr/drift_detector/cascade_detector.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.15"]}]
tags: ["drift-detector","integration","§6.15"]
---
# TASK-INF-0045: 级联故障检测 cascade_detector.py（D-023-22）
对标 §6.15。trigger: 同一module 30min内>=3新漂移且每次前一个被修复
