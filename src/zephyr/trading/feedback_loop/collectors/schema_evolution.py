# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.schema_evolution
# [DOMAIN] D_OPS
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_schema_evolution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Schema Evolution — v0.9.0 R111

Blindspot: Metric schema changes break collectors silently.
Risk: R111 — New schema fields dropped; diagnosis misses new evidence dimensions.
"""

from dataclasses import dataclass


@dataclass
class SchemaEvolution:
    version: int = 1
