---
task_id: "TASK-GOV-0021"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 frontmatter depends_on——SYS-MASTER-001 + MOD-MASTER-001 CT 交叉检查"

# ===== 内容 =====
title: "依赖验证：SYS-MASTER-001 系统总蓝图 + MOD-MASTER-001 基建域蓝图 CT 交叉检查"
description: |
  验证 DOM-GOV-001 蓝图 frontmatter depends_on 的依赖关系一致：
  1. SYS-MASTER-001（_sys-master/blueprint.md）与 MOD-MASTER-001（_master-blueprint/blueprint.md）
     均已声明 DOM-GOV-001 的契约——确认层级关系无丢失
  2. 两方均引用 DOM-GOV-001 中定义的 Governance PIPELINE 作为 8 模块的管控流
  3. 交叉检查逻辑：
     - SYS-MASTER-001 §域间拓扑 中是否出现治理域节点（DOM-GOV-001）
     - MOD-MASTER-001 §B 轨模块表 中是否出现全部 8 个 MOD-INF-xxx
     - 双方契约表与 DOM-GOV-001 CT 编号是否一致
  4. 检查结果写入 dependency_crosscheck.md 报告
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\crosscheck_sys_master_deps.py"
    description: "CT 交叉检查脚本——验证 SYS-MASTER-001 + MOD-MASTER-001 与 DOM-GOV-001 一致"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\dependency_crosscheck.md"
    description: "依赖交叉检查报告——SYS-MASTER-001 + MOD-MASTER-001 CT mapping"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\crosscheck_sys_master_deps.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\dependency_crosscheck.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "frontmatter depends_on"
    reason: "依赖声明——SYS-MASTER-001 + MOD-MASTER-001"
  - module_id: "GOV-DOC-002"
    section: "§三"
    reason: "LPC 双轨——治理域（B 轨）→基建域（B 轨）→系统总图（A 轨）"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "frontmatter depends_on + 全本 8 契约——交叉检查真源"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "SYS-MASTER-001——系统总图的域间拓扑声明"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "MOD-MASTER-001——基建域模块表与契约"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "ModuleID→Blueprint 路径映射真源"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
estimated_tokens: 12000
timeout_minutes: 30

# ===== 验收标准 =====
acceptance_criteria:
  - "crosscheck_sys_master_deps.py 扫描 SYS-MASTER-001 §域间拓扑——确认出现 DOM-GOV-001 治理域节点"
  - "crosscheck_sys_master_deps.py 扫描 MOD-MASTER-001 §B 轨模块表——确认出现全部 8 个 MOD-INF-xxx"
  - "三方 CT 编号一致性：DOM-GOV-001 G-CT-001~008 ↔ SYS-MASTER-001 引用的 CT ↔ MOD-MASTER-001 引用的 CT"
  - "dependency_crosscheck.md 逐项标注：[OK] 一致 / [DRIFT] 漂移 / [MISSING] 缺失"
  - "若发现 DRIFT 或 MISSING——报告具体差异，不执行修改"
  - "回滚方案：删除新创建的 2 个文件"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\crosscheck_sys_master_deps.py
  2. 删除 D:\ZephyrAlpha\docs\03_modules\_domain-governance\_domain-governance\changes\DOM-GOV-001\dependency_crosscheck.md

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
