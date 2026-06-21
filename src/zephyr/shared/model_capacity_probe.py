# [A_module] module_id=MOD-SHR_model_capacity_probe | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
