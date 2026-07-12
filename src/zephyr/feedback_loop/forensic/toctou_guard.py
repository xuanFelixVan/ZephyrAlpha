# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.toctou_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_toctou_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""TOCTOU Guard — v0.15.0 R207

Blindspot: State changes between diagnosis and repair execution invalidate diagnosis assumptions.
Risk: R207 — Diagnosis based on t=0 state; repair executes at t=1 when state already changed.

Mitigation: Time-of-Check-Time-of-Use guard: snapshots state at diagnosis, re-validates before action.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class StateSnapshot:
    snapshot_id: str
    state_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class TOCTOUGuard:
    snapshots: dict[str, StateSnapshot] = field(default_factory=dict)

    def snapshot(self, decision_id: str, state: dict) -> StateSnapshot:
        state_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        snap = StateSnapshot(snapshot_id=decision_id, state_hash=state_hash)
        self.snapshots[decision_id] = snap
        return snap

    def validate(self, decision_id: str, current_state: dict) -> bool:
        snap = self.snapshots.get(decision_id)
        if snap is None:
            return False
        current_hash = hashlib.sha256(json.dumps(current_state, sort_keys=True).encode()).hexdigest()
        return snap.state_hash == current_hash
