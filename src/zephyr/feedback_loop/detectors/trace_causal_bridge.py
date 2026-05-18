# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.trace_causal_bridge

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
