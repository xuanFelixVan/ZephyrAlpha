---
task_id: "TASK-GOV-0017"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §6 风险 R2——所有模块均依赖 RBAC，但 RBAC/Audit 存在循环依赖风险"

# ===== 内容 =====
title: "风险 R2 缓解：RBAC/Audit 循环依赖打破验证——确保全链路单向依赖"
description: |
  缓解 DOM-GOV-001 §6 风险 R2："所有模块均依赖 RBAC——RBAC 成为治理域单点故障源；RBAC 与 Audit 互相依赖可能循环"。
  缓解策略：
  1. §5 裁定已确认：Audit 不依赖 RBAC（TASK-GOV-0014 实施）
  2. 本任务卡在 Phase 1-4 门禁中嵌入循环依赖检查——每次门禁通过前自动扫描 import
  3. 构建 governance/ 下有向依赖图——确认无意外的反向依赖
  4. RBAC 作为治理域单点故障源：Phase 1 中实施 bytebuddy 超管冗余（硬编码超管不依赖数据库）
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_audit_rbac_isolation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\dependency_graph.py"
    description: "治理域有向依赖图——扫描所有 import 生成 graphviz/dict"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_dependency_graph_acyclic.py"
    description: "依赖无循环测试——验证 governance/ 下有向图无环"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\dependency_graph.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_dependency_graph_acyclic.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§6 R2"
    reason: "风险 R2——RBAC 单点故障+循环依赖"
  - module_id: "DOM-GOV-001"
    section: "§5"
    reason: "§5 裁定——打破 RBAC/Audit 循环"
  - module_id: "GOV-DOC-002"
    section: "§四"
    reason: "依赖方向——B 轨模块间导入规则"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§6 R2——风险定义与缓解策略"
  - file_path: "D:\\ZephyrAlpha\\scripts\\governance\\check_audit_rbac_isolation.py"
    reason: "TASK-GOV-0014 的产出——Audit/RBAC 隔离检查"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "RBAC 公共接口——确认单向调用方向"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 9000
timeout_minutes: 25

# ===== 验收标准 =====
acceptance_criteria:
  - "dependency_graph.py 扫描 governance/ 下所有 .py 文件——构建模块级有向依赖图"
  - "test_dependency_graph_acyclic.py 验证有向图无环——若检测到环列出具体路径"
  - "Phase 1 门禁检查中包含循环依赖检查——每次门禁通过前自动运行"
  - "RBAC 冗余：bytebuddy 超管在 RBAC 不可用时提供应急权限通道（TASK-GOV-0010）"
  - "回滚方案：删除新创建的 2 个文件"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\dependency_graph.py
  2. 删除 D:\ZephyrAlpha\tests\governance\test_dependency_graph_acyclic.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0014"
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
  - "risk:R2"

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
