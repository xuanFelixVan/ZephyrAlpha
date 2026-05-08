"""Model Rotation v2 — v0.10.0 R140

Enhanced model rotation with weighted selection based on recent performance.
"""
from dataclasses import dataclass, field

@dataclass
class ModelRotationV2:
    models: dict[str, float] = field(default_factory=dict)

    def select(self) -> str:
        return max(self.models, key=self.models.get) if self.models else ""
