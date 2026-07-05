# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.resilience.degradation_chain
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DegradationLevel(Enum):
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    FAILED = 3


@dataclass
class DegradationNode:
    component: str
    level: DegradationLevel
    affected_by: list[str] = field(default_factory=list)


class DegradationChain:
    def __init__(self):
        self._nodes: dict[str, DegradationNode] = {}
        self._edges: dict[str, list[str]] = {}

    def add_component(self, name: str) -> None:
        self._nodes[name] = DegradationNode(name, DegradationLevel.NORMAL)
        self._edges[name] = []

    def add_dependency(self, source: str, target: str) -> None:
        if source in self._edges:
            self._edges[source].append(target)

    def propagate(self, component: str, level: DegradationLevel) -> list[DegradationNode]:
        if component not in self._nodes:
            raise KeyError(f"Component '{component}' not registered in DegradationChain")
        affected = []
        self._nodes[component].level = level
        affected.append(self._nodes[component])
        for dep in self._edges.get(component, []):
            if dep in self._nodes and self._nodes[dep].level.value < level.value:
                self._nodes[dep].level = level
                self._nodes[dep].affected_by.append(component)
                affected.append(self._nodes[dep])
        return affected
