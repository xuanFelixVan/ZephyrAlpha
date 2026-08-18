# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.global_action_scheduler
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Global Action Scheduler — v0.16.0 R226

Blindspot: Multiple concurrent autonomous actions uncoordinated; resource conflicts undetected.
Risk: R226 — Two FLE repairs target same resource simultaneously; deadlock or race.

Mitigation: Global priority-based action scheduler with deadlock detection and preemption.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 待调度动作
#   fields: ScheduledAction(action_id, priority, target_resources)
#   code: GlobalActionScheduler.enqueue
# 层: 算法
# - id: A1
#   name_zh: 优先级队列调度
#   name_en: priority_queue_dispatch
#   intro: enqueue 按 priority 降序排序，_dispatch 在 max_concurrent=3 上限内出队执行
#   code: GlobalActionScheduler.enqueue / _dispatch
# - id: A2
#   name_zh: 资源冲突死锁检测
#   name_en: resource_deadlock_detection
#   intro: 扫描运行中动作的 target_resources，共享同一资源的动作对判为死锁
#   code: GlobalActionScheduler.detect_deadlock
# 层: 输出
# - id: O1
#   name_zh: 运行态与死锁清单
#   name_en: running_state_and_deadlocks
#   intro: running 中 RUNNING 动作及 detect_deadlock 返回的冲突 action_id 列表
#   downstream: FLE 动作执行层（actors 各执行器）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ActionState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PREEMPTED = "PREEMPTED"
    DONE = "DONE"


@dataclass
class ScheduledAction:
    action_id: str
    priority: int
    state: ActionState = ActionState.QUEUED
    queued_at: float = field(default_factory=time.time)
    started_at: float | None = None
    target_resources: list[str] = field(default_factory=list)


@dataclass
class GlobalActionScheduler:
    queue: list[ScheduledAction] = field(default_factory=list)
    running: dict[str, ScheduledAction] = field(default_factory=dict)
    max_concurrent: int = 3

    def enqueue(self, action: ScheduledAction) -> None:
        self.queue.append(action)
        self.queue.sort(key=lambda a: a.priority, reverse=True)
        self._dispatch()

    def _dispatch(self) -> None:
        while len(self.running) < self.max_concurrent and self.queue:
            action = self.queue.pop(0)
            action.state = ActionState.RUNNING
            action.started_at = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
            self.running[action.action_id] = action

    def complete(self, action_id: str) -> None:
        if action_id in self.running:
            action = self.running.pop(action_id)
            action.state = ActionState.DONE
            self._dispatch()

    def preempt(self, action_id: str) -> None:
        if action_id in self.running:
            self.running[action_id].state = ActionState.PREEMPTED

    def detect_deadlock(self) -> list[str]:
        resources_used: dict[str, str] = {}
        deadlocked: list[str] = []
        for aid, action in self.running.items():
            for res in action.target_resources:
                if res in resources_used:
                    deadlocked.extend([aid, resources_used[res]])
                resources_used[res] = aid
        return deadlocked
