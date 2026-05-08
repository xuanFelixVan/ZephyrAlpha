"""全局降级级联预防（CT-DEGRADE-CASCADE）——降级传播链检测+熔断。"""

from __future__ import annotations

DEGRADE_PROPAGATION_CHAIN: list[str] = [
    "script_system", "feedback_loop", "orchestrator"
]

class DegradeCascadeGuard:
    def detect_cascade(self, degraded_systems: list[str]) -> bool:
        found = 0
        for sys in DEGRADE_PROPAGATION_CHAIN:
            if sys in degraded_systems:
                found += 1
        return found >= 3

    def break_cascade(self) -> list[str]:
        return ["CIRCUIT_BREAKER_OPEN", "BULKHEAD_ISOLATED"]
