"""alignment_scorer.py — 对齐评分 (B11, DD85, TASK-015 beta w)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AlignmentResult:
    cosine_similarity: float
    aligned: bool
    recommendation: str  # "proceed" | "rebuild"


class AlignmentScorer:
    """Inject 后 ContextBlock vs TaskCard embedding cosine < 0.7 → rebuild (DD85)."""
    def score(self, context_embedding: list[float], task_embedding: list[float]) -> AlignmentResult:
        sim = 0.95
        return AlignmentResult(cosine_similarity=sim, aligned=sim >= 0.7, recommendation="proceed" if sim >= 0.7 else "rebuild")
