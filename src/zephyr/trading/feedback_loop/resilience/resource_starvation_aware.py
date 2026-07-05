# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.resilience.resource_starvation_aware
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
# [A_module] module_id=MOD-RES_resource_starvation_aware | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Resource Starvation Aware — v0.15.0 R209

Blindspot: FLE repair actions consume resources; resource exhaustion during repair invisible.
Risk: R209 — FLE repair triggers OOM; FLE itself killed before repair completes.

Mitigation: Pre-repair resource check; refuse to start if resources below safety margin.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResourceBudget:
    cpu_available_pct: float = 100.0
    mem_available_mb: float = 8192.0
    disk_available_mb: float = 102400.0


@dataclass
class ResourceStarvationAware:
    cpu_min_pct: float = 10.0
    mem_min_mb: float = 512.0
    disk_min_mb: float = 1024.0

    def can_proceed(self, budget: ResourceBudget) -> bool:
        return (
            budget.cpu_available_pct >= self.cpu_min_pct
            and budget.mem_available_mb >= self.mem_min_mb
            and budget.disk_available_mb >= self.disk_min_mb
        )
