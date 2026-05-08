---
task_id: "TASK-SYS-0017"
source_blueprint: "SYS-MASTER-001"
source_section: "§22 合规映射 + §23 纵深防御L1-L6 + §47 金融合规与法律"

title: "合规映射(5法规: KYC/AML/MiFID II/GDPR/SOX) + 纵深防御6层(依赖审计→断路器) + 金融合规(3×7×4框架)体系搭建"
description: |
  将 SYS-MASTER-001 §22 合规映射 + §23 纵深防御 + §47 金融合规与法律三合一落地。
  §22 合规映射: KYC(1)/AML(1)/MiFID II(1—个人交易豁免)/GDPR(always→data_minimization+L3_Confidential)/SOX(N/A personal→retain 5yr+immutable_runtime_assertions)。
  每法规→control mapping + status(compliant/exempt/non_compliant)+evidence_path。
  §23 纵深防御 L1-L6:
  L1-依赖审计 / L2-静态分析 / L3-沙箱隔离(wasmtime-py) / L4-Secrets(local vault+Git加密) / L5-审计追踪(every mutation logged)/ L6-断路器(自动熔断+自愈)。
  每层 enabled/tech_stack/audit_frequency 定义。
  §47 金融合规: 3合规层×7保障措施×4协议(Client Statement/MRM/Record Keeping/Incident Notification)。
  本卡搭建 compliance_matrix.py + defense_depth.py + financial_compliance.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\compliance_matrix.py"
    description: "§22 5法规→control→status→evidence_path 合规映射矩阵"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\defense_depth.py"
    description: "§23 L1-L6 纵深防御——依赖审计→静态分析→沙箱→Secrets→审计追踪→断路器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\financial_compliance.py"
    description: "§47 3层×7保障×4协议 金融合规框架"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\compliance_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\defense_depth.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\financial_compliance.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§22 合规映射(KYC/AML/MiFID/GDPR/SOX)+§23 L1-L6 纵深防御(依赖审计→断路器)+§47 金融合规3×7×4"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 24000
timeout_minutes: 65

acceptance_criteria:
  - "ComplianceItem: reg_id/status(compliant/exempt/non_compliant)/control/evidence_path/last_audit——5条注册"
  - "DefenseLayer 枚举 L1_DEP_AUDIT→L6_CIRCUIT_BREAKER——每层 enabled(bool)/tech_stack/audit_frequency_days"
  - "financial_compliance.py 定义 ComplianceLayer(3)/Safeguard(7)/Protocol(4)——每 Protocol description+owner+review_date"

rollback_instructions: |
  git rm src/zephyr/governance/compliance_matrix.py defense_depth.py financial_compliance.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0014"
blocked_by: []
status: "done"
tags_fn:
  - "security"
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
