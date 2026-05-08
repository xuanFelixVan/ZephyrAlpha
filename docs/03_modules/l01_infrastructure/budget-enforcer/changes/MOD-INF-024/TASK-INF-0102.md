---
task_id: "TASK-INF-0102"
module_id: "MOD-INF-024"
title: "BudgetTracker — 七级三维（Token+Cost+Time）消耗统计 + BudgetPool 弹性共享 + Consumption Deviation（§2.1 + §2.10 + §2.12）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.1 + §2.10 + §2.12"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
acceptance_criteria:
  - "AC-01: BudgetTracker 类初始化接受 budget_policy.yaml 路径，解析为结构化配置对象"
  - "AC-02: 实现七级计数器：global_counter, session_counter, workflow_counter, task_counter, turn_counter, request_counter, self_budget_counter"
  - "AC-03: 每个计数器三维度追踪：token_count (input + output + reasoning), cost_amount (USD), elapsed_time_s"
  - "AC-04: 提供 consume(level, tokens, cost, time_s) 统一消费接口——原子更新所有上级计数器（如 request 消费同时更新 task+session+global）"
  - "AC-05: 提供 remaining(level, dimension) 查询接口——返回该级该维度的剩余预算（hard_limit - consumed）"
  - "AC-06: 提供 ratio(level, dimension) 查询接口——返回 consumed/hard_limit 比率"
  - "AC-07: 时间维度实现 Timer 上下文管理器——__enter__ 启动计时，__exit__ 自动 consume 时间"
  - "AC-08: reset(level) 方法——按 reset 配置（会话结束/周一零时/任务完成）清空计数器"
  - "AC-09: BudgetPool 实现 adaptive_weighted 分配 + dynamic_rebalance（任一 Task > 80% + 存在 Task < 40% → 转移 20%）"
  - "AC-10: 实现 cross_session_savings——session 结束时未用预算 30% 入储蓄池，global_used > 80% 时自动释放"
  - "AC-11: 实现 per_agent_sub_pool——默认 max_share 25%，code_generation 50%、analysis 30%、operations 20%"
  - "AC-12: 实现 plan_estimated vs actual 偏差记录——偏差 > 30% 触发 budget_enforcer_deviation_events"
  - "AC-13: 偏差校准系数按模型独立维护，每周基于最近 20 任务自动更新"
  - "AC-14: 所有方法线程安全——使用 threading.Lock 保护计数器更新"
  - "AC-15: 输出格式统一为 Python dataclass——BudgetSnapshot(level, tokens, cost, time, ratio, remaining)"
rollback_instructions: "删除 budget_tracker.py 并回退 budget_policy.yaml 到上一版本（若修改过）——其他组件（Pre-flight Gate/Stream Abort）依赖此组件，回滚前确认无 downstream consumer 活跃引用"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L78-L138 (§2.1 seven-level budget + time_budget)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L623-L668 (§2.10 Budget Pool + Agent sub-pool)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L720-L736 (§2.12 Consumption Deviation)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [budget-tracker, seven-level, 3d-budget, pool-elastic, consumption-deviation, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0102: BudgetTracker — 七级三维消耗统计 + BudgetPool + Consumption Deviation

## 1. 任务目标

实现 Budget Enforcer 的核心数据引擎——BudgetTracker。它是所有预算决策的数值来源：Pre-flight Gate 预取剩余预算、Degradation Manager 判断降级阈值、ROI Calculator 取消耗数据、Burn Rate Monitor 取速率快照，全部依赖此组件。

## 2. 背景

蓝图 §2.1 定义七级预算体系（D-024-02 决策升级：五级→七级，D-024-19 新增 Self-Budget 级，D-024-22 新增 Workflow 级），三维度涵盖 Token（input+output+reasoning）、Cost（USD）、Time（wall-clock seconds）。蓝图 §2.10 定义 BudgetPool 弹性共享策略（adaptive_weighted + dynamic_rebalance + cross_session_savings + per_agent_sub_pool）。蓝图 §2.12 定义计划消耗 vs 实际消耗偏差追踪。

## 3. 实施步骤

### Step 1: 类型定义
```python
from dataclasses import dataclass, field
from enum import Enum

class BudgetLevel(Enum):
    REQUEST = "request"       # L0
    TURN = "turn"             # L1
    TASK = "task"             # L2
    SESSION = "session"       # L3
    WORKFLOW = "workflow"     # L3.5
    GLOBAL = "global"         # L4
    SELF = "self_budget"      # L4.5

class BudgetDimension(Enum):
    TOKENS = "tokens"
    COST = "cost"
    TIME = "time"

@dataclass
class BudgetSnapshot:
    level: BudgetLevel
    tokens_consumed: int
    tokens_hard_limit: int
    cost_consumed: float
    cost_hard_limit: float
    time_consumed_s: float
    time_hard_limit_s: float
    ratio_tokens: float
    ratio_cost: float
    ratio_time: float
```

### Step 2: BudgetCounter 实现
- 每个 Counter 维护三维累计值 + hard_limit/soft_limit
- consume() 原子加——带 threading.Lock
- remaining() / ratio() 即时计算

### Step 3: BudgetTracker 实现
- `__init__(policy_path)` 加载 budget_policy.yaml
- `consume(level, tokens, cost, time_s)` 级联消耗
- `remaining(level, dim)` / `ratio(level, dim)` 查询
- `snapshot(level)` → BudgetSnapshot
- `reset(level)` 按策略时间规则重置

### Step 4: TimeTracker 上下文管理器
```python
class TimeTracker:
    def __init__(self, tracker, level):
        self.tracker = tracker
        self.level = level
    def __enter__(self):
        self.start = time.monotonic()
        return self
    def __exit__(self, *args):
        elapsed = time.monotonic() - self.start
        self.tracker.consume(self.level, tokens=0, cost=0, time_s=elapsed)
```

### Step 5: BudgetPool 实现
- 初始化：complexity_weighted 分配 + 15% reserve_buffer
- dynamic_rebalance()：每 30 分钟检查 imbalance
- cross_session_savings：session.reset 时 30% 入池
- per_agent_sub_pool：三个 category（code_generation/analysis/operations）

### Step 6: Consumption Deviation 实现
- plan_estimated_tokens 记录（task_start 时写入）
- task_end 对比 actual vs plan
- 偏差 > 30% → 写入 budget_enforcer_deviation_events
- calibration_factor 按 model 维护，每周滚动更新

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/budget_tracker.py` | 新建 |
