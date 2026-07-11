# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.resilience.oscillation_damping
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_oscillation_damping | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Oscillation Damping — v0.37.0 R450

Blindspot: FLE actions in rapid succession cause oscillatory instability;
system flips between corrective states without convergence.

Risk: R450 — Unstable feedback loop; FLE overcorrects -> re-corrects -> oscillates indefinitely.

Mitigation: PID-style damping with action cooldown windows. Track reversal frequency;
if >3 reversals in 60s -> force cooldown + escalate to owner.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DampingState(str, Enum):
    STABLE = "STABLE"
    DAMPING = "DAMPING"
    COOLDOWN = "COOLDOWN"


@dataclass
class OscillationDamping:
    cooldown_seconds: float = 60.0
    max_reversals: int = 3
    reversal_window: float = 60.0

    state: DampingState = DampingState.STABLE
    last_action_type: str = ""
    reversal_count: int = 0
    reversal_history: list[float] = field(default_factory=list)
    cooldown_until: float = 0.0

    def record_action(self, action_type: str) -> DampingState:
        now = time.time()
        self.reversal_history = [t for t in self.reversal_history if now - t < self.reversal_window]

        if action_type != self.last_action_type and self.last_action_type:
            self.reversal_count += 1
            self.reversal_history.append(now)

        self.last_action_type = action_type

        if len(self.reversal_history) >= self.max_reversals:
            self.state = DampingState.COOLDOWN
            self.cooldown_until = now + self.cooldown_seconds
        elif len(self.reversal_history) >= 1:
            self.state = DampingState.DAMPING
        else:
            self.state = DampingState.STABLE

        return self.state

    def is_allowed(self) -> bool:
        if self.state is DampingState.COOLDOWN and time.time() < self.cooldown_until:
            return False
        return True

    def remaining_cooldown(self) -> float:
        if self.state is not DampingState.COOLDOWN:
            return 0.0
        return max(0.0, self.cooldown_until - time.time())
