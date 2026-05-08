---
task_id: "TASK-INF-0109"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §1.2 目标 #9/#10 + 盲点 #16/#17/#18/#19/#20"

title: "实现全链路可观测性——Trace + 通知 + 成本追踪 + CLI 摘要 + 失败模式匹配"
description: |
  实现任务执行 Trace——全局 trace_id 贯穿任务卡全生命周期。
  通知——状态变更通知到 NTF-INF-002 NotificationTriage。
  成本追踪——每次 LLM 调用记录 token/prompt_type/model 到成本账本。
  CLI 摘要——`task-cli summary` 命令读取 SQLite 输出可读摘要。
  失败模式匹配——失败原因自动标记语义标签便于归类。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\trace.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\trace.py"
    description: "TraceManager——trace_id 生成 + span 管理"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\cost_tracker.py"
    description: "CostTracker——LLM 调用成本记录"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\failure_matcher.py"
    description: "FailureMatcher——失败模式匹配与归类"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\cli_summary.py"
    description: "CLI 摘要生成器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\notifier.py"
    description: "Notifier——状态变更通知"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\trace.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\cost_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\failure_matcher.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\cli_summary.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\notifier.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§1.2 目标 #9/#10"
    reason: "可观测性目标定义"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§1.2 目标 #9/#10 + 盲点 #16-#20 定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
  - "M7"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "trace_id 贯穿状态转换全链路——每个 transition 关联同一 trace_id"
  - "成本追踪——LLM 调用后 cost_tracker 被调用且记录正确"
  - "CLI summary 命令输出可读任务状态摘要"
  - "失败模式匹配——失败任务自动标记语义标签"
  - "通知——状态变更触发通知发送"

rollback_instructions: |
  1. 移除 observability/ 目录下新增文件（保留旧 trace.py）
  2. 回退 pipeline 订阅回调

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "observability"
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

# 实现全链路可观测性——Trace + 通知 + 成本追踪 + CLI 摘要 + 失败模式匹配

## 目标

构建任务系统的全链路可观测性：
1. Trace——全生命周期 trace_id + span
2. 通知——状态变更通知
3. 成本追踪——LLM 调用成本记录
4. CLI 摘要——可读的任务状态摘要
5. 失败模式匹配——失败原因语义归类

## 触发条件

- core/models.py 重写完成（TASK-INF-0102）

## 执行步骤

### 读
- core/models.py 模型
- pipeline-module-registry.yaml ——M7 自动化审阅

### 做
1. TraceManager——trace_id/span_id 生成 + 父子 span 关联
2. CostTracker——prompt_type/model/tokens 记录
3. FailureMatcher——失败原因正则 + 语义标签映射
4. CLISummary——SQLite → stdout 格式化
5. Notifier——NTF-INF-002 集成

### 产
- observability/ 目录 5 个文件

### 检
```bash
pytest tests/unit/test_observability.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | 5 个模块均可独立 import |
| 2 | test | 有单元测试覆盖 |
| 3 | lint | 0 errors |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 成本跟踪 I/O 干扰主流程 | 异步写入——成本记录在单独线程中 |
| 通知发送失败阻塞任务状态流转 | 通知采用 fire-and-forget——失败仅记录日志 |
