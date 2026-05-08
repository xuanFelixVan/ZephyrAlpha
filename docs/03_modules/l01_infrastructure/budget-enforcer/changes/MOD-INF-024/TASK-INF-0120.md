---
task_id: "TASK-INF-0120"
module_id: "MOD-INF-024"
title: "Self-Budget Tracker — Budget Enforcer 自身运营成本管控 + Guard Efficiency Ratio（§2.21 + D-024-19）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.21"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\self_budget_tracker.py"
acceptance_criteria:
  - "AC-01: SelfBudgetTracker daily_cap=50000 tokens——Budget Enforcer 自身每日 token 上限"
  - "AC-02: LLM-Free triggers 归类：format_check(regex), action_history(hash), timeout_guard(timer), context_waste_detector(non-LLM), burn_rate_monitor(EMA)"
  - "AC-03: LLM-Dependent triggers 归类且强制 tier_0_free：relevance_check(cap 500), hallucination_check(cap 1000), auto_compact_suggest(cap 2000/d), reference_analysis(cap 1500/d)"
  - "AC-04: guard_efficiency——metric = tokens_saved_by_guard / tokens_consumed_by_guard"
  - "AC-05: guard auto_disable threshold < 0.5——guard 每花 2 token 才省 1 token → 关闭该 guard"
  - "AC-06: weekly_efficiency_report——生成 guard efficiency 趋势报告"
  - "AC-07: self_budget_exceeded——HALT 所有 LLM-dependent guards 降级为 warn-only（不 block）"
  - "AC-08: 终端显示 '🛡 Self-Budget: 18K/50K (36%) | Guard 效率: 1:4.2'"
  - "AC-09: 所有 guard 调用前后追踪 token consumption——在 Self-Budget counter 中核减"
rollback_instructions: "删除 self_budget_tracker.py。系统退化为无 Self-Budget——Budget Enforcer guards 自身（Output Quality Gate relevance 等 LLM-dependent checks）消耗不再被限制"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1010-L1051 (§2.21 Self-Budget)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [self-budget, guard-efficiency, llm-free, supervisoragent, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0120: Self-Budget Tracker — 自身运营成本管控

## 1. 任务目标

实现 Self-Budget——Budget Enforcer 自身所有 guards/detectors/analyzers 消耗的 token 需要独立追踪和上限。对标 SUPERVISORAGENT (ICLR 2026) 原则：guards 应该是 LLM-free trigger，仅在必要时升级到 LLM evaluation。这是"一个 AI 构建的系统如何可信地约束 AI"的关键自我校验层。

## 2. 背景

蓝图 §2.21（决策 D-024-19，v0.6.0 新增）：传统 guards 自身消耗 token 来评估 token 消耗——形成悖论。SUPERVISORAGENT 提出 LLM-free 原则来解决此问题。

## 3. 实施步骤

```python
class SelfBudgetTracker:
    DAILY_CAP = 50000

    def __init__(self, tracker: BudgetTracker):
        self.consumed = 0
        self.guard_stats: dict[str, GuardStats] = {}

    def track_call(self, guard_name: str, tokens: int,
                   is_llm_free: bool):
        self.consumed += tokens
        self.guard_stats[guard_name].consume(tokens, is_llm_free)

    def check_efficiency(self, guard_name: str) -> float:
        stats = self.guard_stats[guard_name]
        return stats.tokens_saved / max(stats.tokens_consumed, 1)

    def auto_disable_low_efficiency(self):
        for name, stats in self.guard_stats.items():
            if stats.efficiency_ratio < 0.5:
                stats.disabled = True
                self._audit(f"Guard {name} auto-disabled: efficiency={stats.efficiency_ratio}")
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/self_budget_tracker.py` | 新建 |
