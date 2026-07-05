# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.capacity_governance.model_capacity_probe
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization; tests.unit.shared.test_orphan_integration
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

from dataclasses import dataclass


@dataclass
class ProbeResult:
    model_id: str
    tokens_per_second: float
    avg_latency_ms: float
    error_rate: float
    available: bool


class ModelCapacityProbe:
    def __init__(self) -> None:
        self._results: dict[str, ProbeResult] = {}

    def probe(self, model_id: str, latency_ms: float, tokens: int) -> ProbeResult:
        tps = tokens / (latency_ms / 1000.0) if latency_ms > 0 else 0.0
        result = ProbeResult(model_id, tps, latency_ms, 0.0, tps > 0)
        self._results[model_id] = result
        return result

    def get_result(self, model_id: str) -> ProbeResult | None:
        return self._results.get(model_id)

    def mark_unavailable(self, model_id: str) -> None:
        if model_id in self._results:
            self._results[model_id] = ProbeResult(model_id, 0.0, 0.0, 1.0, False)
