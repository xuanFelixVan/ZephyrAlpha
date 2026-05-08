---
task_id: "TASK-GOV-0003"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-002——Audit → Rollback 集成契约"

# ===== 内容 =====
title: "实现 G-CT-002：MOD-INF-020 (Audit) → MOD-INF-021 (Rollback) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-002 集成契约：
  Audit 的 anomaly_detector 检测到异常操作签名时，产出异常事件→Rollback 消费，触发自动回滚。
  需实现：
  1. Audit.anomaly_detector 异常事件定义（anomaly事件格式：含操作签名、时间、agent_id、资源路径）
  2. Rollback 消费 Audit 异常事件的接口（Rollback.on_audit_anomaly()）
  3. 事件传递的数据结构定义（AnomalyEvent Pydantic V2 BaseModel）
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\anomaly.py"
    description: "Audit 异常检测器——AnomalyEvent Pydantic V2 BaseModel"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
    description: "Rollback 消费端——on_audit_anomaly() 接口"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_002_audit_to_rollback.py"
    description: "G-CT-002 集成测试——Audit 异常事件→Rollback 触发"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\anomaly.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_002_audit_to_rollback.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-002"
    reason: "契约定义——Audit 异常检测→Rollback 触发"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——AnomalyEvent 使用 BaseModel"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-002 契约定义——Audit→Rollback 异常事件数据流"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    reason: "TASK-GOV-0002 的产出——Audit.write() 公共接口"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M5"
estimated_tokens: 10000
timeout_minutes: 25

# ===== 验收标准 =====
acceptance_criteria:
  - "AnomalyEvent 模型定义：Pydantic V2 BaseModel——含 agent_id/operation_signature/timestamp/resource_path/anomaly_type"
  - "Audit.anomaly_detector 产出 AnomalyEvent 实例——异常操作签名不匹配时触发"
  - "Rollback.on_audit_anomaly(event: AnomalyEvent) 接收异常事件并执行回滚决策"
  - "G-CT-002 集成测试覆盖：正常操作→不触发、异常签名→AnomalyEvent 产出→Rollback 消费"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\audit_trail\anomaly.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\rollback\contracts.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_002_audit_to_rollback.py

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
