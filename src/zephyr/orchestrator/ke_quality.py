"""知识质量评分契约（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评分。"""

from __future__ import annotations

class KnowledgeEntryQuality:
    def score(self, completeness: float, accuracy: float, timeliness: float) -> float:
        return (completeness + accuracy + timeliness) / 3.0

    def is_acceptable(self, score: float) -> bool:
        return score >= 0.7

    def needs_review(self, score: float) -> bool:
        return score < 0.5
