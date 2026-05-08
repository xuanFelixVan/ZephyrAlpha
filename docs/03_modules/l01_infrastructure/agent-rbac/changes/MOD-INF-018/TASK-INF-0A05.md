---
task_id: "TASK-INF-0A05"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.4 L1 — RBAC 三层权限模型 + D-018-01"

title: "实现L1 RBACGuard — 三层权限模型(always_allow/auto_guard/blocked)"
description: |
  实现rbac_guard.py与identity.py。三层权限模型：95% always_allow + 4% auto_guard + 1% blocked。
  AgentIdentity含maturity_level(L0_INTERN/L1_JUNIOR/L2_REGULAR/L3_SENIOR/L4_PRINCIPAL)、
  权限角色、IDE来源(TRAE/Cursor/RooCode/CLI)、session_token、delegation_chain。
  角色定义：Reader/Writer/Executor/Admin/Auditor五种基础角色。
  实施D-018-01：分层信任策略——95/4/1分布，取消needs_approval层。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
    description: "AgentIdentity/Role/MaturityLevel/RoleBinding/DelegationChain/delegation_depth/IDESource类型定义"

  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rbac_guard.py"
    description: "RBACGuard——基于角色的always_allow/auto_guard/blocked判定"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_identity.py"
    description: "测试AgentIdentity/MaturityLevel/DelegationChain"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_rbac_guard.py"
    description: "测试三层权限判定——always_allow/auto_guard/blocked/RoleBinding超时/Maturity上限"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rbac_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_identity.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_rbac_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制Pydantic V2——AgentIdentity/MaturityLevel/Role类型使用BaseModel"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.4 L1 RBAC+§2.13 Agent身份模型+§1.3多IDE约束+决策D-018-01"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "AgentIdentity.pydantic V2 BaseModel——含maturity_level/session_token/delegation_chain/ide_source字段"
  - "MaturityLevel五级: L0_INTERN/L1_JUNIOR/L2_REGULAR/L3_SENIOR/L4_PRINCIPAL"
  - "RBACGuard——check()返回PermissionDecision(ALLOW/AUTO_GUARD/BLOCKED)"
  - "always_allow操作无需代理确认"
  - "auto_guard操作执行→记录后验→失败自动回滚"
  - "blocked操作拒绝且输出拒绝原因到审计日志"
  - "95%覆盖目标——always_allow >= 90%操作, auto_guard <= 8%, blocked <= 2%"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\identity.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\rbac_guard.py
  3. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_identity.py
  4. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_rbac_guard.py

depends_on:
  - "TASK-INF-0A02"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
