---
task_id: "TASK-INF-0028"
title: "告警路由与疲劳管理 alert_router.py（D-023-13）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "5h"
depends_on: ["TASK-INF-0002","TASK-INF-0007"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\alert_router.py"]
acceptance_criteria:
  - "P0_CRITICAL: Feishu @owner+终端告警、ack_required=true、30min未确认→升级"
  - "P0: Feishu群消息(非@)、每小时聚合摘要"
  - "P1: 每日摘要报告、Feishu定时推送"
  - "P2: 不推送仅dashboard"
  - "deduplication: 同一(module,detector,dimension)6h只告警一次；连续3次scan→persistent_alert"
  - "grouping: >10漂移→batch(top3+N)、同根因→causal_group_alert"
  - "silence: 夜间(22-08)仅P0_CRITICAL、周末延迟周一、focus_time 2h免打扰"
rollback_instructions: "git checkout src/zephyr/drift_detector/alert_router.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.4"]}]
tags: ["drift-detector","alert","routing","D-023-13"]
---
# TASK-INF-0028: 告警路由与疲劳管理（D-023-13）
对标 §5.4。实现四级路由(P0_CRITICAL/P0/P1/P2)+去重(6h×persistent)+聚合(batch+causal_group)+静默策略(夜间/周末/focus_time)。
