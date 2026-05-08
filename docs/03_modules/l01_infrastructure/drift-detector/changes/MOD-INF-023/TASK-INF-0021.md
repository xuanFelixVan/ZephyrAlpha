---
task_id: "TASK-INF-0021"
title: "Owner 缺席模式 absence_manager.py（D-023-34）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\absence_manager.py"]
acceptance_criteria:
  - "activation: Owner手动ABSENCE_START→ABSENCE_END / 连续48h无人确认告警→自动LENIENT_ABSENCE"
  - "LENIENT(<3天): 预算×2容忍、自动修复仍执行、告警聚合日报、级联故障正常工作"
  - "SURVIVAL(>3天): 预算关闭、自动修复关闭、告警静默存储、扫描正常仅存档、hotfix过期暂停"
  - "return_handover: 生成缺席期摘要报告(漂移总数/修复成功率/级联风暴/预算状态/Top5待处理)"
rollback_instructions: "git checkout src/zephyr/drift_detector/absence_manager.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.20"]}]
tags: ["drift-detector","absence-mode","owner","D-023-34"]
---
# TASK-INF-0021: Owner 缺席模式（D-023-34）
对标 §2.20。实现手动/自动缺席激活、LENIENT(宽松)+SURVIVAL(维持)双模式、回归交接报告生成。
