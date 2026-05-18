---

task_id: "TASK-SYS-0007"
source_blueprint: "SYS-MASTER-001"
source_section: "§9 已知风险 + §10 后果声明"

title: "风险矩阵(4风险:操作/数据/法律/孤立) + 后果声明BLUF框架搭建"
description: |
  将 SYS-MASTER-001 §9 已知风险与 §10 后果声明工程化落地。
  §9 定义 4 大已知风险：操作风险（AI/AI为主的人为错误/系统错误/流程失败/外部事件）、
  数据风险（供应商停机/数据质量/备份失效）、法律与合规风险（法规违规/合同违约/KYC/AML）、
  孤立风险（系统孤岛/依赖孤岛/知识孤岛——类比微服务架构反模式）。
  每风险含 likelihood/impact/risk_level、mitigation/mitigator、trigger_flags[]、互动热图(risk→risk)。
  §10 定义 4 条后果声明：Alpha 不可用时的 BLUF（Bottom Line Up Front）宣告格式。
  本卡搭建 risk_matrix.py + consequence_manager.py。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\risk_matrix.py"
    description: "§9 4大风险矩阵——RiskItem(name,likelihood,impact,mitigation,trigger_flags,interaction_matrix)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\consequence_manager.py"
    description: "§10 后果声明——BLUF 格式 + 触发→恢复时间→升级链"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\risk_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\consequence_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§9 4大风险(操作/数据/法律/孤立) + §10 4条后果声明 BLUF 格式"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 30

acceptance_criteria:
  - "RiskItem 含 name/likelihood(1-5)/impact(1-5)/risk_level/mitigation/mitigator/trigger_flags[] 字段"
  - "4 风险全部注册——OPERATIONAL/DATA/LEGAL_COMPLIANCE/ISOLATION"
  - "互动热图: risk_a→risk_b 关联标记（如 DataRisk→OperationalRisk related=True）"
  - "ConsequenceDeclaration 含 alpha_unavailable→BLUF text→t_min_to_recover→escalation_chain"

rollback_instructions: |
  git rm src/zephyr/governance/risk_matrix.py consequence_manager.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0001"
blocked_by: []
status: "done"
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
