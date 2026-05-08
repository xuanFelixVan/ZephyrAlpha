---
task_id: "TASK-INF-0106"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §3.1.2 TaskLifecycleManager + §3.2.1 GateLevel 枚举 + §4.1 约束 #1/#2/#3/#4/#5"

title: "实现 G0-G7 全生命周期门禁系统"
description: |
  实现 TaskLifecycleManager 类——封装完整状态机（10态 + SUSPENDED）。
  实现 G0 创建门禁（task_id 格式 / 所有全字段值非空 / upstream_files 路径存在 /
  rollback_instructions 非空 / forbidden_touch 非空 + MANDATORY-ZR 命名规范合法）。
  实现 G7 输出校验门禁（downstream_outputs 路径完整 / READ-ONLY 路径禁止写入 /
  context_assembly_manifest 索引正确）。
  实现 G1-G6 中间门禁的逻辑与状态转换时的回调触发。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-card-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-closure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
    description: "TaskLifecycleManager——状态机 + G0-G7 门禁回调 + GateCheckResult"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§3.1.2"
    reason: "TaskLifecycleManager API 契约——transition() 签名 + 回调机制"
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #1-#5"
    reason: "G0 创建门禁 + G7 输出校验门禁具体规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.1.2 TaskLifecycleManager 代码块 + G0/G7 门禁定义 + 约束 #1-#5"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M9"
estimated_tokens: 20000
timeout_minutes: 60

acceptance_criteria:
  - "G0 校验失败 → create_task 被拒绝并返回 GATE_BLOCKED(422)"
  - "G7 校验失败 → transition() 到 completed 被拒绝"
  - "门禁回调在状态转换前触发（pre_hook）"
  - "GateCheckResult 含 passed: bool + checks: dict + failures: list[dict]"
  - "TaskStatus 枚举完整——TODO/IN_PROGRESS/REVIEW/BLOCKED/COMPLETED/CANCELLED/DEFERRED/TRIAGE/PLANNED + SUSPENDED"
  - "transition() 使用 TaskStatus 枚举而非裸字符串"

rollback_instructions: |
  1. 恢复 `task_lifecycle_manager.py` 为 v0.2.0 版——无 G0/G7 门禁的简单状态机
  2. 确认旧版 create_task / transition 不受影响

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "gate"
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

# 实现 G0-G7 全生命周期门禁系统

## 目标

实现任务卡的全生命周期门禁：
- **G0 创建门禁**：task_id 格式 / 必填字段检查 / upstream_files 路径存在 / rollback_instructions 非空 / forbidden_touch 非空 + 命名规范
- **G1 就绪门禁**：依赖项健康 / 冲突检测
- **G2 开始门禁**：上下文准备 / 前置校验
- **G3 审阅门禁**：diff 完整性 / consumer tests
- **G4 完成门禁**：全量审计 / 关闭报告
- **G5 取消门禁**：取消安全协议
- **G6 归档门禁**：版本固化
- **G7 输出校验**：downstream_outputs 完整 / READ-ONLY 禁止写入 / context_assembly_manifest 正确

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）

## 执行步骤

### 读
- core/models.py TaskCard 模型
- task-lifecycle-standard.md 状态机规范
- task-card-standard.md 门禁要求
- task-closure-standard.md 关闭流程

### 做
1. 实现 TaskLifecycleManager：
   - `transition(task, target_status)` → 执行门禁 → 更新状态
   - 注册门禁回调到 transition() 的 pre_hook 域
   - GateCheckResult 返回
2. 实现各门禁函数：
   - `gate_g0_create(task)` / `gate_g7_output(task)` / `gate_g1_ready(task)` 等
   - G0 检查：task_id 正则 / upstream_files 存在 / rollback_instructions 非空
   - G7 检查：downstream_outputs 路径完整 / 无 READ-ONLY 写入

### 产
- `task_lifecycle_manager.py`

### 检
```python
mgr = TaskLifecycleManager()
result = mgr.transition(task, TaskStatus.IN_PROGRESS)
assert isinstance(result, GateCheckResult)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | lint | 0 errors |
| 3 | diff | 仅修改 lifecycle/ 目录 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 门禁检查 I/O 过多影响性能 | 路径存在性检查做批量缓存——一次检查后短时间复用 |
| G0 过于严格阻止合法创建 | 区分 ERROR（硬阻止）vs WARNING（软通过） |
