---
task_id: "TASK-SYS-0024"
source_blueprint: "SYS-MASTER-001"
source_section: "§34 离线自治 + §79 Local-First + §80 决策疲劳"

title: "离线模式(2模式: 全自动/半自动+手动) + Local-First Architecture(All compute locally, cloud=backfill) + 决策疲劳(Eisenhower Matrix P0-P3)体系"
description: |
  将 SYS-MASTER-001 §34 离线自治 + §79 Local-First + §80 决策疲劳三合一落地。
  §34: 2模式——全自动（冻结→offline rules engine+control）/
  半自动+手动（断开后仅缓存操作→手动 command）。
  §79: Local-First原则——All computation run locally。
  WebSocket行情→本地消费唯一依赖 / 云端同步=backfill only→灾难恢复 /
  离线后一切继续运作→zero cloud dependency。
  §80: Decision Fatigue Management——Eisenhower Matrix priority分类:
  urgent+important=P0(do now)/important not urgent=P1(schedule)/
  urgent not important=P2(delegate to AI Agent)/neither=P3(eliminate)→自动分类。
  本卡搭建 offline_autonomy.py + local_first_arch.py + decision_fatigue.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\offline_autonomy.py"
    description: "§34 2模式——全自动(frozen+engine takeover)/半自动+手动(cache+safe commands)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\local_first_arch.py"
    description: "§79 Local-First——all compute locally/WS唯一依赖/cloud=backfill/zcloud dep—zero"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\decision_fatigue.py"
    description: "§80 Eisenhower Matrix P0-P3 auto classify"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\decision_fatigue_cli.py"
    description: "§80 CLI `zephyr priorities --filter=P0` triage board"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\offline_autonomy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\local_first_arch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\decision_fatigue.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\decision_fatigue_cli.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§34 离线2模式+§79 Local-First(zcloud dep→zero)+§80 EisenhowerMatrix P0-P3auto"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 50

acceptance_criteria:
  - "offline_autonomy.py: OfflineMode枚举AUTO(engine takeover)/SEMIAUTO_MANUAL(cache+manual commands)→ mode_transition based on connectivity"
  - "local_first_arch.py: check_all local deps→network_deps=empty→WS唯一→data_lake=localDB→zero_cloud guarantee"
  - "decision_fatigue.py: eisenhower_classify(task:TaskCard)→urgent×important→P0/P1/P2/P3 quadrant"

rollback_instructions: |
  git rm src/zephyr/governance/offline_autonomy.py local_first_arch.py decision_fatigue.py decision_fatigue_cli.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0018"
blocked_by: []
status: "done"
tags_fn:
  - "ops"
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
---
