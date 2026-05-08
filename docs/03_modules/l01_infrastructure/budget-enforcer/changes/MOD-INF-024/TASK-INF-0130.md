---
task_id: "TASK-INF-0130"
module_id: "MOD-INF-024"
title: "Bootstrapping Calibrator — Day 0→30 渐进收紧阈值 + Self-Learning + Fail-Safe Defaults（§2.30）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: self_calibrating
blueprint_section: "§2.30"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0133"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\bootstrapping_calibrator.py"
acceptance_criteria:
  - "AC-01: 1-Phase 建模——模块刚上线（无历史值基准）→默认值 + 自学习阈值过程"
  - "AC-02: Day 0 defaults 设为宽松——基于业界 benchmark 的 True North 目标 (not current state)"
  - "AC-03: self_learning_model——Day 7 self-learning period, Day 30 完成 calibration"
  - "AC-04: auto_calibrate——每日检查 actuals vs targets 并自动更新阈值（auto=true, max_adjust_ratio=0.30）"
  - "AC-05: divergence_signal——如果 actual > expected × 2 → 延迟校准（调查是否有 leak/new pattern）"
  - "AC-06: zero-session 正向分析——对照 Budget Enforcer 上线后 30 天内的消耗趋势与引入之前"
  - "AC-07: fail-safe defaults——如果 Day 0-30 数据不足以生成有效阈值 → 使用保守默认值"
  - "AC-08: weekly calibration audit——记录原始值、参考值、实际值、更新时间、auto=true/false"
  - "AC-09: manual_override——Owner 可通过 budget_overrides.yaml 手动覆盖所有自动校准值"
  - "AC-10: reset calibration history——提供 'zephyr budget calibration reset' 一键清空所有自动校准数据"
rollback_instructions: "删除 bootstrapping_calibrator.py + 所有自动校准历史数据。系统回退到 Day 0 硬编码默认阈值（重新进入 Bootstrapping Phase）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1397-L1418 (§2.30 Bootstrapping Calibration)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [bootstrapping, calibration, cold-start, self-learning, progressive-tightening, self_calibrating]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0130: Bootstrapping Calibrator — 渐进式收紧阈值

## 1. 任务目标

实现启动校准器——Budget Enforcer 刚上线没有历史消耗数据时，使用宽松默认值 + 30 天自学习过程逐步收紧到真实模式。防止新系统上线就把所有请求误杀（over-blocking bias）。

## 2. 背景

蓝图 §2.30（v0.6.0 新增，D-024-28 关联）：Day 0-30 是 budget system 的脆弱期——钱少但阈值未校准。精确的阈值需要积累数据但积累数据需要有预算。

## 3. 实施步骤

```python
class BootstrappingCalibrator:
    DAY_ZERO_DEFAULTS = {
        "session_cost_hard_limit": 1.00,    # 基于 Gemini Free Tier 平均调用
        "task_cost_hard_limit": 0.20,
        "global_daily_cost_limit": 30.00,   # 业界 Agent startup budget median
    }
    CALIBRATION_DAYS = 30

    def __init__(self, policy: dict, history_store):
        self.day = self._calculate_day()
        self.tightness = self._tightness_factor(self.day)

    def calibrate(self, actuals: dict[str, float]) -> CalibrationResult:
        updated = {}
        for key, value in actuals.items():
            target = self.DAY_ZERO_DEFAULTS[key] * self.tightness
            updated[key] = min(value * 1.1, target)
        return CalibrationResult(updated, self.day, self.tightness)

    def _tightness_factor(self, day: int) -> float:
        # Day 0: 1.0 (loose)
        # Day 15: 0.5 (moderate)
        # Day 30: 0.3 (tight)
        return max(0.3, 1.0 - (day / self.CALIBRATION_DAYS) * 0.7)
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/bootstrapping_calibrator.py` | 新建 |
