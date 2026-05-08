---
task_id: "TASK-INF-0100"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤1 — 善后：注册表 + 元数据同步"

title: "更新 blueprint-registry.yaml — MOD-INF-006 条目升级至 v0.6.0"
description: |
  更新蓝图注册表 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`。
  将 MOD-INF-006 条目的 version 从当前值更新为 0.6.0，blueprint_status 设为 approved，
  change_log 追加 v0.4.0 → v0.5.0 → v0.6.0 三级变更条目。
  同时执行安全删除协议检查——确认 MOD-INF-003/MOD-INF-004 已标记 deprecated 或物理删除。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    description: "MOD-INF-006 条目 version→0.6.0，status→approved，change_log 追加变更条目"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——产出物路径必须与路径映射一致"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建——不得自主决定目录层级"
  - module_id: "MOD-INF-006"
    section: "§4.3"
    reason: "迁移/废弃方案——确认已废弃蓝图的安全删除"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "本蓝图——§4.3 迁移方案 + §11.3 步骤1 + 安全删除协议"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    reason: "当前注册表——了解 MOD-INF-006 条目现有内容"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 15

acceptance_criteria:
  - "blueprint-registry.yaml 中 MOD-INF-006.version == '0.6.0'"
  - "blueprint-registry.yaml 中 MOD-INF-006.blueprint_status == 'approved'"
  - "change_log 含 v0.4.0 + v0.5.0 + v0.6.0 三级变更条目摘要"
  - "MOD-INF-003 条目保持 deprecated 标记或已移除"
  - "MOD-INF-004 条目保持 deprecated 标记或已移除"
  - "YAML 格式合法——`python -c 'import yaml; yaml.safe_load(open(...))'` 通过"

rollback_instructions: |
  1. 使用 git 回退 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` 到修改前版本
  2. 如无 git 备份——手动将 version 字段恢复为修改前的值
  3. 确认 change_log 中无 v0.6.0 条目

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 更新蓝图注册表 — MOD-INF-006 v0.6.0

## 目标

将 MOD-INF-006（任务系统蓝图）在蓝图注册表中的条目更新至 v0.6.0：
- version: 0.6.0
- blueprint_status: approved
- change_log 追加 v0.4.0 → v0.5.0 → v0.6.0 三级变更摘要

## 触发条件

- 本蓝图 MOD-INF-006 v0.6.0 已完成所有章节编写（§1-§13 + 治理信息）
- 必备链接中所有 14 项真源文件在磁盘存在

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` — 当前注册表内容
- `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` — 本蓝图 §11.3 步骤1 + §4.3 迁移方案

### 做
1. 打开 `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`
2. 定位 MOD-INF-006 条目
3. 将 `version` 字段更新为 `"0.6.0"`
4. 将 `blueprint_status` 更新为 `"approved"`
5. 在 `change_log` 中追加三条记录：
   - 2026-05-06 / 0.6.0 / 第三轮深度盲点审计——41→48盲点八大类（新增大类H+七个扩充分类）
   - 2026-05-05 / 0.4.0 / 全量盲点审计——30盲点六大类 + v0.4.0已解决14项
   - 2026-05-03 / 0.3.1 / 路径修正 + 蓝图-代码同步
6. 确认 MOD-INF-003 和 MOD-INF-004 条目标记为 deprecated
7. YAML 语法校验

### 产
- `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml`（已更新）

### 检
```bash
python -c "import yaml; data=yaml.safe_load(open('D:/ZephyrAlpha/docs/03_modules/blueprint-registry.yaml',encoding='utf-8')); [print(m['module_id'], m['version']) for m in data['modules'] if m['module_id']=='MOD-INF-006']"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | files | blueprint-registry.yaml 更新成功 |
| 2 | build | YAML 合法——yaml.safe_load 通过 |
| 3 | diff | 仅修改 MOD-INF-006 条目内容 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| MOD-INF-006 条目不存在于注册表 | 创建新条目——按 blueprint-registry.yaml 模板格式补录 |
| YAML 格式写入错误 | 修改前备份原文件——写入后立即 yaml.safe_load 校验 |
