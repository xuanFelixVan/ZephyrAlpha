# [A_module] module_id=MOD-UNK_self_ha | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.detectors.self_ha

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Self HA — v0.13.0 R173

Blindspot: Single FLE instance is SPOF for self-healing.
Risk: R173 — FLE itself fails; no other instance takes over.
"""

from dataclasses import dataclass, field

@dataclass
class SelfHA:
    active_instance: str = "primary"
    standby_instances: list[str] = field(default_factory=list)
