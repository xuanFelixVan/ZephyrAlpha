# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.actors.global_action_scheduler
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_global_action_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Global Action Scheduler — v0.16.0 R226

Blindspot: Multiple concurrent autonomous actions uncoordinated; resource conflicts undetected.
Risk: R226 — Two FLE repairs target same resource simultaneously; deadlock or race.

Mitigation: Global priority-based action scheduler with deadlock detection and preemption.
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
            action.started_at = time.time()
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
