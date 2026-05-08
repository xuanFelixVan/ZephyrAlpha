---
task_id: "TASK-GOV-0009"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-008——A2A → RBAC/Escalation 集成契约 + §4 Phase 4 HOLD"

# ===== 内容 =====
title: "实现 G-CT-008：MOD-INF-025 (A2A) → MOD-INF-018 (RBAC) + MOD-INF-022 (Escalation) 集成契约——仅契约定义，Phase 4 Hold"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-008 集成契约：
  A2A Protocol 处理 agent-to-agent 通信——每次通信需 RBAC 验证发送/接收权限 + Escalation 记录通信失败。
  需实现：
  1. A2A Communication 数据格式定义（含 a2a_id、from_agent_id、to_agent_id、message_type、payload_size、transfer_token_count）
  2. A2A.send() 前调用 RBAC.verify_a2a_pair()——验证 from/to 通信权限
  3. A2A 通信失败后调用 Escalation.on_a2a_failure()
  4. Phase 4 HOLD 标记：A2A 模块与 Agent Spec 并列 Phase 4——最早在 Phase 4 启动施工
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\protocol.py"
    description: "A2ACommunication Pydantic V2 BaseModel——通信数据结构"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\a2a_check.py"
    description: "RBAC.verify_a2a_pair()——验证 agent 间通信权限"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\a2a_failure.py"
    description: "Escalation.on_a2a_failure()——跨 agent 通信失败升级"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_008_a2a_to_rbac_escalation.py"
    description: "G-CT-008 集成测试——agent-to-agent 通信→RBAC+Escalation"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\a2a_check.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\a2a_failure.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_008_a2a_to_rbac_escalation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-008"
    reason: "契约定义——A2A 通信→RBAC+Escalation"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 4 + §6 R3"
    reason: "A2A Phase 4 Hold——最早 Phase 4 施工，与其他 Phase 3 模块不可并发"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-008 契约定义——A2A→RBAC+Escalation 通信权限"
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
estimated_tokens: 11000
timeout_minutes: 30

# ===== 验收标准 =====
acceptance_criteria:
  - "A2ACommunication 模型定义：Pydantic V2 BaseModel——含 a2a_id/from_agent_id/to_agent_id/message_type/payload_size/transfer_token_count"
  - "RBAC.verify_a2a_pair(from, to) 返回通信权限判定——双方均在 allowed_talk 对表中"
  - "A2A 通信失败→Escalation.on_a2a_failure()——记录失败、触发重试或降级"
  - "G-CT-008 集成测试覆盖：合法通信→通过、未注册 agent→拒绝、通信失败→升级"
  - "Phase 4 HOLD：本任务的契约定义和代码实现放在 Phase 4，不提前到 Phase 1-3"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\a2a\protocol.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_rbac\a2a_check.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\governance\escalation\a2a_failure.py
  4. 删除 D:\ZephyrAlpha\tests\governance\test_gct_008_a2a_to_rbac_escalation.py

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
