---
task_id: "TASK-GOV-0008"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-007——Agent Spec → RBAC/Audit 集成契约"

# ===== 内容 =====
title: "实现 G-CT-007：MOD-INF-019 (Agent Spec) → MOD-INF-018 (RBAC) + MOD-INF-020 (Audit) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-007 集成契约：
  Agent Spec（agent能力声明）是治理域的入口真源——每个 agent 必须在 Spec Registry 注册其 claim 的能力范围。
  部署前 RBAC 验证 agent 的能力声明范围内权限；Audit 记录 Spec 声明与实际的 diff。
  需实现：
  1. Agent Spec Registry 能力声明格式（agent_id、claimed_capabilities、model_provider）
  2. Agent.deploy() 前调用 RBAC.verify_capability_scope()——验证 claimed_capabilities 权限
  3. Agent Spec 能力注册 →Audit 写入能力声明记录
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
    description: "Agent Spec Registry——AgentCapability Pydantic V2 BaseModel + register/deploy 接口"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\capability_check.py"
    description: "RBAC.verify_capability_scope()——验证 claimed_capabilities 权限范围"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\spec_auditor.py"
    description: "Audit.record_agent_spec()——记录 Agent Spec 注册与变更"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_007_spec_to_rbac_audit.py"
    description: "G-CT-007 集成测试——Agent Spec 注册→RBAC+Audit"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\capability_check.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\spec_auditor.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_007_spec_to_rbac_audit.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-007"
    reason: "契约定义——Agent Spec 治理域入口→RBAC+Audit"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 4"
    reason: "施工顺序——Agent Spec 属于 Phase 4"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-007 契约定义——Agent Spec→RBAC+Audit"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "TASK-GOV-0002 的产出——RBAC 公共接口"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    reason: "TASK-GOV-0002 的产出——Audit 公共接口"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M5"
estimated_tokens: 12000
timeout_minutes: 30

# ===== 验收标准 =====
acceptance_criteria:
  - "AgentCapability 模型定义：Pydantic V2 BaseModel——含 agent_id/claimed_capabilities/model_provider"
  - "Agent Spec Registry.register() 注册 agent 能力声明→Audit.record_agent_spec() 写入"
  - "Agent.deploy() 前调用 RBAC.verify_capability_scope()——超出能力声明的权限拒绝部署"
  - "G-CT-007 集成测试覆盖：合法注册→通过、能力溢出→拒绝、变更能力→Audit diff 记录"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_spec\registry.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_rbac\capability_check.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\governance\audit_trail\spec_auditor.py
  4. 删除 D:\ZephyrAlpha\tests\governance\test_gct_007_spec_to_rbac_audit.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0002"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "security"
  - "observability"
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
