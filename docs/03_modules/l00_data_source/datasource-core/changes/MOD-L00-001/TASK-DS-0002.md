---
task_id: "TASK-DS-0002"
source_blueprint: "MOD-L00-001"
source_section: "蓝图 frontmatter module_id + 正文 §1"

# ===== 内容 =====
title: "在 blueprint-registry.yaml 中注册 MOD-L00-001"
description: |
  datasource-core 模块的 module_id 为 MOD-L00-001，当前未在 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` 中注册。
  需要在注册表中新增条目，登记模块的 module_id、路径、status、layer 等元信息，
  使全项目蓝图索引工具（validate_blueprint_provenance.py / generate_rule_catalog.py）能发现此模块。
  注册格式需对齐 blueprint-registry.yaml 现有条目的字段结构。
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    description: "新增 MOD-L00-001 条目——登记模块元信息"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\index.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "module_id 格式——MOD-L00-001 的 DOMAIN 为 L00 业务层的 MOD 域"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——blueprint-registry.yaml 位置验证"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
    reason: "本蓝图——提取 module_id / title / status / version / layer 用于注册"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    reason: "蓝图注册表——了解现有条目格式，新增 MOD-L00-001 条目"

# ===== 执行 =====
assigned_model: "any"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 4000
timeout_minutes: 10

# ===== 验收标准 =====
acceptance_criteria:
  - "blueprint-registry.yaml 中存在 module_id: MOD-L00-001 的条目"
  - "条目包含字段：module_id、path（指向 datasource-core/blueprint.md）、status、layer、title"
  - "path 字段值为 D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
  - "status 对齐蓝图 frontmatter（draft）"
  - "layer 对齐蓝图 frontmatter（l00_data_source）"
  - "新条目格式与 blueprint-registry.yaml 现有条目一致"
  - "YAML 语法合法（python -c \"import yaml; yaml.safe_load(open(...))\" 通过）"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml 中 MOD-L00-001 条目
  2. 恢复文件原有 YAML 结构——确保删除后 registry 中不再有 MOD-L00-001

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

# TASK-DS-0002：在 blueprint-registry.yaml 中注册 MOD-L00-001

## 目标

在项目蓝图注册表 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` 中新增 MOD-L00-001 条目，使全项目蓝图索引工具可发现 datasource-core 模块。

## 触发条件

- TASK-DS-0001（frontmatter 合规修复）已通过——注册表条目需引用修正后的 frontmatter 值

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\l00_data_source\datasource-core\blueprint.md`（本蓝图——提取 module_id / title / status / version / layer）
- `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`（了解现有条目格式）

### 做
1. 读取 blueprint.md 的 frontmatter，提取：module_id、title、status、version、layer、date
2. 读取 blueprint-registry.yaml 现有条目格式
3. 按现有格式新增 MOD-L00-001 条目：
   ```yaml
   - module_id: "MOD-L00-001"
     title: "数据接入层蓝图（C 轨占位 — 禁止施工）"
     path: "D:\\ZephyrAlpha\\docs\\03_modules\\l00_data_source\\datasource-core\\blueprint.md"
     status: "draft"
     layer: "l00_data_source"
     version: "0.1.0"
     date: "2026-05-05"
   ```
4. 追加条目到 blueprint-registry.yaml 的蓝图清单列表末尾

### 产
- `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`（新增 MOD-L00-001 条目）

### 检
```bash
python -c "import yaml; d = yaml.safe_load(open('D:/ZephyrAlpha/docs/03_modules/blueprint-registry.yaml', encoding='utf-8')); print('OK' if any(e.get('module_id') == 'MOD-L00-001' for e in d.get('blueprints', d)) else 'MISSING')"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | 条目存在 | `module_id: "MOD-L00-001"` 在 registry 中 |
| 2 | 路径正确 | `path` 指向 l00_data_source/datasource-core/blueprint.md |
| 3 | 状态一致 | `status` 与蓝图 frontmatter 一致 |
| 4 | 层级一致 | `layer` 与蓝图 frontmatter 一致 |
| 5 | YAML 合法 | `yaml.safe_load()` 通过 |
| 6 | 格式一致 | 条目字段结构与 registry 现有条目一致 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| blueprint-registry.yaml 字段结构与预期不同 | 先读取现有条目格式再新增——不对现有条目做任何修改 |
| MOD-L00-001 已在 registry 中存在（重复） | 先搜索现有条目——如已存在则更新而非新增 |
