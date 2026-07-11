# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.api_dependency_metrics
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_api_dependency_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""API Dependency Metrics — v0.17.0+ R237-R242

6 维依赖指标：
  - dep_count: 总受监控依赖数
  - cve_active: 当前活跃CVE数
  - license_copyleft: copyleft许可计数
  - sunset_overdue: 已过sunset日期的API数
  - contract_slos: API合约SLO违规追踪
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class DependencyStatusRecord:
    service: str
    version: str
    cve_count: int = 0
    license_copyleft: bool = False
    sunset_overdue: bool = False

    @property
    def risk_level(self) -> str:
        if self.cve_count > 0:
            return "HIGH"
        if self.license_copyleft:
            return "MEDIUM"
        if self.sunset_overdue:
            return "HIGH"
        return "LOW"


@dataclass
class APIDependencyMetrics:
    dependencies: dict[str, DependencyStatusRecord] = field(default_factory=dict)
    history: deque[dict] = field(default_factory=lambda: deque(maxlen=500))

    def register(self, service: str, version: str) -> DependencyStatusRecord:
        dep = DependencyStatusRecord(service=service, version=version)
        self.dependencies[service] = dep
        return dep

    def scan(self) -> dict[str, int]:
        return {
            "total": len(self.dependencies),
            "cve_active": sum(1 for d in self.dependencies.values() if d.cve_count > 0),
            "copyleft": sum(1 for d in self.dependencies.values() if d.license_copyleft),
            "sunset_overdue": sum(1 for d in self.dependencies.values() if d.sunset_overdue),
        }

    def snapshot(self) -> None:
        self.history.append(self.scan())
