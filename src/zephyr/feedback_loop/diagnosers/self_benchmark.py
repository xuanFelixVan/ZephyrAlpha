"""Self Benchmark — v0.9.0 R115

Blindspot: FLE performance trends invisible without historical comparison.
Risk: R115 — Gradual degradation invisible without baseline comparison.
"""
from dataclasses import dataclass, field


@dataclass
class SelfBenchmark:
    baselines: dict[str, float] = field(default_factory=dict)

    def compare(self, metric: str, current: float) -> float:
        baseline = self.baselines.get(metric, current)
        return current - baseline
