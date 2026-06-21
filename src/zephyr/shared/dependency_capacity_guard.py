# [A_module] module_id=MOD-SHR_dependency_capacity_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CapacityViolation:
    dependency: str
    current_load: float
    max_capacity: float
    utilization_pct: float


class DependencyCapacityGuard:
    def __init__(self):
        self._capacities: dict[str, float] = {}
        self._loads: dict[str, float] = {}

    def set_capacity(self, dependency: str, max_capacity: float) -> None:
        if max_capacity <= 0:
            raise ValueError(f"max_capacity must be > 0 for dependency '{dependency}', got {max_capacity}")
        self._capacities[dependency] = max_capacity

    def update_load(self, dependency: str, current_load: float) -> CapacityViolation | None:
        self._loads[dependency] = current_load
        cap = self._capacities.get(dependency, float('inf'))
        util = (current_load / cap * 100) if cap > 0 else 0.0
        if util > 90.0:
            return CapacityViolation(dependency, current_load, cap, util)
        return None

    def check_all(self) -> list[CapacityViolation]:
        violations = []
        for dep in self._capacities:
            load = self._loads.get(dep, 0.0)
            cap = self._capacities[dep]
            util = (load / cap * 100) if cap > 0 else 0.0
            if util > 90.0:
                violations.append(CapacityViolation(dep, load, cap, util))
        return violations
