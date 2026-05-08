"""Self LLM Observability — v0.12.0 R160

Blindspot: FLE uses LLM but cannot observe LLM quality degradation.
Risk: R160 — Silent LLM quality drop corrupts all downstream diagnosis.
"""
from dataclasses import dataclass

@dataclass
class SelfLLMObservability:
    error_rate: float = 0.0
    latency_p95: float = 0.0

    def alert(self) -> bool:
        return self.error_rate > 0.05 or self.latency_p95 > 10000.0
