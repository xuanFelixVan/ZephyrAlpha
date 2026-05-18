---

task_id: "TASK-SYS-0016"
source_blueprint: "SYS-MASTER-001"
source_section: "§21 Canary部署 + §66 Feature Flags"

title: "Canary 渐进式部署(5→10→25→50→100%) + Feature Flags(FF/Toggle/BlueGreen/DarkLaunch)安全网"
description: |
  将 SYS-MASTER-001 §21 Canary 部署策略 + §66 Feature Flags 安全网工程化落地。
  §21: Canary 流水线——5%→10%→25%→50%→100%，每阶段通过健康门(latency<3×baseline/
  error_rate<2×baseline/Sharpe degradation<20%)→推进，否则自动回撤。
  §66: Feature Flags 体系——Feature Toggle、Blue-Green 部署、Dark Launch。
  灰度从 10% 起始→所有检查通过→+15%/次。Kill Switch 集成。
  CLI: `zephyr feature-flags list|enable|disable`。
  本卡搭建 canary_rollout.py + feature_flags.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\canary_rollout.py"
    description: "§21 Canary 5/10/25/50/100% 五阶段——三健康门自动推进/中止"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\feature_flags.py"
    description: "§66 FF/Toggle/BG/DarkLaunch——CLI+JSON持久化+Kill Switch集成"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\canary_rollout.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\feature_flags.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§21 Canary 5%→100%三健康门 + §66 FeatureFlags Toggle/BG/DarkLaunch 10%灰度"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 45

acceptance_criteria:
  - "CanaryStage 枚举 5_PCT/10_PCT/25_PCT/50_PCT/100_PCT——每阶段 traffic_percent + health_gate(latency<3×/error<2×/Sharpe<20%退化)"
  - "CanaryOrchestrator: check_health→all_green→advance→else halt+alert+rollback"
  - "FeatureFlags: model(id,name,enabled,rollout_pct,target_segments)——CLI list|enable|disable"

rollback_instructions: |
  git rm src/zephyr/governance/canary_rollout.py feature_flags.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0015"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
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
