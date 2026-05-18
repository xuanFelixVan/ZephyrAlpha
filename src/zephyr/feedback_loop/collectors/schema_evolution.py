# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.collectors.schema_evolution

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
