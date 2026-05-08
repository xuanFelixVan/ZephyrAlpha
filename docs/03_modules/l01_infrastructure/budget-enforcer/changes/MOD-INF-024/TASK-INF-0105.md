---
task_id: "TASK-INF-0105"
module_id: "MOD-INF-024"
title: "Degradation Manager — 六级降级链 + L1.5 沉没成本干预 + Narrow/Reroute + Auto-Recovery + Anti-Spiral（§2.4 + D-024-05）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.4"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
acceptance_criteria:
  - "AC-01: DegradationManager 管理完整八级降级状态机：L0_notify → L1_warning → L1.5_sunk_cost_warn → L2_model_switch → L3_compress → L4_minimal → L5_halt → L6_kill_switch"
  - "AC-02: 每级 trigger 条件、action、auto 标志独立配置且可被 budget_policy.yaml 覆盖"
  - "AC-03: L0_notify：session_budget_used > 50% OR burn_rate_1h > 3× normal → 终端显示 '💰 预算: X/Y tokens (Z%)'"
  - "AC-04: L1.5_sunk_cost_warn：cost_to_completion_ratio > 3× AND 任务产出 < 20% → '预算已消耗 80% 但产出仅 10%——建议放弃'"
  - "AC-05: L2_model_switch：优先级最高——在压缩上下文之前执行模型降级"
  - "AC-06: L3_compress：集成 MOD-INF-008 Context Engine DocCompressor aggressive 模式"
  - "AC-07: L5_halt.user_communication：预算耗尽后输出结构化模板（含 {level}, {used}/{limit}, {output_path}）"
  - "AC-08: L6_kill_switch：单日成本 > $100 OR 连续 5 请求 DENY OR runaway loop → 全局熔断"
  - "AC-09: Adaptive Interventions——narrow_scope（task_budget_used > 70% AND progress < 30%）+ reroute_strategy（同 task 内 model_switch 2 次+）"
  - "AC-10: global_timeout_kill：task_timeout OR session_timeout → IMMEDIATE_ABORT + Action History checkpoint"
  - "AC-11: auto_recovery：连续 3 请求 burn_rate < 1× normal AND budget < soft_limit × 0.6 → 回升一级"
  - "AC-12: anti_spiral：max_degradation_per_minute=1, recovery_cooldown=180s"
  - "AC-13: 新会话开始 → 完全重置到 L0"
  - "AC-14: 每次降级决策写入 audit trail（包含 trigger_event, current_level, new_level, reason, timestamp）"
  - "AC-15: resume checkpoint 保存——abort 时写入完整状态便于恢复"
rollback_instructions: "删除 degradation_manager.py，所有调用点降级为静态配置——系统退化为无动态降级模式，超预算仅记录日志不干预（fail-unsafe 退化状态）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L268-L368 (§2.4 Degradation + Adaptive Interventions)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [degradation-manager, degrdation-chain, sunk-cost, narrow, reroute, anti-spiral, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0105: Degradation Manager — 六级降级链 + 自适应干预 + 反螺旋

## 1. 任务目标

实现完整降级管理器——Budget Enforcer 的核心执行器。当预算消耗达到各级阈值时，自动执行对应降级动作（通知→降模型→压缩上下文→最小化→硬停止→熔断）。同时支持 Narrow（窄化范围）和 Reroute（切换策略）两种轻量干预，以及自动回升和反螺旋保护。

## 2. 背景

蓝图 §2.4（决策 D-024-05）：六级降级链（v0.4.0 新增 L1.5 沉没成本干预 + L5_halt 用户沟通协议）。v0.5.0 新增 adaptive_interventions（Oracle Runtime Budget Guardrails 对标——在 degrade/stop 二元外增加 Narrow 和 Reroute）。v0.6.0 新增 global_timeout_kill。

## 3. 实施步骤

### Step 1: 降级状态机
```python
class DegradationLevel(Enum):
    L0_NOTIFY = 0
    L1_WARNING = 1
    L1_5_SUNK_COST = 1.5
    L2_MODEL_SWITCH = 2
    L3_COMPRESS = 3
    L4_MINIMAL = 4
    L5_HALT = 5
    L6_KILL_SWITCH = 6

class DegradationManager:
    def __init__(self, tracker, policy, context_engine_proxy):
        self.current_level = DegradationLevel.L0_NOTIFY
        self.level_history: list[DegradationEvent] = []
        self._anti_spiral = AntiSpiralGuard(max_per_minute=1, cooldown=180)

    def evaluate(self) -> DegradationAction:
        # 基于 tracker.ratio(all_levels) 判断是否需要升降级
        # 返回 DegradationAction(target_level, reason, actions)

    def execute(self, action: DegradationAction) -> DegradationResult:
        # 执行 action.actions 列表中的所有操作
        # 写入 audit trail
```

### Step 2: 每级 Action 实现
- L0: 终端彩色输出剩余预算
- L1: WARNING 日志 + 标记 task 为 'budget_watch'
- L1.5: 计算 cost_to_completion_ratio，告警并建议放弃
- L2: 调用 ModelRouter.degrade()
- L3: 调用 ContextEngine.compress(aggressive=True)
- L4: 设置 minimal_context 标志
- L5: 硬停止 + user_communication 模板渲染 + fallback_action
- L6: 全局熔断 + 调用 MOD-INF-001 Kill Switch

### Step 3: Narrow/Reroute
- narrow_scope(): 生成 core_subtasks（仅需完成的最关键 20%）
- reroute_strategy(): 判断是否切换 pipeline 模式

### Step 4: Auto-Recovery
- 定期检查 recovery conditions
- 确认非 spiral → 回升一级
- max_recovery=L1（不自动回 L0）

### Step 5: Anti-Spiral Guard
- 跟踪最近 1 分钟内的降级次数
- count >= max_per_minute → 锁定当前级别
- recovery_cooldown 过后才允许下一次降级

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/degradation_manager.py` | 新建 |
