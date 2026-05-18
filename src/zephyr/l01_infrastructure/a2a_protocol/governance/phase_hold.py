# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.governance.phase_hold

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他 Phase 3 模块不可并发施工."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


PHASE_HOLD_ACTIVE = True
PHASE_HOLD_REASON = "A2A module locked to Phase 4 — cannot be built concurrently with Phase 3 modules (Drift, Budget, Rollback, Escalation)"


class Phase4Hold:
    """A2A Phase 4 施工锁定."""

    def __init__(self) -> None:
        self.hold_active = PHASE_HOLD_ACTIVE
        self.hold_since = datetime.now(timezone.utc).isoformat()

    def check(self) -> dict[str, Any]:
        return {
            "hold_active": self.hold_active,
            "reason": PHASE_HOLD_REASON,
            "hold_since": self.hold_since,
        }

    def can_proceed(self, current_phase: str) -> bool:
        return current_phase in ("Phase4", "phase4", "4") and self.hold_active
