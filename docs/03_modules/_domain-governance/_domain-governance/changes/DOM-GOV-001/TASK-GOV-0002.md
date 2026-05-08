---
task_id: "TASK-GOV-0002"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §3 G-CT-001——RBAC → Audit 集成契约"

# ===== 内容 =====
title: "实现 G-CT-001：MOD-INF-018 (RBAC) → MOD-INF-020 (Audit) 集成契约"
description: |
  实现 DOM-GOV-001 §3 定义的 G-CT-001 集成契约：
  RBAC（MOD-INF-018）每次权限判定完成后，主动调用 Audit（MOD-INF-020）写入审计记录。
  数据流：RBAC.check() → result → RBAC 调用 Audit.write(result)。
  调用链单向——RBAC 依赖 Audit，Audit 不依赖 RBAC（Audit 只记录事实，不验证权限）。
  需实现：Audit.write() 接收 agent_id/permission/resource/decision_basis/timestamp/session_id。
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    description: "Audit.write() 公共接口定义——G-CT-001 契约消费端"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    description: "RBAC 侧调用 Audit 的集成代码——G-CT-001 契约生产端"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_001_rbac_to_audit.py"
    description: "G-CT-001 集成测试——RBAC→Audit 端到端数据流通"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_001_rbac_to_audit.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\*"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§3 G-CT-001"
    reason: "契约定义——RBAC→Audit 数据流格式与触发时机"
  - module_id: "DOM-GOV-001"
    section: "§5"
    reason: "循环依赖裁决——Audit 不依赖 RBAC，RBAC 单向依赖 Audit"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT-001 契约定义——数据字段与循环依赖打破方案"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "TaskCard 模型基座——agent_id/session_id/timestamp 字段真源"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\task-card-template.md"
    reason: "防漂移任务卡格式——下游路径规范"

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
  - "Audit.write() 接收参数：agent_id (str)、permission (str)、resource (str)、decision_basis (dict)、timestamp (datetime)、session_id (str)"
  - "Audit.write() 写入后返回写入确认（write_id 或 True），失败时抛出 AuditWriteException"
  - "RBAC.check() 执行后自动调用 Audit.write(result)——集成在 RBAC 侧而非 Audit 侧反向调用"
  - "G-CT-001 集成测试覆盖：正常权限判定→审计写入、权限拒绝→审计写入、Audit.write() 失败时不阻塞 RBAC 返回"
  - "Audit 无任何对 RBAC 的 import——符合 §5 单向依赖裁定"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\audit_trail\contracts.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_rbac\contracts.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_gct_001_rbac_to_audit.py
  4. 如果 tests/governance/__init__.py 为本任务新建——也删除之

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0001"
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
