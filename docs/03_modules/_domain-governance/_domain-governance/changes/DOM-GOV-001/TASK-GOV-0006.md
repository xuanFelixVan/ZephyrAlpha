---
task_id: "TASK-GOV-0006"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-005——Drift → Rollback 集成契约"

# ===== 内容 =====
title: "实现 G-CT-005：MOD-INF-023 (Drift) → MOD-INF-021 (Rollback) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-005 集成契约：
  Drift Detector 检测到可自动修复的漂移时，产出 drift_event（含 fix_suggestion）→ Rollback 消费，执行自动修复。
  需实现：
  1. Drift.drift_event 数据格式定义（含 drift_id、detected_at、target、drift_type、fix_suggestion、auto_fixable）
  2. Rollback 消费 drift_event 的接口（Rollback.on_drift_fix()）
  3. 自动修复决策：auto_fixable=True → Rollback 执行修复；auto_fixable=False → 仅记录，不自动修复
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\result_types.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\events.py"
    description: "DriftEvent Pydantic V2 BaseModel——漂移事件定义"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\drift_fix.py"
    description: "Rollback.on_drift_fix()——消费漂移事件执行自动修复"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_005_drift_to_rollback.py"
    description: "G-CT-005 集成测试——漂移检测→自动修复"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\events.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\drift_fix.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_005_drift_to_rollback.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-005"
    reason: "契约定义——漂移检测→自动修复"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 3"
    reason: "施工顺序——Drift 属于 Phase 3，依赖 Phase 2 的 Rollback"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——DriftEvent 使用 BaseModel"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-005 契约定义——Drift→Rollback 自动修复"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\result_types.py"
    reason: "TASK-GOV-0004 的产出——RollbackResult 数据结构"

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
  - "DriftEvent 模型定义：Pydantic V2 BaseModel——含 drift_id/detected_at/target/drift_type/fix_suggestion/auto_fixable"
  - "Rollback.on_drift_fix(event: DriftEvent) 接收漂移事件——auto_fixable=True 时执行修复，False 时仅记录"
  - "自动修复结果写回 DriftEvent——状态从 DETECTED→FIXED 或 DETECTED→MANUAL_REQUIRED"
  - "G-CT-005 集成测试覆盖：可自动修复漂移→修复成功、不可自动修复→仅记录"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\drift_detector\events.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\rollback\drift_fix.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_005_drift_to_rollback.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0003"
  - "TASK-GOV-0004"
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
