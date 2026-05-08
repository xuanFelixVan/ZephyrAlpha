---
task_id: "TASK-SYS-0014"
source_blueprint: "SYS-MASTER-001"
source_section: "§19 模型风险管理 MR101-MR113"

title: "模型风险 13 条治理(MR101 Inventory→MR113 Retirement)自动化合规管线"
description: |
  将 SYS-MASTER-001 §19 的 13 条模型风险管理(Model Risk Management)治理要求工程化落地。
  MR101 Model Inventory——全量模型注册登记。
  MR102 Validation Framework——验证框架定义。
  MR103 Independent Review——独立审查。
  MR104 Documentation——文档化。
  MR105 Change Management——变更管理。
  MR106 Input Data Integrity——输入数据完整性。
  MR107 Output Analysis——输出分析。
  MR108 Model Limitation——局限性声明。
  MR109 Ongoing Monitoring——持续监控。
  MR110 Exception Handling——异常处理。
  MR111 Audit Trail——审计追踪。
  MR112 Stress Testing——压力测试。
  MR113 Model Retirement——模型退役流程。
  每条映射 check_func→auto audit→compliance_score。
  本卡搭建 model_risk_governance.py + model_risk_report.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_risk_governance.py"
    description: "§19 MR101-MR113——13条 MR governance item + auto check pipeline"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_risk_report.py"
    description: "§19 合规报告——compliance_pct / gap_analysis / remediation_plan"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_risk_governance.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_risk_report.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§19 MR101-MR113——13条治理要求(Inventory→Validation→Review→Doc→Change→Data→Output→Limitation→Monitor→Exception→Audit→Stress→Retire)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 35

acceptance_criteria:
  - "MREntry 枚举 13 成员 MR101→MR113——每成员含 checklist_item / auto_check_func / owner / last_review"
  - "MRComplianceChecker.run() 遍历13条→返回 compliance_pct(目标≥90%)"
  - "model_risk_report.py generate→ Dashboard + gap_analysis + remediation_plan"

rollback_instructions: |
  git rm src/zephyr/governance/model_risk_governance.py model_risk_report.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0012"
blocked_by: []
status: "created"
tags_fn:
  - "compliance"
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
