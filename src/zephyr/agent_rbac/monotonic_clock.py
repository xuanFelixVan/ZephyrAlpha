# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.monotonic_clock

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""单调时钟——防止时间回拨攻击(NTP/timestamp manipulation)."""
from __future__ import annotations

import time
from typing import Any


class MonotonicClock:
    def __init__(self) -> None:
        self._last_wall_time: float = 0.0
        self._monotonic_base: float = time.monotonic()
        self._drift_violations: int = 0

    def now(self) -> float:
        mono = time.monotonic() - self._monotonic_base
        wall = time.time()
        return max(mono, wall)

    def verify(self, timestamp: float, tolerance_seconds: float = 10.0) -> dict[str, Any]:
        now = time.time()
        if timestamp < self._last_wall_time - tolerance_seconds:
            self._drift_violations += 1
            return {"valid": False, "reason": "clock_drift_backward", "provided": timestamp, "expected_min": self._last_wall_time}

        self._last_wall_time = max(self._last_wall_time, timestamp)
        return {"valid": True, "timestamp": timestamp, "drift_violations": self._drift_violations}
