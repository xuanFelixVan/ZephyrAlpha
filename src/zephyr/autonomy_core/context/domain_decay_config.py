# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.domain_decay_config
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
