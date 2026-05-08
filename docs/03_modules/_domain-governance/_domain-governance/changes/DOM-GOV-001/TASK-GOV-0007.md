---
task_id: "TASK-GOV-0007"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-006——Budget → Escalation 集成契约"

# ===== 内容 =====
title: "实现 G-CT-006：MOD-INF-024 (Budget) → MOD-INF-022 (Escalation) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-006 集成契约：
  Budget Enforcer 检测到预算告急时（Burn Rate > 阈值 或 全局预算耗尽），产出 budget_alert → Escalation 消费，启动升级流程。
  需实现：
  1. Budget.budget_alert 数据格式定义（含 alert_id、detected_at、session_id、budget_type、burn_rate、burn_rate_threshold、remaining_budget、severity）
  2. Escalation 消费 budget_alert 的接口（Escalation.on_budget_alert()）
  3. 触发条件（与蓝图 §3 G-CT-006 完全一致）：
     - Burn Rate > 阈值（consumption_rate 超过 burn_rate_threshold）
     - 全局预算耗尽（remaining_budget ≤ 0）
  4. 严重程度分级：WARNING（Burn Rate > 阈值）—通知 / CRITICAL（全局预算耗尽）—升级
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\alerts.py"
    description: "BudgetAlert Pydantic V2 BaseModel——预算告急事件"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\budget_handler.py"
    description: "Escalation.on_budget_alert()——消费预算告急事件启动升级"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_006_budget_to_escalation.py"
    description: "G-CT-006 集成测试——预算告急（Burn Rate超限/预算耗尽）→升级处理"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\alerts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\budget_handler.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_006_budget_to_escalation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-006"
    reason: "契约定义——预算超标→升级处理"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 3"
    reason: "施工顺序——Budget 属于 Phase 3"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-006 契约定义——Budget→Escalation 预算告急（Burn Rate > 阈值 | 全局预算耗尽）→启动升级流程"
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
  - "BudgetAlert 模型定义：Pydantic V2 BaseModel——含 alert_id/detected_at/session_id/budget_type/burn_rate/burn_rate_threshold/remaining_budget/severity"
  - "触发条件 1—Burn Rate > 阈值：burn_rate > burn_rate_threshold → BudgetAlert(severity=WARNING) → Escalation.on_budget_alert() 通知"
  - "触发条件 2—全局预算耗尽：remaining_budget ≤ 0 → BudgetAlert(severity=CRITICAL) → Escalation.on_budget_alert() 启动升级流程"
  - "G-CT-006 集成测试覆盖：预算正常→不触发、Burn Rate 超标→WARNING 通知、预算耗尽→CRITICAL 升级"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\budget_enforcer\alerts.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\escalation\budget_handler.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_006_budget_to_escalation.py

# ===== 依赖 =====
depends_on:
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
