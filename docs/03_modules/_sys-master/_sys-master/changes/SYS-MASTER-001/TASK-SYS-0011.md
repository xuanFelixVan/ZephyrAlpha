---

task_id: "TASK-SYS-0011"
source_blueprint: "SYS-MASTER-001"
source_section: "§16 FMEA 故障模式分析 + §99 沉默故障聚合评分(AFS)"

title: "FMEA 8大故障(F1行情延迟→F8灾难性遗忘)分析 + 沉默故障AFS级联风险防御"
description: |
  将 SYS-MASTER-001 §16 的 FMEA 分析与 §99 的沉默故障聚合评分(Aggregated Failure Score)工程化落地。
  §16 定义 8 大 FMEA 故障：
  F1-行情数据延迟 / F2-信号 WAL 损坏 / F3-重复订单 / F4-Risk SQLite 锁 /
  F5-API 密钥过期 / F6-Look-Ahead 数据泄露 / F7-Broker API 不可达 / F8-灾难性遗忘（Catastrophic Forgetting）。
  每故障含 detect_metric / threshold / severity / RPN / recovery_action / preventions。
  §99 定义 AFS 沉默故障聚合——Σ(W_i×F_i) 加权评分模型。多微小故障同时发生时产生级联风险(Cascading Risk)。
  当 AFS≥0.8→CRITICAL→shed load+Owner 通知。
  本卡搭建 fmea_register.py + silent_fault_aggregator.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\fmea_register.py"
    description: "§16 FMEA——F1→F8 8条，FMEARecord(fmea_id,detect_metric,threshold,severity,RPN,recovery,preventions)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\silent_fault_aggregator.py"
    description: "§99 AFS——SilentFaultAggregator.register(fault_id,weight,current_score)→compute cascade score→trigger≥0.8"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\fmea_register.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\silent_fault_aggregator.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§16 F1-F8 FMEA——detect_metric/threshold/RPN/recovery/preventions + §99 AFS 加权聚合"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 35

acceptance_criteria:
  - "FMEARegister: 8条 F1-F8——每条含 detect_metric/threshold/severity/RPN/recovery_action/preventions"
  - "SilentFaultAggregator: 注册故障(weight,score)→compute_cascading_score=Σ(W_i×F_i)→≥0.8→trigger_shedload+alert"
  - "script_manifest.yaml 注册"

rollback_instructions: |
  git rm src/zephyr/governance/fmea_register.py silent_fault_aggregator.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0007"
blocked_by: []
status: "created"
tags_fn:
  - "risk"
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
