# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.capacity_fingerprint
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapacitySnapshot:
    cpu_pct: float
    mem_pct: float
    disk_pct: float
    net_mbps: float
    active_tasks: int
    timestamp: str


class CapacityFingerprint:
    def __init__(self) -> None:
        self._snapshots: dict[str, CapacitySnapshot] = {}

    def capture(self, component_id: str, snapshot: CapacitySnapshot) -> str:
        self._snapshots[component_id] = snapshot
        return f"{component_id}:{hash(snapshot)}"

    def compare(self, component_id: str, current: CapacitySnapshot) -> dict[str, float]:
        baseline = self._snapshots.get(component_id)
        if not baseline:
            return {}
        return {
            "cpu_delta": current.cpu_pct - baseline.cpu_pct,
            "mem_delta": current.mem_pct - baseline.mem_pct,
            "disk_delta": current.disk_pct - baseline.disk_pct,
        }

    def get_baseline(self, component_id: str) -> CapacitySnapshot | None:
        return self._snapshots.get(component_id)
