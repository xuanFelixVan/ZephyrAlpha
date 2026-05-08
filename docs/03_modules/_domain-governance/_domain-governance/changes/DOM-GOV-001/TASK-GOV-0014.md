---
task_id: "TASK-GOV-0014"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §5——循环依赖解决裁定"

# ===== 内容 =====
title: "实现 §5 循环依赖裁决：Audit 不依赖 RBAC——仅 RBAC 单向调用 Audit"
description: |
  实现 DOM-GOV-001 §5 循环依赖解决裁定：
  检测到系统循环依赖风险：所有模块均依赖 RBAC，但 RBAC 也需要调用 Audit。
  裁定结果：打破循环——Audit 不依赖 RBAC。RBAC 单向调用 Audit，Audit 只记录事实，不验证权限。
  需实现：
  1. 代码审计脚本——扫描 governance/ 下所有 .py 文件，确认 Audit 无任何 import RBAC
  2. 集成测试验证——所有 Audit 接口可独立运行（不加载 RBAC 上下文）
  3. 将 §5 裁定结论写入 governance/__init__.py 的 docstring
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_cycle_dependency_audit_isolation.py"
    description: "循环依赖测试——Audit 独立运行验证 + 无 RBAC import 扫描"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\check_audit_rbac_isolation.py"
    description: "静态分析脚本——扫描 Audit 目录确认无 RBAC import"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\governance\\test_cycle_dependency_audit_isolation.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_audit_rbac_isolation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\__init__.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§5"
    reason: "循环依赖裁定——确认 Audit 不依赖 RBAC"
  - module_id: "GOV-DOC-002"
    section: "§四"
    reason: "新模块归属——治理域各模块间导入规则从属于 LPC 架构"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§5——循环依赖裁定结论"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    reason: "审计 Audit 无 RBAC import"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "验证 RBAC 单向调用 Audit"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "路径映射——scripts/governance/ 位置规范"

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
  - "check_audit_rbac_isolation.py 扫描 src/zephyr/governance/audit_trail/ 下所有 .py 文件——确认 0 处 import RBAC"
  - "test_cycle_dependency_audit_isolation.py 验证 Audit.write() 可独立运行——不依赖 RBAC.check() 上下文"
  - "governance/__init__.py docstring 明确记录 §5 裁定结论：'Audit 不依赖 RBAC。RBAC 单向调用 Audit。'"
  - "若发现 Audit→RBAC import——立即报告并阻断，不执行修复"
  - "回滚方案：删除新创建的 2 个文件 + 还原 __init__.py docstring"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\governance\test_cycle_dependency_audit_isolation.py
  2. 删除 D:\ZephyrAlpha\scripts\governance\check_audit_rbac_isolation.py
  3. 用 git checkout 还原 D:\ZephyrAlpha\src\zephyr\governance\__init__.py 或删除 docstring 行

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0001"
  - "TASK-GOV-0002"
blocked_by: []

# ===== 状态 =====
status: "created"

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
