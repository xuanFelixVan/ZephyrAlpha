---
task_id: "TASK-INF-0103"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤4 — 重写 blueprint_decomposer.py"

title: "重写 BlueprintDecomposer — 对接 task_repo（SQLite）+ 拓扑排序 + .md 同步"
description: |
  重写 `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py`。
  decompose() 从以 .md 为主 → 以 `task_repo.create(task)` 为主（写 SQLite 真源），.md 同步生成为辅。
  task_id 从 `TASK-INF-0001` 自增 → `{NAMESPACE}-{SEQ}` 格式（按蓝图域+查询 task_repo 最大 seq）。
  实现拓扑排序 + 循环依赖检测（约束 #18）。
  每张任务卡执行 G0/G7 门禁校验。
  task_repo.create() 成功后同步生成 .md 副本到 changes/ 目录。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\task-card-template.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
    description: "BlueprintDecomposer 类——decompose() 对接 task_repo + 拓扑排序 + .md 同步"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§3.1.1"
    reason: "BlueprintDecomposer API 契约 + decompose() 算法——SSoT"
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #18"
    reason: "依赖拓扑排序——必须输出拓扑序，检测循环依赖时拒绝拆解"
  - module_id: "PS-STD-001"
    section: "§7.10"
    reason: "task_id 格式 {NAMESPACE}-{SEQ}——NAMESPACE 枚举值"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.1.1 BlueprintDecomposer Python 代码块 + §3.3 输入契约 + §3.4 输出契约"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
    reason: "task_repo.create()/list_tasks() 接口——数据层真源"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    reason: "TaskCard/DecompositionResult 模型——类型正确性"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M4"
estimated_tokens: 25000
timeout_minutes: 75

acceptance_criteria:
  - "decompose(本蓝图) → task_repo.list_tasks() 返回 N≥1 条记录"
  - "每条记录 task_id 格式匹配 '^(ADR|CP|KE|STD|DW|SRC|OPS)-\\\\d+$'"
  - "changes/MOD-INF-006/ 目录下生成对应 .md 副本"
  - "拓扑排序输出——dependencies 无循环"
  - "unassigned_items ≤ 10%"
  - "G7 门禁通过——每张任务卡 downstream_outputs 路径完整+rollback_instructions 非空"
  - "task_repo.create() 总是成功——SQLite integrity 检查通过"

rollback_instructions: |
  1. 恢复 `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` 为旧版 .md 为主的拆解器
  2. 删除 task_repo 中由新版 decomposer 创建的任务记录（如有）
  3. 删除 changes/MOD-INF-006/ 目录下的新版 .md 副本（如有）

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
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

# 重写 BlueprintDecomposer — 对接 task_repo + 拓扑排序

## 目标

重写蓝图拆解器核心逻辑：
1. decompose() 主输出：task_repo.create(task) → SQLite 真源
2. task_id 生成：解析蓝图域 → NAMESPACE → 查询 task_repo 最大 seq → {NAMESPACE}-{seq+1}
3. 拓扑排序：解析 depends_on → 构建 DAG → 检测循环 → 拒绝有循环的拆解
4. G0/G7 门禁：每张任务卡创建前做完整性校验
5. .md 同步：task_repo.create() 成功后 → 同步生成 .md 副本

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）
- task_repo.py 可用——create() / list_tasks() / get() 正常

## 执行步骤

### 读
- task_repo.py 完整 API——create/get/update/upsert/list 参数和返回值
- 蓝图 §3.1.1 decompose() 算法描述
- core/models.py TaskCard/DecompositionResult 模型

### 做
1. 解析 blueprint_path 的 §11 施工指引 → 提取步骤列表
2. 每个步骤 → 确定 NAMESPACE → 生成 task_id
3. 解析 depends_on 关系 → 构建邻接表 → 拓扑排序
4. 检测循环依赖 → 存在时 raise CyclicDependencyError
5. 按 GOV-AI-002 决策树分配 execution_model
6. 逐张任务卡 → G0/G7 门禁 → task_repo.create() → .md 同步

### 产
- `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py`

### 检
```python
decomposer = BlueprintDecomposer(repo)
result = decomposer.decompose("D:/ZephyrAlpha/docs/03_modules/l01_infrastructure/task-system/blueprint.md", "D:/ZephyrAlpha/docs/03_modules/l01_infrastructure/task-system/changes/MOD-INF-006")
assert result.total_tasks >= 1
assert all(re.match(r'^(ADR|CP|KE|STD|DW|SRC|OPS)-\d+$', t.task_id) for t in result.tasks)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误，decompose() 可执行 |
| 2 | files | SQLite 写入 + .md 副本生成 |
| 3 | diff | 仅修改 blueprint_decomposer.py |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 蓝图 §11 格式变化 → 正则解析失败 | 解析前先验证 §11 最低结构要求，不满足时明确报错 |
| task_repo 不可用 | 构造时 Dependency Injection——decompose() 接受 repo 参数 |
