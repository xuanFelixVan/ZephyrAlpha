---
task_id: "TASK-GOV-0020"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §2 模块进度表 + §7 变更记录运维"

# ===== 内容 =====
title: "§2 模块清单进度追踪 + §7 变更记录——治理域施工进度看板更新与变更管理"
description: |
  管理 DOM-GOV-001 §2 模块清单的进度更新和 §7 变更记录运维：
  1. §2 模块清单表——8 个模块的进度列（最初全 0%），每个 Phase 门禁通过后更新对应模块进度
  2. §7 变更记录表——版本 v1.0.0~v1.0.2 的变更日志维护
  3. 变更记录格式：版本号/日期/变更类型（Add/Modify/Del）/ 变更范围 / 描述
  4. 语义版本规则：MAJOR（不兼容契约变更）/ MINOR（新增功能/契约）/ PATCH（措辞修正）
  5. 本任务卡不修改 blueprint.md——仅创建运维脚本体系确保进度可视化
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\domain_progress.json"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\sync_progress.py"
    description: "进度同步脚本——从 domain_progress.json 同步到 §2 模块表"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\changelog.py"
    description: "变更记录脚本——管理 §7 变更日志的读写"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\sync_progress.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\changelog.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§2"
    reason: "模块清单——8 模块进度追踪"
  - module_id: "DOM-GOV-001"
    section: "§7"
    reason: "变更记录——语义版本规则 MAJOR/MINOR/PATCH"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§2 模块进度表 + §7 变更记录"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\domain_progress.json"
    reason: "TASK-GOV-0016 的产出——治理域进度数据源"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 7000
timeout_minutes: 20

# ===== 验收标准 =====
acceptance_criteria:
  - "sync_progress.py 读取 domain_progress.json → 生成 §2 模块表更新（dry-run 模式，不直接修改 blueprint.md）"
  - "changelog.py 管理 §7 变更记录——读取/追加/验证格式"
  - "变更记录格式校验：版本号符合 MAJOR.MINOR.PATCH、日期 ISO8601、变更类型 Add/Modify/Del、变更范围非空"
  - "changelog.py 支持检查 same-date version --reject-first 防御模式——同日期多版本拒绝提交"
  - "回滚方案：删除 scripts/governance/sync_progress.py 和 changelog.py"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\sync_progress.py
  2. 删除 D:\ZephyrAlpha\scripts\governance\changelog.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0016"
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
