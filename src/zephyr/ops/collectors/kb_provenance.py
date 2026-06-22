# [A_module] module_id=MOD-UNK_kb_provenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.collectors.kb_provenance

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""KB Provenance — v0.10.0 R136

Blindspot: KB entries lack origin tracking; stale sources pollute diagnosis.
Risk: R136 — Unreliable source knowledge weighted equally with verified knowledge.
"""

from dataclasses import dataclass


@dataclass
class KBProvenance:
    source: str = "unknown"
    reliability: float = 0.5
