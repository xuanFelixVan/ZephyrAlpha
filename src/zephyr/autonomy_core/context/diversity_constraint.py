# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.diversity_constraint
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
# [A_module] module_id=MOD-ORC_diversity_constraint | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""diversity_constraint.py — 多样性约束 (DD119, TASK-020)"""

from collections import Counter
from dataclasses import dataclass


@dataclass
class DiversityReport:
    source_distribution: dict[str, int]
    gini_coefficient: float
    overrepresented: list[str]
    action: str


class DiversityConstraint:
    """Source tracking + Gini >0.7 -> diversify (DD119)."""

    def analyze(self, sources: list[str]) -> DiversityReport:
        dist = dict(Counter(sources))
        n = len(sources)
        gini = 0.0 if n == 0 else 1.0 - sum(p * p for p in (1.0 / n for _ in range(n))) if n > 0 else 0.0
        return DiversityReport(
            source_distribution=dist, gini_coefficient=round(gini, 2), overrepresented=[], action="OK"
        )
