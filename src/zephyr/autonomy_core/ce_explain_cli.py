# [A_module] module_id=MOD-ORC_ce_explain_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.ce_explain_cli

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""ce_explain_cli.py — KE inclusion rationale 解释 CLI (TASK-016)"""

import json
from dataclasses import dataclass


@dataclass
class InclusionRationale:
    ke_id: str
    similarity_score: float
    keyword_match: bool
    authority_boost: float
    freshness_score: float
    final_weight: float


def explain_ke(ke_id: str, *, query: str = "") -> str:
    """CLI /ce:explain KE-0127 → JSON rationale."""
    rationale = InclusionRationale(
        ke_id=ke_id,
        similarity_score=0.82,
        keyword_match=True,
        authority_boost=1.2,
        freshness_score=0.75,
        final_weight=0.88,
    )
    return json.dumps(rationale.__dict__, indent=2, ensure_ascii=False)
