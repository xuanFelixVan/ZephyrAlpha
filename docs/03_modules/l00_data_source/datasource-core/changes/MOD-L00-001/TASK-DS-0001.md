---
task_id: "TASK-DS-0001"
source_blueprint: "MOD-L00-001"
source_section: "蓝图 frontmatter（全量字段）"

# ===== 内容 =====
title: "修复 datasource-core 蓝图 frontmatter 违规字段"
description: |
  datasource-core 蓝图（MOD-L00-001）的 frontmatter 存在 3 个违反 metadata-registry.md（PS-STD-001）的字段值：
  1. `ttl: evolving` — `evolving` 不是合法 ttl 值（合法：permanent / 30d / 7d / session / periodic_review_90d），应为 `periodic_review_90d`（占位蓝图需定期审查）
  2. `layer: L00` — 应为全小写蛇形 `l00_data_source`（PS-STD-001 §5.5 格式：`l{xx}_{snake_case}`）
  3. `status: Draft` — 应为全小写 `draft`（PS-STD-001 §4.1 DocStatus 枚举值全小写）
  同步修正后确保 pre-commit GATE-15 不再告警。
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\vocabularies\\ttl-vocabulary.yaml"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
    description: "修正 frontmatter 的 ttl/layer/status 字段值"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\delivery\\**\\*.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\index.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\*.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§4.1"
    reason: "DocStatus 枚举值全小写——status 必须为 draft（非 Draft）"
  - module_id: "PS-STD-001"
    section: "§5.5"
    reason: "layer 字段格式——l{xx}_{snake_case}，L00 数据源层应为 l00_data_source"
  - module_id: "PS-STD-001"
    section: "§6"
    reason: "ttl 受控词表——evolving 不是合法值，合法值为 permanent / 30d / 7d / session / periodic_review_90d"
  - module_id: "PS-STD-001"
    section: "§4.5"
    reason: "枚举值全小写——frontmatter 枚举值必须全小写"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
    reason: "本蓝图——需修改的源文件"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "元数据注册表——§4.1 状态枚举、§5.5 layer格式、§6 ttl词表——字段合法值的唯一真源"

# ===== 执行 =====
assigned_model: "any"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 3000
timeout_minutes: 10

# ===== 验收标准 =====
acceptance_criteria:
  - "blueprint.md frontmatter 中 ttl 值变为 periodic_review_90d（合法 ttl 值之一）"
  - "blueprint.md frontmatter 中 layer 值变为 l00_data_source（全小写蛇形）"
  - "blueprint.md frontmatter 中 status 值变为 draft（全小写）"
  - "pre-commit GATE-15 不再报告 MOD-L00-001 的 frontmatter 违规"
  - "正文内容不受影响——仅修改 frontmatter 的 3 个字段值"
  - "文件编码保持 UTF-8 无 BOM + LF 换行"

# ===== 回滚 =====
rollback_instructions: |
  1. 还原 D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md 中 frontmatter 的 3 个字段：
     - ttl: 改回 evolving
     - layer: 改回 L00
     - status: 改回 Draft
  2. 确认文件编码仍为 UTF-8 无 BOM + LF 换行

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

# TASK-DS-0001：修复 datasource-core 蓝图 frontmatter 违规字段

## 目标

修正 MOD-L00-001 蓝图 frontmatter 中 3 个违反 metadata-registry.md（PS-STD-001）的字段值，使蓝图通过 pre-commit GATE-15 frontmatter 合规校验。

## 触发条件

- 无前置依赖

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`（本蓝图——需修改的源文件）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md`（字段合法值真源）

### 做
1. 打开 `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`
2. 修改 frontmatter 中以下 3 行：
   - 第 5 行：`status: Draft` → `status: draft`
   - 第 7 行：`layer: L00` → `layer: l00_data_source`
   - 第 14 行：`ttl: evolving` → `ttl: periodic_review_90d`
3. 不在 frontmatter 中添加或删除任何其他字段
4. 不在正文中做任何修改

### 产
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`（frontmatter 已修正）

### 检
```bash
python scripts/governance/check_frontmatter_metadata.py --file "D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | ttl 合规 | `ttl: periodic_review_90d`（合法 ttl 值之一） |
| 2 | layer 合规 | `layer: l00_data_source`（全小写蛇形） |
| 3 | status 合规 | `status: draft`（全小写） |
| 4 | pre-commit 通过 | GATE-15 不再报告 MOD-L00-001 违规 |
| 5 | 内容不变 | 正文零修改 |
| 6 | 编码合规 | UTF-8 无 BOM + LF 换行 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| ttl 值语义变更导致蓝图被自动清理 | `periodic_review_90d` 仅在审查时提醒，不会自动删除——这是对占位蓝图最安全的 ttl 选择 |
| 其他校验器依赖 `layer: L00` 大写格式 | 全项目 layer 字段标准已是全小写蛇形（l00_data_source）——此为对齐而非引入新格式 |
