---
task_id: "TASK-INF-0031"
title: "Evolution Engine 反馈闭环集成（D-023-10）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "integration"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0025"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md","D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\..\\..\\feedback_loop\\evolution_engine.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "每次DEEP scan完成后推送drift_velocity_30d/top_dimensions/suggested_action到Evolution Engine"
  - "suggested_action: EVOLVE_BLUEPRINT | ADD_CONTRACT | SPLIT_MODULE"
  - "feedback_loop: Evolution Engine更新blueprint_scorer调整模块评分影响施工优先级"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.1"]}]
tags: ["drift-detector","evolution-engine","D-023-10"]
---
# TASK-INF-0031: Evolution Engine 反馈闭环（D-023-10）
对标 §6.1。实现 drift_engine→Evolution Engine 数据推送，suggested_action(EVOLVE_BLUEPRINT/ADD_CONTRACT/SPLIT_MODULE)，反向影响蓝图评分和施工优先级。
