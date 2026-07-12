# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.gov_kb.fragmentation_index
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
# [A_module] module_id=MOD-ORC_fragmentation_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""fragmentation_index.py — 知识碎片化指数 (DD108, TASK-019)"""

from dataclasses import dataclass


@dataclass
class FragmentationScore:
    ke_count_by_domain: dict[str, int]
    total_ke: int
    entropy: float  # 0-1, higher=more fragmented
    alert: bool


class FragmentationIndex:
    """per-domain KE count entropy; >0.7 -> flag (DD108)."""

    def compute(self, ke_counts: dict[str, int]) -> FragmentationScore:
        import math

        total = sum(ke_counts.values())
        if total == 0:
            return FragmentationScore(ke_count_by_domain=ke_counts, total_ke=0, entropy=0.0, alert=False)
        entropy = -sum((c / total) * math.log(max(c / total, 1e-9)) for c in ke_counts.values()) / math.log(
            max(len(ke_counts), 2)
        )
        return FragmentationScore(
            ke_count_by_domain=ke_counts,
            total_ke=total,
            entropy=round(min(1.0, max(0.0, entropy)), 3),
            alert=entropy > 0.7,
        )
