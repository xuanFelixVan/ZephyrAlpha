---
task_id: "TASK-INF-0103"
module_id: "MOD-INF-024"
title: "Pre-flight Gate — 事前三维预算预估 + ALLOW/DENY/DEGRADE/BORROW/NARROW 决策（§2.2 + D-024-03）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.2"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pre_flight_gate.py"
acceptance_criteria:
  - "AC-01: PreFlightGate 类位于每次 API 调用的咽喉位置——在 token 实际消耗前执行全部检查"
  - "AC-02: 实现 6 项预检规则：global_budget_check, session_budget_check, task_budget_check, turn_budget_check, request_size_check, cost_threshold_check"
  - "AC-03: 每项检查返回 GateDecision dataclass（outcome, reason, suggested_action, remaining_budget）"
  - "AC-04: 决策枚举完整实现：GateOutcome.ALLOW, .WARN, .DEGRADE, .DENY, .BORROW, .NARROW"
  - "AC-05: global_budget_check：本周 soft_limit 剩余 < 预估消耗 × 1.2 → DENY（exception: Owner 提额令）"
  - "AC-06: session_budget_check：hard_limit 剩余 < 预估消耗 → DEGRADE（强制 /compact 后再试）"
  - "AC-07: task_budget_check：hard_limit 剩余 < 预估消耗 → DEGRADE（任务拆分 + 委托新会话）"
  - "AC-08: turn_budget_check：soft_limit 剩余 < 预估消耗 → WARN（检查循环指纹 + 建议跳过冗余调用）"
  - "AC-09: request_size_check：预估 input_tokens > request_level.input_limit → DENY"
  - "AC-10: cost_threshold_check：预估单次调用成本 > $0.50 → DEGRADE（切 Tier-1 模型）"
  - "AC-11: 预估器使用 TikToken-based tokenizer，误差 < 10%——支持 Anthropic/OpenAI/Google/DeepSeek 四种 tokenizer"
  - "AC-12: Borrow 机制：enabled=true, max_borrow_ratio=0.20, payback 逻辑完整（下次任务少分 30% 直到还清）"
  - "AC-13: Narrow 决策：task_budget_used > 70% AND task_progress < 30% → NARROW（仅做核心 20%）"
  - "AC-14: Pre-flight Gate 必须非阻塞异步可重入——多 Agent 并发调用不互相阻塞"
  - "AC-15: 所有 GateDecision 写入结构化日志（decision_log.append）供事后审计"
rollback_instructions: "删除 pre_flight_gate.py，移除调用点对该类的 import。BudgetTracker 继续正常工作——回滚后系统退化为纯事后反应模式（无事前拦截）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L140-L181 (§2.2 Pre-flight Gate)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [pre-flight-gate, gate-decision, budget-check, tiktoken, borrow, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0103: Pre-flight Gate — 事前三维预算预估与拦截决策

## 1. 任务目标

实现 Pre-flight Gate——在每次 LLM API 调用前执行 6 项预算预检，返回 ALLOW/WARN/DEGRADE/DENY/BORROW/NARROW 六种决策。这是 v0.3.0 补齐的最核心盲点（盲点 #2）——将 Budget Enforcer 从纯事后反应升级为事前预防。

## 2. 背景

蓝图 §2.2（决策 D-024-03）：Google Adaptive Budgeting / kagenti pre-request blocking 启发——在 tokens 被实际消耗之前就拦截。位于所有 API 调用的咽喉位置（Pre-flight→In-flight→Post-flight 生命周期第一阶段）。v0.4.0 新增 Borrow 机制，v0.5.0 新增 NARROW 决策。

## 3. 实施步骤

### Step 1: 类型定义
```python
from dataclasses import dataclass
from enum import Enum

class GateOutcome(Enum):
    ALLOW = "allow"
    WARN = "warn"
    DEGRADE = "degrade"
    DENY = "deny"
    BORROW = "borrow"
    NARROW = "narrow"

@dataclass
class GateDecision:
    outcome: GateOutcome
    check_id: str
    reason: str
    suggested_action: str
    remaining_budget: dict
    timestamp: float
```

### Step 2: PreFlightGate 实现
```python
class PreFlightGate:
    def __init__(self, budget_tracker: BudgetTracker, policy: dict):
        self.tracker = budget_tracker
        self.policy = policy
        self.estimator = TokenEstimator()
        self.decision_log: list[GateDecision] = []

    def check(self, estimated_input: int, estimated_output: int,
              estimated_cost: float, model_tier: str,
              agent_category: str = "operations") -> GateDecision:
        # 按优先级顺序执行 6 个 check
        # 返回第一个非 ALLOW 的决策
```

### Step 3: 6 个 Check 方法
- `_check_global()` — 周预算充足性
- `_check_session()` — 会话预算充足性
- `_check_task()` — 任务预算充足性
- `_check_turn()` — 本轮预算充足性
- `_check_request_size()` — 请求大小限制
- `_check_cost_threshold()` — 单次调用成本上限

### Step 4: TokenEstimator 实现
- 支持 TikToken cl100k_base / anthropic / gemini / deepseek 四种 tokenizer
- estimate_tokens(text, model_family) → int
- 提供 batch_estimate(messages) → int

### Step 5: Borrow 逻辑
- check_outcome=BORROW 时：计算可借额度 = max_borrow_ratio × 同 Session 其他 Task 剩余预算
- 记录 borrow_amount + payback_schedule

### Step 6: NARROW 逻辑
- check_outcome=NARROW 时：生成 narrowed_scope（仅核心子任务列表）
- 注入 system prompt："你的预算已消耗 70% 但产出仅 30%——请仅完成核心子任务"

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/pre_flight_gate.py` | 新建 |
