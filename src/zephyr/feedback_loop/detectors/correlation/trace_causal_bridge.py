# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.trace_causal_bridge
# [DOMAIN] D_FBL_DETECTORS
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
# [A_module] module_id=MOD-UNK_trace_causal_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Trace Causal Bridge — v0.6.0 R62

Blindspot: Distributed trace spans disconnected from diagnosis context.
Risk: R62 — Root cause spans multiple services; single-service view misses causal chain.
"""

from dataclasses import dataclass, field


@dataclass
class TraceCausalBridge:
    spans: list[dict] = field(default_factory=list)

    def bridge(self, span: dict) -> None:
        self.spans.append(span)
