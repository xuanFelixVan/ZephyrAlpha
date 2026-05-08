---
task_id: "TASK-INF-0060"
title: "Phase experimental 施工执行——完整漂移状态机(全10状态)+自动对账+pre-fix快照+乐观并发控制+rollback验证闭环+契约-代码AST对比..."
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "phase"
priority: "P1"
status: "draft"
estimated_effort: "40h"
depends_on: ["TASK-INF-0009","TASK-INF-0016","TASK-INF-0017","TASK-INF-0018","TASK-INF-0019","TASK-INF-0029","TASK-INF-0039","TASK-INF-0040","TASK-INF-0045","TASK-INF-0046","TASK-INF-0050","TASK-INF-0051","TASK-INF-0052","TASK-INF-0021"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: []
acceptance_criteria:
  - "本Phase全部子任务执行完毕并通过各自的验收标准"
  - "construction_progress更新为phase_experimental_complete"
  - "Phase完成时自动触发baseline_manager拍摄基线快照"
  - "所有关联drift_events完成VERIFIED状态"
rollback_instructions: "若Phase中任一子任务回滚，则执行级联回滚：按逆序回滚本Phase已完成子任务。重新运行DEEP scan确认无级联漂移。"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§8 experimental"]}]
tags: ["drift-detector","phase-experimental"]
---
# TASK-INF-0060: Phase experimental 施工执行
对标 §8 experimental。完整任务范围：完整漂移状态机(全10状态)+自动对账+pre-fix快照+乐观并发控制+rollback验证闭环+契约-代码AST对比+AI死码/逻辑断裂/重复功能检测器+自漂移检测(self_check.py)+漂移预算与施工门禁+修复ROI优先级引擎+漂移演练手册自动生成+级联故障检测基础版+资源上限与优雅降级基础版+多实例竞态控制+scan mutex+孤儿资源检测基础版+文件底层属性+Python版本兼容性基础版+Owner缺席模式基础版+告警可信度评分基础版。Phase完成自动拍摄基线+更新construction_progress。
