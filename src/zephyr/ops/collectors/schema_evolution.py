# [A_module] module_id=MOD-UNK_schema_evolution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.collectors.schema_evolution

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Schema Evolution — v0.9.0 R111

Blindspot: Metric schema changes break collectors silently.
Risk: R111 — New schema fields dropped; diagnosis misses new evidence dimensions.
"""

from dataclasses import dataclass


@dataclass
class SchemaEvolution:
    version: int = 1
