# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.otel_adapter

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""OTel Adapter — v0.12.0 R170

Blindspot: FLE internal telemetry incompatible with external OTel ecosystem.
Risk: R170 — FLE metrics invisible to organization-wide observability.
"""
from dataclasses import dataclass

@dataclass
class OTelAdapter:
    endpoint: str = "http://localhost:4317"
