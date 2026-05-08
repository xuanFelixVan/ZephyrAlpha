---
task_id: "TASK-GOV-0005"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-004——Escalation → RBAC 集成契约"

# ===== 内容 =====
title: "实现 G-CT-004：MOD-INF-022 (Escalation) → MOD-INF-018 (RBAC) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-004 集成契约：
  升级到人工审批时，Escalation 需要验证审批人的代理权限，调用 RBAC 验证 human_approver 权限。
  需实现：
  1. Escalation.approval_request 数据格式定义（含 task_id、requested_action、human_approver、reason）
  2. RBAC 验证审批人权限的接口（RBAC.verify_approver()——验证 human_approver 是否有代理权限执行 requested_action）
  3. 此为反向引用——Escalation→RBAC，与 G-CT-001 RBAC→Audit 形成有向图
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\approval.py"
    description: "ApprovalRequest Pydantic V2 BaseModel——审批请求数据结构"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\approver_check.py"
    description: "RBAC.verify_approver()——验证审批人代理权限"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_004_escalation_to_rbac.py"
    description: "G-CT-004 集成测试——升级审批→RBAC 权限验证"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\approval.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\approver_check.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_004_escalation_to_rbac.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-004"
    reason: "契约定义——升级审批→RBAC 权限验证"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 2"
    reason: "施工顺序——Escalation 属于 Phase 2，依赖 Phase 1 的 RBAC"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-004 契约定义——Escalation→RBAC 审批人验证"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "TASK-GOV-0002 的产出——RBAC 公共接口"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
    reason: "TASK-GOV-0004 的产出——Escalation 公共接口"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M5"
estimated_tokens: 9000
timeout_minutes: 25

# ===== 验收标准 =====
acceptance_criteria:
  - "ApprovalRequest 模型定义：Pydantic V2 BaseModel——含 task_id/requested_action/human_approver/reason"
  - "RBAC.verify_approver(approval: ApprovalRequest) 返回 approver 是否有权限执行 requested_action"
  - "Escalation 在发起升级流程前调用 RBAC.verify_approver()——验证通过才继续"
  - "G-CT-004 集成测试覆盖：有效审批人→通过、无效审批人→拒绝、权限不足→拒绝"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\escalation\approval.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_rbac\approver_check.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_004_escalation_to_rbac.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0002"
  - "TASK-GOV-0004"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "security"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "DOM-GOV-001"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
