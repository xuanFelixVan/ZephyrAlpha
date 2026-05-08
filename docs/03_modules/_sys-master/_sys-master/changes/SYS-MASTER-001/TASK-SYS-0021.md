---
task_id: "TASK-SYS-0021"
source_blueprint: "SYS-MASTER-001"
source_section: "§29 数据质量 + §53 上线后验证 + §83 数据源可靠性"

title: "数据质量6维DQ + 上线后5验证(paper vs live/reconciliation/risk/checksum/position) + 数据源可靠性5维评分(U/A/T/C/C)体系"
description: |
  将 SYS-MASTER-001 §29 数据质量 + §53 上线后验证 + §83 数据源可靠性三合一落地。
  §29: 6维DQ——Completeness(缺失%)/Accurateness(偏差σ)/Consistency(重构对账)/
  Timeliness(延迟ms)/Uniqueness(重复率)/Validity(Schema约束)。
  每维 check_func→data ingestion 自动触发。
  §53: 5条 Post-Live 验证——paper vs live order flow(订单偏差)/
  execution quality(FillRate/Slippage)→T+1 vs T-1回归/risk limits conformance(≥limits)/
  data integrity(checksum verified)/position & PnL reconciliation(±threshold)。
  §83: 5维数据源可靠性评分——Uptime可用性(w=0.25)/Accuracy准确性(w=0.30)/
  Timeliness及时性(w=0.20)/Completeness(w=0.15)/Consistency一致性(w=0.10)。
  本卡搭建 data_quality.py + post_live_verification.py + data_source_reliability.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_quality.py"
    description: "§29 6维DQ——comp/acc/cons/time/uniq/vali——check_func DE自动触发"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\post_live_verification.py"
    description: "§53 5 PLV——paper/live/reconciliation/risk/checksum/position验证"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_source_reliability.py"
    description: "§83 5维 Reliability Score——U/A/T/C/C 各有权重 加权 composite"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_quality.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\post_live_verification.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_source_reliability.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§29 6DQ+§53 5PLV(paper/live/reconcile/risk/checksum/position)+§83 5 Reliability(U/A/T/C/C)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 60

acceptance_criteria:
  - "DQDimension 枚举 6 成员——Completeness/Accuracy/Consistency/Timeliness/Uniqueness/Validity——每成员 check_func(DataFrame→float score)"
  - "PLV 5-check: order_count(paper vs live deviation)/fill_rate(T+1 vs T-1)/risk_conformance/data_integrity(checksum)/pnl_reconcile(±$5/1000trades)"
  - "Reliability: 5-dim(Uptime/Accuracy/Timeliness/Completeness/Consistency) weighted composite(0.25+0.30+0.20+0.15+0.10=1.0)"

rollback_instructions: |
  git rm src/zephyr/governance/data_quality.py post_live_verification.py data_source_reliability.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0009"
blocked_by: []
status: "done"
tags_fn:
  - "data"
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
