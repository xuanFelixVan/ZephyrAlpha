---
task_id: "TASK-INF-0020"
title: "冷启动策略——零基线状态漂移检测引导 cold_start.py（D-023-33）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0004"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\cold_start.py"]
acceptance_criteria:
  - "phase_1_bootstrap_scan: 首次运行全量DEEP scan模式BOOTSTRAP→结果记录INITIAL_BASELINE不标记DETECTED"
  - "phase_2_trust_establishment: Owner审查COLD_START_REPORT→ACCEPT_CURRENT或DECLARE_DEBT"
  - "phase_3_baseline_creation: Owner完成审查→拍摄全量基线→正常模式"
  - "re_bootstrap: drift_events.db损坏/丢失→保留旧数据backup→重新冷启动"
  - "shallow_clone_awareness: git rev-parse --is-shallow-repository→禁用溯源→通知Owner"
rollback_instructions: "git checkout src/zephyr/drift_detector/cold_start.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.19"]}]
tags: ["drift-detector","cold-start","bootstrap","D-023-33"]
---
# TASK-INF-0020: 冷启动策略（D-023-33）
对标 §2.19。实现三阶段冷启动(扫描→信任→基线) + re_bootstrap + shallow clone感知。
