"""Knowledge Freshness — v0.5.0 R47

Blindspot: Stale KB entries have same weight as fresh ones.
Risk: R47 — Outdated knowledge misguides current diagnosis.
"""
from dataclasses import dataclass, field
import time

@dataclass
class KnowledgeFreshness:
    entries: dict[str, float] = field(default_factory=dict)

    def score(self, entry_id: str, created_at: float) -> float:
        age_days = (time.time() - created_at) / 86400.0
        return max(0.0, 1.0 - age_days / 90.0)
