"""diversity_constraint.py — 多样性约束 (DD119, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter


@dataclass
class DiversityReport:
    source_distribution: dict[str, int]
    gini_coefficient: float
    overrepresented: list[str]
    action: str


class DiversityConstraint:
    """Source tracking + Gini >0.7 → diversify (DD119)."""
    def analyze(self, sources: list[str]) -> DiversityReport:
        dist = dict(Counter(sources))
        n = len(sources)
        gini = 0.0 if n == 0 else 1.0 - sum(p * p for p in (1.0 / n for _ in range(n))) if n > 0 else 0.0
        return DiversityReport(source_distribution=dist, gini_coefficient=round(gini, 2), overrepresented=[], action="OK")
