---
task_id: "TASK-INF-0102"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤3 — 重写 core/models.py：TaskCard 继承 Task"

title: "重写 core/models.py — TaskCard 继承 shared/schemas.py Task（62字段）"
description: |
  重写 `D:\ZephyrAlpha\src\zephyr\core\models.py`。
  TaskCard 类从独立 Pydantic BaseModel → 继承 `shared/schemas.py` Task（31字段基座）。
  追加 Vibe Coding 执行层扩展：防漂移六维 + 门禁 + 管线 + v0.4.0-v0.6.0 新增字段。
  最终 TaskCard 共计 62 字段（31 基座 + 31 执行层）。
  实现 TaskNamespace 枚举、GateLevel 枚举、AISelfGovernanceLevel 五级枚举、
  DecompositionResult/GateCheckResult/AuditFinding 模型。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\task-card-template.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    description: "TaskCard(继承Task) + TaskNamespace + GateLevel + AISelfGovernanceLevel + DecompositionResult + GateCheckResult + AuditFinding"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2 BaseModel——禁止 dataclass"
  - module_id: "MOD-INF-006"
    section: "§3.2.1"
    reason: "TaskCard 62字段定义 + 字段源流对照表——SSoT"
  - module_id: "PS-STD-001"
    section: "§7.1-§7.1.1"
    reason: "Task 基座 31 字段（语义28+追踪3）——metadata-registry.md 真源"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.2.1 TaskCard 完整模型定义 Python 代码块——施工依据"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Task 基座类——了解字段名和类型以确保正确继承"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    reason: "现有 v0.2.0 代码——了解需替换的旧结构"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M4"
estimated_tokens: 20000
timeout_minutes: 60

acceptance_criteria:
  - "isinstance(TaskCard(...), Task) == True"
  - "task_id pattern 匹配 '^(ADR|CP|KE|STD|DW|SRC|OPS)-\\\\d+$'"
  - "status ∈ TaskStatus enum（10态 + SUSPENDED）"
  - "防漂移六维字段全部存在：upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions"
  - "v0.4.0 新增11字段全部存在：parent_task_id/epic/retry_count/max_retries/retry_backoff_seconds/checkpoint_path/estimated_context_tokens/context_window_limit/effective_priority/diff_plan_required/circuit_breaker_open/suspend_context_json"
  - "v0.5.0 新增10字段全部存在：prompt_version/prompt_variant/compensation_steps/sla_deadline/sla_escalation_policy/original_priority/model_snapshot_pinned/thinking_state_json/emergency_mode/cross_task_learning/dependency_fingerprint"
  - "v0.6.0 新增8字段全部存在：cancelled_artifacts/upstream_files_content_hash/consumer_impact_report/run_consumer_tests/replan_proposed/modified_files_actual/lines_changed_actual/context_cache_key"
  - "AISelfGovernanceLevel 五级枚举：SUPERVISED/SEMI_AUTONOMOUS/AUTONOMOUS/FULL_AUTO/EMERGENCY_ONLY"
  - "GateLevel 枚举：G0/G7/G1/G2/G3/G4/G5/G6"
  - "TaskNamespace 枚举：ADR/CP/KE/STD/DW/SRC/OPS"
  - "DecompositionResult / GateCheckResult / AuditFinding 模型可用"
  - "Pydantic V2 ConfigDict(extra='allow')"

rollback_instructions: |
  1. 恢复 `D:\ZephyrAlpha\src\zephyr\core\models.py` 为 v0.2.0 独立 TaskCard 模型
  2. 确认 task_id 格式恢复为 TASK-INF-XXXX
  3. 确认标签恢复为五轴 tags_fn/tags_ly/tags_md/tags_st/tags_mo
  4. 如已执行 TASK-INF-0103/0104 依赖重写——同步回退这两个文件

depends_on: ["TASK-INF-0100", "TASK-INF-0101"]
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

# 重写 core/models.py — TaskCard 继承 Task

## 目标

重写 `D:\ZephyrAlpha\src\zephyr\core\models.py`：
1. TaskCard 从独立 BaseModel 改为继承 `shared/schemas.py` Task（31字段基座）
2. 追加防漂移六维 + 门禁 + 管线 + v0.4.0/v0.5.0/v0.6.0 扩展字段 → 共62字段
3. 实现所有枚举类：TaskNamespace / GateLevel / AISelfGovernanceLevel
4. 实现辅助模型：DecompositionResult / GateCheckResult / AuditFinding

## 触发条件

- 蓝图注册表和元注册表已更新（TASK-INF-0100/0101 完成）
- shared/schemas.py Task 类可正常 import

## 执行步骤

### 读
- `shared/schemas.py` Task 类——了解基座字段
- 蓝图 §3.2.1 TaskCard Python 代码块——施工依据
- metadata-registry.md §7——字段定义真源

### 做
1. 清空 `core/models.py` 现有 v0.2.0 代码
2. 按蓝图 §3.2.1 代码块逐字段实现 TaskCard 类（继承 Task）
3. 实现 TaskNamespace / GateLevel / AISelfGovernanceLevel 枚举
4. 实现 DecompositionResult / GateCheckResult / AuditFinding Pydantic 模型
5. 字段分组注释：防漂移六维 / 门禁追踪 / 管线分配 / v0.4.0-v0.6.0 新增

### 产
- `D:\ZephyrAlpha\src\zephyr\core\models.py`

### 检
```python
from zephyr.core.models import TaskCard, TaskNamespace, GateLevel, AISelfGovernanceLevel
from zephyr.shared.schemas import Task
tc = TaskCard(task_id="SRC-001", title="test", ...)
assert isinstance(tc, Task)
assert tc.task_id == "SRC-001"
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | lint | 0 errors, 0 warnings |
| 3 | diff | 仅修改 core/models.py |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| Task 基座字段与蓝图声明不一致 | 以 shared/schemas.py 磁盘代码为准——蓝图可能是旧版本描述 |
| 破坏已有导入 core/models.py 的代码 | 旧 v0.2.0 代码已标记 deprecated——TASK-INF-0103/0104 同步重写 |
