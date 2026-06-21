# [A_module] module_id=MOD-ORC_domain_decay_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.domain_decay_config

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""domain_decay_config.py — 每领域半衰期 (DD105, TASK-019)"""

from dataclasses import dataclass

@dataclass
class DomainDecay:
    domain: str
    halflife_days: float
    ttl_days: float
    decay_mode: str  # "exponential" | "linear"

class DomainDecayConfig:
    """Per-domain halflife table + TTL (DD105)."""
    _HALFLIFE: dict[str, DomainDecay] = {
        "CODE_GEN": DomainDecay("CODE_GEN", halflife_days=60, ttl_days=180, decay_mode="exponential"),
        "OPS_FIX": DomainDecay("OPS_FIX", halflife_days=90, ttl_days=270, decay_mode="exponential"),
        "SECURITY": DomainDecay("SECURITY", halflife_days=30, ttl_days=90, decay_mode="exponential"),
    }

    def get(self, domain: str) -> DomainDecay:
        return self._HALFLIFE.get(domain, DomainDecay(domain, halflife_days=90, ttl_days=365, decay_mode="exponential"))
