"""EWC KB Review — v0.6.0 R51

Blindspot: KB entries overwritten without Elastic Weight Consolidation.
Risk: R51 — New knowledge catastrophically erases old critical knowledge.
"""
from dataclasses import dataclass

@dataclass
class EWCKBReview:
    importance_weights: dict[str, float] = {}

    def protect(self, param: str, importance: float) -> None:
        self.importance_weights[param] = importance
