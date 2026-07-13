# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly.infinite_loop_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_infinite_loop_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Infinite Loop Detector — v0.15.0 R219

Blindspot: FLE repair-recheck cycle can loop indefinitely; no loop detection.
Risk: R219 — Repair->metric improves->threshold triggers another repair->same metric->loop.

Mitigation: Loop detection via action ID repetition tracking with cooldown enforcement.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class LoopAction:
    action_signature: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class InfiniteLoopDetector:
    recent_actions: deque[LoopAction] = field(default_factory=lambda: deque(maxlen=50))
    loop_threshold: int = 3
    cooldown_seconds: float = 300.0
    active_loops: set[str] = field(default_factory=set)

    def track(self, action_signature: str) -> bool:
        now = time.time()
        self.recent_actions.append(LoopAction(action_signature=action_signature, timestamp=now))
        recent_matches = [
            a
            for a in self.recent_actions
            if a.action_signature == action_signature and now - a.timestamp < self.cooldown_seconds
        ]
        if len(recent_matches) >= self.loop_threshold:
            self.active_loops.add(action_signature)
            return True
        return False

    def clear(self, action_signature: str) -> None:
        self.active_loops.discard(action_signature)
