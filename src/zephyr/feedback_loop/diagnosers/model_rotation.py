"""Model Rotation — v0.9.0 R125

Blindspot: Single model reliance creates SPOF in diagnosis pipeline.
Risk: R125 — Model degradation without rotation causes systemic diagnosis failure.
"""
from dataclasses import dataclass

@dataclass
class ModelRotation:
    models: list[str] = []
    active: str = ""

    def rotate(self) -> str:
        if not self.models:
            return self.active
        idx = (self.models.index(self.active) + 1) % len(self.models) if self.active in self.models else 0
        self.active = self.models[idx]
        return self.active
