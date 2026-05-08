---
task_id: "TASK-INF-0108"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #13/#14/#15/#16/#17 + 盲点 #10/#11/#14/#15"

title: "实现 AI 执行可靠性——断路器 + Retry + 幂等 + diff-plan + 上下文保护 + 前置漂移 + 范围蔓延"
description: |
  实现断路器——按 task 纬度连续失败 N 次后跳闸（约束 #13）。
  Retry 与幂等——retry_count/retry_backoff_seconds（约束 #14）。
  diff-plan 模式——仅修改代码块而不重写文件（约束 #15）。
  上下文保护——文件内容写入前与任务定义的上下文绑定校验（约束 #16）。
  前置漂移校验——执行前检查 upstream_files 是否被修改（约束 #34）。
  范围蔓延检测——记录 modified_files_actual/lines_changed_actual 与下游比对（约束 #37）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\circuit_breaker.py"
    description: "CircuitBreaker——按 task 维度断路器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\retry_handler.py"
    description: "RetryHandler——重试 + 退避 + 幂等"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\diff_planner.py"
    description: "DiffPlanner——diff-plan 模式"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\context_guard.py"
    description: "ContextGuard——上下文绑定校验 + 前置漂移 + 范围蔓延"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\retry_handler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\diff_planner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\context_guard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #13-#17"
    reason: "AI 执行可靠性约束——SSoT"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #13-#17 详细实现要求"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 18000
timeout_minutes: 60

acceptance_criteria:
  - "断路器：同一 task 连续 3 次失败后跳闸，需人工 reset"
  - "retry：retry_count ≤ max_retries，退避时间= retry_backoff_seconds"
  - "幂等：同一 task_id + checkpoint 重复执行不会重复写入"
  - "diff-plan：生成 SearchReplace 式 diff 而非全文重写"
  - "上下文保护：写入前验证 allowed_touch 和 forbidden_touch"
  - "前置漂移：执行前 upstream_files hash 比对——不一致时报告"
  - "范围蔓延：modified_files_actual ⊆ allowed_touch"

rollback_instructions: |
  1. 移除 reliability/ 目录下新增文件
  2. 回退 blueprint_decomposer.py 中的可靠性调用

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

# 实现 AI 执行可靠性——断路器 + Retry + 幂等 + diff-plan + 上下文保护

## 目标

构建 AI 任务执行的可靠性保障体系：
1. 断路器——按 task 维度失败保护
2. Retry 与幂等——可控重试 + 幂等写入
3. diff-plan——精细化代码修改
4. 上下文保护——写入前合规校验
5. 前置漂移——执行前文件不变检测
6. 范围蔓延——执行后范围合规校验

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）

## 执行步骤

### 读
- core/models.py 可靠性相关字段（retry_count/max_retries/retry_backoff_seconds/circuit_breaker_open/allowed_touch/forbidden_touch）

### 做
1. CircuitBreaker——task 维度失败计数 + N次跳闸 + 人工 reset
2. RetryHandler——retry 计数 + 退避延迟 + 上限
3. DiffPlanner——diff-plan 实现
4. ContextGuard——allowed_touch/forbidden_touch 验证 + hash 比对 + 范围蔓延检测

### 产
- reliability/ 目录 4 个文件

### 检
```bash
pytest tests/unit/test_reliability.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | 4 个模块均可独立 import |
| 2 | test | 断路器 / 重试 / diff-plan / 保护 均有测试 |
| 3 | lint | 0 errors |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 断路器过敏感——正常波动触发跳闸 | 仅对同一 task + 同一错误类型计数 |
| 上下文保护阻塞合法修改 | 仅对 checked 到已修改的文件做校验——不是所有文件 |
