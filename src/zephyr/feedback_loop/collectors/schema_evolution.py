# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.schema_evolution
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Schema Evolution — v0.9.0 R111

Blindspot: Metric schema changes break collectors silently.
Risk: R111 — New schema fields dropped; diagnosis misses new evidence dimensions.

# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/collectors/schema_evolution.yaml
"""

from dataclasses import dataclass


@dataclass
class SchemaEvolution:
    version: int = 1
