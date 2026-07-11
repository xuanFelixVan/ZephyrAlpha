# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.reliability.blast_radius
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_blast_radius | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
