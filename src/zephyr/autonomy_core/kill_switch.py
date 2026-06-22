# [A_module] module_id=MOD-ORC_kill_switch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.kill_switch

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# SRC-0041: Copy file -- keep independent implementation, pending future review
#   shared/kill_switch.py is now the unified export SSoT; this file exported
#   as ContextKillSwitch alias from shared.
#
"""kill_switch.py -- safety circuit breaker (DD110, TASK-019)"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FuseState:
    on: bool
    trigger_reason: str
    manual_reset_needed: bool


class KillSwitch:
    """per-session_err>threshold → fuse off. needs manual reset (DD110)."""

    def __init__(self, threshold: int = 5) -> None:
        self._threshold = threshold
        self._error_count = 0
        self._fuse_on = False

    def record_error(self, reason: str = "") -> FuseState:
        self._error_count += 1
        if self._error_count >= self._threshold:
            self._fuse_on = True
        return FuseState(on=self._fuse_on, trigger_reason=reason, manual_reset_needed=True)

    def reset(self) -> None:
        self._error_count = 0
        self._fuse_on = False
