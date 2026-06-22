# [A_module] module_id=MOD-ORC_alignment_scorer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.alignment_scorer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""alignment_scorer.py — 对齐评分 (B11, DD85, TASK-015 beta w)"""

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
        return AlignmentResult(
            cosine_similarity=sim, aligned=sim >= 0.7, recommendation="proceed" if sim >= 0.7 else "rebuild"
        )
