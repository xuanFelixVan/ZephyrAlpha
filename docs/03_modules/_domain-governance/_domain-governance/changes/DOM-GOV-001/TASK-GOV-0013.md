---
task_id: "TASK-GOV-0013"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §4 Phase 4——Agent Spec (MOD-INF-019) + A2A Protocol (MOD-INF-025) 施工启动门禁 + HOLD"

# ===== 内容 =====
title: "Phase 4 施工启动门禁：Agent Spec + A2A Protocol——验证 G-CT-007/008 契约实现就绪"
description: |
  实现 DOM-GOV-001 §4 Phase 4 施工门禁：
  Phase 4 包含 Agent Spec（MOD-INF-019）和 A2A Protocol（MOD-INF-025）。
  本任务卡为门禁卡——验证 Phase 4 两个模块的施工前提已满足：
  1. Phase 3 门禁已通过（TASK-GOV-0012 完成）
  2. G-CT-007 集成测试通过（Agent Spec→RBAC+Audit）
  3. G-CT-008 集成测试通过（A2A→RBAC+Escalation）
  4. A2A Phase 4 Hold 标记——A2A 模块仅在 Phase 4 启动，不提前到 Phase 1-3，与其他 Phase 3 模块不可并发
  5. Phase 4 门禁检查通过后，治理域 8 个模块全部完成 Phase 0 蓝图契约定义
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\capability_check.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\spec_auditor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\a2a_check.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\a2a_failure.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_007_spec_to_rbac_audit.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_008_a2a_to_rbac_escalation.py"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_phase4_gate_check.py"
    description: "Phase 4 门禁验证测试——G-CT-007/008 全部通过"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\governance\\test_phase4_gate_check.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 4"
    reason: "Phase 4 施工门禁——Agent Spec+A2A 启动前提"
  - module_id: "DOM-GOV-001"
    section: "§6 R3"
    reason: "风险 R3——A2A 仅在 Phase 4 启动施工"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§4 Phase 4 + §6 R3——施工顺序与 A2A Hold"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 7000
timeout_minutes: 20

# ===== 验收标准 =====
acceptance_criteria:
  - "Phase 4 门禁检查脚本通过：G-CT-007/008 集成测试 ALL PASS"
  - "Agent Spec 和 A2A 的 __init__.py 正确声明 module_id"
  - "A2A 模块未在 Phase 1-3 中出现任何代码——仅在 Phase 4 启动施工"
  - "Phase 4 门禁通过后，手动在 DOM-GOV-001 blueprint.md §2 中更新 Agent Spec 和 A2A 进度"
  - "回滚方案：删除 test_phase4_gate_check.py"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\governance\test_phase4_gate_check.py
  2. 如果 blueprint.md §2 进度字段被修改——人工回退

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0008"
  - "TASK-GOV-0009"
  - "TASK-GOV-0012"
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
