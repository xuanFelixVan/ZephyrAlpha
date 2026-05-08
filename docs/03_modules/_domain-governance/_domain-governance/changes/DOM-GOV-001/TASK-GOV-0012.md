---
task_id: "TASK-GOV-0012"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §4 Phase 3——Drift Detector (MOD-INF-023) + Budget Enforcer (MOD-INF-024) 施工启动门禁"

# ===== 内容 =====
title: "Phase 3 施工启动门禁：Drift Detector + Budget Enforcer——验证 G-CT-005/006 契约实现就绪"
description: |
  实现 DOM-GOV-001 §4 Phase 3 施工门禁：
  Phase 3 包含 Drift Detector（MOD-INF-023）和 Budget Enforcer（MOD-INF-024）。
  本任务卡为门禁卡——验证 Phase 3 两个模块的施工前提已满足：
  1. Phase 2 门禁已通过（TASK-GOV-0011 完成）
  2. G-CT-005 集成测试通过（Drift→Rollback 漂移自动修复）
  3. G-CT-006 集成测试通过（Budget→Escalation 预算违规升级）
  4. Phase 3 门禁检查通过后，允许 Phase 4 启动
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\events.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\drift_fix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\violations.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\budget_handler.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_005_drift_to_rollback.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_006_budget_to_escalation.py"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\ZephyrAlpha\tests\governance\test_phase4_gate_check.py"
    description: "Phase 3 门禁验证测试——G-CT-005/006 全部通过"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\governance\\test_phase3_gate_check.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 3"
    reason: "Phase 3 施工门禁——Drift+Budget 启动前提"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 约束"
    reason: "Phase 3 依赖 Phase 2 门禁通过"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§4 Phase 3——施工顺序与门禁条件"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 6000
timeout_minutes: 15

# ===== 验收标准 =====
acceptance_criteria:
  - "Phase 3 门禁检查脚本通过：G-CT-005/006 集成测试 ALL PASS"
  - "Drift 和 Budget 的 __init__.py 正确声明 module_id"
  - "Phase 3 门禁通过后，手动在 DOM-GOV-001 blueprint.md §2 中更新 Drift Detector 和 Budget Enforcer 进度"
  - "回滚方案：删除 test_phase3_gate_check.py"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\governance\test_phase3_gate_check.py
  2. 如果 blueprint.md §2 进度字段被修改——人工回退

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0006"
  - "TASK-GOV-0007"
  - "TASK-GOV-0011"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
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
