---
task_id: "TASK-INF-0040"
title: "知识图谱实体化集成（§6.10）"
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
  - DriftEvent/Detector/Module三实体+DETECTED_BY/AFFECTS/INTRODUCED_BY/CORRELATED_WITH/RESOLVED_BY关系
  - mcp_Knowledge_Graph_Memory MCP server读写
  - queries: 从未产生漂移的检测器/漂移成对出现的模块/热点区域
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.10"]}]
tags: ["drift-detector","integration","§6.10"]
---
# TASK-INF-0040: 知识图谱实体化集成（§6.10）
对标 §6.10。DriftEvent/Detector/Module三实体+DETECTED_BY/AFFECTS/INTRODUCED_BY/CORRELATED_WITH/RESOLVED_BY关系
