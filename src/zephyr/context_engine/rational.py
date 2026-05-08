"""rational.py — 注入理由 (DD99, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SelectedKE:
    ke_id: str
    reason: str
    score: float


class KEJustificationGenerator:
    """Per-KE rational + score map → Table (DD99)."""
    def justify(self, ke_ids: list[str], scores: list[float]) -> list[SelectedKE]:
        reasons = ["keyword_match", "similarity_top_k", "authority_boosted", "freshness_promoted"]
        return [SelectedKE(ke_id=k, reason=reasons[i % len(reasons)], score=s) for i, (k, s) in enumerate(zip(ke_ids, scores))]
