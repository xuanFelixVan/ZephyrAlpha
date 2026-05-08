---
task_id: "TASK-INF-0121"
module_id: "MOD-INF-024"
title: "Token Spiral EWS — 四维早期预警（Context Expansion/Tool Multiplication/Depth Explosion/Time Growth）+ Spiral Score（§2.22 + D-024-20）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.22"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\spiral_ews.py"
acceptance_criteria:
  - "AC-01: expanding_context——last_5_inputs 递增趋势（Pearson r > 0.7）→ WARN '上下文在膨胀——建议立即 /compact'"
  - "AC-02: multiplying_tool_calls——last_5_turns tool_call count 单调递增 → WARN + 连续 3 次递增触发 L3_compress"
  - "AC-03: depth_explosion——delegation_depth > 4 → HALT delegation + 扁平化处理"
  - "AC-04: time_per_turn_growth——last_5_turns duration 单调递增 → WARN + 建议 Narrow Scope/拆分任务"
  - "AC-05: spiral_score 综合评分 0-100——weighted_sum(4 markers)"
  - "AC-06: score thresholds——30: L1_warning, 60: L3_compress + auto_narrow, 80: L6_kill_switch"
  - "AC-07: spiral_score 每次 LLM 调用后 update——积分滑动窗口 5 轮"
  - "AC-08: EWS 自身 LLM-free（仅统计计算无需 LLM call）——零 self-budget 消耗"
  - "AC-09: EWS 事件写入 audit trail——含 marker, score, trend_vector, triggered_action"
  - "AC-10: 支持 reset_recent_window()——手动重置滑动窗口消除误报累积"
rollback_instructions: "删除 spiral_ews.py。系统退化为无螺旋早期预警——依赖 Burn Rate Monitor（总速率）和 Timeout Guard（硬超时）作为最后防线"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1054-L1091 (§2.22 Spiral EWS)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [spiral-ews, token-spiral, pearson-r, early-warning, spiral-score, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0121: Token Spiral EWS — 四维螺旋早期预警

## 1. 任务目标

实现 Token Spiral 早期预警系统——专门检测请求量指数增长的螺旋模式。与 Burn Rate Monitor（总速率）互补——Burn Rate 说"烧得快"，Spiral EWS 说"每一个请求让下一个请求更大/更多"。Border TechAhead 2026: "1 task → 47 API calls" spiral pattern。

## 2. 背景

蓝图 §2.22（决策 D-024-20，v0.6.0 新增）：四维检测（expanding_context, multiplying_tool_calls, depth_explosion, time_per_turn_growth）+ spiral_score 综合评分。LLM-free 设计——纯统计计算，零 self-budget 消耗。

## 3. 实施步骤

```python
class SpiralEWS:
    def __init__(self, tracker: BudgetTracker, delegation_tracker):
        self.markers = {
            "expanding_context": ExpandingContextDetector(pearson_r=0.7),
            "multiplying_tool_calls": MultiplyingToolCallsDetector(),
            "depth_explosion": DepthExplosionDetector(max_depth=4),
            "time_per_turn_growth": TimePerTurnGrowthDetector(),
        }
        self.score_calc = SpiralScoreCalculator(weights={
            "expanding_context": 0.25,
            "multiplying_tool_calls": 0.30,
            "depth_explosion": 0.25,
            "time_per_turn_growth": 0.20,
        })

    def update(self, turn_data: TurnData) -> SpiralStatus:
        scores = {}
        for name, detector in self.markers.items():
            scores[name] = detector.evaluate(turn_data)
        spiral_score = self.score_calc.compute(scores)
        return SpiralStatus(spiral_score, scores, self._action(spiral_score))

    def _action(self, score: float) -> SpiralAction:
        if score >= 80: return SpiralAction.KILL_SWITCH
        if score >= 60: return SpiralAction.L3_COMPRESS_NARROW
        if score >= 30: return SpiralAction.L1_WARNING
        return SpiralAction.NONE
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/spiral_ews.py` | 新建 |
