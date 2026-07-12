# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.decision_provenance
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_decision_provenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Decision Provenance — v0.12.0 R166

Blindspot: FLE decisions lack audit trail of contributing factors.
Risk: R166 — Why was this repair chosen?  Invisible after the fact.
"""

from dataclasses import dataclass, field


@dataclass
class DecisionProvenance:
    decisions: list[dict] = field(default_factory=list)

    def record(self, decision: dict) -> None:
        self.decisions.append(decision)
