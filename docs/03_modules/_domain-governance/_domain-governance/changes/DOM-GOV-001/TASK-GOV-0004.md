---
task_id: "TASK-GOV-0004"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-003——Rollback → Escalation 集成契约"

# ===== 内容 =====
title: "实现 G-CT-003：MOD-INF-021 (Rollback) → MOD-INF-022 (Escalation) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-003 集成契约：
  回滚失败或回滚后验证不通过（Rollback auto_guard 后验失败）时，Rollback 产出 rollback_result → Escalation 消费，升级到人工处理。
  需实现：
  1. Rollback.rollback_result 数据格式定义（含 rollback_id、target、status、validation_result、error_detail）
  2. Escalation 消费 rollback_result 的入口（Escalation.on_rollback_failure()）
  3. 升级触发条件：rollback_result.status = FAILED 或 validation_result = FAIL
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\result_types.py"
    description: "RollbackResult Pydantic V2 BaseModel——回滚结果数据结构"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
    description: "Escalation 消费端——on_rollback_failure() 接口"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_003_rollback_to_escalation.py"
    description: "G-CT-003 集成测试——回滚失败→人工升级"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\result_types.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_003_rollback_to_escalation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-003"
    reason: "契约定义——回滚失败→升级人工处理"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——RollbackResult 使用 BaseModel"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-003 契约定义——Rollback→Escalation 数据流"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
    reason: "TASK-GOV-0003 的产出——Rollback 公共接口"

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
  - "RollbackResult 模型定义：Pydantic V2 BaseModel——含 rollback_id/target/status/validation_result/error_detail"
  - "Escalation.on_rollback_failure(result: RollbackResult) 接收回滚失败结果并生成升级工单"
  - "升级触发条件正确：rollback_result.status=FAILED 或 validation_result=FAIL"
  - "G-CT-003 集成测试覆盖：回滚成功→不升级、回滚失败→升级触发、验证不通过→升级触发"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\rollback\result_types.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\escalation\contracts.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_003_rollback_to_escalation.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0003"
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
