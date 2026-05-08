---
task_id: "TASK-INF-0059"
title: "Phase scaffold 施工执行——整合现有80+脚本为检测器+DriftReport模型+drift_events表+基础状态机+post-commit ..."
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "phase"
priority: "P0"
status: "draft"
estimated_effort: "40h"
depends_on: ["TASK-INF-0001","TASK-INF-0002","TASK-INF-0003","TASK-INF-0004","TASK-INF-0005","TASK-INF-0006","TASK-INF-0007","TASK-INF-0008","TASK-INF-0010","TASK-INF-0011","TASK-INF-0013"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: []
acceptance_criteria:
  - "本Phase全部子任务执行完毕并通过各自的验收标准"
  - "construction_progress更新为phase_scaffold_complete"
  - "Phase完成时自动触发baseline_manager拍摄基线快照"
  - "所有关联drift_events完成VERIFIED状态"
rollback_instructions: "若Phase中任一子任务回滚，则执行级联回滚：按逆序回滚本Phase已完成子任务。重新运行DEEP scan确认无级联漂移。"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§8 scaffold"]}]
tags: ["drift-detector","phase-scaffold"]
---
# TASK-INF-0059: Phase scaffold 施工执行
对标 §8 scaffold。完整任务范围：整合现有80+脚本为检测器+DriftReport模型+drift_events表+基础状态机+post-commit LIGHT增量扫描+基线快照管理器(minimal)+AI幻觉import检测器(P0)+AI上下文注入minimal级别(<100token)+告警路由(P0_CRITICAL+P0渠道)+崩溃恢复检查点+热修复旁路+冷启动引导+append-only drift_events表。Phase完成自动拍摄基线+更新construction_progress。
