"""Model Health Monitor — v0.5.0 R40

Blindspot: ML model serving health degraded without detection.
Risk: R40 — Stale models produce corrupted inference outputs.
"""
from dataclasses import dataclass


@dataclass
class ModelHealth:
    model_id: str
    accuracy: float = 100.0
    last_validation: float = 0.0

    @property
    def degraded(self) -> bool:
        return self.accuracy < 85.0
