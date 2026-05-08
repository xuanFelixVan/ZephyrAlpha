---
task_id: "TASK-GOV-0015"
source_blueprint: "DOM-GOV-001"
source_section: "G-CT 契约下游锚点——验证全部 8 模块 had DOM-GOV-001 benchmark anchor"

# ===== 内容 =====
title: "G-CT 下游锚点验证：检查 8 个 L01 模块均已落锚 DOM-GOV-001 契约"
description: |
  验证 DOM-GOV-001 蓝图 "G-CT 契约下游锚点" 表格中的所有模块均已嵌入 DOM-GOV-001 跨域锚点：
  8 个模块的 blueprint.md 中必须包含 "DOM-GOV-001 G-CT-* benchmark anchor" 表格。
  模块列表：
  | MOD-INF-018 | docs/03_modules/l01_infrastructure/agent_rbac/blueprint.md       |
  | MOD-INF-019 | docs/03_modules/l01_infrastructure/agent_spec/blueprint.md      |
  | MOD-INF-020 | docs/03_modules/l01_infrastructure/audit_trail/blueprint.md     |
  | MOD-INF-021 | docs/03_modules/l01_infrastructure/rollback_system/blueprint.md |
  | MOD-INF-022 | docs/03_modules/l01_infrastructure/escalation_protocol/blueprint.md |
  | MOD-INF-023 | docs/03_modules/l01_infrastructure/drift_detector/blueprint.md  |
  | MOD-INF-024 | docs/03_modules/l01_infrastructure/budget_enforcer/blueprint.md |
  | MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a_protocol/blueprint.md    |
  本任务卡检查每个模块的 blueprint.md 中是否嵌入了 G-CT-* contractRef anchor 表格，并输出检查报告。
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent_rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent_spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit_trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback_system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\escalation_protocol\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift_detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget_enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\a2a_protocol\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\verify_downstream_anchors.py"
    description: "下游锚点验证脚本——扫描 8 个模块的 blueprint.md 确认 DOM-GOV-001 anchor"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\downstream-anchor-report.md"
    description: "下游锚点检查报告——逐模块标注是否落锚"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\verify_downstream_anchors.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\downstream-anchor-report.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\**\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "G-CT 契约下游锚点"
    reason: "全部 8 模块需嵌入 DOM-GOV-001 anchor table"
  - module_id: "GOV-DOC-002"
    section: "§三"
    reason: "跨域契约锚——治理域为 B 轨横切域"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "G-CT 下游锚点——8 模块 × G-CT contractRef 映射"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "ModuleID→Blueprint 路径映射真源"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 15000
timeout_minutes: 40

# ===== 验收标准 =====
acceptance_criteria:
  - "verify_downstream_anchors.py 可运行并通过——输出逐模块报告"
  - "检查逻辑：扫描每个模块的 blueprint.md 是否包含 'DOM-GOV-001' 或 'G-CT-00' 关键词"
  - "downstream-anchor-report.md 逐模块标注：[OK] 已落锚 / [MISSING] 未落锚"
  - "未落锚模块列出具体的缺失项——缺 contractRef table 还是缺 anchor tag"
  - "若全部 8 模块均已落锚——报告判定 100%"
  - "回滚方案：删除新创建的文件"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\verify_downstream_anchors.py
  2. 删除 D:\ZephyrAlpha\docs\03_modules\_domain-governance\_domain-governance\changes\DOM-GOV-001\downstream-anchor-report.md

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0001"
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
