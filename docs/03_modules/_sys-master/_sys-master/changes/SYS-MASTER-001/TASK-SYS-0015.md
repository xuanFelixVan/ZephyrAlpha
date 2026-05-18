---

task_id: "TASK-SYS-0015"
source_blueprint: "SYS-MASTER-001"
source_section: "§20 事故响应 + §75 5级熔断 + §76 Paper→Live"

title: "事故响应L1-L5(瞬时→灾难) + 实盘5级熔断(超限→API超时) + Paper→Live三阶段(并行→影子→灰度)体系"
description: |
  将 SYS-MASTER-001 §20 事故响应 + §75 实盘熔断 + §76 Paper→Live 过渡合并落地。
  §20: 事故响应 L1-L5 分级——
  L1 瞬时故障(<5min) / L2 持续降级(<30min) / L3 部分功能丧失(<2h) /
  L4 全系统故障(<8h) / L5 灾难级。
  每级: escalation_chain / notification_channel / postmortem_required。
  §75: 实盘 5 级熔断开关——
  位置超限→reduce_only / 日亏>3%→cancel all+disable new / 断路器→disconnect /
  秒级熔断→full shutdown / API 超时→auto kill。
  每级: trigger_condition / action / cooldown_seconds / auto_reenable(bool)。
  §76: Paper→Live 三阶段——Phase 1 并行运行(30d) / Phase 2 影子账户(小额真实资金) /
  Phase 3 灰度上线(逐级放大至全量)。
  本卡搭建 incident_response.py + kill_switch.py + paper_live_transition.py。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\incident_response.py"
    description: "§20 L1-L5 事故响应——response_time/escalation_chain/notification/postmortem"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\kill_switch.py"
    description: "§75 5级熔断——超限/日亏3%/断路器/秒级/API超时——trigger/action/cooldown/auto_reenable"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\paper_live_transition.py"
    description: "§76 三阶段过渡——Paper Parallel(30d)→Shadow→Gray Ramp"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\incident_response.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\paper_live_transition.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_execution\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§20 L1-L5(瞬时<5min→灾难) + §75 5级熔断(位置超限→API超时) + §76 Paper→Live 3Phase"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 55

acceptance_criteria:
  - "IncidentLevel 枚举 L1_INSTANT(5min)/L2_DEGRADED(30min)/L3_PARTIAL(2h)/L4_TOTAL(8h)/L5_CATASTROPHIC"
  - "KillSwitchLevel 枚举 5级——每级 trigger_condition(Predicate)/action/cooldown/auto_reenable"
  - "TransitionPhase 枚举 3 阶段——PARALLEL(30d)/SHADOW/GRAY_RAMP——valid_transition检查不可跳 Phase"

rollback_instructions: |
  git rm src/zephyr/governance/incident_response.py kill_switch.py paper_live_transition.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0007"
blocked_by: []
status: "done"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
blueprint_id: DOM-GOV-001
---
