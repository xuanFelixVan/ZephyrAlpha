# [A_module] module_id=MOD-UNK_otel_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.detectors.otel_adapter

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
