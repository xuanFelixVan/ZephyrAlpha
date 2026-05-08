---
task_id: "TASK-INF-0124"
module_id: "MOD-INF-024"
title: "Think-Time Cost Model — Thinking/Reasoning Token 独立核算 + Guard Upgrade Path: LLM-Dependent → LLM-Free（§2.25 + D-024-23）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.25"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\think_time_model.py"
acceptance_criteria:
  - "AC-01: ThinkTimeCostModel 独立追踪 thinking_tokens vs output_tokens——不在同一 counter 中合并"
  - "AC-02: thinking_overhead_too_high——thinking_tokens > 2× output_tokens → DEGRADE（切 tier_0 非 reasoner）"
  - "AC-03: zero_effect_thinking——thinking_tokens > 500 AND output unchanged from previous attempt → MARK wasteful"
  - "AC-04: Guard Upgrade Path——每个 LLM-dependent guard 自动跟踪转型进度 {guard_name: phase} 五阶段模型"
  - "AC-05: upgrade_phase 五阶段：1.llm_only(costly) → 2.hybrid_both(run both compare) → 3.hybrid_confidence(> 90% agree N days) → 4.llm_free_primary(LLM backup only) → 5.llm_free(removed LLM)"
  - "AC-06: ThinkTime 数据在 cost attribution 中分开展示——'thinking_cost' 独立子维度"
  - "AC-07: think_time 集成到 Model Router——thinking_heavy 标志影响路由决策"
  - "AC-08: OpenRouter 不支持 thinking_tokens 拆分 → fallback: estimate thinking=output×0.8"
rollback_instructions: "删除 think_time_model.py。系统退化为不分 thinking/output 的统一 token tracking"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1163-L1198 (§2.25 Think-Time Cost)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [think-time, reasoning-tokens, cost-split, upgrade-path, llm-dependent-to-free, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0124: Think-Time Cost Model + Guard Upgrade Path

## 1. 任务目标

实现 Think-Time 成本模型——区分 thinking/reasoning tokens 与 output tokens，独立核算，防止思考时间过长（thinking > 2× output）且无效果。同时实现 Guard Upgrade Path——将 LLM-dependent guards 逐步转型到纯计算，降低 Self-Budget。

## 2. 背景

蓝图 §2.25（决策 D-024-23，v0.6.0+ 新增）：Claude 3.7 extended thinking tokens 消耗不可见但计费。Abacus.AI 2025: thinking tokens 可能 5-10× output tokens。

## 3. 实施步骤

```python
class ThinkTimeCostModel:
    def __init__(self, tracker: BudgetTracker):
        self.tracker = tracker
        self.upgrade_tracker = GuardUpgradeTracker()

    def analyze(self, thinking_tokens: int, output_tokens: int,
                output_changed: bool) -> ThinkTimeReport:
        overhead = thinking_tokens / max(output_tokens, 1)
        wasteful = thinking_tokens > 500 and not output_changed
        return ThinkTimeReport(overhead, wasteful, self._action(overhead, wasteful))

    def _action(self, overhead: float, wasteful: bool) -> ThinkTimeAction:
        if wasteful: return ThinkTimeAction.MARK_WASTEFUL_AND_RETRY
        if overhead > 2: return ThinkTimeAction.DEGRADE_TO_NON_REASONER
        return ThinkTimeAction.ALLOW

class GuardUpgradeTracker:
    PHASES = ["llm_only", "hybrid_both", "hybrid_confidence", "llm_free_primary", "llm_free"]

    def track(self, guard_name: str):
        # 评估当前阶段，推进升级
    def weekly_audit(self):
        # 报告哪些 guard 可以升级到下一阶段
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/think_time_model.py` | 新建 |
