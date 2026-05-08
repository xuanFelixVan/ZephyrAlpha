---
task_id: "TASK-INF-0101"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤2 — 同步 task-card-meta-registry.yaml"

title: "同步 task-card-meta-registry.yaml — 记录 MOD-INF-006 v0.2.0→v0.6.0 迁移追踪"
description: |
  更新任务卡元注册表 `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml`。
  记录 MOD-INF-006 从 v0.2.0→v0.6.0 的迁移历程：TaskCard 基座从独立 BaseModel → 继承 shared/schemas.py Task，
  task_id 格式升级，状态机/标签/门禁/约束全部升级。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\task-card-meta-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\task-card-meta-registry.yaml"
    description: "MOD-INF-006 迁移追踪条目更新——记录 v0.2.0→v0.6.0 完整迁移路径"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\task-card-meta-registry.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§7"
    reason: "TaskCard 字段定义真源——迁移追踪需引用字段版本变化"
  - module_id: "MOD-INF-006"
    section: "§3.2.1"
    reason: "TaskCard 模型各版本字段增量——v0.3.2+14/v0.4.0+11/v0.5.0+10/v0.6.0+8"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.2.1 字段源流对照表 + 变更记录——迁移追踪的数据源"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\task-card-meta-registry.yaml"
    reason: "当前迁移状态——V-13，需更新至反映 v0.6.0"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 10

acceptance_criteria:
  - "task-card-meta-registry.yaml 中 MOD-INF-006 条目含 v0.2.0→v0.6.0 完整迁移链"
  - "迁移描述注明 TaskCard 基座从独立 BaseModel → 继承 Task 的核心变更"
  - "YAML 格式合法——不含制表符"
  - "字段版本增量准确：+14(v0.3.2) / +11(v0.4.0) / +10(v0.5.0) / +8(v0.6.0)"

rollback_instructions: |
  1. 使用 git 回退 `task-card-meta-registry.yaml` 到修改前版本
  2. 如无 git 备份——手动将 MOD-INF-006 迁移条目恢复为 V-13 状态
  3. 确认无 v0.6.0 迁移记录残留

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

# 同步 task-card-meta-registry.yaml — 迁移追踪

## 目标

在 `task-card-meta-registry.yaml` 中记录 MOD-INF-006 从 v0.2.0 到 v0.6.0 的四阶段迁移历程：
- v0.3.0：TaskCard 基座切换 ——独立 BaseModel → 继承 shared/schemas.py Task
- v0.4.0：盲点审计与设计补全 ——11 个新增字段 + 五级 AI 自治枚举
- v0.5.0：质量管理与深度可靠性 ——10 个新增字段（Prompt/Saga/质量退化/SLA/等）
- v0.6.0：运行时演化与持久化 ——8 个新增字段（Schema迁移/取消安全/前置漂移/等）

## 触发条件

- MOD-INF-006 v0.6.0 蓝图已定稿
- 蓝图注册表已先行更新（TASK-INF-0100 完成）

## 执行步骤

### 读
- `task-card-meta-registry.yaml` — 当前迁移追踪状态
- 蓝图 §3.2.1 字段源流对照表

### 做
1. 打开 `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml`
2. 定位 MOD-INF-006 迁移条目（当前 V-13）
3. 将迁移版本记录更新为覆盖 v0.2.0→v0.6.0 全路径
4. 添加迁移重点说明：基座切换 / 字段版本增量 / 破坏性变更
5. YAML 语法校验

### 产
- `task-card-meta-registry.yaml`（已更新）

### 检
```bash
python -c "import yaml; yaml.safe_load(open('D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.yaml',encoding='utf-8'))"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | files | task-card-meta-registry.yaml 更新成功 |
| 2 | build | YAML 合法 |
| 3 | diff | 仅修改 MOD-INF-006 迁移条目 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 元注册表结构与预期不符 | 先读取现有 YAML 结构——按现有格式追加而非覆盖 |
| 字段增量计数与蓝图不一致 | 对照蓝图 §3.2.1 源流对照表逐版验证 |
