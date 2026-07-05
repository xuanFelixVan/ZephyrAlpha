# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.toctou_revalidation
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_toctou_revalidation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""TOCTOU Revalidation — v0.37.0 R458

Blindspot: FLE checks system state, then acts on it with a time gap;
state may have changed between check and action (Time-of-Check-Time-of-Use).

Risk: R458 — FLE applies repair to stale state; makes situation worse.

Mitigation: Mandatory revalidation immediately before action execution.
If state changed beyond tolerance since initial check, abort action
and restart diagnosis from fresh state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum


class TOCTOUResult(str, Enum):
    FRESH = "FRESH"
    STALE_ABORT = "STALE_ABORT"
    STALE_RECHECK = "STALE_RECHECK"


@dataclass
class TOCTOURevalidation:
    max_staleness_seconds: float = 5.0
    state_tolerance: float = 0.1

    last_check_at: float = 0.0
    last_check_hash: str = ""
    abort_count: int = 0

    def snapshot_state(self, state_dict: dict) -> str:
        self.last_check_at = time.time()
        self.last_check_hash = self._hash_state(state_dict)
        return self.last_check_hash

    def revalidate(self, current_state: dict) -> TOCTOUResult:
        now = time.time()
        staleness = now - self.last_check_at

        if staleness > self.max_staleness_seconds:
            self.abort_count += 1
            return TOCTOUResult.STALE_ABORT

        current_hash = self._hash_state(current_state)
        if current_hash != self.last_check_hash:
            self.abort_count += 1
            return TOCTOUResult.STALE_RECHECK

        return TOCTOUResult.FRESH

    @staticmethod
    def _hash_state(state: dict) -> str:
        import hashlib

        raw = str(sorted(state.items())).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]
