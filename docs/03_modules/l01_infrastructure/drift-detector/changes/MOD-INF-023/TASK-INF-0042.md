---
task_id: "TASK-INF-0042"
title: "漂移作为AI训练数据闭环（§6.12）"
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
  - pattern_extraction: 30天高频漂移维度+根因commit diff pattern提取AI易错代码模式
  - injection: 高频模式注入AGENTS.md/system prompt
  - effectiveness: 追踪注入前后同类漂移发生率下降>50%固化到AGENTS.md
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.12"]}]
tags: ["drift-detector","integration","§6.12"]
---
# TASK-INF-0042: 漂移作为AI训练数据闭环（§6.12）
对标 §6.12。pattern_extraction: 30天高频漂移维度+根因commit diff pattern提取AI易错代码模式
