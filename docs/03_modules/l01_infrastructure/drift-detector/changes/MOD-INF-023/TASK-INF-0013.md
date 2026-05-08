---
task_id: "TASK-INF-0013"
title: "热修复/紧急变更旁路（D-023-19）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "2h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "[HOTFIX]/[EMERGENCY] commit前缀识别 → 自动HOTFIX_ACKNOWLEDGED → SUPPRESSED(ttl=72h)"
  - "不消耗漂移预算、不触发告警"
  - "72h后恢复DETECTED → 通知Owner确认是否转为正式修复"
  - "hotfix审计日志写入 drift_hotfix_log 表(commit_hash/module_ids/dimensions/owner_ack/timestamp，永久保留)"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.12"]}]
tags: ["drift-detector","hotfix","bypass","D-023-19"]
---

# TASK-INF-0013: 热修复旁路（D-023-19）
## 目标: 实现P0 hotfix快速旁路——[HOTFIX] commit自动标记，不消耗预算，72h后必须正规化。对标 §2.12。
