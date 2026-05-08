---
task_id: "TASK-GOV-0010"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §4 Phase 1——Audit Trail (MOD-INF-020) + Agent RBAC (MOD-INF-018) 施工启动门禁"

# ===== 内容 =====
title: "Phase 1 施工启动门禁：Audit Trail + Agent RBAC——验证 G-CT-001 契约实现就绪"
description: |
  实现 DOM-GOV-001 §4 Phase 1 施工门禁：
  Phase 1 包含 Audit Trail（MOD-INF-020）和 Agent RBAC（MOD-INF-018）。
  本任务卡为门禁卡——验证 Phase 1 两个模块的施工前提已满足：
  1. Audit Trail 的 Audit.write() 接口已实现（消费自 TASK-GOV-0002）
  2. Agent RBAC 的 RBAC.check() 接口已实现——调用 Audit.write()
  3. G-CT-001 集成测试通过（RBAC→Audit 端到端数据流通）
  4. bytebuddy 超管角色伪实现——硬编码单个超管 account（允许 bootstrap）
  5. Phase 1 门禁检查通过后，允许 Phase 2 启动
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_001_rbac_to_audit.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\bootstrap_superadmin.py"
    description: "bytebuddy 超管角色伪实现——硬编码单个超管 account"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_phase1_gate_check.py"
    description: "Phase 1 门禁验证测试——G-CT-001 通过 + bytebuddy bootstrap"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\bootstrap_superadmin.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_phase1_gate_check.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 1"
    reason: "Phase 1 施工门禁——Audit+RBAC 启动前提"
  - module_id: "DOM-GOV-001"
    section: "§5"
    reason: "循环依赖裁决——Audit 不依赖 RBAC，RBAC 单向依赖 Audit"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§4 Phase 1——施工顺序与门禁条件"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    reason: "TASK-GOV-0002 的产出——Audit.write() 接口"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "TASK-GOV-0002 的产出——RBAC 侧集成代码"
  - file_path: "D:\\ZephyrAlpha\\tests\\governance\\test_gct_001_rbac_to_audit.py"
    reason: "TASK-GOV-0002 的产出——G-CT-001 集成测试"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 8000
timeout_minutes: 20

# ===== 验收标准 =====
acceptance_criteria:
  - "bytebuddy 超管角色伪实现：硬编码单个 account——bootstrap/superadmin 角色，无需数据库"
  - "Phase 1 门禁检查脚本通过：G-CT-001 集成测试 ALL PASS + bytebuddy 超管可调用 RBAC.check()"
  - "Audit 和 RBAC 的 __init__.py 正确声明 module_id"
  - "Phase 1 门禁通过后，手动在 DOM-GOV-001 blueprint.md §2 中更新 Audit Trail 和 Agent RBAC 进度为 >0%"
  - "回滚方案：删除 bootstrap_superadmin.py 和 test_phase1_gate_check.py"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\agent_rbac\bootstrap_superadmin.py
  2. 删除 D:\ZephyrAlpha\tests\governance\test_phase1_gate_check.py
  3. 如果 blueprint.md §2 进度字段被修改——人工回退

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0002"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "security"
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
