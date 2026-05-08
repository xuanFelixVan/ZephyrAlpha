---
task_id: "TASK-DS-0003"
source_blueprint: "MOD-L00-001"
source_section: "蓝图正文（全篇结构） + §1 概述"

# ===== 内容 =====
title: "搭建 datasource-core 模块骨架——changes/ 目录结构与蓝图占位"
description: |
  datasource-core 蓝图（MOD-L00-001）正文仅 §1 概述一节（1 段占位描述），
  整体为 C 轨占位蓝图——`ai_read_only_hint: DO_NOT_IMPLEMENT`。
  当前 changes/ 目录已创建（MOD-L00-001/），本任务卡负责：
  1. 确认模块骨架 directories 齐全（changes/MOD-L00-001/ + delivery/）
  2. 验证 index.md 中模块目录索引与磁盘一致
  3. 在 `ai_read_only_hint: DO_NOT_IMPLEMENT` 约束下记录模块当前状态——为后续施工 Phase 就绪时快速开工做准备
priority: "P3"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\index.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\delivery\\index.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0001.md"
    description: "TASK-DS-0001（frontmatter 修复）——已存在，验证即可"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0002.md"
    description: "TASK-DS-0002（registry 注册）——已存在，验证即可"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0003.md"
    description: "本任务卡"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0004.md"
    description: "TASK-DS-0004（未来扩展计划）——已存在，验证即可"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0005.md"
    description: "TASK-DS-0005（架构模型链接验证）——已存在，验证即可"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\*.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\delivery\\**\\*.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.3"
    reason: "03_modules/ 准入规则——模块子目录结构必须含 blueprint.md + delivery/ + changes/"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建——产出物路径必须符合目录结构标准"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
    reason: "本蓝图——了解模块骨架定义"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——验证模块子目录结构合规性"

# ===== 执行 =====
assigned_model: "any"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 3000
timeout_minutes: 10

# ===== 验收标准 =====
acceptance_criteria:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\ 目录物理存在"
  - "changes/MOD-L00-001/ 下存在 5 张任务卡 .md 文件（TASK-DS-0001 至 TASK-DS-0005）"
  - "delivery/ 目录物理存在（交付记录占位）"
  - "所有 .md 文件编码 UTF-8 无 BOM + LF 换行"
  - "模块目录结构符合 GOV-DOC-002 §5.3：blueprint.md + delivery/ + changes/"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\changes\MOD-L00-001\ 目录
  2. 恢复 changes/ 目录至空（如 changes/ 为空则删除）
  3. 不影响 blueprint.md / delivery/ / index.md

# ===== 依赖 =====
depends_on: []
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "data"
tags_ly: "l00_data_source"
tags_md: "any"
tags_st: "active"
tags_mo:
  - "MOD-L00-001"

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

# TASK-DS-0003：搭建 datasource-core 模块骨架

## 目标

确认 datasource-core 模块（MOD-L00-001）的目录骨架完整：`blueprint.md` + `delivery/` + `changes/MOD-L00-001/`，为模块后续施工提供标准化的文件存放基础设施。

## 触发条件

- 无前置依赖——changes/ 目录已创建，本任务为验证性审计

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`（了解 `ai_read_only_hint: DO_NOT_IMPLEMENT` 约束）
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\index.md`（模块目录索引）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md`（目录结构标准）

### 做
1. 遍历 `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\` 下所有文件和子目录
2. 核验目录结构：blueprint.md ✓ + delivery/ ✓ + changes/MOD-L00-001/ ✓
3. 核验 5 张任务卡全部物理存在
4. 编码检查：所有 .md 文件 UTF-8 无 BOM + LF 换行

### 产
- 模块骨架完整性验证记录（写入本任务卡 execution_log）

### 检
```bash
python scripts/governance/check_frontmatter_metadata.py --dir "D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\changes\MOD-L00-001"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | changes 目录 | MOD-L00-001/ 子目录存在 |
| 2 | 任务卡完整性 | 5 张 .md 任务卡全部存在 |
| 3 | delivery 目录 | delivery/ 物理存在 |
| 4 | 编码合规 | 所有文件 UTF-8 无 BOM + LF |
| 5 | 结构合规 | 符合 GOV-DOC-002 §5.3 模块子目录结构 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 模块骨架被视为"已就绪可施工"而误触发业务代码生成 | 蓝图 frontmatter 的 `ai_read_only_hint: DO_NOT_IMPLEMENT` 是第一道防线——任何 AI 施工前 MUST 读取 blueprint.md |
