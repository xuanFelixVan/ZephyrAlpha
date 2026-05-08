---
task_id: "TASK-INF-0119"
module_id: "MOD-INF-024"
title: "Timeout Guard — 独立并行 asyncio Daemon Timer（§2.20 + D-024-18）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: scaffold
blueprint_section: "§2.20"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\timeout_guard.py"
acceptance_criteria:
  - "AC-01: TimeoutGuard 独立 asyncio task——与 Pre-flight Gate/Stream Abort 并行运行，fire-and-forget"
  - "AC-02: session_timer——countdown 28800s(8h)，on_expiry: FORCE_ABORT 所有活跃请求 + 保存 Action History + resume checkpoint + audit"
  - "AC-03: session expiry message——'⏰ Session 时间预算已耗尽（8h）——当前进度已保存。下次启动自动恢复。'"
  - "AC-04: task_timer——countdown 3600s(1h)，on_expiry: FORCE_ABORT + 自动委托到新 Task"
  - "AC-05: request_timer——countdown 120s(2min)，on_expiry: CANCEL streaming SSE + ABORT + auto_retry（不同 Provider）"
  - "AC-06: Session daemon timer 在 Budget Enforcer 启动时自动创建——不在 budget chain 中"
  - "AC-07: 支持 pause/resume 操作——用于等待人工确认场景（如 borrow/payback down-time）"
  - "AC-08: timer expiry 写入 audit trail——含 level, elapsed, max_timeout, checkpoint_saved"
  - "AC-09: sidestep 机制——'--no-timeout' 可绕过单次任务超时（Owner 确认的风险决策）"
rollback_instructions: "删除 timeout_guard.py，daemon timer 停止。系统退化为无墙钟超时控制——仅依赖 token/cost 预算（慢模型/dead loop 无法被拦截）"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L980-L1006 (§2.20 Timeout Guard)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [timeout-guard, daemon-timer, wall-clock, asyncio, agentguard, scaffold]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0119: Timeout Guard — 独立并行超时守卫

## 1. 任务目标

实现独立并行超时守卫——一个与预算链（Pre-flight→Degradation→Stream Abort）并行的 asyncio daemon timer。在 Token/Cost 预算基础上补充 wall-clock 时间预算。对标 AgentGuard (2026.4) 的三大 guard 之一 Timeout Guard。

## 2. 背景

蓝图 §2.20（决策 D-024-18，v0.5.0 新增）：存在 token 消耗少但耗时极长的任务（死循环/慢模型/网络抖动）——仅 token/cost 预算无法覆盖。Timeout Guard 独立于降级协商流程，一旦触发即刻 abort。

## 3. 实施步骤

```python
class TimeoutGuard:
    def __init__(self, time_budget: dict):
        self.session_timer = CountdownTimer(time_budget["session_timeout"])
        self.task_timer = CountdownTimer(time_budget["task_timeout"])
        self.request_timer = CountdownTimer(time_budget["request_timeout"])

    async def start_session_guard(self):
        self.session_timer.start()
        try:
            await self.session_timer.wait()
        except CountdownExpired:
            await self._on_session_expiry()

    async def _on_session_expiry(self):
        # FORCE_ABORT all active requests
        # Save Action History
        # Generate resume checkpoint
        # Write audit trail
        # Output expired message

class CountdownTimer:
    def __init__(self, seconds: float):
        self.remaining = seconds
        self.paused = False

    def start(self):
        self._task = asyncio.create_task(self._countdown())

    async def _countdown(self):
        await asyncio.sleep(self.remaining)
        raise CountdownExpired()

    def pause(self):
        self.paused = True

    def pause_resume(self):
        self.paused = False
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/timeout_guard.py` | 新建 |
