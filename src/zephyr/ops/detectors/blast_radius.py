# [A_module] module_id=MOD-UNK_blast_radius | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.detectors.blast_radius

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Blast Radius Detector — v0.12.0 R167

Blindspot: Repair side effects across subsystems not modeled.
Risk: R167 — Repair on subsystem A breaks subsystem B; cascading failure.
"""

from dataclasses import dataclass, field


@dataclass
class BlastRadius:
    dependency_graph: dict[str, list[str]] = field(default_factory=dict)

    def estimate(self, target: str) -> list[str]:
        return self.dependency_graph.get(target, [])
