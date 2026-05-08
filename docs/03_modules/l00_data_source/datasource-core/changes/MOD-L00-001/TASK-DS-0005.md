---
task_id: "TASK-DS-0005"
source_blueprint: "MOD-L00-001"
source_section: "蓝图正文——L00 层架构模型引用"

# ===== 内容 =====
title: "验证 datasource-core 与 L00 架构模型 YAML 的一致性"
description: |
  datasource-core 蓝图正文声明："子模块与契约以 `docs/02_enterprise_architecture/target-architecture/architecture-model/layers/l00-data-source.yaml` 为真源。
  本文件仅保证登记表 `path` 与磁盘一致。"
  本任务卡验证：
  1. l00-data-source.yaml 文件在磁盘上存在
  2. YAML 内容合法可解析
  3. YAML 中声明的 datasource-core 子模块与磁盘蓝图文件路径一致
  4. 蓝图 frontmatter 中 module_id（MOD-L00-001）与 YAML 中对应条目一致
  此验证确保"蓝图→架构模型 YAML→磁盘路径"三向一致性——避免蓝图占位与架构模型脱节。
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\layers\\l00-data-source.yaml"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0005.md"
    description: "本任务卡——验证执行记录写在 execution_log 中"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\changes\\MOD-L00-001\\TASK-DS-0005.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\**\\*.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\index.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§1.4"
    reason: "SSoT 声明——架构模型 YAML 是子模块与契约的真源——MD 文件不得与其冲突"
  - module_id: "GOV-DOC-002"
    section: "§5.2"
    reason: "02_enterprise_architecture/ 准入规则——架构模型 YAML 的正确存放位置"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
    reason: "本蓝图——提取声明引用 l00-data-source.yaml 的段落"
  - file_path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\layers\\l00-data-source.yaml"
    reason: "L00 层架构模型真源——验证子模块清单与蓝图路径一致"

# ===== 执行 =====
assigned_model: "any"
assigned_pipeline: "B"
pipeline_modules:
  - "M6"
estimated_tokens: 4000
timeout_minutes: 10

# ===== 验收标准 =====
acceptance_criteria:
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\layers\\l00-data-source.yaml 磁盘存在"
  - "YAML 文件可用 yaml.safe_load() 成功解析——语法合法"
  - "YAML 中 datasource-core 的 module_id 字段值为 MOD-L00-001（与蓝图 frontmatter 一致）"
  - "YAML 中 datasource-core 的 path 字段指向 D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "如 YAML 中无 MOD-L00-001 条目——输出 FINDING（需在 YAML 中新增子模块条目）"
  - "如 YAML 中 path 与磁盘不一致——输出 FINDING（需修正 YAML 中的 path）"

# ===== 回滚 =====
rollback_instructions: |
  本任务为只读验证——不修改任何文件。如发现不一致，记录到 TASK-DS-0005.md 正文中作为审计发现，
  创建 TASK-DS-0006 修复任务卡。无操作需要回滚。

# ===== 依赖 =====
depends_on:
  - "TASK-DS-0001"
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

# TASK-DS-0005：验证 datasource-core 与 L00 架构模型 YAML 的一致性

## 目标

验证 datasource-core 蓝图（MOD-L00-001）正文中声明的架构模型真源引用——`l00-data-source.yaml`——与磁盘实际文件一致，确保蓝图-架构模型 YAML-磁盘路径三向对齐。

## 触发条件

- TASK-DS-0001（frontmatter 合规修复）已通过——使用修正后的 module_id/layer 做交叉验证

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`（提取 YAML 引用声明）
- `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\layers\l00-data-source.yaml`（架构模型真源）

### 做
1. 读取 l00-data-source.yaml——验证文件存在且 YAML 合法
2. 在 YAML 内容中搜索 datasource-core 或 MOD-L00-001 相关条目
3. 交叉验证：
   - YAML 条目中的 module_id = MOD-L00-001
   - YAML 条目中的 path 指向 datasource-core/blueprint.md
4. 如条目缺失或字段不一致——记录 FINDING 到本任务卡

### 产
- 本任务卡（execution_log 中记录验证结果）

### 检
```bash
python -c "import yaml; d = yaml.safe_load(open('D:/ZephyrAlpha/docs/02_enterprise_architecture/target-architecture/architecture-model/layers/l00-data-source.yaml', encoding='utf-8')); print('OK - YAML valid')"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | YAML 存在 | l00-data-source.yaml 磁盘存在 |
| 2 | YAML 合法 | yaml.safe_load() 通过 |
| 3 | module_id 一致 | YAML 中 MOD-L00-001 条目 module_id = MOD-L00-001 |
| 4 | path 一致 | YAML 中 path 指向 datasource-core/blueprint.md |
| 5 | 交叉审计 | 蓝图→YAML→磁盘三向无矛盾 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| l00-data-source.yaml 不存在 | 输出 FINDING——YAML 缺失，创建独立任务卡生成该 YAML（不在本任务范围内生成） |
| YAML 存在但无 MOD-L00-001 条目 | 输出 FINDING——条目缺失，创建独立任务卡补充条目 |
