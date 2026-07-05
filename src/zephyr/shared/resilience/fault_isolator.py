# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.resilience.fault_isolator
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


class IsolationState(Enum):
    HEALTHY = "healthy"
    SUSPECT = "suspect"
    ISOLATED = "isolated"


@dataclass
class FaultDomain:
    name: str
    state: IsolationState
    failure_count: int = 0
    dependencies: list[str] = field(default_factory=list)


class FaultIsolator:
    def __init__(self, failure_threshold: int = 3):
        self._threshold = failure_threshold
        self._domains: dict[str, FaultDomain] = {}

    def register(self, name: str, dependencies: list[str] | None = None) -> None:
        self._domains[name] = FaultDomain(name, IsolationState.HEALTHY, 0, dependencies or [])

    def report_failure(self, name: str) -> FaultDomain:
        domain = self._domains.get(name)
        if not domain:
            return FaultDomain(name, IsolationState.HEALTHY)
        domain.failure_count += 1
        if domain.failure_count >= self._threshold:
            domain.state = IsolationState.ISOLATED
        elif domain.failure_count >= self._threshold // 2:
            domain.state = IsolationState.SUSPECT
        return domain

    def is_isolated(self, name: str) -> bool:
        domain = self._domains.get(name)
        return domain.state is IsolationState.ISOLATED if domain else False

    def get_isolated(self) -> list[str]:
        return [n for n, d in self._domains.items() if d.state is IsolationState.ISOLATED]
