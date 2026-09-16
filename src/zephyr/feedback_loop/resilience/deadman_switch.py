# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.deadman_switch
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] (none — stdlib only)
# [CONSUMERS] zephyr.data.tick_subscriber; zephyr.ex_core.live_strategy_adapter; zephyr.risk.core.emergency_stop_confirmation; zephyr.frontend.dashboard.services_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/feedback/resilience_dr/test_deadman_switch.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Deadman Switch — v0.15.0 R212

Blindspot: FLE runs autonomously with no external kill-switch; runaway unstoppable.
Risk: R212 — Malicious skill takes over; FLE keeps running; no external forced shutdown.

Mitigation: 60s heartbeat; 3 consecutive misses -> automatic self-lock + external alert.

# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/resilience/deadman_switch.yaml
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DeadmanState(str, Enum):
    ALIVE = "ALIVE"
    WARNING = "WARNING"
    LOCKED = "LOCKED"


@dataclass
class DeadmanSwitch:
    heartbeat_interval: float = 60.0
    max_missed: int = 3
    state: DeadmanState = DeadmanState.ALIVE
    missed_count: int = 0
    last_beat: float = field(default_factory=time.time)

    def heartbeat(self) -> DeadmanState:
        self.last_beat = time.time()
        self.missed_count = 0
        if self.state is DeadmanState.WARNING:
            self.state = DeadmanState.ALIVE
        return self.state

    def check(self) -> DeadmanState:
        elapsed = time.time() - self.last_beat
        if elapsed > self.heartbeat_interval:
            self.missed_count += 1
            self.last_beat = time.time()
        if self.missed_count >= self.max_missed:
            self.state = DeadmanState.LOCKED
        elif self.missed_count > 0:
            self.state = DeadmanState.WARNING
        return self.state

    @property
    def is_locked(self) -> bool:
        return self.state is DeadmanState.LOCKED
