# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.governance.kb.ke_justification
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_rational | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""rational.py — 注入理由 (DD99, TASK-019)"""

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
        return [
            SelectedKE(ke_id=k, reason=reasons[i % len(reasons)], score=s)
            for i, (k, s) in enumerate(zip(ke_ids, scores, strict=False))
        ]
