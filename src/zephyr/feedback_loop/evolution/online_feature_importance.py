"""Online Feature Importance — v0.7.0 R73

Blindspot: Feature importance computed offline; stale in real-time.
Risk: R73 — Importance rankings lag; wrong features drive diagnosis.
"""
from dataclasses import dataclass, field

@dataclass
class OnlineFeatureImportance:
    scores: dict[str, float] = field(default_factory=dict)

    def update(self, feature: str, importance: float) -> None:
        self.scores[feature] = importance
