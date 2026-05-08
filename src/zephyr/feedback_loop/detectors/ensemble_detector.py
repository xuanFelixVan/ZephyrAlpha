"""Ensemble Detector — v0.4.0 R21

Blindspot: Single anomaly detection method misses multi-modal anomalies.
Risk: R21 — False negatives on anomalies detectable only by ensemble voting.
"""
from dataclasses import dataclass, field

@dataclass
class EnsembleDetector:
    detectors: list[str] = field(default_factory=list)

    def vote(self, scores: dict[str, float]) -> bool:
        return sum(1 for v in scores.values() if v > 2.5) > len(scores) // 2
