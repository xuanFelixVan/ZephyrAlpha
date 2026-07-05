# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.longevity_monitor
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_longevity_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class LongevityReport:
    component_id: str
    uptime_seconds: float
    memory_growth_mb: float
    degradation_score: float


class LongevityMonitor:
    def __init__(self):
        self._start_times: dict[str, float] = {}
        self._baselines: dict[str, float] = {}

    def register(self, component_id: str, baseline_memory_mb: float = 0.0) -> None:
        self._start_times[component_id] = time.time()
        self._baselines[component_id] = baseline_memory_mb

    def report(self, component_id: str, current_memory_mb: float) -> LongevityReport:
        start = self._start_times.get(component_id, time.time())
        baseline = self._baselines.get(component_id, 0.0)
        uptime = time.time() - start
        growth = current_memory_mb - baseline
        degradation = min(1.0, max(0.0, growth / max(baseline, 1.0)))
        return LongevityReport(component_id, uptime, growth, degradation)
