---
task_id: "TASK-INF-0107"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #11/#12/#18/#19/#30 + 盲点 #5/#6/#7/#8/#39"

title: "实现依赖管理——拓扑排序 + 循环检测 + 优先级传播 + WIP/并发冲突 + 依赖新鲜度"
description: |
  实现依赖拓扑排序输出——按 DAG 拓扑序输出任务卡。
  循环依赖检测——存在循环时拒绝拆解（约束 #18）。
  优先级传播——blocker 升级时检查 consumer 预警（约束 #12）。
  WIP 并行限制——max_parallel 控制批量并发上限（约束 #11）。
  并发冲突检测——任务开启前检查 upstream_files 是否有冲突任务在工作（约束 #19）。
  依赖新鲜度验证——首次执行前验证 depends_on 已完成且未过期（约束 #30）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\dependency\\dependency_graph.py"
    description: "DependencyGraph——拓扑排序 + 循环检测 + 优先级传播 + 并发冲突 + 新鲜度"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\dependency\\dependency_graph.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #11/#12/#18/#19/#30"
    reason: "依赖管理所有约束——SSoT"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #11/#12/#18/#19/#30 详细规则"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M4"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "拓扑排序输出为合法 DAG 拓扑序"
  - "存在循环依赖时抛出 CyclicDependencyError"
  - "优先级传播——blocker 升级时 consumer 收到预警信号"
  - "WIP 限制——并行执行的任务数 ≤ max_parallel"
  - "并发冲突——任务字段与另一进行中任务重叠时标记 CONFLICT"
  - "依赖新鲜度——约定期限过期时任务状态降级为 STALE_UPSTREAM"

rollback_instructions: |
  1. 移除 dependency_graph.py
  2. 回退 blueprint_decomposer.py 中的依赖解析调用

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

ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---

# 实现依赖管理——拓扑排序 + 循环检测 + 优先级传播 + WIP/并发冲突 + 依赖新鲜度

## 目标

实现完整的任务卡依赖管理系统：
1. 拓扑排序输出 + 循环依赖检测（约束 #18）
2. 优先级传播——blocker 升级 → consumer 预警（约束 #12）
3. WIP 并行限制——max_parallel 控制（约束 #11）
4. 并发冲突检测——upstream_files 共享冲突（约束 #19）
5. 依赖新鲜度验证（约束 #30）

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）
- task_repo 可用

## 执行步骤

### 读
- core/models.py 依赖相关字段
- task_repo API

### 做
1. 实现 DependencyGraph 类
2. 实现 `topological_sort(tasks)` → 返回拓扑序 + 循环检测
3. 实现 `propagate_priority(task)` → blocker 升级时通知 consumer
4. 实现 `check_concurrency(tasks)` → allowed_touch 交集检测
5. 实现 `validate_freshness(task)` → 依赖新鲜度检查

### 产
- `dependency_graph.py`

### 检
```python
graph = DependencyGraph(tasks)
order = graph.topological_sort()
assert len(order) == len(tasks)
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 循环检测 / 优先级传播 / 并发检测 / 新鲜度 均有测试覆盖 |
| 3 | lint | 0 errors |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 复杂依赖链拓扑排序性能 | 使用 Kahn 算法——O(V+E)，≤ 200 节点时性能足够 |
| 并发冲突误报 | allowed_touch 交集检测 + forbidden_touch 互补——降低误报 |
